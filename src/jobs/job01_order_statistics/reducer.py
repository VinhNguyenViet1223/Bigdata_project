#!/usr/bin/env python3
"""
Job 01: Order Statistics - Reducer
Reads sorted (order_status\tcount) pairs from stdin.
Aggregates and emits: order_status\ttotal_orders
"""
import sys

def main():
    current_status = None
    current_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            status, count_str = line.split("\t", 1)
            count = int(count_str)
        except ValueError:
            continue

        if current_status == status:
            current_count += count
        else:
            if current_status is not None:
                print("{}\t{}".format(current_status, current_count))
            current_status = status
            current_count = count

    if current_status is not None:
        print("{}\t{}".format(current_status, current_count))

if __name__ == "__main__":
    main()
