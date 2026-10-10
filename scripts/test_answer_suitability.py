import unittest
from answer_suitability import assess, rank_answers

class SuitabilityTests(unittest.TestCase):
    def test_obscurity_is_penalised_less_for_challenging(self):
        easy=assess('KINABALU',.15,'accessible')
        hard=assess('KINABALU',.15,'challenging')
        self.assertTrue(easy.eligible and hard.eligible)
        self.assertGreater(hard.score,easy.score)

    def test_legitimacy_is_not_inferred_from_rarity(self):
        self.assertTrue(assess('ASHANTI',0,'challenging').eligible)
        self.assertFalse(assess('NOTAWORD',1,'challenging',validity=False).eligible)

    def test_evidence_can_improve_or_lower_ranking(self):
        a=assess('MANTEGNA',.3,'challenging',clueability=.9)
        b=assess('MANTEGNA',.3,'challenging',clueability=.1)
        self.assertGreater(a.score,b.score)

    def test_rank_is_deterministic(self):
        ranks=rank_answers(['ASHANTI','KINABALU'],{'ASHANTI':65,'KINABALU':35},'standard')
        self.assertEqual([r.answer for r in ranks],['ASHANTI','KINABALU'])

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            assess('WORD',1.2)
        with self.assertRaises(ValueError):
            assess('WORD',.2,'unknown')

if __name__=='__main__':
    unittest.main()
