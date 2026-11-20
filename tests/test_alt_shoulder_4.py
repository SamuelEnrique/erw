"""Ruling alternative 4 of /shoulder (session 7703, 17 November 2026, branch wip/alt-shoulder-4; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-shoulder-2026-11-17.md, line 4): should "the ten
worst days" be ranked by the tightest evening (the highest evening net load) instead of the largest shoulder energy above
the day's own mean? On this branch warehouse/derived/shoulder_hours.py worst_days ranks by day_evening_peak_mw.

Pinned on made-up days, and, where EIA's ERCO workbook of Form EIA-930 is on the machine (warehouse/raw/eia930_emissions
beside the folder ERW_TABLES_DIR names, or this checkout's own) with storage_buildout_monthly, on ERCOT's 2025 with the
builder's own functions: 360 days ranked; the ten are 18, 20 and 19 August, 30 and 31 July, 3 September, 24 August,
4 September, 29 July and 11 August (18 August first, 68,781 MW); their mean evening peak 67,122 MW (main's ten: 48,751),
mean energy above the day's mean 64,206 MWh (101,073), mean hours needed 5.78 (8.88); no day is in both tens.

    python -m unittest tests.test_alt_shoulder_4 -v
"""

import glob
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402
import shoulder_hours as sh  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
RAW = os.path.join(os.path.dirname(os.path.abspath(TABLES)), "raw", "eia930_emissions")
HAS_RAW = bool([f for f in glob.glob(os.path.join(RAW, "*", "*_ERCO.xlsx")) if os.path.getsize(f) > 0])
MAIN_TEN = {"2025-01-31", "2025-12-10", "2025-02-27", "2025-11-07", "2025-12-14", "2025-11-30", "2025-01-19", "2025-12-29", "2025-12-18", "2025-10-20"}


def day_hours(day, net, solar):
    return pd.DataFrame({"day": day, "hour": range(24), "m": day[:7], "demand": [n + s for n, s in zip(net, solar)], "solar": solar, "wind": 0.0,
                         "net_load": net, "bat": float("nan")})


class TheRule(unittest.TestCase):
    def test_the_tightest_evening_ranks_first(self):
        solar = [0] * 7 + [5, 20, 40, 60, 70, 70, 60, 40, 20, 5] + [0] * 7
        flat_high = [60 + (10 if 18 <= h <= 20 else 0) for h in range(24)]          # a high day: peak 70, little above its mean
        deep = [40 - (25 if 10 <= h <= 14 else 0) + (25 if 18 <= h <= 21 else 0) for h in range(24)]   # a deep midday, a long evening above the mean
        h = pd.concat([day_hours("2025-07-01", flat_high, solar), day_hours("2025-03-01", deep, solar)], ignore_index=True)
        wd, wy = sh.worst_days(h, pd.DataFrame(), "ercot", lambda *_: None)
        self.assertEqual(wd["2025-07-01"]["worst_rank"], 1)                              # main would rank 2025-03-01 first
        self.assertGreater(wd["2025-03-01"]["day_shoulder_mwh_above_mean"], wd["2025-07-01"]["day_shoulder_mwh_above_mean"])
        self.assertEqual(wy["2025"]["year_days_ranked"], 2)


@unittest.skipUnless(HAS_RAW and os.path.exists(os.path.join(TABLES, "storage_buildout_monthly.csv")), "EIA's ERCO workbook is not on this machine")
class OnErcot2025(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        keep_raw, keep_out = sh.RAW, ip.OUT_DIR
        sh.RAW = RAW
        ip.set_out_dir(TABLES)
        try:
            h, _ = sh.hourly("ERCO")
            fl = sh.fleet_by_month("ercot")
        finally:
            sh.RAW = keep_raw
            ip.set_out_dir(keep_out)
        h["local"] = h["ts"].dt.tz_convert("America/Chicago")
        h["day"] = h["local"].dt.strftime("%Y-%m-%d")
        h["hour"] = h["local"].dt.hour
        h["m"] = h["local"].dt.strftime("%Y-%m")
        h = h[h["m"].str.startswith("2025")]
        h["net_load"] = h["demand"] - h["solar"] - h["wind"]
        need = h.groupby("day")["ts"].size()
        ok = h.dropna(subset=["demand", "solar", "wind"]).groupby("day").size()
        full = {d for d in need.index if ok.get(d, 0) == need[d] and need[d] in (23, 24, 25)}
        cls.wd, cls.wy = sh.worst_days(h[h["day"].isin(full)], fl, "ercot", lambda *_: None)

    def test_the_ten(self):
        ten = sorted(self.wd, key=lambda d: self.wd[d]["worst_rank"])
        self.assertEqual(ten, ["2025-08-18", "2025-08-20", "2025-08-19", "2025-07-30", "2025-07-31", "2025-09-03", "2025-08-24", "2025-09-04", "2025-07-29", "2025-08-11"])
        self.assertEqual(round(self.wd["2025-08-18"]["day_evening_peak_mw"]), 68781)
        self.assertEqual(set(ten) & MAIN_TEN, set())

    def test_the_means(self):
        ten = list(self.wd.values())
        self.assertEqual(self.wy["2025"]["year_days_ranked"], 360)
        self.assertEqual(round(sum(v["day_evening_peak_mw"] for v in ten) / 10), 67122)
        self.assertEqual(round(self.wy["2025"]["year_worst10_mean_shoulder_mwh_above_mean"]), 64206)
        self.assertEqual(round(self.wy["2025"]["year_worst10_mean_shoulder_hours_needed"], 2), 5.78)


if __name__ == "__main__":
    unittest.main()
