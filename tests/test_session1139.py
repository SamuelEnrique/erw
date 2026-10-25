"""Session 1139 (chain 076): the board's figures as functions, tested on the board's own saved rows.

Held here, with no request and no table: for every row of the site's board file (site/data/board.json) that has a value
and a whole-history file (site/public/board/s/<id>.json, the same build's), the builder's own `stats`
(warehouse/derived/board_page.py) run on that history gives back the row's latest value and date, its four moves, its
one-year range and, for a daily row, its 7-day and 30-day means, as the file holds them, to the files' rounding. So a change to a read
or to a figure's rule that would change what the board draws is caught by the suite, before a build. A row the file
holds but whose history file is older or newer than it (the two are written by one build, but page_keep.py may keep a
row of an earlier build) is counted, not judged; at least nine in ten rows of every group with values are judged.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import collections
import datetime as dt
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


def near(a, b, key=""):
    """Equal, a number within the files' rounding: the history files hold values to 4 decimals, and the board's file
    made its moves and means from the values before rounding, so a figure may differ in its last place (2 in 10,000),
    and a percent by its last place or, over a base near zero, by a thousandth of itself."""
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False
        if {"v", "ch", "pct"} <= a.keys() and all(isinstance(b[k], (int, float)) and not isinstance(b[k], bool) for k in ("v", "ch", "pct")) \
                and isinstance(a["pct"], (int, float)) and b["v"]:
            # session 2699: a move's percent is its change over its base, both held to 4 decimals, so over a small base the
            # rounding (5 in 100,000 on each) moves the percent by 100 * (5e-5 / |base| + 5e-5 * |change| / base ** 2), beyond a
            # thousandth of itself (caiso-as-caiso-as-price-dam-rd on 24 October 2026: base 0.0146, 2215.75 against 2218.13)
            v, ch = abs(b["v"]), abs(b["ch"])
            tol = 100 * (5e-5 / v + 5e-5 * ch / v ** 2)
            return all(near(a[k], b[k], k) for k in a if k != "pct") and (near(a["pct"], b["pct"], "pct") or abs(a["pct"] - b["pct"]) <= tol)
        return all(near(a[k], b[k], k) for k in a)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if key == "pct":
            return abs(a - b) <= 0.011 or abs(a - b) <= 1e-3 * abs(b)
        return abs(a - b) <= 2e-4 + 1e-6 * abs(b)
    return a == b


def history(rid):
    path = os.path.join(SITE, "public", "board", "s", rid + ".json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    t0 = dt.date.fromisoformat(s["t0"])
    return {t0 + dt.timedelta(days=d): v for d, v in zip(s["d"], s["v"])}, s


class ThePercentsRounding(unittest.TestCase):
    def test_a_small_base_allows_its_rounding_and_no_more(self):
        file = {"t": "2026-10-24", "v": 0.0146, "ch": 0.3235, "pct": 2218.13}
        self.assertTrue(near({"t": "2026-10-24", "v": 0.0146, "ch": 0.3235, "pct": 2215.75}, file))
        self.assertFalse(near({"t": "2026-10-24", "v": 0.0146, "ch": 0.3235, "pct": 2200.0}, file))
        self.assertFalse(near({"t": "2026-10-24", "v": 0.0150, "ch": 0.3235, "pct": 2215.75}, file))
        big = {"t": "2026-10-24", "v": 41.25, "ch": 3.1, "pct": 7.52}
        self.assertTrue(near({"t": "2026-10-24", "v": 41.25, "ch": 3.1, "pct": 7.515}, big))
        self.assertFalse(near({"t": "2026-10-24", "v": 41.25, "ch": 3.1, "pct": 7.6}, big))


class TheFiguresAreTheFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bp = builder()
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            cls.file = json.load(f)

    def test_every_row_is_stats_of_its_own_history(self):
        judged, skipped, wrong = collections.Counter(), collections.Counter(), []
        for r in self.file["rows"]:
            if r.get("status") != "ok" or not r.get("last") or r.get("freq") not in ("D", "W", "M"):
                continue
            h = history(r["id"])
            if h is None or h[0] and max(h[0]).isoformat() != r["last"]["t"]:
                skipped[r["group"]] += 1
                continue
            series, _ = h
            got = self.bp.stats(series, r["freq"])
            want = {k: r.get(k) for k in ("last", "moves", "range", "avg7", "avg30", "lo30", "hi30") if k in r}
            for k, v in want.items():
                if not near(got.get(k), v):
                    wrong.append(f"{r['id']} {k}: stats {got.get(k)}, file {v}")
            judged[r["group"]] += 1
        self.assertEqual(wrong[:10], [])
        self.assertGreater(sum(judged.values()), 500)
        for g in judged:
            self.assertGreaterEqual(judged[g], 0.9 * (judged[g] + skipped[g]), (g, judged[g], skipped[g]))

    def test_the_spread_rows_are_their_formulas(self):
        bp = self.bp
        da, gas = history("ercot-hb-hubavg-da"), history("eia-henry-hub-spot")
        spark = history("ercot-hb-hubavg-spark")
        if not (da and gas and spark):
            raise unittest.SkipTest("the spread's inputs are not in this copy")
        made = bp.spark(da[0], gas[0])
        common = [d for d in spark[0] if d in made]
        self.assertGreater(len(common), 300)
        self.assertTrue(all(abs(made[d] - spark[0][d]) < 1e-3 for d in common))
        g, d_, c = history("eia-eer-epmru-pf4-rgc-dpg-spot"), history("eia-eer-epd2dxl0-pf4-rgc-dpg-spot"), history("eia-wti-cushing-spot")
        crack = history("erw-crack-321-gulf-coast")
        if g and d_ and c and crack:
            made = bp.crack(g[0], d_[0], c[0])
            common = [x for x in crack[0] if x in made]
            self.assertGreater(len(common), 300)
            self.assertTrue(all(abs(made[x] - crack[0][x]) < 1e-2 for x in common))


if __name__ == "__main__":
    unittest.main()
