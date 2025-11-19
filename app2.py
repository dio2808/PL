# app.py

import os
from dotenv import load_dotenv
import sys

# Add project root for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import Agents
from google.adk.tools import VerttexAISearchTool
from Agent.AgentFactory import AgentFactory, AgentType
from tools.pdf_search import search_pdf
from tools.google_search import google_cloud_docs_search

# Load environment variables from .env
load_dotenv()

# Initialize your ADK Agent using AgentFactory
# You can define your AgentType (for example: LLM agent)
agent: Agents = AgentFactory.create_agent(
    agent_type=AgentType.LLM,  # replace with the appropriate type
    model="gemini-2.0-flash"
)

# Create a VerttexAISearchTool instance if needed
vertex_tool = VerttexAISearchTool(
    name="vertex_search",
    description="Fallback Google Cloud search tool",
)

# CLI loop for user input
if __name__ == "__main__":
    print("\n🤖 Cloud Build Troubleshooting Assistant")
    print("Ask about an error and I’ll check the PDF or Google Docs.\n")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ("exit", "quit"):
            print("👋 Goodbye.")
            break

        # Step 1: Search PDF
        pdf_result = search_pdf(query)

        if "No matching error" in pdf_result:
            # Step 2: Fallback to Vertex AI / Google Docs search
            # Using your tool instance directly
            search_result = vertex_tool.run(query)
            # Or fallback to your Google search function if needed
            response = google_cloud_docs_search(query) + "\n\nVertex AI Result:\n" + search_result
        else:
            response = pdf_result

        print("\nAgent:", response, "\n")
