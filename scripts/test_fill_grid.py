"""Tests for crossword fill mechanics (synthetic letter sequences, not publishable words)."""
import tempfile
import unittest
from pathlib import Path
from fill_grid import fill, slots_of

class FillTests(unittest.TestCase):
    def test_numbering(self):
        slots=slots_of(['...','...','...'])
        self.assertEqual(len(slots),6)
        self.assertEqual([s[1] for s in slots if s[0]=='across'],[1,4,5])
        self.assertEqual([s[1] for s in slots if s[0]=='down'],[1,2,3])

    def test_crossings_and_unique_entries(self):
        with tempfile.TemporaryDirectory() as d:
            dictionary=Path(d)/'words.txt'
            dictionary.write_text('ABC\nDEF\nGHI\nADG\nBEH\nCFI\n')
            puzzle,nodes=fill(['...']*3,dictionary,seed=0,max_nodes=1000)
            self.assertEqual(len(puzzle['clues']['across']),3)
            self.assertEqual(len(puzzle['clues']['down']),3)
            self.assertEqual(len({c['answer'] for direction in puzzle['clues'].values() for c in direction}),6)
            for direction,dr,dc in [('across',0,1),('down',1,0)]:
                for clue in puzzle['clues'][direction]:
                    for i,ch in enumerate(clue['answer']):
                        self.assertEqual(puzzle['grid'][clue['row']+i*dr][clue['col']+i*dc],ch)

    def test_quality_threshold_and_ranked_fill(self):
        with tempfile.TemporaryDirectory() as d:
            dictionary=Path(d)/'words.txt'
            dictionary.write_text('ABC\nDEF\nGHI\nADG\nBEH\nCFI\nZZZ\n')
            scores={w:4.0 for w in ('ABC','DEF','GHI','ADG','BEH','CFI')}
            scores['ZZZ']=1.0
            puzzle,_=fill(['...']*3,dictionary,seed=0,max_nodes=1000,
                          word_scores=scores,min_score=3.0)
            answers={c['answer'] for group in puzzle['clues'].values() for c in group}
            self.assertEqual(answers,set(scores)-{'ZZZ'})

    def test_threshold_rejects_missing_scores(self):
        with tempfile.TemporaryDirectory() as d:
            dictionary=Path(d)/'words.txt'
            dictionary.write_text('ABC\n')
            with self.assertRaises(ValueError):
                fill(['...']*3,dictionary,min_score=3.0)

    def test_limited_rare_word_exceptions(self):
        with tempfile.TemporaryDirectory() as d:
            dictionary=Path(d)/'words.txt'
            dictionary.write_text('ABC\nDEF\nGHI\nADG\nBEH\nCFI\n')
            scores={w:4.0 for w in ('ABC','DEF','GHI','ADG','BEH')}
            scores['CFI']=2.2
            puzzle,_=fill(['...']*3,dictionary,max_nodes=1000,
                          word_scores=scores,min_score=2.0,
                          preferred_score=3.0,max_exceptions=1)
            answers=[c['answer'] for group in puzzle['clues'].values() for c in group]
            self.assertEqual(len(answers),6)
            self.assertEqual(sum(scores[w]<3.0 for w in answers),1)
            with self.assertRaises(RuntimeError):
                fill(['...']*3,dictionary,max_nodes=1000,
                     word_scores=scores,min_score=2.0,
                     preferred_score=3.0,max_exceptions=0)

    def test_unavoidable_rare_words_exceed_budget(self):
        with tempfile.TemporaryDirectory() as d:
            dictionary=Path(d)/'words.txt'
            dictionary.write_text(chr(10).join(('ABC','DEF','GHI','ADG','BEH','CFI'))+chr(10))
            scores={w:2.2 for w in ('ABC','DEF','GHI','ADG','BEH','CFI')}
            with self.assertRaises(RuntimeError) as context:
                fill(['...']*3,dictionary,max_nodes=1000,word_scores=scores,
                     min_score=2.0,preferred_score=3.0,max_exceptions=5)
            self.assertIn('after 0 attempts',str(context.exception))

if __name__=='__main__':unittest.main()
