import unittest
from scripts.wordplay_explorer import verify, explore

class WordplayTests(unittest.TestCase):
    def test_spot_reversal(self):
        self.assertTrue(verify("SPOT", "reversal", "TOPS"))
        self.assertFalse(verify("SPOT", "reversal", "POTS"))
    def test_spot_anagram(self):
        self.assertTrue(verify("SPOT", "anagram", "POTS"))
        self.assertFalse(verify("SPOT", "anagram", "POSTER"))
    def test_hidden(self):
        self.assertTrue(verify("BASIL", "hidden", "SCUBA SILHOUETTES"))
    def test_charade(self):
        self.assertTrue(verify("SOTOSPEAK", "charade", "SOT OS PEAK"))
        self.assertTrue(verify("PATELLA", "charade", "PAT ELLA"))
    def test_container(self):
        self.assertTrue(verify("SALUTE", "container", "L", container="SAUTE", position=2))
        self.assertFalse(verify("SALUTE", "container", "L", container="SAUTE", position=3))
    def test_deletion(self):
        self.assertTrue(verify("CAT", "deletion", "S", container="CAST"))
    def test_explore(self):
        found = explore("SPOT", ["TOPS", "POTS", "STONE"])
        self.assertEqual({(x["mechanism"], x["fodder"]) for x in found},
                         {("reversal", "TOPS"), ("anagram", "TOPS"), ("anagram", "POTS")})
        self.assertTrue(all(x["editorial_status"] == "needs-development" for x in found))

if __name__ == "__main__":
    unittest.main()
