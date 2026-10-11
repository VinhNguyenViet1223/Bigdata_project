#!/usr/bin/env python3
"""
Unit test for Job 01: Order Statistics
"""
import os
import sys
import subprocess
import unittest

JOB_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "jobs", "job01_order_statistics")
MAPPER_PATH = os.path.join(JOB_DIR, "mapper.py")
REDUCER_PATH = os.path.join(JOB_DIR, "reducer.py")

SAMPLE_CSV = """order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date
e481f51cbdc54678b7cc49136f2d6af7,9ef432eb6251297304e76186b10a928d,delivered,2017-10-02 10:56:33,2017-10-02 11:07:15,2017-10-04 19:55:00,2017-10-10 21:25:13,2017-10-18 00:00:00
53cdb2fc8bc7dce0b6741e2150273451,b0830fb4747a6c6d20dea0b8c802d77f,delivered,2018-07-24 20:41:37,2018-07-26 03:24:27,2018-07-26 14:31:00,2018-08-07 15:27:45,2018-08-13 00:00:00
136cce7faa42938203109c84e5787968,ed0271e0b7da060a39379659073b015b,canceled,2018-02-19 19:48:52,2018-02-19 20:31:10,,,2018-03-09 00:00:00
malformed_row_without_enough_columns
"""

class TestJob01(unittest.TestCase):
    def test_mapper(self):
        p = subprocess.Popen(
            [sys.executable, MAPPER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = p.communicate(input=SAMPLE_CSV)
        self.assertEqual(p.returncode, 0, err)
        lines = [line.strip() for line in out.strip().split("\n") if line.strip()]
        self.assertIn("delivered\t1", lines)
        self.assertIn("canceled\t1", lines)
        self.assertEqual(len(lines), 3)

    def test_pipeline(self):
        p_map = subprocess.Popen(
            [sys.executable, MAPPER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        map_out, _ = p_map.communicate(input=SAMPLE_CSV)

        # Simulation of Hadoop Shuffle & Sort
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

        lines = dict(line.split("\t") for line in red_out.strip().split("\n") if line.strip())
        self.assertEqual(lines.get("delivered"), "2")
        self.assertEqual(lines.get("canceled"), "1")

if __name__ == "__main__":
    unittest.main()
