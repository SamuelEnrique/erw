"""Session 7006 (chain 301): what the policy monitor's replication (replication/policy/replicate.py) found, policy
faults row 32: a held row of policy_actions the feed no longer lists and that carries no fields gets them from its own
row before the write, so the table and the monitor's file agree. Also: the replication's grouping on rows written here
(MADE UP: no such documents). No network, no data lock.

    python -m unittest tests.test_session7006_policy_replication -v
"""

import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for part in ("connectors", "policy", "derived"):
    sys.path.insert(0, os.path.join(ROOT, "warehouse", part))
import policy_sources as ps  # noqa: E402

spec = importlib.util.spec_from_file_location("rep_policy", os.path.join(ROOT, "replication", "policy", "replicate.py"))
REP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(REP)


def quiet(*a, **k):
    return None


class Row32FillBare(unittest.TestCase):
    def test_a_kept_row_without_fields_gets_them(self):
        cols = ps.COLS
        listed = pd.DataFrame([dict({c: "" for c in cols}, event_id="doe:1", event_date="2026-11-01", fields_from="title")])
        held = {"doe:2": dict({c: "" for c in cols}, event_id="doe:2", event_date="2026-10-08", agency="DOE",
                              action_type="press_release", status="news release",
                              title="DOE Announces $96 Million for Grid Projects", fields_from=""),
                "doe:1": dict({c: "" for c in cols}, event_id="doe:1", event_date="2026-11-01", fields_from="title")}
        out = ps.fill_bare(listed, held, quiet)
        self.assertEqual(list(out["event_id"]), ["doe:2", "doe:1"])
        r = out[out["event_id"] == "doe:2"].iloc[0]
        self.assertTrue(r["fields_from"])
        self.assertEqual(r["body"], "DOE")

    def test_nothing_bare_leaves_the_frame(self):
        f = pd.DataFrame([dict({c: "" for c in ps.COLS}, event_id="x", event_date="2026-01-01", fields_from="title")])
        self.assertIs(ps.fill_bare(f, {"x": {"fields_from": "title"}}, quiet), f)


class TheReplicationsGrouping(unittest.TestCase):
    def doc(self, e, day, docket, title="T", body="EPA"):
        return dict(event_id=e, event_date=day, docket=docket, body=body, agency=body, title=title)

    def test_rules(self):
        g = REP.group([self.doc("a", "2026-01-01", "CP26-1-000", body="FERC"), self.doc("b", "2026-02-01", "CP26-1-001", body="FERC"),
                       self.doc("c", "2026-09-17", "EPA-HQ-OAR-2025-0124;2060-AW55"),
                       self.doc("d", "2026-09-17", "EPA-HQ-OAR-2025-0124;2060-AX00"),
                       self.doc("e", "2026-03-01", "", title="Same Title"), self.doc("f", "2026-03-20", "", title="Same Title"),
                       self.doc("g", "2026-06-01", "", title="Same Title")])
        self.assertEqual(g["a"], g["b"])
        self.assertEqual(g["a"], "ferc:CP26-1")
        self.assertNotEqual(g["c"], g["d"])
        self.assertEqual(g["e"], g["f"])
        self.assertNotEqual(g["f"], g["g"], "a repeat more than 45 days on is a record of its own")


if __name__ == "__main__":
    unittest.main()
