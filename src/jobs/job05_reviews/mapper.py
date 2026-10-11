#!/usr/bin/env python3
"""
Job 05: Customer Reviews Analysis - Mapper
Reads olist_order_reviews_dataset.csv from stdin.
Emits:
  SCORE_<N>\t1
  OVERALL_AVERAGE\t<N>,1
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
            if row[0].strip() == "review_id":
                continue

            score_str = row[2].strip()
            if not score_str.isdigit():
                continue

            score = int(score_str)
            if score < 1 or score > 5:
                continue

            # Emit for individual score frequency
            print("SCORE_{}\t1".format(score))
            # Emit for global average computation
            print("OVERALL_AVERAGE\t{},1".format(score))
        except Exception:
            continue

if __name__ == "__main__":
    main()
