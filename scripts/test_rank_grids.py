import unittest
from generate_grid import valid
from rank_grids import candidates, metrics, select

class GridRankingTests(unittest.TestCase):
    def test_ranked_candidates_are_valid_and_sorted(self):
        ranked=candidates(seed=0,count=3,attempts=20000)
        self.assertEqual(len(ranked),3)
        self.assertEqual([x[0] for x in ranked],sorted(x[0] for x in ranked))
        for score,seed,grid in ranked:
            self.assertTrue(valid(grid))
            self.assertEqual(score,metrics(grid)['score'])
            self.assertEqual(len(grid),15)
    def test_measurements_are_consistent(self):
        from generate_grid import generate
        grid=generate(seed=0)
        m=metrics(grid)
        self.assertEqual(m['across']+m['down'],m['entries'])
        self.assertEqual(sum(m['length_distribution'].values()),m['entries'])
        self.assertEqual(m['block_count']+sum(cell!='#' for row in grid for cell in row),225)
        self.assertEqual(m['three_letter_entries'],m['length_distribution'].get(3,0))
        self.assertTrue(m['rotationally_symmetric'])
        self.assertAlmostEqual(m['crossing_ratio']+m['unchecked_ratio'],1,places=2)

    def test_selection_is_reproducible(self):
        self.assertEqual(select(2,count=2),select(2,count=2))
    def test_rejects_empty_candidate_pool(self):
        with self.assertRaises(ValueError):
            candidates(0,count=0)

if __name__=='__main__':
    unittest.main()
