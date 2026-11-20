"""Session 7627: the other choice of the ruling on a deal's grid in the deal tracker (branch wip/alt-deals-3, not
landed). The tracker tab, the comparables and the AI view read a deal's grid from its state alone; under the other
choice they read the grid the story names first, as the table's own Grid column does.

energy_deals is held whole (license needed): the page draws none of its rows, so the figures here are counts.
Read through the page's own functions (site/lib/deals2.ts: toDeal, fold) on the repository's copy of the table:
  578 deals either way; one deal moves from "not stated" to PJM: not stated 544 to 543, PJM 10 to 11 (+10 percent of
    PJM's count); no other grid moves.

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
const all = D.fold(rows.map(D.toDeal), pairs);
const by = {};
for (const d of all) by[d.grid || "none"] = (by[d.grid || "none"] ?? 0) + 1;
console.log(JSON.stringify({ deals: all.length, none: by.none ?? 0, pjm: by.PJM ?? 0, ercot: by.ERCOT ?? 0 }));
"""


class TheStorysGridFirst(unittest.TestCase):
    def test_the_counts(self):
        exe = shutil.which("node")
        if not exe or not os.path.exists(TABLE):
            raise unittest.SkipTest("node or energy_deals.csv is not on this machine")
        r = subprocess.run([exe, "--input-type=module", "-e", JS, TABLE], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        got = json.loads(r.stdout)
        self.assertEqual((got["deals"], got["none"], got["pjm"]), (578, 543, 11))

    def test_the_rule(self):
        with open(os.path.join(ROOT, "site", "lib", "deals2.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('grid: (x.grid ?? "").trim() || (STATE_GRID[state] ?? ""),', s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
