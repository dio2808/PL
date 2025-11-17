from agent import ask_gemini

print("\n🚀 Gemini RAG Cloud Build Helper Ready!")
print("Type 'exit' to quit.\n")

while True:
    query = input("❓ Enter Cloud Build error: ")

    if query.lower() == "exit":
        break

    print("\n⏳ Thinking...\n")
    answer = ask_gemini(query)
    
    print("💡 Suggested Fix:\n")
    print(answer)
    print("\n" + "-"*70 + "\n")
