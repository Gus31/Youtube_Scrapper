import sys
sys.path.append('.')
sys.path.append('../')

import unittest
import invoke
import os
import json
import scrapper as sc

class _testScrapper(unittest.TestCase):
    def test_general_ok(self):
        invoke.run("python scrapper.py --input input.json --output output.json", in_stream=False)
        self.assertTrue(os.path.isfile("output.json"))