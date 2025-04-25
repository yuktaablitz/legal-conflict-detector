import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, parse_qs
import re
import ollama
import streamlit as st

# ---- DuckDuckGo search with filtering ----
def duckduckgo_search(name):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f"{name} site:linkedin.com OR site:iccwbo.org OR site:chambers.com OR site:law.com"
    res = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers, timeout=5)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'duckduckgo.com/l/?uddg=' in href:
            parsed = urlparse(href)
            query_params = parse_qs(parsed.query)
            if 'uddg' in query_params:
                real_url = unquote(query_params['uddg'][0])
                if all(x not in real_url for x in ["linkedin.com/", "linkedin.com/in/"]) or "/in/" in real_url:
                    links.append(real_url)

    filtered_links = [url for url in links if not url.rstrip('/').endswith("linkedin.com")]
    st.session_state["debug_links"] = filtered_links[:2]  # Save for display in app
    return filtered_links[:2]

# ---- Extract full text from a page ----
def extract_bio_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=" ").strip()
        text = re.sub(r'\s+', ' ', text)
        st.session_state.setdefault("debug_bios", []).append({"url": url, "length": len(text)})
        return text[:3000]
    except Exception as e:
        st.session_state.setdefault("debug_errors", []).append({"url": url, "error": str(e)})
        return f"[Error fetching bio from {url}]: {e}"

# ---- Summarize bio with LLaMA (using Mistral) ----
def summarize_text_with_llama(raw_text):
    prompt = f"""
Summarize the following profile or bio in 3 sentences, focusing on professional background, affiliations, and past arbitration/legal experience:

Text:
{raw_text[:1000]}
"""
    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "user", "content": prompt}
        ])
        summary = response['message']['content'].strip()
        st.session_state.setdefault("debug_summaries", []).append(summary[:300])
        return summary
    except Exception as e:
        st.session_state.setdefault("debug_errors", []).append({"stage": "llama_summary", "error": str(e)})
        return "Summary failed."

# ---- Final orchestrator with direct state injection ----
def auto_extract_and_summarize_bio(name, role=None):
    links = duckduckgo_search(name)
    previews = []
    best_summary = "No usable bio found."

    for link in links:
        bio = extract_bio_from_url(link)
        if "error" not in bio.lower():
            summary = summarize_text_with_llama(bio)
            previews.append({
                "source": link,
                "summary": summary,
                "full_text": bio
            })
            best_summary = summary
            break

    st.session_state["debug_best_summary"] = best_summary[:300]
    if role in ("arbitrator", "lawyer"):
        st.session_state[f"{role}_bio"] = best_summary  # 🪄 Instant population

    return best_summary, previews
