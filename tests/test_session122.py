"""Session 122: how clean, and when (/mix/clean, in review).

Energy Research Warehouse (ERW). No request leaves the machine. The arithmetic of warehouse/derived/mix_clean.py on
small frames made for the tests (round numbers, shown nowhere: they test the sums, not the data), the two tables and
the site's copy where they are on this machine, and the page's words.

    python -m unittest tests.test_session122 -v
"""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("ERW_LOCK_EXEMPT", "1")
for p in ("warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import iso_prices as ip  # noqa: E402
import mix_clean as mc  # noqa: E402
import mix_profile as mp  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SITE = os.path.join(ROOT, "site", "data", "clean")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def hours(n=48, start="2024-06-01T05:00:00Z", **cols):
    """A frame of n hours in the shape mix_profile.hours_of gives, every source at the given constant or list."""
    idx = pd.date_range(start, periods=n, freq="h", tz="UTC")
    x = pd.DataFrame(index=idx)
    base = dict(natural_gas=500.0, coal=100.0, nuclear=200.0, wind=100.0, solar=0.0, hydro=50.0, storage=0.0, other=50.0)
    base.update(cols)
    for k, v in base.items():
        x[k] = v
    x["net_generation"] = x[mp.SOURCES].sum(axis=1)
    x["demand"] = x["net_generation"]
    x["interchange"] = 0.0
    x["side"] = "eia930"
    x["held"] = True
    local = idx.tz_convert("America/Chicago")
    x["day"], x["month"], x["hour"] = local.strftime("%Y-%m-%d"), local.strftime("%Y-%m"), local.hour
    return x


class TheShare(unittest.TestCase):
    def test_carbon_free_is_nuclear_wind_solar_and_hydro_over_the_seven_sources(self):
        x = mc.clean_hours(hours())
        self.assertEqual(mc.CLEAN, ["nuclear", "wind", "solar", "hydro"])
        self.assertEqual(x["generation"].iloc[0], 1000.0)
        self.assertEqual(x["carbon_free"].iloc[0], 350.0)
        self.assertEqual(x["share"].iloc[0], 35.0)

    def test_storage_is_not_a_source_and_a_source_below_zero_adds_nothing(self):
        x = mc.clean_hours(hours(storage=300.0, solar=-5.0))
        self.assertEqual(x["generation"].iloc[0], 1000.0)          # the battery's 300 is not generation; the solar farm's own use is not negative generation
        self.assertEqual(x["share"].iloc[0], 35.0)

    def test_other_is_not_carbon_free(self):
        a, b = mc.clean_hours(hours(other=50.0)), mc.clean_hours(hours(other=550.0))
        self.assertLess(b["share"].iloc[0], a["share"].iloc[0])
        self.assertIn("other", mc.DIRTY)

    def test_an_impossible_hour_of_net_generation_is_not_held(self):
        x = hours()
        x.iloc[10, x.columns.get_loc("net_generation")] = 9_000_000.0     # the unadjusted value EIA's file sometimes holds
        got = mc.clean_hours(x)
        self.assertFalse(got["held"].iloc[10])
        self.assertTrue(got["held"].iloc[9] and got["held"].iloc[11])

    def test_caisos_own_hours_are_not_put_to_the_rule_for_eias_totals(self):
        x = hours()
        x["side"] = "caiso"
        x.iloc[10, x.columns.get_loc("net_generation")] = 9_000_000.0
        self.assertTrue(mc.clean_hours(x)["held"].iloc[10])


class NuclearUnderAnotherName(unittest.TestCase):
    def frame(self):
        x = hours(n=400)
        return x

    def test_nuclear_at_nothing_with_other_up_by_as_much_is_not_held(self):
        x = self.frame()
        x.iloc[100:150, x.columns.get_loc("nuclear")] = 0.0
        x.iloc[100:150, x.columns.get_loc("other")] = 250.0            # 50 as usual, and the reactors' 200
        wrong = mc.misnamed_nuclear(x)
        self.assertEqual(int(wrong.sum()), 50)
        self.assertEqual(int(mc.clean_hours(x)["held"].sum()), 350)

    def test_a_fleet_that_is_truly_off_is_kept(self):
        x = self.frame()
        x.iloc[100:150, x.columns.get_loc("nuclear")] = 0.0            # "other" where it was: the plants are off
        self.assertEqual(int(mc.misnamed_nuclear(x).sum()), 0)
        self.assertEqual(float(mc.clean_hours(x)["share"].iloc[120]), 100.0 * 150.0 / 800.0)

    def test_it_is_not_asked_of_a_grid_where_nuclear_is_not_a_main_source(self):
        x = hours(n=400, nuclear=10.0, natural_gas=690.0)              # 1 percent of generation
        x.iloc[100:150, x.columns.get_loc("nuclear")] = 0.0
        x.iloc[100:150, x.columns.get_loc("other")] = 900.0
        self.assertEqual(int(mc.misnamed_nuclear(x).sum()), 0)


class TheShift(unittest.TestCase):
    def test_the_days_energy_is_unchanged(self):
        for n, hrs in ((24, list(range(24))), (23, [0, 1] + list(range(3, 24))), (25, [0, 1, 1] + list(range(2, 24)))):
            for s in (0.1, 0.2):
                load = mc.shifted(hrs, [10, 11, 12, 13], s)
                self.assertAlmostEqual(load.sum(), n, places=9, msg=f"{n} hours, {s}")
        load = mc.shifted(list(range(24)), [10, 11, 12, 13], 0.2)
        self.assertAlmostEqual(load[0], 0.8)
        self.assertAlmostEqual(load[10], 0.8 + 0.2 * 24 / 4)
        self.assertIsNone(mc.shifted([0, 1, 2], [10, 11], 0.1))

    def test_moving_load_into_a_clean_hour_lowers_carbon_by_what_the_sum_says(self):
        x = hours(n=24)
        x["hour"] = range(24)
        x["day"] = "2024-06-01"
        x["v"] = [400.0] * 24
        x.loc[x["hour"].isin([10, 11, 12, 13]), "v"] = 100.0
        f = mc.shift_figures(x, [10, 11, 12, 13], "v")
        flat = (20 * 400 + 4 * 100)
        self.assertEqual((f["flat"], f["energy"], f["days"]), (flat, 24.0, 1))
        self.assertAlmostEqual(f["shift10"], 0.9 * flat + 0.1 * 24 * 100.0)      # a tenth of the day's 24 MWh now at 100
        self.assertAlmostEqual(f["shift20"], 0.8 * flat + 0.2 * 24 * 100.0)

    def test_a_day_with_an_hour_missing_the_figure_does_not_count(self):
        x = hours(n=48)
        x["v"] = 300.0
        x.iloc[5, x.columns.get_loc("v")] = np.nan
        f = mc.shift_figures(x, [10, 11, 12, 13], "v")
        days = x.groupby("day").size()
        whole = [d for d, n in days.items() if not x[x["day"] == d]["v"].isna().any()]
        self.assertEqual(f["days"], len(whole))
        self.assertEqual(mc.shift_figures(x.assign(v=np.nan), [10], "v"), {})


class TheMatching(unittest.TestCase):
    def test_a_flat_supply_bought_at_a_hundred_percent_covers_everything_and_half_covers_half(self):
        y = mc.clean_hours(hours(n=100))
        self.assertEqual(mc.matching(y, "mix", 100), (100.0, 100.0))
        e, h = mc.matching(y, "mix", 50)
        self.assertAlmostEqual(e, 50.0)
        self.assertEqual(h, 0.0)

    def test_a_supply_that_runs_half_the_hours_covers_half_the_energy_whatever_is_bought(self):
        y = mc.clean_hours(hours(n=100, solar=[1000.0, 0.0] * 50))
        e100, h100 = mc.matching(y, "solar", 100)
        e150, _ = mc.matching(y, "solar", 150)
        self.assertAlmostEqual(e100, 50.0)
        self.assertAlmostEqual(h100, 50.0)
        self.assertAlmostEqual(e150, 50.0)                                 # the surplus of the sunny hours is not counted and not stored
        self.assertIsNone(mc.matching(mc.clean_hours(hours(n=10)), "solar", 100))   # a grid with no solar has no solar shape


class TheTables(unittest.TestCase):
    """The two tables and the site's copy, where they are on this machine."""

    def table(self, name):
        path = os.path.join(OUT, name + ".csv")
        if not os.path.exists(path):
            raise unittest.SkipTest(f"{name} is not on this machine")
        return pd.read_csv(path, skiprows=ip.header_rows(path))

    def test_a_share_is_between_nothing_and_everything_and_the_two_sums_give_it(self):
        h = self.table(mc.HOURLY)
        self.assertTrue(h["value"].between(0, 100).all())
        self.assertLess((100 * h["x_carbon_free_mwh"] / h["x_generation_mwh"] - h["value"]).abs().max(), 0.06)   # the sums are written to one decimal
        self.assertEqual(set(h["x_side"]), {"eia930", "caiso"})
        self.assertEqual(set(h[h["x_side"] == "caiso"]["entity"]), {"iso:caiso"})
        self.assertFalse(h.duplicated(["entity", "ts_utc"]).any())

    def test_californias_hydro_gap_is_in_no_figure(self):
        import impossible_hours as ih
        h = self.table(mc.HOURLY)
        c = h[h["entity"] == "iso:caiso"]
        self.assertEqual(int(ih.in_hydro_gap(c["ts_utc"]).sum()), 0)
        s = self.table(mc.SUMMARY)
        months = set(s[(s["entity"] == "iso:caiso") & (s["variable"] == "carbon_free_share_pct")]["ts_utc"].str[:7])
        self.assertFalse(months & {f"2020-{m:02d}" for m in range(1, 8)})
        import caiso_join as cj
        join_month = pd.Timestamp(cj.JOIN).tz_convert("America/Los_Angeles").strftime("%Y-%m")
        self.assertNotIn(join_month, months)                              # a month is never built on both sources

    def test_a_month_and_a_year_never_share_a_key_and_a_year_adds_up(self):
        s = self.table(mc.SUMMARY)
        self.assertFalse(s.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(set(s[s["variable"].str.startswith("year_")]["freq"]), {"P1Y"})
        self.assertEqual(set(s[~s["variable"].str.startswith("year_")]["freq"]), {"P1M"})
        y = s[s["variable"].str.startswith("year_")].pivot(index=["entity", "ts_utc"], columns="variable", values="value")
        self.assertTrue((y["year_months_due"] - y["year_months"] <= 1).all())
        for p in mc.PURCHASES:                                            # what is met in its own hour is never more than what was bought, or than the load
            e = y[f"year_match_mix_{p}_energy_pct"].dropna()
            self.assertTrue((e <= min(p, 100) + 1e-6).all(), p)
        self.assertTrue((y["year_match_mix_150_energy_pct"] >= y["year_match_mix_100_energy_pct"]).all())
        self.assertTrue((y["year_hours_cf_ge90_pct"] <= y["year_hours_cf_ge75_pct"]).all() and (y["year_hours_cf_ge75_pct"] <= y["year_hours_cf_ge50_pct"]).all())
        self.assertTrue((y["year_shift20_carbon_change_pct"].dropna() <= 0.5).all())    # the cleanest hours of the month are not dirtier than its average day

    def test_no_cost_for_pjm_or_miso_and_none_before_a_price_is_held(self):
        s = self.table(mc.SUMMARY)
        cost = s[s["variable"].str.contains("cost")]
        self.assertFalse(set(cost["entity"]) & {"iso:pjm", "iso:miso"})
        self.assertEqual(set(mc.NO_PRICE), {"pjm", "miso"})
        first = cost[cost["variable"] == "flat_cost_usd_per_mwh"].groupby("entity")["ts_utc"].min()
        self.assertEqual(first["iso:ercot"][:4], "2019")
        for g in ("iso:caiso", "iso:isone", "iso:nyiso", "iso:spp"):
            self.assertGreaterEqual(first[g][:7], "2024-09", g)

    def test_the_sites_copy_is_the_table(self):
        s = self.table(mc.SUMMARY)
        for grid in mp.GRIDS:
            p = os.path.join(SITE, f"{grid}.json")
            if not os.path.exists(p):
                raise unittest.SkipTest("the site's copy is not on this machine")
            f = json.load(open(p, encoding="utf-8"))
            g = s[s["entity"] == f"iso:{grid}"]
            n = 0
            for r in g.itertuples():
                if r.variable.startswith("year_"):
                    got = f["years"][r.ts_utc[:4]][r.variable[5:]]
                elif r.variable.startswith("cf_share_pct_h"):
                    got = f["months"][r.ts_utc[:7]]["day"][int(r.variable[-2:])]
                else:
                    got = f["months"][r.ts_utc[:7]][r.variable]
                self.assertEqual(got, r.value, f"{grid} {r.variable} {r.ts_utc}")
                n += 1
            self.assertEqual(n, sum(len(v) + (23 if "day" in v else 0) for v in f["months"].values()) + sum(len(v) for v in f["years"].values()), grid)


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module"], input=js, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, encoding="utf-8")
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class ThePage(unittest.TestCase):
    def test_it_is_in_review_with_its_method_and_no_live_page_knows_of_it(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/mix/clean": "review"', rel)
        routes = src("site", "scripts", "check-routes.mjs")
        self.assertIn('"/mix/clean"', routes)
        self.assertIn('"/data/methods/clean_energy"', routes)
        for f in ("site/app/page.tsx", "site/app/storage/page.tsx", "site/app/network/page.tsx", "site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/seller/page.tsx"):
            if os.path.exists(os.path.join(ROOT, *f.split("/"))):
                self.assertNotIn("mix/clean", src(*f.split("/")), f)

    def test_it_says_first_what_the_figures_are(self):
        page = src("site", "app", "mix", "clean", "page.tsx")
        lead = page[page.index('data-clean-what="1"'):page.index("<div className=\"grid gap-8")]
        for words in ("not what the grid&apos;s customers used", "imported power is not in it", "the average of the hour&apos;s generation, not the marginal plant&apos;s"):
            self.assertIn(words, lead)
        self.assertLess(page.index('data-clean-what="1"'), page.index("data-clean-summary"))
        for words in ("California is two series, not one.", "data-clean-nuclear", "data-clean-no-price", "not a forecast", "known only afterwards"):
            self.assertIn(words, page)

    def test_no_figure_is_written_into_the_page(self):
        page = re.sub(r"^\s*//.*$", "", src("site", "app", "mix", "clean", "page.tsx"), flags=re.M)
        self.assertIsNone(re.search(r">\s*-?\d+\.\d+\s*<", page))
        self.assertEqual(re.findall(r"\b\d+(?:\.\d+)? percent of (?:its|the load)", page), [])
        self.assertNotIn("2025-12-16", page)                               # the join's date has one home (tests/test_session78.py)
        self.assertNotIn("2025-12-16", src("warehouse", "derived", "mix_clean.py"))

    def test_the_library_picks_and_never_computes(self):
        p = os.path.join(SITE, "ercot.json")
        if not os.path.exists(p):
            raise unittest.SkipTest("the site's copy is not on this machine")
        f = json.load(open(p, encoding="utf-8"))
        r = node("""
import fs from "node:fs";
import { yearView, defaultYear, yearsOf, monthsOf, dayOf, cleanestOf, hoursName, sideOf, wholeYear, pct, signedPct, isGrid } from "./lib/clean.ts";
const f = JSON.parse(fs.readFileSync("data/clean/ercot.json", "utf8"));
const y = defaultYear(f);
const c = JSON.parse(fs.readFileSync("data/clean/caiso.json", "utf8"));
console.log(JSON.stringify({ y, years: yearsOf(f), v: yearView(f, y), months: monthsOf(f, y).length, day: dayOf(f, y + "-07"), top: cleanestOf(f, y + "-07"), whole: wholeYear(f, y),
  names: [hoursName([10, 11, 9, 12]), hoursName([23, 1]), hoursName([])], fmt: [pct(null), pct(45.84), signedPct(-2.09), signedPct(1.5), signedPct(null)], grids: [isGrid("ercot"), isGrid("nope")],
  sides: yearsOf(c).map((k) => sideOf(yearView(c, k))) }));
""")
        y = r["y"]
        self.assertTrue(r["whole"] and f["years"][y]["months"] == 12)
        self.assertEqual(r["v"]["share"], f["years"][y]["carbon_free_share_pct"])
        self.assertEqual(r["v"]["match"]["mix"]["100"]["energy"], f["years"][y]["match_mix_100_energy_pct"])
        self.assertEqual(r["v"]["carbon"]["change"]["20"], f["years"][y]["shift20_carbon_change_pct"])
        self.assertEqual(r["day"], f["months"][f"{y}-07"]["day"])
        self.assertEqual(r["top"], [f["months"][f"{y}-07"][f"cleanest_hour_{i}"] for i in (1, 2, 3, 4)])
        self.assertEqual(r["names"], ["09:00 to 13:00", "01:00, 23:00", "not held"])
        self.assertEqual(r["fmt"], ["not held", "45.8%", "-2.1%", "+1.5%", "not held"])
        self.assertEqual(r["grids"], [True, False])
        self.assertEqual(set(r["sides"]) - {"eia930", "caiso", "both"}, set())
        self.assertEqual(r["sides"][-1], "caiso")                           # California's newest year rests on CAISO's own data

    def test_no_em_dash_and_miso_is_still_paused(self):
        for parts in (("warehouse", "derived", "mix_clean.py"), ("docs", "methods", "clean_energy.md"), ("site", "app", "mix", "clean", "page.tsx"), ("site", "lib", "clean.ts"),
                      ("site", "app", "mix", "clean", "data.ts"), ("tests", "test_session122.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])
        self.assertIn("miso", src("warehouse", "metadata", "paused_sources.csv").lower())
        self.assertNotIn("requests", src("warehouse", "derived", "mix_clean.py").split('"""', 2)[2])   # the builder asks no one for anything


if __name__ == "__main__":
    unittest.main()
