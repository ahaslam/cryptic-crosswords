"""Grid clue-count contract tests."""
import unittest
from generate_grid import generate,slots,valid

class GridCountTests(unittest.TestCase):
    def test_multiple_seeds_have_at_most_55_entries(self):
        for seed in (0,1,2):
            grid=generate(seed=seed)
            self.assertTrue(valid(grid))
            self.assertTrue(50<=len(slots(grid))<=55)

    def test_cannot_request_more_than_55(self):
        with self.assertRaises(ValueError):
            generate(max_clues=60)

if __name__=='__main__':
    unittest.main()
