"""Audit of the policy monitor, finding 1 (session 10217, docs/reviews/policy-model-audit-2026-11-26.md), a test that
shows it; not for landing (the fix would move every figure of the view, so it is the owner's ruling).

policy_actions and policy_reads are held whole, "license needed", from 21 October 2026, because they carry the Public
Utility Commission of Texas's news releases (site/data/license_status.json; the owner's ruling of 12 October 2026). The
first view of /policy reads the table through the license gate and draws "license needed" and no figure. The monitor
view draws site/data/policy/monitor.json, built from the same held table, with no gate (app/policy/page.tsx, the
`view === "monitor"` branch). On the file of 25 November 2026: 1,568 records, 37 of them the PUCT's own pages (the PUCT
20, the Texas Governor's releases on the PUCT's page 17), 11 of them shown as the view opens, 9 with a figure.

The other choices, measured: hold the monitor as the first view is held (295 shown as it opens, 1,568 held, to none);
or leave out the PUCT's rows (1,568 to 1,531 records; 295 to 284 shown as it opens). Default: left as it is (line 1 of
docs/reviews/ruling-impact-policy-2026-11-17.md, which waits for the owner)."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheMonitorDrawsAHeldTable(unittest.TestCase):
    def test_the_table_is_held_whole(self):
        status = json.loads(src("site", "data", "license_status.json"))
        self.assertEqual(status["tables"]["policy_actions"]["status"], "license needed")
        self.assertEqual(status["all"]["policy_actions"]["status"], "license needed")
        self.assertEqual(status["all"]["policy_actions"].get("hold"), "whole")

    def test_the_monitor_branch_reads_the_file_with_no_gate(self):
        page = src("site", "app", "policy", "page.tsx")
        branch = page[page.index('if (view === "monitor") {'):page.index('if (view === "week") {')]
        self.assertIn("const m = monitorFile as unknown as MonitorFile;", branch)
        self.assertNotRegex(branch, r"licenseNeeded|attempt\(|NoData")

    def test_the_file_holds_the_held_publishers_rows(self):
        rows = json.loads(src("site", "data", "policy", "monitor.json"))["rows"]
        puct = [r for r in rows if r["body"] in ("PUCT", "Texas Governor")]
        self.assertGreater(len(puct), 0)
        self.assertTrue(all(any(re.search(r"puc\.texas\.gov|gov\.texas\.gov", u) for u in r.get("sources", [])) for r in puct))
        opened = [r for r in puct if (r.get("significance") or -1) >= 5]
        self.assertGreater(len(opened), 0)


if __name__ == "__main__":
    unittest.main()
