import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import unquote, urlparse, parse_qs

def scrape_bio(name):
    print(f"Searching for {name}...")
    query = f"{name} site:linkedin.com OR site:iccwbo.org OR site:chambers.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # DuckDuckGo wraps URLs, we extract true URL from 'uddg' parameter
    real_urls = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'duckduckgo.com/l/?uddg=' in href:
            parsed = urlparse(href)
            query_params = parse_qs(parsed.query)
            if 'uddg' in query_params:
                real_url = unquote(query_params['uddg'][0])
                real_urls.append(real_url)

    if not real_urls:
        return {"name": name, "bio": "No bio found from search results."}

    try:
        profile_url = real_urls[0]
        print(f"Found: {profile_url}")
        profile = requests.get(profile_url, headers=headers, timeout=10)
        soup_profile = BeautifulSoup(profile.text, 'html.parser')
        text = soup_profile.get_text(separator="\n")
        text = re.sub(r'\n+', '\n', text)
        return {
            "name": name,
            "bio": text[:2000]  # Limit for performance
        }
    except Exception as e:
        return {"name": name, "bio": f"Error fetching profile: {e}"}
