"""Session 96: where power is cheap (/prices/compare), in review.

Energy Research Warehouse (ERW). The builder of hub_price_comparison (warehouse/derived/price_compare.py) on prices
made here and on the table as built, computed again from the price tables; the site's copy against the table; the
page's pure part (site/lib/pricecompare.ts), run by node; and that the page is in review. Every number the page shows
against the site's copy is site/scripts/check-prices-compare.mjs, which runs here when ERW_SITE_URL names a built site.

    python -m unittest tests.test_session96 -v
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
import price_compare as pc  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
COPY = os.path.join(SITE, "data", "price_compare.json")


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


def prices(entity, side, start, hours, value, tz="America/Chicago", freq="PT1H", table="iso_hub_prices_history"):
    """Hourly (or 15-minute) prices from a local start; value is a number or a function of the local hour of the day."""
    step = "h" if freq == "PT1H" else "15min"
    n = hours if freq == "PT1H" else hours * 4
    ts = pd.date_range(pd.Timestamp(start, tz=tz).tz_convert("UTC"), periods=n, freq=step)
    local = ts.tz_convert(tz).hour
    v = [value(h) for h in local] if callable(value) else [value] * n
    return pd.DataFrame({"entity": entity, "side": side, "ts": ts, "value": v, "freq": freq, "geo": "US-TX", "table": table})


class TheMeasures(unittest.TestCase):
    def test_the_mean_the_two_shares_and_the_spread_of_a_known_day(self):
        # an average day: 10 from midnight to 19:00, 110 for the four hours 20:00 to 23:00, and minus 5 at 03:00 and 04:00
        day = lambda h: 110.0 if h >= 20 else -5.0 if h in (3, 4) else 10.0
        x = prices("ercot:HB_TEST", "dam", "2026-09-01", 720, day)
        h = pd.Series(x["value"].values, index=x["ts"])
        m = pc.measures(h, "America/Chicago")
        self.assertEqual(m["avg_price"], round((18 * 10 + 4 * 110 - 2 * 5) / 24, 2))
        self.assertEqual(m["negative_hours_share_pct"], round(100 * 2 / 24, 2))
        self.assertEqual(m["above_200_hours_share_pct"], 0.0)
        self.assertEqual(m["day_spread_top4_bottom4"], 110 - (-5 - 5 + 10 + 10) / 4)
        h.iloc[100] = 250.0
        self.assertEqual(pc.measures(h, "America/Chicago")["above_200_hours_share_pct"], round(100 / 720, 2))
        self.assertIsNone(pc.measures(h[h.index.tz_convert("America/Chicago").hour != 7], "America/Chicago"))   # an hour of the day missing

    def test_an_hour_of_real_time_needs_its_four_quarter_hours(self):
        x = prices("ercot:HB_TEST", "rtm", "2026-09-01", 3, 20.0, freq="PT15M")
        s = pd.Series([10.0, 20.0, 30.0, 40.0] + [20.0] * 8, index=x["ts"])
        h = pc.hourly(s.drop(s.index[5]), "PT15M")
        self.assertEqual(list(h.values), [25.0, 20.0])                          # the hour that lost a quarter is not an hour
        self.assertEqual(len(pc.hourly(s, "PT1H")), 12)                         # an hourly series is left as it is

    def test_the_hours_of_a_window_follow_the_clock(self):
        self.assertEqual(pc.window_hours("2026-09-01", "2026-10-01", "America/Chicago")[2], 720)
        self.assertEqual(pc.window_hours("2026-03-01", "2026-04-01", "America/New_York")[2], 743)       # the clocks go forward
        self.assertEqual(pc.window_hours("2025-11-01", "2025-12-01", "America/Los_Angeles")[2], 721)    # and back
        self.assertEqual(pc.window_hours("2025-10-01", "2026-10-01", "America/Chicago")[2], 8760)

    def build(self, x, hidden=None):
        return pc.build(x, OUT, "2026-09", hidden or {}, lambda *_: None)

    def test_a_window_with_too_few_hours_is_not_written_and_a_paused_publisher_is_named_without_a_number(self):
        if not os.path.exists(os.path.join(OUT, "carbon_intensity_daily.csv")):
            self.skipTest("carbon_intensity_daily is not on this machine")
        full = prices("ercot:HB_TEST", "dam", "2026-09-01", 720, 30.0)
        short = prices("ercot:HB_SHORT", "dam", "2026-09-01", 600, 30.0)        # 83 percent of the month
        two = pd.concat([prices("isone:.Z.TEST", "rtm", "2026-09-01", 500, 40.0, tz="America/New_York", freq="PT15M"),
                         prices("isone:.Z.TEST", "rtm", "2026-09-01", 720, 50.0, tz="America/New_York", table="isone_rtm_zone_prices_hourly")])
        miso = prices("miso:TEST.HUB", "dam", "2026-09-01", 720, 25.0)
        rows, view, hidden, windows = self.build(pd.concat([full, short, two, miso]), {"miso": "its terms are under review"})
        r = pd.DataFrame(rows)
        self.assertEqual(sorted(r["entity"].unique()), ["ercot:HB_TEST", "isone:.Z.TEST"])
        self.assertEqual(hidden, [{"entity": "miso:TEST.HUB", "grid": "MISO", "node": "TEST.HUB", "reason": "its terms are under review"}])
        self.assertEqual(view["year"], [])                                       # a month of prices is not a year
        m = {v["entity"]: v for v in view["month"]}
        self.assertEqual((m["ercot:HB_TEST"]["dam_avg_price"], m["ercot:HB_TEST"]["dam_hours_held"], m["ercot:HB_TEST"]["dam_hours_in_window"]), (30.0, 720, 720))
        self.assertNotIn("rtm_avg_price", m["ercot:HB_TEST"])
        self.assertEqual((m["isone:.Z.TEST"]["rtm_avg_price"], m["isone:.Z.TEST"]["rtm_basis"]), (50.0, "PT1H"))   # the basis that holds more, whole, never mixed
        self.assertEqual(windows["year"][:2], ("2025-10-01", "2026-10-01"))
        self.assertEqual(set(r[r["entity"] == "ercot:HB_TEST"]["freq"]), {"P1M"})


class TheTableAsBuilt(unittest.TestCase):
    def table(self):
        path = os.path.join(OUT, f"{pc.NAME}.csv")
        if not os.path.exists(path):
            self.skipTest("hub_price_comparison is not built on this machine")
        return pd.read_csv(path, comment="#")

    def test_two_hubs_computed_again_from_the_price_tables(self):
        t = self.table()
        at = lambda e, v, ts: float(t[(t["entity"] == e) & (t["variable"] == v) & (t["ts_utc"] == ts)]["value"].iloc[0])
        end = copy()["end_month"]
        self.assertEqual(end, "2026-09")
        d = pd.read_csv(os.path.join(OUT, "iso_hub_prices_history.csv"), comment="#", usecols=["entity", "variable", "ts_utc", "value"])
        s = d[(d["entity"] == "nyiso:N.Y.C.") & (d["variable"] == "lmp_dam")]
        h = pd.Series(s["value"].values, index=pd.to_datetime(s["ts_utc"], utc=True)).sort_index()
        a, b = pd.Timestamp("2025-10-01", tz="America/New_York"), pd.Timestamp("2026-10-01", tz="America/New_York")
        h = h[(h.index >= a) & (h.index < b)]
        self.assertEqual(at("nyiso:N.Y.C.", "dam_hours_held", "2025-10-01T00:00:00Z"), len(h))
        self.assertEqual(at("nyiso:N.Y.C.", "dam_avg_price", "2025-10-01T00:00:00Z"), round(float(h.mean()), 2))
        self.assertEqual(at("nyiso:N.Y.C.", "dam_above_200_hours_share_pct", "2025-10-01T00:00:00Z"), round(100 * float((h > 200).mean()), 2))
        day = h.groupby(h.index.tz_convert("America/New_York").hour).mean().sort_values()
        self.assertEqual(at("nyiso:N.Y.C.", "dam_day_spread_top4_bottom4", "2025-10-01T00:00:00Z"), round(float(day.iloc[-4:].mean() - day.iloc[:4].mean()), 2))
        s = d[(d["entity"] == "caiso:TH_SP15_GEN-APND") & (d["variable"] == "lmp_rtm_15m_mean")]
        q = pd.Series(s["value"].values, index=pd.to_datetime(s["ts_utc"], utc=True)).sort_index()
        a, b = pd.Timestamp("2026-09-01", tz="America/Los_Angeles"), pd.Timestamp("2026-10-01", tz="America/Los_Angeles")
        g = q.groupby(q.index.floor("h"))
        h = g.mean()[g.size() == 4]
        h = h[(h.index >= a) & (h.index < b)]
        self.assertEqual(at("caiso:TH_SP15_GEN-APND", "rtm_avg_price", "2026-09-01T00:00:00Z"), round(float(h.mean()), 2))
        self.assertEqual(at("caiso:TH_SP15_GEN-APND", "rtm_negative_hours_share_pct", "2026-09-01T00:00:00Z"), round(100 * float((h < 0).mean()), 2))

    def test_what_the_table_holds_and_what_it_does_not(self):
        t = self.table()
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertFalse(t["entity"].str.startswith(("miso:", "pjm:")).any())    # MISO: its terms are under review; PJM: not held
        self.assertEqual(set(t["freq"]), {"P1Y", "P1M"})
        held = t[t["variable"].str.endswith("_hours_held")].merge(
            t[t["variable"].str.endswith("_hours_in_window")].assign(variable=lambda d: d["variable"].str.replace("in_window", "held")), on=["entity", "variable", "ts_utc"])
        self.assertTrue((held["value_x"] >= pc.NEAR_HOURS * held["value_y"]).all())
        self.assertTrue((held["value_x"] <= held["value_y"]).all())
        share = t[t["variable"].str.endswith("share_pct")]
        self.assertTrue(((share["value"] >= 0) & (share["value"] <= 100)).all())
        y = t[t["freq"] == "P1Y"]
        self.assertEqual(y["entity"].nunique(), 11)
        self.assertEqual(t[t["freq"] == "P1M"]["entity"].nunique(), 31)
        self.assertNotIn("grid_carbon_intensity", set(y[y["entity"] == "spp:SPPNORTH_HUB"]["variable"]))   # 236 of 365 days: not held
        self.assertNotIn("rtm_avg_price", set(y[y["entity"] == "isone:.H.INTERNAL_HUB"]["variable"]))      # under 95 percent of the year's hours

    def test_the_sites_copy_is_the_table(self):
        t = self.table()
        c = copy()
        n = 0
        for name, freq in (("year", "P1Y"), ("month", "P1M")):
            for r in c[name]:
                rows = t[(t["entity"] == r["entity"]) & (t["freq"] == freq)]
                want = dict(zip(rows["variable"], rows["value"]))
                got = {k: v for k, v in r.items() if k not in ("entity", "grid", "node", "dam_basis", "rtm_basis", "grid_carbon_days_due")}
                self.assertEqual(got, want, (name, r["entity"]))
                n += len(want)
        self.assertEqual(n, len(t))
        self.assertEqual(len(c["held_not_shown"]), 8)
        self.assertTrue(all(h["grid"] == "MISO" and "terms are under review" in h["reason"] for h in c["held_not_shown"]))
        self.assertEqual(c["internal_tables"], [])


class ThePage(unittest.TestCase):
    def test_the_choices_and_the_order(self):
        d = node("import fs from 'node:fs'; import * as p from './lib/pricecompare.ts'; const f = JSON.parse(fs.readFileSync('./data/price_compare.json', 'utf-8'));"
                 "const c0 = p.choices({}); const c1 = p.choices({period:'month', market:'rtm', sort:'spread'}); const c2 = p.choices({period:'week', market:'x', sort:'y', dir:'up'});"
                 "const flat = (c) => [c.period, c.market, c.sort.slug, c.dir];"
                 "const o = p.ordered(f.year, c0).map((r) => r.dam_avg_price); const carbon = p.ordered(f.year, p.choices({sort:'carbon'}));"
                 "const rt = p.ordered(f.year, p.choices({market:'rtm'}));"
                 "console.log(JSON.stringify({c: [flat(c0), flat(c1), flat(c2)], o, lastCarbon: carbon.at(-1).entity, n: carbon.length, rt: rt.length,"
                 "lack: p.lacking(f.year, 'rtm').map((r) => r.entity), href: p.href({period:'year', market:'dam', sort:'neg'}),"
                 "label: [p.label(f.year.find((r) => r.entity === 'ercot:HB_NORTH')), p.label({entity: 'x:Y', grid: 'X', node: 'Y'})],"
                 "when: [p.periodName(f, 'year'), p.periodName(f, 'month')], named: f.month.every((r) => !p.label(r).endsWith(r.node))}));")
        self.assertEqual(d["c"], [["year", "dam", "avg", "asc"], ["month", "rtm", "spread", "desc"], ["year", "dam", "avg", "asc"]])
        self.assertEqual(d["o"], sorted(d["o"]))
        self.assertEqual(d["lastCarbon"], "spp:SPPNORTH_HUB")                    # a hub that lacks the measure goes last, whatever the direction
        self.assertEqual((d["n"], d["rt"], d["lack"]), (11, 10, ["isone:.H.INTERNAL_HUB"]))
        self.assertEqual(d["href"], "/prices/compare?period=year&market=dam&sort=neg")
        self.assertEqual(d["label"], ["ERCOT, North hub", "X, Y"])
        self.assertEqual(d["when"], ["the twelve months to September 2026", "September 2026"])
        self.assertTrue(d["named"])                                              # every hub and zone shown has a reader's name

    def test_the_page_is_in_review_says_a_hub_is_not_a_site_and_reads_its_own_copy(self):
        d = node("import { statusOf } from './lib/release.ts'; console.log(JSON.stringify([statusOf('/prices/compare'), statusOf('/data/methods/hub_price_comparison')]));")
        self.assertEqual(d, ["review", "review"])
        page = src("site", "app", "prices", "compare", "page.tsx")
        self.assertNotIn("supabase", page)
        self.assertIn("robots: { index: false, follow: false }", page)
        self.assertIn("A hub is not a site.", page)
        self.assertIn("Held, not shown: license needed.", page)

    def test_every_number_on_the_built_page_where_a_site_is_served(self):
        base = os.environ.get("ERW_SITE_URL")
        exe = shutil.which("node")
        if not base or not exe:
            self.skipTest("ERW_SITE_URL names no served site (or node is absent): node site/scripts/check-prices-compare.mjs <base>")
        r = subprocess.run([exe, "--import", "./scripts/alias-loader.mjs", "scripts/check-prices-compare.mjs", base], cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "derived", "price_compare.py"), ("docs", "methods", "hub_price_comparison.md"), ("site", "lib", "pricecompare.ts"),
                      ("site", "app", "prices", "compare", "page.tsx"), ("site", "scripts", "check-prices-compare.mjs"), ("tests", "test_session96.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
