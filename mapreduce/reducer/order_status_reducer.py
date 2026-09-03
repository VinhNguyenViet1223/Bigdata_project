#!/usr/bin/env python3

import sys

current_status = None
current_count = 0

for line in sys.stdin:
    line = line.strip()

    if not line:
        continue

    try:
        status, count = line.split("\t", 1)
        count = int(count)
    except ValueError:
        continue

    if current_status == status:
        current_count += count

    else:
        if current_status is not None:
            print(f"{current_status}\t{current_count}")

        current_status = status
        current_count = count


# Xuất kết quả cuối cùng
if current_status is not None:
    print(f"{current_status}\t{current_count}")