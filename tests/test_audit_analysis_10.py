"""Audit of Automated Analysis, finding 10 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): the
scanner's rules flag series with nothing in them.

The engine's own findings_scanner.rule_record, rule_spike, rule_weekly and settled, with warehouse/config/scanner.yaml,
on simulated daily series that are persistent (log AR(1), rho 0.9) and hold no event: more than 0.1 percent of series
raise a flag on one scan. Across the 6,797 series of the first run that is about 30 a day (the audit's a6), before the
cap of 12 drafts. Passes on main; printing the count chance gives is the owner's ruling.

No table, no request, no model call; the environment is read, never set."""
import datetime as dt
import os
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
START = np.datetime64("2020-01-01", "D")
N_DAYS = 2100


class S:
    def __init__(self, v):
        self.table, self.key, self.key_str = "audit_sim", {"entity": "sim", "variable": "x"}, "sim|x"
        self.days = START + np.arange(len(v)).astype("timedelta64[D]")
        self.v = self.lo = self.hi = v
        self.unit, self.grain, self.sub, self.source, self.note, self.geo = "MW", "daily", False, "sim", "", ""

    def label(self):
        return "sim"


class ScannerFlagsNoise(unittest.TestCase):
    def test_persistent_series_raise_flags(self):
        import findings_scanner as fs
        cfg = fs.load_config()
        last = START + np.timedelta64(N_DAYS - 1, "D")
        scan_date = str((last + np.timedelta64(int(cfg["settle_days_default"]), "D")).astype(dt.date))
        rng = np.random.default_rng(10204)
        trials, flagged = 2500, 0
        for _ in range(trials):
            e = 0.3 * rng.standard_normal(N_DAYS)
            x = np.zeros(N_DAYS)
            for i in range(1, N_DAYS):
                x[i] = 0.9 * x[i - 1] + e[i]
            s = S(np.exp(x) * 100)
            n, f = fs.settled(s, cfg, scan_date)
            flagged += any(rule(s, cfg, scan_date, n, f) for rule in (fs.rule_record, fs.rule_spike, fs.rule_weekly))
        self.assertGreater(flagged / trials, 0.001, flagged / trials)


if __name__ == "__main__":
    unittest.main()
