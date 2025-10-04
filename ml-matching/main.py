from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import AutoModel, AutoTokenizer
import torch.nn.functional as F

app = FastAPI()

model_name = 'sentence-transformers/all-MiniLM-L6-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

class CandidateJob(BaseModel):
    candidate_resume: str
    job_description: str

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return (token_embeddings * input_mask_expanded).sum(1) / input_mask_expanded.sum(1)

@app.post("/match")
def match_skill(candidate_job: CandidateJob):
    inputs1 = tokenizer(candidate_job.candidate_resume, return_tensors='pt', truncation=True, padding=True)
    inputs2 = tokenizer(candidate_job.job_description, return_tensors='pt', truncation=True, padding=True)

    with torch.no_grad():
        outputs1 = model(**inputs1)
        outputs2 = model(**inputs2)

    emb1 = mean_pooling(outputs1, inputs1['attention_mask'])
    emb2 = mean_pooling(outputs2, inputs2['attention_mask'])

    similarity_score = F.cosine_similarity(emb1, emb2).item()

    return {
        "similarity_score": similarity_score,
        "message": "Semantic similarity computed with HuggingFace transformers directly"
    }
