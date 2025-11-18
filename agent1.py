from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
from sentence_transformers import SentenceTransformer
import chromadb
from PyPDF2 import PdfReader

# --- Step 1: Build Chroma vector DB from PDF ---
PDF_PATH = "./data/cloudbuild_errors.pdf"
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Persistent ChromaDB
client = chromadb.PersistentClient(path="./vectordb")
collection = client.get_or_create_collection("cloud_errors")

def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

def ingest_pdf():
    """Read PDF and store chunks into ChromaDB."""
    reader = PdfReader(PDF_PATH)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        collection.add(ids=[str(i)], documents=[chunk], embeddings=[embedding])
    print("✅ PDF ingested into vector DB!")

# --- Step 2: Create VertexAiSearchTool ---
search_tool = VertexAiSearchTool(
    collection=collection,            # pass Chroma collection directly
    embedding_model=embedder.encode,  # embedding function
    top_k=3
)

# --- Step 3: Create ADK Agent ---
rag_agent = Agent(
    name="CloudBuildRAG",
    tools=[search_tool],
    model_name="gemini-2.5-flash"
)
