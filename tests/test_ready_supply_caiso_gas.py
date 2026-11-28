"""Ready for the owner's ruling (session 11407, chain 770 part C): California's gas burned for power on /supply read
from CAISO's own supply by fuel throughout.

The audit (session 10222, docs/reviews/supply-model-audit-2026-11-26.md, finding 1, test branch wip/audit-supply-2)
found California's gas row, and the seven grids' total, compared across the change from EIA-930's hours to CAISO's own
supply on 16 December 2025. The other choice, made here: warehouse/derived/supply_page.py reads California's gas from
caiso_fuel_supply_history and caiso_fuel_supply in every week (CAISO_OWN_GAS, caiso_own_hours), marks the two gas rows
caiso_own, and site/lib/supply.ts writes no "crosses a change of source" on a row so marked. site/data/supply.json is
rebuilt at landing by the desk (a data machine's run); the page file here is still main's.

1. The rule on two small made-up tables (no real figure).
2. The builder and the page's words read from the files.
3. Measured with the builder's code on the main checkout's tables (skipped where they are not on the machine, or the
   page file is not the one of the week ending 13 November 2026): California on the year -22.8 percent becomes +0.8,
   its five-year average 1.89 becomes 1.73 Bcf/d, the seven grids' total of 30 October 2026 +3.49 becomes +6.46.
"""
import csv
import datetime as dt
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import supply_page as sp  # noqa: E402
import mix_profile as mp  # noqa: E402
import caiso_join as cj  # noqa: E402

MAIN_OUT = os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")
EVIDENCE = os.path.join(ROOT, "docs", "reviews", "supply-model-audit-2026-11-26", "burn_caiso.csv")


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def write_table(path, hours, skip=()):
    """A table in the warehouse's series shape: every hour gives all thirteen columns (gas 1,000 MW, the rest 100)
    but those named in skip, a set of (hour, column)."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# made up for a test\n")
        w = csv.writer(f)
        w.writerow(["entity", "variable", "ts_utc", "value", "unit"])
        for ts, gas in hours:
            for c in cj.ALL:
                if (ts, c) not in skip:
                    w.writerow(["caiso:ISO", c, ts, gas if c == "natural_gas_mw" else 100.0, "MW"])


class TheRule(unittest.TestCase):
    def test_caiso_own_hours(self):
        with tempfile.TemporaryDirectory() as d:
            write_table(os.path.join(d, mp.HISTORY + ".csv"),
                        [("2019-03-01T08:00:00Z", 1000.0), ("2019-03-01T09:00:00Z", 1000.0), ("2019-03-01T10:00:00Z", 1000.0)],
                        skip={("2019-03-01T10:00:00Z", "wind_mw")})
            write_table(os.path.join(d, cj.SUPPLY + ".csv"), [("2019-03-01T09:00:00Z", 2000.0), ("2026-01-05T08:00:00Z", 500.0)])
            x = sp.caiso_own_hours(d, lambda *_: None)
            hours = [t.strftime("%Y-%m-%dT%H") for t in x.index]
            self.assertEqual(hours, ["2019-03-01T08", "2019-03-01T09", "2026-01-05T08"])   # an hour short of a column is absent
            self.assertEqual(list(x["natural_gas"]), [1000.0, 2000.0, 500.0])             # the later table's hour where both hold it
            self.assertTrue(x["held"].all())
            self.assertEqual(list(x["day"]), ["2019-03-01", "2019-03-01", "2026-01-05"])   # the Pacific day
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                sp.caiso_own_hours(d, lambda *_: None)


class TheBuilderAndThePage(unittest.TestCase):
    def test_the_builder_reads_californias_gas_from_caiso_own(self):
        self.assertTrue(sp.CAISO_OWN_GAS)
        src = read("warehouse", "derived", "supply_page.py")
        self.assertIn('weekly[("caiso", "natural_gas")] = burn_weeks(caiso_own_hours(in_dir, log)', src)
        self.assertIn('extra={"caiso_own": True} if own else None', src)
        self.assertIn('extra={"caiso_own": True} if mine else None', src)

    def test_a_marked_row_says_nothing_of_a_change_of_source(self):
        lib = read("site", "lib", "supply.ts")
        body = lib[lib.index("export function joinWords("):]
        body = body[:body.index("\n}\n")]
        self.assertIn("if (r.caiso_own) return null;", body)
        self.assertIn("caiso_own?: boolean;", lib)
        note = read("docs", "methods", "supply_and_trade.md")
        self.assertIn("California's natural gas from CAISO's own supply throughout (session 11407", note)
        self.assertIn("+3.49 percent on the year, becomes +6.46", note)


class Measured(unittest.TestCase):
    def test_on_the_main_checkouts_tables(self):
        if not all(os.path.exists(os.path.join(MAIN_OUT, n + ".csv")) for n in (mp.HISTORY, cj.SUPPLY)) or not os.path.exists(EVIDENCE):
            self.skipTest("CAISO's two supply tables are not on this machine")
        rows = {r["id"]: r for r in json.loads(read("site", "data", "supply.json"))["rows"]}
        ca, tot = rows.get("burn-caiso-natural-gas"), rows.get("burn-all-natural-gas")
        if not ca or ca.get("status") != "ok" or ca["last"]["t"] != "2026-11-13" or not tot or tot["last"]["t"] != "2026-10-30":
            self.skipTest("the page file is not the one measured (California's week ending 13 November 2026)")
        self.assertEqual(round(ca["year"]["pct"], 1), -22.8)                      # main's file, before
        self.assertEqual(round(ca["avg5"]["v"], 2), 1.89)
        own = sp.burn_weeks(sp.caiso_own_hours(MAIN_OUT, lambda *_: None), mp.GRIDS["caiso"]["tz"], ["natural_gas"])["natural_gas"]
        spark = {dt.date.fromisoformat(t): v for t, v in zip(ca["spark"]["t"], ca["spark"]["v"])}
        after_join = [d for d in spark if d in own and d >= dt.date(2025, 12, 26)]
        self.assertGreaterEqual(len(after_join), 40)
        for d in after_join:                                                       # CAISO's own weeks are the file's
            self.assertAlmostEqual(spark[d], own[d], places=4)
        series = dict(own)
        series.update({d: v for d, v in spark.items() if d > max(own)})
        c = sp.compare(series, "W")
        self.assertEqual(c["year"]["t"], "2025-11-14")
        self.assertEqual(round(c["year"]["pct"], 1), 0.8)                         # after
        self.assertAlmostEqual(c["avg5"]["v"], 1.725, places=3)
        self.assertEqual(round(c["avg5"]["pct"], 1), -15.6)
        eia = {r["week_end"]: float(r["value"]) for r in csv.DictReader(open(EVIDENCE, encoding="utf-8")) if r.get("fuel") == "natural_gas"}
        base = tot["year"]["t"]
        alt = tot["year"]["v"] - eia[base] + own[dt.date.fromisoformat(base)]
        self.assertEqual(round(tot["year"]["pct"], 2), 3.49)
        self.assertEqual(round(100 * (tot["last"]["v"] - alt) / alt, 2), 6.46)


if __name__ == "__main__":
    unittest.main()
