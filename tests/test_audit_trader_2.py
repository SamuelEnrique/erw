"""Audit of the trader view, finding 2 (session 10209, docs/reviews/trader-model-audit-2026-11-26.md): the implied heat
rate divides the day-ahead daily mean by the Henry Hub spot price EIA dates on the operating day (or up to 4 days
before). EIA dates the daily spot by its trading day, gas traded that day for the next day's flow; the day-ahead power
of the operating day traded the day before. So on a weekday the gas was traded a day after the power, and at the
newest days the 4-day reach takes gas older than the power (on the board of 25 November 2026 the heat-rate week ends
21 November on Henry Hub of 17 November). The note said "the Henry Hub price is that of the operating day"; the page
said nothing.

1. The measured gap, from the page's own files (site/public/board/h/ercot-hb-hubavg.json and
   site/public/board/s/eia-henry-hub-spot.json, the 365 days to the hourly file's last whole day): the gas of the
   trading day before the operating day moves the daily heat rate by more than 0.2 MMBtu/MWh on average. Passes on main.
2. The fix on this branch, words only: the note says which gas, and a line under the week table says it. Drawn with the
   page's own component (no build). Fails on main. Taking the trading day before would move every heat rate: for
   Samuel's ruling, not made here."""
import collections
import datetime as dt
import json
import os
import statistics
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
const m = html.match(/<p[^>]*data-week-heat="1"[^>]*>([^<]*)<\\/p>/);
console.log(JSON.stringify({ line: m ? m[1].replace(/&#x27;/g, "'") : null }));
"""


def daily_means(hid, days=365):
    with open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8") as f:
        hf = json.load(f)
    tz = ZoneInfo(hf["tz"])
    by = collections.defaultdict(list)
    for i, v in enumerate(hf["da"]):
        if v is not None:
            by[dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz=dt.timezone.utc).astimezone(tz).date()].append(v)
    out = {}
    for d, vs in by.items():
        a = dt.datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(dt.timezone.utc)
        n = d + dt.timedelta(days=1)
        if len(vs) == round((dt.datetime(n.year, n.month, n.day, tzinfo=tz).astimezone(dt.timezone.utc) - a).total_seconds() / 3600):
            out[d] = sum(vs) / len(vs)
    last = max(out)
    return {d: m for d, m in out.items() if (last - d).days < days}


def henry_hub():
    with open(os.path.join(SITE, "public", "board", "s", "eia-henry-hub-spot.json"), encoding="utf-8") as f:
        s = json.load(f)
    t0 = dt.date.fromisoformat(s["t0"])
    return {t0 + dt.timedelta(days=d): v for d, v in zip(s["d"], s["v"])}


def gas(day, hh, back):
    for k in range(back, back + 5):
        if day - dt.timedelta(days=k) in hh:
            return hh[day - dt.timedelta(days=k)], day - dt.timedelta(days=k)
    return None, None


class HeatRateGasDay(unittest.TestCase):
    def test_the_trading_day_before_moves_the_heat_rate(self):
        hh = henry_hub()
        means = daily_means("ercot-hb-hubavg")
        diffs = []
        for d, m in sorted(means.items()):
            g0, _ = gas(d, hh, 0)
            g1, _ = gas(d, hh, 1)
            if g0 and g1 and g0 > 0 and g1 > 0:
                diffs.append(m / g0 - m / g1)
        print(f"\n  ERCOT hub average, {len(diffs)} days to {max(means)}: mean {statistics.mean(diffs):+.3f}, mean absolute "
              f"{statistics.mean(abs(x) for x in diffs):.3f}, largest {max(diffs, key=abs):+.3f} MMBtu/MWh, "
              f"days that move more than 0.5: {sum(1 for x in diffs if abs(x) > 0.5)}")
        self.assertGreater(len(diffs), 200)
        self.assertGreater(statistics.mean(abs(x) for x in diffs), 0.2)

    def test_the_newest_days_take_older_gas(self):
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            b = json.load(f)
        if not b["built"].startswith("2026-11-25"):
            self.skipTest(f"the measured file was built on 25 November 2026; this one {b['built']}")
        w = next(x for x in b["week"] if x["hub"] == "ercot-hb-hubavg")["means"]["implied_heat_rate"]
        end = dt.date.fromisoformat(w["end"])
        self.assertEqual(end, dt.date(2026, 11, 21))
        _, used = gas(end, henry_hub(), 0)
        self.assertEqual(used, dt.date(2026, 11, 17))         # four days before the power's day

    @unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
    def test_the_note_and_the_page_say_which_gas(self):
        with open(os.path.join(ROOT, "docs", "methods", "trader_view.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn("The Henry Hub price is that of the operating day", text)
        self.assertIn("EIA dates the daily spot by its trading day", text)
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS,
                              URL("lib", "board.ts"), URL("components", "board", "BoardView.tsx"), os.path.join(SITE, "data", "board.json")],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        line = json.loads(out.stdout.strip().splitlines()[-1])["line"]
        self.assertIsNotNone(line)
        self.assertIn("gas traded that day for the next day's flow, while the day-ahead power traded the day before", line)
        self.assertIn("up to 4 days older", line)


if __name__ == "__main__":
    unittest.main()
