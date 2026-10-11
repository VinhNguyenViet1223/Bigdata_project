#!/usr/bin/env python3
"""
Job 03: Category Analysis - Mapper (Map-Side Join)
Reads olist_order_items_dataset.csv from stdin.
Joins with olist_products_dataset.csv and product_category_name_translation.csv.
Emits: category\t1,price,freight,value
"""
import sys
import os
import csv

def find_file(filename):
    """Locate reference dimension file in various environments."""
    candidates = [
        filename,                                                    # DistributedCache / current working dir
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", filename), # local repo relative
        os.path.join("/app", "data", filename),                      # Docker container mount
        os.path.join("/data", filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def load_translations(filepath):
    """Loads Portuguese to English category mappings."""
    translations = {}
    if not filepath or not os.path.exists(filepath):
        return translations

    with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            pt = row[0].strip().lstrip("\ufeff")
            en = row[1].strip()
            if pt == "product_category_name":
                continue
            if pt and en:
                translations[pt] = en
    return translations

def load_product_categories(filepath, translations):
    """Maps product_id -> english_category (or fallback)."""
    product_cats = {}
    if not filepath or not os.path.exists(filepath):
        return product_cats

    with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            prod_id = row[0].strip()
            if prod_id == "product_id":
                continue
            pt_cat = row[1].strip()
            if not pt_cat:
                en_cat = "unknown"
            else:
                en_cat = translations.get(pt_cat, pt_cat)
            product_cats[prod_id] = en_cat
    return product_cats

def main():
    trans_path = find_file("product_category_name_translation.csv")
    prod_path = find_file("olist_products_dataset.csv")

    translations = load_translations(trans_path)
    product_map = load_product_categories(prod_path, translations)

    reader = csv.reader(sys.stdin)
    for row in reader:
        try:
            if not row or len(row) < 7:
                continue
            # Skip CSV header
            if row[0].strip() == "order_id":
                continue

            product_id = row[2].strip()
            price = float(row[5].strip())
            freight = float(row[6].strip())

            if price < 0 or freight < 0:
                continue

            category = product_map.get(product_id, "unknown")
            item_value = price + freight

            print("{}\t1,{:.2f},{:.2f},{:.2f}".format(category, price, freight, item_value))
        except Exception:
            continue

if __name__ == "__main__":
    main()
