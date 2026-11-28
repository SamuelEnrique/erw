"""Session 9000, chain 601 (part C): congestion, the connector's parsing, the page file and the page /congestion."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheConnector(unittest.TestCase):
    def test_spp_constraints_keep_the_operators_columns_and_sign(self):
        import pandas as pd
        import grid_congestion as gc
        text = ("Interval,GMTIntervalEnd,Constraint Name,Constraint Type,NERCID,State,Shadow Price,Monitored Facility,"
                "Contingent Facility,Contingency Name\n"
                "11/18/2026 01:00:00,11/18/2026 07:00:00,TP1338_33520,FG,33520,BINDING,-172.1,LN STILW1 - SPVALLY2,X,33380\n")
        rows = gc.spp_constraints(pd.Timestamp("2026-11-18"), text, {"url": "u", "retrieved_at": "t"})
        self.assertEqual(rows["entity"].tolist(), ["spp:TP1338_33520|33380"])
        self.assertEqual(rows["ts_utc"].tolist(), ["2026-11-18T06:00:00Z"])
        self.assertEqual(rows["value"].tolist(), [-172.1])
        self.assertEqual(rows["x_monitored"].tolist(), ["LN STILW1 - SPVALLY2"])
        self.assertEqual(list(rows.columns), gc.COLS_CONS)

    def test_caiso_contingency_is_part_of_the_key(self):
        import pandas as pd
        import grid_congestion as gc
        x = pd.DataFrame({"INTERVALSTARTTIME_GMT": ["2019-01-15T16:00:00-00:00"] * 3,
                          "NOMOGRAM_ID_XML": ["24086_LUGO_BR"] * 3,
                          "CONSTRAINT_CAUSE": ["SC1 PVERDE", "SD1 N.GILA", "SD1 N.GILA"],
                          "PRC": ["1.30669", "5.47316", "5.47316"], "GROUP": ["3", "4", "5"]})
        rows = gc.caiso_constraints(x, {"url": "u", "retrieved_at": "t"})
        self.assertEqual(sorted(rows["entity"]), ["caiso:24086_LUGO_BR|SC1 PVERDE", "caiso:24086_LUGO_BR|SD1 N.GILA"])
        self.assertFalse(rows.duplicated(gc.KEY).any())

    def test_a_short_price_day_is_left_out(self):
        import pandas as pd
        import grid_congestion as gc
        hours = gc.day_hours("2026-11-18", gc.SPP_TZ)
        rows = pd.DataFrame({"place": "SPPNORTH_HUB", "variable": "lmp_dam", "ts": hours[:23],
                             "value": 1.0, "day": pd.Timestamp("2026-11-18")})
        gaps = []
        kept = gc.complete_prices(rows, gc.SPP_TZ, print, gaps)
        self.assertEqual(len(kept), 0)
        self.assertEqual(len(gaps), 1)

    def test_no_held_or_paused_operator_is_asked(self):
        s = src("warehouse", "connectors", "grid_congestion.py")
        for host in ("ercot.com", "pjm.com", "nyiso.com", "iso-ne.com", "misoenergy.org"):
            self.assertNotIn(host, s)


@unittest.skipUnless(os.path.exists(FILE), "the congestion file is not on this machine")
class TheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FILE, encoding="utf-8") as f:
            cls.f = json.load(f)

    def test_held_operators_are_named_not_drawn(self):
        st = {o["id"]: o["status"] for o in self.f["operators"]}
        self.assertEqual(st["pjm"], "license needed")
        self.assertEqual(st["nyiso"], "license needed")
        self.assertEqual(st["isone"], "license needed")
        self.assertEqual(st["miso"], "paused")
        self.assertEqual(st["ercot"], "source needed")
        for op in ("pjm", "nyiso", "isone", "miso", "ercot"):
            self.assertNotIn(op, self.f["constraints"])
            self.assertNotIn(op, self.f["places"])

    def test_top_lists_name_constraints_in_the_file(self):
        for op, o in self.f["constraints"].items():
            for y, t in o["top"].items():
                for k in t["by_hours"] + t["by_cost"]:
                    self.assertIn(k, o["constraints"], f"{op} {y} {k}")

    def test_a_constraints_months_sum_to_its_hours(self):
        for op, o in self.f["constraints"].items():
            for k, c in o["constraints"].items():
                self.assertEqual(sum(m[1] for m in c["monthly"]), c["hours"], k)
                self.assertEqual(sum(map(sum, c["hod_month"])), c["hours"], k)
                self.assertEqual(sum(v["hours"] for v in c["by_year"].values()), c["hours"], k)

    def test_shares_follow_the_rule(self):
        for op, ps in self.f["places"].items():
            for p in ps:
                for m in p["monthly"]:
                    lmp, cong, share = m[2], m[4], m[7]
                    if lmp is None or lmp <= 0:
                        self.assertIsNone(share)
                    else:
                        self.assertAlmostEqual(share, 100 * cong / lmp, delta=0.2)


class ThePage(unittest.TestCase):
    def test_page_reads_its_file_and_is_not_indexed(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn("@/data/conditions/congestion.json", s)
        self.assertIn("index: false", s)
        self.assertIn("license needed", src("warehouse", "derived", "congestion_page.py"))

    def test_page_is_in_no_menu(self):
        self.assertIn('"/congestion": "review"', src("site", "lib", "release.ts"))   # session 11405 (decision 4, readied): in the menu, its own line, in review

    def test_page_is_in_the_route_check(self):
        self.assertIn('"/congestion"', src("site", "scripts", "check-routes.mjs"))


if __name__ == "__main__":
    unittest.main()
