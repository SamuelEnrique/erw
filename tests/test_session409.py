"""Session 409: the method notes against the pages (site/scripts/check-methods.mjs).

Energy Research Warehouse (ERW). No network, no model, no site: the script's rule on known keys and notes, the page
to note mapping read from the pages' code, the keys file, and the script's own offline run over every page of
site/scripts/check-values-floor.json (exit 0 only when every figure of every page with a note is named).

    python -m unittest tests.test_session409 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
SCRIPT = os.path.join(SITE, "scripts", "check-methods.mjs")
KEYS = os.path.join(SITE, "scripts", "check-methods-keys.json")
FLOOR = os.path.join(SITE, "scripts", "check-values-floor.json")
NODE = shutil.which("node")


def node_eval(js):
    """Run an ES module snippet that imports the script's functions as M; return its printed JSON."""
    code = 'import * as M from "./scripts/check-methods.mjs";\n' + js
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stdout + r.stderr)
    return json.loads(r.stdout)


@unittest.skipUnless(NODE, "node is not installed")
class Rule(unittest.TestCase):
    def test_figures(self):
        out = node_eval("""
const k = [
  "series|carbon_intensity_hourly|eia930:CISO|intensity_generation|2026-10-17T23:00:00+00:00",
  "latest_prices|ercot:HB_HUBAVG|spp_rtm|2026-10-20T22:15:00+00:00",
  "series_sum|eia930_all_generation|net_generation_mw|2026-10-18T00:00:00Z|2026-10-19T00:00:00Z|eia930:US48",
  "event|energy_deals|deal:587d09fd8e27a774|dollars",
  "bs|grid=ercot&dur=4&strat=foresight&mw=100|l12_kw:total",
  "series|cost_of_power_hourly_profile|ercot:HB_HUBAVG|rt_mean_h03|2026-09-01T00:00:00+00:00",
  "calc|ratio|storage~iso_mw~ERCOT~operating|battery~fleet_mw",
  "es|uri_2021|eia930:ERCO|demand_mwh|pooled|est",
  "dcll|none of the seven|row:llstmt:48367a1ed351bb6c:mw",
];
console.log(JSON.stringify(k.map((x) => M.figures(x).map((f) => f.id))));
""")
        self.assertEqual(out, [
            ["carbon_intensity_hourly intensity_generation"],
            ["latest_prices spp_rtm"],
            ["eia930_all_generation net_generation_mw"],
            ["energy_deals dollars"],
            ["bs| l#_kw"],   # its number set aside (rule 3: l12_kw and l<n>_kw name it)
            ["cost_of_power_hourly_profile rt_mean_h#"],
            ["storage| iso_mw", "battery| fleet_mw"],
            ["es| demand_mwh"],
            ["dcll| row"],   # large_load_public's grid "none of the seven" is a case, not the measure (finished 21 October)
        ])

    def test_named(self):
        out = node_eval("""
const f = (k) => M.figures(k)[0];
const t = (text, k) => M.named(M.noteWords(text), f(k));
console.log(JSON.stringify([
  t("the table `carbon_intensity_hourly`, its variable `intensity_generation`", "series|carbon_intensity_hourly|e:X|intensity_generation|2026-01-01"),
  t("the table carbon_intensity_hourly", "series|carbon_intensity_hourly|e:X|intensity_generation|2026-01-01"),
  t("carbon_intensity_hourly holds intensity generation", "series|carbon_intensity_hourly|e:X|intensity_generation|2026-01-01"),
  t("`cost_of_power_hourly_profile`, `rt_mean_h<hour>`", "series|cost_of_power_hourly_profile|e:X|rt_mean_h22|2026-01-01"),
  t("`shoulder_hours_monthly`: `year_mean_<shoulder_hours, fleet_mw>`", "series|shoulder_hours_monthly|e:X|year_mean_fleet_mw|2026-01-01"),
  t("`bs|<case>|l12_kw:<stream>`", "bs|grid=ercot|l12_kw:total"),
  t("l12_kw, with no family", "bs|grid=ercot|l12_kw:total"),
  t("`bs|` and l12_kwh", "bs|grid=ercot|l12_kw:total"),
]));
""")
        self.assertEqual(out, [True, False, True, True, True, True, False, False])

    def test_notes_of_pages(self):
        out = node_eval("""
const of = (route) => [...M.notesOf(M.codeFiles(M.pageFile(route))).keys()].sort();
console.log(JSON.stringify({ battery: of("/cost-of-power/battery"), policy: of("/policy"), impact: of("/impact"),
  grid: M.routeOf("/grid/ercot"), emissions: M.routeOf("/emissions"), home: of("/") }));
""")
        self.assertEqual(out["battery"], ["battery_earns_algorithm", "battery_stack"])
        self.assertEqual(out["policy"], ["policy_monitor"])      # a constant of lib/policyweek.ts, METHOD.href
        self.assertEqual(out["impact"], ["economic_impact"])     # a constant of lib/impact.ts
        self.assertEqual(out["grid"], "/grid")
        self.assertEqual(out["emissions"], "/grid")
        self.assertEqual(out["home"], [])


@unittest.skipUnless(NODE, "node is not installed")
class TheRun(unittest.TestCase):
    def test_keys_file_is_the_floors_pages(self):
        with open(KEYS, encoding="utf-8") as f:
            keys = json.load(f)
        with open(FLOOR, encoding="utf-8") as f:
            floor = json.load(f)["floor"]
        self.assertTrue(keys["pages"])
        self.assertTrue(set(keys["pages"]) <= set(floor))
        for page, ks in keys["pages"].items():
            self.assertTrue(ks, page)
            self.assertEqual(ks, sorted(set(ks)), page)

    def test_every_figure_named(self):
        r = subprocess.run([NODE, SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertNotIn("MISSING |", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr)
        m = re.search(r"^(\d+) of (\d+) figures named", r.stdout, re.M)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), m.group(2))

    def test_no_em_dash(self):
        with open(SCRIPT, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
