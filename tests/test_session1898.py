"""Session 1898: three faults session 1885 found walking the lab's path on 13 November 2026 (docs/reviews/lab-path.md,
"Walked 13 November 2026 (session 1885)", faults 2 to 4). One class a fault.

No network, no model, no browser. Nothing here sets the environment at import.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node_ok():
    return shutil.which("node") and os.path.isdir(os.path.join(SITE, "node_modules"))


def stat_map(text, start):
    """The "first|second": "table" pairs of the object literal that follows `start`."""
    i = text.index(start)
    body = text[text.index("{", i):text.index("};", i)]
    return dict(re.findall(r'"([a-z_]+\|[a-z_]+)"\s*:\s*"([a-z0-9_]+)"', body))


class Fault2TheGridsOwnFiguresArePrinted(unittest.TestCase):
    """Fault 2: "The facilities against each grid" printed "license needed" (note 1, the facilities' hold) in the Peak
    hour MW and Capacity MW columns of every grid and in ERCOT's Reserve margin, though the line under the table names
    them as each grid's own figures (grid_peak_vs_capacity) and note 2 says ERCOT's margin is held.

    Why: components/Num.tsx heldBy read every dcgrid| key as datacenter_facilities (KEY_TABLE), held from 2026-10-21.
    Fix: KEY_STAT_TABLE names the table by the key's second word, read before KEY_TABLE: dcgrid|peak_mw and
    dcgrid|capacity_mw are grid_peak_vs_capacity, dcgrid|reserve_margin ercot_cdr_reserve_margins; both are public in
    sources.csv and absent from the site's license list, so the figures print. check-holds.mjs reads the same map."""

    WANT = {"dcgrid|peak_mw": "grid_peak_vs_capacity", "dcgrid|capacity_mw": "grid_peak_vs_capacity",
            "dcgrid|reserve_margin": "ercot_cdr_reserve_margins"}

    def test_num_and_check_holds_hold_the_same_map(self):
        self.assertEqual(stat_map(src("site", "components", "Num.tsx"), "const KEY_STAT_TABLE"), self.WANT)
        self.assertEqual(stat_map(src("site", "scripts", "check-holds.mjs"), "export const KEY_STAT_TABLE"), self.WANT)

    def test_the_map_is_read_before_key_table(self):
        for parts in (("site", "components", "Num.tsx"), ("site", "scripts", "check-holds.mjs")):
            s = src(*parts)
            stat = s.index("in KEY_STAT_TABLE) table = KEY_STAT_TABLE[")
            self.assertLess(stat, s.index("else if (head in KEY_TABLE) table = KEY_TABLE[head];"), "/".join(parts))

    def test_the_tables_are_public_and_not_on_the_license_list(self):
        held = json.loads(src("site", "data", "license_status.json"))["tables"]
        sources = src("warehouse", "metadata", "sources.csv")
        for table in set(self.WANT.values()):
            self.assertNotIn(table, held)
            self.assertRegex(sources, r",public," + table + r",")
        # the facilities stay held: their other columns are still the hold's words
        self.assertEqual(held["datacenter_facilities"]["status"], "license needed")

    @unittest.skipUnless(node_ok(), "node or site/node_modules is not on this machine")
    def test_check_holds_judges_the_grid_figures_free_and_the_facilities_held(self):
        script = (
            "import { judgeKey } from './scripts/check-holds.mjs';"
            "const held = new Map([['datacenter_facilities', { byGrid: false, grids: new Set() }]]);"
            "const out = {};"
            "for (const k of ['dcgrid|peak_mw|ERCOT', 'dcgrid|capacity_mw|PJM', 'dcgrid|reserve_margin|ERCOT', 'dcgrid|planned|ERCOT', 'dcgrid|share_of_peak|ERCOT'])"
            "  out[k] = judgeKey(k, held, new Set()) ? 'held' : 'free';"
            "console.log(JSON.stringify(out));"
        )
        r = subprocess.run(["node", "--input-type=module", "-e", script], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(got, {"dcgrid|peak_mw|ERCOT": "free", "dcgrid|capacity_mw|PJM": "free",
                               "dcgrid|reserve_margin|ERCOT": "free", "dcgrid|planned|ERCOT": "held",
                               "dcgrid|share_of_peak|ERCOT": "held"})


if __name__ == "__main__":
    unittest.main()
