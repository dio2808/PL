from google import genai
from google.auth import default
import chromadb
from sentence_transformers import SentenceTransformer

# Authenticate using ADC (no API key needed)
credentials, _ = default()
client = genai.Client(credentials=credentials)

# DB + embeddings
db = chromadb.PersistentClient(path="./vectordb")
collection = db.get_collection("errors")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query):
    embedding = embedder.encode(query).tolist()
    result = collection.query(query_embeddings=[embedding], n_results=3)
    return "\n\n".join(result["documents"][0])

def ask_gemini(user_question):
    context = retrieve(user_question)

    prompt = f"""
You are a Google Cloud Build troubleshooting assistant.

User Question:
{user_question}

Relevant extracted knowledge:
{context}

Respond with:
- Cause
- Fix steps
- Example Cloud Build YAML or gcloud command if useful
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
