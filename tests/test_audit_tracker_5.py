"""Audit of the datacenter power tracker, finding 5 (session 10211, docs/reviews/tracker-model-audit-2026-11-26.md): every
section of the page counts the facilities in a named US state and not cancelled, and says so, except the timeline from
first reported to energized, which counts every facility held (site/lib/dcrollups.ts, timeline: no counted filter; the
method note, section 7.6, "Every facility held") and did not say so. On the table of 25 November 2026, 6 of its 9 rows
state no US state; on the counted rows the median wait is 3 years, not 2.

1. Through the page's library (run by Node): a row with no state and a cancelled row are on the timeline. Passes on main.
2. The fix on this branch, words only: the timeline's note says it counts every facility held. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dcrollups.ts").replace("\\", "/")
JS = """
const R = await import(process.argv[1]);
const row = (id, state, status) => ({ entity_id: id, capacity_mw: null, status, operator: "", extra: { ...(state ? { state } : {}), first_story_at: "2026-10-02T00:00:00Z", energized_year: "2029" } });
const rows = [row("abroad", "", "planned"), row("gone", "TX", "withdrawn"), row("us", "TX", "planned")];
console.log(JSON.stringify({ timeline: R.timeline(rows).map((t) => t.id), counted: rows.filter(R.counted).map((r) => r.entity_id) }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheTimelineSaysWhatItCounts(unittest.TestCase):
    def test_the_timeline_counts_every_facility_held(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["timeline"], ["us"])   # ready branch wip/ready-tracker-timeline-counted (session 11408): the counted rows only
        self.assertEqual(r["counted"], ["us"])

    def test_the_note_says_it(self):
        self.assertIn("A median needs three facilities with both. As the sums above, it counts the facilities in a named US state and not "
                      "cancelled.", src("site", "app", "datacenters", "Timeline.tsx"))


if __name__ == "__main__":
    unittest.main()
