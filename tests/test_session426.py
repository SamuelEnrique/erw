"""Session 426: the datacenter cost tool's cross-check table (docs/methods/datacenter_cost.md, its last section).

Energy Research Warehouse (ERW). No network, no model. Checks the section session 426 added: the note before it is
unchanged against the branch's base; no em or en dash; every row of the table in six cells, with a key, a source link
and a page; every figure of the page's side equal to the tariff's own figure converted as the page converts it (a
charge per 4CP kW a month, times 12 times 1,000, over 8,760 hours, for a flat load), and every published figure and
gap equal to a recomputation from the page's own file (site/data/datacenter/texas_delivery.json); and the keys named
as site/scripts/check-values.mjs reads them (dcd|<MW>|<utility>:<component>).

    python -m unittest tests.test_session426 -v
"""

import json
import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOTE = os.path.join(ROOT, "docs", "methods", "datacenter_cost.md")
FILE = os.path.join(ROOT, "site", "data", "datacenter", "texas_delivery.json")
HEAD = "## Cross-checks of the tool's defaults (session 426)"
BASE = "origin/wip/461-combined"
SLUGS = {"Oncor": "oncor", "CenterPoint Energy Houston Electric": "centerpoint_energy_houston_electric",
         "AEP Texas": "aep_texas", "Texas-New Mexico Power": "texas_new_mexico_power"}


def note():
    with open(NOTE, encoding="utf-8") as f:
        return f.read()


def section():
    s = note()
    return s[s.index(HEAD):]


def rows():
    """The table's rows as lists of cells, the escaped pipes of the key cells kept inside their cell."""
    out = []
    for line in section().splitlines():
        if line.startswith("| ") and not line.startswith("| The page's figure") and not line.startswith("|---"):
            out.append([c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]])
    return out


def delivery():
    with open(FILE, encoding="utf-8") as f:
        return json.load(f)


def per_mwh(v):
    return round(v * 12 * 1000 / 8760, 2)


class TheSection(unittest.TestCase):
    def test_no_dash(self):
        self.assertNotIn("—", section())
        self.assertNotIn("–", section())

    def test_the_note_before_it_is_unchanged(self):
        try:
            base = subprocess.run(["git", "show", f"{BASE}:docs/methods/datacenter_cost.md"], cwd=ROOT,
                                  capture_output=True, text=True, encoding="utf-8").stdout
        except OSError:
            self.skipTest("git not available")
        if not base:
            self.skipTest(f"{BASE} not fetched")
        before = note()[:note().index(HEAD)].rstrip()
        self.assertEqual(before.replace("\r\n", "\n"), base.rstrip().replace("\r\n", "\n"))

    def test_eight_rows_each_with_a_key_a_link_and_a_page(self):
        rs = rows()
        self.assertEqual(len(rs), 8)
        for i, r in enumerate(rs):
            self.assertEqual(len(r), 6, r)
            self.assertRegex(r[1], r"^`dcd\|100\|[a-z_]+:transmission`$")
            if i < 5:   # the rows after the first against the Commission's rate cite the same source as "the same"
                self.assertIn("](https://", r[3])
                self.assertRegex(r[3], r"page \d+")
            else:
                self.assertEqual(r[3], "the same")
            self.assertGreaterEqual(len(r[5]), 8)

    def test_each_key_is_the_utility_the_row_names(self):
        for r in rows():
            utility = r[0].split(", transmission")[0]
            self.assertIn(utility, SLUGS)
            self.assertEqual(r[1], f"`dcd|100|{SLUGS[utility]}:transmission`")


class TheFigures(unittest.TestCase):
    """Each figure against the page's own file: the tariff's factor converted, the Commission's rate converted."""

    def setUp(self):
        if not os.path.exists(FILE):
            self.skipTest("the page's delivery file is not here")
        d = delivery()
        self.factor = {r["utility"]: r for r in d["rows"] if r["kind"] == "transmission" and r["value"] > 0}
        self.rate = [m for m in d["matrix"] if m["quantity"] == "postage_stamp_rate" and m["scope"] == "ERCOT"][0]

    def test_the_four_factors(self):
        self.assertEqual(set(self.factor), set(SLUGS))

    def test_ours_is_the_factor_converted(self):
        for r in rows():
            utility = r[0].split(", transmission")[0]
            ours = float(re.search(r"USD ([\d.]+) per MWh", r[0]).group(1))
            self.assertEqual(ours, per_mwh(self.factor[utility]["value"]), utility)

    def test_the_first_four_rows_quote_the_tariff_and_its_page(self):
        for r in rows()[:4]:
            utility = r[0].split(", transmission")[0]
            f = self.factor[utility]
            self.assertIn(f"USD {f['value']}", r[2])
            self.assertIn(f"page {f['page']}", r[3])
            self.assertIn(f["url"], r[3])
            self.assertEqual(r[4], "0.00")

    def test_the_last_four_rows_against_the_commissions_rate(self):
        flat = round(self.rate["value"] * 1000 / 8760, 2)
        self.assertEqual(flat, 7.83)
        for r in rows()[4:]:
            utility = r[0].split(", transmission")[0]
            self.assertIn(f"{flat:.2f} per MWh", r[2])
            gap = round(per_mwh(self.factor[utility]["value"]) - flat, 2)
            self.assertEqual(float(r[4]), gap, utility)
        self.assertIn("68.547301", section())
        self.assertIn(f"attachment page {self.rate['page']}, page {self.rate['scan_page']} of the filed scan", section())

    def test_no_request_was_counted(self):
        self.assertIn("No publisher was asked for anything by this session", section())


if __name__ == "__main__":
    unittest.main()
