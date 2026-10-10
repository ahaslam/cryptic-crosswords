"""Tests for crossing propagation, uniqueness and rare-word budgets."""
import tempfile
import unittest
from pathlib import Path
from fill_grid import fill

class CspTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dictionary=Path(self.tmp.name)/'words.txt'
        self.dictionary.write_text('ABC\nDEF\nGHI\nADG\nBEH\nCFI\n',encoding='utf-8')
        self.scores={w:4.0 for w in ('ABC','DEF','GHI','ADG','BEH')}
        self.scores['CFI']=2.2

    def test_complete_crossing_fill(self):
        draft,nodes=fill(['...']*3,self.dictionary,solver='csp',max_nodes=1000)
        self.assertEqual(draft['grid'],['ABC','DEF','GHI'])
        answers=[c['answer'] for entries in draft['clues'].values() for c in entries]
        self.assertEqual(len(answers),len(set(answers)))
        self.assertGreater(nodes,0)

    def test_one_rare_word_allowed(self):
        draft,_=fill(['...']*3,self.dictionary,solver='csp',max_nodes=1000,
                     word_scores=self.scores,min_score=2.0,
                     preferred_score=3.0,max_exceptions=1)
        answers=[c['answer'] for entries in draft['clues'].values() for c in entries]
        self.assertEqual(sum(self.scores[w]<3.0 for w in answers),1)

    def test_zero_rare_words_rejected(self):
        with self.assertRaises(RuntimeError):
            fill(['...']*3,self.dictionary,solver='csp',max_nodes=1000,
                 word_scores=self.scores,min_score=2.0,
                 preferred_score=3.0,max_exceptions=0)

    def test_insufficient_dictionary_rejected(self):
        self.dictionary.write_text('ABC\n',encoding='utf-8')
        with self.assertRaises(RuntimeError):
            fill(['...']*3,self.dictionary,solver='csp',max_nodes=100)

if __name__=='__main__':
    unittest.main()
