"""Audit of the policy monitor, finding 2 (session 10217, docs/reviews/policy-model-audit-2026-11-26.md), a test that
shows it; not for landing (restoring the documents moves the view's figures, and the table is the data machine's).

Since session 7009 the monitor's builder reads the fifteen large-load orders and steps of FERC and the grid operators
(utility_large_load_rule_changes, group operators_federal: PJM's large-load definition and registry, ER26-3515; SPP's
CHILLS, ER26-1323; ERCOT's Batch Zero, PGRR 145; the show-cause dockets EL26-67 and EL26-71) as documents of the monitor
(warehouse/policy/monitor_site.py, change_actions), and the method note (section 16) says they join its records. The
file the daily run wrote on 20 November 2026 dropped them (the run's tables hold no utility_large_load_rule_changes.csv,
so the builder reads none; its guard counts records, and new Register documents kept the count up), and the file of 25
November holds none: `fields_from` has no "utility_large_load_rule_changes".

Measured with the builder itself on the main copy's tables of 13 and 14 November: with the fifteen, 2,057 to 2,072
documents and 1,518 to 1,528 records (ten records of their own, two records joined); as the view opens (significance 5
or more) 295 shown either way, since the fifteen are not scored (finding 3). Default: left as it is, with the data
request that the daily run read the table.

1. The builder still reads them when the table is there. Passes on main.
2. The page's file holds them. FAILS on main: that failure is the finding."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheLargeLoadOrdersAreInTheMonitor(unittest.TestCase):
    def test_the_builder_reads_them(self):
        import pandas as pd
        import monitor_site
        ch = pd.DataFrame([{"event_id": "llchange:operators_federal-99", "event_date": "2026-10-09T00:00:00Z", "x_group": "operators_federal",
                            "status": "order issued", "x_docket": "ER26-3515-000", "parties": "PJM Interconnection, L.L.C.",
                            "x_rule_name": "PJM large load definition", "source_url": "https://example.org/a", "x_what": "", "x_state": "PA"}])
        got = monitor_site.change_actions(ch)
        self.assertEqual(list(got["agency"]), ["FERC"])
        self.assertEqual(list(got["fields_from"]), ["utility_large_load_rule_changes"])

    def test_the_page_file_holds_them(self):
        m = json.loads(src("site", "data", "policy", "monitor.json"))
        self.assertIn("utility_large_load_rule_changes", m["fields_from"],
                      "the monitor's file holds none of the fifteen large-load orders read from utility_large_load_rule_changes")


if __name__ == "__main__":
    unittest.main()
