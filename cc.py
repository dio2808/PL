# agent.py
import chromadb
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

PDF_PATH = "./data/cloudbuild_errors.pdf"

# --- Embed PDF in ChromaDB ---
embedder = SentenceTransformer("all-MiniLM-L6-v2")
client_db = chromadb.PersistentClient(path="./vectordb")

# Safely get or create collection
try:
    collection = client_db.get_collection("cloud_errors")
except ValueError:
    collection = client_db.create_collection("cloud_errors")

def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

def ingest_pdf():
    reader = PdfReader(PDF_PATH)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        collection.add(ids=[str(i)], documents=[chunk], embeddings=[embedding])
    print("✅ PDF ingested!")

# --- Create search tool ---
search_tool = VertexAiSearchTool(
    collection=collection,
    embedding_model=embedder.encode,
    top_k=3
)

# --- Create Agent ---
rag_agent = Agent(
    name="CloudBuildRAG",
    tools=[search_tool],
    model_name="gemini-2.5-flash"
)
