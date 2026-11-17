"""Ruling alternative 2 of /grid (session 7725, 17 November 2026, branch wip/alt-grid-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-grid-2026-11-17.md, line 2): should the Mix tab's
"right now" read the hourly snapshot's demand, as the Network tab does, instead of the daily table a day behind it? On
this branch it does where the snapshot's hour is newer (site/lib/griddemand.ts pickDemand; site/components/grid/NowView.tsx
draws it with the snapshot's check key, netsnap|<BA>|demand_mw|<hour>, and says where it is from). On the live site of 17
November the impact file measured: ERCOT 54,008 MW (15 November 23:00 UTC) to 46,760 (17 November 06:00 UTC), -13.42
percent; PJM -8.56, SPP -8.80, CAISO +0.56 percent; most of each change is the hour of the day. On this machine the
committed snapshot (built 15 November) and the daily table both end at 12 November 23:00 UTC with the same values (ERCOT
54,234 MW, CAISO 26,528, SPP 33,343, PJM 99,115), so the branch draws the table's row there: the snapshot's demand agrees
with the table at a shared hour, and the switch moves the hour only. Pinned on made-up rows and on those copies.

    python -m unittest tests.test_alt_grid_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


def node(js):
    p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-1500:])
    return json.loads(p.stdout)


class TheRule(unittest.TestCase):
    def test_the_newer_hour_wins(self):
        got = node("const G = await import('./lib/griddemand.ts');"
                   "const t = { entity: 'eia930:ERCO', variable: 'demand_mw', ts_utc: '2026-11-15T23:00:00Z', value: 54008 };"
                   "const n = (ts, v) => ({ id: 'ERCO', demand_ts: ts, demand_mw: v });"
                   "process.stdout.write(JSON.stringify([G.pickDemand(t, n('2026-11-17T06:00:00Z', 46760), 'eia930:ERCO'), G.pickDemand(t, n('2026-11-15T23:00:00Z', 54008), 'eia930:ERCO'),"
                   " G.pickDemand(t, n(null, null), 'eia930:ERCO'), G.pickDemand(undefined, n('2026-11-17T06:00:00Z', 46760), 'eia930:ERCO')].map((p) => [p.fromSnap, p.d && p.d.value, p.d && p.d.ts_utc])));")
        self.assertEqual(got, [[True, 46760, "2026-11-17T06:00:00Z"], [False, 54008, "2026-11-15T23:00:00Z"], [False, 54008, "2026-11-15T23:00:00Z"], [True, 46760, "2026-11-17T06:00:00Z"]])
        self.assertEqual(round((46760 - 54008) / 54008 * 100, 2), -13.42)

    def test_the_view_uses_it(self):
        with open(os.path.join(SITE, "components", "grid", "NowView.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("pickDemand(", s)
        self.assertIn("netsnap|${grid.ba}|demand_mw|${r.ts_utc}", s)


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "eia930_all_demand.csv")), "eia930_all_demand is not on this machine")
class OnTheCopiesHere(unittest.TestCase):
    def test_the_snapshot_and_the_table_agree_at_a_shared_hour(self):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-grid-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        f = json.loads(p.stdout)
        for ba, v in (("ERCO", 54234), ("CISO", 26528), ("SWPP", 33343), ("PJM", 99115)):
            self.assertEqual((f[ba]["table"], f[ba]["snapshot"], f[ba]["fromSnap"]), (["2026-11-12T23:00:00Z", v], ["2026-11-12T23:00:00Z", v], False), ba)


if __name__ == "__main__":
    unittest.main()
