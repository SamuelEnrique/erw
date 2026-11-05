"""Session 701: the energy column of the All grids tab (docs/methods/siting.md). One function: each grid's main region
bought day-ahead is the figure "Your load" computes for it (scripts/datacenter-ways.mjs, pageOf, the page's own steps)
to the last digit; a node's figure is its hub's plus its mean daily basis over the hub's twelve months, drawn only
with at least 90 percent of the days; every row says why when it has no figure. No request and no model call."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(*args, script=None):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    cmd = [exe, *args] if script is None else [exe, "--input-type=module", "-e", script]
    r = subprocess.run(cmd, cwd=SITE, capture_output=True, text=True, timeout=600, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class Energy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = node("scripts/siting-files.mjs", "energy")

    def test_each_main_region_equals_your_load_bought_day_ahead(self):
        self.assertEqual(len(self.e["page"]), 5)
        for rid, per in self.e["page"].items():
            self.assertIsNotNone(per, rid)
            self.assertEqual(self.e["rows"][rid]["da"], per, rid)

    def test_every_priced_region_with_twelve_months_has_a_figure(self):
        idx = json.loads(src("site", "data", "datacenter", "index.json"))
        for g, gi in idx["grids"].items():
            for r in gi["regions"]:
                rid = f"{g}:{r['id']}"
                if r.get("da") and r["da"]["hours"] >= 8760:
                    self.assertTrue(self.e["rows"][rid]["da"] or self.e["rows"][rid]["rt"], rid)

    def test_unpriced_rows_have_no_figure(self):
        for rid, v in self.e["rows"].items():
            if rid.startswith(("miso:", "pjm:")):
                self.assertEqual(v, {"da": None, "rt": None}, rid)

    def test_most_nodes_are_drawn_and_none_in_real_time(self):
        nodes = {k: v for k, v in self.e["rows"].items() if k.startswith("ercot:") and not k.split(":")[1].startswith(("HB_", "LZ_"))}
        self.assertEqual(len(nodes), 873)
        self.assertGreater(sum(v["da"] is not None for v in nodes.values()), 700)
        self.assertTrue(all(v["rt"] is None for v in nodes.values()))


class NodeFormula(unittest.TestCase):
    def test_hub_plus_day_weighted_basis_and_the_ninety_percent_rule(self):
        script = (
            "const S = await import('./lib/siting.ts');"
            "const ms = [];for (let k = 0; k < 12; k++) { const d = new Date(Date.UTC(2025, 9 + k, 1)); ms.push({ m: d.toISOString().slice(0, 7), per: 30 }); }"
            "const hub = { per: 30, from: ms[0].m, to: ms[11].m, months: ms, hours: 8760, year: null };"
            "const full = {}; for (const r of ms) full[r.m] = [2, new Date(Date.UTC(+r.m.slice(0,4), +r.m.slice(5,7), 0)).getUTCDate()];"
            "full['2025-10'] = [-10, 31];"
            "const a = S.nodeEnergy(hub, { dam_basis: full });"
            "const thin = { '2025-10': [5, 31] };"
            "const b = S.nodeEnergy(hub, { dam_basis: thin });"
            "process.stdout.write(JSON.stringify({ a, b }));"
        )
        r = node(script=script)
        due = 365
        want = (2 * (due - 31) + -10 * 31) / due
        self.assertEqual(r["a"]["due"], due)
        self.assertEqual(r["a"]["days"], due)
        self.assertAlmostEqual(r["a"]["basis"], want, places=9)
        self.assertAlmostEqual(r["a"]["per"], 30 + want, places=9)
        self.assertIn("31 of the 365 days", r["b"]["why"])


class Page(unittest.TestCase):
    def test_the_cells_carry_their_keys_and_check_values_recomputes_them(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("check={`allgrids|energy|${r.id}|da`}", v)
        self.assertIn("check={`allgrids|energy|${r.id}|rt`}", v)
        self.assertIn("S.sitingStat(F.files(), check, await F.dc())", src("site", "scripts", "check-values.mjs"))

    def test_the_tab_uses_the_page_s_own_functions(self):
        d = src("site", "lib", "sitingdata.ts")
        self.assertIn("{ monthsRuled: DCL.monthsRuled, lastTwelve: DCL.lastTwelve, span: DCL.span, years: DCL.years", d)  # session 702 adds three after them
        self.assertNotIn(chr(0x2014), src("site", "lib", "siting.ts") + v_if_exists())


def v_if_exists():
    return src("site", "app", "cost-of-power", "AllGridsView.tsx")


if __name__ == "__main__":
    unittest.main()
