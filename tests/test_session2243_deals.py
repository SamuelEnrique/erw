"""Session 2243 (chain 156): the datacenter tracker's table and rollups (site/lib/dcrollups.ts,
site/app/datacenters/, warehouse/derived/datacenter_facilities.py).

Node runs the rollups on rows shaped as the live set serves datacenter_facilities: a sum of the MW stated by the rows
the page counts (a named US state, not cancelled), the rows stating none counted beside it, no sum where none states
MW, the grid read from the state for a row built before this session. The builder is run as a trial (no Census
request, a temporary folder) on small tables: a news facility's named grid wins, a queue's ISO comes next, then the
state's grid; the MW basis is that of the member the MW is from.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def fac(i, op, state, mw, status="planned", **x):
    return {"entity_id": f"datacenter:{i}", "capacity_mw": mw, "status": status, "operator": op, "extra": {"state": state, **x}}


ROWS = [fac(1, "Google", "TX", 200), fac(2, "Google", "TX", None), fac(3, "Meta", "LA", None),
        fac(4, "Meta", "LA", 500, status="withdrawn"), fac(5, "Nebius", "", 50), fac(6, "Fermi", "TX", 222, grid="ERCOT", grid_basis="queue")]


class Rollups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = node("const R = await import('./lib/dcrollups.ts');"
                     f"const rows = {json.dumps(ROWS)};"
                     "console.log(JSON.stringify({grid: R.rollups(rows, 'grid'), op: R.rollups(rows, 'operator'),"
                     " basis: rows.map(R.gridBasisOf), key: R.rollupKey('without', 'grid', '')}));")

    def by(self, dim, v):
        return next(x for x in self.r[dim] if x["value"] == v)

    def test_a_sum_of_the_counted_rows_with_the_rest_beside_it(self):
        e = self.by("grid", "ERCOT")
        self.assertEqual((e["facilities"], e["counted"], e["mw"], e["withMw"], e["without"]), (3, 3, 422, 2, 1))
        m = self.by("grid", "MISO")
        self.assertEqual((m["counted"], m["mw"], m["without"]), (1, None, 1))   # the withdrawn 500 MW is not counted
        n = self.by("grid", "")
        self.assertEqual((n["facilities"], n["counted"]), (1, 0))               # no US state: not in the sums

    def test_the_grid_basis(self):
        self.assertEqual(self.r["basis"], ["state", "state", "state", "state", "", "queue"])

    def test_by_operator_and_the_key(self):
        self.assertEqual(self.by("op", "Google")["mw"], 200)
        self.assertEqual(self.r["key"], "datacenters|rollup_without|grid|-")


class TheBuilder(unittest.TestCase):
    def test_the_grid_and_the_mw_basis(self):
        import datacenter_facilities as dcf
        d = tempfile.mkdtemp(prefix="erw_s2243_")
        src = os.path.join(d, "in")
        os.makedirs(src)
        news_cols = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
                     "source", "source_url", "retrieved_at", "vintage", "kind", "developer", "site_name", "state", "county",
                     "city", "mw", "phase", "project_status", "planned_year", "power_source", "utility", "ai_power", "confidence",
                     "geo_precision", "geo_note", "first_story_at", "n_stories", "story_ids", "story_urls", "model_id",
                     "extracted_at", "mw_basis", "power_kind", "grid", "grid_basis", "utility_eia861", "utility_eia861_number",
                     "utilities_in_county", "energized_year", "country", "fields_version"]
        base = {c: "" for c in news_cols}
        rows = [dict(base, entity_id="datacenter:a", name="Abilene", operator="Crusoe", state="TX", city="Abilene", mw="1200",
                     mw_basis="total", grid="ERCOT", grid_basis="named", status="planned", source="x",
                     source_url="https://example.org/a", story_urls="https://example.org/a", first_story_at="2026-10-01"),
                dict(base, entity_id="datacenter:b", name="", operator="Meta", state="LA", city="Richland", mw="2000",
                     mw_basis="it", grid="MISO", grid_basis="state", status="planned", source="x",
                     source_url="https://example.org/b", story_urls="https://example.org/b", first_story_at="2026-10-02")]
        with open(os.path.join(src, "datacenter_projects.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# fixture\n")
            pd.DataFrame(rows, columns=news_cols).to_csv(f, index=False)
        out = os.path.join(d, "out")
        old = os.environ.get("ERW_LOCK_EXEMPT")
        os.environ["ERW_LOCK_EXEMPT"] = "1"
        try:
            rc = dcf.main(["--in-dir", src, "--out-dir", out, "--no-gazetteer"])
        finally:
            if old is None:
                os.environ.pop("ERW_LOCK_EXEMPT", None)
            else:
                os.environ["ERW_LOCK_EXEMPT"] = old
        self.assertEqual(rc, 0)
        t = pd.read_csv(os.path.join(out, "datacenter_facilities.csv"), comment="#", dtype=str, keep_default_na=False).set_index("entity_id")
        self.assertEqual((t.loc["datacenter:a", "grid"], t.loc["datacenter:a", "grid_basis"], t.loc["datacenter:a", "mw_basis"]), ("ERCOT", "named", "total"))
        # the projects table's state reading is read again here, as the state's
        self.assertEqual((t.loc["datacenter:b", "grid"], t.loc["datacenter:b", "grid_basis"], t.loc["datacenter:b", "mw_basis"]), ("MISO", "state", "it"))
        shutil.rmtree(d, ignore_errors=True)


class TheSources(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(SITE, *p), encoding="utf-8") as f:
            return f.read()

    def test_the_table(self):
        s = self.read("app", "datacenters", "DatacentersTable.tsx")
        for w in ('name="Grid"', 'name="Power"', "MW at most", 'data-download="csv"', 'data-download="py"', 'data-download="do"',
                  'setCountry(""); setState(""); setStatus(""); setOperator(""); setKind(""); setMinMw("");'):
            self.assertIn(w, s)
        self.assertNotIn("—", s)

    def test_the_page_and_the_check(self):
        self.assertIn("<Rollups rows={res.data} />", self.read("app", "datacenters", "page.tsx"))
        self.assertIn('String(p[1]).startsWith("rollup_")', self.read("scripts", "check-values.mjs"))


if __name__ == "__main__":
    unittest.main()
