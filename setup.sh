#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install streamlit beautifulsoup4 requests scikit-learn fpdf plotly pymupdf neo4j ollama

# Start the app
streamlit run app.py
