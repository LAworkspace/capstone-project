# explainability_module.py

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# Use the same model consistent with embedding_module.py
model = SentenceTransformer("all-mpnet-base-v2")

kw_model = KeyBERT(model=model)

def extract_keywords(text, top_n=10):
    """
    Extract top keywords/keyphrases from text.
    """
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words='english', 
        top_n=top_n,
        use_mmr=True,       # Use Maximal Marginal Relevance to diversify
        diversity=0.7       # Control diversity of results
    )
    return keywords

if __name__ == "__main__":
    with open("parsed_resume.txt", "r", encoding="utf-8", errors="ignore") as f:
        resume_text = f.read()
    with open("job_description.txt", "r", encoding="utf-8") as f:
        job_text = f.read()

    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_text)

    print("Resume Keywords:")
    for kw, score in resume_keywords:
        print(f"{kw} (score: {score:.4f})")

    print("\nJob Description Keywords:")
    for kw, score in job_keywords:
        print(f"{kw} (score: {score:.4f})")
