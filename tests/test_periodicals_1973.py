"""Chain 228 (sessions 1973 to 1999, 13 November 2026): the faults of the Digest of 12 November 2026 and the Roundups of W45
and W46, read as a reader (docs/reviews/periodicals-faults-2026-11-05.md, rows 79 onward). One class a row, on fixtures:
no model, no network."""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), os.path.join("warehouse", "analysis", "findings"), "scripts"):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402


def cand(label, key, v, pv, pct, table="eia_fuel_spot_prices", unit="USD/MMBtu", reason="", node=""):
    return dict(label=label, key=key, unit=unit, v=v, pv=pv, d=pd.Timestamp("2026-11-11"), pd=pd.Timestamp("2026-11-10"),
                ch=round(v - pv, 4), pct=pct, table=table, reason=reason, node=node, ref="[1]")


def rec(cid, title, sector="datacenter_power", parties="", mw="", price="", why="", links=None, first="2026-11-11T12:00:00Z"):
    return {"cluster_id": cid, "titles": [title], "sector": sector, "parties": parties, "mw": mw, "price": price, "why": why,
            "links": links or [("Bloomberg.com", "https://example.org/a")], "first": first, "region": "USA"}


# 12 November 2026's candidates as the dry run of session 1973 read them (runs/periodicals_dryrun/s1973/)
SPP = cand("SPP SPPSOUTH_HUB day-ahead", "SPP", 20.68, 33.98, -39.14, table="iso_dam_hub_prices", unit="USD/MWh", node="SPPSOUTH_HUB")
HH = cand("Henry Hub natural gas", "Henry Hub natural gas", 3.00, 3.00, 0.0)
BRENT = cand("Brent crude", "Brent crude", 92.14, 90.16, 2.2, unit="USD/bbl")
SPACEX = rec("s", "SpaceX plans USD 74 billion in data center projects in Arizona and Texas", price="$74 billion")


class Row79TheOpeningDoesNotDenyAMove(unittest.TestCase):
    """Row 79: a story's figure leads past a single hub's unnamed move; the opening names that move."""

    def test_the_passed_move_is_named(self):
        op = brief.opening_number([SPP, HH, BRENT], [SPACEX])
        self.assertEqual(op["kind"], "story")
        self.assertEqual(op["passed"]["key"], "SPP")
        line = brief.opening_lines(op, {})[2]
        self.assertNotIn("No price moved enough to lead", line)
        self.assertIn("The day's largest move, SPP SPPSOUTH_HUB day-ahead down 39.1%, is one hub's and no story names it", line)
        self.assertIn("not a warehouse table's", line)

    def test_no_move_past_a_bar_keeps_the_old_sentence(self):
        small = dict(SPP, pct=-4.0, ch=-1.0)
        op = brief.opening_number([small, HH], [SPACEX])
        self.assertIsNone(op["passed"])
        self.assertIn("No price moved enough to lead; this is a reported figure", brief.opening_lines(op, {})[2])

    def test_the_hub_still_leads_when_no_story_states_a_figure(self):
        op = brief.opening_number([SPP, HH], [rec("t", "A story with no figure")])
        self.assertEqual((op["kind"], op["cand"]["key"]), ("mover", "SPP"))


if __name__ == "__main__":
    unittest.main()
