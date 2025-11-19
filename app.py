import sys
import os

# Add project root to PYTHONPATH for VS Code / imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import LlmAgent
from tools.pdf_search import search_pdf
from tools.google_search import google_cloud_docs_search

MODEL_NAME = "gemini-2.0-flash"

# Create the LLM agent
agent = LlmAgent(
    model=MODEL_NAME,
    name="cloud_build_assistant",
    description="Assists with Cloud Build troubleshooting.",
    tools=[search_pdf, google_cloud_docs_search],  # functions directly
    instruction=(
        "You are a helpful Cloud Build troubleshooting assistant. "
        "Use search_pdf first. If the PDF doesn't contain the answer, "
        "use google_cloud_docs_search."
    ),
    memory=True  # remember context
)

if __name__ == "__main__":
    print("\n🤖 Cloud Build Troubleshooting Assistant")
    print("Ask about an error and I’ll check the PDF or Google Docs.\n")
    print("Example: `cloudbuild.builds.create denied`\n")

    while True:
        prompt = input("You: ")
        if prompt.lower() in ("exit", "quit"):
            print("👋 Goodbye.")
            break

        response = agent.run(prompt)
        print("\nAgent:", response, "\n")
