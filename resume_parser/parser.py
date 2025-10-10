import spacy
from sentence_transformers import SentenceTransformer
import re

# Load spaCy model for NLP parsing
nlp = spacy.load("en_core_web_sm")

# Load sentence transformer model for embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Example list of skills you expect to extract (can grow)
SKILL_SET = {
    "python", "java", "sql", "docker", "machine learning",
    "nlp", "deep learning", "data analysis", "cloud",
    "tensorflow", "pytorch", "fastapi"
}

def extract_skills(text):
    """
    Simple keyword-based skill extractor as example.
    """
    text_lower = text.lower()
    found_skills = {skill for skill in SKILL_SET if skill in text_lower}
    return list(found_skills)

def parse_resume(text):
    """
    Use spaCy NLP to parse named entities and keywords from resume text.
    """
    doc = nlp(text)

    # Extract named entities for organization, dates, etc.
    entities = {ent.label_: [] for ent in doc.ents}
    for ent in doc.ents:
        if ent.text not in entities[ent.label_]:
            entities[ent.label_].append(ent.text)

    skills = extract_skills(text)

    return {
        "skills": skills,
        "entities": entities,
        "raw_text": text
    }

def get_resume_embedding(text):
    """
    Generate semantic embedding vector for the entire resume text.
    """
    return embedder.encode(text).tolist()

if __name__ == "__main__":
    # Example usage
    sample_resume = """
    John Doe is a software engineer with 5 years experience
    in Python, SQL, and Docker. Skilled in machine learning and NLP.
    Worked at Acme Corp from 2018 to 2023.
    """

    parsed = parse_resume(sample_resume)
    embedding = get_resume_embedding(sample_resume)

    print("Parsed Resume:", parsed)
    print("Embedding vector length:", len(embedding))
