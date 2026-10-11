#!/usr/bin/env python3
"""
Unit test for Job 05: Customer Reviews Analysis
"""
import os
import sys
import subprocess
import unittest

JOB_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "jobs", "job05_reviews")
MAPPER_PATH = os.path.join(JOB_DIR, "mapper.py")
REDUCER_PATH = os.path.join(JOB_DIR, "reducer.py")

SAMPLE_CSV = """review_id,order_id,review_score,review_comment_title,review_comment_message,review_creation_date,review_answer_timestamp
7bc2406110b926393aa56f80a40eba40,73fc7af87114b39712e6da79b0a377eb,4,,,2018-01-18 00:00:00,2018-01-18 21:46:59
e2344537d80db647974097b602d3494f,a5489c0dbe60c4341b6f989234be0f3f,5,,,2018-03-10 00:00:00,2018-03-15 23:18:57
f7c4243c7fe9e387e1e0e9e13032356b,f9e4b658b201a9f2ecb08b186b53c3f3,5,,,2018-01-04 00:00:00,2018-01-05 15:49:51
11111111111111111111111111111111,22222222222222222222222222222222,1,,,2018-01-04 00:00:00,2018-01-05 15:49:51
invalid_row_with_no_score
"""

class TestJob05(unittest.TestCase):
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
        self.assertEqual(lines.get("SCORE_1"), "1")
        self.assertEqual(lines.get("SCORE_4"), "1")
        self.assertEqual(lines.get("SCORE_5"), "2")

        avg_parts = lines.get("OVERALL_AVERAGE").split("\t")
        avg_score = float(avg_parts[0])
        total_cnt = int(avg_parts[1])
        # (4 + 5 + 5 + 1) / 4 = 15 / 4 = 3.75
        self.assertAlmostEqual(avg_score, 3.75, places=2)
        self.assertEqual(total_cnt, 4)

if __name__ == "__main__":
    unittest.main()
