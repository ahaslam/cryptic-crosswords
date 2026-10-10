"""Tests for the British crossword vocabulary adapter."""
import tempfile
import unittest
from pathlib import Path
from crossword_lexicon import load_scored_tsv, export_solver_dictionary, normalize_answer

class LexiconTests(unittest.TestCase):
    def test_normalize_phrases_and_british_spelling(self):
        self.assertEqual(normalize_answer("Colour-blind"),"COLOURBLIND")
        self.assertEqual(normalize_answer("King's Cross"),"KINGSCROSS")

    def test_load_and_export(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/"words.tsv"
            source.write_text("COLOUR\t92\nKing's Cross\t81\nCOLOUR\t60\nBAD\t12\n")
            scores=load_scored_tsv(source)
            self.assertEqual(scores["COLOUR"],92)
            self.assertEqual(scores["KINGSCROSS"],81)
            target=Path(directory)/"solver.txt"
            self.assertEqual(export_solver_dictionary(scores,target,80),2)
            self.assertEqual(target.read_text().splitlines(),["COLOUR","KINGSCROSS"])

    def test_reject_invalid_scores(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/"words.tsv"
            source.write_text("COLOUR\tpopular\n")
            with self.assertRaisesRegex(ValueError,"invalid score"):
                load_scored_tsv(source)

if __name__=="__main__":
    unittest.main()
