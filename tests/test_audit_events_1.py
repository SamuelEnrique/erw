"""Session 10225 (chain 710, the events audit, finding 1): "What the estimates say" prints "the weather terms account for
N percent" from a pooled regression that fits the four weather terms on the event days as well as the baseline days,
while each event day's estimate on the same block fits them on the baseline days alone. On Winter Storm Uri the two
rules give ERCOT +30,284 and -92,180 MWh a day: 80.56 percent under the page's, no share under the other. Words only:
the block and docs/methods/event_study.md say where the weather terms are fitted; no figure moves (the rule is
finding 2, the owner's ruling). docs/reviews/events-model-audit-2026-11-26.md.
"""
import csv
import datetime as dt
import os
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


def uri_rows():
    with open(ROWS, encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(l for l in fh if not l.startswith("#")) if r["event"] == "uri_2021"]
    dem = sorted((r["ts_utc"][:10], float(r["value"])) for r in rows if r["entity"] == "eia930:ERCO" and r["variable"] == "demand_mwh")
    wx = {}
    for r in rows:
        if r["entity"] in ("noaa:DFW", "noaa:IAH") and r["variable"] in ("hdd_65f", "cdd_65f"):
            wx.setdefault(r["ts_utc"][:10], {}).setdefault(r["variable"], []).append(float(r["value"]))
    w = {d: (np.mean(v["hdd_65f"]), np.mean(v["cdd_65f"])) for d, v in wx.items() if "hdd_65f" in v and "cdd_65f" in v}
    return [(d, y, w[d]) for d, y in dem if d in w]


def design(days, event, pooled):
    years = sorted({int(d[:4]) for d, e in zip(days, event) if not e})
    X = []
    for d, e in zip(days, event):
        wd = dt.date.fromisoformat(d).weekday()
        r = [1.0] + ([float(e)] if pooled else []) + [float(wd == k) for k in range(1, 7)]
        r += [0.0 if e else float(int(d[:4]) == y) - float(int(d[:4]) == years[-1]) for y in years[:-1]]
        X.append(r)
    return np.array(X)


class WhereTheWeatherTermsAreFitted(unittest.TestCase):
    def test_the_block_says_it(self):
        s = src("site", "components", "EventStudy.tsx")
        self.assertIn('<span data-weather-fit="1">{WEATHER_FIT_WORDS}</span>', s)
        for w in ["fitted on the event days and the baseline days together", "fits them on the baseline days alone",
                  "colder or hotter than any baseline day", "not a measured part of the effect that the weather caused"]:
            self.assertIn(w, s)

    def test_the_note_says_it(self):
        n = src("docs", "methods", "event_study.md")
        self.assertIn("### Where the weather terms are fitted (session 10225, 26 November 2026)", n)
        self.assertIn("so the pooled effect is then not a mean of the day effects", n)

    @unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
    def test_the_two_rules_give_uri_opposite_signs(self):
        r = uri_rows()
        days = [d for d, _, _ in r]
        y = np.array([v for _, v, _ in r])
        ev = np.array(["2021-02-07" <= d <= "2021-02-24" for d in days])
        Z = np.array([[h, h * h, c, c * c] for _, _, (h, c) in r])
        # the page's rule: one pooled indicator, the weather terms over every day (CDD is all but empty in February:
        # keep only the columns that raise the rank, in order)
        Xp = np.hstack([design(days, ev, True), Z])
        keep = []
        for j in range(Xp.shape[1]):
            if np.any(Xp[:, j]) and np.linalg.matrix_rank(Xp[:, keep + [j]]) > len(keep):
                keep.append(j)
        b, *_ = np.linalg.lstsq(Xp[:, keep], y, rcond=None)
        pooled_temp = b[keep.index(1)]
        self.assertAlmostEqual(pooled_temp, 30283.66, delta=1.0)
        # the day rule: the same columns fitted on the baseline days alone, the window's mean of value less fit
        Xd = np.hstack([design(days, ev, False), Z])
        kd = []
        for j in range(Xd.shape[1]):
            if np.any(Xd[~ev][:, j]) and np.linalg.matrix_rank(Xd[~ev][:, kd + [j]]) > len(kd):
                kd.append(j)
        bd, *_ = np.linalg.lstsq(Xd[~ev][:, kd], y[~ev], rcond=None)
        mean_day = float(np.mean(y[ev] - Xd[ev][:, kd] @ bd))
        self.assertAlmostEqual(mean_day, -92179.67, delta=1.0)
        self.assertGreater(pooled_temp, 0)
        self.assertLess(mean_day, 0)
        # and half the window was colder than any baseline day
        hdd = np.array([h for _, _, (h, _) in r])
        self.assertEqual(int((hdd[ev] > hdd[~ev].max()).sum()), 9)


if __name__ == "__main__":
    unittest.main()
