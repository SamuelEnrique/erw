"""Session 370 (the chain of 20 October 2026, day, code machine): the three checks that failed on production.

1. check-battery-scenarios' CAISO 2-hour case: the page was right. The file of steps (site/data/battery_scenario_steps.json,
   built 14 October) holds 29 days in each CAISO November; session 322 filled the three fall-back days and the live
   battery_stack_monthly holds 30, so the page offers the default step alone and says so. The check now asks the
   library (stepState) which state the page must be in, from the page's own months.csv.
2. check-datacenter: session 138's assertions follow the page as it stands (the figures session 213 moved are read from
   tables.csv), and the blocks that left the page are retired.
3. The shared SVG chart (components/svgchart.tsx, CategoryChart): a name at the right wider than its room is drawn in
   lines that fit (lib/chartwrap.ts); a name that fits is drawn as before.
Energy Research Warehouse (ERW)."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)
MINE = (("site", "lib", "chartwrap.ts"), ("site", "components", "svgchart.tsx"), ("site", "scripts", "check-datacenter.mjs"),
        ("site", "scripts", "check-battery-scenarios.mjs"), ("tests", "test_session370.py"))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


# the names that ran past the box on production at 390 px (runs/chain_oct20d/s370/cards_prod_390.out)
NAMES = ["ERCOT battery fleet (MW, operating)", "Worst-interval multiple (P99.9 / median)", "ERCOT: battery fleet, MW operating (EIA-860M)",
         "ERCOT North Hub real-time price minus NYISO New York City real-time price", "spp:SPP curtailed_solar_redispatch_mwh", "Flat load"]


class TheNames(unittest.TestCase):
    def test_a_name_that_fits_is_one_line_and_a_long_one_fits_its_room(self):
        out = node("const w = await import('./lib/chartwrap.ts'); const names = " + json.dumps(NAMES) + ";"
                   "console.log(JSON.stringify({ char: w.CHAR, at156: names.map((n) => w.wrapName(n, 156)), at400: names.map((n) => w.wrapName(n, 400)) }));")
        per = 12 * out["char"]
        for name, lines in zip(NAMES, out["at156"]):
            for line in lines:
                self.assertLessEqual(len(line) * per, 156, line)          # every line fits the room
            self.assertEqual("".join(lines).replace(" ", ""), name.replace(" ", ""))   # nothing lost, nothing added
        self.assertEqual(out["at156"][-1], ["Flat load"])                  # a name that fits stays one line
        self.assertEqual(out["at156"][0], ["ERCOT battery fleet (MW,", "operating)"])
        self.assertGreater(len(out["at156"][3]), 2)
        self.assertIn("curtailed_solar_redispa", "".join(out["at156"][4]))   # a word wider than the room is cut into pieces
        self.assertEqual(out["at400"][:3], [[n] for n in NAMES[:3]])        # with room, one line each

    def test_one_line_names_are_placed_as_before(self):
        # before session 370: sorted by y, each at least 13 px below the one above it, nothing else
        ys = [120.0, 125.0, 40.0, 41.0, 280.0, 290.0]
        out = node("const w = await import('./lib/chartwrap.ts');"
                   "const e = " + json.dumps([{"k": i, "y": y, "lines": ["x"]} for i, y in enumerate(ys)]) + ";"
                   "console.log(JSON.stringify(w.stackNames(e, 294).map((x) => [x.k, x.y])));")
        old = sorted(({"k": i, "y": y} for i, y in enumerate(ys)), key=lambda e: e["y"])
        for i in range(1, len(old)):
            if old[i]["y"] < old[i - 1]["y"] + 13:
                old[i]["y"] = old[i - 1]["y"] + 13
        self.assertEqual(out, [[e["k"], e["y"]] for e in old])

    def test_wrapped_names_do_not_overlap_and_stay_inside(self):
        out = node("const w = await import('./lib/chartwrap.ts');"
                   "const e = [{ k: 0, y: 280, lines: ['a', 'b', 'c'] }, { k: 1, y: 270, lines: ['d', 'e'] }, { k: 2, y: 30, lines: ['f'] }];"
                   "console.log(JSON.stringify(w.stackNames(e, 294)));")
        for a, b in zip(out, out[1:]):
            self.assertGreaterEqual(b["y"], a["y"] + 13 * len(a["lines"]))
        last = out[-1]
        self.assertLessEqual(last["y"] + 13 * (len(last["lines"]) - 1), 294)
        self.assertEqual(out[0]["y"], 30)                                  # a name with room is not moved

    def test_the_chart_draws_through_it(self):
        s = src("site", "components", "svgchart.tsx")
        self.assertIn('import { stackNames, wrapName } from "@/lib/chartwrap";', s)
        self.assertIn("wrapName(series[e.k].name, W - endX - 2)", s)
        self.assertIn("lines.length === 1 ? series[k].name", s)            # a name that fits is the same text node as before
        self.assertIn("<tspan key={j} x={endX} dy={j ? 13 : 0}>", s)
        self.assertIn("stackNames(ends, height - 6);", s)                  # the placing is the library's
        self.assertEqual(s.count('data-direct-labels="1"'), 7)             # session 317's count, unchanged
        self.assertNotIn("\nimport ", src("site", "lib", "chartwrap.ts"))   # Node runs it as it is


class TheChecks(unittest.TestCase):
    def test_battery_scenarios_asks_the_library(self):
        s = src("site", "scripts", "check-battery-scenarios.mjs")
        self.assertIn("function stepsExpected(csv, key)", s)
        self.assertIn("F.stepState(c, ms, (B.last36(ms)?.months ?? []).map((r) => r.m))", s)
        self.assertIn("/cost-of-power/battery/months.csv?grid=caiso&dur=2&strat=foresight&mw=5000", s)
        self.assertIn("s.steps === want.state", s)
        self.assertNotIn('s.steps === "held" && Number(s.fields.find((f) => f.key === "capex").value) === 610', s)

    def test_the_steps_file_is_behind_the_live_months_in_caisos_novembers(self):
        # the cause, as the session found it: the file of 14 October counts 29 days in each November of CAISO
        f = json.loads(src("site", "data", "battery_scenario_steps.json"))
        c = f["cases"]["caiso|foresight|2"]
        nov = {m: d for m, d in zip(c["months"], c["days"]) if m.endswith("-11")}
        if f["built"] > "2026-10-20":
            self.skipTest("the file of steps was rebuilt after session 370")
        self.assertEqual(nov, {"2023-11": 29, "2024-11": 29, "2025-11": 29})

    def test_datacenter_follows_the_page(self):
        s = src("site", "scripts", "check-datacenter.mjs")
        for said in ('"What will it pay?"', "datacenter_pays_algorithm#cannot-see", "/cost-of-power/tables.csv", '"large_load_in_line"',
                     "`hours_tight_${y}`", '"demand_by_region_"', "this_loads_own_hours_", 'data-matrix-rate="2025"', "is not held here, so ERCOT is shown",
                     "[data-year-cost] [data-chart-card]", "deliveryOf(d.rows, \"Oncor\", 100)"):
            self.assertIn(said, s)
        for gone in ("data-contract", "data-rules-fold", "echarts", "data-own_clean", "Hours the grid was tight\\s+licensed", "docs/methods/datacenter_cost.md"):
            self.assertNotIn(gone, s)

    def test_no_em_dash(self):
        for parts in MINE:
            self.assertNotIn(DASH, src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
