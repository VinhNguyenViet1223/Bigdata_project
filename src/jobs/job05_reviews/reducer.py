#!/usr/bin/env python3
"""
Job 05: Customer Reviews Analysis - Reducer
Reads sorted pairs from stdin.
Computes frequency of each review score and overall average score.
"""
import sys

def main():
    current_key = None
    score_count = 0

    avg_sum = 0.0
    avg_total = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            key, val_str = line.split("\t", 1)
        except ValueError:
            continue

        if key.startswith("SCORE_"):
            try:
                cnt = int(val_str)
            except ValueError:
                continue

            if current_key == key:
                score_count += cnt
            else:
                if current_key is not None:
                    print("{}\t{}".format(current_key, score_count))
                current_key = key
                score_count = cnt

        elif key == "OVERALL_AVERAGE":
            try:
                sc_str, cnt_str = val_str.split(",", 1)
                avg_sum += float(sc_str)
                avg_total += int(cnt_str)
            except (ValueError, IndexError):
                continue

    if current_key is not None:
        print("{}\t{}".format(current_key, score_count))

    if avg_total > 0:
        avg_score = avg_sum / avg_total
        print("OVERALL_AVERAGE\t{:.2f}\t{}".format(avg_score, avg_total))

if __name__ == "__main__":
    main()
