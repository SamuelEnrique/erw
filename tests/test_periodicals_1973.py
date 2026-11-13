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


class Row80TheMarketRowMoved(unittest.TestCase):
    """Row 80: the market row is not a price that did not move; an oil headline that settles names the crude benchmarks."""

    def test_a_zero_move_comes_last(self):
        self.assertEqual(brief.best_price([HH, BRENT, SPP], "story:s")["key"], "Brent crude")
        self.assertEqual(brief.best_price([HH], "story:s")["key"], "Henry Hub natural gas")   # alone, it is still the row

    def test_an_oil_headline_names_brent_and_wti(self):
        t = " oil settles $3 higher on attacks on saudi energy sites, strait of hormuz disruptions  ".lower()
        self.assertTrue(brief.names_price("Brent crude", t))
        self.assertTrue(brief.names_price("WTI Cushing crude", " oil jumps after trump says us doesn't need deal with iran "))
        self.assertFalse(brief.names_price("Henry Hub natural gas", t))
        self.assertFalse(brief.names_price("Brent crude", " saudi oil production surges to one of highest levels in years "))
        frame = pd.DataFrame([{"titles": ["Oil settles $3 higher on attacks on Saudi energy sites"], "why": ""}])
        self.assertTrue(brief.price_named("Brent crude", frame))

    def test_a_named_move_leads_the_row(self):
        named = dict(BRENT, named=True)
        spp_named = dict(SPP)
        self.assertEqual(brief.best_price([HH, spp_named, named], "story:s")["key"], "Brent crude")


class Row81TheCloseSaysItsOwnDay(unittest.TestCase):
    """Row 81: the market row names the close's trading day, not a lag of a week; "1 day", not "1 days"."""

    def test_the_market_row(self):
        op = {"kind": "story", "key": "story:s", "rec": SPACEX}
        lines = brief.numbers_block({"cands": [BRENT]}, op, [], {})
        row = next(ln for ln in lines if ln.startswith("- **Market price.**"))
        self.assertIn("Status: observed, EIA's spot close of the trading day 2026-11-11, the newest EIA had published.", row)
        self.assertNotIn("about a week", row)

    def test_the_fuel_lines(self):
        import inspect
        src = inspect.getsource(brief.numbers_today)
        self.assertNotIn("EIA publishes its closes about a week after the day", src)
        self.assertIn("day{'' if age == 1 else 's'} before this issue", src)


class Row82DispatchedIsNotCapacity(unittest.TestCase):
    """Row 82: a story of power dispatched is not named as capacity."""

    def test_the_row(self):
        r = rec("v", "Recent dispatch of VPP power to grid demonstrates viability of coordinated residential storage at scale",
                sector="storage", parties="Sunrun; Tesla", mw="580", links=[("pv magazine USA", "https://example.org/v")])
        line, detail = brief.story_row("Project or capacity", [r], ("storage",), {"v": "Sunrun and Tesla dispatched more than 580 MW"},
                                       None, "a project figure", ("mw",))
        self.assertIn("Storage dispatched, USA: 580 MW (Sunrun, Tesla; pv magazine USA, 2026-11-11)", line)
        self.assertEqual(detail, "story v (mw)")

    def test_a_capacity_story_keeps_its_noun(self):
        r = rec("b", "Developer files for a 300 MW battery in Arizona", sector="storage", mw="300")
        line, _ = brief.story_row("Project or capacity", [r], ("storage",), {}, None, "a project figure", ("mw",))
        self.assertIn("Storage capacity, USA: 300 MW", line)


if __name__ == "__main__":
    unittest.main()
