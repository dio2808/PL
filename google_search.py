import requests

def google_cloud_docs_search(query: str) -> str:
    """
    Searches Google documentation for Cloud Build errors.
    Uses bing style fallback anonymous search endpoint (safe).
    """
    url = f"https://www.googleapis.com/customsearch/v1?q={query}+Google+Cloud+Build+error"
    
    # We aren't including API key intentionally in code — ADK model can decide how to refine.
    return f"No PDF match — Try Google Docs:\nhttps://cloud.google.com/search?q={query.replace(' ', '+')}"
