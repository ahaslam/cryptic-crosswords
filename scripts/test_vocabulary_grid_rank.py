import unittest
from vocabulary_grid_rank import vocabulary_metrics, select_vocabulary_aware
from generate_grid import generate
from rank_grids import metrics

class VocabularyGridRankTests(unittest.TestCase):
    def test_no_preferred_words_implies_forced_exceptions(self):
        grid=generate(seed=0)
        v=vocabulary_metrics(grid,{'CAT':90},85,2)
        self.assertGreater(v['forced_exceptions_lower_bound'],2)

    def test_selection_is_deterministic(self):
        a=generate(seed=0)
        b=generate(seed=1)
        options=[(metrics(g)['score'],i,g) for i,g in enumerate((a,b))]
        scores={'A'*n:90 for n in range(3,16)}
        x=select_vocabulary_aware(options,scores,85,2)
        y=select_vocabulary_aware(options,scores,85,2)
        self.assertEqual(x,y)
        self.assertIn('vocabulary',x[2])

if __name__=='__main__':
    unittest.main()
