#!/usr/bin/env python3
"""
Job 06: Delivery Logistics Analysis - Reducer
Reads sorted (DELIVERY_METRICS\tdelivery_days,is_late) pairs from stdin.
Computes and emits:
  total_delivered_orders\t<count>
  avg_delivery_days\t<avg>
  min_delivery_days\t<min>
  max_delivery_days\t<max>
  late_orders\t<count>
  on_time_orders\t<count>
  late_delivery_rate_pct\t<pct>%
"""
import sys

def main():
    total_count = 0
    sum_days = 0.0
    min_days = 999999.0
    max_days = 0.0
    late_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            key, val_str = line.split("\t", 1)
            days_str, late_str = val_str.split(",", 1)
            days = float(days_str)
            is_late = int(late_str)
        except (ValueError, IndexError):
            continue

        total_count += 1
        sum_days += days
        if days < min_days:
            min_days = days
        if days > max_days:
            max_days = days
        late_count += is_late

    if total_count > 0:
        avg_days = sum_days / total_count
        on_time_count = total_count - late_count
        late_rate = (float(late_count) / float(total_count)) * 100.0

        print("total_delivered_orders\t{}".format(total_count))
        print("avg_delivery_days\t{:.2f}".format(avg_days))
        print("min_delivery_days\t{:.2f}".format(min_days))
        print("max_delivery_days\t{:.2f}".format(max_days))
        print("late_orders\t{}".format(late_count))
        print("on_time_orders\t{}".format(on_time_count))
        print("late_delivery_rate_pct\t{:.2f}%".format(late_rate))

if __name__ == "__main__":
    main()
