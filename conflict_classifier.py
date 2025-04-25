import ollama
import re
from fpdf import FPDF
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import fitz  # for PDF reading

# --- Summarize bios to 3 core sentences ---
def summarize_bio(bio):
    sentences = re.split(r'(?<=[.!?]) +', bio)
    return ' '.join(sentences[:3])

# --- Faster, simpler IBA guideline prompt ---
IBA_GUIDELINES = """
Use these IBA arbitration conflict rules:
- 🔴 Red: direct work, same case, financial ties.
- 🟠 Orange: shared org in 3 years, repeated appointments, indirect bias.
- 🟢 Green: no conflict or only minor social/professional contact.

Return: Conflict Level (Red/Orange/Green), Explanation, Key Evidence.
"""

def classify_conflict_with_llama(arbitrator_bio, lawyer_bio):
    prompt = f"""
{IBA_GUIDELINES}

Arbitrator:
{summarize_bio(arbitrator_bio)}

Lawyer:
{summarize_bio(lawyer_bio)}

What is the conflict level and why?
"""

    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "user", "content": prompt}
        ])
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Error using LLaMA model: {e}"

# --- Conflict check from legal brief ---
def detect_conflicts_in_brief(brief_text, known_arbitrator):
    prompt = f"""
You are a legal analyst. A lawyer is submitting a legal opinion or arbitration brief.
Please identify if the following text contains any conflict of interest involving the arbitrator "{known_arbitrator}".

Highlight potential references to the arbitrator, their affiliations, or prior engagements. Use the IBA arbitration conflict categories (Red/Orange/Green).

Text:
{brief_text[:1500]}

What is the conflict type and reasoning?
"""
    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "user", "content": prompt}
        ])
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Error detecting conflict in brief: {e}"

# --- Cosine similarity score ---
def get_bio_similarity_score(bio1, bio2):
    vect = TfidfVectorizer(stop_words="english")
    tfidf = vect.fit_transform([bio1, bio2])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(score, 3)

# --- PDF export ---
def export_conflict_to_pdf(arbitrator_name, lawyer_name, result_text, path="conflict_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Legal Conflict of Interest Report", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Arbitrator: {arbitrator_name}", ln=True)
    pdf.cell(200, 10, txt=f"Lawyer: {lawyer_name}", ln=True)
    pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    for line in result_text.split("\n"):
        pdf.multi_cell(0, 10, txt=line)

    pdf.output(path)
    return path

# --- PDF text extractor for legal briefs ---
def extract_text_from_pdf(file):
    text = ""
    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        return f"[Error extracting PDF text]: {e}"
