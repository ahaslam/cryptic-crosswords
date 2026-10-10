import unittest
from editorial_signals import review_signal, review_draft

class EditorialSignalsTests(unittest.TestCase):
    def test_american_reference_is_welcome(self):
        result=review_signal('NBC')
        self.assertFalse(result.review_required)
        self.assertIn('american_institution',result.topics)

    def test_historical_term_requires_contextual_review(self):
        result=review_signal('NEGRO')
        self.assertTrue(result.review_required)

    def test_names_are_not_blacklisted(self):
        for word in ('KINABALU','ASHANTI','MANTEGNA','WASHINGTON'):
            self.assertFalse(review_signal(word).review_required)

    def test_draft_annotations_do_not_change_answers(self):
        draft={'clues':{'across':[{'number':1,'answer':'NBC'}],
                        'down':[{'number':2,'answer':'NEGRO'}]}}
        result=review_draft(draft)
        self.assertEqual([x['answer'] for x in result],['NBC','NEGRO'])
        self.assertEqual([x['review_required'] for x in result],[False,True])

if __name__=='__main__':
    unittest.main()
