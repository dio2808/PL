from agent import ask_gemini
from sentence_transformers import SentenceTransformer
import chromadb

# Embedding + vector DB
embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./vectordb")
collection = client.get_collection("cloud_errors")

def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Finds top-k most relevant PDF chunks for the query.
    """
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return "\n\n".join(results["documents"][0])

def solve_error(user_query: str) -> str:
    """
    Retrieves context from PDF and asks Gemini to produce a fix.
    """
    context = retrieve_context(user_query)
    prompt = f"""
You are a Google Cloud Build CI/CD troubleshooting assistant.

User Error:
{user_query}

Relevant Documentation:
{context}

Provide:
- Cause
- Step-by-step fix
- Example gcloud commands or YAML if needed
"""
    return ask_gemini(prompt)
