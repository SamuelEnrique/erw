"""Session 7404 (chain 303): the deal tracker's replication (replication/deals/), the month's cells as one library
function (site/lib/dealsview.ts, monthBlock), the grid a story names read by every view (site/lib/deals2.ts, toDeal),
and the script that runs the page's functions on the rows (site/scripts/deal-tracker-figures.mjs).

Every deal here is made up for the test: no row of the held table energy_deals is in this file. Two of the made-up
rows carry the ids of a pair the register folds (ids are not rows), so the fold is exercised on both sides.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "deals")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def module(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REP, "replicate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def pair():
    """The ids of the register's first folded pair (kept, duplicate)."""
    p = next(p for p in json.loads(src("site", "data", "deal_duplicates.json"))["pairs"] if p["ruling"] == "fold")
    return p["kept"], p["duplicate"]


def deal(i, date, deal_type, mw=None, price=None, status=None, event_id=None, **extra):
    x = {"deal_type": deal_type, "ai_power": "false", "confidence": "0.8", **extra}
    return {"event_id": event_id or f"deal:test{i:04d}", "event_date": f"{date}T00:00:00+00:00", "status": status, "mw": mw, "price": price, "currency": "USD",
            "parties": "", "source": "Made-up Wire", "source_url": f"https://example.org/{i}", "extra": {k: str(v) for k, v in x.items() if v not in (None, "")}}


def rows():
    kept, dup = pair()
    return [
        deal(1, "2026-11-03", "ppa", mw=100, price=42.5, status="signed", buyer="Alpha Cloud", seller="Sun Co", technology="solar", state="TX", ai_power="true", kind="ppa"),
        deal(2, "2026-11-05", "ppa", mw=300, price=55, status="signed", buyer="Alpha Cloud", seller="Wind Co", technology="wind", state="TX", ai_power="True", kind="ppa"),
        deal(3, "2026-10-20", "ppa", mw=200, price=48, buyer="Beta Corp", seller="Sun Co", technology="solar", state="CA", kind="ppa"),
        deal(4, "2026-10-21", "offtake", mw=50, price=60, buyer="Alpha Cloud", seller="Atom Co", technology="nuclear", ai_power="true", kind="smr", asset="small modular reactors"),
        deal(5, "2026-08-02", "m_and_a", status="signed", buyer="Gamma", seller="Delta", asset="Delta gas plant", technology="gas", dollars=3800000000, usd=3800000000, kind="m_and_a", event_id=kept),
        deal(6, "2026-08-02", "m_and_a", mw=900, status="rumored", buyer="Gamma", seller="Delta", asset="Delta gas plant", technology="gas", kind="m_and_a", event_id=dup),
        deal(7, "2026-07-11", "debt", buyer="Lender One; Lender Two", seller="Storage Co", asset="battery portfolio", technology="battery storage", dollars=500000000,
             kind="storage", grid="PJM", stage="financed"),
        deal(8, "2026-05-30", "other", mw=1200, buyer="Alpha Cloud", asset="gas turbines for a campus", technology="natural gas", ai_power="true", kind="gas_buildout",
             other_parties="Turbine Maker; Pipeline Co", dollars=2500000000),
        deal(9, "2026-04-02", "lease", buyer="Epsilon AI", seller="Hall Owner", asset="data center lease", ai_power="true", kind="compute_capacity", dollars=7500000000),
        deal(10, "2025-12-15", "equity_raise", seller="Zeta Fusion", technology="fusion", dollars=120000000, price_value=3.5, price_unit="USD/MMBtu", flags="headline: 150 MW; record: none"),
        deal(11, "2025-12-18", "fuel_supply", buyer="Beta Corp", seller="LNG Co", technology="LNG", status="cancelled"),
    ]


def page(tmp, month="2026-11"):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    with open(os.path.join(tmp, "energy_deals.json"), "w", encoding="utf-8") as f:
        json.dump(rows(), f)
    r = subprocess.run([exe, os.path.join("scripts", "deal-tracker-figures.mjs"), tmp, month], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-800:])
    return json.loads(r.stdout)


class TheMonthIsOneFunction(unittest.TestCase):
    def test_the_page_calls_the_library(self):
        p, lib = src("site", "app", "deals", "page.tsx"), src("site", "lib", "dealsview.ts")
        self.assertIn('import { monthBlock, rowOf } from "@/lib/dealsview";', p)
        self.assertIn("monthBlock(rows, current)", p)
        self.assertNotIn("const inMonth", p)                                  # the arithmetic is not in the page twice
        self.assertIn("export function monthBlock(rows: Row[], current: string)", lib)
        self.assertNotRegex(lib, r"(?m)^import ")                             # Node runs the file alone

    def test_the_two_readings_of_a_deals_grid_stand_as_they_were(self):
        # deals faults row 22 (a ruling, default unchanged): the tracker's views read the state alone (session 113's rule,
        # pinned by tests/test_session113.py and 466); the table's Grid column reads a grid a story names first (session 2238)
        self.assertIn('grid: STATE_GRID[state] ?? "",', src("site", "lib", "deals2.ts"))
        self.assertIn('grid: named || STATE_GRID[state] || "",', src("site", "lib", "dealsview.ts"))


class TheReplicationAgreesWithThePage(unittest.TestCase):
    def test_made_up_deals_key_by_key(self):
        rep = module("deals_replicate")
        pairs = json.loads(src("site", "data", "deal_duplicates.json"))["pairs"]
        with tempfile.TemporaryDirectory() as tmp:
            shown = page(tmp)["figures"]
        mine = rep.table(rows(), "2026-11")
        ds, n_folded = rep.folded_deals(rows(), pairs)
        mine.update(rep.tracker(ds, n_folded))
        mine.update(rep.comparables(ds))
        mine.update(rep.ai_view(ds))
        chart, party_mw = rep.charts(ds)
        mine.update(chart)
        mine.update(rep.top_parties(party_mw, shown))
        keys = [k for k in shown if not k.startswith("capital|")]
        self.assertGreater(len(keys), 150)
        for k in keys:
            self.assertIn(k, mine, k)
            self.assertAlmostEqual(float(mine[k]), float(shown[k]), delta=rep.tolerance(k, shown[k]), msg=k)
        for k in mine:
            self.assertIn(k, shown, k)                                        # nothing on one side only
        # the rules, on deals whose answers are known by hand
        self.assertEqual(shown["table|rows"], 11)                             # the table lists every row
        self.assertEqual(shown["tracker|deals"], 10)                          # the register's pair counted once
        self.assertEqual(shown["tracker|folded"], 1)
        self.assertEqual(shown["tracker|mw"], 100 + 300 + 200 + 50 + 1200)    # the folded duplicate's 900 MW leaves with its row
        self.assertEqual(shown["deals|month_count|2026-11"], 2)
        self.assertEqual(shown["deals|month_mw|2026-11"], 400)
        self.assertEqual(shown["deals|month_ai_pct|2026-11"], 100)            # "True" and "true" are one flag
        self.assertEqual(shown["tracker|grid|PJM"], 0)                        # named in a story, no state: the tracker reads the state alone
        self.assertEqual(shown["tracker|grid|ERCOT"], 2)
        self.assertEqual(shown["deals|comp_median_price|type|ppa"], 48)       # three power purchases state a price
        self.assertNotIn("deals|comp_median_price|type|offtake", shown)       # one: fewer than three, no median
        self.assertEqual(shown["deals|priced"], 4)
        self.assertEqual(shown["deals|price_median|year|2026"], 51.5)
        self.assertEqual(shown["deals|ai_tagged"], 5)
        self.assertEqual(shown["deals|ai_deals|supply|nuclear"], 1)
        self.assertEqual(shown["deals|ai_deals|supply|compute"], 1)
        self.assertEqual(shown["deals|ai_top_mw|1"], 1200)
        self.assertEqual(shown["deals|ai_top_usd|1"], 7500000000)             # a lease of compute is not a capital deal
        self.assertEqual(shown["tracker|with_other_price"], 1)                # a price in another unit, as extracted
        self.assertEqual(shown["table|filter|price|yes"], 5)
        self.assertEqual(shown["tracker|party|Alpha Cloud"], 4)
        self.assertEqual(shown["deals|chart_ai|2026-Q4|share"], 69.2)         # 450 of 650 MW

    def test_no_deal_this_month_shows_the_month_before(self):
        rep = module("deals_replicate_month")
        with tempfile.TemporaryDirectory() as tmp:
            got = page(tmp, "2026-12")
        self.assertEqual(got["figures"]["deals|month_count|2026-11"], 2)
        self.assertIn("the month before", got["words"]["table|month"])
        self.assertEqual(rep.table(rows(), "2026-12")["deals|month_count|2026-11"], 2)
        self.assertEqual(rep.table(rows(), "2026-01")["deals|month_count|2025-12"], 2)   # January's month before is December


class TheFiguresFile(unittest.TestCase):
    def test_every_figure_is_inside_its_tolerance_or_named(self):
        p = json.loads(src("replication", "deals", "page_figures.json"))
        self.assertEqual(p["tool"], "/deals")
        self.assertGreater(len(p["figures"]), 900)
        named = [f for f in p["figures"] if "named" in f]
        self.assertEqual([f["key"] for f in named], ["capital|n_rows"])       # the one difference, and it says why
        self.assertIn("data machine", named[0]["named"])
        for f in p["figures"]:
            if "named" not in f:
                self.assertLessEqual(abs(float(f["page"]) - float(f["replication"])), f["tolerance"] + 1e-9, f["key"])

    def test_no_row_of_the_held_table_is_committed_with_the_replication(self):
        self.assertEqual(src("replication", "deals", "rows", ".gitignore").split("\n")[2:4], ["*", "!.gitignore"])
        got = subprocess.run(["git", "ls-files", "replication/deals/rows"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        self.assertIn(got, ([], ["replication/deals/rows/.gitignore"]))


class NoEmDash(unittest.TestCase):
    def test_no_em_or_en_dash_in_what_the_session_wrote(self):
        for parts in (("site", "scripts", "deal-tracker-figures.mjs"), ("replication", "deals", "replicate.py"), ("replication", "deals", "fetch_rows.py"),
                      ("tests", "test_session7404_trackers.py")):
            for ch in (chr(0x2014), chr(0x2013)):
                self.assertNotIn(ch, src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
