from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel, Field, field_validator


app = FastAPI()

class UploadRequest(BaseModel):
    text: str

    @field_validator("text")
    def text_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Text can't be empty")
        return value


@app.get("/health")
def health():
    return{
        "Health": "OK",
        "Serivce": "Gateway"
    }

@app.post("/upload")
async def upload(data: UploadRequest):
    async with AsyncClient() as client:
        response = await client.post("http://localhost:8001/process",json={"text": data.text})
        return response.json()



#uvicorn Gateway.main:app --port 8000 --reload