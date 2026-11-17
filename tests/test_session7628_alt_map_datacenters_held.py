"""Session 7628: the other choice of the ruling on the project map's datacenter layer (branch wip/alt-datacenters-1, not
landed). The datacenter tracker draws none of its facilities (datacenter_facilities is held whole, license needed),
while /map's Projects tab drew 278 datacenters with names, operators and MW from its own copy. Under the other choice
the map's copy is held too, as bare points.

What is held to (lib/projectmap.ts, heldDatacenters, run by node on site/data/map.json built 16 November 2026):
  the map keeps its 35,035 points and its 278 datacenter points, each at its place, state and grid;
  the datacenter points lose their 28,254.0 MW, every name and operator, and the card's city, developer, power,
    utility and sources; no other kind's figure moves;
  the page and the card route both read the file through it.

No request, no model call. Skips when node is absent."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

JS = r"""
import fs from "node:fs";
const P = await import("./lib/projectmap.ts");
const f = JSON.parse(fs.readFileSync("data/map.json", "utf-8"));
const h = P.heldDatacenters(f);
const dc = f.kinds[3], a = dc.start, b = dc.start + dc.rows;
const sum = (x) => Math.round(x.mw.slice(a, b).reduce((s, v) => s + (v ?? 0), 0) * 10) / 10;
const m = h.more.datacenter;
console.log(JSON.stringify({ points: h.k.length, dc: dc.rows, before: sum(f), after: sum(h), named: h.n.slice(a, b).filter((v) => v).length,
  operators: h.o.slice(a, b).filter((v) => v >= 0).length, details: [...m.city, ...m.developer, ...m.power, ...m.utility].filter(Boolean).length + m.urls.flat().length,
  placed: JSON.stringify(h.la.slice(a, b)) === JSON.stringify(f.la.slice(a, b)), others: JSON.stringify(h.mw.slice(0, a)) === JSON.stringify(f.mw.slice(0, a)) }));
"""


class TheMapsDatacentersHeld(unittest.TestCase):
    def test_the_layer(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "--input-type=module", "-e", JS], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertEqual(json.loads(r.stdout), {"points": 35035, "dc": 278, "before": 28254.0, "after": 0, "named": 0, "operators": 0, "details": 0,
                                                "placed": True, "others": True})

    def test_every_reader(self):
        for parts in (("site", "app", "map", "page.tsx"), ("site", "app", "map", "card", "route.ts")):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
                self.assertIn("heldDatacenters(mapJson as unknown as MapFile)", f.read(), parts)
        with open(os.path.join(ROOT, "site", "lib", "projectmap.ts"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("export const HOLD_DATACENTER_LAYER = true;", s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
