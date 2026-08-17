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

from datetime import datetime, timezone

def extract_raw_records(cache_path: str, product_url: str, source_page: str):
    if not os.path.exists(cache_path):
        print("ERROR: Cache not found")
        return None

    with open(cache_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("div.product_main h1").text.strip()

    price_text = soup.select_one("p.price_color").text.strip()

    availability_text = soup.select_one("p.instock.availability").text.strip()

    rating_tag = soup.select_one("p.star-rating")
    rating_classes = rating_tag.get("class") 
    rating_text = rating_classes[1]

    description_header = soup.select_one("#product_description")

    if description_header:
        description = description_header.find_next_sibling("p").text.strip()
    else:
        description = None

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    all_book_urls = []

    current_url = CATALOGUE_URL
    page_number = 1

    while current_url and page_number <= 3:
        cache_path = os.path.join(CACHE_DIR, f"catalogue-page-{page_number}.html")
        html = fetch_with_cache(current_url, cache_path)

        book_urls = find_sublinks(html, current_url)
        all_book_urls.extend(book_urls)

        source_page = current_url          
        current_url = find_next_page(html, current_url)
        page_number += 1

    unique_urls = list(set(all_book_urls))
    print(f"catalogue_pages={page_number - 1}, discovered={len(all_book_urls)}, unique_urls={len(unique_urls)}")

    all_records = []
    for i, book_url in enumerate(unique_urls, start=1):
        book_cache_path = os.path.join(CACHE_DIR, f"book-{i}.html")
        fetch_with_cache(book_url, book_cache_path)   

        record = extract_raw_records(
            cache_path=book_cache_path,
            product_url=book_url,
            source_page=CATALOGUE_URL   
        )
        all_records.append(record)

    print(f"detail_pages={len(all_records)}")
    print(all_records)  


if __name__ == "__main__":
    main()