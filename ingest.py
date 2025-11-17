from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

PDF_PATH = "./data/cloudbuild_errors.pdf"
db = chromadb.PersistentClient(path="./vectordb")
collection = db.get_or_create_collection(name="errors")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def chunk(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

def ingest():
    reader = PdfReader(PDF_PATH)
    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    chunks = chunk(text)

    for i, c in enumerate(chunks):
        embedding = embedder.encode(c).tolist()
        collection.add(ids=[str(i)], documents=[c], embeddings=[embedding])

    print("PDF indexed successfully.")

if __name__ == "__main__":
    ingest()
