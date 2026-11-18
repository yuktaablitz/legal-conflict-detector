# ⚖️ Legal Conflict of Interest Detector

A GenAI-powered tool to help legal professionals identify potential conflicts of interest between arbitrators and lawyers using public bios, resumes, and legal briefs.

---

## 🚀 Features

- 🧠 **AI-Powered Conflict Analysis** using LLaMA (Mistral) based on IBA guidelines
- 🔍 **Web Bio Extraction** via DuckDuckGo and summarization using LLaMA
- 📥 **PDF Uploads** for resumes and legal opinions
- 🧾 **Similarity Scoring** using TF-IDF and cosine similarity
- 🕸 **Neo4j Relationship Graph** with interactive visual output
- 📅 **Affiliation Timelines** visualized using Plotly
- 📄 **PDF Report Export** of the analysis

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Graph DB**: Neo4j (Desktop or Docker)
- **AI Model**: LLaMA via Ollama (Mistral model)
- **Libraries**: `requests`, `beautifulsoup4`, `scikit-learn`, `fpdf`, `plotly`, `fitz` (PyMuPDF), `pyvis`, `networkx`, `neo4j`, `streamlit`, `ollama`

---

## 🧠 Workflow / Algorithm

1. User enters arbitrator and lawyer names
2. Tool scrapes and summarizes their bios (or allows PDF upload)
3. Bios are stored and visualized as Neo4j nodes with affiliations
4. LLaMA classifies conflict level based on IBA guidelines
5. Cosine similarity checks overlapping affiliations or patterns
6. Legal briefs can be uploaded to detect textual conflicts
7. Results are shown, graphed, and exported as PDF

---

## 👤 Target Users

- Arbitration lawyers
- Legal compliance teams
- Legal research students
- International arbitration institutions

---

## 🛠️ Setup

You need Python 3.10+, [Ollama](https://ollama.com/download) for the local LLM, and Neo4j (Docker is easiest).

```bash
git clone https://github.com/yuktaablitz/legal-conflict-detector.git
cd legal-conflict-detector

# 1. Python environment
python3 -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Settings (Neo4j credentials, Ollama model)
cp .env.example .env

# 3. Local LLM
ollama pull mistral

# 4. Neo4j: Docker, or Neo4j Desktop with the same credentials as .env
docker compose up -d

# 5. Run
streamlit run app.py          # http://localhost:8501
```

Or run `bash setup.sh` to do steps 1-3 and 5 in one go (start Neo4j first).

---

## 📂 Project layout

```
app.py                  Streamlit UI: inputs, analysis, graph, timeline, PDF export
bio_scraper.py          DuckDuckGo search + page scraping, bio summarised by the local LLM
scraper.py              simpler bio scraper used by the tests
conflict_classifier.py  LLM conflict classification (IBA guidelines), TF-IDF similarity, brief scanning, PDF report
graph_builder.py        writes people and affiliations to Neo4j
graph_visualizer.py     reads the graph from Neo4j and renders it with PyVis (graph.html)
neo4j_connection.py     Neo4j driver wrapper (credentials from .env)
data/sample_bios.json   sample bios for testing without scraping
test_*.py               small manual checks for scraping, graph and classification
```

---

## 🧪 Sample Names to Test

- Arbitrator: `Marc Isserles`
- Lawyer: `Jennifer Bonjean`

Web search results change over time; if scraping finds nothing, upload a PDF bio instead.

---

*This tool supports a human conflict check. It is not legal advice.*
