import fitz  # PyMuPDF to extract PDF text
import docx  # For DOCX files
import spacy
import re
import os
from rapidfuzz import process, fuzz

nlp = spacy.load("en_core_web_sm")

SKILL_KEYWORDS = [
    "python", "java", "sql", "docker", "machine learning", "nlp", "deep learning",
    "fastapi", "tensorflow", "pytorch", "react", "aws", "azure", "devops", "cloud",
    "flask", "postgreSQL", "data science", "feature engineering", "transformers"
]

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_skills(text):
    found_skills = set()
    # Regex exact matches
    for skill in SKILL_KEYWORDS:
        if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
            found_skills.add(skill)
    # NER fuzzy matches
    doc = nlp(text)
    ner_candidates = [ent.text for ent in doc.ents if ent.label_ in {"ORG", "PRODUCT", "WORK_OF_ART", "LANGUAGE"}]
    fuzzy_matches = [process.extractOne(candidate, SKILL_KEYWORDS, scorer=fuzz.partial_ratio) for candidate in ner_candidates]
    fuzzy_skills = {match[0] for match in fuzzy_matches if match and match[1] >= 85}
    return sorted(found_skills | fuzzy_skills)

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def parse_resume(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported file format. Only PDF, DOCX, and TXT supported")

    skills = extract_skills(text)
    entities = extract_entities(text)

    return {
        "file_path": file_path,
        "raw_text": text,
        "skills": skills,
        "entities": entities
    }

if __name__ == "__main__":
    file_path = "/Users/lakshmianand/Desktop/capstone-project/LAKSHMI_RESUME_PLACEMENT.pdf"
    try:
        result = parse_resume(file_path)
        print("Extracted skills:", result["skills"])
        print("Named entities:", result["entities"])
        with open("parsed_resume.txt", "w", encoding="utf-8") as f:
            f.write(result["raw_text"])
    except Exception as e:
        print("Error:", e)
