"""Session 804: the numbers section says what moved (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 4).

The day-ahead table carries the day before and the change; "What moved most" ranks the five largest moves in percent
among the main hubs' day-ahead averages (against the day before) and EIA's spot closes (against the close before them),
each with a reason only when a scored story of the day names that price; a held grid's price is not ranked (the board's
rule); TTF and JKM say they are not held; the fuel closes say how old they are; US48 demand's peak is set against the same
weekday a year before where the warehouse holds it. The move is the price board's (warehouse/derived/board_page.py stats).
Every figure keeps a key the site's parser and scripts/check_digest.py trace. Fixtures: frames the test writes; erw.fetch is
replaced. No model, no network.
"""

import datetime as dt
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402

DAY = pd.Timestamp("2026-10-20")   # yesterday for a Digest of 2026-10-21


def hours(day, tz, values):
    """24 hourly rows of a local operating day."""
    start = pd.Timestamp(day.date()).tz_localize(tz)
    ts = [start + pd.Timedelta(hours=i) for i in range(24)]
    return pd.DataFrame({"ts_utc": [t.tz_convert("UTC") for t in ts], "value": values, "node": "x", "variable": "dam", "freq": "PT1H"})


def fake_fetch(table, start=None, end=None, node=None, market=None, ba=None, **kw):
    """The tables of a saved day: ERCOT and CAISO move, SPP stays, NYISO and ISO-NE are held, MISO is paused and empty."""
    if table == "iso_dam_hub_prices":
        day = start.tz_convert(None).normalize() if start is not None else DAY
        is_yday = pd.Timestamp(start.date()) == pd.Timestamp(DAY.date())
        if market == "ercot_dam":
            return hours(day, "America/Chicago", [28.38 if is_yday else 26.28] * 24)
        if market == "caiso_dam":
            return hours(day, "America/Los_Angeles", [45.01 if is_yday else 40.81] * 24)
        if market == "spp_dam":
            return hours(day, "America/Chicago", [23.33] * 24)
        return pd.DataFrame(columns=["ts_utc", "value"])
    if table in ("nyiso_dam_zone_prices", "isone_dam_zone_prices"):
        day = start.tz_convert(None).normalize()
        return hours(day, "America/New_York", [49.25] * 24)
    if table == "eia_fuel_spot_prices":
        rows = []
        for ent, vals in (("eia:henry_hub", [("2026-10-13", 3.32), ("2026-10-14", 3.22)]),
                          ("eia:wti_cushing", [("2026-10-13", 99.00), ("2026-10-14", 101.91)]),
                          ("eia:brent", [("2026-10-13", 120.00), ("2026-10-14", 126.55)])):
            for d, v in vals:
                rows.append({"entity": ent, "ts_utc": pd.Timestamp(d, tz="UTC"), "value": v, "unit": "USD/MMBtu" if "henry" in ent else "USD/bbl"})
        return pd.DataFrame(rows)
    if table == "eia930_all_demand":
        d0 = start
        if d0.year == 2026:
            vals = [600000 + 1000 * i for i in range(24)]
        else:
            vals = [590000 + 500 * i for i in range(24)]
        ts = [d0 + pd.Timedelta(hours=i) for i in range(24)]
        return pd.DataFrame({"ts_utc": ts, "value": vals, "variable": "demand_mw", "entity": "eia930:US48"})
    raise brief.erw.ERWDataNotFound(table)


def quiet(_):
    pass


class Section(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "license_status.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("table,status,from,publishers,verdict,permission,permission_ref,note\n"
                        "nyiso_dam_zone_prices,license needed,2026-10-21,NYISO,needs written permission,,,n\n"
                        "isone_dam_zone_prices,license needed,2026-10-21,ISO-NE,needs written permission,,,n\n"
                        "iso_dam_hub_prices,license needed,2026-10-21,MISO,needs written permission,,,n\n")
            held = brief.held_grids(p)
        clusters = pd.DataFrame([{"cluster_id": "c1", "titles": ["Brent crude trades at $110.30 per barrel as Middle East supply worries persist"],
                                  "sector": "oil", "parties": "", "sig": 7, "ai": 0, "why": "Geopolitical supply risk drives crude prices higher.",
                                  "mw": "", "price": "", "links": [("OilPrice.com", "https://oilprice.com/x")], "summary": "", "n": 1}])
        with mock.patch.object(brief.erw, "fetch", side_effect=fake_fetch), mock.patch.object(brief, "held_grids", return_value=held), \
                mock.patch.object(brief, "rt_parts", return_value=[]), mock.patch.object(brief, "cite_short", side_effect=lambda t: f"`{t}`"), \
                mock.patch.object(brief, "paused_row", side_effect=lambda label: {"paused_on": "2026-10-04", "reason": "terms"} if label == "MISO" else None), \
                mock.patch.object(brief, "licensed_outlets", return_value=set()):
            cls.lines = brief.numbers_today("2026-10-21", quiet, clusters)
        cls.text = "\n".join(cls.lines)

    def movers(self):
        i = next(k for k, ln in enumerate(self.lines) if ln.startswith("**What moved most**"))
        return [ln for ln in self.lines[i + 1:] if ln.startswith("- ")][:6]

    def test_the_five_largest_moves_in_percent_lead(self):
        m = self.movers()
        labels = [re.match(r"- (.+?): ", ln).group(1) for ln in m if not ln.startswith("- Not ranked")]
        self.assertEqual(labels, ["CAISO TH_SP15_GEN-APND day-ahead", "ERCOT HB_NORTH day-ahead", "Brent crude", "Henry Hub natural gas", "WTI Cushing crude"])
        self.assertIn("- CAISO TH_SP15_GEN-APND day-ahead: 45.01 USD/MWh on 2026-10-20, up 4.20 USD/MWh (10.3%) from 40.81 USD/MWh on 2026-10-19 [", m[0])
        self.assertIn("- Henry Hub natural gas: 3.22 USD/MMBtu on 2026-10-14, down 0.10 USD/MMBtu (3.0%) from 3.32 USD/MMBtu on 2026-10-13 [", m[3])

    def test_spp_with_no_move_is_not_among_them(self):
        self.assertNotIn("SPP SPPSOUTH_HUB day-ahead:", self.text)

    def test_a_reason_only_when_a_story_names_the_price(self):
        brent = next(ln for ln in self.movers() if ln.startswith("- Brent"))
        self.assertIn("Reason, from the day's stories: Geopolitical supply risk drives crude prices higher. ([OilPrice.com](https://oilprice.com/x))", brent)
        wti = next(ln for ln in self.movers() if ln.startswith("- WTI"))
        self.assertNotIn("Reason", wti)

    def test_held_paused_and_not_held_prices_are_not_ranked_and_say_so(self):
        nr = next(ln for ln in self.movers() if ln.startswith("- Not ranked"))
        self.assertIn("NYISO N.Y.C. (licensed source needed)", nr)
        self.assertIn("ISO-NE .H.INTERNAL_HUB (licensed source needed)", nr)
        self.assertIn("MISO INDIANA.HUB (paused by the ERW since 2026-10-04)", nr)
        self.assertIn("TTF, the Dutch gas benchmark", nr)
        self.assertIn("JKM, the Japan-Korea LNG marker", nr)
        self.assertNotIn("NYISO N.Y.C. day-ahead:", self.text)

    def test_the_table_carries_the_day_before_and_the_change(self):
        row = next(ln for ln in self.lines if ln.startswith("| ERCOT |"))
        self.assertEqual(row, "| ERCOT | HB_NORTH | 2026-10-20 | 28.38 | [1] | 26.28 | +2.10 (+8.0%) |")
        miso = next(ln for ln in self.lines if ln.startswith("| MISO |"))
        self.assertIn("not requested: paused by the ERW since 2026-10-04", miso)
        self.assertRegex(miso, r"\| +\| not computed \|$")
        self.assertIn("| ISO | Hub or zone | Operating day | Average USD/MWh | Table | Day before USD/MWh | Change |", self.lines)

    def test_the_fuel_closes_say_their_age(self):
        hh = next(ln for ln in self.lines if ln.startswith("- Henry Hub natural gas: 3.22 USD/MMBtu on 2026-10-14 ["))
        self.assertIn("EIA's newest close when this was written (7 days before this issue)", hh)

    def test_us48_demand_against_the_same_weekday_a_year_before(self):
        d = next(ln for ln in self.lines if ln.startswith("**US48 demand, yesterday:**"))
        self.assertIn("peaked at 623,000 MW in the hour starting 2026-10-20 23:00 UTC [", d)
        self.assertIn("the same weekday a year before (2025-10-21) peaked at 601,500 MW in the hour starting 2025-10-21 23:00 UTC [", d)
        self.assertIn("so +3.6% on the year.", d)
        self.assertEqual(dt.date(2025, 10, 21).weekday(), dt.date(2026, 10, 20).weekday())

    def test_every_figure_line_keeps_the_parser_s_form(self):
        mover = re.compile(r"^- (.+?): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2}), (?:up|down) [\d,.]+ \S+ \([\d.]+%\) from (-?[\d,]+\.\d{2}) \S+ on (\d{4}-\d{2}-\d{2}) \[(\d+)\]")
        self.assertEqual(sum(1 for ln in self.lines if mover.match(ln)), 5)
        fuel = re.compile(r"^- (.+?): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2})\b")
        self.assertEqual(sum(1 for ln in self.lines if fuel.match(ln) and not mover.match(ln)), 3)
        demand = re.compile(r"peaked at (-?[\d,]+) MW in the hour starting (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC")
        self.assertEqual(len(demand.findall(self.text)), 2)

    def test_no_dash(self):
        self.assertNotIn(chr(0x2014), self.text)
        self.assertNotIn(chr(0x2013), self.text)


class TheMove(unittest.TestCase):
    def test_the_move_is_the_board_s(self):
        got = brief.day_move(28.38, "2026-10-20", 26.28, "2026-10-19")
        self.assertEqual(got, {"ch": 2.1, "pct": 7.99})
        try:
            sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
            import board_page
        except Exception:
            self.skipTest("board_page does not import here")
        m = board_page.stats({dt.date(2026, 10, 19): 26.28, dt.date(2026, 10, 20): 28.38})["moves"]["d"]
        self.assertEqual({"ch": m["ch"], "pct": m["pct"]}, got)

    def test_a_base_of_zero_has_no_percent(self):
        self.assertIsNone(brief.day_move(1.0, "2026-10-20", 0.0, "2026-10-19")["pct"])


class TheHeldGrids(unittest.TestCase):
    def test_the_repository_s_file(self):
        got = brief.held_grids()
        self.assertTrue(got <= {"NYISO", "ISO-NE", "MISO", "ERCOT", "CAISO", "SPP"})
        if got:
            self.assertIn("NYISO", got)

    def test_without_the_file(self):
        self.assertEqual(brief.held_grids(os.path.join(tempfile.gettempdir(), "no-such-file.csv")), set())


class TheReason(unittest.TestCase):
    def test_a_story_that_names_ercot(self):
        c = pd.DataFrame([{"cluster_id": "a", "titles": ["ERCOT prices spike as heat lingers"], "sector": "power_prices", "parties": "ERCOT",
                           "sig": 8, "ai": 0, "why": "Major scarcity pricing lifts Texas power costs.", "mw": "", "price": "",
                           "links": [("Reuters", "https://news.google.com/rss/articles/x")], "summary": "", "n": 1}])
        with mock.patch.object(brief, "licensed_outlets", return_value=set()):
            r = brief.price_reason("ERCOT", c)
        self.assertEqual(r, " Reason, from the day's stories: Scarcity pricing lifts Texas power costs. ([Reuters](https://news.google.com/rss/articles/x) (via Google News))")
        self.assertEqual(brief.price_reason("CAISO", c), "")
        self.assertEqual(brief.price_reason("ERCOT", None), "")


if __name__ == "__main__":
    unittest.main()
