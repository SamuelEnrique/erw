"""Ruling alternative 2 of /prices/compare (session 7724, 17 November 2026, branch wip/alt-compare-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-compare-2026-11-17.md, line 2): monthly rows, so
the reader chooses any months (summer 2026, calendar 2025)? On this branch the builder computes every month from January
2025 to the end month into the site's copy ("months"; warehouse/derived/price_compare.py MONTHS_FROM, the table keeps its
two windows) and the page's "Any months" section combines a run of them (site/lib/pricecompare.ts anyMonths: the mean
price and the shares of hours weighted by each month's hours held). Pinned with the builder's own build and the page's own
anyMonths on the local tables where they are on the machine (warehouse/output, or the folder ERW_TABLES_DIR names): mean
day-ahead price, calendar 2025 and summer 2026 (June to August): SPP North 28.09 and 40.17; CAISO SP15 32.22 and 34.83;
ERCOT Hub average 33.50 and 30.96 (the twelve months to October 2026: 34.27, 30.27 and 34.59).

    python -m unittest tests.test_alt_compare_2 -v
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import price_compare as pc  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
NEED = ("iso_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices", "carbon_intensity_daily")


class TheRule(unittest.TestCase):
    def test_the_first_month_and_the_read(self):
        self.assertEqual(pc.MONTHS_FROM, "2025-01")
        with open(os.path.join(ROOT, "warehouse", "derived", "price_compare.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('read_prices(inputs, min("2025-08-01", f"{MONTHS_FROM}-01"), log)', s)
        self.assertIn('months={k[2:]: v for k, v in view.items() if k.startswith("m:")}', s)


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in NEED), "the price tables are not on this machine")
class OnTheLocalTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logs = []
        log = logs.append
        x = pc.read_prices(TABLES, "2025-01-01", log)
        end_month = pc.last_whole_month(x[x["table"] == "iso_hub_prices_history"], {"miso": "paused"})
        rows, view, held, windows = pc.build(x, TABLES, end_month, {"miso": "paused"}, log)
        cls.end_month = end_month
        months = {k[2:]: v for k, v in view.items() if k.startswith("m:")}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "months.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(months, f, default=float)
            js = ("import fs from 'node:fs'; const P = await import('./lib/pricecompare.ts');"
                  "const m = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));"
                  "const pick = (a) => Object.fromEntries(a.map((r) => [r.entity, r.avg]));"
                  "process.stdout.write(JSON.stringify({ y2025: pick(P.anyMonths(m, '2025-01', '2025-12', 'dam')), summer: pick(P.anyMonths(m, '2026-06', '2026-08', 'dam')) }));")
            p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", js, path], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_calendar_2025_and_summer_2026(self):
        for e, y, s in (("spp:SPPNORTH_HUB", 28.09, 40.17), ("caiso:TH_SP15_GEN-APND", 32.22, 34.83), ("ercot:HB_HUBAVG", 33.50, 30.96)):
            self.assertEqual((round(self.f["y2025"][e], 2), round(self.f["summer"][e], 2)), (y, s), e)


if __name__ == "__main__":
    unittest.main()
