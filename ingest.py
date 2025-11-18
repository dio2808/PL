import os
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

PDF_PATH = "./data/cloudbuild_errors.pdf"

# Embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Persistent vector DB
client = chromadb.PersistentClient(path="./vectordb")
collection = client.get_or_create_collection("cloud_errors")

def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

def ingest_pdf():
    reader = PdfReader(PDF_PATH)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    chunks = chunk_text(full_text)

    for i, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        collection.add(ids=[str(i)], documents=[chunk], embeddings=[embedding])

    print("✅ PDF successfully indexed!")

if __name__ == "__main__":
    ingest_pdf()
