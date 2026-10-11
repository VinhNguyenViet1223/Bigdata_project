#!/usr/bin/env python3
"""
Job 02: Revenue by Order - Reducer
Reads sorted (order_id\tprice,freight) pairs from stdin.
Aggregates and emits: order_id\ttotal_price\ttotal_freight\ttotal_value
"""
import sys

def main():
    current_order = None
    sum_price = 0.0
    sum_freight = 0.0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            order_id, values = line.split("\t", 1)
            price_str, freight_str = values.split(",", 1)
            price = float(price_str)
            freight = float(freight_str)
        except (ValueError, IndexError):
            continue

        if current_order == order_id:
            sum_price += price
            sum_freight += freight
        else:
            if current_order is not None:
                total_value = sum_price + sum_freight
                print("{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
                    current_order, sum_price, sum_freight, total_value
                ))
            current_order = order_id
            sum_price = price
            sum_freight = freight

    if current_order is not None:
        total_value = sum_price + sum_freight
        print("{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
            current_order, sum_price, sum_freight, total_value
        ))

if __name__ == "__main__":
    main()
