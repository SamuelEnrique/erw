"""Audit of "What a datacenter pays", finding 2 (session 10203, docs/reviews/datacenter-model-audit-2026-11-26.md): the All
grids tab's "All-in" (site/lib/siting.ts, allInCell) adds three parts, energy, transmission and capacity. The cell's hover
named delivery, distribution, ancillary and retail charges as left out, but neither the hover nor the column's tip named
losses, and the column's tip named nothing left out.

1. The sum holds exactly the three parts, and the page's own delivery table (site/data/datacenter/texas_delivery.json,
   through lib/datacenter/delivery.ts run by Node) holds distribution and riders beside the transmission in Oncor's area
   at 100 MW: a part of the bill the all-in figure does not hold. Passes on main: it shows the gap.
2. The fix on this branch, words only: the column's tip and the cell's hover name delivery, distribution, ancillary,
   loss and retail charges as not in it. Fails on main."""
import json
import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "datacenter", "delivery.ts").replace("\\", "/")
JS = """
const D = await import(process.argv[1]);
const fs = await import("node:fs");
const del = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const d = D.deliveryOf(del.rows, "Oncor", 100);
console.log(JSON.stringify(Object.fromEntries(d.components.map((c) => [c.kind, c.perMwh]))));
"""


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AllInLeavesOut(unittest.TestCase):
    def test_three_parts_and_a_bill_beside_them(self):
        src = read("site", "lib", "siting.ts")
        body = src.split("export function allInCell(")[1].split("\n}\n")[0]
        self.assertTrue(re.search(r"allIn\(\{ energy, transmission, capacity \}\)", body))
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, os.path.join(ROOT, "site", "data", "datacenter", "texas_delivery.json")],
                             capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        parts = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertGreater(parts["distribution"] + parts["other"], 0.1)   # USD 0.23 per MWh left out in Oncor's area

    def test_tips_name_what_is_left_out(self):
        self.assertIn("No delivery, distribution, ancillary, loss or retail charge is in it, so it is not the whole bill.", read("site", "lib", "siting.ts"))
        self.assertIn("No delivery, distribution, ancillary, loss or retail charge is in it.", read("site", "app", "cost-of-power", "AllGridsView.tsx"))


if __name__ == "__main__":
    unittest.main()
