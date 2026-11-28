"""Audit of /equities, finding 2 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): one business is
listed twice in the same segment.

Plains GP Holdings (PAGP) consolidates Plains All American Pipeline (PAA), and SunocoCorp (SUNC) consolidates Sunoco LP
(SUN): each pair files the very same revenue for every period both filed (87 of 87, and 6 of 6), from two filings, and
both companies of each pair sit in the same segments. With finding 1's three utilities beside their parents, a segment
counts one business twice: of the 3-month revenue filed for the quarter to 30 September 2026, 10.4 percent of
midstream's sum, 4.4 percent of integrated and refining's, 8.4 percent of regulated utilities' and 6.3 percent of
independent power's is a second count. The page prints no segment sum and no segment line today; an equal-weight line
built by the contract's rule (docs/state/page_files_equities.md) would count each pair as two companies. The list's
download lets a reader sum them.

The test shows it on main's files (it passes on main). Which listing of a pair a segment keeps is a rule for Samuel's
ruling: nothing is changed."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "site", "data", "equities")
TWICE = [("PAGP", "PAA"), ("SUNC", "SUN")]
WITH_ONE = [("CMS", "CMS-PB"), ("EIX", "SCE-PG"), ("PCG", "PCG-PE")]


def load(rel):
    with open(os.path.join(D, rel), encoding="utf-8") as f:
        return json.load(f)


def revenue(tk):
    s = load(f"series/{tk}.json")
    out = {}
    for r in s["quarterly"]:
        r = dict(zip(s["quarterly_columns"], r))
        if r["revenue"] is not None:
            k = (r["period_end"], r["months"])
            if k not in out or (r["filed"], r["accession"]) > out[k][1]:
                out[k] = (r["revenue"], (r["filed"], r["accession"]), r["accession"])
    return out


class OneBusinessTwice(unittest.TestCase):
    def test_holding_and_partnership_file_one_revenue(self):
        idx = {c["ticker"]: c for c in load("index.json")["companies"]}
        for a, b in TWICE:
            ra, rb = revenue(a), revenue(b)
            both = set(ra) & set(rb)
            self.assertGreaterEqual(len(both), 6, (a, b))
            self.assertTrue(all(ra[k][0] == rb[k][0] for k in both), f"{a} and {b}: one revenue in every period")
            self.assertTrue(all(ra[k][2] != rb[k][2] for k in both), f"{a} and {b}: two filings")
            self.assertEqual(idx[a]["segments"], idx[b]["segments"])

    def test_the_second_count_in_each_segment(self):
        idx = load("index.json")
        want = {"midstream_pipelines": 10.4, "integrated_oil_gas": 4.4, "refining": 4.4, "regulated_utilities": 8.4,
                "independent_power": 6.3}
        for sid, pct in want.items():
            cs = [c for c in idx["companies"] if sid in c["segments"]]
            q = {c["ticker"]: c["newest_filed"]["revenue"]["v"] for c in cs if c.get("newest_filed")
                 and c["newest_filed"]["period_end"] == "2026-09-30" and c["newest_filed"]["revenue"]
                 and c["newest_filed"]["revenue"]["months"] == 3}
            twice = sum(q[b] for a, b in TWICE + WITH_ONE if a in q and b in q)
            self.assertAlmostEqual(twice / sum(q.values()) * 100, pct, delta=0.05, msg=sid)


if __name__ == "__main__":
    unittest.main()
