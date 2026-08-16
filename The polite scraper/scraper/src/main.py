import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

USER_AGENT = "FlyRankInternshipA9/1.0 (https://github.com/KrzysDev/Flyrank-Internship-Assignments)"
TIMEOUT_SECONDS = 10
CACHE_DIR = "cache"
CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-1.html"


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


def find_sublinks(html: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select("h3 a")

    urls = []
    for link in links:
        href = link["href"]
        absolute_url = urljoin(page_url, href)
        urls.append(absolute_url)   # <- brakujący krok

    return urls


def find_next_page(html: str, page_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if next_link:
        return urljoin(page_url, next_link["href"])
    return None


def main():
    all_book_urls = []
    current_url = CATALOGUE_URL
    page_number = 1

    while current_url and page_number <= 3:
        cache_path = os.path.join(CACHE_DIR, f"catalogue-page-{page_number}.html")
        html = fetch_with_cache(current_url, cache_path)

        book_urls = find_sublinks(html, current_url)
        all_book_urls.extend(book_urls)

        current_url = find_next_page(html, current_url)
        page_number += 1

    unique_urls = set(all_book_urls)
    print(f"catalogue_pages={page_number - 1}, discovered={len(all_book_urls)}, unique_urls={len(unique_urls)}")


if __name__ == "__main__":
    main()