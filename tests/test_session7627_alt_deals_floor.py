"""Session 7627: the other choice of the ruling on a floor of the extraction's confidence in the deal tracker (branch
wip/alt-deals-1, not landed). The tracker, the comparables and the AI view open with no floor (every row from 0.3 up);
under the other choice they open at "Sure at least" 0.7, as the Roundup's tables do.

energy_deals is held whole (license needed): the page draws none of its rows, in the internal view too, so the figures
here are counts and a sum, never a deal's parties or its own figures. Read through the page's own functions
(site/lib/deals2.ts: toDeal, fold) on the repository's copy of the table (583 rows, 5 folded by
site/data/deal_duplicates.json):
  no floor: 578 deals, 40,297 MW stated by 35, 212 AI-power deals (the impact file's figures);
  at 0.7, applied to each deal as folded by its kept row: 281 deals (-51.4 percent), 21,705 MW (-46.1 percent), 99
    AI-power deals (-53.3 percent).

No request, no model call. Skips when node or the table is absent."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLE = os.path.join(os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output"), "energy_deals.csv")

JS = r"""
import fs from "node:fs";
const D = await import("./lib/deals2.ts");
const pairs = JSON.parse(fs.readFileSync("data/deal_duplicates.json", "utf-8")).pairs;
function parseCsv(text) {
  const rows = []; let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true; else if (c === ",") { row.push(cell); cell = ""; }
    else if (c === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; } else if (c !== "\r") cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows;
}
const text = fs.readFileSync(process.argv[1], "utf-8").split("\n").filter((l) => !l.startsWith("#")).join("\n");
const [head, ...body] = parseCsv(text);
const TOP = ["event_id", "event_date", "status", "mw", "price", "currency", "parties", "source", "source_url"];
const rows = body.filter((r) => r.length === head.length).map((r) => {
  const o = Object.fromEntries(head.map((h, i) => [h, r[i]]));
  return { ...Object.fromEntries(TOP.map((h) => [h, o[h] === "" ? null : o[h]])), extra: Object.fromEntries(head.filter((h) => !TOP.includes(h)).map((h) => [h, o[h]])) };
});
const all = D.atFloor(D.fold(rows.map(D.toDeal), pairs));
const unfloored = D.fold(rows.map(D.toDeal), pairs);
const sum = (ds) => Math.round(ds.filter((d) => d.mw !== null).reduce((a, d) => a + d.mw, 0));
console.log(JSON.stringify({ floor: D.SURE_FLOOR, rows: rows.length, before: [unfloored.length, sum(unfloored), unfloored.filter((d) => d.ai).length],
  after: [all.length, sum(all), all.filter((d) => d.ai).length] }));
"""


class TheFloor(unittest.TestCase):
    def test_the_counts(self):
        exe = shutil.which("node")
        if not exe or not os.path.exists(TABLE):
            raise unittest.SkipTest("node or energy_deals.csv is not on this machine")
        r = subprocess.run([exe, "--input-type=module", "-e", JS, TABLE], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        got = json.loads(r.stdout)
        self.assertEqual(got, {"floor": 0.7, "rows": 583, "before": [578, 40297, 212], "after": [281, 21705, 99]})
        self.assertEqual((f"{100 * (281 / 578 - 1):.1f}", f"{100 * (21705 / 40297 - 1):.1f}", f"{100 * (99 / 212 - 1):.1f}"), ("-51.4", "-46.1", "-53.3"))

    def test_the_rule(self):
        with open(os.path.join(ROOT, "site", "lib", "deals2.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("export const SURE_FLOOR = 0.7;", s)
        self.assertIn("confidence: num(x.confidence),", s)
        self.assertIn("export const atFloor = (deals: Deal[]): Deal[] => deals.filter((d) => (d.confidence ?? 0) >= SURE_FLOOR);", s)
        for v in ("ai", "charts", "comparables", "v2"):
            with open(os.path.join(ROOT, "site", "app", "deals", v, "view.tsx"), encoding="utf-8") as f:
                self.assertIn("atFloor(fold(", f.read(), v)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
