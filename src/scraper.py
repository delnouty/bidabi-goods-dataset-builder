"""
OpenFoodFacts product scraper with retry logic, image downloading,
CSV export and category filtering.
"""

import csv
import time
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://world.openfoodfacts.org/cgi/search.pl"
HEADERS = {"User-Agent": "MyAwesomeApp/1.0"}

TARGET_COUNT = 180
PAGE_SIZE = 100
MAX_PAGES = 50
CATEGORY = "champagnes"

OUTPUT_DIR = "data"

# -------------------------
# Session with retry logic
# -------------------------
def create_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = create_session()


# -------------------------
# API Fetching
# -------------------------
def fetch_products(category, page, page_size):
    params = {
        "action": "process",
        "tagtype_0": "categories",
        "tag_contains_0": "contains",
        "tag_0": category,
        "page": page,
        "page_size": page_size,
        "json": 1
    }

    try:
        response = SESSION.get(API_URL, params=params, headers=HEADERS, timeout=(10, 30))
        response.raise_for_status()
        return response.json().get("products", [])
    except Exception as error:
        print(f"⚠ Erreur API page {page} :", error)
        return []


# -------------------------
# Product validation
# -------------------------
def get_best_image(product):
    return (
        product.get("image_url")
        or product.get("image_front_url")
        or product.get("image_small_url")
        or product.get("image_thumb_url")
    )


def is_valid_product(product):
    required = ["_id", "product_name", "categories_tags"]
    if not all(product.get(f) for f in required):
        return False
    return bool(get_best_image(product))


def extract_product_info(product):
    return [
        product.get("_id"),
        product.get("product_name"),
        ", ".join(product.get("categories_tags", [])),
        product.get("ingredients_text", ""),
        get_best_image(product)
    ]


# -------------------------
# Image download
# -------------------------
def download_image(url, image_id, folder="data/images"):
    if not url:
        return

    os.makedirs(folder, exist_ok=True)

    ext = url.split(".")[-1].split("?")[0]
    filename = os.path.join(folder, f"{image_id}.{ext}")

    if os.path.exists(filename):
        return

    try:
        response = SESSION.get(url, headers=HEADERS, timeout=(10, 30))
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
    except Exception as error:
        print(f"⚠ Impossible de télécharger {url} :", error)


# -------------------------
# CSV export
# -------------------------
def save_to_csv(filename, rows):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["foodId", "label", "category", "foodContentsLabel", "image"])
        writer.writerows(rows)


# -------------------------
# Main scraping loop
# -------------------------
def scrape_category(category, target_count, page_size, max_pages):
    valid_products = []
    page = 1

    while len(valid_products) < target_count and page <= max_pages:
        print(f"→ Téléchargement page {page}…")

        products = fetch_products(category, page, page_size)
        if not products:
            print("Aucun produit trouvé sur cette page.")
            break

        for product in products:
            if is_valid_product(product):
                info = extract_product_info(product)
                valid_products.append(info)

                image_url = info[-1]
                image_id = info[0]
                download_image(image_url, image_id)

                if len(valid_products) >= target_count:
                    break

        page += 1
        time.sleep(0.3)

    return valid_products


def main():
    products = scrape_category(CATEGORY, TARGET_COUNT, PAGE_SIZE, MAX_PAGES)

    output_file = f"{OUTPUT_DIR}/metadata_{CATEGORY}_{TARGET_COUNT}.csv"
    save_to_csv(output_file, products)

    print(f"✔ Fichier {output_file} créé. Produits valides collectés : {len(products)}")


if __name__ == "__main__":
    main()
