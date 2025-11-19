def google_cloud_docs_search(query: str) -> str:
    """
    Searches Google Cloud documentation for Cloud Build errors.
    Returns a link to Google Cloud search as a fallback.
    """
    if not query.strip():
        return "No query detected."

    return f"No PDF match — Try Google Docs:\nhttps://cloud.google.com/search?q={query.replace(' ', '+')}"
