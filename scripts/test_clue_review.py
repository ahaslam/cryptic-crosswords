#!/usr/bin/env python3
import unittest
from clue_review import review

def sample():
    return {'difficulty':'challenging','clues':{'across':[{
        'number':1,'answer':'LISTEN','text':'Silent, oddly rearranged? (6)',
        'editorial':{'device':'anagram','definition':'hear attentively',
                     'wordplay':'SILENT anagram','fairness_reviewed':True,'reviewer':'editor'}
    }],'down':[]}}

class ClueReviewTests(unittest.TestCase):
    def test_complete_record(self):
        self.assertTrue(review(sample())['approved'])
    def test_placeholder_rejected(self):
        p=sample();p['clues']['across'][0]['text']='[CRYPTIC CLUE REQUIRED]'
        self.assertFalse(review(p)['approved'])
    def test_missing_fairness_signoff_rejected(self):
        p=sample();p['clues']['across'][0]['editorial']['fairness_reviewed']=False
        self.assertFalse(review(p)['approved'])
    def test_unattributed_approval_rejected(self):
        p=sample();del p['clues']['across'][0]['editorial']['reviewer']
        self.assertFalse(review(p)['approved'])
    def test_unknown_difficulty_rejected(self):
        p=sample();p['difficulty']='expert'
        self.assertFalse(review(p)['approved'])

if __name__=='__main__':
    unittest.main()
