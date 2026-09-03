#!/usr/bin/env python3

import sys
import csv

reader = csv.reader(sys.stdin)

for row in reader:
    # Bỏ qua dòng header
    if row and row[0] == "order_id":
        continue

    # CSV Olist:
    # 0 = order_id
    # 1 = customer_id
    # 2 = order_status

    if len(row) > 2:
        order_status = row[2].strip()

        if order_status:
            print(f"{order_status}\t1")