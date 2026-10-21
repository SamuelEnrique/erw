"""Session 531: the Roundup's deal rows, extracted once (the Roundup audit's fix 8, docs/reviews/roundup-audit-2026-10-21.md).

The second row came from the daily extraction: it sends only stories not yet checked, so a deal reported over several
days is sent again with its later stories, and the model's same_as was the only guard. warehouse/deals/deal_parties.py
now matches a deal the model did not mark against every deal held, in code, and refuses a deal between two governments.

The fixture is the audit's own example, the stories as warehouse/output/news_stories.csv holds them (titles, and a
summary where the extraction read a number from it): the Vistra loan of 2 and 5 October, the Amazon and Constellation
PPA of 30 September and 6 October, and the story of Russia's diesel of 9 October. The model is a fake that answers what
the real one answered on 4, 6 and 7 October (energy_deals as it stood on 21 October): no test reaches the model's API or
the network, and nothing is written outside a temporary folder.
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEALS_DIR = os.path.join(ROOT, "warehouse", "deals")
if DEALS_DIR not in sys.path:
    sys.path.insert(0, DEALS_DIR)

import deal_parties as dp  # noqa: E402


def load_extract():
    spec = importlib.util.spec_from_file_location("erw_deals_extract_s531", os.path.join(DEALS_DIR, "extract.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def story(sid, date, cluster, source, title, summary=""):
    return {"event_id": sid, "event_date": date, "event_type": "news", "source": source,
            "source_url": f"https://example.org/{sid.split(':')[1]}", "title": title, "summary": summary or title,
            "significance": "8", "sector": "deal", "cluster_id": cluster, "scored_at": "2026-10-10T00:00:00Z"}


VISTRA_1 = story("news:1f65c9dbe1b72828", "2026-10-02T19:14:10Z", "news:1f65c9dbe1b72828", "Bloomberg",
                 "US to Offer $4 Billion Loan for Vistra to Boost Nuclear Output")
AMAZON_1 = story("news:9067996958167ead", "2026-09-30T21:24:49Z", "news:9067996958167ead", "Reuters",
                 "Constellation, Amazon sign 20-year power deal to support Maryland nuclear plant")
AMAZON_2 = story("news:2f3e1d70e9826932", "2026-10-01T12:14:56Z", "news:9067996958167ead", "Power Engineering",
                 "Amazon signs PPA with Constellation for Maryland nuclear plant",
                 "20-year deal to see 190MW of capacity added to Calvert Cliffs plant")
VISTRA_2 = story("news:8080802f867bd3fe", "2026-10-05T16:46:31Z", "news:42140c47d3602872", "POWER",
                 "Vistra in Line for $4.2B DOE Loan Package to Uprate Nuclear Plants in Ohio and Pennsylvania",
                 "The Department of Energy's (DOE's) Office of Energy Dominance Financing (EDF) has announced a "
                 "conditional loan commitment of up to $4.2 billion to finance uprates and modernization at Vistra's "
                 "Beaver Valley nuclear plant in Pennsylvania and its Davis-Besse and Perry plants in Ohio.")
GOOGLE = story("news:d214d30f5edc7f4b", "2026-10-06T12:55:10Z", "news:30ea8886bcac164a", "Utility Dive",
               "Constellation-Google deal will bring $4.3B investment, 890 MW new nuclear to PJM",
               "Constellation Energy has signed 20-year power purchase agreements with both Google and Amazon in the "
               "last week, supporting almost 1.1 GW of nuclear expansions.")
RUSSIA = story("news:970b4455b281c749", "2026-10-09T15:43:00Z", "news:970b4455b281c749", "Reuters",
               "Trump says Russia to supply diesel to US and global markets")


def deal(deal_type, buyer, seller, asset, story_id, evidence, same_as="", **nums):
    d = {k: "" for k in ("mw", "mw_text", "mwh", "mwh_text", "dollars", "dollars_text", "price_value", "price_unit",
                         "price_text", "term_years", "term_text", "state", "country", "state_text", "country_text",
                         "status", "status_text", "announced_date", "technology")}
    d.update(deal_type=deal_type, buyer=buyer, seller=seller, other_parties=[], asset=asset, ai_power=False,
             confidence=0.85, evidence=evidence, story_id=story_id, same_as=same_as)
    d.update(nums)
    return d


# what the model answered, by cluster (energy_deals of 21 October: deal:29c1d07b7456f089, deal:6d416fb10be3a6f0,
# deal:70bf30d372e1d674, deal:55bb75196a90af9e, deal:3768a40d6f7e3242, deal:c6802080adad0a9b)
ANSWERS = {
    VISTRA_1["cluster_id"]: [deal("debt", "US", "Vistra", "nuclear output", VISTRA_1["event_id"], VISTRA_1["title"],
                                  dollars="4000000000", dollars_text="$4 Billion")],
    AMAZON_1["cluster_id"]: [deal("ppa", "Amazon", "Constellation", "Maryland nuclear plant", AMAZON_1["event_id"],
                                  AMAZON_1["title"], mw="190", mw_text="190MW")],
    VISTRA_2["cluster_id"]: [deal("debt", "Department of Energy", "Vistra",
                                  "Beaver Valley, Davis-Besse and Perry nuclear plants", VISTRA_2["event_id"],
                                  VISTRA_2["title"], dollars="4200000000", dollars_text="$4.2 billion")],
    GOOGLE["cluster_id"]: [deal("ppa", "Google", "Constellation Energy", "", GOOGLE["event_id"], GOOGLE["title"]),
                           deal("ppa", "Amazon", "Constellation Energy", "nuclear expansions", GOOGLE["event_id"],
                                GOOGLE["summary"])],
    RUSSIA["cluster_id"]: [deal("fuel_supply", "US", "Russia", "diesel", RUSSIA["event_id"], RUSSIA["title"],
                                confidence=0.6)],
}


class FakeMessages:
    def __init__(self, calls):
        self.calls = calls

    def create(self, **kw):
        user = kw["messages"][0]["content"]
        items = json.loads(user.split("Clusters (JSON):\n", 1)[1])
        self.calls.append(user)
        text = json.dumps({"results": [{"cluster_id": i["cluster_id"], "deals": ANSWERS[i["cluster_id"]]}
                                       for i in items]})
        return types.SimpleNamespace(
            usage=types.SimpleNamespace(input_tokens=10, output_tokens=10, cache_creation_input_tokens=0,
                                        cache_read_input_tokens=0),
            stop_reason="end_turn", content=[types.SimpleNamespace(type="text", text=text)], _request_id="req_test")


class Runs(unittest.TestCase):
    """Two days of the extraction on the audit's stories, with the fake model."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw_s531_")
        self.ex = load_extract()
        self.calls = []
        client = types.SimpleNamespace(messages=FakeMessages(self.calls))
        ip = self.ex.ip
        self.patches = [
            mock.patch.dict(os.environ, {"ERW_LOCK_EXEMPT": "1"}),
            mock.patch.object(ip, "OUT_DIR", self.tmp),
            mock.patch.object(ip, "LOG_DIR", os.path.join(self.tmp, "logs")),
            mock.patch.object(ip, "STATUS_DIR", os.path.join(self.tmp, "status")),
            mock.patch.object(ip, "load_key", lambda *a, **k: "test-key"),
            mock.patch.object(ip, "update_sources", lambda entries: None),
            mock.patch.object(self.ex, "CHECKED", os.path.join(self.tmp, "checked.csv")),
            mock.patch.object(self.ex, "pick_model", lambda client, log: "claude-test"),
            mock.patch.object(self.ex.llm, "client", lambda *a, **k: client),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def news(self, rows):
        cols = self.ex.NEWS_COLS
        pd.DataFrame([{c: r.get(c, "") for c in cols} for r in rows], columns=cols).to_csv(
            os.path.join(self.tmp, "news_stories.csv"), index=False, lineterminator="\n")

    def deals(self):
        return self.ex.ip.read_series(os.path.join(self.tmp, "energy_deals.csv"), self.ex.DEAL_COLS)

    def two_days(self):
        self.news([VISTRA_1, AMAZON_1, AMAZON_2])
        self.assertEqual(self.ex.main([]), 0)
        self.news([VISTRA_1, AMAZON_1, AMAZON_2, VISTRA_2, GOOGLE, RUSSIA])
        self.assertEqual(self.ex.main([]), 0)
        return self.deals()

    def test_the_second_rows_came_from_the_later_days_stories(self):
        # the extraction as it was: only the model's same_as, which it left empty on 6 and 7 October
        with mock.patch.object(dp, "find_same", lambda *a, **k: None), mock.patch.object(dp, "fault", lambda *a: None):
            d = self.two_days()
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(len(d), 6)
        self.assertEqual(int((d["seller"] == "Vistra").sum()), 2)
        self.assertEqual(int((d["buyer"] == "Amazon").sum()), 2)

    def test_each_deal_resolves_to_one_event_id(self):
        d = self.two_days()
        vistra = d[d["seller"] == "Vistra"]
        amazon = d[d["buyer"] == "Amazon"]
        self.assertEqual(len(vistra), 1)
        self.assertEqual(len(amazon), 1)
        self.assertEqual(vistra["event_id"].iloc[0], self.ex.deal_id(VISTRA_1["event_id"], 0))
        self.assertEqual(amazon["event_id"].iloc[0], self.ex.deal_id(AMAZON_1["event_id"], 0))
        self.assertIn(VISTRA_2["event_id"], vistra["story_ids"].iloc[0].split(";"))
        self.assertIn(GOOGLE["event_id"], amazon["story_ids"].iloc[0].split(";"))
        # the kept rows keep their own fields: the first story's sum and date
        self.assertEqual(vistra["dollars"].iloc[0], "4000000000")
        self.assertEqual(amazon["mw"].iloc[0], "190")
        # Google's deal with Constellation is its own
        self.assertEqual(int((d["buyer"] == "Google").sum()), 1)

    def test_us_and_russia_for_the_export_ban_story_is_no_deal(self):
        d = self.two_days()
        self.assertFalse(d["parties"].str.contains("Russia").any())
        self.assertEqual(len(d), 3)
        chk = pd.read_csv(os.path.join(self.tmp, "checked.csv"), dtype=str, keep_default_na=False)
        self.assertIn(RUSSIA["event_id"], set(chk["story_id"]))   # checked, so it is not sent again
        logs = ""
        for f in sorted(os.listdir(os.path.join(self.tmp, "logs"))):
            with open(os.path.join(self.tmp, "logs", f), encoding="utf-8") as fh:
                logs += fh.read()
        self.assertIn("both governments", logs)
        self.assertIn("by the code's match", logs)


class Rules(unittest.TestCase):
    def test_a_party_with_words_added_is_the_same_party(self):
        self.assertTrue(dp.same_party("Constellation", "Constellation Energy"))
        self.assertTrue(dp.same_party("Vistra Corp", "Vistra"))
        self.assertFalse(dp.same_party("Amazon", "Google"))
        self.assertFalse(dp.same_party("Energy Transfer", "Energy"))   # a generic word alone is no party
        self.assertTrue(dp.same_party("Energy Transfer", "Energy Transfer LP"))

    def test_the_us_government_is_one_party(self):
        for n in ("US", "U.S.", "United States", "Department of Energy", "DOE", "US Department of Energy",
                  "Pentagon", "US government"):
            self.assertEqual(dp.government(n), "us", n)
        self.assertEqual(dp.government("Russia"), "russia")
        self.assertIsNone(dp.government("Vistra"))
        self.assertIsNone(dp.government("Georgia Power"))
        self.assertFalse(dp.same_party("US", "Russia"))

    def base(self, **kw):
        d = {"event_id": "deal:a", "deal_type": "ppa", "buyer": "Amazon", "seller": "Constellation",
             "asset": "Maryland nuclear plant", "dollars": "", "event_date": "2026-09-30T21:24:49Z"}
        d.update(kw)
        return d

    def test_same_deal_needs_type_parties_window_asset_and_sum(self):
        a = self.base()
        self.assertTrue(dp.same_deal(a, self.base(event_id="deal:b", asset="nuclear expansions",
                                                  seller="Constellation Energy", event_date="2026-10-06")))
        self.assertTrue(dp.same_deal(a, self.base(buyer="Constellation", seller="Amazon")))   # either order
        self.assertFalse(dp.same_deal(a, self.base(deal_type="m_and_a")))
        self.assertFalse(dp.same_deal(a, self.base(buyer="Google")))
        self.assertFalse(dp.same_deal(a, self.base(buyer="")))
        self.assertFalse(dp.same_deal(a, self.base(event_date="2026-11-15")))   # 46 days
        self.assertFalse(dp.same_deal(a, self.base(asset="Calvert Cliffs")))    # no word shared
        self.assertTrue(dp.same_deal(a, self.base(asset="")))
        # session 113's doubtful pair: USD 200 and 15 billion are not one deal; 4.0 and 4.2 billion are
        self.assertFalse(dp.same_deal(self.base(dollars="200000000000"), self.base(dollars="15000000000")))
        self.assertTrue(dp.same_deal(self.base(dollars="4000000000"), self.base(dollars="4200000000")))

    def test_find_same_takes_the_nearest(self):
        held = [self.base(event_id="deal:far", event_date="2026-09-10"),
                self.base(event_id="deal:near", event_date="2026-09-29"),
                self.base(event_id="deal:other", buyer="Google")]
        self.assertEqual(dp.find_same(self.base(event_id="deal:new", event_date="2026-10-01"), held), "deal:near")
        self.assertIsNone(dp.find_same(self.base(event_id="deal:new", buyer="Meta"), held))

    def test_fault_and_unnamed(self):
        text = RUSSIA["title"]
        self.assertIn("both governments", dp.fault({"buyer": "US", "seller": "Russia"}, text))
        self.assertIsNone(dp.fault({"buyer": "Department of Energy", "seller": "Vistra"}, VISTRA_2["title"]))
        self.assertIsNone(dp.fault({"buyer": "Fervo Energy", "seller": ""}, "Fervo Energy raises"))
        self.assertEqual(dp.unnamed({"buyer": "investors", "seller": "Fervo Energy"},
                                    "Fervo Energy raises USD 462 million"), ["buyer"])
        self.assertEqual(dp.unnamed({"buyer": "Amazon", "seller": "Constellation Energy"}, GOOGLE["summary"]), [])
        self.assertEqual(dp.unnamed({"buyer": "Department of Energy", "seller": "Vistra"}, VISTRA_1["title"]), [])

    def test_the_seeder_reads_the_same_lists(self):
        with open(os.path.join(ROOT, "warehouse", "companies", "seed_from_deals.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("from deal_parties import COUNTRIES, PUBLIC_BODIES", src)
        self.assertNotIn('"afghanistan"', src)
        self.assertIn("russia", dp.COUNTRIES)


class Words(unittest.TestCase):
    def test_no_dash(self):
        dash = chr(0x2014)
        for p in (os.path.join(DEALS_DIR, "deal_parties.py"), os.path.join(DEALS_DIR, "extract.py"), __file__,
                  os.path.join(ROOT, "warehouse", "companies", "seed_from_deals.py")):
            with open(p, encoding="utf-8") as fh:
                self.assertNotIn(dash, fh.read(), p)


if __name__ == "__main__":
    unittest.main()
