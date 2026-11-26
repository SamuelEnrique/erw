"""Audit of the home page, finding 6 (session 10236, docs/reviews/home-model-audit-2026-11-26.md), a test only, for
Samuel's ruling: in the "Right now" strip a held grid's price is drawn "license needed" (components/Num.tsx, heldBy, for
latest_prices|<entity>|...), but the figure's unit and its line "real time, the interval from <time>" are drawn from the
held row all the same (the drawing of tonight: MISO "license needed USD/MWh real time, the interval from 2026-10-03 04:00
UTC"). It describes the row rather than reads its value, as the data audit's finding 8 found on /data.

This test shows the behaviour and passes on main. The choice, default "left as it is": draw a held grid's figure with no
unit and "real time" alone (3 interval times and 3 units not drawn while NYISO, MISO and ISO-NE are held). No fix is made.
Nothing here sets the environment, reads a table or makes a request."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheHeldGridsTime(unittest.TestCase):
    def test_the_strip_draws_the_held_rows_time_and_unit(self):
        page = src("site", "app", "page.tsx")
        self.assertIn("unit={p ? p.unit : undefined} when={p ? `real time, the interval from ${utc(p.ts_utc)}` : \"real time\"} />", page)
        start = page.index("async function RightNow()")
        body = page[start:page.index("function TodayChart()")]
        self.assertNotIn("heldBy", body)                          # the strip asks nothing of the hold for its unit and time
        self.assertIn('if (head === "latest_prices") {', src("site", "components", "Num.tsx"))

    def test_three_grids_of_the_strip_are_held(self):
        markets = json.loads(src("site", "data", "markets.json"))
        held = json.loads(src("site", "data", "license_status.json"))
        text = json.dumps(held)
        isos = [m["iso"] for m in markets["isos"]]
        self.assertEqual([i for i in isos if f'"{i}"' in text and i in ("NYISO", "MISO", "ISO-NE")], ["NYISO", "MISO", "ISO-NE"])


if __name__ == "__main__":
    unittest.main()
