"""Session 422: the five tools' checks on a built site, and the mirrors' headline figures against the pages.

Energy Research Warehouse (ERW). No network, no model, no build. Checks what session 422 wrote and what it can recompute
without a server: each of the five packs (docs/reviews/packs/) carries one paragraph "On a built site (session 422,
...)" inside its section "Against roadmap item 2", with no em or en dash; the four file-only mirrors run from their own
folders and print the headline figures the packs quote, which are the figures the pages drew at their defaults in the
build of 21 October (check-decisions-face.mjs's face.json); the Research mirror compares 304 figures with 0 different;
and the ten callouts check-analysis.mjs failed in that build each name NYISO or ISO-NE, the two grids held since
21 October, so the failures are the check's (session 474's version reads them as held), not the cards'.

    python -m unittest tests.test_session422 -v
"""

import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PACKS = os.path.join(ROOT, "docs", "reviews", "packs")
PUBLIC = os.path.join(ROOT, "site", "public")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_422_REPORT.md")
MARK = "**On a built site (session 422, 21 October 2026).**"

# The headline figures each pack quotes, as the mirror prints them (label prefix, value).
MIRRORS = {
    "battery": ("erw_2026_battery_replication.py", [], [
        ("last twelve months, all streams, USD per kW:", "81.40"),
        ("a bad month: 2024-12, USD for 100 MW:", "475,477"),
        ("debt coverage, last twelve months, times:", "2.63"),
    ]),
    "seller": ("erw_2026_generator_replication.py", [], [
        ("revenue, last twelve months, USD per kW:", "59.85"),
        ("price received, weighted by generation, USD per MWh:", "23.27"),
        ("debt coverage, last twelve months, times:", "0.67"),
    ]),
    "datacenter": ("erw_2026_datacenter_replication.py", [], [
        ("market energy, a flat load, last twelve months, USD per MWh:", "33.73"),
        ("a bad month, nearest rank 4: 2026-08, USD per MWh:", "37.88"),
        ("power per GPU-hour, USD:", "0.0684"),
    ]),
}
PACK_OF = {"battery": "battery", "seller": "generator", "datacenter": "datacenter"}

# check-analysis.mjs's ten failures in the build of 21 October, 15:22 UTC (runs/chain_021/s422/analysis.out)
FAILED = [("batteries_lunch_grids", 1), ("batteries_lunch_grids", 2), ("gas_sets_price", 1), ("impact_study", 1),
          ("peak_hour_grids", 1), ("peak_hour_grids", 2)]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def run_mirror(folder, script, args=()):
    return subprocess.run([sys.executable, script, *args], cwd=os.path.join(PUBLIC, folder),
                          capture_output=True, text=True, timeout=600)


class ThePacks(unittest.TestCase):
    def test_each_pack_has_the_paragraph_inside_its_item_2_section(self):
        for name in ("battery", "generator", "datacenter", "grid", "research"):
            text = read(os.path.join(PACKS, f"{name}.md"))
            self.assertEqual(text.count(MARK), 1, name)
            start = text.index("## Against roadmap item 2")
            nxt = text.index("\n## ", start + 3)
            self.assertTrue(start < text.index(MARK) < nxt, f"{name}: the paragraph is not inside the item 2 section")
            para = text[text.index(MARK):].split("\n")[0]
            self.assertNotIn("—", para)
            self.assertNotIn("–", para)
            self.assertRegex(para, r"exit [01]", name)

    def test_the_packs_quote_the_mirrors_figures(self):
        for folder, (_, _, figures) in MIRRORS.items():
            para = read(os.path.join(PACKS, f"{PACK_OF[folder]}.md"))
            para = para[para.index(MARK):].split("\n")[0]
            for _, value in figures:
                self.assertIn(value, para, f"{folder}: {value}")


class TheMirrors(unittest.TestCase):
    def test_the_three_economics_mirrors_print_the_headlines(self):
        for folder, (script, args, figures) in MIRRORS.items():
            r = run_mirror(folder, script, args)
            self.assertEqual(r.returncode, 0, f"{folder}: {r.stderr[-800:]}")
            lines = r.stdout.splitlines()
            for label, value in figures:
                hits = [l for l in lines if l.startswith(label)]
                self.assertTrue(hits, f"{folder}: no line {label!r}")
                self.assertEqual(hits[0][len(label):].strip(), value, f"{folder}: {label}")

    def test_the_research_mirror_equals_the_cards(self):
        r = run_mirror("findings", "erw_2026_research_replication.py", ["--json", "../../data/findings"])
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        self.assertIn("304 figures compared with the cards' JSON, 0 different", r.stdout)


class TheAnalysisFailures(unittest.TestCase):
    def test_each_failed_callout_names_a_held_grid(self):
        held = re.compile(r"\b(NYISO|ISO-NE)\b")
        for card, i in FAILED:
            with open(os.path.join(ROOT, "site", "data", "findings", f"{card}.json"), encoding="utf-8") as f:
                co = json.load(f)["callouts"][i]
            words = " ".join([co["label"], str(co["before"].get("period", "")), str(co["after"].get("period", ""))])
            self.assertRegex(words, held, f"{card} callout {i}: {words}")


class TheReport(unittest.TestCase):
    def test_no_dash(self):
        if not os.path.exists(REPORT):
            self.skipTest("the report is not written yet")
        text = read(REPORT)
        self.assertNotIn("—", text)
        self.assertNotIn("–", text)


if __name__ == "__main__":
    unittest.main()
