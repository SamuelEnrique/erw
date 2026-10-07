"""Session 98: curtailment, version 2 (/curtailment/v2), in review, and the approved pull behind it. Since session
144 version 2 is part of the one page, /curtailment: its address redirects there, its page is kept under
site/app/_retired/curtailment-v2, and its numbers are checked on the one page by site/scripts/check-curtailment.mjs.

Energy Research Warehouse (ERW). The connector (warehouse/connectors/caiso_curtailment_intervals.py) on a workbook and a
report made here, with no request; the profile's builder (warehouse/derived/curtailment_profile.py) on rows made here;
the two tables as built; the site's copy against the table; and the page's pure part (site/lib/curtailmentv2.ts), run by
node. Every number the page shows against the site's copy is site/scripts/check-curtailment-v2.mjs, which runs here
when ERW_SITE_URL names a built site.

    python -m unittest tests.test_session98 -v
"""

import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import caiso_curtailment_intervals as cc  # noqa: E402
import curtailment_profile as cp  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
COPY = os.path.join(SITE, "data", "curtailment_profile.json")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def copy():
    with open(COPY, encoding="utf-8") as f:
        return json.load(f)


def book(rows, reason=True):
    """A workbook as CAISO's, in memory: rows of (date, hour, interval, wind, solar[, reason])."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Curtailments"
    ws.append(["Date", "Hour", "Interval", "Wind Curtailment", "Solar Curtailment"] + (["Reason"] if reason else []))
    for r in rows:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def report(day, fill=None, hours=24, chart=None):
    """A daily report's page as CAISO's: every hourly array of the day, zeros but for fill {(fuel, cat): {hour: MWh}}."""
    y, m, d = (int(x) for x in (chart or day).split("-"))
    html = f"<script>var chart_date = new Date(Date.UTC({y}, {m - 1}, {d}));\n"
    for fuel in ("solar", "wind"):
        for cat in cc.CATS:
            v = [(fill or {}).get((fuel, cat), {}).get(h, 0) for h in range(hours)]
            html += f"var curt_hr_tot_{fuel}_{cat}_mwh = [{', '.join(str(x) for x in v)}];\n"
    return html + "</script>"


class TheConnector(unittest.TestCase):
    def test_an_intervals_start(self):
        self.assertEqual(cc.ip.utc_iso(cc.interval_start("2024-07-15", 12, 1)[0]), "2024-07-15T18:00:00Z")      # hour ending 12 is 11:00 Pacific daylight time
        self.assertEqual(cc.ip.utc_iso(cc.interval_start("2024-01-15", 12, 12)[0]), "2024-01-15T19:55:00Z")     # standard time, the hour's last interval
        ts, twice = cc.interval_start("2019-11-03", 2, 3)                                                       # 01:10 on the day the clock hour happens twice
        self.assertEqual((cc.ip.utc_iso(ts), twice), ("2019-11-03T08:10:00Z", True))                            # dated the first, daylight time
        self.assertEqual(cc.interval_start("2019-11-03", 12, 1)[1], False)

    def test_a_workbooks_rows_are_read_once_by_fuel_and_reason(self):
        day = dt.datetime(2024, 7, 15, 7, 0)                                                                   # CAISO's Date carries the day's UTC offset as a time
        a = book([(day, 12, 1, None, 30.5, "Local"), (day, 12, 1, 4.0, 10.0, "System"), (day, 12, 2, 0, "", "Local"), (dt.datetime(2018, 5, 1), 12, 1, 9.0, 9.0, "Local")])
        b = book([(day, 12, 1, None, 30.5, "Local"), (day, 13, 1, 2.0, None, "Local")])                         # the first row repeats the other workbook's
        old = book([(dt.datetime(2020, 3, 1), 10, 6, 5.0, 60.0)], reason=False)
        rows, days = cc.legacy_rows([("a.xlsx", "https://x/a.xlsx", a, "Wed, 22 Jan 2025 19:26:14 GMT", "2026-10-04T10:36:17Z"), ("b.xlsx", "https://x/b.xlsx", b, "", ""),
                                     ("old.xlsx", "https://x/old.xlsx", old, "", "")], lambda *_: None)
        got = sorted((cc.ip.utc_iso(ts), v, mw, url) for ts, v, mw, url, _, _ in rows)
        self.assertEqual(got, [("2020-03-01T17:25:00Z", "curtailed_solar_mw", 60.0, "https://x/old.xlsx"), ("2020-03-01T17:25:00Z", "curtailed_wind_mw", 5.0, "https://x/old.xlsx"),
                               ("2024-07-15T18:00:00Z", "curtailed_solar_local_mw", 30.5, "https://x/a.xlsx"), ("2024-07-15T18:00:00Z", "curtailed_solar_system_mw", 10.0, "https://x/a.xlsx"),
                               ("2024-07-15T18:00:00Z", "curtailed_wind_system_mw", 4.0, "https://x/a.xlsx"), ("2024-07-15T19:00:00Z", "curtailed_wind_local_mw", 2.0, "https://x/b.xlsx")])
        self.assertEqual(rows[0][4], "2025-01-22T19:26:14Z")                                                    # the workbook's own date is the vintage
        self.assertEqual(sorted(days), ["2020-03-01", "2024-07-15"])                                            # 2018 is before the pull's first year

    def test_a_daily_reports_rows_and_a_report_that_is_not_written(self):
        html = report("2026-07-15", {("solar", "econ_local"): {7: 10.29, 16: 604.1}, ("wind", "oi_system"): {3: 1.5}})
        rows, totals = cc.report_rows(html, "2026-07-15")
        self.assertEqual(sorted((cc.ip.utc_iso(ts), v, x) for ts, v, x in rows), [("2026-07-15T10:00:00Z", "curtailed_wind_oi_system_mwh", 1.5),
                         ("2026-07-15T14:00:00Z", "curtailed_solar_econ_local_mwh", 10.29), ("2026-07-15T23:00:00Z", "curtailed_solar_econ_local_mwh", 604.1)])
        self.assertEqual((round(totals["solar"], 2), totals["wind"]), (614.39, 1.5))
        self.assertEqual(cc.report_rows(report("2026-07-15"), "2026-07-15"), ([], {"wind": 0.0, "solar": 0.0}))  # a day with none is a day, with zero
        self.assertIsNone(cc.report_rows(html, "2026-07-16"))                                                   # the page of another day
        spring = cc.report_rows(report("2026-03-08", {("solar", "econ_system"): {1: 2.0, 9: 3956.0}}), "2026-03-08")   # 24 values on a day of 23 hours: by the clock
        self.assertEqual(sorted((cc.ip.utc_iso(ts), x) for ts, _, x in spring[0]), [("2026-03-08T09:00:00Z", 2.0), ("2026-03-08T16:00:00Z", 3956.0)])   # 01:00 standard, 09:00 daylight
        self.assertIsNone(cc.report_rows(report("2026-03-08", {("solar", "econ_system"): {2: 5.0}}), "2026-03-08"))   # a value in the clock hour that does not exist
        self.assertIsNotNone(cc.report_rows(report("2026-03-08", hours=23), "2026-03-08"))
        self.assertIsNone(cc.report_rows(report("2026-07-15", hours=20), "2026-07-15"))                          # a short array
        self.assertIsNone(cc.report_rows(html.replace("var curt_hr_tot_wind_ss_local_mwh", "var other"), "2026-07-15"))

    def test_the_pull_has_a_ceiling_and_asks_the_pause_first(self):
        self.assertEqual((cc.CEILING, cc.FIRST_YEAR), (500_000, 2019))
        code = src("warehouse", "connectors", "caiso_curtailment_intervals.py")
        self.assertLess(code.index('if ip.paused("caiso")'), code.index("books = workbooks("))                 # before any request
        self.assertLess(code.index("if len(out) > CEILING"), code.index("ip.write_csv(out"))                   # and it stops before it writes
        self.assertIn("credit the California ISO", cc.TERMS)


class TheProfile(unittest.TestCase):
    def test_a_month_by_hour_reason_and_battery(self):
        rows = []
        days = pd.date_range("2026-06-01", "2026-06-30").strftime("%Y-%m-%d")
        for d in days:
            rows.append(dict(variable="curtailed_solar_day_mwh", ts_utc=f"{d}T00:00:00Z", value=110.0, freq="P1D"))
            rows.append(dict(variable="curtailed_wind_day_mwh", ts_utc=f"{d}T00:00:00Z", value=0.0, freq="P1D"))
            noon = pd.Timestamp(f"{d} 12:00", tz=cp.TZ).tz_convert("UTC")
            rows.append(dict(variable="curtailed_solar_econ_local_mwh", ts_utc=cc.ip.utc_iso(noon), value=100.0, freq="PT1H"))
            rows.append(dict(variable="curtailed_solar_oi_system_mwh", ts_utc=cc.ip.utc_iso(noon + pd.Timedelta(hours=7)), value=10.0, freq="PT1H"))   # 19:00: the batteries discharge
        t = pd.DataFrame(rows)
        start = pd.Timestamp("2026-06-01", tz=cp.TZ).tz_convert("UTC")
        idx = pd.date_range(start, periods=30 * 288, freq="5min")
        hour = idx.tz_convert(cp.TZ).hour
        b = pd.DataFrame({"variable": "batteries_mw", "ts_utc": [cc.ip.utc_iso(i) for i in idx], "value": [-600.0 if 10 <= h < 14 else 500.0 if 18 <= h < 21 else 0.0 for h in hour]})
        m = cp.summarize(cp.hourly_curtailment(t), cp.covered_days(t), cp.battery_hours(b))["2026-06"]
        self.assertEqual((m["days_held"], m["days_in_month"], m["battery_days_held"]), (30, 30, 30))
        self.assertEqual((m["curtailed_solar_mwh"], m["curtailed_wind_mwh"]), (3300.0, 0.0))
        self.assertEqual((m["curtailed_solar_local_mwh"], m["curtailed_solar_system_mwh"], m["curtailed_solar_unspecified_mwh"]), (3000.0, 300.0, 0.0))
        self.assertEqual((m["curtailed_solar_econ_mwh"], m["curtailed_solar_oi_mwh"], m["curtailed_solar_ss_mwh"]), (3000.0, 300.0, 0.0))
        self.assertEqual((m["curtailed_solar_mwh_h12"], m["curtailed_solar_mwh_h19"], m["curtailed_solar_mwh_h11"]), (3000.0, 300.0, 0.0))
        self.assertEqual((m["avg_curtailed_mw_h12"], m["avg_battery_charging_mw_h12"], m["avg_battery_charging_mw_h19"]), (100.0, 600.0, 0.0))
        self.assertEqual((m["battery_charging_mwh"], m["curtailed_mwh_battery_days"]), (30 * 4 * 600.0, 3300.0))
        self.assertEqual(m["curtailed_while_charging_share_pct"], round(100 * 3000 / 3300, 2))

    def test_five_minute_mw_is_energy_over_five_minutes_and_a_month_needs_its_days(self):
        t = pd.DataFrame([dict(variable="curtailed_wind_mw", ts_utc="2020-03-01T17:25:00Z", value=60.0, freq="PT5M"),
                          dict(variable="curtailed_wind_mw", ts_utc="2020-03-01T17:30:00Z", value=60.0, freq="PT5M")]
                         + [dict(variable="curtailed_wind_day_mwh", ts_utc=f"{d}T00:00:00Z", value=0.0, freq="P1D") for d in pd.date_range("2020-03-01", "2020-03-28").strftime("%Y-%m-%d")])
        m = cp.summarize(cp.hourly_curtailment(t), cp.covered_days(t), cp.battery_hours(pd.DataFrame(columns=["variable", "ts_utc", "value"])))
        self.assertEqual(m["2020-03"]["curtailed_wind_mwh"], 10.0)                                              # 60 MW over two intervals
        self.assertEqual(m["2020-03"]["curtailed_wind_unspecified_mwh"], 10.0)
        self.assertEqual(m["2020-03"]["curtailed_wind_mwh_h09"], 10.0)                                          # 17:25 UTC is 09:25 Pacific standard time
        self.assertNotIn("curtailed_wind_econ_mwh", m["2020-03"])
        self.assertNotIn("battery_days_held", m["2020-03"])
        short = t[~t["ts_utc"].isin([f"2020-03-{d:02d}T00:00:00Z" for d in range(20, 29)])]                     # 19 days of 31
        self.assertEqual(cp.summarize(cp.hourly_curtailment(short), cp.covered_days(short), cp.battery_hours(pd.DataFrame(columns=["variable", "ts_utc", "value"]))), {})
        self.assertEqual([cp.unit_of(v) for v in ("days_held", "battery_days_held", "avg_curtailed_mw_h03", "curtailed_solar_mwh_h03", "curtailed_while_charging_share_pct", "battery_charging_mwh")],
                         ["count", "count", "MW", "MWh", "pct", "MWh"])

    def test_a_year_is_the_sum_of_its_months_when_all_are_held(self):
        months = {f"2025-{i:02d}": {"days_held": 30, "days_in_month": 30, "curtailed_solar_mwh": 10.0, "curtailed_solar_mwh_h12": 4.0, "curtailed_while_charging_share_pct": 50.0} for i in range(1, 13)}
        y = cp.year_of(months, "2025")
        self.assertEqual((y["months"], y["curtailed_solar_mwh"], y["curtailed_solar_mwh_h12"], y["days_held"]), (12, 120.0, 48.0, 360))
        self.assertNotIn("curtailed_while_charging_share_pct", y)                                               # a share is not summed
        del months["2025-06"]
        self.assertIsNone(cp.year_of(months, "2025"))


class TheTablesAsBuilt(unittest.TestCase):
    def table(self, name):
        path = os.path.join(OUT, f"{name}.csv")
        if not os.path.exists(path):
            self.skipTest(f"{name} is not on this machine")
        return pd.read_csv(path, comment="#")

    def test_the_pull_is_under_its_ceiling_and_equals_the_daily_table(self):
        t = self.table(cc.NAME)
        self.assertLessEqual(len(t), cc.CEILING)
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(set(t["freq"]), {"PT5M", "PT1H", "P1D"})
        self.assertTrue((t[t["freq"] != "P1D"]["value"] > 0).all())
        self.assertGreaterEqual(t[t["freq"] == "PT5M"]["ts_utc"].min(), "2019-01-01")
        self.assertLess(t[t["freq"] == "PT5M"]["ts_utc"].max(), "2026-01-01T08:00:00Z")
        self.assertGreaterEqual(t[t["freq"] == "PT1H"]["ts_utc"].min(), "2026-01-01T08:00:00Z")
        head = src("warehouse", "output", f"{cc.NAME}.csv")[:5000]
        self.assertIn("credit the California ISO", head)
        d = t[t["freq"] == "P1D"].assign(fuel=lambda x: x["variable"].str.split("_").str[1])
        old = self.table("caiso_curtailment_daily")
        old = old[old["variable"].isin(["curtailed_wind_mwh", "curtailed_solar_mwh"])].assign(fuel=lambda x: x["variable"].str.split("_").str[1])
        m = d.merge(old, on=["ts_utc", "fuel"], suffixes=("", "_daily"))
        self.assertGreater(len(m), 5600)
        self.assertLess((m["value"] - m["value_daily"]).abs().max(), 0.01)
        x = t[(t["freq"] == "PT5M") & (t["ts_utc"] >= "2024-05-01T07:00:00Z") & (t["ts_utc"] < "2024-05-02T07:00:00Z") & t["variable"].str.contains("solar")]
        day = d[(d["ts_utc"] == "2024-05-01T00:00:00Z") & (d["fuel"] == "solar")]["value"].iloc[0]
        self.assertAlmostEqual(float((x["value"] * 5 / 60).sum()), day, delta=0.02)                             # a day's five-minute MW add up to its day row

    def test_a_month_of_the_profile_added_again_from_the_intervals(self):
        p, t = self.table(cp.NAME), self.table(cc.NAME)
        at = lambda v, m: float(p[(p["variable"] == v) & (p["ts_utc"] == f"{m}-01T00:00:00Z")]["value"].iloc[0])
        a, b = pd.Timestamp("2024-04-01", tz=cp.TZ).tz_convert("UTC"), pd.Timestamp("2024-05-01", tz=cp.TZ).tz_convert("UTC")
        x = t[t["freq"] == "PT5M"].assign(ts=lambda d: pd.to_datetime(d["ts_utc"], utc=True))
        x = x[(x["ts"] >= a) & (x["ts"] < b)]
        self.assertAlmostEqual(at("curtailed_solar_mwh", "2024-04"), float((x[x["variable"].str.contains("solar")]["value"] * 5 / 60).sum()), delta=0.06)
        self.assertAlmostEqual(at("curtailed_wind_system_mwh", "2024-04"), float((x[x["variable"] == "curtailed_wind_system_mw"]["value"] * 5 / 60).sum()), delta=0.06)
        noon = x[x["variable"].str.contains("solar") & (x["ts"].dt.tz_convert(cp.TZ).dt.hour == 12)]
        self.assertAlmostEqual(at("curtailed_solar_mwh_h12", "2024-04"), float((noon["value"] * 5 / 60).sum()), delta=0.06)
        self.assertEqual(at("days_held", "2026-03"), 31)                                                        # the day the clocks went forward is held, placed by the clock
        self.assertFalse(p["variable"].str.startswith("battery").any() and p[p["variable"] == "battery_days_held"]["ts_utc"].min() < "2025-09")
        share = p[p["variable"] == "curtailed_while_charging_share_pct"]["value"]
        self.assertTrue(((share >= 0) & (share <= 100)).all())
        for m in ("2023-06", "2026-05"):                                                                        # the reasons add up to the fuel's total
            for fuel in cp.FUELS:
                self.assertAlmostEqual(sum(at(f"curtailed_{fuel}_{r}_mwh", m) for r in cp.REASONS), at(f"curtailed_{fuel}_mwh", m), delta=0.3)

    def test_the_sites_copy_is_the_table(self):
        p = self.table(cp.NAME)
        c = copy()
        want = {(r.variable, r.ts_utc[:7]): r.value for r in p.itertuples()}
        got = {(k, m): v for m, r in c["months"].items() for k, v in r.items()}
        self.assertEqual(got, want)
        y = c["years"]["2025"]
        self.assertAlmostEqual(y["curtailed_solar_mwh"], sum(c["months"][f"2025-{i:02d}"]["curtailed_solar_mwh"] for i in range(1, 13)), delta=0.2)
        self.assertEqual(c["days_not_held"], [])


class ThePage(unittest.TestCase):
    def test_the_choices_and_what_a_period_holds(self):
        d = node("import fs from 'node:fs'; import * as c from './lib/curtailmentv2.ts'; const f = JSON.parse(fs.readFileSync('./data/curtailment_profile.json', 'utf-8'));"
                 "const r = f.months['2026-05'];"
                 "console.log(JSON.stringify({p: [c.choice({}, f), c.choice({period:'2024-04'}, f), c.choice({period:'1999'}, f), c.choice({period:'2026'}, f)], href: c.href('2024-04'),"
                 "cover: [c.reasonCover(f.years['2019']), c.reasonCover(f.years['2022']), c.reasonCover(f.years['2024'])], cats: [c.hasCats(f.years['2025']), c.hasCats(r)],"
                 "batt: [c.hasBattery(f.months['2025-08'] ?? {}), c.hasBattery(r)], bm: c.batteryMonths(f), peak: c.peakHour(r), sum: c.byHour(r, 'solar').reduce((a, b) => a + b, 0),"
                 "day: c.battDay(r)[12], names: [c.periodName('2026-05'), c.periodName('2025'), c.hourName(7), c.whole(1361345.6), c.two(98.65)]}));")
        c = copy()
        newest = sorted(c["years"])[-1]
        self.assertEqual(d["p"], [newest, "2024-04", newest, "2026"])
        self.assertEqual(d["href"], "/curtailment?period=2024-04")                                               # session 144: the one page's address
        self.assertEqual(d["cover"], ["none", "part", "all"])
        self.assertEqual((d["cats"], d["batt"]), ([False, True], [False, True]))
        self.assertEqual((d["bm"][0], len(d["bm"])), ("2025-09", 13))
        r = c["months"]["2026-05"]
        best = max(range(24), key=lambda h: r[f"curtailed_solar_mwh_h{h:02d}"] + r[f"curtailed_wind_mwh_h{h:02d}"])
        self.assertEqual(d["peak"], {"hour": best, "solar": r[f"curtailed_solar_mwh_h{best:02d}"], "wind": r[f"curtailed_wind_mwh_h{best:02d}"]})
        self.assertAlmostEqual(d["sum"], r["curtailed_solar_mwh"], delta=2)                                      # the hours of the day add up to the month
        self.assertEqual(d["day"], {"hour": 12, "curtailed": r["avg_curtailed_mw_h12"], "charging": r["avg_battery_charging_mw_h12"]})
        self.assertEqual(d["names"], ["May 2026", "2025", "07:00", "1,361,346", "98.65"])

    def test_the_page_is_in_review_and_what_it_said_of_what_is_not_located_is_kept(self):
        d = node("import { statusOf } from './lib/release.ts'; console.log(JSON.stringify([statusOf('/curtailment'), statusOf('/curtailment/v2'), statusOf('/data/methods/caiso_curtailment_intervals')]));")
        self.assertEqual(d, ["review", "review", "review"])
        # session 144: version 2 is part of /curtailment. Its page is kept, not routed (app/_retired); what it said of
        # what the data does not locate moved, whole, to the Method note; the one page carries the credit
        self.assertFalse(os.path.exists(os.path.join(SITE, "app", "curtailment", "v2")))
        page = src("site", "app", "_retired", "curtailment-v2", "page.tsx")
        self.assertNotIn("supabase", page)
        self.assertIn("robots: { index: false, follow: false }", page)
        self.assertIn("The data does not say where.", page)
        self.assertIn("The data does not say where.", src("docs", "methods", "curtailment.md"))
        self.assertIn("Credit: California ISO", src("site", "app", "curtailment", "page.tsx"))
        self.assertIn('{ source: "/curtailment/v2", destination: "/curtailment", permanent: true }', src("site", "next.config.ts"))

    def test_every_number_on_the_built_page_where_a_site_is_served(self):
        base = os.environ.get("ERW_SITE_URL")
        exe = shutil.which("node")
        if not base or not exe:
            self.skipTest("ERW_SITE_URL names no served site (or node is absent): node site/scripts/check-curtailment.mjs <base>")
        r = subprocess.run([exe, "scripts/check-curtailment.mjs", base], cwd=SITE, capture_output=True, text=True, timeout=900)                 # session 144: the one page's check
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "connectors", "caiso_curtailment_intervals.py"), ("warehouse", "derived", "curtailment_profile.py"), ("docs", "methods", "caiso_curtailment_intervals.md"),
                      ("site", "lib", "curtailmentv2.ts"), ("site", "app", "_retired", "curtailment-v2", "page.tsx"), ("site", "scripts", "check-curtailment-v2.mjs"), ("tests", "test_session98.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
