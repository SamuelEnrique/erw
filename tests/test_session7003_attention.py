"""Session 7003 (chain 301): the Attention and Friction indices' data faults, rows 2, 7, 16 and 18 of
docs/reviews/attention-faults-2026-11-11.md.

Energy Research Warehouse (ERW). A corpus written here (MADE UP: no such stories) over four weeks, the first not yet
classified, goes through attention_index.build and site_files: the week files carry `us` (row 2); "What rose" averages
only the classified weeks before, says how many, and writes no row where none is classified (row 7); the opposition
stories are counted as distinct events by news cluster beside the story count (row 16); each sector's figures over the
classified weeks together (row 18). No model, no file of the warehouse is read.

    python -m unittest tests.test_session7003_attention -v
"""

import json
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import attention_index as ai  # noqa: E402

NOW = "2026-11-16T09:00:00Z"
# weeks: 2026-10-19 (not classified), 2026-10-26, 2026-11-02, 2026-11-09
W0, W1, W2, W3 = "2026-10-19T00:00:00Z", "2026-10-26T00:00:00Z", "2026-11-02T00:00:00Z", "2026-11-09T00:00:00Z"


def story(i, date, cluster=""):
    return dict(event_id=f"news:{i}", event_date=date, source="Outlet", source_url=f"https://x.test/{i}", title=f"t{i}",
                summary=f"s{i}", significance="5", sector="other", headline=f"h{i}", cluster_id=cluster)


STORIES = {1: story(1, "2026-10-20T08:00:00Z"),                       # week 0: never classified
           2: story(2, "2026-10-27T08:00:00Z"), 3: story(3, "2026-10-28T08:00:00Z"),
           4: story(4, "2026-11-03T08:00:00Z", "c1"), 5: story(5, "2026-11-04T08:00:00Z", "c1"),
           6: story(6, "2026-11-05T08:00:00Z"),
           7: story(7, "2026-11-10T08:00:00Z")}


def row(i, sector, us, opposition=False, kind="none", tone=0):
    return dict(event_id=f"news:{i}", event_date=STORIES[i]["event_date"], source="Outlet", source_url=f"https://x.test/{i}",
                headline=f"h{i}", significance="5", scorer_sector="other", sector=sector, us=us, state="", place="",
                place_kind="", opposition=opposition, kind=kind, tone=tone, fixed="", model_id="claude-test",
                prompt_version=3, classified_at=NOW)


CLASSIFIED = [row(2, "datacenters", True), row(3, "gas", False),
              row(4, "datacenters", True, True, "lawsuit", -1), row(5, "datacenters", True, True, "lawsuit", -1),
              row(6, "datacenters", False, True, "protest", -1),
              row(7, "datacenters", True)]


class Built(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stories = pd.DataFrame(list(STORIES.values()))
        cls.links, cls.att, cls.fri, cls.weeks, cls.c = ai.build(stories, pd.DataFrame(CLASSIFIED), NOW)
        cls.dir = tempfile.TemporaryDirectory()
        ai.site_files(cls.links, cls.att, cls.fri, cls.weeks, cls.c, cls.dir.name, NOW, "note")
        with open(os.path.join(cls.dir.name, "data", "attention.json"), encoding="utf-8") as f:
            cls.data = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def test_row2_the_week_files_carry_us(self):
        with open(os.path.join(self.dir.name, "public", "attention", "stories", "2026-11-02.json"), encoding="utf-8") as f:
            wk = json.load(f)
        self.assertEqual(wk["columns"][-1], "us")
        us = {r[0]: r[-1] for r in wk["rows"]}
        self.assertEqual(us, {"news:4": 1, "news:5": 1, "news:6": 0})

    def test_row7_what_rose_counts_only_classified_weeks(self):
        wi = {w: i for i, w in enumerate(self.data["weeks"])}
        si = self.data["sectors"].index("datacenters")
        rows = [r for r in self.data["rising"] if r[1] == "sector" and r[2] == si]
        by_week = {r[0]: r for r in rows}
        self.assertNotIn(wi[W1], by_week, "the week before W1 is not classified: no row")
        r2 = by_week[wi[W2]]
        # W2: 3 of the week's 3 judged stories are datacenters (100); before: W1 only (1 of 2, 50); W0 is not a zero
        self.assertEqual((r2[3], r2[4], r2[5], r2[6]), (100.0, 50.0, 50.0, 1))
        r3 = by_week[wi[W3]]
        self.assertEqual((r3[4], r3[6]), (75.0, 2))

    def test_row16_opposition_events_by_cluster(self):
        f = self.fri[(self.fri["entity"] == "attention:datacenters:all") & (self.fri["ts_utc"] == W2)]
        got = dict(zip(f["variable"], f["value"]))
        self.assertEqual((got["opposition_stories"], got["opposition_events"]), (3, 2))
        si = self.data["sectors"].index("datacenters")
        cell = next(c for c in self.data["cells"] if c[0] == si and c[1] == 0 and self.data["weeks"][c[2]] == W2)
        self.assertEqual((cell[5], cell[8]), (3, 2))

    def test_row18_the_classified_weeks_together(self):
        si = self.data["sectors"].index("datacenters")
        t = next(x for x in self.data["together"] if x[0] == si and x[1] == 0)
        # datacenters over W1 to W3: 5 stories, 3 opposition (2 events), friction 60, tone -0.6; opposition -1, rest 0
        self.assertEqual(t, [si, 0, 3, 5, 3, 2, 60.0, -0.6, -1.0, 0.0])
        self.assertEqual(self.data["columns"]["together"][0], "sector")


class Row25Ahead(unittest.TestCase):
    def test_a_story_dated_after_it_was_read_is_in_no_week(self):
        st = [dict(story(1, "2026-11-03T08:00:00Z"), retrieved_at="2026-11-03T09:00:00Z"),
              dict(story(2, "2026-12-01T12:00:00Z"), retrieved_at="2026-10-19T16:11:44Z")]
        cl = [dict(row(4, "datacenters", True), event_id="news:1", event_date="2026-11-03T08:00:00Z"),
              dict(row(4, "datacenters", True), event_id="news:2", event_date="2026-12-01T12:00:00Z")]
        links, att, fri, weeks, c = ai.build(pd.DataFrame(st), pd.DataFrame(cl), NOW)
        self.assertEqual(list(weeks.index), [W2])
        self.assertEqual(list(links["story_event_id"]), ["news:1"])


if __name__ == "__main__":
    unittest.main()
