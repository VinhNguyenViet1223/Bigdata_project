#!/usr/bin/env python3
"""
Unit test for Job 06: Delivery Logistics Analysis
"""
import os
import sys
import subprocess
import unittest

JOB_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "jobs", "job06_delivery")
MAPPER_PATH = os.path.join(JOB_DIR, "mapper.py")
REDUCER_PATH = os.path.join(JOB_DIR, "reducer.py")

SAMPLE_CSV = """order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date
order_on_time,cust1,delivered,2017-10-02 10:00:00,2017-10-02 11:00:00,2017-10-04 19:00:00,2017-10-10 10:00:00,2017-10-18 00:00:00
order_late,cust2,delivered,2018-07-01 10:00:00,2018-07-01 12:00:00,2018-07-03 14:00:00,2018-07-25 10:00:00,2018-07-20 00:00:00
order_canceled,cust3,canceled,2018-02-19 19:48:52,2018-02-19 20:31:10,,,2018-03-09 00:00:00
order_missing_deliv,cust4,delivered,2018-02-19 19:48:52,2018-02-19 20:31:10,,2018-03-09 00:00:00
"""

class TestJob06(unittest.TestCase):
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

        lines = dict(l.split("\t", 1) for l in red_out.strip().split("\n") if l)
        self.assertEqual(lines.get("total_delivered_orders"), "2")
        self.assertEqual(lines.get("late_orders"), "1")
        self.assertEqual(lines.get("on_time_orders"), "1")
        self.assertEqual(lines.get("late_delivery_rate_pct"), "50.00%")
        # order 1: 8 days (10/02 to 10/10), order 2: 24 days (07/01 to 07/25)
        # min = 8.00, max = 24.00, avg = 16.00
        self.assertEqual(lines.get("min_delivery_days"), "8.00")
        self.assertEqual(lines.get("max_delivery_days"), "24.00")
        self.assertEqual(lines.get("avg_delivery_days"), "16.00")

if __name__ == "__main__":
    unittest.main()
