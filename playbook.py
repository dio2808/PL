import os
import time
import sys
from google import genai
from google.genai.errors import APIError
from pypdf import PdfReader

# --- Configuration ---
# Your PDF file name. Ensure this file is in the same directory as this script.
PLAYBOOK_FILE = 'CloudBuild Troubleshooting Playbook - Sheet1.pdf' 

# Set a delay for API retry logic
RETRY_DELAY = 1  # seconds

def load_playbook_content(file_path: str) -> str:
    """
    Extracts text content from the specified PDF file using pypdf.
    Returns the extracted text as a single string.
    """
    print(f"--- RAG System: Loading data from {file_path} ---")
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            print(f"Warning: Extracted text from PDF is empty. Check PDF format.")
            return "# Cloud Build Troubleshooting Playbook: No content found in PDF."
            
        print(f"--- RAG System: Successfully extracted {len(text.splitlines())} lines of text. ---")
        
        # Clean up common PDF extraction artifacts (optional cleanup)
        text = text.replace('\r\n', '\n').strip()
        
        return f"# Cloud Build Troubleshooting Playbook (Sourced from {file_path})\n\n{text}"

    except FileNotFoundError:
        print(f"\nERROR: Playbook file not found at path: {file_path}")
        print("Please ensure the PDF file name matches exactly (including case and extension).")
        sys.exit(1) # Exit if the core data source is missing
    except Exception as e:
        print(f"\nERROR: Could not read or parse PDF file: {e}")
        sys.exit(1)


def run_agent(user_query: str, playbook_context: str):
    """
    Initializes the Gemini client (using ADC) and runs the RAG query.
    """
    try:
        # The client automatically uses Application Default Credentials (ADC)
        # when running on GCP or after local 'gcloud auth' setup.
        client = genai.Client()
        print("--- Gemini Client Initialized (using Service Account credentials) ---")
    except Exception as e:
        print(f"ERROR: Failed to initialize Gemini Client: {e}")
        print("Please ensure your Service Account is authenticated locally (gcloud auth) or the VM has the correct role.")
        return

    # 1. Define the System Instruction (Persona + RAG Context)
    system_prompt = f"""
    You are a world-class Cloud Build Troubleshooting Expert. 
    Your primary function is to resolve errors in CI/CD pipelines.

    --- PRIORITY 1: INTERNAL KNOWLEDGE BASE (RAG) ---
    You MUST first attempt to answer the user's query using the following troubleshooting playbook.
    If you find a match, always explain the potential cause and provide the clear, step-by-step remedies from the playbook.

    {playbook_context}

    --- PRIORITY 2: GOOGLE SEARCH GROUNDING ---
    If the internal playbook does NOT contain a relevant answer, use the Google Search tool to find next steps, primarily focusing on official Google Cloud documentation.

    Instructions for Output:
    1. Be concise, professional, and actionable.
    2. Always mention which source was used (Internal Playbook or Google Search).
    """

    # 2. Define the Request Payload
    payload = {
        "contents": [{ "parts": [{ "text": user_query }] }],
        "system_instruction": { "parts": [{ "text": system_prompt }] },
        
        # Enable Google Search grounding as the fallback tool
        "tools": [{ "google_search": {} }],
        
        # Model to use
        "model": "gemini-2.5-flash"
    }

    # 3. Call the Gemini API with Retry Logic
    max_retries = 5
    response = None
    
    for attempt in range(max_retries):
        try:
            print(f"--- Sending query to Gemini (Attempt {attempt + 1}/{max_retries})... ---")
            response = client.models.generate_content(**payload)
            break
        except APIError as e:
            if 'rate limit' in str(e).lower() and attempt < max_retries - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)
                print(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Fatal API Error: {e}")
                return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return


    # 4. Process and Display Response
    if response and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        generated_text = response.text
        
        print("\n" + "="*80)
        print("AGENT RESPONSE:")
        print("="*80)
        print(generated_text)
        print("="*80)

        # Extract and display grounding sources if available
        if response.candidates[0].grounding_metadata and response.candidates[0].grounding_metadata.grounding_attributions:
            sources = response.candidates[0].grounding_metadata.grounding_attributions
            print("\nGROUNDING SOURCES (Used for Fallback Search):")
            for source in sources:
                print(f"- {source.web.title}: {source.web.uri}")
            print("-" * 80)
        else:
            print("\nGROUNDING SOURCES: Only internal playbook context was used (RAG).")
            print("-" * 80)

    else:
        print("\nERROR: No response or empty content received from the model.")


def main():
    """Main execution function."""
    
    # 1. Load the internal playbook content from the PDF
    playbook_context = load_playbook_content(PLAYBOOK_FILE)

    # 2. Define the user's specific query
    # TEST 1: Query covered by the RAG playbook (expect answer from PDF)
    user_query = "I'm seeing a Missing necessary permission iam.serviceAccounts actAs error in my CI/CD pipeline. How do I fix that?"

    # TEST 2: Query NOT covered by the RAG playbook (expect Google Search grounding)
    # user_query = "What is the recommended structure for a secure VPC Service Controls perimeter and how does it affect Cloud Build?" 

    print(f"\nUSER QUERY: {user_query}")
    print("-" * 80)

    # 3. Run the agent with the loaded context and query
    run_agent(user_query, playbook_context)


if __name__ == "__main__":
    main()
