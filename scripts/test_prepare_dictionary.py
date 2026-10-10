import unittest
from prepare_dictionary import prepare

class DictionaryPreparationTests(unittest.TestCase):
    def test_normalizes_deduplicates_and_filters(self):
        words=prepare([' apple ', 'APPLE', 'co-op', 'can't', 'cat', 'XYZ123', 'a', 'BEAUTIFUL', ''],excluded=['cat'])
        self.assertEqual(words,['APPLE','BEAUTIFUL'])

    def test_respects_length_limits(self):
        self.assertEqual(prepare(['CAT','APPLE','BANANAS'],minimum=4,maximum=6),['APPLE'])

if __name__=='__main__':unittest.main()
