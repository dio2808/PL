from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
from google.adk.agents import AgentFactory, AgentType
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

load_dotenv()

# --- Step 1: Build vector DB from PDF ---
PDF_PATH = "./data/cloudbuild_errors.pdf"

embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./vectordb")
collection = client.get_or_create_collection("cloud_errors")

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

# --- Step 2: Create RAG search tool ---
search_tool = VertexAiSearchTool(
    name="cloud_build_search",
    collection_name="cloud_errors",
    embedding_model=embedder,
    vector_db_path="./vectordb",
    top_k=3
)

# --- Step 3: Create ADK Agent ---
rag_agent = AgentFactory.create(
    agent_type=AgentType.CHAT,
    tools=[search_tool],
    model_name="gemini-2.5-flash",
    agent_name="CloudBuildRAG"
)
