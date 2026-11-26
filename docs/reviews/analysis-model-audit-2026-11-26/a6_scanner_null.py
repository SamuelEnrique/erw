"""Audit of Automated Analysis (session 10204): the scanner's rules on daily series with nothing in them.

The engine's own rule functions (findings_scanner.rule_record, rule_spike, rule_weekly) and its own settled() on
simulated daily series of 2,100 days (about 5.75 years), scanned once on the day after the last point plus the settle
days, with the configuration of warehouse/config/scanner.yaml. Three kinds of series with no event in them:
  iid: independent lognormal days (a positive quantity with noise);
  ar: log AR(1) with rho 0.9 (persistent, like a price or a load);
  t3: independent days with Student t (3 degrees of freedom) noise on a positive level (fat tails, like prices).
Prints the share of series that raise at least one flag per rule on one scan, and what that is across the 6,797
series the first run scanned (docs/methods/automated_analysis_scanner.md), before the caps.

Run: python runs/a6_scanner_null.py > runs/a6.out
"""
import datetime as dt
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import findings_scanner as fs  # noqa: E402

CFG = fs.load_config()
N_DAYS = 2100
N_SERIES = 3000
rng = np.random.default_rng(102041)
START = np.datetime64("2020-01-01", "D")


class S:
    def __init__(self, v):
        self.table = "audit_sim"
        self.key = {"entity": "sim", "variable": "x"}
        self.key_str = "sim|x"
        self.days = START + np.arange(len(v)).astype("timedelta64[D]")
        self.v = v
        self.lo = v
        self.hi = v
        self.unit = "MW"
        self.grain = "daily"
        self.sub = False
        self.source = "sim"
        self.note = ""
        self.geo = ""

    def label(self):
        return "sim"


def make(kind):
    if kind == "iid":
        return np.exp(0.3 * rng.standard_normal(N_DAYS)) * 100
    if kind == "ar":
        x = np.zeros(N_DAYS)
        e = 0.3 * rng.standard_normal(N_DAYS)
        for i in range(1, N_DAYS):
            x[i] = 0.9 * x[i - 1] + e[i]
        return np.exp(x) * 100
    return np.clip(100 + 15 * rng.standard_t(3, N_DAYS), 1, None)


def main():
    last = START + np.timedelta64(N_DAYS - 1, "D")
    scan_date = str((last + np.timedelta64(int(CFG["settle_days_default"]), "D")).astype(dt.date))
    print(f"scan date {scan_date}; settle {CFG['settle_days_default']} days; fresh window {CFG['fresh_days']['daily']} days")
    print("kind,rule,share_of_series_flagged,expected_flags_over_6797_series")
    for kind in ("iid", "ar", "t3"):
        hits = {"record": 0, "spike": 0, "weekly": 0, "any": 0}
        for _ in range(N_SERIES):
            s = S(make(kind))
            n, f = fs.settled(s, CFG, scan_date)
            got = set()
            for name, rule in (("record", fs.rule_record), ("spike", fs.rule_spike), ("weekly", fs.rule_weekly)):
                if rule(s, CFG, scan_date, n, f):
                    hits[name] += 1
                    got.add(name)
            hits["any"] += bool(got)
        for k, h in hits.items():
            print(f"{kind},{k},{h / N_SERIES:.4f},{6797 * h / N_SERIES:.1f}")


if __name__ == "__main__":
    main()
