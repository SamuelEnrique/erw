"""Ready branch for the datacenter tracker (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.3, the
datacenter tracker; audit docs/reviews/tracker-model-audit-2026-11-26.md, finding 5). Not the default: it waits for
Samuel's ruling; no visitor sees either while the hold stands.

The other choice: the timeline from first reported to energized counts the facilities the sums count (a named US state,
not cancelled: site/lib/dcrollups.ts timeline reads rows.filter(counted)). Measured through the page's own library on
this machine's datacenter_facilities.csv (458 rows): 9 rows to 3, the median wait 2 years to 3; the year 2026's median
(2 years) goes, 2 rows left. tests/test_audit_tracker_5.py is turned to the same rule.

1. Through the page's library (run by Node): a row with no state and a cancelled row are not on the timeline.
2. The note's and the method's words."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dcrollups.ts").replace("\\", "/")
JS = """
const R = await import(process.argv[1]);
const row = (id, state, status, y) => ({ entity_id: id, capacity_mw: null, status, operator: "", extra: { ...(state ? { state } : {}), first_story_at: "2026-10-02T00:00:00Z", energized_year: y } });
const rows = [row("abroad", "", "planned", "2028"), row("gone", "TX", "withdrawn", "2028"), row("us", "TX", "planned", "2029"),
  row("wrong", "UT", "planned", "2027")];
console.log(JSON.stringify({ timeline: R.timeline(rows).map((t) => t.id) }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheTimelineCountsTheCountedRows(unittest.TestCase):
    def test_the_rule(self):
        self.assertIn("for (const r of rows.filter(counted)) {", src("site", "lib", "dcrollups.ts"))
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout.strip().splitlines()[-1])["timeline"], ["us", "wrong"])

    def test_the_words(self):
        self.assertIn("As the sums above, it counts the facilities in a named US state and not cancelled.",
                      src("site", "app", "datacenters", "Timeline.tsx"))
        self.assertIn("Every facility the sums count (a named US state, not cancelled; tracker audit of 26 November 2026, finding 5)",
                      src("docs", "methods", "datacenter_tracker.md"))


if __name__ == "__main__":
    unittest.main()
