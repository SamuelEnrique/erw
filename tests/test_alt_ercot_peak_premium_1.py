"""Ruling alternative 1 of /explore/ercot-peak-premium (session 7708, 17 November 2026, branch
wip/alt-ercot-peak-premium-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-ercot-peak-premium-2026-11-17.md, line 1): build
a mean, or the traded 06:00 to 22:00 weekday block, beside the medians of the 16:00 to 21:00 block, so the page can be held
to published figures? On this branch the builder (warehouse/derived/ercot_peak_premium.py, metrics, metrics_of,
with_load) writes <block>_mean, all_mean, traded_median, traded_mean and all_mean_load_weighted beside the medians, and the
page draws them in a section of their own (site/lib/explore/peakpremium.ts MEANS). The medians stand as they were.

Pinned on made-up intervals, and, where the tables are on the machine (warehouse/output, or the folder ERW_TABLES_DIR
names), on HB_HUBAVG's real-time prices with the builder's own functions: 2024, peak median USD 27.20 against its mean
51.01; all intervals median 19.60, mean 26.83, load-weighted 28.88 (Potomac Economics publishes 31.91, weighting load zones
by zone load); the traded block median 20.81, mean 31.68; 2025 traded block 27.09 and 36.16. The 700 MB price history is
streamed for the one hub; only its rows and ERCOT's system load go into a temporary folder.

    python -m unittest tests.test_alt_ercot_peak_premium_1 -v
"""

import csv
import os
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ercot_peak_premium as pp  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
INPUTS = ("ercot_all_hub_prices_history", "iso_rtm_hub_prices")
NEED = INPUTS + ("ercot_zone_load_hourly",)


def quiet(*a, **k):
    pass


class TheRule(unittest.TestCase):
    def test_means_traded_block_and_load_weighting(self):
        # five intervals: Monday 07:00, 17:00 and 13:00, Saturday 07:00 and 23:00 (local hours)
        prices = np.array([10.0, 100.0, 20.0, 30.0, 40.0])
        hours = np.array([7, 17, 7, 23, 13])
        weekdays = np.array([0, 0, 5, 5, 0])
        loads = np.array([1.0, 3.0, np.nan, 1.0, 1.0])
        m = pp.metrics(prices, hours, weekdays, loads)
        self.assertEqual(m["all_mean"][0], 40.0)
        self.assertEqual(m["peak_mean"][0], 100.0)
        self.assertEqual((m["overnight_mean"][0], m["midday_mean"][0]), (20.0, 40.0))
        self.assertEqual((m["traded_median"][0], m["traded_mean"][0]), (40.0, 50.0))   # the three weekday intervals in 06:00 to 22:00
        self.assertEqual((round(m["all_mean_load_weighted"][0], 6), m["n_load_weighted"][0]), (round(380 / 6, 6), 4.0))   # (10 + 300 + 30 + 40) / 6
        self.assertEqual(m["peak_median"][0], 100.0)   # the medians stand

    def test_without_weekdays_or_loads_main_figures_only(self):
        m = pp.metrics(np.array([1.0, 2.0, 3.0]), np.array([1, 13, 17]))   # main's call: no weekdays, no loads
        self.assertNotIn("traded_mean", m)
        self.assertNotIn("all_mean_load_weighted", m)


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in NEED), "the price and load tables are not on this machine")
class OnTheTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows, seen = [], set()
        for name in INPUTS:
            with open(os.path.join(TABLES, name + ".csv"), encoding="utf-8") as f:
                rd = csv.reader(line for line in f if not line.startswith("#"))
                ix = {k: i for i, k in enumerate(next(rd))}
                for r in rd:
                    if r[ix["entity"]] != "ercot:HB_HUBAVG" or r[ix["variable"]] != "spp_rtm" or r[ix["market"]] != "ercot_rtm":
                        continue
                    ts = r[ix["ts_utc"]]
                    if ts < "2023-12-31" or ts >= "2026-01-02" or ts in seen:
                        continue
                    seen.add(ts)
                    rows.append((r[ix["node"]], ts, float(r[ix["value"]])))
        d = pd.DataFrame(rows, columns=["node", "ts_utc", "value"])
        d["ts"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
        d["local"] = d["ts"].dt.tz_convert(pp.TZ)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ercot_zone_load_hourly.csv")
            with open(os.path.join(TABLES, "ercot_zone_load_hourly.csv"), encoding="utf-8") as f, open(path, "w", encoding="utf-8", newline="") as out:
                head = None
                for line in f:
                    if line.startswith("#"):
                        continue
                    if head is None:
                        head = line
                        out.write(line)
                    elif line.startswith("ercot:system,"):
                        out.write(line)
            d = pp.with_load(d, quiet, path)
        cls.y = {y: pp.metrics_of(d[d["local"].dt.year == y]) for y in (2024, 2025)}

    def fig(self, y, v):
        return round(self.y[y][v][0], 2)

    def test_2024(self):
        self.assertEqual(self.y[2024]["n_intervals"][0], 35136.0)   # a whole leap year of 15-minute intervals
        self.assertEqual((self.fig(2024, "peak_median"), self.fig(2024, "peak_mean")), (27.20, 51.01))
        self.assertEqual((self.fig(2024, "all_median"), self.fig(2024, "all_mean"), self.fig(2024, "all_mean_load_weighted")), (19.60, 26.83, 28.88))
        self.assertEqual((self.fig(2024, "traded_median"), self.fig(2024, "traded_mean")), (20.81, 31.68))

    @unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"ercot_peak_premium_{p}.csv")) for p in ("annual", "monthly")), "the page's tables are not on this machine")
    def test_the_page_draws_the_means_beside_the_medians(self):
        """The annual table as it stands, with the rows the branch's builder adds for HB_HUBAVG in 2024 and 2025 (computed
        above with its own functions), drawn by the page's own function: the section shows them beside the medians."""
        import json
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            annual = os.path.join(tmp, "ercot_peak_premium_annual.csv")
            with open(os.path.join(TABLES, "ercot_peak_premium_annual.csv"), encoding="utf-8") as f:
                text = f.read()
            head = next(line for line in text.splitlines() if not line.startswith("#")).split(",")
            extra = []
            for y, m in self.y.items():
                for v in ("peak_mean", "all_mean", "all_mean_load_weighted", "traded_median", "traded_mean"):
                    row = dict(entity="ercot:HB_HUBAVG", variable=v, ts_utc=f"{y}-01-01T00:00:00Z", value=f"{m[v][0]:.6f}", unit="USD/MWh", freq="P1Y")
                    extra.append(",".join(row.get(c, "") for c in head))
            with open(annual, "w", encoding="utf-8", newline="\n") as f:
                f.write(text.rstrip("\n") + "\n" + "\n".join(extra) + "\n")
            p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-peak-premium-figures.mjs", annual, os.path.join(TABLES, "ercot_peak_premium_monthly.csv")],
                               cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        got = json.loads(p.stdout)
        self.assertTrue(got["drawn"])
        s = got["shown"]
        self.assertEqual((s["peak_median|2024"], s["peak_mean|2024"], s["all_mean_load_weighted|2024"], s["traded_mean|2024"]), ("27.20", "51.01", "28.88", "31.68"))
        self.assertEqual((s["traded_median|2025"], s["traded_mean|2025"]), ("27.09", "36.16"))

    def test_2025(self):
        self.assertEqual((self.fig(2025, "peak_median"), self.fig(2025, "peak_mean")), (37.03, 48.13))
        self.assertEqual((self.fig(2025, "traded_median"), self.fig(2025, "traded_mean")), (27.09, 36.16))


if __name__ == "__main__":
    unittest.main()
