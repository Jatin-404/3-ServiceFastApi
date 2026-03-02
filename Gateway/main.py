from fastapi import FastAPI, BackgroundTasks, HTTPException
from httpx import AsyncClient, RequestError, HTTPStatusError
from pydantic import BaseModel, Field, field_validator
import uuid


app = FastAPI()

jobs = {}

class UploadRequest(BaseModel):
    text: str

    @field_validator("text")
    def text_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Text can't be empty")
        return value
    
async def get_text(data: UploadRequest, job_id):
    jobs[job_id]["status"] = "Processing" 
    try:
        async with AsyncClient() as client:
            response = await client.post("http://localhost:8001/process",json={"text": data.text})
            response.raise_for_status()
            result = response.json()

            jobs[job_id]["status"] = "completed"
            jobs[job_id]["result"] = result
            jobs[job_id]["Total_Chunks"] = result["total Chunks"]

            return result
        
    
    except RequestError as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = f"Service B unreachable: {str(e)}"
    except HTTPStatusError as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = f"Service B returned error: {str(e)}"
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = f"Unexpected error: {str(e)}"





@app.get("/health")
def health():
    return{
        "Health": "OK",
        "Serivce": "Gateway"
    }

@app.post("/upload")
async def upload(data: UploadRequest,  background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "queued",
        'Total_Chunks': 0,
        'result': None
    } 

    background_tasks.add_task(get_text, data, job_id)

    return {"job_id": job_id, "check_status_at": f"/status/{job_id}"}

@app.get('/status')
async def status():
    return jobs

@app.get("/status/{job_id}")
async def get_status_by_id(job_id: str):
    if job_id in jobs:
        return jobs[job_id]
    else:
        raise HTTPException(status_code=404 , detail= "Job id not found ")


#uvicorn Gateway.main:app --port 8000 --reload