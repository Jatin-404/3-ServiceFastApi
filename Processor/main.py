from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel, Field, field_validator
import asyncio

app = FastAPI()

class ProcessRequest(BaseModel):
    text: str

    @field_validator("text")
    def text_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Text cant be empty")
        return value


def split_into_chunks(text: str, chunk_size: int = 50):   # keeping chunk_size small so you can test with short text
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunks.append({
            "chunk_index": i // chunk_size,
            "text": " ".join(chunk_words)
        })

    return chunks

async def call_worker(client: AsyncClient, chunk: dict) -> dict:
    response = await client.post("http://localhost:8002/work", json=chunk)
    response.raise_for_status()
    return response.json()


@app.get("/health")
def health():
    return{
        "Health": "OK",
        "Service": "Processer"
    }

@app.post("/process")
async def process(data: ProcessRequest):
    chunks = split_into_chunks(data.text)
    results = []

    async with AsyncClient() as client:
        tasks = [call_worker(client, chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    summaries = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            summaries.append({
                "chunk_index": i,
                "word_count": 0,
                "most_common_word": f"[error on chunk {i}]"
            })
        else:
            summaries.append(result)


    return{
        "total Chunks": len(chunks),
        "results": summaries
    }


#uvicorn Processor.main:app --port 8001 --reload