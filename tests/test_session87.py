"""Session 87: who owns the batteries (warehouse/derived/storage_owners.py, storage_owners_monthly, /storage/owners).

Energy Research Warehouse (ERW). The builder is tested on made-up units (companies that do not exist), only to exercise
the arithmetic; the table, its agreement with the build-out table and the page's snapshot are tested where the machine
holds them.

    python -m unittest tests.test_session87 -v
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
for p in ("warehouse", "warehouse/connectors", "warehouse/derived", "warehouse/supabase"):
    sys.path.insert(0, os.path.join(ROOT, p))

import storage_buildout as sb  # noqa: E402
import storage_owners as so  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SNAPSHOT = os.path.join(SITE, "data", "storage_owners.json")


def unit(i, owner, name, ba, mw, mwh="", pm="BA"):
    return dict(entity_id=f"eia860:{i}:1", utility_id=owner, operator=name, balancing_authority=ba, prime_mover=pm,
                nameplate_mw=str(mw), energy_capacity_mwh=str(mwh), vintage="2026-08")


def tables(op, pl):
    return pd.DataFrame(op), pd.DataFrame(pl if pl else [unit(999, "9", "Nine", "PJM", 1)]).iloc[0:len(pl)]


def metrics(rows):
    return {(r["entity"], r["grid"], r["metric"]): r["value"] for r in rows}


class Builder(unittest.TestCase):
    def setUp(self):
        op = [unit(1, "1", "Alpha Storage LLC", "CISO", 100, 400), unit(2, "1", "Alpha Storage LLC", "CISO", 50, 100),
              unit(3, "2", "Beta Power", "CISO", 150, ""), unit(4, "2", "Beta Power", "ERCO", 20, 20),
              unit(5, "3", "Gamma Co", "AZPS", 10, 40), unit(6, "4", "Not A Battery", "CISO", 500, "", pm="PV")]
        pl = [unit(7, "1", "Alpha Storage LLC", "ERCO", 200), unit(8, "5", "Epsilon Development", "CISO", 300)]
        self.rows, self.st = so.build(pd.DataFrame(op), pd.DataFrame(pl))
        self.m = metrics(self.rows)

    def test_a_companys_megawatts_hours_and_units_by_grid(self):
        a = "eia860:utility:1"
        self.assertEqual((self.m[(a, "caiso", "operating_mw")], self.m[(a, "caiso", "operating_mwh")], self.m[(a, "caiso", "operating_units")]), (150.0, 500.0, 2.0))
        self.assertEqual(self.m[(a, "caiso", "operating_hours")], 3.3333)          # 500 MWh over 150 MW, half up
        self.assertEqual((self.m[(a, "ercot", "planned_mw")], self.m[(a, "ercot", "planned_units")]), (200.0, 1.0))
        self.assertNotIn((a, "ercot", "operating_mw"), self.m)                     # no unit there: no row, never a zero
        self.assertEqual(self.m[(a, "us", "operating_mw")], 150.0)
        self.assertEqual(self.m[(a, "us", "planned_mw")], 200.0)

    def test_a_duration_is_omitted_where_no_unit_reports_energy(self):
        b = "eia860:utility:2"
        self.assertEqual(self.m[(b, "caiso", "operating_mwh")], 0.0)
        self.assertNotIn((b, "caiso", "operating_hours"), self.m)
        self.assertEqual(self.m[(b, "us", "operating_hours")], 1.0)                # its Texas unit alone: 20 MWh over 20 MW
        self.assertEqual(self.m[("iso:caiso", "caiso", "operating_hours")], 3.3333)   # over the units that report energy only

    def test_rank_ties_by_name_and_shares(self):
        # CAISO: Alpha 150 MW and Beta 150 MW tie; Alpha comes first by name
        self.assertEqual((self.m[("eia860:utility:1", "caiso", "operating_rank")], self.m[("eia860:utility:2", "caiso", "operating_rank")]), (1.0, 2.0))
        self.assertEqual(self.m[("eia860:utility:1", "caiso", "operating_share_pct")], 50.0)
        self.assertEqual(self.m[("iso:caiso", "caiso", "top5_share_pct")], 100.0)
        us = [self.m[(f"eia860:utility:{k}", "us", "operating_rank")] for k in ("2", "1", "3")]
        self.assertEqual(us, [1.0, 2.0, 3.0])                                      # Beta 170, Alpha 150, Gamma 10
        self.assertEqual(self.m[("eia860:utility:2", "us", "operating_share_pct")], 51.52)   # 170 of 330, half up

    def test_grids_totals_and_companies(self):
        self.assertEqual(self.m[("iso:caiso", "caiso", "operating_mw")], 300.0)    # the solar unit is not a battery
        self.assertEqual(self.m[("us:outside_isos", "outside_isos", "operating_mw")], 10.0)
        self.assertEqual(self.m[("us:total", "us", "operating_mw")], 330.0)
        self.assertEqual((self.m[("us:total", "us", "owners_operating")], self.m[("us:total", "us", "owners_planned")]), (3.0, 2.0))
        self.assertEqual(self.m[("us:total", "us", "planned_mw")], 500.0)
        self.assertEqual(self.m[("iso:pjm", "pjm", "operating_mw")], 0.0)
        self.assertNotIn(("iso:pjm", "pjm", "top5_share_pct"), self.m)             # no operating MW: no share, never a zero
        self.assertFalse([k for k in self.m if k[2].startswith("planned_mwh")])    # EIA's planned sheet has no energy
        self.assertEqual((self.st["owners_operating"], self.st["owners_planned"], self.st["owners_both"]), (3, 2, 1))

    def test_a_company_with_planned_units_only_has_no_rank(self):
        e = "eia860:utility:5"
        self.assertEqual(self.m[(e, "caiso", "planned_mw")], 300.0)
        self.assertNotIn((e, "caiso", "operating_rank"), self.m)
        self.assertNotIn((e, "caiso", "operating_mw"), self.m)

    def test_one_id_two_names_or_two_vintages_stop_the_build(self):
        op = [unit(1, "1", "Alpha", "CISO", 1, 1), unit(2, "1", "Alpha Renamed", "CISO", 1, 1)]
        with self.assertRaises(RuntimeError):
            so.build(pd.DataFrame(op), pd.DataFrame([unit(3, "2", "B", "CISO", 1)]))
        other = unit(3, "2", "B", "CISO", 1)
        other["vintage"] = "2026-07"
        with self.assertRaises(RuntimeError):
            so.build(pd.DataFrame([unit(1, "1", "Alpha", "CISO", 1, 1)]), pd.DataFrame([other]))

    def test_the_series_shape(self):
        s = so.to_series(self.rows, "2026-08", "2026-10-04T00:00:00Z")
        self.assertEqual(list(s.columns), so.COLS)
        self.assertFalse(s.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(set(s["ts_utc"]), {"2026-08-01T00:00:00Z"})
        r = s[(s["entity"] == "eia860:utility:1") & (s["variable"] == "caiso_operating_mw")].iloc[0]
        self.assertEqual((r["value"], r["unit"], r["x_grid"], r["x_metric"], r["x_owner"]), (150.0, "MW", "caiso", "operating_mw", "Alpha Storage LLC"))
        self.assertLessEqual(set(s["unit"]), {"MW", "MWh", "MWh/MW", "count", "pct"})


class Table(unittest.TestCase):
    """The table, where the machine holds it."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(OUT, so.NAME + ".csv")
        if not os.path.exists(path):
            raise unittest.SkipTest("storage_owners_monthly.csv is not on this machine")
        cls.t = sb.read(path)
        cls.t["value"] = cls.t["value"].astype(float)
        cls.month = cls.t["ts_utc"].max()
        cls.t = cls.t[cls.t["ts_utc"] == cls.month]
        cls.v = {(e, k): x for e, k, x in zip(cls.t["entity"], cls.t["variable"], cls.t["value"])}

    def test_it_agrees_with_the_build_out_table(self):
        path = os.path.join(OUT, "storage_buildout_monthly.csv")
        if not os.path.exists(path):
            self.skipTest("storage_buildout_monthly.csv is not on this machine")
        b = sb.read(path)
        b = b[b["ts_utc"] == self.month]
        if b.empty:
            self.skipTest("the build-out table is of another inventory month")
        bv = {(e, k): float(x) for e, k, x in zip(b["entity"], b["variable"], b["value"])}
        for grid, entity in so.GRID_ENTITY.items():
            self.assertEqual(self.v[(entity, f"{grid}_operating_mw")], bv[(entity, "battery_operating_mw")], grid)
            self.assertEqual(self.v[(entity, f"{grid}_operating_mwh")], bv[(entity, "battery_operating_mwh")], grid)
            self.assertEqual(self.v[(entity, f"{grid}_operating_units")], bv[(entity, "battery_operating_units")], grid)
            self.assertEqual(self.v[(entity, f"{grid}_planned_mw")], bv[(entity, "battery_planned_mw")], grid)

    def test_each_grids_companies_sum_to_the_grid_and_ranks_are_given_once(self):
        own = self.t[self.t["entity"].str.startswith("eia860:utility:")]
        for grid, entity in so.GRID_ENTITY.items():
            g = own[own["x_grid"] == grid]
            mw = g[g["x_metric"] == "operating_mw"]["value"]
            self.assertAlmostEqual(mw.sum(), self.v[(entity, f"{grid}_operating_mw")], places=3, msg=grid)
            self.assertAlmostEqual(g[g["x_metric"] == "planned_mw"]["value"].sum(), self.v[(entity, f"{grid}_planned_mw")], places=3, msg=grid)
            self.assertEqual(len(mw), self.v[(entity, f"{grid}_owners_operating")], grid)
            ranks = sorted(g[g["x_metric"] == "operating_rank"]["value"])
            self.assertEqual(ranks, [float(i) for i in range(1, len(ranks) + 1)], grid)
            if len(mw) and mw.sum() > 0:
                top5 = round(mw.sort_values(ascending=False).head(5).sum() / mw.sum() * 100, 2)
                self.assertAlmostEqual(top5, self.v[(entity, f"{grid}_top5_share_pct")], delta=0.011, msg=grid)
        seven = sum(self.v[(f"iso:{g}", f"{g}_operating_mw")] for g in sb.ISO_OF_BA.values())
        self.assertAlmostEqual(seven + self.v[("us:outside_isos", "outside_isos_operating_mw")], self.v[("us:total", "us_operating_mw")], places=3)

    def test_the_pages_snapshot_is_the_table(self):
        if not os.path.exists(SNAPSHOT):
            self.skipTest("site/data/storage_owners.json is not written yet")
        with open(SNAPSHOT, encoding="utf-8") as f:
            snap = json.load(f)
        if snap["month"] != self.month[:7]:
            self.skipTest("the snapshot is of another inventory month than this machine's table")
        n = 0
        for grid, g in snap["grids"].items():
            for metric, value in g.items():
                if metric != "entity":
                    self.assertEqual(value, self.v[(g["entity"], f"{grid}_{metric}")], (grid, metric))
                    n += 1
        for entity, o in snap["owners"].items():
            for grid, ms in o["grids"].items():
                for metric, value in ms.items():
                    self.assertEqual(value, self.v[(entity, f"{grid}_{metric}")], (entity, grid, metric))
                    n += 1
        self.assertEqual(n, len(self.t))                                           # every row is in it, and nothing else


class Page(unittest.TestCase):
    def src(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
            return f.read()

    def test_in_review_reads_the_snapshot_and_states_what_an_owner_is(self):
        self.assertRegex(self.src("site", "lib", "release.ts"), r'"/storage/owners":\s*"review"')
        page = self.src("site", "app", "storage", "owners", "page.tsx")
        self.assertIn('import data from "@/data/storage_owners.json"', page)
        self.assertNotIn("@/lib/supabase", page)
        self.assertIn("robots: { index: false, follow: false }", page)
        for piece in ("ToolPage", "ToolHeader", "InputPanel", "HeadlineRow", "ChartFrame", "ToolSection", "Fold", "SourceLine"):
            self.assertIn(f"<{piece}", page)                                       # the battery page's layout
        flat = " ".join(page.split())
        self.assertIn("often a project company", flat)
        self.assertIn("nothing here merges names", flat)
        import load
        import yaml
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(so.NAME, yaml.safe_load(f)["catalogue_hold"])
        self.assertIsNone(load.live_rule(so.NAME))

    def test_the_pages_model(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on this machine")
        js = """
import * as c from './lib/storageowners.ts';
const s = { table: c.TABLE, month: '2026-08', built: '20261004T000000Z', source: '', source_urls: [], counts: {},
  grids: { us: { entity: 'us:total', operating_mw: 330 }, caiso: { entity: 'iso:caiso', operating_mw: 300 } },
  owners: {
    'eia860:utility:1': { name: 'Alpha', grids: { us: { operating_mw: 150, operating_rank: 2, planned_mw: 200 }, caiso: { operating_mw: 150, operating_rank: 1 } } },
    'eia860:utility:2': { name: 'Beta', grids: { us: { operating_mw: 170, operating_rank: 1 }, caiso: { operating_mw: 150, operating_rank: 2 } } },
    'eia860:utility:5': { name: 'Epsilon', grids: { us: { planned_mw: 300 }, caiso: { planned_mw: 300 } } },
    'eia860:utility:6': { name: 'Delta', grids: { us: { planned_mw: 200 } } } } };
const us = c.view(s, c.choices({}).grid), ca = c.view(s, c.choices({ grid: 'caiso' }).grid);
console.log(JSON.stringify({
  def: c.choices({ grid: 'nonsense' }).grid.slug, grids: c.GRIDS.map((g) => g.slug),
  usOp: us.operating.map((r) => r.name), usPl: us.planned.map((r) => r.name), caOp: ca.operating.map((r) => r.name), caPl: ca.planned.map((r) => r.name),
  key: c.rowKey('iso:caiso', 'caiso', 'operating_mw', '2026-08'), shown: [c.shown(1234.56, 1), c.shown(undefined), c.shown(3)], month: c.monthName('2026-08'),
}));
"""
        r = subprocess.run([node, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        d = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(d["def"], "us")
        self.assertEqual(sorted(d["grids"]), sorted(so.GRIDS))
        self.assertEqual((d["usOp"], d["caOp"]), (["Beta", "Alpha"], ["Alpha", "Beta"]))       # by the table's rank
        self.assertEqual((d["usPl"], d["caPl"]), (["Epsilon", "Alpha", "Delta"], ["Epsilon"]))  # by planned MW, then name
        self.assertEqual(d["key"], "series|storage_owners_monthly|iso:caiso|caiso_operating_mw|2026-08-01T00:00:00Z")
        self.assertEqual((d["shown"], d["month"]), (["1,234.6", "not held", "3"], "August 2026"))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for rel in ("site/app/storage/owners/page.tsx", "site/lib/storageowners.ts", "warehouse/derived/storage_owners.py",
                    "docs/methods/storage_owners.md", "tests/test_session87.py"):
            self.assertNotIn(chr(0x2014), self.src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
