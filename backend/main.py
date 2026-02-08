from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid

from orchestrator import run_maintainer

app = FastAPI(title="AI Maintainer Backend")

# In-memory job store (hackathon only)
jobs = {}


# -------- request schema --------

class RepoRequest(BaseModel):
    repo_url: str


# -------- background worker --------

def maintainer_task(job_id: str, repo_url: str):
    try:
        result = run_maintainer(repo_url)
        jobs[job_id] = {
            "status": "done",
            "result": result
        }
    except Exception as e:
        jobs[job_id] = {
            "status": "error",
            "error": str(e)
        }


# -------- API endpoints --------

@app.post("/run")
def run_agent(req: RepoRequest, bg: BackgroundTasks):
    """
    Start autonomous maintainer.
    Returns immediately with job_id.
    """
    job_id = str(uuid.uuid4())

    jobs[job_id] = {"status": "running"}

    bg.add_task(maintainer_task, job_id, req.repo_url)

    return {
        "job_id": job_id,
        "status": "started"
    }


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """
    Check job progress.
    """
    return jobs.get(job_id, {"status": "not_found"})
