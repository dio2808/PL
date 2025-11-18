from agent import rag_agent, ingest_pdf

# Step 1: Ingest PDF once
ingest_pdf()

print("🚀 Cloud Build ADK RAG Agent Ready! Type 'exit' to quit.\n")

while True:
    query = input("❓ Enter Cloud Build error: ")
    if query.lower() in ["exit", "quit"]:
        break

    # Step 2: Run agent to get solution
    response = rag_agent.run(query)

    print("\n💡 Suggested Fix:\n")
    print(response)
    print("\n" + "-"*70 + "\n")
