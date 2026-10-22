"""Session 700: the All grids tab of /cost-of-power (chain 050, docs/methods/siting.md). The row list is the tables'
own: every hub and zone of "Your load"'s index (built from the price tables), the regions the page names and does not
price, and every node of node_basis_daily that is neither a hub nor a load zone; the node file agrees with the table
where the table is on this machine, and with coverage.csv's count of its points everywhere. The four profiles set three
inputs and nothing else; the tab's rules (a view of the one page, its keys read by check-values, the existing views
kept). No request and no model call."""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import siting_page as sp  # noqa: E402

SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def data(*parts):
    return json.loads(src("site", "data", *parts))


def node_rows():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "scripts/siting-files.mjs", "rows"], cwd=SITE, capture_output=True, text=True, timeout=120, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


def coverage_row(table):
    cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str)
    m = cov[cov["table"] == table]
    return m.iloc[0] if len(m) else None


class Rows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = node_rows()
        cls.index = data("datacenter", "index.json")
        cls.nodes = data("siting", "nodes.json")

    def test_the_hub_rows_are_the_index_regions_and_the_named_unpriced(self):
        want = {f"{g}:{r['id']}" for g, v in self.index["grids"].items() for r in v["regions"]}
        for g, b in self.index["blank"].items():
            want |= {f"{g}:{r}" for r in b["regions"]} if b["regions"] else {f"{g}:grid"}
        got = [r["id"] for r in self.rows["hubs"]]
        self.assertEqual(len(got), len(set(got)), "a row is listed twice")
        self.assertEqual(set(got), want)
        self.assertEqual(self.rows["stat"]["hubs"], len(want))

    def test_the_rows_are_sorted_by_grid_then_name(self):
        names = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "isone": "ISO-NE", "spp": "SPP", "miso": "MISO", "pjm": "PJM"}
        keys = [(names[r["grid"]], r["region"]) for r in self.rows["hubs"]]
        self.assertEqual([k[0] for k in keys], sorted(k[0] for k in keys))

    def test_every_unpriced_row_says_why(self):
        for r in self.rows["hubs"]:
            if r["grid"] in self.index["grids"]:
                self.assertNotIn("blank", r)
            else:
                self.assertTrue(r["blank"]["words"] and r["blank"]["why"], r["id"])

    def test_the_node_rows_are_the_node_file_and_coverage_counts_its_points(self):
        ids = [r["region"] for r in self.rows["nodes"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {n["id"] for n in self.nodes["nodes"]})
        self.assertEqual(self.rows["stat"]["nodes"], len(ids))
        self.assertTrue(all(not i.startswith(("HB_", "LZ_")) for i in ids))
        cov = coverage_row("node_basis_daily")
        self.assertIsNotNone(cov)
        # coverage counts every point of the table: the nodes, the hubs and the load zones
        self.assertEqual(int(cov["n_nodes"]), self.nodes["points"])
        self.assertEqual(self.nodes["points"], len(ids) + self.nodes["hubs"] + self.nodes["zones"])

    def test_the_node_file_matches_the_table_where_it_is_here(self):
        for d in [os.path.join(ROOT, "warehouse", "output"), os.path.join(ROOT, "runs", "archive_restore")]:
            p = os.path.join(d, "node_basis_daily.csv")
            if os.path.exists(p):
                break
        else:
            raise unittest.SkipTest("node_basis_daily is not on this machine")
        ents = set()
        for ch in pd.read_csv(p, skiprows=sp.header_rows(p), usecols=["entity", "x_class"], dtype=str, chunksize=500_000):
            ents |= set(ch.loc[~ch["x_class"].isin(["hub", "zone"]), "entity"])
        self.assertEqual({e.split(":", 1)[1] for e in ents}, {n["id"] for n in self.nodes["nodes"]})


class Profiles(unittest.TestCase):
    def test_four_profiles_each_set_three_inputs_with_sources(self):
        s = src("site", "lib", "siting.ts")
        for pid in ("datacenter", "flexible", "electrolyzer", "industry"):
            block = re.search(rf"\n  {pid}: \{{(.*?)\n  \}},", s, re.S)
            self.assertIsNotNone(block, pid)
            b = block.group(1)
            for k in ("lf:", "curtail:", "interruptible:", "source:"):
                self.assertIn(k, b, (pid, k))
        self.assertIn('lf: 0.9, lfRange: [0.9, 0.9], curtail: "none"', s)          # datacenter: flat 0.90, never curtails
        self.assertIn('lf: 0.55, lfRange: [0.4, 0.7], curtail: "below_strike"', s)  # electrolyzer: 0.40 to 0.70, below a strike
        self.assertIn('lf: 0.8, lfRange: [0.8, 0.8], curtail: "interruptible", strike: null, interruptible: true', s)  # heavy industry


class Page(unittest.TestCase):
    def test_the_tab_is_a_view_of_the_one_page_and_the_old_views_stay(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn('{item("load", "Your load")}{item("allgrids", "All grids")}{item("grids", "Grid by grid")}', page)
        self.assertIn('x.view === "allgrids" ? <AllGridsView q={q} />', page)
        self.assertIn('q.view === "allgrids" ? "allgrids"', src("site", "lib", "datacenter.ts"))

    def test_check_values_reads_the_tab_and_its_keys(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('"/cost-of-power?view=allgrids", "/cost-of-power?view=allgrids&rows=nodes"', cv)
        self.assertIn('if (p[0] === "allgrids")', cv)
        view = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('check="allgrids|rows|nodes"', view)
        self.assertIn('check="allgrids|rows|hubs"', view)

    def test_no_em_dash_in_the_files_of_this_session(self):
        for p in [("site", "lib", "siting.ts"), ("site", "lib", "sitingdata.ts"), ("site", "app", "cost-of-power", "AllGridsView.tsx"),
                  ("site", "app", "cost-of-power", "AllGridsForm.tsx"), ("site", "scripts", "siting-files.mjs"), ("warehouse", "derived", "siting_page.py"),
                  ("docs", "methods", "siting.md")]:
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
