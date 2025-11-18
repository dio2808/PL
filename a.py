# agent.py
import chromadb
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from google.genai import client as genai_client
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

PDF_PATH = "./data/cloudbuild_errors.pdf"

# --- Step 1: Embed PDF into ChromaDB ---
embedder = SentenceTransformer("all-MiniLM-L6-v2")
client_db = chromadb.PersistentClient(path="./vectordb")
collection = client_db.get_or_create_collection("cloud_errors")

def chunk_text(text, size=500):
    """Split text into chunks for RAG."""
    return [text[i:i+size] for i in range(0, len(text), size)]

def ingest_pdf():
    """Read PDF and store chunks in ChromaDB."""
    reader = PdfReader(PDF_PATH)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        collection.add(ids=[str(i)], documents=[chunk], embeddings=[embedding])
    print("✅ PDF ingested into vector DB!")

# --- Step 2: Create Vertex AI Search Tool ---
search_tool = VertexAiSearchTool(
    collection=collection,
    embedding_model=embedder.encode,
    top_k=3
)

# --- Step 3: Create RAG Agent ---
rag_agent = Agent(
    name="CloudBuildRAG",
    tools=[search_tool],
    model_name="gemini-2.5-flash"
)
