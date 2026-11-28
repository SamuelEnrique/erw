"""Ready branch for the policy monitor (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.3, the policy
monitor; audit docs/reviews/policy-model-audit-2026-11-26.md, finding 6, test wip/audit-policy-10). Not the default:
it waits for Samuel's ruling.

The other choice: a record's status as of the page's day. A final record whose effective date is on or before the
day reads "In effect" (site/lib/policymonitor.ts statusAsOf, applied in site/app/policy/page.tsx). On the page's file
now on main, read on 28 November 2026: Final 126 to 30, In effect 70 to 166; as the view opens, Final 26 to 12 and
In effect 5 to 19.

1. The rule in the code, applied where the page hands the rows to the monitor; the note's words.
2. The counts on the page's own file, by the same rule."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DAY = "2026-11-28"


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def as_of(r, day=DAY):
    if r["status"] == "final" and any(s["kind"] == "effective" and s["date"] <= day for s in r.get("steps", [])):
        return "effective"
    return r["status"]


class TheStatusIsAsOfTheDay(unittest.TestCase):
    def test_the_rule(self):
        lib = src("site", "lib", "policymonitor.ts")
        self.assertIn("export function statusAsOf(rows: MonitorRow[], today: string): MonitorRow[]", lib)
        self.assertIn('r.status === "final" && today && (r.steps ?? []).some((s) => s.kind === "effective" && s.date <= today)', lib)
        page = src("site", "app", "policy", "page.tsx")
        self.assertIn("<MonitorView rows={statusAsOf(m.rows, new Date(renderTime()).toISOString().slice(0, 10))}", page)
        self.assertIn("(`statusAsOf` in `site/lib/policymonitor.ts`)", src("docs", "methods", "policy_monitor.md"))

    def test_the_counts(self):
        rows = json.loads(src("site", "data", "policy", "monitor.json"))["rows"]
        before = sum(1 for r in rows if r["status"] == "final")
        after = sum(1 for r in rows if as_of(r) == "final")
        eff_before = sum(1 for r in rows if r["status"] == "effective")
        eff_after = sum(1 for r in rows if as_of(r) == "effective")
        self.assertLess(after, before)
        self.assertEqual(eff_after - eff_before, before - after)
        # no other status moves
        self.assertTrue(all(as_of(r) == r["status"] for r in rows if r["status"] != "final"))


if __name__ == "__main__":
    unittest.main()
