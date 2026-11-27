"""Audit of the home page, finding 5 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the Infrastructure and
Games figures sum storage_capacity's units of status "operating", which holds EIA's own codes OP (operating), SB
(standby), OA and OS (out of service): on the snapshot of 29 September 2026 20 units, 508.0 MW of 54,488.9 in the US,
and 2 units, 200.0 MW of 18,204.5 in ERCOT. The storage audit of tonight (its finding 6) says so for /storage.

1. Where the table is held, the operating units carry other codes than OP. Skipped where it is not.
2. The fix on this branch, words only: both notes say the units are those EIA lists as operating, standby and
   out-of-service units among them. No figure moves. Fails on main.
Nothing here sets the environment or makes a request."""
import csv
import io
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheOperatingFleet(unittest.TestCase):
    def test_operating_holds_other_codes(self):
        path = os.path.join(ROOT, "warehouse", "output", "storage_capacity.csv")
        if not os.path.exists(path):
            self.skipTest("storage_capacity is not on this machine")
        with open(path, encoding="utf-8") as f:
            body = "\n".join(ln for ln in f.read().splitlines() if not ln.startswith("#"))
        codes = {r["eia_status"] for r in csv.DictReader(io.StringIO(body)) if r["status"] == "operating"}
        self.assertIn("OP", codes)
        self.assertTrue(codes & {"SB", "OA", "OS"}, codes)

    def test_the_notes_say_so(self):
        page = src("site", "app", "page.tsx")
        self.assertNotIn('note: "Batteries operating in the US', page)
        self.assertIn("Batteries EIA lists as operating in the US, a few standby and out-of-service units among them, nameplate power, from its monthly generator inventory.", page)
        self.assertIn("Batteries EIA lists as operating in ERCOT, standby and out-of-service units among them, the real fleet the battery game sets beside your own.", page)


if __name__ == "__main__":
    unittest.main()
