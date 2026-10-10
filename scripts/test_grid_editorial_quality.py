import unittest
from grid_editorial_quality import score_draft, candidate_penalty

def draft(words):
    return {'clues':{'across':[{'answer':w} for w in words],'down':[]}}

class GridEditorialQualityTests(unittest.TestCase):
    def test_varied_grid_beats_repetitive_admin_grid(self):
        varied=score_draft(draft(['NBC','KINABALU','FINALS','MEDIUM','DISTRICT','HATE']))
        repetitive=score_draft(draft(['MANIFESTATIONS','CHARACTERISTICS','ESTABLISHMENTS',
                                      'AFOREMENTIONED','FACILITIES','LIBERALISM']))
        self.assertGreater(varied['score'],repetitive['score'])

    def test_no_nationality_or_name_penalty(self):
        self.assertEqual(score_draft(draft(['NBC','ASHANTI','MANTEGNA']))['score'],100)

    def test_search_penalty_grows_with_repetitive_answers(self):
        self.assertEqual(candidate_penalty('MANIFESTATIONS', []),0)
        self.assertEqual(candidate_penalty('CHARACTERISTICS',['MANIFESTATIONS']),0)
        self.assertGreater(candidate_penalty('ESTABLISHMENTS',['MANIFESTATIONS','CHARACTERISTICS']),0)
        self.assertEqual(candidate_penalty('NBC',['MANIFESTATIONS','CHARACTERISTICS']),0)

    def test_contextual_review_is_visible(self):
        result=score_draft(draft(['NEGRO','NBC']))
        self.assertEqual(result['context_review_answers'],['NEGRO'])
        self.assertLess(result['score'],100)

    def test_duplicates_and_function_word_repetition(self):
        result=score_draft(draft(['THEY','HIS','THAT','ONES','SEEMED','NBC','NBC']))
        self.assertEqual(result['duplicate_count'],1)
        self.assertLess(result['score'],100)

if __name__=='__main__':
    unittest.main()
