"""Session 3402 (chain 202): the Attention and Friction indices counted by code from classified rows.

A corpus of ten stories over two weeks, classified by hand here, goes through attention_index.build; every number the
tables hold is worked out by hand in the assertions' comments. No model, no file of the warehouse is read.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import attention_index as ai  # noqa: E402

NOW = "2026-11-06T20:00:00Z"
# week A: Monday 2026-10-26 (stories dated 26 Oct to 1 Nov); week B: Monday 2026-11-02
W_A, W_B = "2026-10-26T00:00:00Z", "2026-11-02T00:00:00Z"


def story(i, date, significance="5", headline=""):
    return dict(event_id=f"news:{i}", event_date=date, source="Outlet", source_url=f"https://x.test/{i}", title=f"t{i}",
                summary=f"s{i}", significance=significance, sector="other", headline=headline or f"h{i}")


def row(i, sector, us, state="", opposition=False, kind="none", tone=0, place="", place_kind=""):
    return dict(event_id=f"news:{i}", event_date=STORIES[i]["event_date"], source="Outlet", source_url=f"https://x.test/{i}",
                headline=f"h{i}", significance=STORIES[i]["significance"], scorer_sector="other", sector=sector, us=us,
                state=state, place=place, place_kind=place_kind, opposition=opposition, kind=kind, tone=tone, fixed="",
                model_id="claude-test", prompt_version=2, classified_at=NOW)


STORIES = {
    1: story(1, "2026-10-26T08:00:00Z"), 2: story(2, "2026-10-28T08:00:00Z"), 3: story(3, "2026-11-01T23:00:00Z"),
    4: story(4, "2026-10-30T08:00:00Z", significance="0"),  # scored 0, not sent: judged as not energy
    5: story(5, "2026-10-31T08:00:00Z"),                    # never classified, not scored 0: in stories_week only
    6: story(6, "2026-11-02T00:00:00Z"), 7: story(7, "2026-11-04T08:00:00Z"), 8: story(8, "2026-11-08T23:59:59Z"),
    9: story(9, "2026-11-05T08:00:00Z"), 10: story(10, "2026-11-06T08:00:00Z"),
}
CLASSIFIED = [
    row(1, "datacenters", True, "TX", opposition=True, kind="moratorium", tone=-1, place="Williamson County", place_kind="county"),
    row(2, "datacenters", True, "TX", tone=1),
    row(3, "gas", False, tone=0),
    row(6, "datacenters", True, "VA", opposition=True, kind="lawsuit", tone=-1),
    row(7, "datacenters", True, "VA", opposition=True, kind="protest", tone=-1),
    row(8, "not_energy", True, tone=0),
    row(9, "other_energy", True, "", tone=1),
    row(10, "solar_wind", False, tone=0),
]


def val(df, entity, variable, week):
    r = df[(df["entity"] == entity) & (df["variable"] == variable) & (df["ts_utc"] == week)]
    assert len(r) == 1, (entity, variable, week, len(r))
    return r["value"].iloc[0]


class WeekOf(unittest.TestCase):
    def test_monday_to_sunday_in_utc(self):
        when = pd.to_datetime(pd.Series(["2026-11-02T00:00:00Z", "2026-11-08T23:59:59Z", "2026-11-09T00:00:00Z", "2026-11-01T23:00:00Z"]), utc=True)
        self.assertEqual(ai.week_of(when).tolist(), [W_B, W_B, "2026-11-09T00:00:00Z", W_A])


class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stories = pd.DataFrame(list(STORIES.values())).astype(str)
        classified = pd.DataFrame(CLASSIFIED)
        cls.links, cls.att, cls.fri, cls.weeks, cls.c = ai.build(stories, classified, NOW)

    def test_denominators(self):
        # week A holds stories 1 to 5: 3 classified (1, 2, 3), 1 scored 0 and unsent (4), 1 unclassified (5)
        self.assertEqual(val(self.att, "attention:corpus:all", "stories_week", W_A), 5)
        self.assertEqual(val(self.att, "attention:corpus:all", "stories_classified", W_A), 3)
        self.assertEqual(val(self.att, "attention:corpus:all", "stories_unsent_zero", W_A), 1)
        self.assertEqual(val(self.att, "attention:corpus:all", "stories_judged", W_A), 4)
        # week B holds 6 to 10, all classified
        self.assertEqual(val(self.att, "attention:corpus:all", "stories_judged", W_B), 5)

    def test_attention_index_is_the_share_of_the_judged_stories(self):
        # datacenters, every place, week A: stories 1 and 2 of 4 judged = 50 percent
        self.assertEqual(val(self.att, "attention:datacenters:all", "stories", W_A), 2)
        self.assertEqual(val(self.att, "attention:datacenters:all", "attention_index", W_A), 50.0)
        # datacenters in Texas, week A: the same two stories; week B has none, so no Texas row
        self.assertEqual(val(self.att, "attention:datacenters:US-TX", "attention_index", W_A), 50.0)
        self.assertTrue(self.att[(self.att["entity"] == "attention:datacenters:US-TX") & (self.att["ts_utc"] == W_B)].empty)
        # energy (any energy sector) week B: 6, 7, 9, 10 of 5 judged = 80 percent; not_energy (8) is left out
        self.assertEqual(val(self.att, "attention:energy:all", "attention_index", W_B), 80.0)
        # energy about the US, week B: 6, 7, 9 = 60 percent
        self.assertEqual(val(self.att, "attention:energy:US", "attention_index", W_B), 60.0)

    def test_tone_mean(self):
        # datacenters week A: tones -1 and 1, mean 0
        self.assertEqual(val(self.att, "attention:datacenters:all", "tone_mean", W_A), 0.0)
        # datacenters week B: -1 and -1
        self.assertEqual(val(self.att, "attention:datacenters:US-VA", "tone_mean", W_B), -1.0)

    def test_friction_index_is_the_share_of_the_cell(self):
        # datacenters week A: 1 opposition story of 2 = 50 percent; week B: 2 of 2 = 100
        self.assertEqual(val(self.fri, "attention:datacenters:all", "opposition_stories", W_A), 1)
        self.assertEqual(val(self.fri, "attention:datacenters:all", "friction_index", W_A), 50.0)
        self.assertEqual(val(self.fri, "attention:datacenters:US-VA", "friction_index", W_B), 100.0)
        # the kinds: week A one moratorium; week B one lawsuit and one protest
        self.assertEqual(val(self.fri, "attention:datacenters:all", "kind_moratorium", W_A), 1)
        self.assertEqual(val(self.fri, "attention:datacenters:all", "kind_lawsuit", W_B), 1)
        self.assertEqual(val(self.fri, "attention:datacenters:all", "kind_protest", W_B), 1)
        self.assertEqual(val(self.fri, "attention:datacenters:all", "kind_rate_case", W_B), 0)
        # gas week A: one story, no opposition
        self.assertEqual(val(self.fri, "attention:gas:all", "friction_index", W_A), 0.0)

    def test_series_columns_units_and_geo(self):
        for df in (self.att, self.fri):
            self.assertEqual(list(df.columns), ai.SERIES_COLS)
            self.assertTrue((df["freq"] == "P1W").all())
            self.assertTrue(set(df["unit"]) <= {"count", "pct", "ratio"})
            self.assertFalse(df.duplicated(["entity", "variable", "ts_utc"]).any())
        geo = dict(zip(self.att["entity"], self.att["geo"]))
        self.assertEqual(geo["attention:datacenters:US-TX"], "US-TX")
        self.assertEqual(geo["attention:datacenters:US"], "US")
        self.assertEqual(geo["attention:datacenters:all"], "")

    def test_link_rows_one_a_classified_story_without_outlet_text(self):
        self.assertEqual(len(self.links), 8)
        self.assertEqual(list(self.links.columns), ai.LINK_COLS)
        self.assertNotIn("title", self.links.columns)
        self.assertNotIn("summary", self.links.columns)
        r = self.links.set_index("story_event_id").loc["news:1"]
        self.assertEqual((r["event_id"], r["week"], r["geo"], r["opposition"], r["kind"], r["place"]),
                         ("attn:1", W_A, "US-TX", "true", "moratorium", "Williamson County"))
        r3 = self.links.set_index("story_event_id").loc["news:3"]
        self.assertEqual((r3["us"], r3["geo"]), ("false", ""))


class ReadClassified(unittest.TestCase):
    def test_the_newest_classification_of_a_story_is_kept(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw = os.path.join(tmp, "raw")
            os.makedirs(raw)
            a = dict(CLASSIFIED[1], classified_at="2026-11-06T10:00:00Z", sector="gas")
            b = dict(CLASSIFIED[1], classified_at="2026-11-06T12:00:00Z", sector="datacenters")
            with open(os.path.join(raw, "classified_1.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps(b) + "\n" + json.dumps(a) + "\n")
            c = ai.read_classified(raw, tmp)
            self.assertEqual(len(c), 1)
            self.assertEqual(c["sector"].iloc[0], "datacenters")


if __name__ == "__main__":
    unittest.main()
