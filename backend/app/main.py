from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

from orchestrator import run_maintainer

app = FastAPI(title="AI Maintainer Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}


class RepoRequest(BaseModel):
    repo_url: str


def maintainer_task(job_id: str, repo_url: str):
    jobs[job_id] = {"status": "running", "logs": ""}

    def log_callback(line: str):
        jobs[job_id]["logs"] += line + "\n"

    try:
        result = run_maintainer(repo_url, log_callback=log_callback)
        jobs[job_id] = {"status": "done", "result": result}
    except Exception as e:
        jobs[job_id] = {"status": "error", "error": str(e)}


@app.post("/run")
def run_agent(req: RepoRequest, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "logs": ""}
    bg.add_task(maintainer_task, job_id, req.repo_url)
    return {"job_id": job_id, "status": "started"}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})
