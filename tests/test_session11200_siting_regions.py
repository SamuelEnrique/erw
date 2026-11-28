"""Session 11200 (chain 760, part B): the siting regions files and their builder.

The files (site/data/siting/regions/) follow docs/state/page_files_siting_regions.md: every count is a cell with
its unit, period and source; a held count carries no figure; table.json takes each value from the place's own file;
nothing ranks or scores a place. The builder's small rules are tested on their own.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import siting_regions as sr  # noqa: E402

DIR = os.path.join(ROOT, "site", "data", "siting", "regions")
HELD_KINDS = ("license needed:", "paused:", "not published:", "not held:", "not a market:", "too few:")


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def cells(obj, path=""):
    """Every cell (a dict with v, unit, period, src, held) inside a section, with its path."""
    if isinstance(obj, dict):
        if set(obj) >= {"v", "unit", "period", "src", "held"}:
            yield path, obj
            return
        for k, v in obj.items():
            yield from cells(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from cells(v, f"{path}[{i}]")


class TheRules(unittest.TestCase):
    def test_threshold_reads_the_first_figure_in_mw_or_kw(self):
        self.assertEqual(sr.threshold_mw("75 MW or more at a single site"), 75.0)
        self.assertEqual(sr.threshold_mw("50,000 kW of total Reserved Capacity"), 50.0)
        self.assertEqual(sr.threshold_mw("Over 20 MW aggregate at the same premises"), 20.0)
        self.assertEqual(sr.threshold_mw('2 MW: "two megawatts or greater" (web page)'), 2.0)

    def test_threshold_leaves_what_is_not_a_size(self):
        self.assertIsNone(sr.threshold_mw("not published"))
        self.assertIsNone(sr.threshold_mw("no MW threshold: availability at EAL's discretion; Billing kW not less than 100 kW"))
        self.assertIsNone(sr.threshold_mw("10 MVA or more of new or expanded data center capacity"))
        self.assertIsNone(sr.threshold_mw("No threshold: customer-specific special contracts for a 1.0 GW data center"))
        self.assertIsNone(sr.threshold_mw(""))

    def test_periods_are_twelve_whole_months(self):
        from datetime import date
        P = sr.Periods(date(2026, 11, 28))
        self.assertEqual((P.prior_start, P.start, P.end), ("2024-11-01", "2025-11-01", "2026-11-01"))
        self.assertEqual(P.label, "2025-11-01..2026-10-31")
        self.assertEqual(P.hours, 8760)

    def test_a_region_sums_members_that_report(self):
        import pandas as pd
        hours = [f"t{i}" for i in range(10)]
        rows = [("A", t, float(i)) for i, t in enumerate(hours)]
        rows += [("B", t, 10.0 * i) for i, t in enumerate(hours) if t != "t5"]   # 9 of 10 hours: counted
        rows += [("C", "t0", 5.0)]                                              # 1 of 10 hours: left out
        f = pd.DataFrame(rows, columns=["ba", "ts_utc", "v"])
        s = sr.members_sum(f, ["A", "B", "C"])
        want = {t: 11.0 * i for i, t in enumerate(hours) if t != "t5"}        # B misses t5: t5 dropped
        self.assertEqual(dict(zip(s.ts_utc, s.v)), want)

    def test_no_score_or_rank_anywhere(self):
        import re
        words = json.dumps([sr.SECTIONS, sr.TABLE_COLUMNS]).lower()
        for w in (r"\bscore\b", r"\brank", r"\bbest\b", r"\bweight"):
            self.assertIsNone(re.search(w, words), w)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the regions files are not built here")
class TheFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load("index.json")
        cls.table = load("table.json")
        # the contract's example writes one place file of its three places
        cls.places = {p["id"]: load(p["file"]) for p in cls.index["places"]
                      if not cls.index.get("example") or os.path.exists(os.path.join(DIR, p["file"]))}

    def test_the_index_lists_every_kind(self):
        kinds = [p["kind"] for p in self.index["places"]]
        if self.index.get("example"):
            self.assertEqual(sorted(set(kinds)), ["ba", "operator", "region"])
            return
        self.assertEqual(kinds.count("region"), 13)
        self.assertEqual(kinds.count("operator"), 7)
        self.assertGreater(kinds.count("ba"), 0)
        for p in self.index["places"]:
            if p["kind"] == "ba":
                self.assertGreaterEqual(p["peak_mw"], self.index["ba_floor_mw"], p["id"])
        self.assertEqual([s["id"] for s in self.index["sections"]], [s[0] for s in sr.SECTIONS])

    def test_every_cell_is_whole_and_a_held_one_has_no_figure(self):
        for pid, doc in self.places.items():
            for path, c in cells(doc["sections"]):
                if c["held"]:
                    self.assertIsNone(c["v"], (pid, path))
                    self.assertTrue(c["held"].startswith(HELD_KINDS), (pid, path, c["held"]))
                self.assertIn(c["src"], doc["sources"], (pid, path))
                self.assertTrue(c["unit"], (pid, path))

    def test_an_internal_source_never_shows_a_figure(self):
        for pid, doc in self.places.items():
            for path, c in cells(doc["sections"]):
                if doc["sources"][c["src"]]["license"] == "internal":
                    self.assertIsNone(c["v"], (pid, path))

    def test_the_table_takes_each_value_from_the_place_file(self):
        cols = [c["key"] for c in self.table["columns"]]
        self.assertEqual(cols, [k for k, _s, _l, _u in sr.TABLE_COLUMNS])
        self.assertEqual([r["id"] for r in self.table["rows"]], [p["id"] for p in self.index["places"]])
        if self.index.get("example"):
            return
        for r in self.table["rows"]:
            secs = self.places[r["id"]]["sections"]
            ref = next(p["ref_hub"] for p in self.index["places"] if p["id"] == r["id"])
            for i, key in enumerate(cols):
                sec, k = key.split(".", 1)
                if sec == "price":
                    mk = "real-time" if k.endswith("_rt") else "day-ahead"
                    base = k.rsplit("_", 1)[0]
                    hub = [h for h in secs["price"]["hubs"] if h.get("hub_id") == ref and h.get("market") == mk]
                    want = hub[0][base]["v"] if hub else None
                elif key == "congestion.share_pct":
                    hub = [h for h in secs["congestion"]["hubs"] if h["hub_id"] == ref]
                    want = hub[0]["congestion_share_pct"]["v"] if hub else None
                else:
                    want = secs[sec][k]["v"]
                self.assertEqual(r["v"][i], want, (r["id"], key))
                if r["v"][i] is None:
                    self.assertTrue(r["cell"][str(i)]["held"], (r["id"], key))


if __name__ == "__main__":
    unittest.main()
