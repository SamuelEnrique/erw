"""Session 2245 (chain 156): the datacenter tracker's timeline, from first reported to energized
(site/lib/dcrollups.ts timeline and timelineCells, site/app/datacenters/Timeline.tsx).

Only a facility with both dates is on it; the wait is the difference of two stated years; a median needs three; no
wait is estimated from one date.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def fac(i, state, reported, energized):
    x = {"state": state, "first_story_at": reported}
    if energized is not None:
        x["energized_year"] = str(energized)
    return {"entity_id": f"datacenter:{i}", "capacity_mw": None, "status": "planned", "operator": "x", "extra": x}


ROWS = [fac(1, "TX", "2025-03-01T00:00:00Z", 2027), fac(2, "TX", "2025-09-01T00:00:00Z", 2026), fac(3, "TX", "2026-01-10T00:00:00Z", 2028),
        fac(4, "LA", "2026-02-01T00:00:00Z", 2027), fac(5, "TX", "2026-02-01T00:00:00Z", None), fac(6, "TX", "", 2027)]


class TheTimeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = node("const R = await import('./lib/dcrollups.ts');"
                     f"const t = R.timeline({json.dumps(ROWS)});"
                     "console.log(JSON.stringify({t, grid: R.timelineCells(t, 'grid'), year: R.timelineCells(t, 'year'), key: R.timeKey('median', 'grid', 'ERCOT')}));")

    def test_only_facilities_with_both_dates(self):
        self.assertEqual([x["id"] for x in self.r["t"]], ["datacenter:1", "datacenter:2", "datacenter:3", "datacenter:4"])
        self.assertEqual([x["wait"] for x in self.r["t"]], [2, 1, 2, 1])

    def test_the_median_needs_three(self):
        g = {c["value"]: c for c in self.r["grid"]}
        self.assertEqual((g["ERCOT"]["count"], g["ERCOT"]["median"]), (3, 2))
        self.assertEqual((g["MISO"]["count"], g["MISO"]["median"]), (1, None))
        self.assertEqual([c["value"] for c in self.r["year"]], ["2025", "2026"])
        self.assertEqual(self.r["key"], "dctime|median|grid|ERCOT")


class TheSources(unittest.TestCase):
    def test_the_page_and_the_check(self):
        with open(os.path.join(SITE, "app", "datacenters", "page.tsx"), encoding="utf-8") as f:
            self.assertIn("<Timeline rows={res.data} />", f.read())
        with open(os.path.join(SITE, "scripts", "check-values.mjs"), encoding="utf-8") as f:
            self.assertIn('if (p[0] === "dctime") {', f.read())
        with open(os.path.join(SITE, "app", "datacenters", "Timeline.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("no wait is estimated from one", s)
        self.assertNotIn("—", s)


if __name__ == "__main__":
    unittest.main()
