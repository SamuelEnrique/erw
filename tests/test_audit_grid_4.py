"""Audit of the Grid tool, finding 4 (session 10205, docs/reviews/grid-model-audit-2026-11-26.md): the carbon figures'
words claim more than EIA's estimate holds. "Each MWh it generated carried X kg of CO2" and "imports counted" read as a
measured hourly figure that also says what a load adds. It is an average over all the power of the hour, each fuel at
one emission factor, with imports at EIA's own valuation.

1. Against the warehouse (passes on main, skipped where the tables are not on the machine):
   a. EIA's natural gas CO2 over EIA-930's natural gas generation in ERCOT holds within 1.5 percent of its median over
      the hours both tables hold since 20 October 2026 (5th to 95th percentile): one factor per fuel.
   b. On EIA's workbook extract for ERCOT, the hour-to-hour change in CO2 over the change in net generation is under
      two thirds of the year's average intensity: average and marginal differ.
2. The fix on this branch (fails on main): the page and the note say what the figure is."""
import glob
import os
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.environ.get("ERW_AUDIT_OUTPUT_DIR", os.path.join(ROOT, "warehouse", "output"))
RAW = os.environ.get("ERW_AUDIT_RAW_DIR", os.path.join(ROOT, "warehouse", "raw"))


def read_rows(name, keep):
    import pandas as pd
    path = os.path.join(OUT, name + ".csv")
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    parts = [c[keep(c)] for c in pd.read_csv(path, skiprows=n, usecols=["entity", "variable", "ts_utc", "value"], chunksize=400_000)]
    return pd.concat(parts)


class WhatTheIntensityIs(unittest.TestCase):
    def test_one_factor_per_fuel(self):
        if not (os.path.exists(os.path.join(OUT, "eia930_all_emissions.csv")) and os.path.exists(os.path.join(OUT, "eia930_all_generation.csv"))):
            self.skipTest("eia930_all_emissions or eia930_all_generation is not on this machine")
        import pandas as pd
        e = read_rows("eia930_all_emissions", lambda c: (c["entity"] == "eia930:ERCO") & (c["variable"] == "co2_emissions_natural_gas") & (c["ts_utc"] >= "2026-10-20"))
        g = read_rows("eia930_all_generation", lambda c: (c["entity"] == "eia930:ERCO") & (c["variable"] == "net_generation_natural_gas_mw") & (c["ts_utc"] >= "2026-10-20"))
        j = pd.concat([e.set_index("ts_utc")["value"].rename("co2"), g.set_index("ts_utc")["value"].rename("mw")], axis=1).dropna()
        j = j[j["mw"] > 50]
        if len(j) < 48:
            self.skipTest("fewer than 48 hours held by both tables")
        f = j["co2"] * 1000 / j["mw"]
        med = f.median()
        self.assertLess(f.quantile(0.95) / med - 1, 0.015)
        self.assertLess(1 - f.quantile(0.05) / med, 0.015)

    def test_average_is_not_marginal(self):
        found = sorted(glob.glob(os.path.join(RAW, "eia930_emissions", "*", "erco_hours.csv")))
        if not found:
            self.skipTest("no EIA workbook extract for ERCOT on this machine")
        import pandas as pd
        x = pd.read_csv(found[-1], comment="#", usecols=["ts_utc", "net_generation_mwh", "co2_emissions_generated"])
        x = x.dropna()
        x = x.sort_values("ts_utc").tail(8760).copy()
        x["t"] = pd.to_datetime(x["ts_utc"], utc=True)
        d = x[["t", "net_generation_mwh", "co2_emissions_generated"]].diff()
        ok = d["t"] == pd.Timedelta(hours=1)
        slope = np.polyfit(d.loc[ok, "net_generation_mwh"], d.loc[ok, "co2_emissions_generated"] * 1000, 1)[0]
        avg = x["co2_emissions_generated"].sum() * 1000 / x["net_generation_mwh"].sum()
        self.assertLess(slope, avg * 2 / 3)

    def test_the_words_say_what_it_is(self):
        with open(os.path.join(ROOT, "site", "components", "grid", "NowView.tsx"), encoding="utf-8") as f:
            now = f.read()
        self.assertIn("an average over all the power made, not what an added MWh would emit", now)
        self.assertIn("imports counted at EIA&apos;s estimate", now)
        with open(os.path.join(ROOT, "site", "components", "grid", "Emissions.tsx"), encoding="utf-8") as f:
            em = f.read()
        self.assertIn("one emission factor for that fuel", em)
        self.assertIn("not the CO2 an added MWh of load would cause", em)
        with open(os.path.join(ROOT, "docs", "methods", "emissions.md"), encoding="utf-8") as f:
            note = f.read()
        self.assertIn("An average, not a marginal figure", note)
        self.assertIn("Imports at EIA's own estimate", note)


if __name__ == "__main__":
    unittest.main()
