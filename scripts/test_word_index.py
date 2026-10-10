import unittest
from word_index import WordIndex

class WordIndexTests(unittest.TestCase):
    def setUp(self):
        self.index=WordIndex({3: {'CAT','CAR','BAR','BAT','RAT'},4:{'CART'}})

    def test_unconstrained(self):
        self.assertEqual(set(self.index.candidates('...',set())),{'CAT','CAR','BAR','BAT','RAT'})

    def test_intersection(self):
        self.assertEqual(set(self.index.candidates('CA.',set())),{'CAT','CAR'})
        self.assertEqual(self.index.candidates('C.Z',set()),[])

    def test_candidates_are_sorted_even_after_set_intersection(self):
        self.assertEqual(self.index.candidates('...',set()),['BAR','BAT','CAR','CAT','RAT'])
        self.assertEqual(self.index.candidates('CA.',set()),['CAR','CAT'])
        self.assertEqual(self.index.candidates('.A.',{'BAR'}),['BAT','CAR','CAT','RAT'])

    def test_exclusion_and_length(self):
        self.assertEqual(self.index.candidates('CAR',{'CAR'}),[])
        self.assertEqual(self.index.candidates('CART',set()),['CART'])

if __name__=='__main__':unittest.main()
