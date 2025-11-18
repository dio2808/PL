from google.adk.web import WebAgent
from google.adk.tools import VertexAiSearchTool, Tool
from sentence_transformers import SentenceTransformer
import chromadb
from PyPDF2 import PdfReader
from googlesearch import search  # pip install googlesearch-python

# --- Step 1: Ingest PDF as RAG ---
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
    print("✅ PDF ingested!")

ingest_pdf()

# --- Step 2: Vertex AI Search Tool for PDF ---
pdf_search_tool = VertexAiSearchTool(
    collection=collection,
    embedding_model=embedder.encode,
    top_k=3
)

# --- Step 3: Google Search Tool ---
class GoogleSearchTool(Tool):
    def __init__(self, name="google_search"):
        super().__init__(name=name)

    def run(self, query):
        results = list(search(query, num_results=3))
        if results:
            return "\n".join(results)
        return "No results found on Google."

google_search_tool = GoogleSearchTool()

# --- Step 4: Create WebAgent with multiple tools ---
web_agent = WebAgent(
    name="CloudBuildHybridRAG",
    tools=[pdf_search_tool, google_search_tool],
    model_name="gemini-2.5-flash"
)

# --- Step 5: Launch ADK Web ---
web_agent.launch()
