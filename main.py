from rag_agent import solve_error

print("🚀 Gemini RAG Cloud Build Helper Ready!")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("❓ Enter Cloud Build error: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    print("\n⏳ Thinking...\n")
    answer = solve_error(user_input)
    print("💡 Suggested Fix:\n")
    print(answer)
    print("\n" + "-"*70 + "\n")
