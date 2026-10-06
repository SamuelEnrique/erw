"""Session 134: Supply and trade (/supply, in review).

Energy Research Warehouse (ERW). The two connectors the session added (EIA's gas storage, petroleum supply, gas trade
and regional production; the CFTC's managed money positions), the release schedule, and the page's builder
(warehouse/derived/supply_page.py), on real samples saved under tests/fixtures/session134/: rows of EIA's and the CFTC's
own answers as received on 6 October 2026, EIA's two schedule pages, and two series as the warehouse held them (gas in
storage in the Lower 48 by week, pipeline exports to Mexico by month). Where a test removes or changes a real value it
says so: it tests the arithmetic and writes nothing.
"""
import datetime as dt
import json
import os
import re
import sys
import unittest
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import cftc_cot  # noqa: E402
import eia_supply as es  # noqa: E402
import release_schedule as rs  # noqa: E402
import supply_page as sp  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session134")
SITE = os.path.join(ROOT, "site")
D = dt.date
STAMP = ("https://example.invalid/the-address-without-a-key", "2026-10-06T10:44:00Z")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def eia_rows(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        rows = json.load(f)["response"]["data"]
    for r in rows:
        r["_url"], r["_retrieved"] = STAMP
    return rows


def held(name):
    x = pd.read_csv(os.path.join(FIX, name), comment="#")
    return {D.fromisoformat(t[:10]): float(v) for t, v in zip(x["ts_utc"], x["value"])}


def part(table, i=0):
    return es.TABLES[table]["parts"][i]


class EiaConnector(unittest.TestCase):
    def test_gas_storage_rows_are_eia_values_unchanged(self):
        rows = eia_rows("eia_gas_storage_sample.json")
        out, empty, forecast = es.shape(part("eia_gas_storage_weekly"), rows, "weekly")
        self.assertEqual((len(out), empty, forecast), (len(rows), 0, 0))
        raw = next(r for r in rows if r["series"] == "NW2_EPG0_SWO_R48_BCF" and r["period"] == "2026-09-25")
        got = next(r for r in out if r["entity"] == "eia:NW2_EPG0_SWO_R48_BCF" and r["ts_utc"] == "2026-09-25T00:00:00Z")
        self.assertEqual((got["value"], got["unit"], got["freq"], got["variable"]), (float(raw["value"]), "bcf", "P1W", "working_gas"))
        self.assertNotIn("(Billion Cubic Feet)", got["node"])

    def test_weekly_petroleum_series_keep_their_kind_and_unit(self):
        out, _, _ = es.shape(part("eia_petroleum_supply_weekly", 1), eia_rows("eia_wpsr_supply_sample.json"), "weekly")
        by = {r["entity"]: r for r in out if r["ts_utc"] == "2026-09-25T00:00:00Z"}
        self.assertEqual((by["eia:WCRFPUS2"]["variable"], by["eia:WCRFPUS2"]["unit"]), ("production", "kbbl/d"))
        self.assertEqual((by["eia:WPULEUS3"]["variable"], by["eia:WPULEUS3"]["unit"]), ("utilization", "pct"))
        self.assertEqual(by["eia:WCRRIP32"]["variable"], "crude_input")

    def test_gas_trade_keeps_the_totals_and_each_terminals_total_not_the_rows_by_country(self):
        rows = eia_rows("eia_gas_trade_sample.json")
        self.assertTrue(any(r["series"].startswith("NGM_EPG0_ENG_YSPL-N") for r in rows))        # Sabine Pass by country, in EIA's answer
        out, _, _ = es.shape(part("eia_gas_trade_monthly"), rows, "monthly")
        got = {r["entity"] for r in out}
        self.assertIn("eia:N9132MX2", got)
        self.assertIn("eia:N9133US2", got)
        self.assertIn("eia:NGM_EPG0_ENG_YSPL-Z00_MMCF", got)
        self.assertNotIn("eia:N9133JA2", got)                       # LNG to one country is not a row
        self.assertFalse(any(re.search(r"_YSPL-N[A-Z]{2}_", e) for e in got))
        self.assertTrue(all(r["ts_utc"] == "2026-07-01T00:00:00Z" and r["unit"] == "MMcf" for r in out))

    def test_the_outlooks_forecast_months_are_not_written(self):
        rows = eia_rows("eia_steo_sample.json")
        self.assertIn("2026-12", {r["period"] for r in rows})       # EIA's forecast, in EIA's answer
        out, empty, forecast = es.shape(part("eia_basin_production_monthly"), rows, "monthly", last_month="2026-07")
        self.assertEqual(max(r["ts_utc"] for r in out), "2026-07-01T00:00:00Z")
        self.assertEqual(forecast, sum(1 for r in rows if r["period"] > "2026-07"))
        self.assertEqual(len(out) + forecast + empty, len(rows))
        raw = next(r for r in rows if r["seriesId"] == "COPRPM" and r["period"] == "2026-07")
        pm = next(r for r in out if r["entity"] == "eia:COPRPM" and r["ts_utc"] == "2026-07-01T00:00:00Z")
        self.assertAlmostEqual(pm["value"], float(raw["value"]) * 1000, places=3)      # million barrels a day, written in thousand
        self.assertEqual((pm["unit"], pm["variable"]), ("kbbl/d", "crude_production"))
        self.assertEqual(next(r for r in out if r["entity"] == "eia:NGMPHA")["unit"], "bcf/d")
        self.assertEqual(es.HISTORY_LAG, 3)

    def test_an_unexpected_unit_stops_the_pull_and_the_ceiling_stops_a_run(self):
        rows = eia_rows("eia_gas_storage_sample.json")
        rows[0] = dict(rows[0], units="TCF")                        # a real row with its unit changed
        with self.assertRaises(RuntimeError):
            es.shape(part("eia_gas_storage_weekly"), rows, "weekly")
        b = es.Budget()
        with self.assertRaises(RuntimeError):
            b.add(es.CEILING)
        self.assertEqual(es.CEILING, 1_200_000)


class Cftc(unittest.TestCase):
    def test_net_is_long_less_short_and_the_rest_is_the_cftcs(self):
        with open(os.path.join(FIX, "cftc_ng_sample.json"), encoding="utf-8") as f:
            rows = json.load(f)
        out, blank = cftc_cot.parse(rows, "023651", *STAMP)
        self.assertEqual(blank, 0)
        last = rows[-1]
        day = last["report_date_as_yyyy_mm_dd"][:10] + "T00:00:00Z"
        by = {r["variable"]: r["value"] for r in out if r["ts_utc"] == day}
        self.assertEqual(by["managed_money_long"], float(last["m_money_positions_long_all"]))
        self.assertEqual(by["managed_money_short"], float(last["m_money_positions_short_all"]))
        self.assertEqual(by["managed_money_net"], float(last["m_money_positions_long_all"]) - float(last["m_money_positions_short_all"]))
        self.assertEqual(by["open_interest"], float(last["open_interest_all"]))
        self.assertEqual(len(out), 4 * len(rows))
        with self.assertRaises(RuntimeError):
            cftc_cot.parse(rows, "067651", *STAMP)                  # the answer is for another contract than the one asked
        gone = [dict(r) for r in rows]
        del gone[0]["m_money_positions_short_all"]                  # a real week with its short position removed: not written, never a zero
        out2, blank2 = cftc_cot.parse(gone, "023651", *STAMP)
        self.assertEqual((blank2, len(out2)), (1, 4 * (len(rows) - 1)))

    def test_ice_brent_is_not_pulled(self):
        self.assertEqual(set(cftc_cot.CONTRACTS), {"067651", "06765T", "023651", "111659"})
        code = re.sub(r'""".*?"""', "", src("warehouse", "connectors", "cftc_cot.py"), flags=re.S)
        self.assertNotIn("ice.com", code)                           # ICE's address is in the docstring's reason, never in a request
        self.assertIn("ICE's terms", src("warehouse", "connectors", "cftc_cot.py"))


class Comparisons(unittest.TestCase):
    def test_gas_storage_against_last_week_last_year_and_the_five_year_average(self):
        s = held("gas_storage_lower48.csv")
        c = sp.compare(s, "W")
        d0 = D(2026, 9, 25)
        self.assertEqual(c["last"], {"t": "2026-09-25", "v": s[d0]})
        self.assertEqual(c["prev"]["ch"], s[d0] - s[D(2026, 9, 18)])
        self.assertEqual((c["year"]["t"], c["year"]["ch"]), ("2025-09-26", s[d0] - s[D(2025, 9, 26)]))      # 364 days: the same weekday
        five = [s[d0 - dt.timedelta(days=364 * k)] for k in range(1, 6)]
        self.assertAlmostEqual(c["avg5"]["v"], sum(five) / 5, places=4)
        self.assertEqual((c["avg5"]["lo"], c["avg5"]["hi"]), (min(five), max(five)))
        self.assertAlmostEqual(c["avg5"]["ch"], s[d0] - sum(five) / 5, places=4)
        self.assertEqual(c["avg5"]["outside"], not (min(five) <= s[d0] <= max(five)))

    def test_the_surprise_is_the_change_less_the_five_year_average_change(self):
        s = held("gas_storage_lower48.csv")
        c = sp.compare(s, "W")["change"]
        d0 = D(2026, 9, 25)
        changes = [s[d0 - dt.timedelta(days=364 * k)] - s[d0 - dt.timedelta(days=364 * k + 7)] for k in range(1, 6)]
        self.assertEqual(c["v"], s[d0] - s[D(2026, 9, 18)])
        self.assertAlmostEqual(c["avg5"], sum(changes) / 5, places=4)
        self.assertAlmostEqual(c["surprise"], c["v"] - sum(changes) / 5, places=4)
        self.assertEqual((c["lo"], c["hi"]), (min(changes), max(changes)))
        self.assertEqual(c["outside"], not (min(changes) <= c["v"] <= max(changes)))

    def test_a_comparison_whose_value_is_missing_is_not_made(self):
        s = held("gas_storage_lower48.csv")
        d0 = D(2026, 9, 25)
        cut = {d: v for d, v in s.items() if abs((d - (d0 - dt.timedelta(days=364 * 3))).days) > sp.NEAR}       # real values, the week three years back removed
        c = sp.compare(cut, "W")
        self.assertIsNone(c["avg5"])                                # four years are not five
        self.assertIsNone(c["change"]["surprise"])
        self.assertIsNotNone(c["year"])
        no_prev = {d: v for d, v in s.items() if d != D(2026, 9, 18)}
        self.assertIsNone(sp.compare(no_prev, "W")["prev"])
        self.assertIsNone(sp.compare(no_prev, "W")["change"])
        self.assertIsNone(sp.compare({}, "W"))

    def test_a_monthly_series_is_compared_by_the_month(self):
        s = held("gas_exports_mexico.csv")
        c = sp.compare(s, "M")
        d0 = max(s)
        self.assertEqual(d0, D(2026, 7, 1))
        self.assertEqual((c["prev"]["t"], c["year"]["t"]), ("2026-06-01", "2025-07-01"))
        five = [s[D(2026 - k, 7, 1)] for k in range(1, 6)]
        self.assertAlmostEqual(c["avg5"]["v"], sum(five) / 5, places=3)
        self.assertEqual(sp.step(D(2026, 1, 1), "M"), D(2025, 12, 1))
        self.assertEqual(sp.back(D(2026, 7, 1), 2, "M"), D(2024, 7, 1))

    def test_the_seasonal_band_runs_through_the_year_and_past_the_latest(self):
        s = held("gas_storage_lower48.csv")
        se = sp.compare(s, "W")["season"]
        self.assertEqual(len({len(se[k]) for k in ("t", "cur", "last", "avg", "lo", "hi")}), 1)
        self.assertTrue(all(t.startswith("2026") for t in se["t"]))
        i = se["t"].index("2026-09-25")
        self.assertEqual(se["cur"][i], s[D(2026, 9, 25)])
        self.assertEqual(se["last"][i], s[D(2025, 9, 26)])
        self.assertTrue(all(v is None for v in se["cur"][i + 1:]))  # no value of this year past the latest
        self.assertIsNotNone(se["avg"][i + 4])                      # the five years before go on to the end of the year
        self.assertLessEqual(se["lo"][i], se["avg"][i])
        self.assertLessEqual(se["avg"][i], se["hi"][i])


class Calendar(unittest.TestCase):
    def test_eias_holiday_tables_as_published(self):
        w = rs.exceptions("wpsr", rs.text_of(src("tests", "fixtures", "session134", "eia_wpsr_schedule.html")))
        col = next(e for e in w if e["week_ending"] == "2026-10-09")
        self.assertEqual((col["date"], col["day"], col["time"], col["holiday"]), ("2026-10-15", "Thursday", "12:00", "Columbus Day"))
        g = rs.exceptions("wngsr", rs.text_of(src("tests", "fixtures", "session134", "eia_wngsr_schedule.html")))
        vet = next(e for e in g if e["date"] == "2026-11-13")
        self.assertEqual((vet["day"], vet["time"], vet["holiday"]), ("Friday", "10:30", "Veterans Day"))
        self.assertEqual(rs.clock("1:00 p.m."), "13:00")
        self.assertEqual(rs.clock("12:00 p.m."), "12:00")

    def test_the_next_release_is_the_standing_day_or_the_date_the_publisher_moved_it_to(self):
        tz = ZoneInfo("America/New_York")
        by = lambda now: {r["id"]: r for r in sp.calendar(now)["reports"]}      # noqa: E731
        a = by(dt.datetime(2026, 10, 6, 6, 0, tzinfo=tz))             # a Tuesday morning
        self.assertEqual((a["wpsr"]["next"], a["wngsr"]["next"], a["cot"]["next"]), ("2026-10-07T10:30", "2026-10-08T10:30", "2026-10-09T15:30"))
        self.assertIsNone(a["wpsr"]["moved"])
        b = by(dt.datetime(2026, 10, 12, 9, 0, tzinfo=tz))            # the week of Columbus Day
        self.assertEqual(b["wpsr"]["next"], "2026-10-15T12:00")
        self.assertIn("Columbus Day", b["wpsr"]["moved"])
        c = by(dt.datetime(2026, 10, 7, 11, 0, tzinfo=tz))            # Wednesday, after the report is out: the next one
        self.assertEqual(c["wpsr"]["next"], "2026-10-15T12:00")
        self.assertEqual(c["wngsr"]["next"], "2026-10-08T10:30")
        d = by(dt.datetime(2026, 10, 14, 11, 0, tzinfo=tz))           # the standing Wednesday of the moved week: Thursday's is still to come
        self.assertEqual(d["wpsr"]["next"], "2026-10-15T12:00")
        e = by(dt.datetime(2026, 10, 15, 12, 30, tzinfo=tz))          # and once it is out, the Wednesday after
        self.assertEqual((e["wpsr"]["next"], e["wpsr"]["moved"]), ("2026-10-21T10:30", None))

    def test_the_page_works_the_next_release_out_when_it_is_read(self):
        with open(os.path.join(SITE, "data", "supply.json"), encoding="utf-8") as f:
            reports = json.load(f)["calendar"]["reports"]
        for r in reports:                                             # the file carries each report's rule and alternate dates
            self.assertIn(r["weekday"], (2, 3, 4))
            self.assertRegex(r["time"], r"^\d\d:\d\d$")
            self.assertIsInstance(r["exceptions"], list)
        self.assertTrue(any(e["date"] == "2026-10-15" and e["holiday"] == "Columbus Day" for e in reports[0]["exceptions"]))
        page = src("site", "app", "supply", "page.tsx")
        self.assertIn("nextRelease(r, eastern)", page)
        self.assertIn("easternNow(new Date())", page)
        self.assertNotIn("releaseWords(r.next)", page)                # never the date the file was built with


class ThePageFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(SITE, "data", "supply.json"), encoding="utf-8") as f:
            cls.file = json.load(f)
        cls.rows = {r["id"]: r for r in cls.file["rows"]}

    def test_every_number_stands_against_the_three(self):
        ok = [r for r in self.file["rows"] if r["status"] == "ok"]
        self.assertGreaterEqual(len(ok), 80)
        for r in ok:
            for k in ("last", "prev", "year", "avg5", "change", "spark", "season"):
                self.assertIn(k, r, (r["id"], k))
            self.assertIn(r["freq"], ("W", "M"))
        for key in ("eia-nw2-epg0-swo-r48-bcf", "eia-wcestus1", "eia-w-epc0-sax-ycuok-mbbl", "eia-wgtstus1", "eia-wdistus1", "eia-wcrfpus2", "eia-wpuleus3"):
            r = self.rows[key]
            self.assertIsNotNone(r["prev"], key)
            self.assertIsNotNone(r["year"], key)
            self.assertIsNotNone(r["avg5"], key)
            self.assertIsNotNone(r["change"]["surprise"], key)

    def test_storage_in_the_file_is_the_sample_and_its_reading_is_by_its_sense(self):
        s = held("gas_storage_lower48.csv")
        r = self.rows["eia-nw2-epg0-swo-r48-bcf"]
        if r["last"]["t"] == "2026-09-25":                          # the file as built on 6 October 2026
            self.assertEqual(r["last"]["v"], s[D(2026, 9, 25)])
        self.assertEqual((r["sense"], r["unit"]), (1, "bcf"))
        self.assertEqual(self.rows["eia-wcrexus2"]["sense"], -1)    # more exports is tighter
        self.assertEqual(self.rows["eia-wpuleus3"]["sense"], 0)     # refinery utilization carries no reading
        self.assertEqual(self.rows["eia-wcestus1"]["unit"], "million bbl")

    def test_what_is_not_open_is_listed_blank_with_its_source(self):
        gas = self.rows["gasprod-weekly"]
        self.assertEqual(gas["status"], "licensed")
        self.assertIn("S&P Global", gas["note"])
        ice = self.rows["ice-brent"]
        self.assertEqual(ice["status"], "licensed")
        self.assertIn("ICE", ice["note"])
        # session 136: the five operators that publish it openly are held; MISO and PJM stay blank
        self.assertEqual((self.rows["cleared-miso"]["status"], self.rows["cleared-pjm"]["status"]), ("paused", "licensed"))
        self.assertIn(self.rows["cleared-ercot"]["status"], ("ok", "not_held"))
        for r in self.file["rows"]:
            if r["status"] != "ok":
                self.assertTrue(r.get("note"), r["id"])
                self.assertNotIn("last", r, r["id"])

    def test_fuel_burned_is_derived_with_stated_heat_rates(self):
        self.assertEqual(self.file["heat_rate"], {"natural_gas": 7.6, "coal": 10.6, "oil": 11.0})
        self.assertEqual(self.file["heat_content"]["natural_gas"]["unit"], "bcf/d")
        burn = [r for r in self.file["rows"] if r["group"] == "burn" and r["status"] == "ok"]
        self.assertGreaterEqual(len(burn), 12)
        self.assertTrue(all(r["sense"] == -1 and r["freq"] == "W" for r in burn))
        self.assertTrue(all(dt.date.fromisoformat(r["last"]["t"]).weekday() == 4 for r in burn))        # a week ends on Friday, as the storage week does
        for key in ("burn-caiso-oil", "burn-miso-oil", "burn-isone-coal"):      # the hourly file leaves the fuel blank: no value, never a zero
            self.assertEqual(self.rows[key]["status"], "not_held", key)
            self.assertIn("A blank hour is not read as zero", self.rows[key]["note"])
        self.assertNotIn("fillna", re.sub(r"(?s)^.*?def burn_rows", "", src("warehouse", "derived", "supply_page.py")).split("def cleared_rows")[0])

    def test_positioning_for_four_contracts_and_the_calendar_for_three_reports(self):
        pos = [r for r in self.file["rows"] if r["group"] == "position" and r["status"] == "ok"]
        self.assertEqual({r["id"] for r in pos}, {"cftc-067651", "cftc-06765t", "cftc-023651", "cftc-111659"})
        for r in pos:
            self.assertEqual(r["last"]["v"], r["long"] - r["short"])
            self.assertIn("three_year", r)
        self.assertEqual([r["id"] for r in self.file["calendar"]["reports"]], ["wpsr", "wngsr", "cot"])
        self.assertTrue(all(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", r["next"]) for r in self.file["calendar"]["reports"]))


class ThePage(unittest.TestCase):
    def test_under_the_prices_menu_in_review_at_its_address(self):
        pages = src("site", "lib", "pages.ts")
        prices = pages[pages.index('label: "Prices"'):pages.index('label: "Grid"')]
        self.assertIn('{ href: "/supply", label: "Supply and trade"', prices)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/supply":\s*"review"')
        page = src("site", "app", "supply", "page.tsx")
        self.assertIn('title: "Supply and trade"', page)
        self.assertIn("robots: { index: false, follow: false }", page)

    def test_the_page_face_carries_no_method(self):
        face = src("site", "app", "supply", "page.tsx") + src("site", "components", "supply", "SupplyCharts.tsx")
        shown = re.sub(r"(?m)^\s*//.*$", "", face)
        for word in ("methodology", "limitation", "disputed", "<Fold", "SourceLine", "against expectations", "consensus"):
            self.assertNotIn(word, shown, word)
        self.assertIn('"/data/methods/supply_and_trade"', shown)
        lib = src("site", "lib", "supply.ts")
        for words in ("paused while terms are reviewed", "licensed source needed", "not held yet", "working on it"):
            self.assertIn(words, lib)

    def test_the_method_note_holds_the_research_the_terms_and_the_assumptions(self):
        note = src("docs", "methods", "supply_and_trade.md")
        for words in ("What trader desks and public dashboards show each morning", "five-year average change", "7.6", "10.6", "1.037", "public domain", "ICE", "personal, non-commercial use",
                      "S&P Global", "three months before", "Thursday 10:30", "not the whole country"):
            self.assertIn(words, note, words)

    def test_the_refresh_is_scheduled_once_a_week_through_the_guard(self):
        # 6 October 2026: the owner had it scheduled (the chain prompt of that day). Until then this test asserted
        # that nothing called the script; it now asserts the one call, on Saturdays, under health.py, and the guard
        sh = src("warehouse", "refresh_supply.sh")
        for step in ('--step "eia_supply"', '--step "cftc_cot"', '--step "release_schedule"', '--step "supply_page"'):
            self.assertIn("health.py run " + step, sh)
        self.assertIn("warehouse/derived/page_keep.py supply", sh)
        for wf in os.listdir(os.path.join(ROOT, ".github", "workflows")):
            self.assertNotIn("refresh_supply.sh", src(".github", "workflows", wf), wf)
        daily = src("warehouse", "run_daily.sh")
        self.assertEqual(daily.count('health.py run --step "supply" -- bash warehouse/refresh_supply.sh'), 1)
        self.assertIn('if [ "$(date -u +%u)" = "6" ] || [ "${SUPPLY:-0}" = "1" ]; then', daily)
        self.assertIn("site/data/supply.json warehouse/metadata/release_schedule.json", src(".github", "workflows", "daily-prices.yml"))

    def test_the_new_tables_are_held_out_of_the_live_set_and_no_miso_request_is_made(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        import load
        for t in ("eia_gas_storage_weekly", "eia_petroleum_supply_weekly", "eia_gas_trade_monthly", "eia_basin_production_monthly", "cftc_cot_positions"):
            self.assertIn(t, load.LIVE["catalogue_hold"])
        for s in ("eia:natural-gas/stor/wkly", "eia:petroleum/sum/sndw", "eia:steo:basin_production", "cftc:disaggregated_cot_futures"):
            self.assertIn(s, load.LIVE["sources_hold"])
        for f in ("eia_supply.py", "cftc_cot.py", "release_schedule.py"):
            self.assertNotIn("misoenergy", src("warehouse", "connectors", f))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for p in (("warehouse", "connectors", "eia_supply.py"), ("warehouse", "connectors", "cftc_cot.py"), ("warehouse", "connectors", "release_schedule.py"), ("warehouse", "derived", "supply_page.py"),
                  ("warehouse", "refresh_supply.sh"), ("site", "app", "supply", "page.tsx"), ("site", "lib", "supply.ts"), ("site", "components", "supply", "SupplyCharts.tsx"),
                  ("site", "scripts", "check-supply.mjs"), ("site", "scripts", "test-supply.mjs"), ("docs", "methods", "supply_and_trade.md"), ("tests", "test_session134.py")):
            text = src(*p)
            self.assertNotIn(chr(0x2014), text, p)
            self.assertNotIn(chr(0x2013), text, p)


if __name__ == "__main__":
    unittest.main()
