"""Session 474: the landing checks that failed on production, put right where the fault was the check's.

check-analysis.mjs expected every finding card's callout to print its number; from 21 October 2026 a callout whose words
name a grid held under its publisher's terms is drawn as "license needed" (components/Num.tsx, lib/license.ts), so the
check now expects the words there, read with the card's own rule. check-findings-grids.mjs waited for a canvas that no
page draws since sessions 317 and 318 moved the cards' charts to the shared SVG set; it now waits for the drawing's SVG
and counts the small multiples as panels. These tests read the scripts and the files they read; the checks themselves
run against a site (the session's report gives their exits on production)."""

import glob
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
ANALYSIS = os.path.join(SITE, "scripts", "check-analysis.mjs")
GRIDS = os.path.join(SITE, "scripts", "check-findings-grids.mjs")
CARD = os.path.join(SITE, "components", "analysis", "FindingCard.tsx")
STATUS = os.path.join(SITE, "data", "license_status.json")
FINDINGS = os.path.join(SITE, "data", "findings")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_474_REPORT.md")

GRID_PREFIX = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "PJM": "pjm", "SPP": "spp", "CAISO": "caiso", "ERCOT": "ercot"}
GRID_WORD = [(r"\bERCOT\b", "ercot"), (r"\bCAISO\b", "caiso"), (r"\bPJM\b", "pjm"), (r"\bMISO\b", "miso"), (r"\bSPP\b", "spp"),
             (r"\bNYISO\b", "nyiso"), (r"\bISO-NE\b", "isone")]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def held_grids(day):
    status = json.loads(read(STATUS))
    out = set()
    for r in status["tables"].values():
        if r["status"] == "license needed" and day >= r["from"]:
            out.update(GRID_PREFIX[p] for p in r["publishers"] if p in GRID_PREFIX)
    return out


def grid_of_words(s):
    for pat, g in GRID_WORD:
        if re.search(pat, s, re.I):
            return g
    return "-"


class Analysis(unittest.TestCase):
    def test_the_check_reads_the_grid_as_the_card_does(self):
        # the same seven words, in the same order, as components/analysis/FindingCard.tsx
        card = re.search(r"const GRID_WORD[^=]*= (\[.*\]);", read(CARD)).group(1)
        check = re.search(r"const GRID_WORD = (\[.*\]);", read(ANALYSIS)).group(1)
        self.assertEqual(card, check)

    def test_the_check_reads_the_holds_as_lib_license_does(self):
        s = read(ANALYSIS)
        self.assertIn('path.join(here, "..", "data", "license_status.json")', s)
        self.assertIn('r.status === "license needed" && day >= r.from', s)
        self.assertIn('data-license-held="finding ${c.card_id}"', s)
        self.assertIn('"license needed"', s)

    def test_on_21_october_ten_callout_figures_are_held(self):
        # the ten figures check-analysis failed on production at 10:27 UTC on 21 October: NYISO's and ISO-NE's
        day = "2026-10-21"
        held = held_grids(day)
        self.assertEqual(held, {"isone", "miso", "nyiso"})
        n = 0
        for f in sorted(glob.glob(os.path.join(FINDINGS, "*.json"))):
            if f.endswith("catalogue.json"):
                continue
            c = json.loads(read(f))
            for co in c.get("callouts", []):
                for side in ("before", "after"):
                    if grid_of_words(f"{co[side]['period']} {co['label']}") in held:
                        n += 1
        self.assertEqual(n, 10)

    def test_before_the_day_nothing_is_held(self):
        self.assertEqual(held_grids("2026-10-20"), set())


class FindingsGrids(unittest.TestCase):
    def test_no_wait_for_a_canvas(self):
        body = read(GRIDS).split('import { withBrowser } from "./browser.mjs";', 1)[1]
        self.assertNotIn("canvas", body)

    def test_the_multiples_are_counted_as_panels(self):
        s = read(GRIDS)
        self.assertIn('[data-finding-chart=\\\\"multiples\\\\"] [data-panel] svg', s)
        self.assertIn("c.chart.panels.length", s)

    def test_every_drawing_is_waited_for_as_svg(self):
        s = read(GRIDS)
        for frag in ("[data-multi-grid=\"${p.grid}\"] svg", "[data-multi-grid=\\\\\"ercot\\\\\"] svg",
                     "[data-card=\"${id}\"] [data-finding-chart] svg", "[data-render=\\\\\"1\\\\\"] [data-finding-chart] svg"):
            self.assertIn(frag, s, frag)


class Words(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for p in (ANALYSIS, GRIDS, __file__) + ((REPORT,) if os.path.exists(REPORT) else ()):
            s = read(p)
            self.assertNotIn(chr(0x2014), s, p)
            self.assertNotIn(chr(0x2013), s, p)


if __name__ == "__main__":
    unittest.main()
