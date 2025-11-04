from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os

# Import backend modules
from .parser import parse_resume, extract_skills
from .embedding_module import get_embedding, compute_similarity

# -------------------------------------
# Initialize the FastAPI app FIRST
# -------------------------------------
app = FastAPI()

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dir = os.path.join(os.path.dirname(__file__), "/Users/lakshmianand/Desktop/capstone-project/pgrkam-frontend")

# Mount static subfolders at their top-level paths
for subdir in ["css", "fonts", "images", "js", "static"]:
    app.mount(f"/{subdir}", StaticFiles(directory=os.path.join(frontend_dir, subdir)), name=subdir)

# Serve index.html at root
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))


# -------------------------------------
# Resume matching API (existing backend logic)
# -------------------------------------
class MatchResult(BaseModel):
    filename: str
    similarity: float
    skill_overlap: List[str]
    total_skills: List[str]
    entities: List[str]

# Load job description and embeddings
JOB_DESCRIPTION_PATH = "/Users/lakshmianand/Desktop/capstone-project/job_description.txt"
if not os.path.exists(JOB_DESCRIPTION_PATH):
    raise Exception(f"Job description not found at {JOB_DESCRIPTION_PATH}")
with open(JOB_DESCRIPTION_PATH, "r", encoding="utf-8") as f:
    job_text = f.read()
job_skills = extract_skills(job_text)
job_embedding = get_embedding(job_text)

@app.post("/match_resume/", response_model=MatchResult)
async def match_resume(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    try:
        parsed = parse_resume(temp_file_path)
        resume_embedding = get_embedding(parsed["raw_text"])
        similarity = compute_similarity(resume_embedding, job_embedding)
        skill_overlap = list(set(parsed["skills"]).intersection(job_skills))
        entities = [f"{text}({label})" for text, label in parsed["entities"]]
        result = MatchResult(
            filename=file.filename,
            similarity=similarity,
            skill_overlap=skill_overlap,
            total_skills=parsed["skills"],
            entities=entities
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(temp_file_path)
    return result

# -------------------------------------
# Capture UI Event Logs (from JS)
# -------------------------------------
@app.post("/api/logEvent")
async def log_event(request: Request):
    data = await request.json()
    print("Event logged:", data)
    return {"status": "success", "logged_event": data["event_type"]}
