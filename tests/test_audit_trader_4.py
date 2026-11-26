"""Audit of the trader view, finding 4 (session 10209, docs/reviews/trader-model-audit-2026-11-26.md): two heads of
the board's week table said nothing of what they measure.

- "30-day volatility" is the sample standard deviation of 30 day-over-day changes of the day-ahead daily mean, in
  USD/MWh, not annualized and not a percent (docs/methods/trader_view.md), where a trader reads volatility as an
  annualized percent. It needs all 31 calendar days: ERCOT's day-ahead days of 7 and 8 November 2026 are missing, so on
  the board of 25 November ERCOT's figure is the one of 6 November, marked stale, and will be until 9 December.
- "Hours RT over DA + 50" counts hours by the hour's mean of four 15-minute prices; over 26 August to 12 November 2026
  an interval of the hour ran 50 over day-ahead in 1.6 to 6.3 times as many hours (the audit, measured on the
  warehouse's tables).

1. Measured from the page's own files: ERCOT's volatility is of 6 November and its hourly file lacks 7 and 8 November
   whole; the newest 31 days held would give 12.06 against the 13.17 shown. Passes on main.
2. The fix on this branch, words only: both heads say what they measure on hover. Drawn with the page's own component
   (no build). Fails on main. No figure moves."""
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
const head = (k) => { const m = html.match(new RegExp('data-week-head="' + k + '" title="([^"]*)"')); return m ? m[1].replace(/&#x27;/g, "'") : null; };
console.log(JSON.stringify({ vol: head("vol"), hours50: head("hours50") }));
"""


def daily_means(hid):
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
    return out


class WeekHeadsSayWhatTheyMeasure(unittest.TestCase):
    def test_one_missing_day_stops_the_volatility(self):
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            b = json.load(f)
        if not b["built"].startswith("2026-11-25"):
            self.skipTest(f"the measured file was built on 25 November 2026; this one {b['built']}")
        w = next(x for x in b["week"] if x["hub"] == "ercot-hb-hubavg")
        self.assertEqual(w["vol"]["t"], "2026-11-06")
        self.assertAlmostEqual(w["vol"]["v"], 13.1671, delta=0.00005)
        means = daily_means("ercot-hb-hubavg")
        self.assertNotIn(dt.date(2026, 11, 7), means)
        self.assertNotIn(dt.date(2026, 11, 8), means)
        last31 = sorted(means)[-31:]
        ch = [means[last31[i]] - means[last31[i - 1]] for i in range(1, 31)]
        self.assertAlmostEqual(statistics.stdev(ch), 12.06, delta=0.005)

    def test_the_heads_say_what_they_measure(self):
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS,
                              URL("lib", "board.ts"), URL("components", "board", "BoardView.tsx"), os.path.join(SITE, "data", "board.json")],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertIsNotNone(r["vol"])
        self.assertIn("in USD/MWh: not annualized and not a percent", r["vol"])
        self.assertIn("one missing day leaves the last one standing, marked stale, for the 31 days after", r["vol"])
        self.assertIsNotNone(r["hours50"])
        self.assertIn("the mean of its four 15-minute prices", r["hours50"])


if __name__ == "__main__":
    unittest.main()
