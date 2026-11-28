"""Ready branch for /forecast (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "two lines read tables
filled by ERCOT's legacy /misapp pulls (your ruling 2): the operator's wind and solar comparison and the real-time price
line. Keep, or drop"). Not the default: it waits for Samuel's ruling.

The other choice, in the builders: Texas's operator forecast of wind and solar (ercot_wind_solar_forecast) is not used
(predict_ws.USE_ERCOT_LEGACY; wind_solar.py says why in each fuel's operator_held), and no ERCOT hub's real-time price is
forecast (rt_price.LEGACY_MISAPP). On the files now on main: rt_price.json holds 7 hubs, 4 of them ERCOT's, and 2,760
score rows, 1,872 of them ERCOT's (after: 3 hubs, 888 rows); wind_solar.json holds Texas's operator forecast for wind
and solar and 8 Texas operator score rows (after: none, each fuel's operator_held saying why). The site files are
rebuilt at landing by the desk. tests/test_predict.py's hub order test is turned (skipped until the rebuild).

1. predict_ws.panels drops Texas's operator columns after the cache, on a frame the test makes (no table read).
2. rt_price leaves out every ERCOT hub and keeps the others.
3. The words."""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(ROOT, "warehouse", "predict"))
import predict_ws as ws  # noqa: E402
import predict_rt as rtm  # noqa: E402
import rt_price  # noqa: E402


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheLegacyLinesAreNotWritten(unittest.TestCase):
    def test_texas_operator_columns_dropped(self):
        self.assertFalse(ws.USE_ERCOT_LEGACY)
        frame = pd.DataFrame({"region-tex|wind|actual": [1.0], "region-tex|wind|operator": [2.0], "region-tex|solar|operator": [3.0],
                              "grid-caiso|wind|operator": [4.0]})
        keep = ws.data.cached
        try:
            ws.data.cached = lambda key, names, build: frame
            df = ws.panels()
        finally:
            ws.data.cached = keep
        self.assertEqual(list(df.columns), ["region-tex|wind|actual", "grid-caiso|wind|operator"])
        a, o = ws.series_of(df, "region-tex", "wind")
        self.assertIsNotNone(a)
        self.assertIsNone(o)

    def test_no_ercot_real_time_hub(self):
        self.assertEqual(rt_price.LEGACY_MISAPP, {g for g in rtm.RT_HUBS if g.startswith("ercot")})
        self.assertIn("ercot", rt_price.LEGACY_MISAPP)
        self.assertTrue({"spp", "caiso"} <= set(rtm.RT_HUBS) - rt_price.LEGACY_MISAPP)
        self.assertIn("for grid in [g for g in rtm.RT_HUBS if g not in LEGACY_MISAPP]:", src("warehouse", "predict", "rt_price.py"))

    def test_the_words(self):
        self.assertIn('NOT_USED = {"region-tex": "not used: ERCOT\'s short-term wind and solar forecasts are filled by pulls from paths',
                      src("warehouse", "predict", "wind_solar.py"))
        self.assertIn("so Texas's operator forecast is not used (`USE_ERCOT_LEGACY`", src("docs", "methods", "predict_wind_solar.md"))
        self.assertIn("so no\nERCOT hub's real-time price is forecast (`LEGACY_MISAPP`", src("docs", "methods", "predict_price.md"))


if __name__ == "__main__":
    unittest.main()
