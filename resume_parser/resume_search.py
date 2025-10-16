import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.parser import parse_resume, extract_skills
from models.embedding_module import get_embedding, compute_similarity
import os

job_file = "/Users/lakshmianand/Desktop/capstone-project/job_description.txt"
with open(job_file, "r", encoding="utf-8") as f:
    job_text = f.read()
job_skills = extract_skills(job_text)

# List your resume files (.pdf, .docx, .txt allowed)
resumes_dir = "/Users/lakshmianand/Desktop/capstone-project/"
resume_files = [os.path.join(resumes_dir, f) for f in os.listdir(resumes_dir) if f.lower().startswith("resume") and (f.endswith(".pdf") or f.endswith(".docx") or f.endswith(".txt"))]

results = []
for resume_path in resume_files:
    result = parse_resume(resume_path)
    resume_embedding = get_embedding(result["raw_text"])
    job_embedding = get_embedding(job_text)
    similarity = compute_similarity(resume_embedding, job_embedding)
    skill_overlap = set(result["skills"]).intersection(set(job_skills))
    results.append({
        "file": resume_path,
        "similarity": similarity,
        "skill_overlap": skill_overlap,
        "resume_skills": result["skills"],
        "entities": result["entities"],
    })

# Sort and display results
results.sort(key=lambda x: x["similarity"], reverse=True)

print("\nTop Resume Matches with Explainability:\n")
for i, r in enumerate(results):
    print(f"{i+1}. {r['file']}")
    print(f"   Similarity Score: {r['similarity']:.4f}")
    print(f"   Skill Overlap: {', '.join(r['skill_overlap']) if r['skill_overlap'] else 'None'}")
    print(f"   Resume Skills: {', '.join(r['resume_skills'])}")
    print(f"   Named Entities: {r['entities'][:5]}\n")  # Show first 5 for brevity
