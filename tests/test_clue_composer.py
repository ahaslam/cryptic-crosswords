import unittest
from scripts.clue_composer import assess, review_portfolio

class ComposerTests(unittest.TestCase):
    def test_literal_check(self):
        c={"answer":"SPOT","clue":"Under tops looking back is a stain (4)","device":"reversal","definition":"a stain","parse":"TOPS reversed","surface_story":"Clothes","fodder":"TOPS"}
        self.assertEqual(assess(c)["status"],"letter-operation-verified")
        c["fodder"]="POTS"
        self.assertEqual(assess(c)["status"],"invalid")
    def test_semantic_not_approved(self):
        c={"answer":"SPOT","clue":"A blemish, or a location (4)","device":"double-definition","definition":"blemish","parse":"two meanings","surface_story":"A comparison"}
        self.assertEqual(assess(c)["status"],"semantic-review-required")
        self.assertFalse(assess(c)["editorially_approved"])
    def test_diversity(self):
        base={"answer":"SPOT","clue":"draft","definition":"stain","parse":"draft","surface_story":"draft"}
        a=dict(base,device="reversal",fodder="TOPS")
        b=dict(base,device="double-definition")
        r=review_portfolio([a,b])
        self.assertFalse(r["by_answer"]["SPOT"]["needs_broader_exploration"])

if __name__=="__main__":
    unittest.main()
