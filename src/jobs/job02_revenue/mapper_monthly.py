#!/usr/bin/env python3
"""
Job 02: Monthly Revenue & Trend - Mapper (Map-Side Cache Join)
Reads olist_order_items_dataset.csv from stdin.
Caches olist_orders_dataset.csv to map order_id -> YYYY-MM (order_purchase_timestamp).
Emits: YYYY-MM\t1,price,freight,total_value
"""
import sys
import os
import csv

def find_orders_file():
    candidates = [
        "olist_orders_dataset.csv",
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "olist_orders_dataset.csv"),
        os.path.join("/app", "data", "olist_orders_dataset.csv"),
        os.path.join("/data", "olist_orders_dataset.csv"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def load_orders_date_map(filepath):
    order_dates = {}
    if not filepath or not os.path.exists(filepath):
        return order_dates
    with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 4:
                continue
            oid = row[0].strip()
            if oid == "order_id":
                continue
            ts = row[3].strip()
            if len(ts) >= 7:
                order_dates[oid] = ts[:7]  # YYYY-MM
    return order_dates

def main():
    orders_path = find_orders_file()
    orders_map = load_orders_date_map(orders_path)

    reader = csv.reader(sys.stdin)
    for row in reader:
        try:
            if not row or len(row) < 7:
                continue
            if row[0].strip() == "order_id":
                continue

            order_id = row[0].strip()
            shipping_date = row[4].strip()
            price = float(row[5].strip())
            freight = float(row[6].strip())

            if price < 0 or freight < 0:
                continue

            # Priority 1: order_purchase_timestamp from orders dataset
            # Priority 2: shipping_limit_date from items dataset
            month = orders_map.get(order_id)
            if not month and len(shipping_date) >= 7:
                month = shipping_date[:7]
            if not month:
                month = "Unknown"

            item_val = price + freight
            print("{}\t1,{:.2f},{:.2f},{:.2f}".format(month, price, freight, item_val))
        except Exception:
            continue

if __name__ == "__main__":
    main()
