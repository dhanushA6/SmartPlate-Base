import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from typing import List, Dict, Set, Optional
from collections import deque
import time


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------

def normalize_url(url: str) -> str:
    url, _ = urldefrag(url)
    return url.strip().strip('"').strip("'").rstrip(",")


def is_valid_html(response: requests.Response) -> bool:
    content_type = response.headers.get("Content-Type", "")
    return "text/html" in content_type


def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup([
        "script", "style", "nav",
        "footer", "header", "aside",
        "noscript", "form"
    ]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())


def get_title(html: str, fallback: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        return title_tag.get_text(strip=True)
    return fallback


# ---------------------------------------------------------
# DEEP CRAWLER
# ---------------------------------------------------------

def crawl_website(
    start_url: str,
    max_pages: int = 500,
    max_depth: int = 2,
    delay: float = 0.5,
) -> List[Dict[str, str]]:

    start_url = normalize_url(start_url)

    visited: Set[str] = set()
    queue = deque([(start_url, 0)])
    results: List[Dict[str, str]] = []

    base_domain = urlparse(start_url).netloc

    while queue and len(visited) < max_pages:
        url, depth = queue.popleft()

        if url in visited or depth > max_depth:
            continue

        try:
            print(f"[CRAWLING depth={depth}] {url}")

            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()

            if not is_valid_html(response):
                continue

            visited.add(url)

            html = response.text
            text = clean_text(html)

            if len(text) > 500:
                results.append({
                    "url": url,
                    "title": get_title(html, fallback=url),
                    "content": text,
                    "depth": depth
                })

            soup = BeautifulSoup(html, "html.parser")

            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])
                link = normalize_url(link)
                parsed = urlparse(link)

                if (
                    parsed.scheme in ["http", "https"]
                    and parsed.netloc == base_domain
                    and link not in visited
                ):
                    queue.append((link, depth + 1))

            time.sleep(delay)

        except Exception as e:
            print(f"[ERROR] {url} -> {e}")
            continue

    print(f"[INFO] Crawled {len(results)} pages from {start_url}")
    return results
