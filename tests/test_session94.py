"""Session 94: the energy mix, version 2 (any grid, any month or year, two grids side by side, the records), in review.

Energy Research Warehouse (ERW). The builder of the two derived tables (warehouse/derived/mix_profile.py) on hours made
here and on the tables as built; the site's copy against the tables, figure for figure; the page's pure part
(site/lib/mix2.ts), run by node; and that the page is in review and /mix is as it was. Every number the page shows
against the site's copy is site/scripts/check-mix-v2.mjs, which runs here when ERW_SITE_URL names a built site.

    python -m unittest tests.test_session94 -v
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
import mix_profile as mp  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
MIX = os.path.join(SITE, "data", "mix")


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


def hours(start, n, tz="America/Chicago", **over):
    """n hours from a local start: gas 600, wind 300, solar 100, the rest zero, storage blank; net generation their sum."""
    idx = pd.date_range(pd.Timestamp(start, tz=tz).tz_convert("UTC"), periods=n, freq="h")
    x = pd.DataFrame({"demand": 950.0, "net_generation": 1000.0, "interchange": 50.0, "natural_gas": 600.0, "coal": 0.0, "nuclear": 0.0,
                      "wind": 300.0, "solar": 100.0, "hydro": 0.0, "storage": np.nan, "other": 0.0}, index=idx)
    for k, v in over.items():
        x[k] = v
    x["side"] = "eia930"
    local = x.index.tz_convert(tz)
    x["day"], x["month"], x["hour"] = local.strftime("%Y-%m-%d"), local.strftime("%Y-%m"), local.hour
    return x


def copy(grid):
    with open(os.path.join(MIX, f"{grid}.json"), encoding="utf-8") as f:
        return json.load(f)


def table(name):
    path = os.path.join(OUT, f"{name}.csv")
    if not os.path.exists(path):
        raise unittest.SkipTest(f"{name} is not built on this machine")
    return pd.read_csv(path, comment="#", dtype={"x_period": str})


class TheHeldHour(unittest.TestCase):
    def test_a_blank_small_source_is_zero_and_a_blank_main_source_is_not(self):
        x = hours("2024-03-01", 48)
        x.iloc[5, x.columns.get_loc("natural_gas")] = np.nan      # a main source blank: 60 percent of the grid
        x.iloc[5, x.columns.get_loc("net_generation")] = 400.0    # and the total leaves it out too, as California's hydro
        tol, main = mp.flags(x, "ercot")
        self.assertEqual(tol, 0.05)
        self.assertEqual(main, ["natural_gas", "wind", "solar"])
        self.assertFalse(x["held"].iloc[5])
        self.assertTrue(x["held"].drop(x.index[5]).all())          # storage is blank in every hour and the hours are held

    def test_sources_off_the_total_by_more_than_the_tolerance_are_not_held(self):
        x = hours("2024-03-01", 24)
        x.iloc[3, x.columns.get_loc("other")] = 80.0               # 8 percent above the total, as Texas in December 2025
        x.iloc[4, x.columns.get_loc("other")] = 40.0               # 4 percent: held
        x.iloc[6, x.columns.get_loc("net_generation")] = np.nan
        x.iloc[7, x.columns.get_loc("net_generation")] = -5.0
        mp.flags(x, "ercot")
        self.assertEqual(list(x["held"].iloc[[3, 4, 6, 7]]), [False, True, False, False])

    def test_pjm_is_allowed_15_percent_and_no_more(self):
        x = hours("2024-03-01", 24, tz="America/New_York")
        x.iloc[3, x.columns.get_loc("other")] = 80.0
        x.iloc[4, x.columns.get_loc("other")] = 200.0
        tol, _ = mp.flags(x, "pjm")
        self.assertEqual(tol, 0.15)
        self.assertEqual(list(x["held"].iloc[[3, 4]]), [True, False])


class TheMonth(unittest.TestCase):
    def rows(self, x, grid="ercot", join_month=None):
        mp.flags(x, grid)
        return pd.DataFrame(mp.profile_rows(grid, x, "2026-10-04T00:00:00Z", join_month))

    def test_the_average_day_the_shares_and_the_days(self):
        x = hours("2024-04-01", 30 * 24)
        x.loc[x["hour"] == 12, "solar"] = 400.0
        x.loc[x["hour"] == 12, "net_generation"] = 1300.0
        r = self.rows(x).set_index("variable")["value"]
        self.assertEqual(r["days_held"], 30)
        self.assertEqual(r["days_in_month"], 30)
        self.assertEqual(r["avg_solar_mw_h12"], 400.0)
        self.assertEqual(r["avg_solar_mw_h11"], 100.0)
        self.assertEqual(r["avg_storage_mw_h00"], 0.0)             # blank in a held hour counts as zero
        self.assertEqual(r["solar_mwh"], 30 * (23 * 100 + 400))
        whole = 30 * (24 * 900 + 23 * 100 + 400)
        self.assertEqual(r["solar_share_pct"], round(100 * 30 * (23 * 100 + 400) / whole, 2))
        self.assertAlmostEqual(sum(r[f"{s}_share_pct"] for s in mp.SOURCES), 100, places=1)

    def test_a_month_with_too_few_complete_days_is_not_written(self):
        x = hours("2024-04-01", 30 * 24)
        for d in ("2024-04-03", "2024-04-09", "2024-04-15"):       # three days of 30 lose an hour: 27 complete, 90 percent
            x.loc[(x["day"] == d) & (x["hour"] == 7), "net_generation"] = np.nan
        r = self.rows(x.copy())
        self.assertEqual(r.set_index("variable")["value"]["days_held"], 27)
        x.loc[(x["day"] == "2024-04-20") & (x["hour"] == 7), "net_generation"] = np.nan   # a fourth: 26, under 90 percent
        self.assertEqual(len(self.rows(x)), 0)

    def test_the_day_the_clocks_change_is_complete_at_23_hours(self):
        x = hours("2024-03-01", 31 * 24 - 1)                       # March 2024 in Chicago has 743 hours
        r = self.rows(x).set_index("variable")["value"]
        self.assertEqual(r["days_held"], 31)

    def test_the_month_of_the_join_is_not_written(self):
        x = hours("2025-12-01", 31 * 24, tz="America/Los_Angeles")
        self.assertEqual(len(self.rows(x.copy(), "caiso", "2025-12")), 0)
        self.assertGreater(len(self.rows(x, "caiso", None)), 0)


class TheRecords(unittest.TestCase):
    def test_a_share_is_of_what_the_sources_put_out_and_a_partial_report_is_not_ranked(self):
        x = hours("2024-04-01", 3 * 24)
        mid = x.index[12]
        x.loc[mid, ["solar", "storage", "net_generation", "demand"]] = [900.0, -400.0, 1400.0, 1350.0]   # batteries charging at midday
        odd = x.index[30]
        x.loc[odd, ["natural_gas", "wind", "solar", "net_generation", "demand"]] = [0.0, 50.0, 0.0, 50.0, 950.0]  # only its wind reported
        mp.flags(x, "ercot")
        ci = pd.Series(400.0, index=x.index)
        ci[mid] = 150.0
        r = pd.DataFrame(mp.record_rows("ercot", x, ci, "2026-10-04T00:00:00Z"))
        a = r[r["x_period"] == "all"].set_index("variable")
        self.assertEqual(a.loc["solar_share_max_pct", "value"], 50.0)         # 900 of 1,800 put out; against net generation it would be 64
        self.assertEqual(a.loc["solar_share_max_pct", "ts_utc"], mid.strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.assertLess(a.loc["wind_share_max_pct", "value"], 100)            # the partial hour, wind at 100 percent, is not the record
        self.assertEqual(a.loc["cleanest_hour_kgco2_per_mwh", "value"], 150.0)
        self.assertIn("year_solar_share_max_pct", set(r["variable"]))

    def test_the_records_as_built(self):
        r = table(mp.RECORDS)
        share = r[r["variable"].str.contains("share_max_pct")]
        self.assertTrue(((share["value"] > 0) & (share["value"] <= 100)).all())
        self.assertEqual(sorted(r["entity"].unique()), sorted(f"iso:{g}" for g in mp.GRIDS))
        self.assertFalse(r.duplicated(["entity", "variable", "x_period"]).any())
        ny = r[(r["entity"] == "iso:nyiso") & (r["x_period"] == "all")]
        self.assertNotIn("solar_share_max_pct", set(ny["variable"]))          # EIA reports no solar for New York: no record of zero
        ca = r[(r["entity"] == "iso:caiso") & (r["x_period"] == "all")].set_index("variable")
        for v in ca.index:                                                     # California's side follows the join
            self.assertEqual(ca.loc[v, "x_side"], "caiso" if ca.loc[v, "ts_utc"] >= mp.cj.JOIN else "eia930", v)


class TheTablesAsBuilt(unittest.TestCase):
    def test_what_each_grid_holds_and_what_it_does_not(self):
        p = table(mp.PROFILE)
        held = {e[4:]: set(g["ts_utc"].str[:7]) for e, g in p[p["variable"] == "days_held"].groupby("entity")}
        self.assertEqual(set(held), set(mp.GRIDS))
        ca = held["caiso"]
        for m in ("2019-10", "2019-11", "2020-01", "2020-05", "2020-08", "2025-12"):   # no hydro in EIA's file; the join month
            self.assertNotIn(m, ca)
        for m in ("2019-08", "2020-09", "2021-01", "2025-11", "2026-01"):
            self.assertIn(m, ca)
        self.assertNotIn("2025-12", held["ercot"])                                     # EIA's "other" repeats the batteries
        self.assertGreaterEqual(len(held["pjm"]), 90)
        d = p[p["variable"].isin(["days_held", "days_in_month"])].pivot_table(index=["entity", "ts_utc"], columns="variable", values="value")
        self.assertTrue((d["days_held"] >= mp.NEAR * d["days_in_month"]).all())
        self.assertTrue((d["days_held"] <= d["days_in_month"]).all())
        sides = p[p["entity"] == "iso:caiso"].groupby(p["ts_utc"].str[:7])["source"].agg(set)
        for m, s in sides.items():
            self.assertEqual(s, {mp.SOURCE_JOIN if m > "2025-12" else mp.SOURCE}, m)
        self.assertTrue((p[p["entity"] != "iso:caiso"]["source"] == mp.SOURCE).all())

    def test_the_shares_of_a_month_sum_to_100_and_are_its_mwh(self):
        p = table(mp.PROFILE)
        m = p[(p["entity"] == "iso:ercot") & (p["ts_utc"] == "2026-04-01T00:00:00Z")].set_index("variable")["value"]
        whole = sum(m[f"{s}_mwh"] for s in mp.SOURCES)
        for s in mp.SOURCES:
            self.assertAlmostEqual(m[f"{s}_share_pct"], 100 * m[f"{s}_mwh"] / whole, places=2)
        self.assertAlmostEqual(sum(m[f"avg_solar_mw_h{h:02d}"] for h in range(24)) * m["days_held"], m["solar_mwh"], delta=0.05 * 24 * m["days_held"] + 1)


class TheSitesCopy(unittest.TestCase):
    def test_every_figure_of_the_copy_is_the_tables(self):
        p, r = table(mp.PROFILE), table(mp.RECORDS)
        for grid in mp.GRIDS:
            f = copy(grid)
            rows = p[p["entity"] == f"iso:{grid}"]
            self.assertEqual(sorted(f["months"]), sorted(rows["ts_utc"].str[:7].unique()), grid)
            n = 0
            for row in rows.itertuples():
                m = f["months"][row.ts_utc[:7]]
                if row.variable.startswith("avg_"):
                    got = m["avg"][row.variable[4:-7]][int(row.variable[-2:])]
                else:
                    got = m[row.variable]
                self.assertEqual(got, row.value, (grid, row.ts_utc, row.variable))
                n += 1
            held = sum(sum(v is not None for a in m["avg"].values() for v in a) + sum(1 for k in m if k not in ("avg", "side")) for m in f["months"].values())
            self.assertEqual(held, n, grid)                                    # and the copy holds nothing the table does not
            rec = r[r["entity"] == f"iso:{grid}"]
            self.assertEqual(len(f["records"]), len(rec))
            by = {(x["variable"], x["period"]): x for x in f["records"]}
            for row in rec.itertuples():
                x = by[(row.variable, row.x_period)]
                self.assertEqual((x["value"], x["ts_utc"], x["side"]), (row.value, row.ts_utc, row.x_side))

    def test_a_year_is_its_months_weighted_by_their_days(self):
        f = copy("ercot")
        y = f["years"]["2024"]
        ms = [f["months"][f"2024-{m:02d}"] for m in range(1, 13)]
        days = sum(m["days_held"] for m in ms)
        self.assertEqual((y["months"], y["months_due"], y["days_held"]), (12, 12, days))
        self.assertAlmostEqual(y["avg"]["solar"][13], sum(m["avg"]["solar"][13] * m["days_held"] for m in ms) / days, delta=0.06)
        whole = sum(m[f"{s}_mwh"] for m in ms for s in mp.SOURCES)
        self.assertAlmostEqual(y["wind_share_pct"], 100 * sum(m["wind_mwh"] for m in ms) / whole, places=2)

    def test_a_year_is_given_only_when_at_most_one_month_is_missing(self):
        m = {"avg": {k: [1.0] * 24 for k in mp.SOURCES + ["demand", "net_generation"]}, "side": "eia930", "days_held": 30, "net_generation_mwh": 8.0,
             **{f"{s}_mwh": 1.0 for s in mp.SOURCES}}
        months = {f"2024-{i:02d}": dict(m) for i in range(1, 13)}
        self.assertEqual(mp.year_of(months, "2024", "2026-09")["months"], 12)
        del months["2024-03"]
        y = mp.year_of(months, "2024", "2026-09")
        self.assertEqual((y["months"], y["missing"]), (11, ["2024-03"]))
        del months["2024-07"]
        self.assertIsNone(mp.year_of(months, "2024", "2026-09"))
        part = {f"2026-{i:02d}": dict(m) for i in range(1, 10)}
        self.assertEqual(mp.year_of(part, "2026", "2026-09")["months_due"], 9)     # the year so far
        ca = copy("caiso")
        self.assertNotIn("2019", ca["years"])
        self.assertNotIn("2020", ca["years"])
        self.assertEqual(ca["years"]["2025"]["missing"], ["2025-12"])
        self.assertEqual((ca["years"]["2025"]["side"], ca["years"]["2026"]["side"]), ("eia930", "caiso"))


class ThePage(unittest.TestCase):
    FILES = ("import fs from 'node:fs'; import * as m from './lib/mix2.ts';"
             "const F = Object.fromEntries(m.GRIDS.map((g) => [g.slug, JSON.parse(fs.readFileSync(`./data/mix/${g.slug}.json`, 'utf-8'))]));")

    def test_the_choices_from_an_address(self):
        d = node(self.FILES + "console.log(JSON.stringify([m.choices({}, F), m.choices({grid:'caiso', period:'2026-04', vs:'ercot'}, F),"
                 "m.choices({grid:'caiso', period:'2019-11', vs:'caiso', cal:'13'}, F), m.choices({grid:'pjm', period:'2024'}, F), m.choices({grid:'nowhere', period:'x', cal:'07'}, F),"
                 "m.href({grid:'caiso', period:'2026-04', vs:'ercot'}), m.href({grid:'pjm'})]));")
        latest = sorted(copy("ercot")["months"])[-1]
        self.assertEqual(d[0], {"grid": "ercot", "vs": None, "period": latest, "cal": latest[5:]})
        self.assertEqual(d[1], {"grid": "caiso", "vs": "ercot", "period": "2026-04", "cal": "04"})
        ca_latest = sorted(copy("caiso")["months"])[-1]
        self.assertEqual(d[2], {"grid": "caiso", "vs": None, "period": ca_latest, "cal": ca_latest[5:]})   # a month not held, itself as the second grid, a 13th month
        self.assertEqual(d[3], {"grid": "pjm", "vs": None, "period": "2024", "cal": "04"})
        self.assertEqual((d[4]["grid"], d[4]["cal"]), ("ercot", "07"))
        self.assertEqual(d[5], "/mix/v2?grid=caiso&period=2026-04&vs=ercot")
        self.assertEqual(d[6], "/mix/v2?grid=pjm")

    def test_the_stack_net_load_and_the_months_across_years(self):
        d = node(self.FILES + "const p = F.caiso.months['2026-04']; const s = m.stack(p); const n = m.netLoad(p); const a = m.acrossYears(F.caiso, '04');"
                 "console.log(JSON.stringify({up: s.up.map((b) => b.key), down: s.down.map((b) => b.key), hi: s.hi, lo: s.lo, top13: s.up.at(-1).upper[13], n13: n[13],"
                 "years: a.map((x) => x.year), last: a.at(-1), miss: m.missingMonths(F.caiso), missE: m.missingMonths(F.ercot), sh: m.shares(p).map((x) => x.key),"
                 "when: m.localHour('2026-04-29T18:00:00Z', F.caiso.tz), names: [m.periodName('2026-04'), m.periodName('2025'), m.sideName('caiso')]}));")
        p = copy("caiso")["months"]["2026-04"]
        avg = p["avg"]
        order = ["nuclear", "coal", "natural_gas", "hydro", "other", "wind", "solar", "storage"]
        self.assertEqual(d["down"], [k for k in order if min(avg[k]) < 0])  # batteries charging, and solar's own use at night
        self.assertEqual(d["up"], [k for k in order if max(avg[k]) > 0])
        self.assertAlmostEqual(d["top13"], sum(max(0.0, avg[k][13]) for k in mp.SOURCES), places=3)
        self.assertAlmostEqual(d["n13"], avg["demand"][13] - avg["wind"][13] - avg["solar"][13], places=1)
        self.assertEqual(d["years"][-1], "2026")
        self.assertNotIn("2020", d["years"])                               # April 2020 is not held for California
        last = d["last"]
        net = [avg["demand"][h] - avg["wind"][h] - avg["solar"][h] for h in range(24)]
        self.assertAlmostEqual(last["low"]["value"], min(net[9:17]), places=1)
        self.assertAlmostEqual(last["evening"]["value"], max(net[16:24]), places=1)
        self.assertAlmostEqual(last["ramp"], max(net[16:24]) - min(net[9:17]), places=1)
        self.assertEqual(last["side"], "caiso")
        self.assertIn("2025-12", d["miss"])
        self.assertIn("2019-11", d["miss"])
        self.assertEqual(d["missE"], ["2025-12"])
        self.assertEqual(d["sh"][0], max(mp.SOURCES, key=lambda s: p[f"{s}_share_pct"]))
        self.assertEqual(d["when"], "29 April 2026, 11:00")
        self.assertEqual(d["names"], ["April 2026", "2025", "CAISO's own data"])

    def test_the_page_is_in_review_and_the_old_page_is_as_it_was(self):
        d = node("import { statusOf } from './lib/release.ts'; console.log(JSON.stringify([statusOf('/mix'), statusOf('/mix/v2'), statusOf('/data/methods/generation_mix_hourly')]));")
        self.assertEqual(d, ["review", "review", "review"])
        page = src("site", "app", "_retired", "mix-v2", "page.tsx")   # session 133: retired, kept unrouted; its address redirects to /mix
        self.assertNotIn("supabase", page)                                 # the page reads the site's own copy, not the database
        self.assertIn("robots: { index: false, follow: false }", page)
        # session 94 left the first version of the page as it was and checked that against origin/main. Session 118 was
        # asked to change that page (it no longer draws EIA's California generation after the join), so the check is
        # now of what session 94 meant: the first version is still there, still the first version, and still in review
        old = src("site", "app", "_retired", "mix-original", "page.tsx")   # session 133: the first version, kept unrouted; /mix is now the one page
        self.assertIn('const MONTHLY = "state_generation_mix_monthly";', old)
        self.assertIn('const LATEST = "eia930_generation_latest";', old)
        self.assertNotIn("generation_mix_hourly_profile", old)               # the second version's table is not read by the first

    def test_every_number_on_the_built_page_where_a_site_is_served(self):
        base = os.environ.get("ERW_SITE_URL")
        exe = shutil.which("node")
        if not base or not exe:
            self.skipTest("ERW_SITE_URL names no served site (or node is absent): node site/scripts/check-mix-v2.mjs <base>")
        r = subprocess.run([exe, "scripts/check-mix-v2.mjs", base], cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "derived", "mix_profile.py"), ("docs", "methods", "generation_mix_hourly.md"), ("site", "lib", "mix2.ts"),
                      ("site", "app", "_retired", "mix-v2", "page.tsx"), ("site", "app", "_retired", "mix-v2", "data.ts"), ("site", "scripts", "check-mix-v2.mjs"),
                      ("tests", "test_session94.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
