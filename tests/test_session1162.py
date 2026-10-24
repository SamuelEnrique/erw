"""Session 1162 (chain 077): the Grid tool's method notes, check-methods' comma list, the rulings list.

Energy Research Warehouse (ERW). No network, no model, no site.

    python -m unittest tests.test_session1162 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)

NOTES = ("grid_network", "grid_network_v3", "generation_mix", "generation_mix_hourly", "grid_stress",
         "scarcity_hours_by_grid", "california_reliability")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def chain_section(text):
    """The text of the note's section dated chain 077, up to the next second-level heading."""
    m = re.search(r"^## [^\n]*\(chain 077, 23 October 2026\)\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


class TheNotes(unittest.TestCase):
    def test_each_note_has_its_dated_section_with_decisions(self):
        for n in NOTES:
            sec = chain_section(src("docs", "methods", f"{n}.md"))
            self.assertIsNotNone(sec, n)
            self.assertIn("Decisions (chain 077", sec, n)

    def test_the_panels_and_their_keys_are_named(self):
        g = src("docs", "methods", "grid_network.md")
        for w in ("grid_network_<grid>", "grid_gravity_<grid>", "grid_clean24_<grid>", "grid_mix_<grid>",
                  "grid_scarcity_<grid>", "grid_caisoalert_caiso", "grid_ask_<grid>", "net|tie|<BA>|<other>|<hour>",
                  "netsnap|<BA>|demand_mw|<hour>", "series_n|", "awe|last|<group>|<day>", "awe|ndays|<group>|<from>|<to>",
                  "eval_s302_fixtures.json", "eval_s320_first_run.json", "caisoJoinDay()", "169e537a"):
            self.assertIn(w, g)
        h = src("docs", "methods", "generation_mix_hourly.md")
        for w in ("The peak hour is the demand peak", "against the drawing clock", "session 118 ruling",
                  "<coal, hydro, natural_gas, nuclear, other, solar, storage, wind>_mwh", "eia930_subba_demand_hourly",
                  "latestHour", "weather: false"):
            self.assertIn(w, h)
        self.assertIn("35d2c31c", src("docs", "methods", "grid_network_v3.md"))
        self.assertIn("latest 30 days held, not the 30 days before today", src("docs", "methods", "scarcity_hours_by_grid.md"))
        self.assertIn("React's `cache`", src("docs", "methods", "california_reliability.md"))

    def test_no_em_dash(self):
        for p in [("docs", "methods", f"{n}.md") for n in NOTES] + [("docs", "reviews", "grid-rulings-2026-10-23.md"),
                                                                      ("site", "scripts", "check-methods.mjs")]:
            self.assertNotIn(EM, src(*p), p)


class TheRulings(unittest.TestCase):
    def test_grouped_one_a_line_each_with_a_session_and_a_recommendation(self):
        t = src("docs", "reviews", "grid-rulings-2026-10-23.md")
        heads = re.findall(r"^## (.+)$", t, re.M)
        self.assertEqual(heads, ["The page's words", "The design", "The data and licenses",
                                 "To finish: needs a person or a build, not a ruling"])
        rulings = t.split("## To finish")[0]
        items = [l for l in rulings.splitlines() if l.startswith("- ")]
        # Session 1176: chain 078's items joined the same three groups (tests/test_session1176.py counts them);
        # chain 077's 18 stand, each with its session of 1155 to 1161 as before.
        old = [l for l in items if re.search(r"\(Session 11(5[5-9]|6[01])[^)]*\)$", l)]
        self.assertEqual(len(old), 18)
        for l in items:
            self.assertIn("Recommendation:", l)
            self.assertRegex(l, r"\(Sessions? 11(5[5-9]|6\d|7[0-5])[^)]*\)$")


@unittest.skipUnless(NODE, "node is not installed")
class TheCommaList(unittest.TestCase):
    def test_a_comma_list_is_a_figure_of_each_variable(self):
        code = ('import * as M from "./scripts/check-methods.mjs";\n'
                'console.log(JSON.stringify(["series_sum|eia930_all_generation|net_generation_wind_mw,net_generation_wind_with_battery_mw|'
                '2026-10-22T00:00:00Z|2026-10-23T00:00:00Z|eia930:ERCO", "series_sum|eia930_all_generation|net_generation_mw|'
                '2026-10-22T00:00:00Z|2026-10-23T00:00:00Z|eia930:ERCO"].map((k) => M.figures(k).map((f) => f.id))));')
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), [
            ["eia930_all_generation net_generation_wind_mw", "eia930_all_generation net_generation_wind_with_battery_mw"],
            ["eia930_all_generation net_generation_mw"],
        ])


if __name__ == "__main__":
    unittest.main()
