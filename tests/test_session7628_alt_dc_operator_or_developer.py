"""Session 7628: the other choice of the ruling on the datacenter tracker's views by operator (branch
wip/alt-datacenters-2, not landed). The top operators, the rollup and the chart by operator counted a facility under its
operator alone; under the other choice a facility with no operator named counts under its developer, "operator or
developer", as the warehouse's own rollup table does.

datacenter_facilities is held whole (license needed): the page draws none of these views, so the figures here are counts
and sums, never a facility's name, operator or own figure. Read through the page's own rollup (site/lib/dcrollups.ts) on
the repository's copy of the table (458 rows, 274 counted, 28,254 MW stated):
  "operator not stated": facilities stating MW 13 to 4, MW 26,124 to 5,420 (-20,704, -79.3 percent); counted 25 to 11;
  the counted facilities and the MW of all lines together do not move (274; 28,254).

No request, no model call. Skips when node or the table is absent."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLE = os.path.join(os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output"), "datacenter_facilities.csv")

JS = r"""
import fs from "node:fs";
const R = await import("./lib/dcrollups.ts");
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
const TOP = ["entity_id", "capacity_mw", "status", "operator"];
const rows = body.filter((r) => r.length === head.length).map((r) => {
  const o = Object.fromEntries(head.map((h, i) => [h, r[i]]));
  return { ...Object.fromEntries(TOP.map((h) => [h, o[h] === "" ? null : o[h]])), extra: Object.fromEntries(head.filter((h) => !TOP.includes(h)).map((h) => [h, o[h]])) };
});
const ro = R.rollups(rows, "operator"), none = ro.find((x) => !x.value);
console.log(JSON.stringify({ counted: ro.reduce((a, x) => a + x.counted, 0), mw: Math.round(ro.reduce((a, x) => a + (x.mw ?? 0), 0)),
  none: [none.withMw, Math.round(none.mw), none.counted] }));
"""


class OperatorOrDeveloper(unittest.TestCase):
    def test_the_counts(self):
        exe = shutil.which("node")
        if not exe or not os.path.exists(TABLE):
            raise unittest.SkipTest("node or datacenter_facilities.csv is not on this machine")
        r = subprocess.run([exe, "--input-type=module", "-e", JS, TABLE], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertEqual(json.loads(r.stdout), {"counted": 274, "mw": 28254, "none": [4, 5420, 11]})
        self.assertEqual(f"{100 * (5420 / 26124 - 1):.1f}", "-79.3")

    def test_the_rule(self):
        with open(os.path.join(ROOT, "site", "lib", "dcrollups.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('export const operatorOf = (r: FacRow): string => (r.operator ?? "").trim() || (r.extra?.developer ?? "").trim();', s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
