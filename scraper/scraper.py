import os
import time
import requests
import feedparser
from tqdm import tqdm


ARXIV_API_URL = "https://export.arxiv.org/api/query"
CATEGORY = "cat:cs.CL"
MAX_RESULTS = 50
PDF_DIR = "cscl_pdfs"
REQUEST_DELAY = 3 

os.makedirs(PDF_DIR, exist_ok=True)

params = {
    "search_query": CATEGORY,
    "start": 0,
    "max_results": MAX_RESULTS,
    "sortBy": "submittedDate",
    "sortOrder": "descending"
}

response = requests.get(ARXIV_API_URL, params=params)
feed = feedparser.parse(response.text)

print(f"Found {len(feed.entries)} entries")

downloaded = 0

for entry in tqdm(feed.entries):
    arxiv_id = entry.id.split("/")[-1]

    has_pdf = False
    for link in entry.links:
        if getattr(link, "title", "") == "pdf":
            has_pdf = True
            break

    if not has_pdf:
        continue 

    pdf_url = f"https://export.arxiv.org/pdf/{arxiv_id}.pdf"
    pdf_path = os.path.join(PDF_DIR, f"{arxiv_id}.pdf")

    if os.path.exists(pdf_path):
        continue

    try:
        r = requests.get(pdf_url, stream=True, timeout=30)
        if r.status_code == 200 and "application/pdf" in r.headers.get("Content-Type", ""):
            with open(pdf_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            downloaded += 1
            time.sleep(REQUEST_DELAY)

        if downloaded >= 50:
            break

    except Exception as e:
        print(f"Failed to download {arxiv_id}: {e}")

print(f"\nDownloaded {downloaded} full PDFs into '{PDF_DIR}'")
