"""Audit of /forecast, finding 2 (session 11402, docs/reviews/forecast-model-audit-2026-11-28.md): on 28 November 2026
the page draws Friday 27 November under "Tomorrow" for every place, because main's place files (put back by 993a5d99b
to the rebuild of 26 November) are a day behind the ledger, which holds the forecasts for 28 November of all 64 places
(made by the data machine at 19:00 UTC on 27 November). For the 35 authorities added on 27 November the day drawn is a
forecast no ledger holds (made as at 18:00 UTC on 26 November by a rebuild that wrote no ledger row).

1. Against the page's own files (passes on main while they are those audited; skipped once rebuilt): the ledger holds a
   later day than the place file in all 64 places, and no ledger row for the drawn day of the 35 added places.
2. The fix on this branch (fails on main): where the ledger holds a later day for the place than its file, the
   Tomorrow block says the files are behind it and names both days (site/app/forecast/view.tsx, ledgerNewest).
   Drawn to HTML from main's files in the audit (draw2.mjs): Texas, demand and price, and AECI."""
import csv
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site", "data", "predict")
VIEW = os.path.join(ROOT, "site", "app", "forecast", "view.tsx")
AUDITED = "2026-11-27T14:39:36Z"


class FilesBehindTheLedger(unittest.TestCase):
    def test_main_files_draw_a_day_the_ledger_has_passed(self):
        with open(os.path.join(SITE, "index.json"), encoding="utf-8") as f:
            idx = json.load(f)
        if idx.get("built") != AUDITED:
            self.skipTest("the place files are not those audited (rebuilt since)")
        with open(os.path.join(SITE, "ledger_demand.csv"), encoding="utf-8") as f:
            led = list(csv.DictReader([x for x in f.read().splitlines() if x and not x.startswith("#")]))
        newest, held = {}, set()
        for r in led:
            newest[r["place"]] = max(newest.get(r["place"], ""), r["target_day"])
            held.add((r["place"], r["target_day"]))
        behind, unledgered = 0, 0
        for p in idx["places"]:
            day = p["series"]["demand"]["target_day"]
            behind += newest.get(p["place"], "") > day
            unledgered += (p["place"], day) not in held
        self.assertEqual(behind, 64)
        self.assertEqual(unledgered, 35)

    def test_the_page_says_when_its_files_are_behind_the_ledger(self):
        with open(VIEW, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("function ledgerNewest(series: SeriesKey, place: string)", src)
        self.assertIn("data-fc-behind={slot.mark}", src)
        self.assertIn("The ledger already holds a newer {LABEL} for this place", src)


if __name__ == "__main__":
    unittest.main()
