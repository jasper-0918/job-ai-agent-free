# api/app.py
import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from db.database       import Database
from agents.decision   import evaluate_job, final_decision
from agents.cover_letter import generate_cover_letter
from agents.apply      import send_application
from agents.worker     import execute_task, process_queue
from config            import MAX_AUTO_APPLIES_PER_DAY

app = FastAPI(title="Job AI Agent FREE")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

db = Database()

# ── Pydantic models ───────────────────────────────────────

class TaskReq(BaseModel):
    description: str
    context: str = ""

class AddJobReq(BaseModel):
    title: str
    company: str
    platform: str = "Manual"
    url: str = ""
    apply_email: str = ""
    description: str = ""
    salary_info: str = ""

# ── Routes ────────────────────────────────────────────────

@app.get("/api/stats")
def stats():
    return db.get_stats()

@app.get("/api/jobs")
def get_jobs(limit: int = 200):
    return db.get_all(limit)

@app.get("/api/jobs/{job_id}")
def get_job(job_id: int):
    job = db.get_by_id(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job

@app.post("/api/jobs/add")
def add_job(req: AddJobReq):
    job_id = db.add_job(req.dict())
    if not job_id:
        return {"added": False, "message": "Already exists"}
    return {"added": True, "job_id": job_id}

@app.post("/api/jobs/{job_id}/evaluate")
def evaluate(job_id: int):
    job = db.get_by_id(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    ai = evaluate_job(job)
    db.update_ai(job_id, ai)
    return {"job_id": job_id, "evaluation": ai}

@app.post("/api/jobs/{job_id}/apply")
def apply_job(job_id: int):
    job = db.get_by_id(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if not job.get("apply_email"):
        raise HTTPException(400, "No apply email — apply manually")
    if job["status"] == "applied":
        return {"sent": False, "message": "Already applied"}
    cover  = generate_cover_letter(job)
    result = send_application(job, cover, MAX_AUTO_APPLIES_PER_DAY)
    if result["sent"]:
        db.update_status(job_id, "applied", cover)
    return result

@app.post("/api/jobs/{job_id}/reject")
def reject_job(job_id: int):
    db.update_status(job_id, "skipped")
    return {"ok": True}

@app.get("/api/inbox")
def get_inbox():
    return db.get_responses()

@app.post("/api/inbox/scan")
def scan_inbox():
    from agents.inbox import scan_inbox as _scan
    results = _scan(lookback_days=30)
    for r in results:
        db.log_response(r)
    return {"scanned": len(results), "results": results}

@app.get("/api/tasks")
def get_tasks():
    return db.get_pending_tasks()

@app.post("/api/tasks/add")
def add_task(req: TaskReq):
    task_id = db.add_task(req.description)
    return {"task_id": task_id}

@app.post("/api/tasks/{task_id}/run")
def run_task(task_id: int):
    tasks = db.get_pending_tasks()
    task  = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(404, "Task not found or already done")
    result = execute_task(task["description"])
    db.complete_task(task_id, result["result"])
    return result

@app.post("/api/scrape")
def scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(_scrape_and_evaluate)
    return {"message": "Scraping started in background"}

def _scrape_and_evaluate():
    from agents.scraper import scrape_all
    jobs = scrape_all()
    for job in jobs:
        job_id = db.add_job(job)
        if job_id:
            ai = evaluate_job(job)
            db.update_ai(job_id, ai)

# Serve frontend
frontend = Path(__file__).parent.parent / "frontend"
if frontend.exists():
    @app.get("/")
    def serve():
        return FileResponse(str(frontend / "index.html"))
