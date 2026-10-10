import unittest
from scripts.answer_segmentation import segment

class SegmentationTests(unittest.TestCase):
    def test_sot_os_peak(self):
        lex={"SOT":["lush"],"OS":["outsize"],"PEAK":["visor"],"SO":["thus"],"TO":["towards"],"SPEAK":["talk"]}
        results=segment("SO TO SPEAK",lex)
        divisions=[[p["letters"] for p in r["parts"]] for r in results]
        self.assertIn(["SOT","OS","PEAK"],divisions)
        self.assertIn(["SO","TO","SPEAK"],divisions)
        self.assertTrue(all(r["verified"] and not r["editorially_approved"] for r in results))
    def test_no_invented_segments(self):
        self.assertEqual(segment("SPOT",{"SOT":["lush"]}),[])
    def test_limit(self):
        self.assertEqual(len(segment("AAAA",{"A":["a"],"AA":["aa"],"AAA":["aaa"]},max_results=2)),2)

if __name__=="__main__":
    unittest.main()
