"""Audit of the prices pages, finding 3 (session 10218, docs/reviews/prices-model-audit-2026-11-26.md): "Where power is
cheap" (/prices/compare) shows each hub's "Average price" as the simple mean of its hours, each hour once (a flat
load's price), and did not say so. A buyer whose load follows the grid's own pays more: over the twelve months to
October 2026, weighting each day-ahead hour by the grid's own hourly load raises the average by 4.0 to 7.1 percent
(CAISO SP15 30.01 to 31.42 over the hours CAISO's load is held, +4.7 percent).

1. The measured gap (passes on main; skipped where the tables are not on the machine; ERW_AUDIT_TABLES may name
   another copy of warehouse/output): SP15's twelve-month day-ahead average, simple against weighted by CAISO's own
   load (caiso:system), and the page's figure is the simple one.
2. The fix on this branch, words only (fails on main): drawn with the page's own function, the table's note and "How it
   is computed" say the average counts each hour once, as a flat load would pay. No figure moves."""
import datetime as dt
import json
import os
import subprocess
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_AUDIT_TABLES") or os.path.join(ROOT, "warehouse", "output")
UTC = dt.timezone.utc


def sec(ts):
    return int(dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC).timestamp())


class AverageIsAFlatLoads(unittest.TestCase):
    def test_load_weighted_average_is_higher(self):
        need = ["iso_hub_prices_history.csv", "iso_dam_hub_prices.csv", "caiso_area_load_hourly.csv"]
        if not all(os.path.exists(os.path.join(TABLES, n)) for n in need):
            self.skipTest(f"the price and load tables are not in {TABLES}")
        with open(os.path.join(SITE, "data", "price_compare.json"), encoding="utf-8") as f:
            cmp = json.load(f)
        if cmp["end_month"] != "2026-10":
            self.skipTest(f"measured on the copy whose twelve months end in October 2026; this one ends {cmp['end_month']}")
        tz = ZoneInfo("America/Los_Angeles")
        a = int(dt.datetime(2025, 11, 1, tzinfo=tz).timestamp())
        b = int(dt.datetime(2026, 11, 1, tzinfo=tz).timestamp())
        price = {}
        for t in need[:2]:
            with open(os.path.join(TABLES, t), encoding="utf-8") as fh:
                for line in fh:
                    if not line.startswith("caiso:TH_SP15_GEN-APND,lmp_dam,"):
                        continue
                    p = line.split(",", 6)
                    s = sec(p[2])
                    if a <= s < b and p[5] == "PT1H" and s not in price:
                        price[s] = float(p[3])
        load = {}
        with open(os.path.join(TABLES, need[2]), encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("caiso:system,load,"):
                    p = line.split(",", 4)
                    s = sec(p[2])
                    if a <= s < b:
                        load[s] = float(p[3])
        page = next(r["dam_avg_price"] for r in cmp["year"] if r["entity"] == "caiso:TH_SP15_GEN-APND")
        self.assertAlmostEqual(sum(price.values()) / len(price), page, delta=0.005)   # the page's figure: each hour once
        both = [s for s in price if s in load]
        self.assertGreater(len(both), 8000)
        simple = sum(price[s] for s in both) / len(both)
        weighted = sum(price[s] * load[s] for s in both) / sum(load[s] for s in both)
        self.assertAlmostEqual(simple, 30.01, delta=0.005)
        self.assertAlmostEqual(weighted, 31.42, delta=0.005)
        self.assertGreater(weighted / simple - 1, 0.04)

    @unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
    def test_the_page_says_each_hour_counts_once(self):
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/audit-prices-3-draw.mjs", "{}"],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads([x for x in out.stdout.splitlines() if x.startswith("{")][0])
        self.assertIn("The average price counts every hour held once: what a flat load, the same every hour, would pay at the hub or zone.", r["text"])
        self.assertIn("pays more than this average", r["text"])
        self.assertIn("The average is the simple mean of the hours held, each hour once, not weighted by the grid's load or by any buyer's.", r["text"])
        self.assertEqual(r["emDashes"], 0)


if __name__ == "__main__":
    unittest.main()
