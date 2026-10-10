import json
import tempfile
import unittest
from pathlib import Path
from benchmark_summary import summary

class BenchmarkSummaryTests(unittest.TestCase):
    def test_missing_report(self):
        self.assertIn('No benchmark report',summary('/nonexistent-benchmark-report.json'))

    def test_unfilled_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'report.json'
            path.write_text(json.dumps({
                'status':'unfilled','elapsed_seconds':12.5,'max_nodes_total':10000,
                'trials':[{'seed':0,'entries':54,'status':'unfilled',
                           'node_budget':2500,'fill_seconds':12.5}]}))
            result=summary(path)
            self.assertIn('| 0 | 54 | unfilled | 2500 | 12.5 |',result)

    def test_filled_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'report.json'
            path.write_text(json.dumps({
                'status':'filled_unreviewed','trials':[{
                    'seed':1,'entries':53,'status':'filled_unreviewed',
                    'selected':'baseline','exception_count':1,
                    'quality_target_met':True,
                    'exceptions':[{'answer':'RARE','frequency':1.9}]}]}))
            result=summary(path)
            self.assertIn('RARE (1.9)',result)
            self.assertIn('Quality target met:',result)

if __name__=='__main__':
    unittest.main()
