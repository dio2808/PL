import os
from google import genai
from google.genai.errors import APIError

class RagAgent:
    """
    A Retrieval Augmented Generation (RAG) agent that uses the Gemini model
    to answer questions based on a provided text context (the playbook).
    
    This agent relies on Application Default Credentials (ADC) for authentication.
    """
    def __init__(self, playbook_file_path: str = 'playbook_content.txt'):
        """
        Initializes the agent by reading the internal playbook content.
        
        Args:
            playbook_file_path: Path to the local file containing the knowledge base.
        """
        self.playbook_content = self._load_playbook(playbook_file_path)
        self.client = self._initialize_client()

    def _load_playbook(self, file_path: str) -> str:
        """Loads the text content of the troubleshooting playbook."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Error: Playbook file not found at {file_path}")
            return ""

    def _initialize_client(self) -> genai.Client | None:
        """Initializes the Gemini client using ADC."""
        try:
            # Client relies on ADC (gcloud auth application-default login or Service Account)
            client = genai.Client()
            print("✅ Gemini Client initialized successfully using ADC.")
            return client
        except Exception as e:
            print(f"❌ Failed to initialize Gemini Client. Error: {e}")
            return None

    def generate_response(self, user_query: str) -> str:
        """
        Generates a grounded response using the playbook content as context.
        
        Args:
            user_query: The question from the user.
            
        Returns:
            The model's response text.
        """
        if not self.client:
            return "Error: Cannot generate response, Gemini client is not initialized."
            
        if not self.playbook_content:
            return "Error: Cannot generate response, playbook content is missing or could not be loaded."

        # 1. Construct the RAG Prompt
        system_instruction = (
            "You are an expert Google Cloud Troubleshooter. Your task is to answer the user's "
            "question based ONLY on the provided Cloud Build Troubleshooting Playbook content. "
            "If the answer is not found in the playbook, state clearly that the answer is not available in the playbook. "
            "Be concise and directly address the 'Fix/Mitigation' from the relevant error entry."
        )
        
        full_prompt = (
            f"--- Cloud Build Troubleshooting Playbook ---\n\n"
            f"{self.playbook_content}\n\n"
            f"--- User Query ---\n"
            f"{user_query}"
        )

        # 2. Call the API
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt,
                system_instruction=system_instruction
            )
            return response.text
        
        except APIError as e:
            return f"API Error: {e}. Check Service Account permissions (needs 'Vertex AI User' role)."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

# Example Usage (optional, as main.py will handle execution):
if __name__ == "__main__":
    agent = RagAgent()
    query = "What is the fix for the 'Artifact Registry upload denied' error?"
    print(f"\nQuery: {query}")
    answer = agent.generate_response(query)
    print(f"Response:\n{answer}")
