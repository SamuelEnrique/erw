"""Session 11407 (chain 770 part C), readied from session 10225's test of the events audit's finding 2
(wip/audit-events-2, docs/reviews/events-model-audit-2026-11-26.md): the weather share each event page prints is now
taken with the weather terms fitted on the baseline days alone, as each event day's estimate on the same block is
(site/lib/eventstudy.ts weatherShare: one less the window's mean day effect with the weather terms over the mean
without them). Uri (ERCOT) 80.56 percent becomes no share, CAISO 2020 70.47 becomes 63.86, Elliott (PJM) 65.33
becomes no share. The pooled rule's shares are kept here as the before. For the owner's ruling, not for landing alone.
"""
import csv
import datetime as dt
import os
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")
CASES = {  # event, entity, window, stations; the page's share and the share with the weather fitted on the baseline days
    "uri": ("uri_2021", "eia930:ERCO", ("2021-02-07", "2021-02-24"), ("noaa:DFW", "noaa:IAH"), 80.56, None),
    "caiso": ("caiso_heat_2020", "eia930:CISO", ("2020-08-10", "2020-08-24"), ("noaa:SAC", "noaa:LAX"), 70.47, 63.86),
    "elliott": ("elliott_2022", "eia930:PJM", ("2022-12-19", "2022-12-29"), ("noaa:PHL", "noaa:ORD"), 65.33, None),
}


def load():
    with open(ROWS, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(l for l in fh if not l.startswith("#"))]


def columns(days, ev, pooled, Z):
    years = sorted({int(d[:4]) for d, e in zip(days, ev) if not e})
    X = []
    for i, (d, e) in enumerate(zip(days, ev)):
        wd = dt.date.fromisoformat(d).weekday()
        r = [1.0] + ([float(e)] if pooled else []) + [float(wd == k) for k in range(1, 7)]
        r += [0.0 if e else float(int(d[:4]) == y) - float(int(d[:4]) == years[-1]) for y in years[:-1]]
        X.append(r + (list(Z[i]) if Z is not None else []))
    return np.array(X)


def kept(X):
    k = []
    for j in range(X.shape[1]):
        if np.any(X[:, j]) and np.linalg.matrix_rank(X[:, k + [j]]) > len(k):
            k.append(j)
    return k


def shares(rows, event, entity, win, stations):
    dem = sorted((r["ts_utc"][:10], float(r["value"])) for r in rows if r["event"] == event and r["entity"] == entity and r["variable"] == "demand_mwh")
    wx = {}
    for r in rows:
        if r["event"] == event and r["entity"] in stations and r["variable"] in ("hdd_65f", "cdd_65f"):
            wx.setdefault(r["ts_utc"][:10], {}).setdefault(r["variable"], []).append(float(r["value"]))
    w = {d: (np.mean(v["hdd_65f"]), np.mean(v["cdd_65f"])) for d, v in wx.items() if len(v) == 2}

    def pooled(days, y, ev, Z):
        X = columns(days, ev, True, Z)
        k = kept(X)
        b, *_ = np.linalg.lstsq(X[:, k], y, rcond=None)
        return b[k.index(1)]

    def day_mean(days, y, ev, Z):
        X = columns(days, ev, False, Z)
        k = kept(X[~ev])
        b, *_ = np.linalg.lstsq(X[~ev][:, k], y[~ev], rcond=None)
        return float(np.mean(y[ev] - X[ev][:, k] @ b))

    days0, y0 = [d for d, _ in dem], np.array([v for _, v in dem])
    ev0 = np.array([win[0] <= d <= win[1] for d in days0])
    t = [(d, v) for d, v in dem if d in w]
    days1, y1 = [d for d, _ in t], np.array([v for _, v in t])
    ev1 = np.array([win[0] <= d <= win[1] for d in days1])
    Z = np.array([[w[d][0], w[d][0] ** 2, w[d][1], w[d][1] ** 2] for d in days1])

    def share(a, b):
        return round((1 - a / b) * 100, 2) if np.sign(a) == np.sign(b) and abs(a) <= abs(b) else None
    return share(pooled(days1, y1, ev1, Z), pooled(days0, y0, ev0, None)), share(day_mean(days1, y1, ev1, Z), day_mean(days0, y0, ev0, None))


@unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
class TheWeatherShareDependsOnWhereTheTermsAreFitted(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load()

    def test_each_case(self):
        for name, (event, entity, win, st, page, base) in CASES.items():
            with self.subTest(name):
                a, b = shares(self.rows, event, entity, win, st)
                self.assertEqual(a, page, "the page's share")
                self.assertEqual(b, base, "the share with the weather fitted on the baseline days alone")


class ThePagePrintsTheBaselineFitShare(unittest.TestCase):
    @staticmethod
    def src(*p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
            return fh.read()

    def test_the_block_prints_the_day_rule(self):
        s = self.src("site", "components", "EventStudy.tsx")
        self.assertNotIn("(1 - lead.t.pooled.estimate / p.estimate) * 100", s)
        self.assertIn("const share = weatherShare(lead.s, lead.t);", s)
        self.assertIn('term="weather_share" field="pct" v={share}', s)
        self.assertIn("Fitted on the baseline days alone, the weather terms account for", s)

    def test_the_lib_takes_the_mean_of_the_day_effects(self):
        s = self.src("site", "lib", "eventstudy.ts")
        self.assertIn("export function weatherShare(s: Study, t: Study | null): number | null", s)
        self.assertIn("const a = mean(t.days), b = mean(s.days);", s)
        self.assertIn("Math.sign(a) === Math.sign(b) && Math.abs(a) <= Math.abs(b) ? (1 - a / b) * 100 : null", s)

    def test_the_value_check_recomputes_the_same_rule(self):
        s = self.src("site", "scripts", "check-values.mjs")
        self.assertIn('if (term === "weather_share") return weatherShare(s, t) ?? undefined;', s)
        self.assertNotIn("(1 - t.pooled.estimate / s.pooled.estimate) * 100", s)

    def test_the_note_says_it(self):
        n = self.src("docs", "methods", "event_study.md")
        self.assertIn("Uri (ERCOT) 80.56 percent is now no share, CAISO 2020 70.47 is now 63.86, Elliott (PJM) 65.33 is now no share", n)

    def test_no_dash(self):
        for p in (("site", "components", "EventStudy.tsx"), ("site", "lib", "eventstudy.ts"), ("docs", "methods", "event_study.md"),
                  ("tests", "test_ready_events_weather_share.py")):
            self.assertNotIn(chr(0x2014), self.src(*p), p)


if __name__ == "__main__":
    unittest.main()
