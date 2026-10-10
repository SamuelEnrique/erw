"""Session 86: the battery model on the grids whose energy and reserve prices are both public (NYISO, SPP), in review.

Energy Research Warehouse (ERW). Covers the two-way regulation product in the daily program, the grids in review and
their duration rules (cited or labeled assumed: here, assumed), that the live table and the live page's numbers cannot
change, the review table and the page's snapshot where the machine holds them, and the page's gate: greyed for a
visitor, open only in the internal view; an internal grid says "held, not shown: license needed".

    python -m unittest tests.test_session86 -v
"""

import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
for p in ("warehouse", "warehouse/connectors", "warehouse/derived", "warehouse/supabase"):
    sys.path.insert(0, os.path.join(ROOT, p))

import battery_stack as bs  # noqa: E402
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SNAPSHOT = os.path.join(SITE, "data", "battery_stack_review.json")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TwoWayRegulation(unittest.TestCase):
    """NYISO buys regulation as one capacity product: an award must be able to move up and down."""

    def test_the_directions(self):
        self.assertEqual((bs.sides(True), bs.sides(False), bs.sides("both")), ((True, False), (False, True), (True, True)))

    def test_a_two_way_award_takes_power_and_energy_in_both_directions(self):
        T, price = 24, [10.0] * 24
        flat = [0.0] * T                                                   # energy costs and pays nothing: only the reserve pays
        for dur in (2, 4):
            both = bs.solve_day(flat, [price], (("both", 1.0),), dur)
            up = bs.solve_day(flat, [price], ((True, 1.0),), dur)
            down = bs.solve_day(flat, [price], ((False, 1.0),), dur)
            self.assertEqual(bs.check_day(both, (("both", 1.0),), dur), [])
            self.assertLessEqual(both["total"], up["total"] + 1e-6)        # never more than the same award one way
            self.assertLessEqual(both["total"], down["total"] + 1e-6)
            self.assertGreater(both["total"], 0)
            eta = np.sqrt(bs.RTE)
            aw, soc, c, d = both["awards"][0], both["soc"], both["charge"], both["discharge"]
            prev = 0.0
            for t in range(T):
                self.assertLessEqual(d[t] + aw[t], 1 + 1e-6)               # it shares the discharge side
                self.assertLessEqual(c[t] + aw[t], 1 + 1e-6)               # and the charge side
                self.assertLessEqual(aw[t] / eta, min(prev, soc[t]) + 1e-6)          # energy behind the upward half
                self.assertLessEqual(aw[t] * eta, dur - max(prev, soc[t]) + 1e-6)    # room behind the downward half
                prev = soc[t]
            self.assertLess(aw[0], 1e-6)                                   # from empty there is nothing to deliver upward in the first hour

    def test_the_one_way_programs_are_as_they_were(self):
        # the same day solved with booleans, as sessions 67 to 85 did: a two-way product changes nothing for them
        rng = np.random.default_rng(86)
        energy = list(rng.uniform(-5, 120, 24))
        res = [list(rng.uniform(0, 30, 24)), list(rng.uniform(0, 12, 24))]
        a = bs.solve_day(energy, res, ((True, 1.0), (False, 0.5)), 4)
        self.assertEqual(bs.check_day(a, ((True, 1.0), (False, 0.5)), 4), [])
        self.assertAlmostEqual(a["total"], a["energy"] + sum(a["reserve"]), places=6)


class Grids(unittest.TestCase):
    def test_the_live_table_keeps_its_two_grids_and_the_review_has_the_two_public_ones(self):
        self.assertEqual(list(bs.MARKETS), ["ercot", "caiso"])             # battery_stack_monthly cannot gain a grid by this session
        self.assertEqual(list(bs.REVIEW_MARKETS), ["nyiso", "spp"])
        self.assertEqual(bs.HELD, {"isone": "held, not shown: license needed", "miso": "held, not shown: license needed"})
        self.assertNotIn("pjm", bs.ALL_MARKETS)
        self.assertEqual(bs.REVIEW_NAME, "battery_stack_review_monthly")

    def test_a_review_grid_is_one_whose_reserve_prices_are_public_and_a_held_one_is_internal(self):
        import pandas as pd
        reg = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), dtype=str, keep_default_na=False)
        lic = {t: r["license"] for r in reg.to_dict("records") for t in r["tables"].split(";") if t}
        for iso, m in bs.REVIEW_MARKETS.items():
            self.assertEqual(lic[m["as_table"]], "public", iso)
        for iso in bs.HELD:
            self.assertEqual(lic[f"{iso}_as_prices"], "internal", iso)

    def test_every_duration_rule_is_cited_or_labeled_assumed(self):
        for iso, m in bs.ALL_MARKETS.items():
            for p in m["products"]:
                for first, hours, source in p["hours"]:
                    cited = "http" in source and not source.startswith(("assumed", "not verified"))
                    assumed = source.startswith(("assumed", "not verified"))
                    self.assertTrue(cited or assumed, (iso, p["key"], source))
                    self.assertGreater(hours, 0)
        # session 86 assumed one hour for both; session 100 read the operators' documents and session 102 carried the rules
        # here: every product is still one hour, SPP's four and NYISO's spinning reserve cited, NYISO's regulation assumed
        for iso, m in bs.REVIEW_MARKETS.items():
            for p in m["products"]:
                assumed = (iso, p["key"]) == ("nyiso", "reg")
                self.assertEqual([(h, s.startswith("assumed: one hour"), "http" in s) for _, h, s in p["hours"]], [(1.0, assumed, not assumed)], (iso, p["key"]))
        self.assertEqual([p["up"] for p in bs.REVIEW_MARKETS["nyiso"]["products"]], ["both", True])
        self.assertEqual([p["key"] for p in bs.REVIEW_MARKETS["spp"]["products"]], ["regup", "regdn", "spin", "supp"])   # no ramp, no uncertainty product

    def test_the_products_read_exist_in_the_reserve_tables(self):
        import pandas as pd
        for iso, m in bs.REVIEW_MARKETS.items():
            path = os.path.join(OUT, m["as_table"] + ".csv")
            if not os.path.exists(path):
                self.skipTest(f"{m['as_table']}.csv is not on this machine")
            t = pd.read_csv(path, comment="#", usecols=["entity", "variable"]).drop_duplicates()
            have = set(zip(t["entity"], t["variable"]))
            for p in m["products"]:
                self.assertIn((p["entity"], p["variable"]), have, (iso, p["key"]))


class ReviewTable(unittest.TestCase):
    """The table and the page's snapshot, where the machine holds them."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(OUT, bs.REVIEW_NAME + ".csv")
        if not os.path.exists(path):
            raise unittest.SkipTest("battery_stack_review_monthly.csv is not on this machine")
        cols = ip.SERIES_COLS + ["x_strategy", "x_duration_hours", "x_metric"]
        cls.t = ip.read_series(path, cols)
        cls.t["value"] = cls.t["value"].astype(float)
        with open(path, encoding="utf-8") as f:
            cls.header = [ln for ln in f if ln.startswith("#")]

    def test_only_the_two_grids_and_public(self):
        self.assertEqual(sorted(set(self.t["entity"])), ["nyiso:N.Y.C.", "spp:SPPNORTH_HUB"])
        self.assertEqual(sorted(set(self.t["market"])), ["nyiso", "spp"])
        self.assertTrue(any(h.startswith("# License: public") for h in self.header))
        self.assertTrue(any("priced above the product kept in 0 of" in h for h in self.header))   # leaving two NYISO products out lost nothing

    def test_the_live_table_holds_none_of_them(self):
        path = os.path.join(OUT, bs.NAME + ".csv")
        if not os.path.exists(path):
            self.skipTest("battery_stack_monthly.csv is not on this machine")
        live = ip.read_series(path, ip.SERIES_COLS + ["x_strategy", "x_duration_hours", "x_metric"])
        self.assertEqual(sorted(set(live["market"])), ["caiso", "ercot"])

    def test_the_streams_add_up_and_no_month_is_a_zero_for_nothing(self):
        w = self.t.pivot_table(index=["entity", "x_strategy", "x_duration_hours", "ts_utc"], columns="x_metric", values="value")
        held = w[w["days_held"] > 0]
        self.assertTrue(np.allclose(held["revenue_total_usd_per_mw"], held["revenue_energy_usd_per_mw"] + held["revenue_ancillary_usd_per_mw"], atol=0.01))
        prod = [c for c in w.columns if c.startswith("revenue_") and c.split("_")[1] not in ("energy", "ancillary", "total")]
        self.assertTrue(np.allclose(held["revenue_ancillary_usd_per_mw"], held[prod].fillna(0).sum(axis=1), atol=0.01))
        self.assertTrue(((w["days_held"] + w["days_left_out"]) <= w["days_in_month"]).all())
        self.assertTrue(w[w["days_held"] == 0]["revenue_total_usd_per_mw"].isna().all())     # no day held: no revenue row
        self.assertEqual(sorted(set(self.t["x_duration_hours"].astype(int))), [2, 4, 8])

    def test_the_pages_snapshot_is_the_table(self):
        if not os.path.exists(SNAPSHOT):
            self.skipTest("site/data/battery_stack_review.json is not written yet")
        with open(SNAPSHOT, encoding="utf-8") as f:
            snap = json.load(f)
        self.assertEqual(sorted(snap["grids"]), ["nyiso", "spp"])
        have = {(e, v, ts): x for e, v, ts, x in zip(self.t["entity"], self.t["variable"], self.t["ts_utc"], self.t["value"])}
        n = 0
        for g in snap["grids"].values():
            for variable, ts, value in g["rows"]:
                self.assertEqual(value, have[(g["entity"], variable, ts)])
                n += 1
        self.assertEqual(n, len(self.t))


class Page(unittest.TestCase):
    def test_greyed_for_a_visitor_open_in_the_internal_view_and_held_where_internal(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on this machine")
        js = """
import * as b from './lib/batterystack.ts';
const g = Object.fromEntries(b.GRIDS.map((x) => [x.id, x]));
console.log(JSON.stringify({
  ready: b.READY.map((x) => x.id), review: b.IN_REVIEW.map((x) => x.id),
  why: Object.fromEntries(b.GRIDS.filter((x) => !x.ready).map((x) => [x.id, x.why])),
  visitor: ['ercot', 'caiso', 'nyiso', 'spp', 'isone', 'miso', 'pjm'].map((id) => b.inputsOf({ grid: id }).grid),
  internal: ['ercot', 'caiso', 'nyiso', 'spp', 'isone', 'miso', 'pjm'].map((id) => b.inputsOf({ grid: id }, true).grid),
  key: [b.parseKey('grid=nyiso&dur=4&strat=dayahead&mw=100&fom=22&ds=1').grid, b.parseKey('grid=nyiso&dur=4&strat=dayahead&mw=100&fom=22&ds=1', true).grid],
  products: { nyiso: b.PRODUCTS.nyiso.map((p) => p.key), spp: b.PRODUCTS.spp.map((p) => p.key) },
  assumed: [...b.REQUIREMENTS.nyiso, ...b.REQUIREMENTS.spp].map((r) => [r.assumed, r.rule]),
  cited: [...b.REQUIREMENTS.ercot, ...b.REQUIREMENTS.caiso].filter((r) => !r.assumed).length,
  words: [b.CAPACITY_WORDS.nyiso, b.CAPACITY_WORDS.spp, !!b.LEFT_OUT.nyiso, !!b.LEFT_OUT.spp], table: b.REVIEW_TABLE, entity: [g.nyiso.entity, g.spp.entity],
}));
"""
        r = subprocess.run([node, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        d = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual((d["ready"], d["review"]), (["ercot", "caiso"], ["nyiso", "spp"]))
        self.assertEqual(d["why"], {"pjm": "license needed", "nyiso": "coming", "isone": "held, not shown: license needed",
                                    "miso": "held, not shown: license needed", "spp": "coming"})
        self.assertEqual(d["visitor"], ["ercot", "caiso", "ercot", "ercot", "ercot", "ercot", "ercot"])    # a visitor's address cannot open one
        self.assertEqual(d["internal"], ["ercot", "caiso", "nyiso", "spp", "ercot", "ercot", "ercot"])     # nor can the internal view open a held grid
        self.assertEqual(d["key"], ["ercot", "nyiso"])
        self.assertEqual(d["products"], {"nyiso": ["reg", "spin"], "spp": ["regup", "regdn", "spin", "supp"]})
        self.assertEqual(d["assumed"], [[False, "1 hour"], [True, "1 hour"], [False, "60 minutes"]])   # session 102: session 100's verified rules; NYISO's regulation stays assumed
        self.assertGreater(d["cited"], 0)
        self.assertEqual((d["table"], d["entity"]), ("battery_stack_review_monthly", ["nyiso:N.Y.C.", "spp:SPPNORTH_HUB"]))

    def test_the_products_and_durations_on_the_page_are_the_models(self):
        ts = src("site", "lib", "batterystack.ts")
        for iso, m in bs.REVIEW_MARKETS.items():
            block = ts[ts.index(f"  {iso}: [", ts.index("export const PRODUCTS")):]
            for p in m["products"]:
                self.assertIn(f'key: "{p["key"]}"', block[:400], (iso, p["key"]))

    def test_the_page_opens_them_with_the_cookie_only_and_reads_the_snapshot(self):
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertIn("have === (await digest(token))", page)                # the proxy's own test of the internal cookie
        self.assertIn("inputsOf(Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === \"string\" ? v : undefined])), internal)", page)
        self.assertIn('import reviewData from "@/data/battery_stack_review.json"', page)
        branch = page[page.index("const [read, readStress] = g.review"):]
        branch = branch[:branch.index(";\n")]
        self.assertLess(branch.index("reviewRows(x.grid, x)"), branch.index("rowsOf(g.entity!, x)"))   # a review grid never asks Supabase
        self.assertIn("is in review and shown in the internal view only", page)
        form = src("site", "app", "cost-of-power", "battery", "BatteryForm.tsx")
        self.assertIn("const open = g.ready || (internal && !!g.review);", form)
        self.assertIn("disabled={!open}", form)
        # session 166 (the owner's instruction of 8 October 2026): the battery page is in review too; no page is live
        release = src("site", "lib", "release.ts")
        self.assertRegex(release, r'"/cost-of-power/battery":\s*"review"')
        self.assertEqual(re.findall(r'"(/[^"]*)":\s*"live"', release), [])

    def test_held_out_of_the_live_catalogue(self):
        import load
        import yaml
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = yaml.safe_load(f)
        self.assertIn(bs.REVIEW_NAME, live["catalogue_hold"])
        self.assertIsNone(load.live_rule(bs.REVIEW_NAME))
        self.assertIsNotNone(load.live_rule(bs.NAME))                        # the live table is where it was

    def test_no_em_dash_in_what_the_session_wrote(self):
        for rel in ("warehouse/derived/battery_stack.py", "site/lib/batterystack.ts", "site/app/cost-of-power/battery/page.tsx",
                    "site/app/cost-of-power/battery/BatteryForm.tsx", "docs/methods/battery_stack.md", "tests/test_session86.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
