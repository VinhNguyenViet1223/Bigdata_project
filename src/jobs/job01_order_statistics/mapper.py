#!/usr/bin/env python3
"""
Job 01: Order Statistics - Mapper
Reads olist_orders_dataset.csv from stdin.
Emits: order_status\t1
"""
import sys
import csv

def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        try:
            if not row or len(row) < 3:
                continue
            # Skip CSV header
            if row[0].strip() == "order_id":
                continue
            order_status = row[2].strip().lower()
            if order_status:
                print("{}\t1".format(order_status))
        except Exception:
            continue

if __name__ == "__main__":
    main()
