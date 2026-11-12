"""Session 3811 (chain 216): NYISO's real-time intervals allow a regular stamp published a few seconds late.

On 9 November 2026 NYISO's real-time zone file stamped 09:40:01 after 09:35:00 (EST) in all 11 zones: an interval of 301
seconds, and iso_prices.rebuild_irregular_intervals refused anything over 300, so three daily runs wrote none of NYISO's
real time. A stamp up to LATE_STAMP_S seconds late now passes (its own docstring already described "12:10:03 for 12:10");
a missing stamp, an interval of about 600 seconds, still refuses the window, so nothing is ever bridged or filled.

Synthetic rows only. No network, no warehouse table, no model.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402


def rows(stamps, nodes=("CAPITL", "WEST")):
    out = []
    for n in nodes:
        for s in stamps:
            out.append({"node": n, "interval_end": pd.Timestamp(s, tz="UTC"), "value": 30.0})
    return pd.DataFrame(out)


START = pd.Timestamp("2026-11-09T14:20:00Z")
END = pd.Timestamp("2026-11-09T15:00:00Z")
REGULAR = ["2026-11-09T14:25:00Z", "2026-11-09T14:30:00Z", "2026-11-09T14:35:00Z"]
AFTER = ["2026-11-09T14:44:31Z", "2026-11-09T14:45:00Z", "2026-11-09T14:50:00Z", "2026-11-09T14:55:00Z", "2026-11-09T15:00:00Z"]


class LateStamps(unittest.TestCase):
    def test_a_stamp_one_second_late_passes(self):
        log = []
        r = ip.rebuild_irregular_intervals(rows(REGULAR + ["2026-11-09T14:40:01Z"] + AFTER), START, END, ["CAPITL", "WEST"], log.append)
        late = r[r["interval_end"] == pd.Timestamp("2026-11-09T14:40:01Z")]
        self.assertEqual(len(late), 2)
        self.assertTrue(all((late["interval_end"] - late["interval_start"]).dt.total_seconds() == 301))

    def test_a_missing_stamp_still_refuses(self):
        with self.assertRaises(RuntimeError) as cm:
            ip.rebuild_irregular_intervals(rows(REGULAR + AFTER), START, END, ["CAPITL", "WEST"], lambda *a: None)
        self.assertIn("longer than 5 minutes", str(cm.exception))

    def test_the_allowance_is_small(self):
        self.assertGreater(ip.LATE_STAMP_S, 0)
        self.assertLess(ip.LATE_STAMP_S, 60)   # far below the ~300 extra seconds of a missing stamp


if __name__ == "__main__":
    unittest.main()
