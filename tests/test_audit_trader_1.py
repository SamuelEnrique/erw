"""Audit of the trader view, finding 1 (session 10209, docs/reviews/trader-model-audit-2026-11-26.md): SPP's real-time
prices are held (spp_rtm_hub_prices, the rows of iso_rtm_hub_prices whose market is spp_rtm, and the board's own SPP
real-time rows and hourly files), but warehouse/derived/trader_view.py's ISOS map gives SPP no real-time table, so the
week table's SPP real-time cells were empty with the hover "Needs a real-time price on each of the week's 7 days", and
the notes said "the ERW has no SPP real-time table".

1. The measured gap, from the page's own hourly file (site/public/board/h/spp-sppnorth-hub.json): the trader view's
   rule would give SPP North a real-time less day-ahead week of -3.73 USD/MWh (the 7 days with both markets whole to
   22 November 2026) on the board of 25 November; the board's week row holds none. Passes on main.
2. The fix on this branch, words only: the notes say the table is held and not read; the week's three SPP real-time
   cells say "not computed" with the reason on hover. Drawn with the page's own component (no build). Fails on main.
   Computing SPP's real-time metrics would add figures: for Samuel's ruling, not made here."""
import collections
import datetime as dt
import json
import os
import re
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
const spp = (html.match(/data-week-spp-rt="1"/g) || []).length;
const said = (html.match(/SPP&#x27;s real-time prices are held \\(the real-time rows of the groups above\\), but the week&#x27;s real-time measures are not computed for SPP: the trader view does not read them\\./g) || []).length;
console.log(JSON.stringify({ spp, said }));
"""


def whole_days(hf, market):
    tz = ZoneInfo(hf["tz"])
    by = collections.defaultdict(list)
    for i, v in enumerate(hf.get(market) or []):
        if v is None:
            continue
        u = dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz=dt.timezone.utc)
        by[u.astimezone(tz).date()].append((u, v))
    out = {}
    for d, hv in by.items():
        a = dt.datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(dt.timezone.utc)
        n = d + dt.timedelta(days=1)
        want = round((dt.datetime(n.year, n.month, n.day, tzinfo=tz).astimezone(dt.timezone.utc) - a).total_seconds() / 3600)
        if len(hv) == want:
            out[d] = sorted(hv)
    return out


class SppRealTimeIsHeldAndNotRead(unittest.TestCase):
    def test_the_code_reads_no_spp_real_time_table(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "trader_view.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertRegex(src, r'"spp": \("spp_dam_hub_prices", "spp_rtm_hub_prices", "America/Chicago"\)')   # wip/ready-trader-spp-rt: read
        with open(os.path.join(ROOT, "warehouse", "connectors", "iso_prices.py"), encoding="utf-8") as f:
            self.assertIn('file="spp_rtm_hub_prices"', f.read())

    def test_the_week_would_hold_spp_real_time(self):
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            b = json.load(f)
        if not b["built"].startswith("2026-11-25"):
            self.skipTest(f"the measured file was built on 25 November 2026; this one {b['built']}")
        w = next(x for x in b["week"] if x["hub"] == "spp-sppnorth-hub")
        self.assertNotIn("da_rt_spread_mean_usd", w["means"])
        self.assertNotIn("max_spread", w)
        with open(os.path.join(SITE, "public", "board", "h", "spp-sppnorth-hub.json"), encoding="utf-8") as f:
            hf = json.load(f)
        da, rt = whole_days(hf, "da"), whole_days(hf, "rt")
        both = sorted(d for d in da if d in rt and [u for u, _ in rt[d]] == [u for u, _ in da[d]])
        wk = both[-7:]
        self.assertEqual(len(wk), 7)
        means = [sum(r - a for (_, a), (_, r) in zip(da[d], rt[d])) / len(da[d]) for d in wk]
        self.assertAlmostEqual(sum(means) / 7, -3.73, delta=0.005)
        self.assertEqual(str(wk[-1]), "2026-11-22")

    @unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
    def test_the_notes_and_the_page_say_so(self):
        for p in (("docs", "methods", "trader_view.md"), ("docs", "methods", "iso_trader_daily.md")):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn("the ERW has no SPP real-time table", text)
            self.assertIn("finding 1", text)
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS,
                              URL("lib", "board.ts"), URL("components", "board", "BoardView.tsx"), os.path.join(SITE, "data", "board.json")],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["spp"], 0)          # wip/ready-trader-spp-rt: no SPP-only words; an empty cell has every grid's reason
        self.assertEqual(r["said"], 0)


if __name__ == "__main__":
    unittest.main()
