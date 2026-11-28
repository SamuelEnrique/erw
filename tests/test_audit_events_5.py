"""Session 10225 (chain 710, the events audit, finding 5): /events/caiso-heat-2020 draws CAISO's carbon intensity of
generation over 2020-08-10 to 2020-08-24, and EIA's file holds no hydro for CAISO from 2019-10-01T21:00Z to
2020-08-24T17:00Z (warehouse/derived/impossible_hours.py CISO_NO_HYDRO), its net generation leaving the hydro out too:
every day of the window divides CO2 by a net generation without hydro. The window averages 281.32 kg/MWh against
204.95 (2018) and 184.98 (2019) on the baseline days. The ERW's rule leaves those hours out and is held. Words only:
the page and docs/methods/events.md say so; no figure moves (applying the held rule is the owner's ruling, finding 6).
docs/reviews/events-model-audit-2026-11-26.md.
"""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheIntensityHasNoHydroUnderIt(unittest.TestCase):
    def test_the_page_says_it(self):
        s = src("site", "app", "events", "caiso-heat-2020", "page.tsx")
        self.assertIn('<span data-hydro-gap="1">{HYDRO_GAP_WORDS}</span>', s)
        # session 11407 (wip/ready-events-hydro-gap): with the hydro-gap rule approved for the table, the words say the
        # window's intensity is left out, not that it is too high
        for w in ["No carbon intensity of CAISO is drawn for the event's window", "hold no hydro from October 2019 to the morning of 24 August 2020",
                  "The warehouse's own rule for those hours leaves them out, approved for this table"]:
            self.assertIn(w, s)

    def test_the_note_says_it(self):
        self.assertIn("The carbon intensity has no hydro under it (session 10225, 26 November 2026)", src("docs", "methods", "events.md"))

    def test_the_gap_covers_the_window(self):
        s = src("warehouse", "derived", "impossible_hours.py")
        self.assertIn('CISO_NO_HYDRO = ("2019-10-01T21:00:00Z", "2020-08-24T17:00:00Z")', s)
        self.assertIn("event_window_daily", s, "the event table is among the held tables")

    @unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
    def test_the_window_stands_far_above_its_baseline(self):
        with open(ROWS, encoding="utf-8") as fh:
            xs = [(r["ts_utc"][:10], float(r["value"])) for r in csv.DictReader(l for l in fh if not l.startswith("#"))
                  if r["event"] == "caiso_heat_2020" and r["entity"] == "eia930:CISO" and r["variable"] == "intensity_generation"]
        ev = [v for d, v in xs if "2020-08-10" <= d <= "2020-08-24"]
        b19 = [v for d, v in xs if d.startswith("2019")]
        b18 = [v for d, v in xs if d.startswith("2018")]
        self.assertEqual(len(ev), 14)
        self.assertAlmostEqual(sum(ev) / len(ev), 281.32, delta=0.01)
        self.assertGreater(sum(ev) / len(ev), 1.3 * max(sum(b19) / len(b19), sum(b18) / len(b18)))


if __name__ == "__main__":
    unittest.main()
