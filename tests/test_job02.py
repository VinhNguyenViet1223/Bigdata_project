#!/usr/bin/env python3
"""
Unit test for Job 02: Revenue by Order
"""
import os
import sys
import subprocess
import unittest

JOB_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "jobs", "job02_revenue")
MAPPER_PATH = os.path.join(JOB_DIR, "mapper.py")
REDUCER_PATH = os.path.join(JOB_DIR, "reducer.py")

SAMPLE_CSV = """order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value
00010242fe8c5a6d1ba2dd792cb16214,1,4244733e06e7ecb4970a6e2683c13e61,48436dade18ac8b2bce089ec2a041202,2017-09-19 09:45:35,58.90,13.29
00018f77f2f0320c557190d7a1444f90,1,eacb104f0352c183d599c36470921603,414444c01a37e4649041a0ba6ac902ff,2017-05-03 11:05:13,239.90,19.93
00018f77f2f0320c557190d7a1444f90,2,eacb104f0352c183d599c36470921603,414444c01a37e4649041a0ba6ac902ff,2017-05-03 11:05:13,10.00,5.00
malformed_row
"""

class TestJob02(unittest.TestCase):
    def test_pipeline(self):
        p_map = subprocess.Popen(
            [sys.executable, MAPPER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        map_out, err = p_map.communicate(input=SAMPLE_CSV)
        self.assertEqual(p_map.returncode, 0, err)

        sorted_lines = sorted(map_out.strip().split("\n"))
        sorted_input = "\n".join(sorted_lines) + "\n"

        p_red = subprocess.Popen(
            [sys.executable, REDUCER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        red_out, _ = p_red.communicate(input=sorted_input)

        results = {}
        for line in red_out.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            results[parts[0]] = (float(parts[1]), float(parts[2]), float(parts[3]))

        # Check single item order
        self.assertIn("00010242fe8c5a6d1ba2dd792cb16214", results)
        price1, freight1, total1 = results["00010242fe8c5a6d1ba2dd792cb16214"]
        self.assertAlmostEqual(price1, 58.90, places=2)
        self.assertAlmostEqual(freight1, 13.29, places=2)
        self.assertAlmostEqual(total1, 72.19, places=2)

        # Check multi item order (239.90 + 10.00 = 249.90; 19.93 + 5.00 = 24.93; total = 274.83)
        self.assertIn("00018f77f2f0320c557190d7a1444f90", results)
        price2, freight2, total2 = results["00018f77f2f0320c557190d7a1444f90"]
        self.assertAlmostEqual(price2, 249.90, places=2)
        self.assertAlmostEqual(freight2, 24.93, places=2)
        self.assertAlmostEqual(total2, 274.83, places=2)

if __name__ == "__main__":
    unittest.main()
