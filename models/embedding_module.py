from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-mpnet-base-v2")

def get_embedding(text):
    return model.encode(text)

def compute_similarity(vec1, vec2):
    return float(cosine_similarity([vec1], [vec2])[0][0])

if __name__ == "__main__":
    with open("/Users/lakshmianand/Desktop/capstone-project/parsed_resume.txt", "r", encoding="utf-8", errors="ignore") as f:
        resume_text = f.read()
    with open("/Users/lakshmianand/Desktop/capstone-project/job_description.txt", "r", encoding="utf-8") as f:
        job_text = f.read()
    resume_vec = get_embedding(resume_text)
    job_vec = get_embedding(job_text)
    similarity = compute_similarity(resume_vec, job_vec)
    print(f"Resume vs Job similarity score: {similarity:.4f}")
    if similarity > 0.8:
        print("Strong match!")
    elif similarity > 0.6:
        print("Possible match.")
    else:
        print("Weak match.")
