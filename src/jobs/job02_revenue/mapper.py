#!/usr/bin/env python3
"""
Job 02: Revenue by Order - Mapper
Reads olist_order_items_dataset.csv from stdin.
Emits: order_id\tprice,freight_value
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

            order_id = row[0].strip()
            price = float(row[5].strip())
            freight = float(row[6].strip())

            if price < 0 or freight < 0:
                continue

            print("{}\t{:.2f},{:.2f}".format(order_id, price, freight))
        except Exception:
            continue

if __name__ == "__main__":
    main()
