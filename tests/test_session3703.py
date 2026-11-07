"""Sessions 3703 and 3704 (chain 208): the Grid tool's replication a reader can run (replication/grid/).

The network's figures are computed twice on the committed snapshot: by the page's own functions (network_figures.mjs,
node) and by replicate.py without them; every one must agree. Both read the snapshot as it is on the day, so the daily
run's new snapshot never turns this test red. The carbon months and the Ask panel's stored figures need the warehouse's
tables, which a clean checkout lacks: those tests skip there and run on a machine that holds them. replicate.py's
mix_now is held to the Mix tab's latest-hour rules on a small fixture. No network, no model.
"""
import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "replication", "grid")
SNAPSHOT = os.path.join(ROOT, "site", "data", "grid_network.json")
# the tables are read from warehouse/output, or from the folder ERW_REPLICATION_TABLES names (a worktree holds none)
TABLES = os.environ.get("ERW_REPLICATION_TABLES") or os.path.join(ROOT, "warehouse", "output")


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REP, file))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class TheNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(SNAPSHOT):
            raise unittest.SkipTest("the network's snapshot is not in this copy")
        if shutil.which("node") is None:
            raise unittest.SkipTest("node is not installed: the page's own code cannot be run")
        cls.r = module("replicate_grid", "replicate.py")
        cls.b = module("figures_of_the_page_grid", "figures_of_the_page.py")
        cls.a = load(os.path.join(REP, "assumptions.json"))
        cls.page = cls.b.network_group(SNAPSHOT, os.path.join(ROOT, "no-tables-here"))
        cls.snap = load(SNAPSHOT)
        cls.hour, _, _, cls.mine = cls.r.network(cls.snap, {}, cls.a)

    def test_the_same_hour(self):
        self.assertEqual(self.hour, self.page["hour"])

    def test_every_network_figure_agrees_with_the_pages_code(self):
        figs = [f for f in self.page["figures"] if f["tab"] in ("network", "gravity")]
        self.assertGreaterEqual(len(figs), 40)
        missing = [f["check"] for f in figs if f["check"] not in self.mine]
        self.assertEqual(missing, [])
        differ = [(f["check"], f["raw"], self.mine[f["check"]]) for f in figs if abs(self.mine[f["check"]] - f["raw"]) > 1e-9]
        self.assertEqual(differ, [])

    def test_the_gravity_share_with_generation(self):
        # with generation given, the share is the net import over it, as the page's calc|pct key
        gen = {b: 10000.0 + i for i, b in enumerate(self.r.ISOS)}
        _, _, _, v = self.r.network(self.snap, gen, self.a)
        for ba in self.r.ISOS:
            net = v.get(f"net|import|{ba}|{self.hour}")
            if net is None:
                continue
            gk = f"series|eia930_all_generation|eia930:{ba}|net_generation_mw|{self.hour}"
            key = f"calc|pct|net~import~{ba}~{self.hour}|{gk.replace('|', '~')}"
            self.assertAlmostEqual(v[key], net / gen[ba] * 100, places=9)

    def test_the_committed_figures_are_this_snapshots_or_older(self):
        committed = load(os.path.join(REP, "page_figures.json"))
        if committed["snapshot_built"] != self.snap["built"]:
            self.skipTest(f"the snapshot was rebuilt ({self.snap['built']}); page_figures.json is of {committed['snapshot_built']}")
        mine = {f["check"]: f["raw"] for f in committed["figures"] if f["group"] in ("network", "gravity")}
        page = {f["check"]: f["raw"] for f in self.page["figures"] if f["tab"] in ("network", "gravity")}
        self.assertEqual(mine, page)


class TheTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        need = ("carbon_intensity_hourly", "eia930_all_emissions", "carbon_intensity_monthly", "cost_of_power_monthly")
        if not all(os.path.exists(os.path.join(TABLES, t + ".csv")) for t in need):
            raise unittest.SkipTest("the warehouse's tables are not on this machine (a clean checkout holds none)")
        cls.r = module("replicate_grid_t", "replicate.py")
        cls.a = load(os.path.join(REP, "assumptions.json"))
        cls.page = load(os.path.join(REP, "page_figures.json"))

    def test_the_carbon_months_are_rebuilt_from_the_hours(self):
        keys = [f["check"] for f in self.page["figures"] if f["check"].startswith("series|carbon_intensity_monthly|")]
        self.assertEqual(len(keys), 14)
        got = self.r.carbon(TABLES, keys)
        rows = self.r.read_table(TABLES, "carbon_intensity_monthly", sorted({k.split("|")[2] for k in keys}), ["intensity_generation"],
                                 usecols=["entity", "variable", "ts_utc", "value"])
        table = {(e, t): float(v) for e, t, v in zip(rows["entity"], rows["ts_utc"], rows["value"])}
        for k in keys:
            _, _, e, _, t = k.split("|")
            if (e, t) in table and k in got:
                self.assertAlmostEqual(got[k], table[(e, t)], delta=0.005, msg=k)

    def test_the_ask_figures_met_or_explained(self):
        _, ask = self.r.compute(SNAPSHOT, TABLES, self.page, self.a, {"ask"})
        rows = self.r.compare({}, ask, self.page, self.a, {"ask"}, TABLES)
        self.assertEqual([r[0]["check"] for r in rows if r[1].startswith("NO")], [])
        self.assertGreaterEqual(sum(1 for r in rows if r[1] == "yes"), 40)


class TheRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = module("replicate_grid_rules", "replicate.py")
        cls.b = module("figures_of_the_page_rules", "figures_of_the_page.py")

    def test_mix_now_follows_the_mix_tabs_rules(self):
        e = "eia930:ERCO"
        demand = pd.DataFrame([
            {"entity": e, "variable": "demand_mw", "ts_utc": "2026-11-01T10:00:00Z", "value": "40000"},
            {"entity": e, "variable": "demand_mw", "ts_utc": "2026-11-08T10:00:00Z", "value": "42000"},
            {"entity": e, "variable": "demand_mw", "ts_utc": "2026-11-08T09:00:00Z", "value": "41000"},
        ])
        gen = pd.DataFrame([
            {"entity": e, "variable": "net_generation_mw", "ts_utc": "2026-11-08T09:00:00Z", "value": "41500"},
            {"entity": e, "variable": "net_generation_natural_gas_mw", "ts_utc": "2026-11-08T09:00:00Z", "value": "20000"},
            {"entity": e, "variable": "net_generation_wind_mw", "ts_utc": "2026-11-08T09:00:00Z", "value": "15000"},
            {"entity": e, "variable": "net_generation_wind_mw", "ts_utc": "2026-11-08T10:00:00Z", "value": "25000"},   # no total: not the hour
        ])
        ci = pd.DataFrame([
            {"entity": e, "variable": "intensity_generation", "ts_utc": "2026-11-08T08:00:00Z", "value": "300.5"},
            {"entity": e, "variable": "intensity_demand", "ts_utc": "2026-11-08T07:00:00Z", "value": "310.25"},
        ])
        out, top = self.r.mix_now(demand, gen, ci, "ERCO")
        self.assertEqual(out[f"series|eia930_all_demand|{e}|demand_mw|2026-11-08T10:00:00Z"], 42000)
        self.assertEqual(out[f"series|eia930_all_demand|{e}|demand_mw|2026-11-01T10:00:00Z"], 40000)
        self.assertEqual(out[f"series|eia930_all_generation|{e}|net_generation_mw|2026-11-08T09:00:00Z"], 41500)
        self.assertEqual(top, "net_generation_natural_gas_mw")
        self.assertNotIn(f"series|eia930_all_generation|{e}|net_generation_wind_mw|2026-11-08T10:00:00Z", out)
        self.assertEqual(out[f"series|carbon_intensity_hourly|{e}|intensity_demand|2026-11-08T07:00:00Z"], 310.25)

    def test_the_license_hold_is_the_sites(self):
        tables = self.b.license_tables()
        day = "2026-11-06"
        self.assertTrue(self.b.license_held_row(tables, "cost_of_power_monthly", "nyiso:N.Y.C.", day))
        self.assertFalse(self.b.license_held_row(tables, "cost_of_power_monthly", "ercot:HB_HUBAVG", day))
        self.assertFalse(self.b.license_held_row(tables, "cost_of_power_monthly", "nyiso:N.Y.C.", "2026-10-20"))
        self.assertFalse(self.b.license_held_row(tables, "carbon_intensity_monthly", "eia930:NYIS", day))
        self.assertEqual(self.b.grid_of_entity("iso:isone"), "isone")
        self.assertEqual(self.b.grid_of_entity("nyiso_queue:1630"), "nyiso")

    def test_a_query_runs_as_the_ask_tools(self):
        folder = os.path.join(ROOT, "runs", "test_session3703")
        os.makedirs(folder, exist_ok=True)
        rows = ["# a fixture", "entity,variable,ts_utc,value,unit,freq",
                "a:X,v,2025-01-01T00:00:00Z,1,u,P1M", "a:X,v,2025-02-01T00:00:00Z,3,u,P1M", "a:X,v,2026-01-01T00:00:00Z,10,u,P1M",
                "b:Y,v,2025-01-01T00:00:00Z,100,u,P1M"]
        with open(os.path.join(folder, "fix.csv"), "w", encoding="utf-8") as f:
            f.write("\n".join(rows) + "\n")
        q = self.r.run_query
        self.assertEqual(q(folder, "fix", {"aggregation": "mean", "entity": "a:X", "variable": "v", "start": "2025-01-01", "end": "2026-01-01"}), [2, 2.0, 2])
        self.assertEqual(q(folder, "fix", {"aggregation": "latest", "entity": "a:X", "variable": "v"}), [3, 10.0])
        self.assertEqual(q(folder, "fix", {"aggregation": "sum", "variable": "v", "group_by": "year"}), [4, 2, 104.0, 3, 10.0, 1, 57.0])
        self.assertEqual(q(folder, "fix", {"aggregation": "count", "variable": "v"}, {"slug": "a", "by": "entity"}), [3, 3])
        shutil.rmtree(folder, ignore_errors=True)

    def test_python_imports_the_standard_library_and_pandas_only(self):
        for name in ("replicate.py", "figures_of_the_page.py"):
            with open(os.path.join(REP, name), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom):
                    mods.add((node.module or "").split(".")[0])
            self.assertEqual({m for m in mods if m not in sys.stdlib_module_names and m != "pandas"}, set(), name)

    def test_the_held_answers_print_license_needed(self):
        page = load(os.path.join(REP, "page_figures.json"))
        held = [f for f in page["figures"] if f["held"]]
        self.assertTrue(held)
        for f in held:
            self.assertEqual(f["page_text"], "license needed")
            self.assertIsNone(f["raw"])


if __name__ == "__main__":
    unittest.main()


def do_file_faults(lines):
    """The owner's Stata rules: no line continuation; one empty line between commands outside a loop or a program, none
    inside; every destring with force. The faults found, as (line, why)."""
    faults, depth = [], 0
    text = "\n".join(lines)
    if "///" in text:
        faults.append((0, "a line continuation"))
    if "\n\n\n" in text:
        faults.append((0, "two empty lines in a row"))
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("destring") and "force" not in s:
            faults.append((i + 1, "destring without force"))
        opens = s.endswith("{") or s.startswith("program define")
        closes = s == "}" or s == "end"
        if opens:
            depth += 1
            if i + 1 < len(lines) and lines[i + 1].strip() == "":
                faults.append((i + 2, "an empty line inside a block"))
            continue
        if closes:
            depth -= 1
            if depth == 0 and i + 1 < len(lines) and lines[i + 1].strip() != "":
                faults.append((i + 1, "no empty line after a block"))
            continue
        if depth and s == "":
            faults.append((i + 1, "an empty line inside a block"))
        elif not depth and s and i + 1 < len(lines) and lines[i + 1].strip() != "":
            faults.append((i + 1, "two commands without an empty line between them"))
    return faults


class TheDoFiles(unittest.TestCase):
    def test_the_owners_rules(self):
        for name in ("replicate.do", "replicate_ask.do"):
            with open(os.path.join(REP, name), encoding="utf-8") as f:
                lines = f.read().splitlines()
            self.assertEqual(do_file_faults(lines), [], name)

    def test_the_ask_blocks_are_the_plain_queries(self):
        with open(os.path.join(REP, "replicate_ask.do"), encoding="utf-8") as f:
            text = f.read()
        page = load(os.path.join(REP, "page_figures.json"))
        held = {f["check"].rsplit("|", 1)[0] for f in page["figures"] if f["group"] == "ask" and f["held"]}
        for label in held:
            self.assertIn(f"* {label}: license needed", text)
        self.assertGreaterEqual(text.count('erw_read "$tables/'), 20)
        with open(os.path.join(REP, "replicate.do"), encoding="utf-8") as f:
            self.assertIn("do replicate_ask.do", f.read())
