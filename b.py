# main.py
from agent import rag_agent, ingest_pdf

# Step 1: Ingest PDF (run once)
ingest_pdf()

print("🚀 Cloud Build RAG Agent Ready! Type 'exit' to quit.\n")

# Step 2: Chat loop
while True:
    query = input("❓ Enter Cloud Build error: ")
    if query.lower() in ["exit", "quit"]:
        break

    response = rag_agent.run(query)
    print("\n💡 Suggested Fix:\n")
    print(response)
    print("\n" + "-"*70 + "\n")
