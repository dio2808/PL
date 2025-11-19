# app.py

import sys
import os

# Add project root to PYTHONPATH so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import LlmAgent
from tools.pdf_search import search_pdf
from tools.google_search import google_cloud_docs_search

MODEL_NAME = "gemini-2.0-flash"

# Initialize LlmAgent with only model (required in ADK 1.18.0)
agent = LlmAgent(model=MODEL_NAME)

if __name__ == "__main__":
    print("\n🤖 Cloud Build Troubleshooting Assistant")
    print("Ask about an error and I’ll check the PDF or Google Docs.\n")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        prompt = input("You: ").strip()
        if prompt.lower() in ("exit", "quit"):
            print("👋 Goodbye.")
            break

        # Step 1: Search PDF
        pdf_result = search_pdf(prompt)

        if "No matching error" in pdf_result:
            # Step 2: fallback to Google Cloud Docs
            response = google_cloud_docs_search(prompt)
        else:
            response = pdf_result

        print("\nAgent:", response, "\n")
