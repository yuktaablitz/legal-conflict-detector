import streamlit as st
from bio_scraper import auto_extract_and_summarize_bio
from neo4j_connection import Neo4jConnection
from conflict_classifier import (
    classify_conflict_with_llama,
    get_bio_similarity_score,
    export_conflict_to_pdf,
    extract_text_from_pdf,
    detect_conflicts_in_brief
)
from graph_builder import add_person_to_graph
from graph_visualizer import generate_interactive_graph
import streamlit.components.v1 as components
import plotly.express as px
import pandas as pd

# --- Setup ---
st.set_page_config(page_title="Legal Conflict Detector", layout="centered")
st.title("⚖️ Legal Conflict of Interest Detector")
st.markdown("Analyze potential conflicts using IBA Arbitration Guidelines and GenAI reasoning.")

# --- Neo4j connection ---
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "welcome123")

# --- Session state init ---
for key in ["arb_bio", "lawyer_bio", "arb_sources", "lawyer_sources"]:
    if key not in st.session_state:
        st.session_state[key] = "" if "bio" in key else []

# --- Input form ---
st.subheader("📋 Enter Arbitrator and Lawyer Details")

with st.form("bio_form"):
    arbitrator_name = st.text_input("Arbitrator Name", placeholder="Jane Doe")
    arbitrator_bio = st.text_area("Arbitrator Bio", height=150, value=st.session_state["arb_bio"], placeholder="Paste or auto-fill")

    lawyer_name = st.text_input("Lawyer Name", placeholder="Alex Reed")
    lawyer_bio = st.text_area("Lawyer Bio", height=150, value=st.session_state["lawyer_bio"], placeholder="Paste or auto-fill")

    show_timeline = st.checkbox("📅 Show Affiliation Timeline")
    show_graph = st.checkbox("🕸 Show Interactive Relationship Graph")

    submitted = st.form_submit_button("🧠 Analyze Conflict")

# --- Auto-fill Buttons ---
if st.button("🔍 Auto-fill Arbitrator Bio"):
    with st.spinner("Fetching bio..."):
        auto_extract_and_summarize_bio(arbitrator_name, role="arb")

if st.button("🔍 Auto-fill Lawyer Bio"):
    with st.spinner("Fetching bio..."):
        auto_extract_and_summarize_bio(lawyer_name, role="lawyer")

# --- Upload PDF for Arbitrator ---
st.markdown("#### 📥 Upload Arbitrator Resume (PDF)")
arb_pdf = st.file_uploader("Upload Arbitrator PDF", type=["pdf"], key="arb_pdf")
if arb_pdf and arbitrator_name:
    with st.spinner("Extracting Arbitrator bio from PDF..."):
        text = extract_text_from_pdf(arb_pdf)
        summary = classify_conflict_with_llama(text, "")
        st.session_state["arb_bio"] = summary
        st.success("✅ Arbitrator bio extracted!")

# --- Upload PDF for Lawyer ---
st.markdown("#### 📥 Upload Lawyer Resume (PDF)")
lawyer_pdf = st.file_uploader("Upload Lawyer PDF", type=["pdf"], key="lawyer_pdf")
if lawyer_pdf and lawyer_name:
    with st.spinner("Extracting Lawyer bio from PDF..."):
        text = extract_text_from_pdf(lawyer_pdf)
        summary = classify_conflict_with_llama(text, "")
        st.session_state["lawyer_bio"] = summary
        st.success("✅ Lawyer bio extracted!")

# --- Upload PDF Brief ---
st.markdown("#### 📥 Upload Legal Opinion or Arbitration Brief")
brief_file = st.file_uploader("Upload PDF Brief", type=["pdf"], key="brief")
if brief_file and arbitrator_name:
    with st.spinner("Analyzing legal brief for conflicts involving the arbitrator..."):
        brief_text = extract_text_from_pdf(brief_file)
        brief_result = detect_conflicts_in_brief(brief_text, arbitrator_name)
        st.markdown("### ⚖️ Conflict Detection from Brief")
        st.text_area("Brief Analysis Result", value=brief_result, height=200)

# --- Show sources ---
for role, label in [("arb_sources", "Arbitrator"), ("lawyer_sources", "Lawyer")]:
    if st.session_state.get(role):
        st.markdown(f"#### 🔗 {label} Sources:")
        for preview in st.session_state[role]:
            st.markdown(f"- [{preview['source']}]({preview['source']})")
            st.text_area("Preview", value=preview['summary'], height=100)

# --- Analysis Submission ---
if submitted:
    if ("no usable bio" in arbitrator_bio.lower()) or ("no usable bio" in lawyer_bio.lower()):
        st.error("⚠️ Cannot run analysis: usable bio not found for either arbitrator or lawyer.")
    elif not arbitrator_bio.strip() or not lawyer_bio.strip():
        st.error("⚠️ Please enter bios for both the arbitrator and the lawyer.")
    else:
        with st.spinner("Analyzing using LLaMA..."):
            result = classify_conflict_with_llama(arbitrator_bio, lawyer_bio)

        st.success("✅ Conflict Analysis Complete")
        st.markdown("### 📊 Conflict Assessment")
        st.markdown(result)

        # --- Similarity Score ---
        similarity_score = get_bio_similarity_score(arbitrator_bio, lawyer_bio)
        st.markdown(f"**🧪 Similarity Score (Cosine):** `{similarity_score}`")
        st.caption("A higher score (> 0.5) may suggest overlapping background, work, or risk.")

        # --- PDF Report ---
        pdf_path = export_conflict_to_pdf(arbitrator_name, lawyer_name, result)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button("📄 Download Report as PDF", data=pdf_file, file_name="conflict_report.pdf", mime="application/pdf")

        # --- Update Neo4j Graph ---
        add_person_to_graph(arbitrator_name, arbitrator_bio, "arbitrator")
        add_person_to_graph(lawyer_name, lawyer_bio, "lawyer")

        # --- Show Timeline ---
        if show_timeline:
            timeline_data = pd.DataFrame([
                {"Name": arbitrator_name, "Org": "Smith & Partners LLP", "Start": "2017", "End": "2020"},
                {"Name": lawyer_name, "Org": "Smith & Partners LLP", "Start": "2020", "End": "2024"},
            ])
            timeline_data["Start"] = pd.to_datetime(timeline_data["Start"])
            timeline_data["End"] = pd.to_datetime(timeline_data["End"])

            fig = px.timeline(timeline_data, x_start="Start", x_end="End", y="Name", color="Org")
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

        # --- Show Graph ---
        if show_graph:
            st.markdown("### 🕸 Interactive Relationship Graph")
            html_path = generate_interactive_graph()
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
                components.html(html, height=600, scrolling=True)

# --- Cleanup ---
conn.close()
