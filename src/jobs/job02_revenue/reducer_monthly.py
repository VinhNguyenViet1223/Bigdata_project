#!/usr/bin/env python3
"""
Job 02: Monthly Revenue & Trend - Reducer
Reads sorted (YYYY-MM\t1,price,freight,value) pairs from stdin.
Aggregates and emits: YYYY-MM\ttotal_items\ttotal_price\ttotal_freight\ttotal_revenue
At the end, emits summary row: ALL_TIME_TOTAL\ttotal_items\ttotal_price\ttotal_freight\ttotal_revenue
"""
import sys

def main():
    current_month = None
    month_items = 0
    month_price = 0.0
    month_freight = 0.0
    month_value = 0.0

    grand_items = 0
    grand_price = 0.0
    grand_freight = 0.0
    grand_value = 0.0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            month, metrics = line.split("\t", 1)
            cnt_str, price_str, freight_str, val_str = metrics.split(",")
            cnt = int(cnt_str)
            p = float(price_str)
            fr = float(freight_str)
            val = float(val_str)
        except (ValueError, IndexError):
            continue

        if current_month == month:
            month_items += cnt
            month_price += p
            month_freight += fr
            month_value += val
        else:
            if current_month is not None:
                print("{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
                    current_month, month_items, month_price, month_freight, month_value
                ))
            current_month = month
            month_items = cnt
            month_price = p
            month_freight = fr
            month_value = val

        grand_items += cnt
        grand_price += p
        grand_freight += fr
        grand_value += val

    if current_month is not None:
        print("{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
            current_month, month_items, month_price, month_freight, month_value
        ))

    # Grand total summary row for reporting
    if grand_items > 0:
        print("{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(
            "ALL_TIME_TOTAL", grand_items, grand_price, grand_freight, grand_value
        ))

if __name__ == "__main__":
    main()
