from fastapi import FastAPI, HTTPException
from uuid import uuid4
from threading import Thread
import uvicorn
import time
from rp_handler import Handler

app = FastAPI()
jobs = {}

# Initialize the job handler at startup
job_handler = Handler()
job_handler.setup()

def process_job(job_id, input_data):
    try:
        # Process the job using the handler
        result = job_handler.run({"id": job_id, "input": input_data})
        jobs[job_id] = {"status": "COMPLETED", "output": result}
    except Exception as e:
        jobs[job_id] = {"status": "FAILED", "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    try:
        # Check if the job handler is properly initialized
        if not job_handler:
            return {"status": "error", "detail": "Job handler not initialized"}
        
        return {
            "status": "healthy",
            "message": "Service is running",
            "timestamp": time.time()
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/run")
async def run_job(payload: dict):
    if not payload.get("input"):
        raise HTTPException(status_code=400, detail="Input data is required")
    
    job_id = str(uuid4())
    jobs[job_id] = {"status": "IN_PROGRESS"}
    
    # Start processing in a background thread
    Thread(target=process_job, args=(job_id, payload.get("input"))).start()
    return {"id": job_id, "status": "IN_PROGRESS"}

@app.get("/status/{job_id}")
async def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"id": job_id, **job}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3050)