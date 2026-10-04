"""Session 95: the interconnection queue explorer (/queues), in review.

Energy Research Warehouse (ERW). The builder of interconnection_queue_summary (warehouse/derived/queue_summary.py) on
requests made here and on the table as built, counted again from the file; the site's copy against the table; the
page's pure part (site/lib/queues.ts), run by node; and that the page is in review. Every number the page shows
against the site's copy is site/scripts/check-queues.mjs, which runs here when ERW_SITE_URL names a built site.

    python -m unittest tests.test_session95 -v
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import queue_summary as qs  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


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


def request(region="ERCOT", status="active", kind="Solar", mw=100.0, year=2015, q_date=None, on_date=None):
    return dict(region=region, status=status, type_clean=kind, capacity_mw=mw, q_year=year, q_date=q_date or (f"{int(year)}-03-01" if year else None), on_date=on_date)


def summary(reqs, last_year=2025):
    return qs.summarize(qs.prepared(pd.DataFrame(reqs)), last_year)


def table():
    path = os.path.join(OUT, f"{qs.NAME}.csv")
    if not os.path.exists(path) or not os.path.exists(os.path.join(OUT, f"{qs.INPUT}.csv")):
        raise unittest.SkipTest("the queue tables are not on this machine")
    return pd.read_csv(path, comment="#")


class TheSummary(unittest.TestCase):
    def test_the_technology_groups_keep_storage_and_solar_with_storage_apart(self):
        self.assertEqual([qs.tech_of(k) for k in ("Solar", "Solar+Battery", "Battery", "Wind", "Offshore Wind", "Gas", "Wind+Battery", "Hydro", "Other Storage", float("nan"))],
                         ["solar", "solar_battery", "battery", "wind", "offshore_wind", "gas", "other", "other", "other", "other"])
        s = summary([request(kind="Solar"), request(kind="Solar+Battery", mw=300), request(kind="Battery", mw=50), request(kind="Wind+Battery", region="PJM")])
        self.assertEqual(s[("ercot", "solar")]["whole"]["total_active_mw"], 100.0)
        self.assertEqual(s[("ercot", "solar_battery")]["whole"]["total_active_mw"], 300.0)
        self.assertEqual(s[("ercot", "battery")]["whole"]["total_active_mw"], 50.0)
        self.assertEqual(s[("ercot", "all")]["whole"]["total_active_mw"], 450.0)
        self.assertEqual(s[("pjm", "other")]["whole"]["total_requests"], 1)
        self.assertEqual(s[("us", "all")]["whole"]["total_requests"], 4)
        self.assertNotIn(("caiso", "all"), s)                                   # a view with no request has no row

    def test_a_year_entered_holds_each_status_and_a_request_with_no_year_is_in_no_year(self):
        s = summary([request(status="active", mw=100), request(status="suspended", mw=40), request(status="operating", mw=60), request(status="withdrawn", mw=500),
                     request(status="unknown", mw=7), request(status="active", mw=0), request(status="active", mw=-5), request(status="active", year=None, mw=900)])
        y = s[("ercot", "solar")]["years"][2015]
        self.assertEqual(y, {"requests_entered": 7, "mw_entered": 707.0, "requests_active": 3, "mw_active": 100.0, "requests_suspended": 1, "mw_suspended": 40.0,
                             "requests_operating": 1, "mw_operating": 60.0, "requests_withdrawn": 1, "mw_withdrawn": 500.0})
        w = s[("ercot", "solar")]["whole"]
        self.assertEqual((w["total_requests"], w["requests_without_year"], w["total_active_requests"], w["total_active_mw"]), (8, 1, 4, 1000.0))
        self.assertEqual((w["total_suspended_requests"], w["total_suspended_mw"]), (1, 40.0))

    def test_past_requests_are_2000_to_five_years_back_and_a_share_needs_twenty(self):
        reqs = [request(status="operating", year=2010) for _ in range(5)] + [request(status="withdrawn", year=2020, mw=300) for _ in range(12)] \
            + [request(status="active", year=2000) for _ in range(2)] + [request(status="suspended", year=2005)] \
            + [request(status="active", year=2021) for _ in range(30)] + [request(status="withdrawn", year=1999) for _ in range(30)] + [request(status="unknown", year=2012)]
        w = summary(reqs)[("ercot", "solar")]["whole"]
        self.assertEqual(w["past_requests"], 20)                                # 2021, 1999 and the unknown one are not past requests
        self.assertEqual((w["past_operating_share_pct"], w["past_withdrawn_share_pct"], w["past_open_share_pct"]), (25.0, 60.0, 15.0))
        self.assertEqual(w["past_mw"], 5 * 100 + 12 * 300 + 3 * 100)
        self.assertEqual(w["past_mw_withdrawn_share_pct"], round(100 * 3600 / 4400, 2))
        fewer = summary(reqs[1:])[("ercot", "solar")]["whole"]
        self.assertEqual(fewer["past_requests"], 19)
        self.assertNotIn("past_operating_share_pct", fewer)                     # 19: no share is written

    def test_the_median_wait_is_over_dated_requests_in_order_and_needs_five(self):
        built = [request(status="operating", year=2015, q_date="2015-01-01", on_date=f"{2016 + i}-01-01") for i in range(5)]       # 1 to 5 years
        odd = [request(status="operating", year=2015, q_date="2015-01-01", on_date="2014-06-01"),                                 # operating before its request
               request(status="operating", year=2015, q_date="2015-01-01", on_date=None),                                         # no operation date
               request(status="withdrawn", year=2015, q_date="2015-01-01", on_date="2030-01-01")]                                 # not operating
        s = summary(built + odd)[("ercot", "solar")]
        self.assertEqual((s["whole"]["operating_requests"], s["whole"]["years_to_operation_n"]), (7, 5))
        self.assertAlmostEqual(s["whole"]["median_years_to_operation"], 3.0, places=2)
        self.assertEqual(s["on"], {})                                            # one request an operation year: no point
        four = summary(built[:4] + odd)[("ercot", "solar")]["whole"]
        self.assertNotIn("median_years_to_operation", four)
        same = [request(status="operating", year=2015, q_date="2015-01-01", on_date="2019-01-01") for _ in range(5)]
        self.assertEqual(summary(same)[("ercot", "solar")]["on"], {2019: {"on_median_years_to_operation": 4.0, "on_requests_dated": 5}})

    def test_a_row_carries_its_unit(self):
        self.assertEqual([qs.unit_of(v) for v in ("mw_active", "total_active_mw", "past_mw", "requests_active", "past_mw_open_share_pct", "median_years_to_operation",
                                                  "on_median_years_to_operation", "years_to_operation_n", "on_requests_dated", "past_requests")],
                         ["MW", "MW", "MW", "count", "pct", "year", "year", "count", "count", "count"])


class TheTableAsBuilt(unittest.TestCase):
    def test_three_views_counted_again_from_the_file(self):
        t = table()
        d, _ = qs.read_input(OUT)
        self.assertEqual(len(d), 38201)                                          # every row of the file, the ones whose id holds a '#' too
        at = lambda e, v, y: float(t[(t["entity"] == e) & (t["variable"] == v) & (t["ts_utc"] == f"{y}-01-01T00:00:00Z")]["value"].iloc[0])
        mw = pd.to_numeric(d["capacity_mw"], errors="coerce").clip(lower=0)
        act = d["status"] == "active"
        self.assertEqual(at("queue:us:all", "total_active_requests", 2025), int(act.sum()))
        self.assertAlmostEqual(at("queue:us:all", "total_active_mw", 2025), float(mw[act].sum()), delta=0.06)
        e = (d["region"] == "ERCOT") & (d["type_clean"] == "Battery")
        self.assertEqual(at("queue:ercot:battery", "requests_entered", 2024), int((e & (d["q_year"] == 2024)).sum()))
        self.assertAlmostEqual(at("queue:ercot:battery", "mw_active", 2024), float(mw[e & act & (d["q_year"] == 2024)].sum()), delta=0.06)
        c = (d["region"] == "CAISO") & (d["type_clean"] == "Solar+Battery") & (d["q_year"] >= 2000) & (d["q_year"] <= 2020) & d["status"].isin(qs.STATUSES)
        self.assertEqual(at("queue:caiso:solar_battery", "past_requests", 2025), int(c.sum()))
        self.assertEqual(at("queue:caiso:solar_battery", "past_operating_share_pct", 2025), round(100 * float((c & (d["status"] == "operating")).sum()) / float(c.sum()), 2))
        p = (d["region"] == "PJM") & (d["type_clean"] == "Solar") & (d["status"] == "operating")
        years = ((pd.to_datetime(d["on_date"]) - pd.to_datetime(d["q_date"])).dt.days / 365.25)[p].dropna()
        years = years[years >= 0]
        self.assertEqual(at("queue:pjm:solar", "median_years_to_operation", 2025), round(float(years.median()), 2))
        self.assertEqual(at("queue:pjm:solar", "years_to_operation_n", 2025), len(years))

    def test_what_the_table_holds_and_what_it_does_not_write(self):
        t = table()
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertTrue(set(t["unit"]) <= {"MW", "count", "pct", "year"})
        self.assertTrue((t["value"] >= 0).all())
        share = t[t["variable"].str.endswith("share_pct")]
        self.assertTrue((share["value"] <= 100).all())
        w = t[t["variable"].isin(["past_requests", "past_operating_share_pct", "past_withdrawn_share_pct", "past_open_share_pct"])].pivot(index="entity", columns="variable", values="value")
        self.assertTrue((w[w["past_operating_share_pct"].notna()]["past_requests"] >= qs.MIN_SHARE).all())
        self.assertTrue(w[w["past_requests"] < qs.MIN_SHARE]["past_operating_share_pct"].isna().all())
        full = w.dropna()
        self.assertTrue(((full["past_operating_share_pct"] + full["past_withdrawn_share_pct"] + full["past_open_share_pct"] - 100).abs() < 0.02).all())
        self.assertNotIn("median_years_to_operation", set(t[t["entity"] == "queue:isone:all"]["variable"]))   # ISO-NE's built requests carry no operation date
        n = t[t["variable"] == "on_requests_dated"]
        self.assertTrue((n["value"] >= qs.MIN_MEDIAN).all())
        head = src("warehouse", "output", f"{qs.NAME}.csv")[:6000]
        self.assertIn("CC BY 4.0", head)
        self.assertIn("Lawrence Berkeley National Laboratory and GridTracker", head)

    def test_the_sites_copy_is_the_table(self):
        t = table()
        with open(os.path.join(SITE, "data", "queues.json"), encoding="utf-8") as f:
            copy = json.load(f)
        n = 0
        for key, v in copy["views"].items():
            grid, tech = key.split("|")
            rows = t[t["entity"] == f"queue:{grid}:{tech}"]
            got = {}
            for y, r in v["years"].items():
                got.update({(k, int(y)): val for k, val in r.items()})
            for y, r in v["on"].items():
                got.update({(k, int(y)): val for k, val in r.items()})
            got.update({(k, copy["last_year"]): val for k, val in v["whole"].items()})
            want = {(r.variable, int(r.ts_utc[:4])): r.value for r in rows.itertuples()}
            self.assertEqual(got, want, key)
            n += len(want)
        self.assertEqual(n, len(t))
        self.assertEqual(copy["past"], [qs.PAST_FROM, copy["last_year"] - qs.PAST_LAG])


class ThePage(unittest.TestCase):
    def test_the_choices_and_the_years(self):
        d = node("import fs from 'node:fs'; import * as q from './lib/queues.ts'; const f = JSON.parse(fs.readFileSync('./data/queues.json', 'utf-8'));"
                 "const c = q.choices({}); const c2 = q.choices({grid:'ercot', tech:'battery'}); const c3 = q.choices({grid:'mars', tech:'coal'});"
                 "const v = q.viewOf(f, 'ercot', 'battery'); const ys = q.yearsOf(v, f.last_year);"
                 "console.log(JSON.stringify({c: [c.grid.slug, c.tech.slug], c2: [c2.grid.slug, c2.tech.slug], c3: [c3.grid.slug, c3.tech.slug], href: q.href('pjm', 'solar'),"
                 "none: q.viewOf(f, 'miso', 'offshore_wind'), first: ys[0].year, last: ys.at(-1).year, n: ys.length, gaps: ys.filter((y) => !y.row).length,"
                 "o: q.outcome({requests_operating: 1, requests_withdrawn: 2, requests_active: 0, requests_suspended: 1}), o0: q.outcome(null), peak: q.peakActive(v),"
                 "grids: q.GRIDS.map((g) => g.slug).sort(), techs: q.TECHS.map((t) => t.slug), fg: [...f.grids].sort(), ft: f.techs, w: [q.whole(1864963.3), q.two(3.9)]}));")
        self.assertEqual((d["c"], d["c2"], d["c3"]), (["us", "all"], ["ercot", "battery"], ["us", "all"]))
        self.assertEqual(d["href"], "/queues?grid=pjm&tech=solar")
        self.assertIsNone(d["none"])
        self.assertEqual(d["last"], 2025)
        self.assertEqual(d["n"], 2025 - d["first"] + 1)                         # a year with no request is an empty year on the axis, not a missing one
        self.assertEqual(d["o"], {"operating": 0.25, "withdrawn": 0.5, "open": 0.25, "n": 4})
        self.assertIsNone(d["o0"])
        self.assertEqual((d["grids"], d["techs"]), (d["fg"], d["ft"]))           # the page's lists are the table's
        self.assertEqual(d["w"], ["1,864,963", "3.90"])
        with open(os.path.join(SITE, "data", "queues.json"), encoding="utf-8") as f:
            v = json.load(f)["views"]["ercot|battery"]["years"]
        best = max(v, key=lambda y: v[y]["mw_active"])
        self.assertEqual(d["peak"], {"year": best, "mw": v[best]["mw_active"]})

    def test_the_page_is_in_review_and_reads_its_own_copy(self):
        d = node("import { statusOf } from './lib/release.ts'; console.log(JSON.stringify([statusOf('/queues'), statusOf('/data/methods/interconnection_queue_summary')]));")
        self.assertEqual(d, ["review", "review"])
        page = src("site", "app", "queues", "page.tsx")
        self.assertNotIn("supabase", page)
        self.assertIn("robots: { index: false, follow: false }", page)
        self.assertIn("Lawrence Berkeley National Laboratory and GridTracker", page)   # the license's condition: attribution
        self.assertIn("CC BY 4.0", page)

    def test_every_number_on_the_built_page_where_a_site_is_served(self):
        base = os.environ.get("ERW_SITE_URL")
        exe = shutil.which("node")
        if not base or not exe:
            self.skipTest("ERW_SITE_URL names no served site (or node is absent): node site/scripts/check-queues.mjs <base>")
        r = subprocess.run([exe, "--import", "./scripts/alias-loader.mjs", "scripts/check-queues.mjs", base], cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "derived", "queue_summary.py"), ("docs", "methods", "interconnection_queue_summary.md"), ("site", "lib", "queues.ts"),
                      ("site", "app", "queues", "page.tsx"), ("site", "scripts", "check-queues.mjs"), ("tests", "test_session95.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
