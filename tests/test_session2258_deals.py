"""Session 2258 (chain 159): a deal's kind where the rule called it "other".

The second read (session 2249) found 8 of 106 sampled deals with a wrong kind: data-center leases and a data-center
expansion kept as "other" (D007, D050, D053), a credit backstop and credit support kept as "other" (D001, D013), a
stake exit kept as "other" (D020), "Illinois Nuclear Upgrades" (D012) and a joint venture whose other story says it
"May Restart Abandoned US Nuclear Project" (D080). warehouse/deals/fields.py reads a deal the rule would call "other"
once more (other_of), takes "nuclear upgrades" as an uprate's words, and a nuclear deal whose stories name a restart or
an uprate. On the replayed 2249 answers: 8 to 0, and no other row of the 82 changes kind.
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import fields  # noqa: E402
import fixture  # noqa: E402


class TheRule(unittest.TestCase):
    def kind(self, **d):
        text = d.pop("text", "")
        return fields.kind_of(d, text)[0]

    def test_the_eight_forms(self):
        self.assertEqual(self.kind(deal_type="lease", asset="data center", buyer="Nvidia",
                                   evidence="Nvidia to Lease Data Center Funded by $3.8 Billion of Junk Bonds"), "compute_capacity")
        self.assertEqual(self.kind(deal_type="other", asset="credit backstop for TeraWulf data center in Kentucky",
                                   seller="Google"), "project_finance")
        self.assertEqual(self.kind(deal_type="other", asset="Hess Midstream stake", seller="Chevron"), "m_and_a")
        self.assertEqual(self.kind(deal_type="other", asset="Texas data center expansion", buyer="OpenAI",
                                   seller="Oracle"), "compute_capacity")
        self.assertEqual(self.kind(deal_type="other", asset="Illinois nuclear upgrades", technology="nuclear"),
                         "nuclear_restart_uprate")
        self.assertEqual(self.kind(deal_type="joint_venture", asset="nuclear power joint venture", technology="nuclear",
                                   text="new brookfield venture may restart abandoned us nuclear project"),
                         "nuclear_restart_uprate")

    def test_what_is_sold_to_a_data_center_is_not_its_capacity(self):
        self.assertEqual(self.kind(deal_type="other", asset="optical fiber for data centers", buyer="A", seller="B"), "other")
        self.assertEqual(self.kind(deal_type="other", asset="local energy infrastructure for Louisiana data center",
                                   buyer="A", seller="B"), "other")
        self.assertEqual(self.kind(deal_type="other", asset="data center project", seller="G42"), "other")

    def test_a_form_the_rule_already_reads_is_kept(self):
        self.assertEqual(self.kind(deal_type="m_and_a", asset="nuclear plant", text="plans to restart"), "m_and_a")
        self.assertEqual(self.kind(deal_type="ppa", asset="solar farm", evidence="a loan"), "ppa")


class TheSample(unittest.TestCase):
    def test_kind_wrong_eight_to_none(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "deals", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, _ = fixture.replay("2249")
        got = {}
        for r in rows.to_dict("records"):
            for sid in str(r["story_ids"]).split(";"):
                if fx.get(sid):
                    got[fx[sid]] = r["kind"]
        want = {"D001": "project_finance", "D007": "compute_capacity", "D012": "nuclear_restart_uprate",
                "D013": "project_finance", "D020": "m_and_a", "D050": "compute_capacity", "D053": "compute_capacity",
                "D080": "nuclear_restart_uprate",
                # read and left: supplies to a data center, a one-party project
                "D034": "other", "D046": "other", "D055": "other"}
        for n, k in want.items():
            self.assertEqual(got.get(n), k, n)


if __name__ == "__main__":
    unittest.main()
