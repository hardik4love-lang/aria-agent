#!/usr/bin/env python3
import time
import random
import csv
import httpx
from bs4 import BeautifulSoup

def scrape_products(base_url: str, output_csv: str = "products.csv", max_pages: int = 3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    extracted = []
    with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}" if page > 1 else base_url
            try:
                res = client.get(url)
                if res.status_code != 200:
                    break
                soup = BeautifulSoup(res.text, "html.parser")
                items = soup.select(".product-card, .product-item, .product") or [soup]
                for item in items:
                    title_elem = item.select_one(".product-title, h2, h3")
                    title = title_elem.get_text(strip=True) if title_elem else "Product"
                    extracted.append({"title": title, "page": page})
                time.sleep(random.uniform(1.2, 2.5))
            except Exception as e:
                break

    if extracted:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=extracted[0].keys())
            writer.writeheader()
            writer.writerows(extracted)
    return extracted

if __name__ == "__main__":
    scrape_products("https://example.com/shop")
