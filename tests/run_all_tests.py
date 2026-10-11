#!/usr/bin/env python3
"""
Test runner for all MapReduce jobs (Job 01 to Job 06)
"""
import unittest
import sys
import os

def main():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    suite = unittest.defaultTestLoader.discover(start_dir=test_dir, pattern="test_job*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
