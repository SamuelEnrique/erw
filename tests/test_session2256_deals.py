"""Session 2256 (chain 159): the six stated deals the second read found with no row, held by a fixture under both
settings of chain 156's ruling 2.

The second read (session 2249) found six deals of the audit's sample with no row. The recorded answers show the model
returned no deal for any of them (the story selection sent all six), for four reasons, not one:

    D022  "Black Hills plans $1.8 billion investment ..."   a plan: the prompt names this very headline as not a deal
    D031  "Sellafield selects partners ..."                  one party named, the partners not
    D061  "ONEOK, MPLX's 'Wellhead-to-Water' Deal Dominates"  a commentary headline that names a deal
    D071  "... Volta at $2.4 Billion Value"                  a valuation of an AI cloud, not a sum raised
    D084  "Shell to offload Jiffy Lube to Monomoy ..."       two named parties; the asset is not an energy asset
    D092  "Crescent Sells Non-Op D-J Assets ..."             one party named, the buyer not

ERW_DEALS_ONE_PARTY=on (warehouse/deals/extract.py) adds one sentence to the prompt; off, the default, leaves it as it
was. recorded_2249.json holds the answers with it off, recorded_2256.json (one call, USD 0.0240) with it on: the
owner's answer to the ruling is the default, and either is pinned here.
"""

import importlib.util
import json
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIX = os.path.join(ROOT, "tests", "fixtures", "deals")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import fixture  # noqa: E402

CLUSTER = {"D022": "news:da70551560f8939a", "D031": "news:f26abf1c5c49a563", "D061": "news:19821cdb2e72d9f6",
           "D071": "news:3af2a975e7eaa4a7", "D084": "news:691dcf77756dbdfa", "D092": "news:9fc7debc2394441a"}


def stories():
    with open(os.path.join(FIX, "stories_2256.json"), encoding="utf-8") as f:
        return json.load(f)


def by_cluster(rows):
    out = {}
    for r in rows.to_dict("records"):
        for sid in str(r["story_ids"]).split(";"):
            for n, c in CLUSTER.items():
                if sid == c or any(s["event_id"] == sid and s["cluster_id"] == c for s in stories()):
                    out.setdefault(n, []).append(r)
    return out


def system_with(value):
    with mock.patch.dict(os.environ, {"ERW_DEALS_ONE_PARTY": value}):
        return fixture.load_extract().SYSTEM


class ThePrompt(unittest.TestCase):
    def test_off_is_the_default_and_adds_nothing(self):
        env = {k: v for k, v in os.environ.items() if k != "ERW_DEALS_ONE_PARTY"}
        with mock.patch.dict(os.environ, env, clear=True):
            default = fixture.load_extract().SYSTEM
        self.assertEqual(default, system_with("off"))
        self.assertNotIn("one party named and the other not named", default)
        self.assertIn('is not returned.\n', default)

    def test_on_adds_the_one_sentence(self):
        on, off = system_with("on"), system_with("off")
        self.assertIn("one party named and the other not named", on)
        i = on.index(" A sale, an award or a raise")
        j = on.index("\n", i)
        self.assertEqual(on[:i] + on[j:], off)


class TheSix(unittest.TestCase):
    def test_the_fixture_holds_the_six_clusters(self):
        self.assertEqual({s["cluster_id"] for s in stories()}, set(CLUSTER.values()))
        self.assertEqual({s["fixture"] for s in stories()}, set(CLUSTER))

    def test_off_returns_none_of_them(self):
        rows, _ = fixture.replay("2249", stories=stories())
        self.assertEqual(len(rows), 0)

    def test_on_returns_the_one_party_deals_and_no_plan_commentary_or_valuation(self):
        with open(os.path.join(FIX, "recorded_2256.json"), encoding="utf-8") as f:
            rec = json.load(f)
        self.assertEqual(rec["one_party"], "on")
        self.assertLess(rec["usd"], 0.10)
        rows, _ = fixture.replay("2256")
        got = by_cluster(rows)
        self.assertEqual(set(got), {"D031", "D084", "D092"})
        crescent = got["D092"][0]
        self.assertEqual(crescent["seller"], "Crescent")
        self.assertEqual(crescent["buyer"], "")
        self.assertEqual(got["D031"][0]["buyer"], "Sellafield")
        self.assertEqual((got["D084"][0]["seller"], got["D084"][0]["buyer"]), ("Shell", "Monomoy Capital"))
        for n in ("D022", "D061", "D071"):
            self.assertNotIn(n, got)


if __name__ == "__main__":
    unittest.main()
