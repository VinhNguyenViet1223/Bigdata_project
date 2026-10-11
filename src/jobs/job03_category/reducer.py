#!/usr/bin/env python3
"""
Job 03: Category Analysis - Reducer
Reads sorted (category\t1,price,freight,value) pairs from stdin.
Aggregates and emits: category\ttotal_items\ttotal_price\ttotal_freight\ttotal_value
"""
import sys

def main():
    current_category = None
    total_items = 0
    total_price = 0.0
    total_freight = 0.0
    total_value = 0.0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            category, metrics = line.split("\t", 1)
            cnt_str, price_str, freight_str, value_str = metrics.split(",")
            cnt = int(cnt_str)
            price = float(price_str)
            freight = float(freight_str)
            value = float(value_str)
        except (ValueError, IndexError):
            continue

        if current_category == category:
            total_items += cnt
            total_price += price
            total_freight += freight
            total_value += value
        else:
            if current_category is not None:
                print("{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
                    current_category, total_items, total_price, total_freight, total_value
                ))
            current_category = category
            total_items = cnt
            total_price = price
            total_freight = freight
            total_value = value

    if current_category is not None:
        print("{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
            current_category, total_items, total_price, total_freight, total_value
        ))

if __name__ == "__main__":
    main()
