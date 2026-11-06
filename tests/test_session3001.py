"""Session 3001 (chain 164): the findings hunt over the whole warehouse, its builder and its first family (prices).

Energy Research Warehouse (ERW). warehouse/analysis/findings/deep/: builder.py tests a candidate's regions by the weekly
hunt's claim and five tests and writes each draft in the hunt's row form; prices.py holds eight candidates on ERCOT's
hourly prices, each with Python and Stata scripts that recompute its figure from the tables. These tests use small
tables written here: no warehouse file, no network, no database.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
DEEP = os.path.join(FIND, "deep")
sys.path.insert(0, FIND)
sys.path.insert(0, DEEP)
import builder  # noqa: E402
import hunt  # noqa: E402
import hunt_measures as hm  # noqa: E402
import prices  # noqa: E402

HUBS = ["HB_NORTH", "HB_WEST", "HB_HOUSTON", "HB_SOUTH", "HB_HUBAVG"]


def write_tables(d, days=4):
    """ERCOT's two price tables (15-minute real-time rows, one # line on top) and the fuel spot table, for `days` local days of 2015."""
    rng = np.random.default_rng(3001)
    start = pd.Timestamp("2015-01-01T06:00:00Z")
    ts = pd.date_range(start, periods=days * 96, freq="15min")
    def frame(nodes):
        out = []
        for i, node in enumerate(nodes):
            v = 25 + 10 * np.sin(np.arange(len(ts)) / 15.0 + i) + rng.normal(0, 4, len(ts))
            out.append(pd.DataFrame({"entity": "ercot:" + node, "variable": "price", "ts_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                     "value": np.round(v, 2), "market": "ercot_rtm", "node": node}))
        return pd.concat(out, ignore_index=True)
    for name, nodes in (("ercot_all_hub_prices_history", HUBS), ("ercot_zone_prices_history", ["LZ_WEST"])):
        with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# a test table\n")
            frame(nodes).to_csv(f, index=False, lineterminator="\n")
    hh = pd.DataFrame({"entity": "eia:henry_hub", "variable": "spot_price", "ts_utc": [f"2015-01-0{i}T00:00:00Z" for i in (1, 2, 3)],
                       "value": [2.9, 3.1, 3.0]})
    with open(os.path.join(d, "eia_fuel_spot_prices.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        hh.to_csv(f, index=False, lineterminator="\n")


class Reproduce(unittest.TestCase):
    def test_every_price_candidate_reproduces_from_the_table(self):
        """Each candidate's reproduce.py, run on the tables, prints the value the module computed for each region."""
        with tempfile.TemporaryDirectory() as d:
            write_tables(d)
            hm.clear_cache()
            for P in prices.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                for region in regions[:2] + [r for r in regions if "LZ_" in r][:1]:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    text = P["reproduce"](region)["py"]
                    self.assertNotIn(chr(0x2014), text)
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(text)
                    node = region[len("ercot_"):].replace("_north", "")
                    table = "ercot_zone_prices_history" if node.startswith("LZ_") else "ercot_all_hub_prices_history"
                    args = [sys.executable, "-I", path, os.path.join(d, table + ".csv")] + ([os.path.join(d, "eia_fuel_spot_prices.csv")] if P["name"] == "spark_spread" else [])
                    r = subprocess.run(args, capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
            hm.clear_cache()

    def test_every_do_file_keeps_the_owners_rules(self):
        for P in prices.CANDIDATES:
            region = "ercot_HB_WEST_north" if P["name"] == "hub_basis" else "ercot_HB_WEST"
            do = P["reproduce"](region)["do"]
            self.assertNotIn("///", do)
            self.assertNotIn("/*", do)
            self.assertIn("destring value, replace force", do)
            self.assertIn("list year measure n, noobs", do)
            blocks = do.strip("\n").split("\n\n")
            self.assertTrue(all("\n" not in b for b in blocks), P["name"])     # one command a block: no loop in these files


def synthetic(region_specs, years=range(2015, 2026)):
    """A candidate's function: each region rises (or falls) steadily, with full years of 8760 hours."""
    def fn(in_dir):
        rows, tables = [], {}
        for region, slope in region_specs:
            for i, y in enumerate(years):
                rows.append(hm._row(region, f"Place {region}", y, 50 + slope * i + (0.3 if i % 2 else -0.3), 8760))
            tables[region] = ["test_table"]
        return {"rows": rows, "tables": tables}
    return fn


class Builder(unittest.TestCase):
    def candidate(self, specs, area=None):
        P = builder.candidate("test_measure", "testfam", synthetic(specs), "USD per MWh", 2, 8000, 1.0, "A TEST MEASURE", "a test measure",
                              lambda w: f"the test measure at {w}", "A test's limits.",
                              lambda region: {"py": '"""a script"""\nprint(1)\n', "do": "* a do-file\n\nclear all\n"}, consequence=2)
        if area:
            P["area"] = area
        return P

    def test_a_passing_claim_is_drafted_with_its_files_and_document(self):
        P = self.candidate([("ercot_A", 3.0), ("ercot_B", 0.0)])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(builder, "DOCS", os.path.join(d, "docs")), \
                mock.patch.object(hunt, "blocked_grids", lambda meta_dir=None: set()):
            s = builder.run("testfam", [P], d, dry_run=True, log=lambda m: None, out_root=os.path.join(d, "runs"))
            self.assertEqual(len(s["drafts"]), 1)
            did = s["drafts"][0]
            self.assertTrue(did.startswith("scan-deep-"))
            row = json.load(open(os.path.join(d, "runs", os.listdir(os.path.join(d, "runs"))[0], "testfam", did + ".json"), encoding="utf-8"))
            self.assertEqual(row["rule"], "hunt")
            self.assertEqual(row["card"]["hunt"]["module"], "deep.testfam")
            self.assertEqual(len(row["card"]["hunt"]["tests"]), 5)
            self.assertEqual(sorted(row["files"]), sorted(row["card"]["hunt"]["files"]))
            self.assertIn("in 2025, against", row["card"]["subtitle"])
            self.assertIn("Expected: 2015", row["files"][did + "_reproduce.py"]["content"])
            doc = os.path.join(d, "docs", "testfam", "test-measure-ercot-a.md")
            text = open(doc, encoding="utf-8").read()
            for part in ("**The finding.**", "**The tables and rows.**", "**Its strength.**", "**Its limits.**", "**Reproduce.**", "`test_table`"):
                self.assertIn(part, text)
            self.assertTrue(os.path.exists(doc[:-3] + ".png"))
            flat = json.dumps(row, ensure_ascii=False)
            self.assertNotIn(chr(0x2014), flat)
            self.assertNotIn(chr(0x2013), flat)

    def test_one_area_is_one_story(self):
        P = self.candidate([("ercot_HB_X", 3.0), ("ercot_LZ_X", 3.1), ("ercot_HB_Y", 2.0)], area=lambda r: r.split("_")[-1])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(builder, "DOCS", os.path.join(d, "docs")), \
                mock.patch.object(hunt, "blocked_grids", lambda meta_dir=None: set()):
            s = builder.run("testfam", [P], d, dry_run=True, log=lambda m: None, out_root=os.path.join(d, "runs"))
        drafted = sorted(r["region"] for r in s["results"] if r["drafted"])
        self.assertEqual(len(drafted), 2)
        self.assertIn("ercot_HB_Y", drafted)
        self.assertEqual(len([r for r in drafted if r.endswith("_X")]), 1)
        folded = [r for r in s["results"] if r["region"].endswith("_X") and not r["drafted"]][0]
        self.assertIn("folded", folded["reason"])

    def test_a_blocked_grid_is_never_drafted(self):
        P = self.candidate([("nyiso_A", 3.0)])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(builder, "DOCS", os.path.join(d, "docs")), \
                mock.patch.object(hunt, "blocked_grids", lambda meta_dir=None: {"nyiso"}):
            s = builder.run("testfam", [P], d, dry_run=True, log=lambda m: None, out_root=os.path.join(d, "runs"))
        self.assertEqual(s["drafts"], [])

    def test_area_of_the_price_regions(self):
        self.assertEqual({prices.area(r) for r in ("ercot_HB_WEST", "ercot_LZ_WEST", "ercot_HB_WEST_north")}, {"WEST"})


class FixSourceLines(unittest.TestCase):
    def test_a_draft_of_chain_164_is_left_as_it_is(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import lock
        row = {"id": "scan-deep-000000000000", "state": "draft", "table_name": "t", "flag": {}, "files": {},
               "card": {"source_line": "Source: the ERW tables t.", "hunt": {"pattern": "daily_spread", "module": "deep.prices", "region": "ercot_HB_WEST"}}}

        class Reply:
            def raise_for_status(self):
                return None

            def json(self):
                return [row]

        sent, runs = [], []
        with tempfile.TemporaryDirectory() as out, mock.patch.object(lock, "env", create=True, new=lambda k: {
                "SUPABASE_URL": "https://example.invalid/rest/v1/", "SUPABASE_SERVICE_KEY": "not-a-key"}.get(k)):
            got = hunt.fix_source_lines(out, dry_run=False, log=lambda m: None, get=lambda *a, **k: Reply(), patch=lambda *a, **k: sent.append(a),
                                        compute=lambda *a: runs.append(a), out_dir=os.path.join(out, "p"))
        self.assertEqual([(o["id"], o["changed"], o["written"]) for o in got], [(row["id"], False, False)])
        self.assertEqual((sent, runs), ([], []))


if __name__ == "__main__":
    unittest.main()
