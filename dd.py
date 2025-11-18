# main.py
from agent import rag_agent, ingest_pdf
from google.adk.webserver import run_web_agent

# Ingest PDF once
ingest_pdf()

# Launch local web UI
# Default port: 8000 → open http://localhost:8000 in browser
run_web_agent(rag_agent)
