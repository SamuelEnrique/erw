"""Audit of the datacenter power tracker, finding 1, the figure (session 10211, docs/reviews/tracker-model-audit-2026-11-26.md).
NOT FOR LANDING: a test that shows a figure a ruling would move; nothing on this branch changes the page.

The news table holds one row joined before session 166 on a state alone: a 2025 story of a Utah datacenter (no operator,
no county) and a 2026 story of a proposed 9.4 GW campus (docs/methods/datacenter_facilities.md, "The news extractor's merge
rule", datacenter:868a5b4c04ff1f44). The rule does not split a row already joined, so the row's 9,400 MW is in every sum of
the tracker until --reextract, a model run, rebuilds the news table. On the table of 25 November 2026 it is 9,400 of the
28,254 MW stated (33.3 percent); left out, the sum would be 18,854.

The test runs the page's own top block (site/lib/dctop.ts) on datacenter_facilities.csv where this machine holds it (the
warehouse's output, never in git: the table is held for a license) and skips where it does not, or where the row is gone."""
import csv
import json
import os
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dctop.ts").replace("\\", "/")
WRONG = "datacenter:868a5b4c04ff1f44"
ENTITY = {"entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source",
          "source_url", "retrieved_at", "vintage"}
JS = """
const T = await import(process.argv[1]);
const fs = await import("node:fs");
const rows = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const all = T.topBlock(rows.map(T.topRowOf), "2026-11-26");
const without = T.topBlock(rows.filter((r) => r.entity_id !== process.argv[3]).map(T.topRowOf), "2026-11-26");
console.log(JSON.stringify({ all: all.totalMw, without: without.totalMw, inSum: all.withMw.some((f) => f.site === process.argv[4]) }));
"""


def facilities_csv():
    for d in (os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")):
        p = os.path.join(d, "datacenter_facilities.csv")
        if os.path.exists(p):
            return p
    return None


class TheOldJoinIsAThirdOfTheSum(unittest.TestCase):
    def test_the_old_join_is_in_the_sum_and_its_size(self):
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
            out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, p, WRONG, row["name"]], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["all"] - r["without"], float(row["capacity_mw"]))   # the row's MW is in the headline sum, whole
        self.assertEqual(float(row["capacity_mw"]), 9400.0)
        self.assertEqual(row["state"], "UT")
        self.assertGreater((r["all"] - r["without"]) / r["all"], 0.25)          # a quarter or more of the megawatts stated (33.3 percent on 25 November)

    def test_the_note_says_the_row_stays_until_a_reextraction(self):
        with open(os.path.join(ROOT, "docs", "methods", "datacenter_facilities.md"), encoding="utf-8") as f:
            note = f.read()
        self.assertIn("The rule does not split a row already joined", note)
        self.assertIn(WRONG, note)


if __name__ == "__main__":
    unittest.main()
