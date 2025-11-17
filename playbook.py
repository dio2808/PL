import os
import time
from google import genai
from google.genai.errors import APIError

# --- CONFIGURATION ---
MODEL_NAME = 'gemini-2.5-flash'
MAX_RETRIES = 5
PLAYBOOK_FILE = 'playbook_content.txt'  # File containing the troubleshooting data

def load_playbook_content(filepath):
    """
    Reads the RAG context (troubleshooting playbook) from a local text file.
    In a production system, this would be replaced by a vector database lookup.
    """
    if not os.path.exists(filepath):
        print(f"\n[FATAL ERROR] Playbook file not found at: {filepath}")
        print("Please ensure you have created the 'playbook_content.txt' file in the same directory.")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"\n[FATAL ERROR] Could not read playbook file: {e}")
        return None

def get_system_instruction(playbook_context):
    """Defines the agent's role, priority, and injects the loaded knowledge base."""
    if not playbook_context:
        # Fallback instruction if the file couldn't be loaded
        return "You are a Cloud Build CI/CD Troubleshooting Agent. You must use the Google Search tool to find solutions as the internal playbook is unavailable."

    return f"""
    You are a highly specialized Cloud Build CI/CD Troubleshooting Agent.
    Your primary goal is to help the user resolve their pipeline errors.

    **KNOWLEDGE BASE (Priority 1: Use this context first):**
    {playbook_context}

    **INSTRUCTIONS:**
    1. First, search your KNOWLEDGE BASE for the user's error. If a matching cause and remedy are found, provide that answer directly.
    2. If the answer is not in the KNOWLEDGE BASE, use the Google Search tool to find a solution, focusing specifically on official Google Cloud documentation.
    3. Always explain the potential cause and provide clear, step-by-step remedies.
    4. Maintain a professional, helpful, and concise tone.
    """

def run_agent(user_query: str, playbook_context: str):
    """
    Initializes the Gemini client, constructs the prompt, and gets the response.
    """
    print(f"-> Agent Initialized. Query: '{user_query}'")

    try:
        # Initialize the client. The SDK automatically picks up the API key.
        client = genai.Client()
    except Exception as e:
        print("\n[ERROR] Failed to initialize Gemini Client. Check if the GEMINI_API_KEY environment variable is set correctly.")
        print(f"Details: {e}")
        return

    # --- Constructing the Full Prompt and Configuration ---
    
    system_instruction = get_system_instruction(playbook_context)
    tools = [{"google_search": {}}]
    contents = [user_query]
    
    response = None
    for attempt in range(MAX_RETRIES):
        try:
            print(f"-> Attempt {attempt + 1}/{MAX_RETRIES}: Calling Gemini API...")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=tools
                )
            )
            # If successful, break the loop
            break
        except APIError as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt
                print(f"   [WARNING] API Error ({e.status_code}). Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"\n[FATAL ERROR] All API attempts failed after {MAX_RETRIES} retries.")
                print(f"Details: {e}")
                return
        except Exception as e:
            print(f"\n[FATAL ERROR] An unexpected error occurred: {e}")
            return


    # --- Process and Display Results ---
    
    if not response or not response.text:
        print("\n[INFO] Agent could not find a definitive answer or generate content.")
        return

    print("\n" + "="*80)
    print(f"Agent Response (Model: {MODEL_NAME})\n")
    print(response.text)
    print("="*80)

    # Display Grounding Metadata (sources from Google Search)
    grounding_metadata = response.candidates[0].grounding_metadata
    if grounding_metadata and grounding_metadata.grounding_chunks:
        # Extract unique URIs from the grounding chunks
        sources = [c.web.uri for c in grounding_metadata.grounding_chunks if c.web]
        if sources:
            print("\n[INFO] Sources Used (Google Search Grounding):")
            for i, source in enumerate(sorted(list(set(sources)))):
                print(f"  {i+1}. {source}")
        else:
            print("\n[INFO] Response was generated primarily from the internal Playbook Context (RAG).")
    else:
        print("\n[INFO] Response was generated primarily from the internal Playbook Context (RAG).")


def main():
    """Main function to simulate user interaction."""
    
    print("--- Cloud Build Agent Simulation ---")
    
    # 1. Load the playbook content from the external file
    playbook_context = load_playbook_content(PLAYBOOK_FILE)
    if not playbook_context:
        print("Cannot run agent without playbook content.")
        return
    
    # --- RAG Test Case (Answer in the Playbook) ---
    # The agent should use the playbook_content.txt for this answer.
    # Change this query to test different errors from your playbook!
    user_input = "I'm seeing a Missing necessary permission iam.serviceAccounts actAs error in my CI/CD pipeline. How do I fix that?"

    # --- Search Test Case (Answer not in the Playbook) ---
    # The agent should use the Google Search tool for this answer.
    # user_input = "How do I secure my GKE cluster with binary authorization?"

    run_agent(user_input, playbook_context)
    print("\n--- Simulation Complete ---")

if __name__ == "__main__":
    main()