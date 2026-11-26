"""Audit of the price board, finding 4 (session 10206, docs/reviews/board-model-audit-2026-11-26.md): the headline strip's
"Lowest of 3 grids" and "Highest of 3 grids" compare the newest day every priced main hub holds (site/lib/board.ts,
gridExtremes). On the file of 25 November 2026 ERCOT's day-ahead row ended on 20 November, so the strip compared
20 November, five days before the build, with no stale mark, while the four closes beside it and every tile carry one.

The fix on this branch, words only (a mark): the two cells read "(stale)" beside the day past a market's 3 days, with
the age on hover (weekStale, the week table's rule), and carry data-head-stale. Drawn with the page's own component on
the site's file, and on a copy whose build day is set in memory to the strip's day (no mark). No figure moves.
Fails on main."""
import json
import os
import subprocess
import unittest

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
const file = B.holdRows(raw, ["NYISO", "ISO-NE", "MISO", "PJM"]);
const ex = B.gridExtremes(file, "da");
const cell = (html, k) => (html.match(new RegExp(`<button[^>]*data-head-cell="${k}"[^>]*>[\\\\s\\\\S]*?</button>`)) ?? [""])[0];
const read = (f) => { const html = renderToStaticMarkup(h(BoardView, { file: f })); return ["low", "high"].map((k) => { const c = cell(html, k); return { stale: c.includes(`data-head-stale="${k}"`), mark: c.includes("(stale)"), age: c.includes("Stale: a market&#x27;s daily figure is marked stale past 3 days") }; }); };
console.log(JSON.stringify({ day: ex.day, built: file.built, now: read(file), fresh: read({ ...file, built: `${ex.day}T12:00:00Z` }), values: [ex.low.v, ex.high.v] }));
"""


class StripDayMarkedStale(unittest.TestCase):
    def test_the_strip_marks_an_old_day(self):
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS,
                              URL("lib", "board.ts"), URL("components", "board", "BoardView.tsx"), os.path.join(SITE, "data", "board.json")],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads(out.stdout.strip().splitlines()[-1])
        if r["built"].startswith("2026-11-25"):
            self.assertEqual(r["day"], "2026-11-20")
        old = (int(r["built"][8:10]) - int(r["day"][8:10])) > 3 if r["built"][:7] == r["day"][:7] else True
        for c in r["now"]:
            self.assertEqual((c["stale"], c["mark"], c["age"]), (old, old, old))
        for c in r["fresh"]:
            self.assertEqual((c["stale"], c["mark"]), (False, False))
        with open(os.path.join(ROOT, "docs", "methods", "price_board.md"), encoding="utf-8") as f:
            self.assertIn("**Since session 10206** (`docs/reviews/board-model-audit-2026-11-26.md`, finding 4)", f.read())


if __name__ == "__main__":
    unittest.main()
