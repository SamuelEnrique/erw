"""Session 8013 (chain 505, part E2): what power costs across the map (site/data/regions/prices_map.json).

Contract: section 13 of docs/state/page_files_regions.md. Held grids carry their key with no figure and "license
needed"; a paused grid says so; no figure is drawn for either.
"""

import datetime as dt
import json
import os
import sys
import unittest

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "warehouse", "derived"))
FILE = os.path.join(REPO, "site", "data", "regions", "prices_map.json")
FIGS = ("day_avg", "day_on_peak", "day_off_peak", "day_spread_top4_bottom4", "avg_30d", "negative_share_30d_pct", "avg_12m", "negative_share_12m_pct")


def load():
    with open(FILE, encoding="utf-8") as f:
        return json.load(f)


class TheWindow(unittest.TestCase):
    def test_a_short_window_is_blank_with_its_reason(self):
        import prices_map as pm
        tz = "America/Chicago"
        idx = pd.date_range(pd.Timestamp("2026-11-01", tz=tz).tz_convert("UTC"), periods=24 * 20, freq="h")
        h = pd.Series(10.0, index=idx)
        avg, neg, why = pm.window(h, tz, dt.date(2026, 11, 20), 30)
        self.assertIsNone(avg)
        self.assertIn("under 95%", why)
        avg, neg, why = pm.window(h, tz, dt.date(2026, 11, 20), 20)
        self.assertEqual((avg, neg, why), (10.0, 0.0, None))


class TheFile(unittest.TestCase):
    def test_held_and_paused_grids_carry_no_figure(self):
        d = load()
        shown = {g["grid"] for g in d["grids"] if g["state"] == "shown"}
        for g in d["grids"]:
            if g["state"] == "held":
                self.assertTrue(g["why"].startswith("license needed"), g["grid"])
            if g["state"] != "shown":
                self.assertNotIn(g["grid"], {h["grid"] for h in d["hubs"]})
        for h in d["hubs"]:
            self.assertIn(h["grid"], shown)
        self.assertIn("PJM", {g["grid"] for g in d["grids"] if g["state"] == "held"})

    def test_an_authority_area_is_its_grids_main_hub_or_its_reason(self):
        d = load()
        by = {h["entity"]: h for h in d["hubs"]}
        for ba, v in d["bas"].items():
            if v["state"] == "shown" and "hub" in v and v["hub"] in by:
                for k in FIGS:
                    self.assertEqual(v.get(k), by[v["hub"]].get(k), (ba, k))
            else:
                self.assertTrue(v.get("why"), ba)

    def test_a_blank_window_says_why(self):
        for h in load()["hubs"]:
            for k in ("30d", "12m"):
                if h.get("day") and h.get(f"avg_{k}") is None:
                    self.assertTrue(h.get(f"window_{k}_why"), (h["entity"], k))


if __name__ == "__main__":
    unittest.main()


class TheLayer(unittest.TestCase):
    """Part E3: the map's areas by carbon (as it opens) or by price, in the Grid tool only."""

    def src(self, *p):
        with open(os.path.join(REPO, "site", *p), encoding="utf-8") as f:
            return f.read()

    def test_carbon_opens_and_price_is_a_choice(self):
        n = self.src("app", "network", "Network.tsx")
        self.assertIn("const [mapPrice, setMapPrice] = useState(false);", n)
        self.assertIn('{shape === "map" && baRegions ? <PriceControls', n)

    def test_a_held_grid_is_blank_and_says_license_needed(self):
        c = self.src("components", "grid", "MapPrice.tsx")
        self.assertIn('if (b.state === "held") return "Price: license needed";', c)
        self.assertIn('b && b.state === "shown" ? b[k] : null', c)

    def test_the_route_serves_the_file_or_says_not_held(self):
        r = self.src("app", "grid", "prices-map", "route.ts")
        self.assertIn('export const dynamic = "force-static";', r)
        self.assertIn("held: false", r)
