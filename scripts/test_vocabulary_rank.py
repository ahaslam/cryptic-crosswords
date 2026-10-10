"""Tests for dictionary-informed candidate ranking."""
import unittest
from rank_grids import candidates, select_vocabulary, vocabulary_metrics

class VocabularyRankingTests(unittest.TestCase):
    def test_selection_uses_existing_candidate_pool(self):
        options=candidates(0,3,20000)
        counts={n:1000 for n in range(3,16)}
        pattern,seed,score=select_vocabulary(0,counts,3,20000)
        self.assertIn((seed,pattern),[(s,g) for _,s,g in options])
        self.assertIn('vocabulary_scarcity',score)
        self.assertEqual((pattern,seed,score),select_vocabulary(0,counts,3,20000))

    def test_long_word_scarcity_penalised(self):
        options=candidates(1,2,20000)
        counts={n:(1 if n>8 else 10000) for n in range(3,16)}
        values=[vocabulary_metrics(grid,counts) for _,_,grid in options]
        self.assertTrue(all(v['vocabulary_scarcity']>0 for v in values))

if __name__=='__main__':
    unittest.main()
