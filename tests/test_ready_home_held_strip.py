"""wip/ready-home-held-strip (session 11406, chain 770, part C): the other choice of the home page audit of
26 November, finding 6 (docs/reviews/home-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the home page's "Right now" strip draws a held grid's price "license needed" but its unit and its line "real
time, the interval from <time>" from the held row all the same (MISO "license needed USD/MWh real time, the interval
from 2026-10-03 04:00 UTC"). On this branch a held grid's figure has no unit and reads "real time" alone: 3 units and 3
interval times are no longer drawn while NYISO, MISO and ISO-NE are held (before 3 and 3, after 0 and 0). The audit's
test (tests/test_audit_home_6.py on wip/audit-home-6) is carried, turned round."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheHeldGridDescribesNothing(unittest.TestCase):
    def test_the_strip_asks_the_hold_for_its_unit_and_time(self):
        page = src("site", "app", "page.tsx")
        self.assertIn('import { Num, heldBy } from "@/components/Num";', page)
        body = page[page.index("async function RightNow()"):page.index("function TodayChart()")]
        self.assertIn("const held = p ? heldBy(`latest_prices|${p.entity}|${p.variable}|${p.ts_utc}`) !== null : false;", body)
        self.assertIn("unit={p && !held ? p.unit : undefined} when={p && !held ? `real time, the interval from ${utc(p.ts_utc)}` : \"real time\"} />", body)
        self.assertIn("check={`latest_prices|${p.entity}|${p.variable}|${p.ts_utc}`}", body)   # the same key the figure's own hold reads

    def test_three_grids_of_the_strip_are_held(self):
        markets = json.loads(src("site", "data", "markets.json"))
        text = json.dumps(json.loads(src("site", "data", "license_status.json")))
        isos = [m["iso"] for m in markets["isos"]]
        self.assertEqual([i for i in isos if f'"{i}"' in text and i in ("NYISO", "MISO", "ISO-NE")], ["NYISO", "MISO", "ISO-NE"])


if __name__ == "__main__":
    unittest.main()
