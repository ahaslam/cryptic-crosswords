import unittest
import json
from pathlib import Path
from analyse_reference_grids import analyse, inspect_reference


class ReferenceGridTests(unittest.TestCase):
    def test_blank_fifteen_square_grid_is_measurable(self):
        result = inspect_reference('blank', ['.'*15]*15)
        self.assertEqual(result['entries'], 30)
        self.assertEqual(result['across'], 15)
        self.assertEqual(result['down'], 15)
        self.assertEqual(result['block_count'], 0)
        self.assertTrue(result['rotationally_symmetric'])

    def test_bad_dimensions_and_characters_are_rejected(self):
        for grid in (['.'*15]*14, ['.'*14]*15,
                     ['.'*15]*14+['x'*15]):
            with self.assertRaises(ValueError):
                inspect_reference('bad', grid)

    def test_aggregate_is_independent_of_reference_names(self):
        a = analyse({'one': ['.'*15]*15})
        b = analyse({'different': ['.'*15]*15})
        self.assertEqual(a['summary'], b['summary'])
        self.assertEqual(a['reference_count'], 1)

    def test_published_reference_has_expected_structure(self):
        path = Path(__file__).resolve().parents[1] / 'data' / 'reference-grids.json'
        references = json.loads(path.read_text(encoding='utf-8'))
        measured = analyse(references)['grids']['sunday-times-p87']
        self.assertEqual(measured['entries'], 28)
        self.assertEqual(measured['max_entry_length'], 12)
        self.assertTrue(measured['rotationally_symmetric'])
        self.assertEqual(measured['three_letter_entries'], 0)

    def test_empty_references_are_rejected(self):
        with self.assertRaises(ValueError):
            analyse({})


if __name__ == '__main__':
    unittest.main()
