#!/usr/bin/env python3
"""
Job 04: Seller Performance - Reducer
Reads sorted (seller_id\t1,price,freight,value) pairs from stdin.
Aggregates and emits: seller_id\ttotal_items\ttotal_price\ttotal_freight\ttotal_value
"""
import sys

def main():
    current_seller = None
    total_items = 0
    total_price = 0.0
    total_freight = 0.0
    total_value = 0.0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            seller_id, metrics = line.split("\t", 1)
            cnt_str, price_str, freight_str, value_str = metrics.split(",")
            cnt = int(cnt_str)
            price = float(price_str)
            freight = float(freight_str)
            value = float(value_str)
        except (ValueError, IndexError):
            continue

        if current_seller == seller_id:
            total_items += cnt
            total_price += price
            total_freight += freight
            total_value += value
        else:
            if current_seller is not None:
                print("{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
                    current_seller, total_items, total_price, total_freight, total_value
                ))
            current_seller = seller_id
            total_items = cnt
            total_price = price
            total_freight = freight
            total_value = value

    if current_seller is not None:
        print("{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
            current_seller, total_items, total_price, total_freight, total_value
        ))

if __name__ == "__main__":
    main()
