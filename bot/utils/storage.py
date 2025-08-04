import json
from pathlib import Path

DATA_FILE = Path("data/products.json")

def load_products():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    return []
                return json.loads(data)
        except json.JSONDecodeError:
            return []
    return []

def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

def get_next_id():
    products = load_products()
    if not products:
        return 1
    return max(product.get("id", 0) for product in products) + 1

def get_product_by_id_or_name(query):
    products = load_products()
    query = str(query).strip().lower()
    for product in products:
        if str(product.get("id")) == query or product.get("title", "").lower() == query:
            return product
    return None

def update_product(product_id, new_data):
    products = load_products()
    for i, product in enumerate(products):
        if product.get("id") == product_id:
            products[i].update(new_data)
            save_products(products)
            return True
    return False

def delete_product(product_id):
    products = load_products()
    updated = [p for p in products if p.get("id") != product_id]
    if len(products) == len(updated):
        return False
    save_products(updated)
    return True
