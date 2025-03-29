import mlflow
import spacy
from sentence_transformers import SentenceTransformer, util

# Load NLP models
nlp = spacy.load("en_core_web_sm")  
bert_model = SentenceTransformer("all-MiniLM-L6-v2")  # For similarity scoring

# Function to extract keywords from text
def extract_keywords(text):
    doc = nlp(text.lower())
    return {token.lemma_ for token in doc if token.is_alpha and not token.is_stop}

# Function to calculate ATS Match Score (keyword overlap)
def calculate_ats_match(job_desc, resume):
    job_keywords = extract_keywords(job_desc)
    resume_keywords = extract_keywords(resume)
    common_keywords = job_keywords.intersection(resume_keywords)
    return (len(common_keywords) / len(job_keywords)) * 100 if job_keywords else 0

# Function to compute semantic similarity using BERT embeddings
def compute_similarity(job_desc, response):
    emb1 = bert_model.encode(job_desc, convert_to_tensor=True)
    emb2 = bert_model.encode(response, convert_to_tensor=True)
    return util.pytorch_cos_sim(emb1, emb2).item()

# Function to log evaluation results in MLflow
def log_ats_evaluation(job_desc, resume, model_response):
    ats_match = calculate_ats_match(job_desc, resume)
    coherence = compute_similarity(job_desc, model_response)

    with mlflow.start_run():
        mlflow.log_param("Job Description", job_desc)
        mlflow.log_param("Resume Content", resume)
        mlflow.log_text(model_response, "Generated Response")

        # Log metrics
        mlflow.log_metric("ATS Match Score", ats_match)
        mlflow.log_metric("Semantic Coherence", coherence)

        print(f"Logged: ATS Match={ats_match:.2f}%, Coherence={coherence:.2f}")

    return ats_match, coherence
