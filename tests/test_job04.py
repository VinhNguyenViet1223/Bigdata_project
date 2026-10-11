#!/usr/bin/env python3
"""
Unit test for Job 04: Seller Performance
"""
import os
import sys
import subprocess
import unittest

JOB_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "jobs", "job04_seller")
MAPPER_PATH = os.path.join(JOB_DIR, "mapper.py")
REDUCER_PATH = os.path.join(JOB_DIR, "reducer.py")

SAMPLE_CSV = """order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value
00010242fe8c5a6d1ba2dd792cb16214,1,4244733e06e7ecb4970a6e2683c13e61,48436dade18ac8b2bce089ec2a041202,2017-09-19 09:45:35,50.00,10.00
00018f77f2f0320c557190d7a1444f90,1,eacb104f0352c183d599c36470921603,48436dade18ac8b2bce089ec2a041202,2017-05-03 11:05:13,100.00,15.00
"""

class TestJob04(unittest.TestCase):
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

        lines = [l for l in red_out.strip().split("\n") if l]
        self.assertEqual(len(lines), 1)
        seller, items, price, freight, val = lines[0].split("\t")
        self.assertEqual(seller, "48436dade18ac8b2bce089ec2a041202")
        self.assertEqual(int(items), 2)
        self.assertAlmostEqual(float(price), 150.00)
        self.assertAlmostEqual(float(freight), 25.00)
        self.assertAlmostEqual(float(val), 175.00)

if __name__ == "__main__":
    unittest.main()
