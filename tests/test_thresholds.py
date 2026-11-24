import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from thresholds import choose, load_rows, measure


class ThresholdTests(unittest.TestCase):
    def test_cost_changes_decision(self):
        rows = [(0.9, 1), (0.8, 0), (0.7, 0), (0.6, 1)]
        self.assertEqual(choose(rows, 1), 0.9)
        self.assertEqual(choose(rows, 4), 0.6)

    def test_no_alert_and_tie(self):
        self.assertEqual(choose([(1, 0), (1, 1)], 1), math.inf)

    def test_inclusive_boundary(self):
        self.assertEqual(measure([(0.5, 1), (0.4, 1)], 0.5, 4),
                         dict(tp=1, fp=0, tn=0, fn=1, cost=4))

    def test_reject_cross_split_duplicate_and_nan(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "rows.csv"
            for extra in ("a,test,0.4,0", "c,test,nan,0"):
                path.write_text("id,split,score,label\na,validation,1,1\nb,validation,0,0\n"
                                "d,test,0.9,1\n" + extra + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_rows(path)
