#!/bin/bash
# One-shot setup: virtual environment, Python packages, the Ollama model, then the app.
# Needs Python 3.10+, Ollama (https://ollama.com/download) and a running Neo4j (docker compose up -d).
set -e

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

[ -f .env ] || cp .env.example .env
ollama pull "${OLLAMA_MODEL:-mistral}"

streamlit run app.py
