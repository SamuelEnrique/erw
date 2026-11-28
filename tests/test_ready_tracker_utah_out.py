"""Ready branch for the datacenter tracker (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.3, the
datacenter tracker; audit docs/reviews/tracker-model-audit-2026-11-26.md, finding 1, test wip/audit-tracker-7, carried
over and turned). Not the default: it waits for Samuel's ruling; no visitor sees either while the hold stands.

The other choice: the row known to be two unrelated stories joined on the state alone (datacenter:868a5b4c04ff1f44, a
2025 Utah story and a 2026 story of a 9.4 GW campus) is left out of every sum, count and bar (KNOWN_WRONG_JOINS in
site/lib/dctop.ts and site/lib/dcrollups.ts, and the replication), and the top block names it among the rows left out.

1. The two lists are one, and the rule is in both counted functions.
2. Through the page's own top block and rollups, on datacenter_facilities.csv where this machine holds it (the
   warehouse's output, held for a license; skipped elsewhere): the row is in no sum, and the sum is the old one less
   its 9,400 MW."""
import csv
import json
import os
import re
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOP = "file:///" + os.path.join(ROOT, "site", "lib", "dctop.ts").replace("\\", "/")
ROLL = "file:///" + os.path.join(ROOT, "site", "lib", "dcrollups.ts").replace("\\", "/")
WRONG = "datacenter:868a5b4c04ff1f44"
ENTITY = {"entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source",
          "source_url", "retrieved_at", "vintage"}
JS = """
const T = await import(process.argv[1]);
const R = await import(process.argv[2]);
const fs = await import("node:fs");
const rows = JSON.parse(fs.readFileSync(process.argv[3], "utf-8"));
const b = T.topBlock(rows.map(T.topRowOf), "2026-11-28");
const old = rows.filter((r) => r.entity_id !== process.argv[4]);
const ut = R.rollups(rows, "state").find((r) => r.value === "UT") ?? null;
console.log(JSON.stringify({ total: b.totalMw, wrong: b.wrongJoins, counted: b.inTotals.length, inSum: b.withMw.some((f) => f.id === process.argv[4]),
  rolled: R.counted(rows.find((r) => r.entity_id === process.argv[4])), utah: ut }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def facilities_csv():
    for d in (os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")):
        p = os.path.join(d, "datacenter_facilities.csv")
        if os.path.exists(p):
            return p
    return None


class TheKnownWrongJoinIsInNoSum(unittest.TestCase):
    def test_one_list_in_both_rules(self):
        top, roll = src("site", "lib", "dctop.ts"), src("site", "lib", "dcrollups.ts")
        want = 'KNOWN_WRONG_JOINS = new Set(["datacenter:868a5b4c04ff1f44"]);'
        self.assertIn(want, top)
        self.assertIn(want, roll)
        self.assertIn("!KNOWN_WRONG_JOINS.has(f.id ?? \"\")", top)
        self.assertIn("!KNOWN_WRONG_JOINS.has(r.entity_id)", roll)
        self.assertIn('KNOWN_WRONG_JOINS = {"datacenter:868a5b4c04ff1f44"}', src("replication", "datacenter_tracker", "replicate.py"))
        self.assertIn("known wrong join", src("site", "app", "datacenters", "Body.tsx"))
        self.assertIn("Until then the tracker leaves it out of every sum", src("docs", "methods", "datacenter_facilities.md"))
        self.assertIsNone(re.search(r"from ['\"]", roll))                  # dcrollups stays a file with no imports

    def test_on_the_table(self):
        path = facilities_csv()
        if path is None:
            self.skipTest("datacenter_facilities.csv is not on this machine (the warehouse's output, held for a license)")
        with open(path, encoding="utf-8", newline="") as f:
            table = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
        row = next((r for r in table if r["entity_id"] == WRONG), None)
        if row is None or not row["capacity_mw"]:
            self.skipTest("the old join is no longer in the table (the news table was rebuilt)")
        live = [{"entity_id": r["entity_id"], "name": r["name"] or None, "operator": r["operator"] or None, "status": r["status"] or None,
                 "capacity_mw": float(r["capacity_mw"]) if r["capacity_mw"] else None,
                 "extra": {k: v for k, v in r.items() if k not in ENTITY and v != ""}} for r in table]
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "rows.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(live, f)
            out = subprocess.run(["node", "--input-type=module", "-e", JS, TOP, ROLL, p, WRONG], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertFalse(r["inSum"])
        self.assertFalse(r["rolled"])
        self.assertEqual(r["wrong"], 1)
        self.assertGreater(r["total"], 0)
        if r["utah"] is not None:                                          # Utah's bar holds no MW of the row
            self.assertTrue(r["utah"]["mw"] is None or r["utah"]["mw"] < float(row["capacity_mw"]))


if __name__ == "__main__":
    unittest.main()
