from google.adk.agent import Agent
from google.adk.models.gemini import GeminiModel
from google.adk.tools import Tool

from tools.pdf_search import search_pdf
from tools.google_search import google_cloud_docs_search

model = GeminiModel("gemini-2.0-flash")


# Tools registered to agent
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

agent = Agent(
    model=model,
    tools=[search_pdf_tool, fallback_google_tool],
    memory=True
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
