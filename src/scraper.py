"""
OpenFoodFacts product scraper with retry logic, image downloading,
CSV export and category filtering.

Adapted for the bidabi-goods-dataset-builder project:
- images saved to data/images/
- metadata saved to data/metadata.csv
"""

import csv
import time
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://world.openfoodfacts.org/category/{category}.json"
HEADERS = {"User-Agent": "BidabiDatasetBuilder/1.0"}

TARGET_COUNT = 180
PAGE_SIZE = 100
MAX_PAGES = 50
CATEGORY = "champagnes"

IMAGES_DIR = "data/images"
METADATA_FILE = "data/metadata.csv"


# --- Session with retry ---
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


def fetch_page(category, page, page_size):
    url = BASE_URL.format(category=category)
    params = {"page": page, "page_size": page_size, "json": 1}

    try:
        response = SESSION.get(url, params=params, headers=HEADERS, timeout=(10, 30))
        response.raise_for_status()
        return response.json().get("products", [])
    except Exception as error:
        print(f"⚠ Ошибка API на странице {page}: {error}")
        return []


def get_best_image(product):
    return (
        product.get("image_url")
        or product.get("image_front_url")
        or product.get("image_small_url")
        or product.get("image_thumb_url")
    )


def is_valid_product(product):
    required_fields = ["_id", "product_name", "categories_tags"]
    for field in required_fields:
        if not product.get(field):
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


def save_to_csv(filename, rows):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["foodId", "label", "category", "foodContentsLabel", "image"])
        writer.writerows(rows)


def download_image(image_url, image_id, folder=IMAGES_DIR):
    os.makedirs(folder, exist_ok=True)

    ext = image_url.split(".")[-1].split("?")[0]
    filename = os.path.join(folder, f"{image_id}.{ext}")

    if os.path.exists(filename):
        return

    try:
        response = SESSION.get(image_url, headers=HEADERS, timeout=(10, 30))
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)

    except Exception as error:
        print(f"⚠ Не удалось скачать изображение {image_url}: {error}")


def main():
    valid_products = []
    page = 1

    while len(valid_products) < TARGET_COUNT and page <= MAX_PAGES:
        print(f"→ Загрузка страницы {page}…")

        products = fetch_page(CATEGORY, page, PAGE_SIZE)
        if not products:
            print("Нет продуктов на этой странице.")
            break

        for product in products:
            if is_valid_product(product):
                info = extract_product_info(product)
                valid_products.append(info)

                image_url = info[-1]
                image_id = info[0]
                download_image(image_url, image_id)

            if len(valid_products) == TARGET_COUNT:
                break

        page += 1
        time.sleep(0.3)

    save_to_csv(METADATA_FILE, valid_products)

    print(
        f"✔ Файл {METADATA_FILE} создан. "
        f"Собрано валидных продуктов: {len(valid_products)}"
    )


if __name__ == "__main__":
    main()
