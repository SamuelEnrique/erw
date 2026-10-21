"""The landing of wip/461-combined: check-values reads the datacenter queue's active MW by grid as written whole.

Session 468's view by grid of /datacenters (site/app/datacenters/GridsView.tsx) writes `dcq|<grid>|<zone>|active_mw` with
`whole()`, so the page shows 298,606 for 298,605.97; check-values compared it as two decimals and failed (session 461's
report, the six check-values failures). The key now joins the `whole` rule; `mw_asked` stays two decimals, as written.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheActiveMwIsReadWhole(unittest.TestCase):
    def test_the_page_writes_it_whole(self):
        self.assertIn("check={`dcq|${g.grid}|${g.zone}|active_mw`} raw={g.activeMw}>{whole(", read("site", "app", "datacenters", "GridsView.tsx"))

    def test_the_whole_rule_holds_it_and_not_mw_asked(self):
        line = next(l for l in read("site", "scripts", "check-values.mjs").splitlines() if l.strip().startswith("const whole = /"))
        rule = re.compile(line.split("= /", 1)[1].rsplit("/.test(check)", 1)[0])
        self.assertTrue(rule.search("dcq|ercot|-|active_mw"))
        self.assertTrue(rule.search("dcq|pjm|dominion|active_mw"))
        self.assertFalse(rule.search("dcq|ercot|-|mw_asked"))
        self.assertFalse(rule.search("dcq|ercot|-|active_mw_share"))

    def test_no_em_dash(self):
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
