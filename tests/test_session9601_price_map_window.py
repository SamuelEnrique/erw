"""Session 9601 (chain 620, 20 November 2026): the Grid map's price over a window says which days the window holds.

Energy Research Warehouse (ERW). Part C of the browser read set the map's Price color beside `/prices/compare`. For
"twelve months" the two pages give different figures for the same hub (ERCOT's hub average: 34.86 on the map, 34.59
on `/prices/compare`), and both are right: the map's window is the 365 local days ending on the file's day
(`docs/methods/prices_map.md`), the comparison's the twelve calendar months to the last whole month. The map's hover
said "Average over twelve months" with no days, so the two read as a contradiction.

Held here, on the source and the committed file: the hover of a thirty-day or twelve-month figure names its window's
days; a day's figure names the day, as before; a blank says why, as before; the method note gives the same windows;
the file holds a day for every hub it shows. Nothing here sets the environment, reads a table or makes a request.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheHover(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "components", "grid", "MapPrice.tsx")

    def test_a_window_names_its_days(self):
        self.assertIn('const span = k.startsWith("day") ? `, ${b.day}` : b.day ? `, the ${k.includes("30d") ? "30" : "365"} days to ${b.day}` : "";', self.s)
        self.assertIn('at ${b.hub?.split(":")[1] ?? "its main hub"}, day-ahead${span}`', self.s)

    def test_a_blank_still_says_why(self):
        self.assertIn('`Price: not held (${why ?? "no figure for this measure"})`', self.s)
        self.assertIn('if (b.state === "held") return "Price: license needed";', self.s)

    def test_the_measures_and_their_names_are_as_they_were(self):
        for line in ('["avg_30d", "Average over 30 days", "USD/MWh"]', '["avg_12m", "Average over twelve months", "USD/MWh"]'):
            self.assertIn(line, self.s)

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.s)
        self.assertNotIn(EM, src("tests", "test_session9601_price_map_window.py"))


class TheFileAndTheNote(unittest.TestCase):
    def test_the_method_note_gives_the_same_windows(self):
        self.assertIn("The thirty and 365 local days ending on that day give the mean and the share of hours below zero.", src("docs", "methods", "prices_map.md"))

    def test_every_area_shown_names_its_day(self):
        p = json.loads(src("site", "data", "regions", "prices_map.json"))
        shown = [b for b in p["bas"].values() if b.get("state") == "shown"]
        self.assertGreater(len(shown), 0)
        for b in shown:
            self.assertRegex(b.get("day") or "", r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
