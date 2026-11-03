"""Standard-library checks for the demo's reproducible research logic."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'dashboard'))
sys.path.insert(0, str(ROOT / 'src'))
from server import ALL, SUMMARY, catalog, run_live, test_invalid_pair
from negationscope.dataset import validate

class CollegeDemoTests(unittest.TestCase):
    def test_deterministic_dataset_counts(self):
        self.assertEqual((SUMMARY['samples'], SUMMARY['pairs'], SUMMARY['scenes']), (648, 324, 36))
        self.assertEqual(len(SUMMARY['categories']), 18)

    def test_pair_completeness(self):
        self.assertEqual(validate(ALL)['pairs'], 324)

    def test_incomplete_pair_detected(self):
        self.assertTrue(test_invalid_pair()['status'].startswith('PASS'))

    def test_live_answer_changes_metrics(self):
        pair = catalog()[0]['pair_id']
        correct = run_live({'pair_id': pair, 'answer': 'no'})
        wrong = run_live({'pair_id': pair, 'answer': 'yes'})
        unknown = run_live({'pair_id': pair, 'answer': 'unknown'})
        self.assertEqual(correct['target_correct'], 1)
        self.assertEqual(wrong['target_correct'], 0)
        self.assertEqual(unknown['target_correct'], 0)
        self.assertLess(unknown['coverage'], 1)

if __name__ == '__main__':
    unittest.main()
