from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import PyPDF2

load_dotenv()

# Load PDF locally
PDF_PATH = "docs/error.pdf"  # Put your file inside a 'docs' folder in VS Code project

def load_pdf_text():
    text = ""
    with open(PDF_PATH, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

pdf_text = load_pdf_text()

agent = Agent(
    name="Local PDF Support Agent",
    role=f"You must answer only based on this document:\n\n{pdf_text}",
    model="gemini-1.5-flash",
)

if __name__ == "__main__":
    agent.run()
