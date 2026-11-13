"""Session 1896: the Roundup's faults of W45 in docs/reviews/periodicals-faults-2026-11-05.md, rows 74 and 75, proved on
fixtures. No model call, no network, no warehouse table read: every frame is written here (the real storage_daily_cycle
and eia930_all_storage are the data machine's; the source line is fed small frames of the same columns and header notes).

Row 74, the line: "Source: Energy Research Warehouse (ERW), derived, Energy Research Warehouse (ERW), derived from
California ISO via the Energy Research Warehouse (ERW), table storage_daily_cycle; data retrieved to 2026-11-05."
The fault: "The ERW named three times, and California ISO named as the source of a Lower 48 series: the template reads
entity `eia930:US48` (from `eia930_all_storage`, EIA-930); the CAISO rows are the table's other source. `source_line`
lists every publisher of the table, not of the series charted."
The fix: "Source: EIA-930, hourly battery net generation, Lower 48, via the ERW's derived table storage_daily_cycle; data
retrieved to 2026-11-05." The Roundup's caller (roundup.chart_source_line) names the publisher of the charted entity's
rows, through the table its header says it is built from when those rows are the ERW's own, and the ERW once.

Row 75, the line: "The week's stories point to US crude oil exports, whose chart is on [/research](/research) (template
`watch_crude_exports`)."
The fault: "Row 35, re-seen: the pointer is a token match (oil, crude; no story of the week names exports), and it gives
the reader no figure though the record holds one (3,675 kbbl/d in the week to 2026-11-01, down 1,179 from 4,854)."
The fix: "The sentence only when a story names the measure (the Digest's fault 14 rule), then with its figure: \"US crude
exports fell to 3,675 kbbl/d in the week to 2026-11-01, from 4,854; the chart is on /research.\" Else no sentence."
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import roundup  # noqa: E402

EM, EN = chr(0x2014), chr(0x2013)
OLD_LINE = ("Source: Energy Research Warehouse (ERW), derived, Energy Research Warehouse (ERW), derived from California ISO via "
            "the Energy Research Warehouse (ERW), table storage_daily_cycle; data retrieved to 2026-11-05.")
NEW_LINE = ("Source: EIA-930, Hourly Electric Grid Monitor, hourly net generation by energy source, via the ERW's derived table "
            "storage_daily_cycle; data retrieved to 2026-11-05.")


def quiet(*_a, **_k):
    pass


def frame(rows, notes=()):
    df = pd.DataFrame(rows, columns=["entity", "variable", "value", "source"])
    df.attrs["erw"] = {"notes": list(notes)}
    return df


CYCLE = frame([("eia930:US48", "mwh_discharged", 47682.0, "erw:storage_daily_cycle"),
               ("eia930:ERCO", "mwh_discharged", 9000.0, "erw:storage_daily_cycle"),
               ("caiso:ISO", "mwh_discharged", 12000.0, "erw:storage_daily_cycle_caiso")],
              notes=["Derived from: eia930_all_storage; caiso_battery_storage", "Variables: mwh_discharged, mwh_charged"])
EIA930 = frame([("eia930:US48", "net_generation_battery_mw", 2100.0, "eia:electricity/rto/fuel-type-data")])
CAISO = frame([("caiso:ISO", "batteries_mw", 1500.0, "caiso:todays_outlook")])
FUEL = frame([("eia:wti_cushing", "spot_price", 99.6, "eia:pet/pri/spt"), ("eia:henry_hub", "spot_price", 3.1, "eia:ng/pri/fut")])
TABLES = {"storage_daily_cycle": CYCLE, "eia930_all_storage": EIA930, "caiso_battery_storage": CAISO, "eia_fuel_spot_prices": FUEL}
REPORTS = {
    "storage_daily_cycle": [
        {"source": "erw:storage_daily_cycle", "publisher": "Energy Research Warehouse (ERW), derived",
         "report": "Battery storage daily cycle (docs/methods/storage.md)"},
        {"source": "erw:storage_daily_cycle_caiso", "publisher": "Energy Research Warehouse (ERW), derived from California ISO",
         "report": "Battery storage daily cycle, CAISO rows, from CAISO Today's Outlook (caiso_battery_storage; docs/methods/storage.md)"}],
    "eia930_all_storage": [{"source": "eia:electricity/rto/fuel-type-data", "publisher": "U.S. Energy Information Administration (EIA)",
                            "report": "Form EIA-930, Hourly Electric Grid Monitor: hourly net generation by energy source"}],
    "caiso_battery_storage": [{"source": "caiso:todays_outlook", "publisher": "California ISO (CAISO)", "report": "Today's Outlook, batteries"}],
    "eia_fuel_spot_prices": [{"source": "eia:pet/pri/spt", "publisher": "U.S. Energy Information Administration (EIA)",
                              "report": "Spot Prices for Crude Oil and Petroleum Products"},
                             {"source": "eia:ng/pri/fut", "publisher": "U.S. Energy Information Administration (EIA)",
                              "report": "Natural Gas Spot and Futures Prices (NYMEX)"}],
}


def fetch(name, **_k):
    if name not in TABLES:
        raise FileNotFoundError(name)
    return TABLES[name]


def sources(name):
    return {"table": name, "reports": REPORTS[name]}


W45 = {"template": "watch_battery_discharge_us", "title": "Batteries discharging, Lower 48", "source_line": OLD_LINE}


EXPORTS = {"template": "watch_crude_exports", "title": "US crude oil exports", "score": 82.7,
           "finding": "US crude oil exports: 3,675 kbbl/d in the week of 2026-10-26 to 2026-11-01, down 1,179 from 4,854 the week before. "
                      "Of the 104 week-to-week moves before it, 18 were as large."}
CHART75 = {"week": "2026-W45", "template": "watch_battery_discharge_us", "title": "Batteries discharging, Lower 48",
           "finding": "Lower 48 battery discharge, daily mean of the week: 47,682.14 MWh a day in the week of 2026-10-26 to 2026-11-01.",
           "note": "The chart shows it.", "source_line": OLD_LINE, "files": {"email": "chart_email.png"}, "headline": {},
           "also_moved": [EXPORTS]}


def story(title, sector="oil", why=""):
    return {"titles": [title], "sector": sector, "why": why, "parties": ""}


# W45's top stories as the issue printed them: oil and crude, none names exports
W45_STORIES = [story("ConocoPhillips raises its dividend after profit beats estimates on higher oil prices"),
               story("Brent crude falls as Middle East supply fears ease"),
               story("EQT's Zelestra unveils a USD 12 billion plan to meet US AI demand", "deal"),
               story("Worley signs reimbursable EPC contract for Venture Global's CP2 LNG expansion in Louisiana", "deal")]
POINTER = "The week's stories point to US crude oil exports, whose chart is on [/research](/research) (template `watch_crude_exports`)"


def section(stories):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "2026-W45"))
        with open(os.path.join(d, "2026-W45", "chart_of_the_week.json"), "w", encoding="utf-8") as f:
            json.dump(CHART75, f)
        with mock.patch.object(roundup, "ANALYSIS_DIR", d), mock.patch.object(roundup, "chart_source_line", lambda m, log: OLD_LINE), \
                mock.patch.dict(sys.modules, {"roundup_pick": mock.Mock(chosen=lambda *a: None)}):
            return "\n".join(roundup.chart_of_the_week("2026-W45", quiet, stories=stories))


class Row75ThePointer(unittest.TestCase):
    def test_w45_no_story_names_exports_no_sentence(self):
        best, same = roundup.chart_relevance(CHART75, W45_STORIES, quiet)
        self.assertEqual((best["template"], same), ("watch_crude_exports", False))   # the token match still ranks it
        self.assertIsNone(roundup.measure_named(EXPORTS, W45_STORIES))
        text = section(W45_STORIES)
        self.assertNotIn("point to", text)
        self.assertNotIn("watch_crude_exports", text)

    def test_a_story_naming_exports_gets_the_sentence_with_its_figure(self):
        stories = W45_STORIES + [story("OPEC cuts as US crude exports hit a record")]
        self.assertEqual(roundup.measure_named(EXPORTS, stories), "OPEC cuts as US crude exports hit a record")
        text = section(stories)
        self.assertIn(POINTER + ": 3,675 kbbl/d in the week of 2026-10-26 to 2026-11-01, down 1,179 from 4,854 the week before.", text)
        self.assertNotIn("Of the 104", text)

    def test_exports_alone_or_of_another_commodity_do_not_name_it(self):
        self.assertIsNone(roundup.measure_named(EXPORTS, [story("Japan's car exports climb")]))
        self.assertIsNone(roundup.measure_named(EXPORTS, [story("Crude oil stocks rise")]))
        self.assertEqual(roundup.measure_named(EXPORTS, [story("Gulf terminals ship more oil", why="Crude export volumes set a record.")]),
                         "Gulf terminals ship more oil")

    def test_a_price_series_of_the_commodity_named(self):
        wti = {"title": "WTI crude oil", "finding": "WTI spot price at Cushing, weekly mean: 99.64 USD/bbl in the week of 2026-10-26 to 2026-11-01."}
        self.assertTrue(roundup.measure_named(wti, [story("Oil prices rise on Middle East fears")]))
        self.assertIsNone(roundup.measure_named(wti, [story("Henry Hub gas prices slip")]))
        self.assertIsNone(roundup.measure_named(wti, [story("Oil majors report profits")]))

    def test_plural_and_place_words(self):
        bat = {"title": "Batteries discharging, Lower 48", "finding": "Lower 48 battery discharge, daily mean of the week: 47,682 MWh a day."}
        self.assertTrue(roundup.measure_named(bat, [story("Battery discharge sets a record on the Texas grid", "storage")]))
        self.assertIsNone(roundup.measure_named(bat, [story("Lower 48 gas demand rises", "gas")]))

    def test_no_quantity_known_names_nothing(self):
        self.assertIsNone(roundup.measure_named({"title": "Something else", "finding": "A thing: 3 in 2026."}, [story("Something else happens")]))

    def test_the_figure_from_the_record(self):
        self.assertEqual(roundup.measure_figure(EXPORTS), "3,675 kbbl/d in the week of 2026-10-26 to 2026-11-01, down 1,179 from 4,854 the week before")
        self.assertEqual(roundup.measure_figure({"finding": "ERCOT operating battery storage: 19,194.6 MW in September 2026, up 990.1 from "
                                                            "18,204.5 in August 2026. Of the 36 month-to-month moves before it, 3 were as large."}),
                         "19,195 MW in September 2026, up 990 from 18,205 in August 2026")
        self.assertEqual(roundup.measure_figure({"finding": "no figure"}), "")


class Row74TheSourceLine(unittest.TestCase):
    def test_the_charted_series_publisher_and_the_erw_once(self):
        got = roundup.chart_source_line(W45, quiet, fetch=fetch, sources=sources)
        self.assertEqual(got, NEW_LINE)
        self.assertNotIn("California", got)
        self.assertEqual(got.count("ERW"), 1)

    def test_a_caiso_series_of_the_same_table_names_caiso(self):
        spec = {"name": "t", "table": "storage_daily_cycle", "entity": "caiso:ISO", "variable": "mwh_discharged"}
        with mock.patch.object(roundup, "watch_spec", lambda t: spec):
            got = roundup.chart_source_line(dict(W45, template="t"), quiet, fetch=fetch, sources=sources)
        self.assertEqual(got, "Source: CAISO, Today's Outlook, batteries, via the ERW's derived table storage_daily_cycle; data "
                              "retrieved to 2026-11-05.")

    def test_a_source_table_names_the_series_report_only(self):
        m = {"template": "watch_wti", "source_line": "Source: EIA via the Energy Research Warehouse (ERW), table eia_fuel_spot_prices; "
                                                      "data retrieved to 2026-11-01."}
        got = roundup.chart_source_line(m, quiet, fetch=fetch, sources=sources)
        self.assertEqual(got, "Source: EIA, Spot Prices for Crude Oil and Petroleum Products, via the Energy Research Warehouse (ERW), "
                              "table eia_fuel_spot_prices; data retrieved to 2026-11-01.")
        self.assertNotIn("Natural Gas", got)

    def test_nothing_found_keeps_the_stored_line(self):
        def none(name, **_k):
            raise RuntimeError("not on this machine")
        self.assertEqual(roundup.chart_source_line(W45, quiet, fetch=none, sources=sources), OLD_LINE)
        self.assertEqual(roundup.chart_source_line(dict(W45, template="hunt_x"), quiet, fetch=fetch, sources=sources), OLD_LINE)

    def test_the_section_prints_it(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "2026-W45"))
            with open(os.path.join(d, "2026-W45", "chart_of_the_week.json"), "w", encoding="utf-8") as f:
                json.dump(dict(W45, files={"email": "chart_email.png"}, note="The chart shows it.", headline={}), f)
            with mock.patch.object(roundup, "ANALYSIS_DIR", d), mock.patch.object(roundup.erw, "fetch", fetch), \
                    mock.patch.object(roundup.erw, "sources", sources), \
                    mock.patch.dict(sys.modules, {"roundup_pick": mock.Mock(chosen=lambda *a: None)}):
                text = "\n".join(roundup.chart_of_the_week("2026-W45", quiet))
        self.assertIn(NEW_LINE + " Template `watch_battery_discharge_us`", text)
        self.assertNotIn("derived from California ISO", text)

    def test_no_dash(self):
        src = open(__file__, encoding="utf-8").read() + open(roundup.__file__, encoding="utf-8").read()
        self.assertNotIn(EM, src)
        self.assertNotIn(EN, src)


if __name__ == "__main__":
    unittest.main()
