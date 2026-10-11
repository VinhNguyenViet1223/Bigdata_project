#!/usr/bin/env python3
"""
Job 06: Delivery Logistics Analysis - Mapper
Reads olist_orders_dataset.csv from stdin.
Emits: DELIVERY_METRICS\tdelivery_days,is_late
"""
import sys
import csv
from datetime import datetime

def main():
    reader = csv.reader(sys.stdin)
    date_format = "%Y-%m-%d %H:%M:%S"

    for row in reader:
        try:
            if not row or len(row) < 8:
                continue
            # Skip CSV header
            if row[0].strip() == "order_id":
                continue

            status = row[2].strip().lower()
            # Only analyze completed deliveries with valid timestamps
            if status != "delivered":
                continue

            purchase_str = row[3].strip()
            delivered_str = row[6].strip()
            estimated_str = row[7].strip()

            if not purchase_str or not delivered_str or not estimated_str:
                continue

            d_purchase = datetime.strptime(purchase_str, date_format)
            d_delivered = datetime.strptime(delivered_str, date_format)
            d_estimated = datetime.strptime(estimated_str, date_format)

            diff_seconds = (d_delivered - d_purchase).total_seconds()
            if diff_seconds < 0:
                continue

            delivery_days = diff_seconds / 86400.0
            is_late = 1 if d_delivered > d_estimated else 0

            print("DELIVERY_METRICS\t{:.2f},{}".format(delivery_days, is_late))
        except Exception:
            continue

if __name__ == "__main__":
    main()
