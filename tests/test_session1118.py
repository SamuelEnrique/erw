"""Session 1118 (chain 075): the mini-analyses: what a spread's newest value was made of, in its hover.

Held here, on the site's own file (site/data/board.json, the builder's output): the builder's spark_inputs, run on the
last 30 day-ahead means of ERCOT's hub and Henry Hub's last 30 closes as the board holds them, gives the hub's value,
the gas price and its own day, and the stated heat rate, and those make the board's own newest spark spread; the
implied heat rate is the hub over the gas; crack_inputs' three prices make the 3-2-1 crack the board shows; the page
draws the words (site/lib/board.ts inputsWords) on the latest value's cell, and the hold drops them with the figures.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import datetime as dt
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


def rows():
    with open(os.path.join(ROOT, "site", "data", "board.json"), encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)["rows"]}


def points(row):
    t0 = dt.date.fromisoformat(row["spark"]["t0"])
    return {t0 + dt.timedelta(days=d): v for d, v in zip(row["spark"]["d"], row["spark"]["v"])}


class TheInputs(unittest.TestCase):
    def setUp(self):
        self.bp, self.rows = builder(), rows()

    def test_the_spark_spread_is_its_inputs(self):
        da, gas = points(self.rows["ercot-hb-hubavg-da"]), points(self.rows["eia-henry-hub-spot"])
        i = self.bp.spark_inputs(da, gas)
        self.assertEqual(i["heat_rate"], self.bp.HEAT_RATE)
        d, g = dt.date.fromisoformat(i["t"]), dt.date.fromisoformat(i["gas_t"])
        self.assertTrue(dt.timedelta(0) <= d - g <= dt.timedelta(days=self.bp.GAS_BACK))
        self.assertEqual(i["hub"], round(da[d], 4))
        self.assertEqual(i["gas"], round(gas[g], 4))
        spread = points(self.rows["ercot-hb-hubavg-spark"])
        if d in spread:   # the board's own spread on that day is the inputs' arithmetic, to the file's rounding
            self.assertAlmostEqual(spread[d], i["hub"] - i["heat_rate"] * i["gas"], places=3)
        heat = self.bp.implied_heat_rate(da, gas)
        self.assertAlmostEqual(heat[d], da[d] / gas[g], places=9)

    def test_the_crack_is_its_three_prices(self):
        r = self.rows
        g = points(r["eia-eer-epmru-pf4-rgc-dpg-spot"]) if "eia-eer-epmru-pf4-rgc-dpg-spot" in r else None
        dsl = points(r["eia-eer-epd2dxl0-pf4-rgc-dpg-spot"]) if "eia-eer-epd2dxl0-pf4-rgc-dpg-spot" in r else None
        if not g or not dsl:
            raise unittest.SkipTest("the Gulf Coast product rows are not in this copy's board file")
        wti = points(r["eia-wti-cushing-spot"])
        i = self.bp.crack_inputs(g, dsl, wti)
        d = dt.date.fromisoformat(i["t"])
        self.assertAlmostEqual(self.bp.crack(g, dsl, wti)[d], (2 * i["gasoline"] + i["diesel"]) * 42 / 3 - i["crude"], places=3)
        crack = points(r["erw-crack-321-gulf-coast"])
        if d in crack:
            self.assertAlmostEqual(crack[d], (2 * i["gasoline"] + i["diesel"]) * 42 / 3 - i["crude"], places=2)

    def test_no_input_no_words(self):
        self.assertIsNone(self.bp.spark_inputs({}, {}))
        self.assertIsNone(self.bp.dark_inputs({}, {}))
        self.assertIsNone(self.bp.crack_inputs({}, {}, {}))

    def test_the_page_draws_them_and_the_hold_drops_them(self):
        with open(os.path.join(ROOT, "site", "lib", "board.ts"), encoding="utf-8") as f:
            board = f.read()
        self.assertIn('"spark", "hourly", "inputs"] as const;', board)
        self.assertIn("export function inputsWords(row: Row): string | null {", board)
        with open(os.path.join(ROOT, "site", "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            self.assertIn("title={inputsWords(row) ?? undefined}", f.read())


if __name__ == "__main__":
    unittest.main()
