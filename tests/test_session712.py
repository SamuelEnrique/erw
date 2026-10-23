"""Session 712: the method note v1 and the replication of the All grids tab. The note names every column's formula,
table, vintage and license, the four profiles, the dated decisions and the limits; the replication is standard library
only and ports lib/datacenter.ts's hours and months: on a fixture year it gives the twelve months, the flat price and an
electrolyzer's strike as the site's own code does. No request, no model call."""
import ast
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "replication"))
import siting as rep  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Note(unittest.TestCase):
    def test_the_note_v1(self):
        n = src("docs", "methods", "siting.md")
        self.assertTrue("Version 1, session 712" in n or "version 1 was session 712's" in n or "version 1 session 712's" in n)   # 740 wrote version 2, 762 version 3, 784 version 4, 973 version 5
        for head in ("**Energy**", "**Transmission and 4CP**", "**Capacity**", "**Time to connect**", "**Headroom**", "**Carbon**", "**Utility**", "**All-in**"):
            self.assertIn(head, n)
        for part in ("## The load's profiles", "## The screen", "## The replication", "## Decisions", "## The limits"):
            self.assertIn(part, n)
        self.assertNotIn(chr(0x2014), n)


class Replication(unittest.TestCase):
    def test_standard_library_only(self):
        tree = ast.parse(src("warehouse", "replication", "siting.py"))
        mods = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        mods |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertTrue(mods <= {"argparse", "calendar", "csv", "html", "json", "math", "os", "re", "sys", "urllib", "datetime"}, mods)

    def test_the_port_agrees_with_the_site_on_a_fixture(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        prices = [float(i % 24 + 10) for i in range(8760)]
        prices[100], prices[200] = 2000.0, 1500.0
        f = {"grid": "ercot", "year": 2025, "hours": 8760, "built": "", "regions": {"A": {"da": {"s": 0, "v": prices}}}}
        py = rep.profile_twelve([f], "A", "electrolyzer", 0, {"summers": []}, "ercot")
        flat = rep.flat_twelve([f], "A", "da")
        script = ("const S = await import('./lib/siting.ts'); const L = await import('./lib/datacenter.ts');"
                  "const dc = { monthsRuled: L.monthsRuled, lastTwelve: L.lastTwelve, span: L.span, years: L.years, expand: L.expand, monthsOfYear: L.monthsOfYear, monthStarts: L.monthStarts };"
                  "const prices = Array.from({ length: 8760 }, (_, i) => (i % 24) + 10); prices[100] = 2000; prices[200] = 1500;"
                  "const file = { grid: 'ercot', year: 2025, hours: 8760, built: '', regions: { A: { da: { s: 0, v: prices } } } };"
                  "const f = { index: { grids: { ercot: { std_hours_behind_utc: 0, regions: [{ id: 'A' }] } }, blank: {} }, nodes: { nodes: [] }, years: () => [file] };"
                  "const t = S.profileTwelve(dc, f, 'ercot', 'A', { profile: 'electrolyzer', lf: 0.55, strike: null });"
                  "const fl = S.twelveOf(dc, f, 'ercot', 'A', 'da');"
                  "process.stdout.write(JSON.stringify({ per: t.per, run: t.run, lost: t.lost, strike: t.strike, flat: fl.per, from: fl.from, to: fl.to }));")
        r = subprocess.run([exe, "--input-type=module", "-e", script], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        js = json.loads(r.stdout)
        self.assertAlmostEqual(py["per"], js["per"], places=9)
        self.assertEqual((py["run"], py["lost"], py["strike"]), (js["run"], js["lost"], js["strike"]))
        self.assertAlmostEqual(flat["per"], js["flat"], places=9)
        self.assertEqual((flat["from"], flat["to"]), (js["from"], js["to"]))

    def test_js_round_is_half_up(self):
        self.assertEqual((rep.js_round(2.5), rep.js_round(3.5), rep.js_round(-0.5)), (3, 4, 0))

    def test_the_hour_of_an_interval_is_model_ts_s(self):
        self.assertEqual(rep.hour_of("2025-07-30T21:45:00Z", 6), (2025, 210 * 24 + 15))
        self.assertEqual(rep.hour_of("2026-01-01T03:00:00Z", 6), (2025, 8760 - 3))


if __name__ == "__main__":
    unittest.main()
