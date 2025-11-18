from google import genai
from google.auth import default

# Authenticate using Application Default Credentials
credentials, _ = default()
client = genai.Client(credentials=credentials)

def ask_gemini(prompt: str):
    """
    Sends a prompt to Gemini Flash 2.5 and returns the response.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
