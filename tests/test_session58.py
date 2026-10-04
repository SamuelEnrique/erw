"""Session 58: the daily jobs, private inputs, California reliability v1.

Energy Research Warehouse (ERW). No network, no model. Tests that need a warehouse table skip where it is absent.
1. The daily job's failures, fixed in code: the chat spec is current; every news date parse takes any ISO 8601 stamp;
   the loader escalates to VACUUM FULL over the size limit; the daily job and the Roundup have the once-a-day gate; the
   runbook's outside trigger holds no token.
2. private/newsletters is ignored by git except its README.
3. caiso_grid_emergencies: the report's notices, its check against CAISO's own counts, the September 2022 days;
   caiso_reliability_daily recomputed by hand for 2022-09-06; caiso_heat_2022 in the event window, the event study, the
   site and the checks.

    python -m unittest tests.test_session58 -v
"""

import glob
import os
import re
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def table(name):
    path = os.path.join(OUT, name + ".csv")
    n = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str), [ln for ln in open(path, encoding="utf-8") if ln.startswith("#")]


class DailyJob(unittest.TestCase):
    def test_spec_current(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "chat", "check_spec.py")], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_news_dates_take_any_iso_stamp(self):
        for p in glob.glob(os.path.join(ROOT, "warehouse", "news", "*.py")):
            s = open(p, encoding="utf-8").read()
            self.assertIsNone(re.search(r'event_date"\], utc=True\)', s), p)
        x = pd.Series(["2026-09-30T12:00:00Z", "2026-09-30T12:00:00.123Z", "2026-09-30T12:00:00+00:00"])
        self.assertEqual(len(pd.to_datetime(x, utc=True, format="ISO8601")), 3)

    def test_loader_escalates_over_the_limit(self):
        s = src("warehouse", "supabase", "load.py")
        self.assertIn('VACUUM (FULL, ANALYZE) once (session 58)', s)
        self.assertLess(s.index("vacuum(db_url(), full=True)"), s.index('if mb > LIVE["max_mb"]:\n        print(f"FAILED'))

    def test_the_gate(self):
        for wf, job in (("daily-prices.yml", "refresh"), ("roundup.yml", "roundup")):
            s = src(".github", "workflows", wf)
            self.assertIn("  gate:\n", s)
            self.assertIn(f"  {job}:\n    needs: gate\n    if: needs.gate.outputs.run == '1'", s)
            self.assertIn("github.event_name == 'schedule' || github.event.inputs.once == '1'", s)
            self.assertIn(f"actions/workflows/{wf}/runs?status=success", s)
            self.assertIn("actions: read", s)

    def test_status_lists_a_multi_iso_gap(self):
        # 2026-10-02: the daily run's STATUS.md step failed with KeyError 'iso' on a gap of iso_hub_prices_history
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
        import build_status
        self.assertIn("if iso not in ip.ISOS:", src("warehouse", "metadata", "build_status.py"))
        if os.path.exists(os.path.join(OUT, "iso_hub_prices_history.csv")):
            self.assertIsNone(build_status.day_complete("iso_hub_prices_history", "2026-09-01"))

    def test_derived_sources_say_derived(self):
        import csv
        rows = {r["source"]: r for r in csv.DictReader(open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8"))}
        for s in ("erw:grid_network", "erw:caiso_reliability"):
            self.assertEqual(rows[s]["publisher"], "Energy Research Warehouse (ERW), derived", s)

    def test_runbook_has_no_token(self):
        rb = src("docs", "runbook.md")
        self.assertIn("## An outside trigger for the scheduled jobs (session 58)", rb)
        self.assertIn("**Actions: Read and write**", rb)
        for p in ("docs/runbook.md", ".github/workflows/daily-prices.yml", ".github/workflows/roundup.yml"):
            self.assertIsNone(re.search(r"github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,}", src(*p.split("/"))), p)


class Private(unittest.TestCase):
    def test_newsletters_ignored(self):
        r = subprocess.run(["git", "check-ignore", "private/newsletters/2026-10-01.pdf", "private/bills/x.pdf"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(sorted(r.stdout.split()), ["private/bills/x.pdf", "private/newsletters/2026-10-01.pdf"])
        r = subprocess.run(["git", "check-ignore", "private/newsletters/README.md"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "")


@unittest.skipUnless(os.path.exists(os.path.join(OUT, "caiso_grid_emergencies.csv")), "caiso_grid_emergencies is not on this machine")
class Emergencies(unittest.TestCase):
    def test_table(self):
        d, h = table("caiso_grid_emergencies")
        self.assertLessEqual(len(d), 20_000)
        self.assertEqual(set(d["event_type"]) - {"flex_alert", "rmo", "transmission_emergency", "eea_watch", "eea1", "eea2", "eea3", "alert", "warning",
                                                   "stage1", "stage2", "stage3", "vlrp", "load_interruption"}, set())
        self.assertTrue(d["event_id"].is_unique)
        self.assertTrue(any("License: public" in x and "the California ISO is credited" in x for x in h))
        m = re.search(r"(\d+) of (\d+) year-type counts match", "".join(h))
        self.assertTrue(m and int(m.group(1)) >= 214 and m.group(2) == "232", m.group(0) if m else h)
        sep = d[d["event_date"].between("2022-08-31", "2022-09-09")]
        self.assertEqual(sep[sep["event_type"] == "flex_alert"]["event_date"].nunique(), 10)
        self.assertEqual(sorted(sep[sep["event_type"] == "eea3"]["event_date"].unique()), ["2022-09-06"])
        # CAISO's own count of 2020 Flex Alert days is 10 (the report, page 3)
        self.assertEqual(d[(d["event_type"] == "flex_alert") & d["event_date"].str.startswith("2020")]["event_date"].nunique(), 10)


@unittest.skipUnless(os.path.exists(os.path.join(OUT, "caiso_reliability_daily.csv")), "caiso_reliability_daily is not on this machine")
class Tightness(unittest.TestCase):
    def test_2022_09_06_by_hand(self):
        import eia930_emissions as em
        if em.latest_extract("ciso") is None:  # session 77: raw files stay on the machine that downloaded them
            self.skipTest("EIA-930's CISO extract (warehouse/raw/eia930_emissions) is not on this machine")
        x = em.read_extract(em.latest_extract("ciso"))[["ts_utc", "demand_mwh"]].dropna()
        t = pd.to_datetime(x["ts_utc"], utc=True).dt.tz_convert("America/Los_Angeles")
        day = x[t.dt.strftime("%Y-%m-%d") == "2022-09-06"].assign(h=t.dt.hour)
        self.assertEqual(len(day), 24)
        v = day.set_index("h")["demand_mwh"]
        d, _ = table("caiso_reliability_daily")
        get = lambda var: float(d[(d["variable"] == var) & (d["ts_utc"] == "2022-09-06T00:00:00Z")]["value"].iloc[0])  # noqa: E731
        self.assertEqual(get("peak_demand_mw"), float(v.max()))
        am, ev = v[[12, 13, 14]].mean(), v[[17, 18, 19, 20]].max()
        self.assertAlmostEqual(get("afternoon_mean_mw"), am, places=3)
        self.assertAlmostEqual(get("evening_ramp_mw"), ev - am, places=3)
        self.assertEqual(get("notices_eea3"), 1.0)
        # the highest peak held is this day
        p = d[d["variable"] == "peak_demand_mw"].assign(v=lambda z: z["value"].astype(float))
        self.assertEqual(p.sort_values("v").iloc[-1]["ts_utc"], "2022-09-06T00:00:00Z")

    def test_battery_share_by_hand(self):
        d, _ = table("caiso_reliability_daily")
        s = d[d["variable"] == "battery_share_pct"].iloc[-1]
        day = s["ts_utc"][:10]
        g = lambda var: float(d[(d["variable"] == var) & (d["ts_utc"] == s["ts_utc"])]["value"].iloc[0])  # noqa: E731
        self.assertAlmostEqual(float(s["value"]), g("battery_mw_evening_peak") / g("evening_peak_mw") * 100, places=3)
        b, _ = table("caiso_battery_storage")
        b = b[(b["variable"] == "batteries_mw")]
        t = pd.to_datetime(b["ts_utc"], utc=True).dt.tz_convert("America/Los_Angeles")
        h = int(g("evening_peak_hour"))
        sel = b[(t.dt.strftime("%Y-%m-%d") == day) & (t.dt.hour == h)]["value"].astype(float)
        self.assertEqual(len(sel), 12)
        self.assertAlmostEqual(g("battery_mw_evening_peak"), sel.mean(), places=3)


class Wired(unittest.TestCase):
    def test_event_everywhere(self):
        self.assertIn('event="caiso_heat_2022"', src("warehouse", "derived", "event_window.py"))
        self.assertIn('"caiso_heat_2022": ("2022-08-31", "2022-09-09")', src("warehouse", "derived", "event_study.py"))
        self.assertIn('caiso_heat_2022: ["2022-08-31", "2022-09-09"]', src("site", "lib", "eventstudy.ts"))
        self.assertIn('"caiso_heat_2022": ("2022-08-31", "2022-09-09", [364, 728], ["ciso"])', src("warehouse", "connectors", "noaa_isd.py"))
        self.assertIn('"/events/caiso-heat-2022"', src("site", "scripts", "check-routes.mjs"))
        self.assertIn('"/events/caiso-heat-2022"', src("site", "scripts", "check-values.mjs"))
        self.assertIn('p[0] === "awe"', src("site", "scripts", "check-values.mjs"))
        self.assertIn('href: "/events/caiso-heat-2022"', src("site", "app", "events", "page.tsx"))
        grid = src("site", "app", "grid", "[iso]", "page.tsx")
        self.assertIn('g.slug === "caiso" ? <Section id="reliability" title="Reliability"', grid)
        live = src("warehouse", "supabase", "live_set.yaml")
        self.assertIn("'^caiso_grid_emergencies$'", live)
        self.assertIn("'^caiso_reliability_daily$'", live)

    def test_no_em_dashes(self):
        for p in (("warehouse", "connectors", "caiso_emergencies.py"), ("warehouse", "derived", "caiso_reliability.py"), ("site", "lib", "reliability.ts"),
                  ("site", "app", "grid", "[iso]", "Reliability.tsx"), ("site", "app", "events", "caiso-heat-2022", "page.tsx"),
                  ("docs", "methods", "california_reliability.md"), ("docs", "reviews", "clara-questions.md"), ("docs", "runbook.md"),
                  ("private", "newsletters", "README.md"), ("tests", "test_session58.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
