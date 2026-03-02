from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
from collections import Counter
from shared.logger import setup_logger

app = FastAPI()


logger = setup_logger(service_name="Worker")


class ChunkRequest(BaseModel):              # Validating incoming chunk 
    chunk_index: int = Field(..., ge=0)
    text: str

    @field_validator("text")
    def text_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Text cant be empty")
        return value
    

class ChunkResponse(BaseModel):

    chunk_index: int
    word_count: int
    most_common_word: str
    

@app.get("/health")
def health():
    logger.info("Healthy")
    return{
        "Health": "OK",
        "Service": "Worker"
    }

@app.post("/work")
async def do_work(data: ChunkRequest):
    logger.info(msg="Worker service activated")
    words = data.text.lower().split()
    word_counts = Counter(words)           # Counter counts how many times each word appears
    most_common = word_counts.most_common(1)[0][0]   # most_common(1) returns [('the', 5)], [0][0] gets just 'the'

    return ChunkResponse(
        chunk_index= data.chunk_index,
        word_count= len(words),
        most_common_word= most_common
    )

#uvicorn Worker.main:app --port 8002 --reload