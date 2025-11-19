# app.py

from google.adk.agents import Agent  # LlmAgent alias
from google.adk.tools import Tool

from tools.pdf_search import search_pdf
from tools.google_search import google_cloud_docs_search

# Initialize the model by passing the model name string
MODEL_NAME = "gemini-2.0-flash"

# Tools registered to the agent
search_pdf_tool = Tool(
    name="search_pdf",
    func=search_pdf,
    description="Searches the Cloud Build Troubleshooting PDF for an error or related text.",
    args_schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    },
)

fallback_google_tool = Tool(
    name="google_search",
    func=google_cloud_docs_search,
    description="Fallback search in Google Cloud official documentation if PDF doesn't contain the answer.",
    args_schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    },
)

# Create the LLM agent
agent = Agent(
    model=MODEL_NAME,
    name="cloud_build_assistant",
    description="Assists with Cloud Build troubleshooting.",
    tools=[search_pdf_tool, fallback_google_tool],
    instruction=(
        "You are a helpful Cloud Build troubleshooting assistant. "
        "Use the search_pdf tool first. If you can't find the answer, use google_search."
    ),
    memory=True  # if you want the agent to remember context
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
