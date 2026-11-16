"""Session 7019 (chain 301, done-line request 31): the storage awards table by duration class. A resource's class is its
highest state of charge seen in real time over its highest HSL there, a floor on its hours and not a nameplate; a
resource not seen, or with no positive HSL, is not_seen_rt. The class entities carry the fleet's variables over their own
resources, and they add up to the fleet. Every name here is made up. No request, no model call."""
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import ercot_storage_dam_awards as aw  # noqa: E402

HEAD = "entity,variable,ts_utc,value,x_soc_max_mwh,x_hsl_mw\n"


class TheClasses(unittest.TestCase):
    def test_a_floor_by_the_highest_values_seen(self):
        rows = ["ercot:A,v,2026-09-01T00:00:00Z,1,150,100", "ercot:A,v,2026-09-01T01:00:00Z,1,190,100",   # 1.9 h
                "ercot:B,v,2026-09-01T00:00:00Z,1,200,100",                                               # 2.0 h
                "ercot:C,v,2026-09-01T00:00:00Z,1,450,100",                                               # 4.5 h
                "ercot:D,v,2026-09-01T00:00:00Z,1,100,0",                                                 # no HSL
                "ercot:E,v,2026-09-01T00:00:00Z,1,,100"]                                                   # no state of charge
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# a stand-in\n" + HEAD + "\n".join(rows) + "\n")
            got = aw.duration_classes(p)
        self.assertEqual(got, {"ercot:A": "under_2h", "ercot:B": "2_to_4h", "ercot:C": "4h_and_over"})

    def test_the_builder_writes_each_class_and_says_it_is_a_floor(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "ercot_storage_dam_awards.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertEqual(aw.CLASSES, ("under_2h", "2_to_4h", "4h_and_over", "not_seen_rt"))
        self.assertIn('entity=f"ercot:esr_class_{c}"', s)
        self.assertIn("a floor on its hours and not a nameplate", s)


if __name__ == "__main__":
    unittest.main()
