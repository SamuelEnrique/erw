"""Audit of "What a datacenter pays", finding 6 (session 10203, docs/reviews/datacenter-model-audit-2026-11-26.md): "How
clean?" says the power the load used "carried" so many kg of CO2 per MWh. The figure is the grid's average intensity of
consumed electricity (EIA-930), month by month weighted by the load's monthly energy (site/lib/datacenter/answers.ts),
and hour by hour over a window: location-based and average, not what the load's own demand adds at the margin.

1. Through the page's library (run by Node) on the page's own files: a load that moves 20 percent of each day's energy to
   the day's cheapest hours has, month by month, exactly a flat load's energy, so at the monthly average it carries the
   flat load's carbon to the gram whatever hours it runs in. Passes on main: the figure is an average.
2. The fix on this branch, words only: the note under "How clean?" says it is an average, location-based, and not the
   emissions the load's own demand adds at the margin. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "datacenter.ts").replace("\\", "/")
JS = """
const L = await import(process.argv[1]);
const fs = await import("node:fs");
const dir = process.argv[2];
const index = JSON.parse(fs.readFileSync(dir + "/index.json", "utf-8"));
const files = index.grids.ercot.years.map((y) => JSON.parse(fs.readFileSync(dir + "/ercot_" + y + ".json", "utf-8")));
const flat = L.lastTwelve(L.monthsRuled(files, "LZ_NORTH", "rt", { run: "flat", n: 0, pct: 0, shift: 0 }, "forecast").months);
const shift = L.lastTwelve(L.monthsRuled(files, "LZ_NORTH", "rt", { run: "shift", n: 0, pct: 0, shift: 20 }, "forecast").months);
console.log(JSON.stringify({ flat: flat.map((m) => [m.m, m.energy]), shift: shift.map((m) => [m.m, m.energy]) }));
"""


class CarbonIsAnAverage(unittest.TestCase):
    def test_monthly_carbon_is_blind_to_the_hours(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, os.path.join(ROOT, "site", "data", "datacenter")], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual([m for m, _ in r["flat"]], [m for m, _ in r["shift"]])
        for (m, a), (_, b) in zip(r["flat"], r["shift"]):
            self.assertAlmostEqual(a, b, places=9, msg=m)          # the same energy each month: the same monthly carbon

    def test_the_note_says_average_not_marginal(self):
        with open(os.path.join(ROOT, "site", "app", "cost-of-power", "LoadAnswers.tsx"), encoding="utf-8") as f:
            self.assertIn("Each figure is an average of what the grid&apos;s consumed electricity carried (location-based): not the emissions the load&apos;s own demand adds at the margin", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "datacenter_pays_algorithm.md"), encoding="utf-8") as f:
            self.assertIn("not the emissions the load's own demand adds at the margin (no marginal rate is held in the warehouse)", f.read())


if __name__ == "__main__":
    unittest.main()
