"""Session 7627: the other choice of the ruling on folded figures in the deal tracker (branch wip/alt-deals-2, not
landed). When two rows are folded into one deal, the kept row stayed as extracted; under the other choice it takes a
figure only the folded row states, as the warehouse's own merge does.

energy_deals is held whole (license needed): the page draws none of its rows, so the figures here are counts and a sum.
Read through the page's own functions (site/lib/deals2.ts: toDeal, fold) on the repository's copy of the table:
  578 deals either way; MW disclosed 40,297 by 35 deals to 40,730 by 36 (+433, +1.07 percent): one kept row lacks MW
    where its folded row states it (the impact file: the Energy Department's loan to Vistra);
  a figure the kept row states is never replaced.

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
const deals = rows.map(D.toDeal), byId = new Map(deals.map((d) => [d.id, d]));
const all = D.fold(deals, pairs);
const withMw = all.filter((d) => d.mw !== null);
const kept = all.filter((d) => d.folded.length && byId.get(d.id).mw !== null);
console.log(JSON.stringify({ deals: all.length, mw: Math.round(withMw.reduce((a, d) => a + d.mw, 0)), withMw: withMw.length,
  keptUnchanged: kept.every((d) => d.mw === byId.get(d.id).mw) }));
"""


class TheFoldedFigureCarried(unittest.TestCase):
    def test_the_counts(self):
        exe = shutil.which("node")
        if not exe or not os.path.exists(TABLE):
            raise unittest.SkipTest("node or energy_deals.csv is not on this machine")
        r = subprocess.run([exe, "--input-type=module", "-e", JS, TABLE], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertEqual(json.loads(r.stdout), {"deals": 578, "mw": 40730, "withMw": 36, "keptUnchanged": True})
        self.assertEqual(f"{100 * (40730 / 40297 - 1):.2f}", "1.07")

    def test_the_rule(self):
        with open(os.path.join(ROOT, "site", "lib", "deals2.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("if (kept.mw === null && dup.mw !== null) kept.mw = dup.mw;", s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
