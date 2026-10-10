#!/usr/bin/env python3
"""Regression checks for provisional puzzle difficulty profiles."""
import unittest
from benchmark_fill import DIFFICULTY_PRESETS, run

class DifficultyTests(unittest.TestCase):
    def test_ordered_profiles(self):
        a=DIFFICULTY_PRESETS['accessible']
        b=DIFFICULTY_PRESETS['standard']
        c=DIFFICULTY_PRESETS['challenging']
        for scale in ('cmu','lufz'):
            self.assertGreater(a[scale+'_min'],b[scale+'_min'])
            self.assertGreater(b[scale+'_min'],c[scale+'_min'])
            self.assertGreater(a[scale+'_floor'],b[scale+'_floor'])
            self.assertGreater(b[scale+'_floor'],c[scale+'_floor'])
        self.assertLess(a['max_exceptions'],b['max_exceptions'])
        self.assertLess(b['max_exceptions'],c['max_exceptions'])

    def test_unknown_level_is_rejected_before_loading_dictionary(self):
        with self.assertRaisesRegex(ValueError,'Unknown difficulty'):
            run(difficulty='impossible')

if __name__=='__main__':
    unittest.main()
