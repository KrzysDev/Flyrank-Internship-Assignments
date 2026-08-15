## Target classification

**Site:** Books to Scrape (https://books.toscrape.com)

**Why this site:** Books to Scrape is a public sandbox built explicitly for 
practicing web scraping — the homepage states it exists for exactly this 
purpose. It is not a real business, so there are no real users, customers, 
or commercial data at risk.

**Scope:** Only the first 3 catalogue pages (https://books.toscrape.com/
catalogue/page-1.html through page-3.html), plus the 60 individual book 
detail pages linked from those 3 pages. No other pages or sections of the 
site are accessed.

**Data collected:** For each book — title, price, availability, star 
rating, description, and product URL. All of this is publicly visible 
text already present in the page's HTML; nothing behind a login or paywall.

**robots.txt check:** Requested `https://books.toscrape.com/robots.txt` 
on 2026-08-15 — the server returned a 404 (file not found). No robots 
file found. This is not an explicit permission, but combined with the 
site's own stated purpose as a scraping sandbox, scraping a small, 
publicly listed set of pages at a polite rate is appropriate here.

**Ethics note:** I will not reuse this code on another site without 
checking its rules and terms first.