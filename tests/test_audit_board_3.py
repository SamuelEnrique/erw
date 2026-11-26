"""Audit of the price board, finding 3 (session 10206, docs/reviews/board-model-audit-2026-11-26.md): the week table's
"On-peak DA" and "Off-peak DA" (iso_trader_daily, warehouse/derived/trader_view.py) take the 5x16 block in every grid,
CAISO included, while the group "Power, on-peak and off-peak" takes CAISO's Monday to Saturday; and the on-peak week is
the latest 7 weekdays that hold one, over 9 calendar days, where the cell's hover said "the 7 days to".

1. The measured gap, from the page's own hourly file (site/public/board/h): SP15's off-peak week of the file of
   25 November is the 5x16 rule's (42.72), and the on-peak group's rule would give 45.36. Passes on main.
2. The fix on this branch, words only: the two column heads and the on-peak cells say which block and which days, in
   the week table and in the workbench, and the notes say so. Drawn with the page's own component (no build). Fails on
   main. No figure moves."""
import collections
import datetime as dt
import json
import os
import subprocess
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
URL = lambda *p: "file:///" + os.path.join(SITE, *p).replace("\\", "/")   # noqa: E731
JS = """
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
const B = await import(process.argv[1]);
const { BoardView } = await import(process.argv[2]);
const raw = JSON.parse(fs.readFileSync(process.argv[3], "utf-8"));
const html = renderToStaticMarkup(h(BoardView, { file: B.holdRows(raw, ["NYISO", "ISO-NE", "MISO", "PJM"]) }));
const heads = [...html.matchAll(/data-week-peak="([^"]+)"/g)].map((m) => m[1]);
const onpeak = [...html.matchAll(/title="(the latest 7 weekdays with an on-peak mean, to [^"]*)"/g)].map((m) => m[1]);
console.log(JSON.stringify({ heads, onpeak: onpeak.length, first: onpeak[0] ?? null, html: html.includes("CAISO&#x27;s Saturdays are off-peak here") }));
"""


def holidays(y):
    def nth(m, wd, n):
        d = dt.date(y, m, 1)
        return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
    last_may = dt.date(y, 5, 31) - dt.timedelta(days=(dt.date(y, 5, 31).weekday()) % 7)
    days = {dt.date(y, 1, 1), last_may, dt.date(y, 7, 4), nth(9, 0, 1), nth(11, 3, 4), dt.date(y, 12, 25)}
    return {d + dt.timedelta(days=1) if d.weekday() == 6 else d for d in days}


class WeekOnPeakIsFiveBySixteen(unittest.TestCase):
    def test_sp15_off_peak_week_is_the_five_day_block(self):
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            b = json.load(f)
        if not b["built"].startswith("2026-11-25"):
            self.skipTest(f"the measured file was built on 25 November 2026; this one {b['built']}")
        w = next(x for x in b["week"] if x["hub"] == "caiso-th-sp15-gen-apnd")["means"]["da_offpeak_mean_usd"]
        with open(os.path.join(SITE, "public", "board", "h", "caiso-th-sp15-gen-apnd.json"), encoding="utf-8") as f:
            hf = json.load(f)
        tz = ZoneInfo(hf["tz"])
        by = collections.defaultdict(list)
        for i, v in enumerate(hf["da"]):
            loc = dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz=dt.timezone.utc).astimezone(tz)
            by[loc.date()].append((loc, v))
        end = dt.date.fromisoformat(w["end"])
        days = [end - dt.timedelta(days=k) for k in range(6, -1, -1)]

        def off(last_weekday):
            means = []
            for d in days:
                vals = [v for loc, v in by[d] if not (loc.weekday() <= last_weekday and 6 <= loc.hour <= 21 and d not in holidays(d.year))]
                means.append(sum(vals) / len(vals))
            return sum(means) / 7
        self.assertAlmostEqual(off(4), w["v"], delta=0.005)          # Monday to Friday: the week table's figure
        self.assertAlmostEqual(off(5), 45.36, delta=0.005)           # Monday to Saturday: the on-peak group's rule for CAISO
        self.assertAlmostEqual(w["v"], 42.72, delta=0.005)

    @unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
    def test_the_heads_and_cells_say_the_block_and_the_days(self):
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS,
                              URL("lib", "board.ts"), URL("components", "board", "BoardView.tsx"), os.path.join(SITE, "data", "board.json")],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["heads"], ["da_onpeak_mean_usd", "da_offpeak_mean_usd"])
        self.assertTrue(r["html"])
        self.assertGreater(r["onpeak"], 0)
        self.assertIn("the change is on the 7 such weekdays before", r["first"])
        with open(os.path.join(SITE, "components", "board", "Workbench.tsx"), encoding="utf-8") as f:
            self.assertIn("the latest 7 weekdays with an on-peak mean (Monday to Friday in every grid, CAISO included)", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "price_board.md"), encoding="utf-8") as f:
            self.assertIn("**The week's on-peak is not the on-peak group's (session 10206", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "trader_view.md"), encoding="utf-8") as f:
            self.assertIn("in every grid (CAISO's Saturdays included among the off-peak days", f.read())


if __name__ == "__main__":
    unittest.main()
