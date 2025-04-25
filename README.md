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
- **Graph DB**: Neo4j (Desktop)
- **AI Model**: LLaMA via Ollama (Mistral model)
- **Libraries**: `requests`, `beautifulsoup4`, `scikit-learn`, `fpdf`, `plotly`, `fitz` (PyMuPDF), `streamlit`, `ollama`

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

## 📦 One-Click Installer

Use the included `setup.sh` to install dependencies and run the app.

```bash
bash setup.sh
```

---

## 🧪 Sample Names to Test

- Arbitrator: `Marc Isserles`
- Lawyer: `Jennifer Bonjean`

---

## 📤 Deploy on GitHub

1. Create a GitHub repo
2. Add all project files
3. Run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your-username/legal-conflict-detector.git
   git push -u origin main
   ```

---