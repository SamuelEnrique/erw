"""Session 97: the demand growth explorer (/demand), in review.

Energy Research Warehouse (ERW). The builder of eia930_demand_growth (warehouse/derived/demand_growth.py) on hours made
here and on the table as built, computed again from the workbook; the site's copy against the table; the page's pure
part (site/lib/demandgrowth.ts), run by node; and that the page is in review. Every number the page shows against the
site's copy is site/scripts/check-demand.mjs, which runs here when ERW_SITE_URL names a built site.

    python -m unittest tests.test_session97 -v
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import demand_growth as dg  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
COPY = os.path.join(SITE, "data", "demand_growth.json")
TZ = "America/Chicago"


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


def hours(start, end, value):
    """Hourly demand over local [start, end): value is a number or a function of (year, month, hour)."""
    idx = pd.date_range(pd.Timestamp(start, tz=TZ).tz_convert("UTC"), pd.Timestamp(end, tz=TZ).tz_convert("UTC"), freq="h", inclusive="left")
    local = idx.tz_convert(TZ)
    v = [float(value(t.year, t.month, t.hour)) for t in local] if callable(value) else [float(value)] * len(idx)
    return pd.Series(v, index=idx)


class TheScreen(unittest.TestCase):
    def test_a_spike_and_a_zero_are_not_used_and_a_real_ramp_is(self):
        d = hours("2020-07-01", "2020-07-03", lambda y, m, h: 100_000 + 4_000 * min(h, 24 - h))     # a day that ramps 4 percent an hour
        d.iloc[10] = 224_345.0       # the hour of PJM's file
        d.iloc[20] = 0.0
        d.iloc[30] = np.nan
        s = dg.screened(d)
        self.assertTrue(np.isnan(s.iloc[10]) and np.isnan(s.iloc[20]) and np.isnan(s.iloc[30]))
        self.assertEqual(int(s.notna().sum()), len(d) - 3)                                        # every hour of the ramp is kept
        self.assertEqual(float(s.max()), float(d.drop(d.index[10]).max()))

    def test_a_faulty_hour_is_never_a_peak(self):
        d = hours("2019-01-01", "2021-01-01", 50_000.0)
        d[pd.Timestamp("2019-12-12 16:00", tz=TZ).tz_convert("UTC")] = 155_276.0
        d[pd.Timestamp("2019-07-19 17:00", tz=TZ).tz_convert("UTC")] = 52_000.0
        out, at, _ = dg.summarize(dg.screened(d), TZ)
        self.assertEqual(out[2019]["peak_demand_mw"], 52_000.0)
        self.assertEqual(at[2019]["peak_demand_mw"], "2019-07-19T22:00:00Z")
        self.assertEqual((out[2019]["hours_used"], out[2019]["hours_in_year"]), (8759, 8760))


class TheYears(unittest.TestCase):
    def test_growth_the_year_to_date_and_the_partial_year(self):
        level = {2019: 100.0, 2020: 110.0, 2021: 121.0}
        d = hours("2019-01-01", "2021-05-10", lambda y, m, h: level[y] + (10 if h == 17 else 0))
        out, at, last = dg.summarize(d, TZ)
        self.assertEqual(last, "2021-04")                                           # the last whole month of the newest year
        self.assertEqual(sorted(out), [2019, 2020, 2021])
        self.assertNotIn("avg_demand_mw", out[2021])                                # the newest year is partial: no annual figure
        self.assertAlmostEqual(out[2019]["avg_demand_mw"], 100 + 10 / 24, places=1)
        self.assertEqual(out[2020]["avg_demand_growth_since_2019_pct"], round(100 * (out[2020]["avg_demand_mw"] / out[2019]["avg_demand_mw"] - 1), 2))
        self.assertEqual(out[2020]["avg_demand_growth_yoy_pct"], out[2020]["avg_demand_growth_since_2019_pct"])
        self.assertEqual((out[2019]["peak_demand_mw"], out[2020]["peak_demand_mw"]), (110.0, 120.0))
        self.assertEqual(out[2020]["peak_demand_growth_since_2019_pct"], round(100 * (120 / 110 - 1), 2))
        self.assertEqual(out[2021]["ytd_hours_in_window"], dg.hours_between("2021-01-01", "2021-05-01", TZ))
        self.assertEqual(out[2019]["ytd_hours_in_window"], dg.hours_between("2019-01-01", "2019-05-01", TZ))   # the same months of every year
        self.assertEqual(out[2021]["ytd_avg_demand_growth_since_2019_pct"], round(100 * (out[2021]["ytd_avg_demand_mw"] / out[2019]["ytd_avg_demand_mw"] - 1), 2))
        self.assertIn("avg_demand_mw_m04", out[2021])
        self.assertNotIn("avg_demand_mw_m05", out[2021])                            # May is not whole
        self.assertNotIn("growth_mw_m01", out[2019])
        self.assertEqual(out[2020]["growth_mw_m03_h17"], 10.0)                      # on the last whole year: the change from 2019
        self.assertEqual(out[2020]["growth_pct_h05"], 10.0)
        self.assertEqual(len([k for k in out[2020] if k.startswith("growth_pct_m") and "_h" in k]), 288)

    def test_a_year_with_too_few_hours_is_not_written_and_the_lower_48_has_no_peak(self):
        d = hours("2019-01-01", "2021-02-01", 100.0)
        d[(d.index >= pd.Timestamp("2020-03-01", tz="UTC")) & (d.index < pd.Timestamp("2020-04-01", tz="UTC"))] = np.nan   # a month of 2020 blank: 91.5 percent
        out, _, _ = dg.summarize(d, TZ)
        self.assertIn("avg_demand_mw", out[2019])
        self.assertNotIn("avg_demand_mw", out[2020])
        self.assertNotIn("avg_demand_mw_m03", out[2020])
        self.assertIn("avg_demand_mw_m05", out[2020])                               # its whole months are still its months
        self.assertNotIn("growth_mw_m01", out[2019])                                # and with no later whole year, no change is written
        out, at, _ = dg.summarize(hours("2019-01-01", "2021-02-01", 100.0), TZ, peak=False)
        self.assertFalse([k for y in out.values() for k in y if "peak" in k])
        self.assertEqual([unit for unit in map(dg.unit_of, ("avg_demand_mw", "hours_used", "ytd_hours_in_window", "growth_pct_m01_h02", "growth_mw_h05"))], ["MW", "count", "count", "pct", "MW"])

    def test_the_break_check_compares_the_same_dates_of_each_year(self):
        d = hours("2019-01-01", "2026-03-01", lambda y, m, h: 20_000 + (500 if m == 12 else 0))
        d.index = d.index.tz_convert("America/Los_Angeles").tz_convert("UTC")
        rows = dg.break_check(d, "America/Los_Angeles")
        self.assertEqual([r["year"] for r in rows], [2025, 2024, 2023, 2022, 2021, 2020, 2019])
        self.assertTrue(all(0.95 < r["ratio"] < 1.05 for r in rows))


class TheTableAsBuilt(unittest.TestCase):
    def table(self):
        path = os.path.join(OUT, f"{dg.NAME}.csv")
        if not os.path.exists(path):
            self.skipTest("eia930_demand_growth is not built on this machine")
        return pd.read_csv(path, comment="#")

    def test_one_area_computed_again_from_the_workbook(self):
        t = self.table()
        try:
            raw, _, column = dg.read_demand("SWPP")
        except FileNotFoundError:
            self.skipTest("the EIA-930 workbooks are not on this machine")
        self.assertEqual(column, "Adjusted demand")
        local = raw.index.tz_convert("America/Chicago")
        y = raw[local.year == 2024]
        at = lambda v, yr: t[(t["entity"] == "eia930:SWPP") & (t["variable"] == v) & (t["ts_utc"] == f"{yr}-01-01T00:00:00Z")].iloc[0]
        self.assertEqual(at("hours_in_year", 2024)["value"], 8784)
        self.assertEqual(at("peak_demand_mw", 2024)["value"], float(y.drop(pd.Timestamp("2024-07-19T04:00:00Z")).max()))
        self.assertEqual(at("peak_demand_mw", 2024)["x_at"], dg.ip.utc_iso(y.drop(pd.Timestamp("2024-07-19T04:00:00Z")).idxmax()))
        self.assertAlmostEqual(at("avg_demand_mw", 2024)["value"], float(y.drop(pd.Timestamp("2024-07-19T04:00:00Z")).mean()), delta=0.06)   # one hour of 2024 is not used
        self.assertEqual(at("hours_used", 2024)["value"], 8783)

    def test_what_the_table_holds(self):
        t = self.table()
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(sorted(t["entity"].unique()), sorted(f"eia930:{b}" for b in dg.AREAS))
        self.assertFalse(t[(t["entity"] == "eia930:US48")]["variable"].str.contains("peak").any())
        peaks = t[t["variable"].isin(["peak_demand_mw", "ytd_peak_demand_mw"])]
        self.assertTrue(peaks["x_at"].str.match(r"^\d{4}-\d\d-\d\dT\d\d:00:00Z$").all())
        self.assertTrue(t[~t["variable"].isin(["peak_demand_mw", "ytd_peak_demand_mw"])]["x_at"].isna().all())
        pjm = t[(t["entity"] == "eia930:PJM") & (t["variable"] == "peak_demand_mw")].set_index("ts_utc")
        self.assertLess(pjm.loc["2020-01-01T00:00:00Z", "value"], 160_000)          # not the 224,345 MW of EIA's file
        self.assertTrue(pjm.loc["2019-01-01T00:00:00Z", "x_at"].startswith("2019-07"))   # and 2019's peak is in July, not on a December afternoon
        hours_used = t[t["variable"] == "hours_used"].merge(t[t["variable"] == "hours_in_year"], on=["entity", "ts_utc"])
        self.assertTrue((hours_used["value_x"] >= dg.NEAR_YEAR * hours_used["value_y"]).all())
        self.assertFalse(((t["variable"] == "avg_demand_mw") & (t["ts_utc"] == "2026-01-01T00:00:00Z")).any())   # the partial year has no annual figure

    def test_the_sites_copy_is_the_table_and_california_does_not_step(self):
        t = self.table()
        c = copy()
        n = 0
        for ba, a in c["areas"].items():
            rows = t[t["entity"] == f"eia930:{ba}"]
            want = {(r.variable, r.ts_utc[:4]): r.value for r in rows.itertuples()}
            got = {(k, y): v for y, r in a["years"].items() for k, v in r.items()}
            self.assertEqual(got, want, ba)
            when = {(r.variable, r.ts_utc[:4]): r.x_at for r in rows.itertuples() if isinstance(r.x_at, str)}
            self.assertEqual({(k, y): v for y, r in a["at"].items() for k, v in r.items()}, when, ba)
            n += len(want)
        self.assertEqual(n, len(t))
        rows = c["caiso_break"]["rows"]
        self.assertEqual(rows[0]["year"], 2025)
        earlier = [r["ratio"] for r in rows[1:]]
        self.assertTrue(min(earlier) <= rows[0]["ratio"] <= max(earlier))           # 2025's ratio is inside the earlier years' range


class ThePage(unittest.TestCase):
    def test_the_choices_the_ranking_and_the_cells(self):
        d = node("import fs from 'node:fs'; import * as g from './lib/demandgrowth.ts'; const f = JSON.parse(fs.readFileSync('./data/demand_growth.json', 'utf-8'));"
                 "const c0 = g.choices({}), c1 = g.choices({area:'caiso', rank:'peak'}), c2 = g.choices({area:'mars', rank:'x'}); const a = f.areas.ERCO;"
                 "const cs = g.cells(f, a), ex = g.extremes(cs), r = g.ranking(f, g.RANKS[0]), rp = g.ranking(f, g.RANKS[1]);"
                 "console.log(JSON.stringify({c: [[c0.ba, c0.rank.slug], [c1.ba, c1.rank.slug], [c2.ba, c2.rank.slug]], href: g.href('pjm', 'ytd'), years: g.wholeYears(a).map((y) => y.year),"
                 "ytd: g.yearToDate(f, a).year, n: cs.length, ex, r: r.map((x) => [x.ba, x.value]), lastPeak: rp.at(-1).ba, bm: g.byMonth(f, a).length, bh: g.byHour(f, a).length,"
                 "when: g.localHour('2025-08-18T22:00:00Z', a.tz), s: [g.signed(27.22), g.signed(-2.73), g.whole(55717.2)], slug: g.slugOf('SWPP')}));")
        self.assertEqual(d["c"], [["ERCO", "avg"], ["CISO", "peak"], ["ERCO", "avg"]])
        self.assertEqual(d["href"], "/demand?area=pjm&rank=ytd")
        self.assertEqual(d["years"], ["2019", "2020", "2021", "2022", "2023", "2024", "2025"])
        self.assertEqual(d["ytd"], "2026")
        r = copy()["areas"]["ERCO"]["years"]["2025"]
        cells = {k: v for k, v in r.items() if k.startswith("growth_pct_m") and "_h" in k}
        self.assertEqual(d["n"], len(cells))
        best = max(cells, key=cells.get)
        self.assertEqual((d["ex"]["most"]["month"], d["ex"]["most"]["hour"], d["ex"]["most"]["pct"]), (int(best[12:14]), int(best[16:18]), cells[best]))
        values = [v for _, v in d["r"]]
        self.assertEqual(values, sorted(values, reverse=True))
        self.assertEqual(d["r"][0][0], "ERCO")
        self.assertEqual(d["lastPeak"], "US48")                                      # the Lower 48 has no peak: it goes last in that ranking
        self.assertEqual((d["bm"], d["bh"]), (12, 24))
        self.assertEqual(d["when"], "18 August 2025, 17:00")
        self.assertEqual(d["s"], ["+27.22", "-2.73", "55,717"])
        self.assertEqual(d["slug"], "spp")

    def test_the_page_is_in_review_says_weather_is_not_removed_and_reads_its_own_copy(self):
        d = node("import { statusOf } from './lib/release.ts'; console.log(JSON.stringify([statusOf('/demand'), statusOf('/data/methods/demand_growth')]));")
        self.assertEqual(d, ["review", "review"])
        page = src("site", "app", "demand", "page.tsx")
        self.assertNotIn("supabase", page)
        self.assertIn("robots: { index: false, follow: false }", page)
        self.assertIn("Weather is not removed.", page)

    def test_every_number_on_the_built_page_where_a_site_is_served(self):
        base = os.environ.get("ERW_SITE_URL")
        exe = shutil.which("node")
        if not base or not exe:
            self.skipTest("ERW_SITE_URL names no served site (or node is absent): node site/scripts/check-demand.mjs <base>")
        r = subprocess.run([exe, "--import", "./scripts/alias-loader.mjs", "scripts/check-demand.mjs", base], cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "derived", "demand_growth.py"), ("docs", "methods", "demand_growth.md"), ("site", "lib", "demandgrowth.ts"),
                      ("site", "app", "demand", "page.tsx"), ("site", "scripts", "check-demand.mjs"), ("tests", "test_session97.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
