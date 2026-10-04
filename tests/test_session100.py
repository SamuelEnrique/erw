"""Session 100: New York and SPP. The reserve quantities each operator procures, the fleet-limited estimate, and each
product's duration rule as the operator's own document states it.

Energy Research Warehouse (ERW). The SPP connector (warehouse/connectors/spp_as_quantities.py) on files made here, with no
request; the shared framework's new options and their defaults; the caps of the analysis
(warehouse/analysis/battery_fleet_limited_review.py); the method note's quotations against the documents saved on the
data machine; and the table as built.

    python -m unittest tests.test_session100 -v
"""

import os
import re
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
import iso_as_common as common  # noqa: E402
import spp_as_quantities as sq  # noqa: E402
import battery_fleet_limited_review as fl  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SAVED = os.path.join(ROOT, "runs", "session100")
HEAD = "Interval,GMTIntervalEnd,{baa}Generation,RegUP,RegDN,RampUP,RampDN,UncUP,Spin,Supp\n"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def day_file(day="2026-09-01", baas=("SPP", "SWPW"), blank=None, drop=None):
    """A Day-Ahead Market Clearing file as SPP's: 24 hours of a Central daylight-time day, one row per BAA (or one row an
    hour with no BAA column, as before April 2026)."""
    lines = [HEAD.format(baa="BAA," if baas else "")]
    start = pd.Timestamp(day, tz="America/Chicago").tz_convert("UTC")
    for h in range(24):
        end = (start + pd.Timedelta(hours=h + 1)).tz_localize(None)
        for i, b in enumerate(baas or [None]):
            cells = [str(500 + h + 100 * i), str(400 + h), "200", "900", "0", str(700 + h), "650"]
            if blank == (b, h):
                cells[5] = ""
            if drop == (b, h):
                continue
            lines.append(f"{day} {h + 1:02d}:00:00,{end:%m/%d/%Y %H:%M:%S},{b + ',' if b else ''}30000.5,{','.join(cells)}\n")
    return "".join(lines)


class TheConnector(unittest.TestCase):
    def test_a_days_file_with_the_baa_column(self):
        d = sq.parse_day(day_file(), "2026-09-01", lambda *_: None)
        self.assertEqual(sorted(d["region"].unique()), ["SPP", "SWPW"])
        self.assertEqual(len(d), 2 * 7 * 24)
        self.assertEqual(sorted(d["variable"].unique()), sorted(sq.PRODUCTS.values()))
        x = d[(d["region"] == "SWPW") & (d["variable"] == "quantity_mw_dam_regup")].sort_values("ts")
        self.assertEqual(sq.ip.utc_iso(x["ts"].iloc[0]), "2026-09-01T05:00:00Z")             # the hour's start: GMTIntervalEnd less one hour
        self.assertEqual(list(x["value"].iloc[:2]), [600, 601])
        self.assertEqual(float(d[(d["region"] == "SPP") & (d["variable"] == "quantity_mw_dam_uncup")]["value"].sum()), 0.0)   # zero is a quantity

    def test_the_older_layout_is_the_systems_rows(self):
        d = sq.parse_day(day_file("2024-09-01", baas=None), "2024-09-01", lambda *_: None)
        self.assertEqual(list(d["region"].unique()), ["SPP"])
        self.assertEqual(len(d), 7 * 24)

    def test_an_empty_cell_is_no_row_and_a_changed_layout_stops_the_run(self):
        d = sq.parse_day(day_file(blank=("SPP", 7)), "2026-09-01", lambda *_: None)
        self.assertEqual(len(d), 2 * 7 * 24 - 1)
        rows, gaps = common.complete(d, sq.WANTED, sq.TZ, lambda *_: None)
        self.assertEqual(len(rows), 2 * 7 * 24 - 24)                                         # the day of that product and BAA is not written
        self.assertEqual(len(gaps), 1)
        with self.assertRaises(RuntimeError):
            sq.parse_day(day_file().replace(",Spin,", ",Spinning,"), "2026-09-01", lambda *_: None)
        with self.assertRaises(RuntimeError):
            sq.parse_day(day_file("2026-09-01"), "2026-09-02", lambda *_: None)             # hours outside the operating day

    def test_the_pulls_ceiling_unit_and_pause(self):
        self.assertEqual((sq.SPEC["ceiling"], sq.SPEC["unit"], sq.SPEC["namespace"], sq.SPEC["first"]), (300_000, "MW", "spp", "2024-09-01"))
        code = src("warehouse", "connectors", "iso_as_common.py")
        self.assertIn('ceiling = spec.get("ceiling", CEILING)', code)                        # the other reserve connectors keep 500,000
        self.assertIn('spec.get("unit", UNIT)', code)
        self.assertEqual((common.CEILING, common.UNIT), (500_000, "USD/MW-hour"))
        self.assertLess(code.index('if ip.paused(spec["namespace"])'), code.index('docs = spec["documents"]'))   # the pause is asked before any request
        self.assertIn("with appropriate citation", sq.SPEC["license_line"])
        for name in ("spp_as_prices", "nyiso_as_prices"):
            self.assertNotIn("ceiling=", src("warehouse", "connectors", f"{name}.py").split("SPEC = dict(")[1])


class TheCaps(unittest.TestCase):
    def test_a_cap_is_the_quantity_over_the_fleet_and_never_above_one(self):
        hrs = pd.date_range("2026-09-01T05:00:00Z", periods=4, freq="h")
        prods = [dict(key="regup"), dict(key="spin"), dict(key="reg")]
        qty = {"regup": pd.Series([100.0, 245.0, 490.0, 980.0], index=hrs), "spin": 655.0, "reg": None}
        caps, missing = fl.caps_of(prods, qty, hrs, 490.0)
        self.assertEqual(list(caps[0]), [100 / 490, 0.5, 1.0, 1.0])
        self.assertEqual(list(caps[1]), [1.0] * 4)                                           # 655 MW against a fleet of 490
        self.assertEqual(list(caps[2]), [1.0] * 4)                                           # no quantity held: not capped, and the output says so
        self.assertFalse(missing)
        caps, missing = fl.caps_of(prods[:1], {"regup": qty["regup"].iloc[:3]}, hrs, 490.0)
        self.assertTrue(missing)                                                             # an hour with no quantity: the day is left out
        self.assertEqual(float(fl.caps_of(prods[1:2], qty, hrs, 1310.0)[0][0][0]), 0.5)

    def test_what_the_analysis_takes_as_new_yorks_quantities(self):
        self.assertEqual(fl.NYISO_SPIN_MW, 655.0)
        self.assertEqual(fl.QUANTITY["nyiso"], {"constant": {"spin": 655.0}, "not_held": ["reg"]})
        self.assertEqual(set(fl.QUANTITY["spp"]["variables"]), {p["key"] for p in fl.bs.REVIEW_MARKETS["spp"]["products"]})
        code = src("warehouse", "analysis", "battery_fleet_limited_review.py")
        self.assertIn("analysis_internal", code)                                             # it writes no table of the live set
        self.assertNotIn("ip.write_csv", code)


class TheDurationRules(unittest.TestCase):
    QUOTES = {
        "nyiso_mst.txt": ["will be used to ensure that Operating Reserves scheduled from the Resource can be sustained for one hour if the Operating Reserves are converted to Energy",
                          "The ISO may reduce the real-time Regulation Capacity (in MW) from an Energy Storage Resource",
                          "The ISO shall establish and post a target level of Regulation Service for each hour"],
        "spp_protocols_119.txt": ["capable of deploying 100% of cleared Regulation-Up or cleared Regulation-Down within the Regulation Response Time for a continuous duration of 60 minutes",
                                  "within the Contingency Reserve Deployment Period for a continuous duration of 60 minutes",
                                  "will impact the Resource’s State of Charge by 50% of the cleared product"],
        "nyiso_loc_res.txt": ["½ A = 655"],
    }

    def test_the_method_note_quotes_the_documents_with_their_sections(self):
        doc = " ".join(src("docs", "methods", "reserve_quantities_nyiso_spp.md").split())
        for quotes in self.QUOTES.values():
            for q in quotes[:2]:
                self.assertIn(q.replace("’", "'").replace("½ A = 655", "655 MW"), doc.replace("’", "'"))
        for section in ("4.4.2.1", "15.3.2.1", "15.3.7", "4.2.2", "Revision 119", "9/16/2026", "7/17/2026"):
            self.assertIn(section, doc)

    def test_the_quotations_are_in_the_documents_as_saved(self):
        if not os.path.exists(os.path.join(SAVED, "nyiso_mst.txt")):
            self.skipTest("the documents are saved on the data machine only (runs/session100)")
        for name, quotes in self.QUOTES.items():
            with open(os.path.join(SAVED, name), encoding="utf-8") as f:
                text = " ".join(re.sub(r"<<page \d+>>", " ", f.read()).split())
            for q in quotes:
                self.assertIn(q, text, name)


class TheTableAsBuilt(unittest.TestCase):
    def test_spp_quantities(self):
        path = os.path.join(OUT, "spp_as_quantities.csv")
        if not os.path.exists(path):
            self.skipTest("spp_as_quantities is not on this machine")
        t = pd.read_csv(path, comment="#")
        self.assertLessEqual(len(t), 300_000)
        self.assertEqual(set(t["unit"]), {"MW"})
        self.assertEqual(sorted(t["entity"].unique()), ["spp:SPP", "spp:SWPW"])
        self.assertEqual(sorted(t["variable"].unique()), sorted(sq.PRODUCTS.values()))
        self.assertTrue((t["value"] >= 0).all())
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(t["ts_utc"].min(), "2024-09-01T05:00:00Z")
        s = t[(t["entity"] == "spp:SPP") & (t["variable"] == "quantity_mw_dam_regup")]
        local = pd.to_datetime(s["ts_utc"], utc=True).dt.tz_convert("America/Chicago")
        per_day = local.dt.strftime("%Y-%m-%d").value_counts()
        self.assertTrue(per_day.isin([23, 24, 25]).all())                                    # whole days only
        head = src("warehouse", "output", "spp_as_quantities.csv")[:6000]
        self.assertIn("ceiling 300,000", head)
        self.assertIn("with appropriate citation", head)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "connectors", "spp_as_quantities.py"), ("warehouse", "analysis", "battery_fleet_limited_review.py"),
                      ("docs", "methods", "reserve_quantities_nyiso_spp.md"), ("tests", "test_session100.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
