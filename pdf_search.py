import re
from pypdf import PdfReader

PDF_PATH = "CloudBuildTroubleshootingPlaybook.pdf"

# Load and index PDF only once
reader = PdfReader(PDF_PATH)
pdf_text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        pdf_text += page_text + "\n"


def search_pdf(query: str) -> str:
    """
    Searches PDF text for a matching error code or phrase.
    Uses case-insensitive fuzzy matching.
    """
    if not query.strip():
        return "No query detected."

    pattern = re.compile(re.escape(query), re.IGNORECASE)

    lines = pdf_text.split("\n")

    results = [
        line for line in lines if pattern.search(line)
    ]

    if results:
        return "\n".join(results[:5])  # return top 5 matches

    return "No matching error found in the PDF."
