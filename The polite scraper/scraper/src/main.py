import os
import requests

USER_AGENT = "FlyRankInternshipA9/1.0 (https://github.com/KrzysDev/Flyrank-Internship-Assignments)"
TIMEOUT_SECONDS = 10
CACHE_DIR = "cache"
CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")


def fetch_with_cache(url: str, cache_path: str) -> str:
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT: {cache_path} ({len(html)} bytes)")
        return html

    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url}: status {response.status_code}")

    html = response.text

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"FETCH: {url} ({len(html)} bytes)")
    return html


def main():
    html = fetch_with_cache(CATALOGUE_URL, CACHE_FILE)
    print(f"Loaded page, total length: {len(html)} characters")


if __name__ == "__main__":
    main()