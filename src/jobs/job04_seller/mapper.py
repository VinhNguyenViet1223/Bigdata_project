#!/usr/bin/env python3
"""
Job 04: Seller Performance - Mapper
Reads olist_order_items_dataset.csv from stdin.
Emits: seller_id\t1,price,freight,value
"""
import sys
import csv

def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        try:
            if not row or len(row) < 7:
                continue
            # Skip CSV header
            if row[0].strip() == "order_id":
                continue

            seller_id = row[3].strip()
            if not seller_id:
                continue

            price = float(row[5].strip())
            freight = float(row[6].strip())

            if price < 0 or freight < 0:
                continue

            value = price + freight
            print("{}\t1,{:.2f},{:.2f},{:.2f}".format(seller_id, price, freight, value))
        except Exception:
            continue

if __name__ == "__main__":
    main()
