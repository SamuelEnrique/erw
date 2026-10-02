"""Session 68: who supplies a grid (warehouse/derived/ba_supply.py), the two EIA-930 pulls, the network's stories.

Energy Research Warehouse (ERW). No request leaves the machine. The builders' rules are tested on small made-up frames;
the known bad pair-day (SWPP-MISO, 2026-07-21) is also tested on the real table where this machine holds it.

    python -m unittest tests.test_session68 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))

import ba_supply as bs  # noqa: E402
import eia930_daily_total_interchange as ti  # noqa: E402
import eia930_event_hourly as ev  # noqa: E402
import network_stories as ns  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


def pairs(rows):
    """Pair-days from (ba, to, day, v) tuples, v positive when ba exports (EIA's sign)."""
    it = pd.DataFrame(rows, columns=["ba", "to", "day", "v"])
    it["entity"] = "eia930:" + it["ba"] + "-" + it["to"]
    it["bad"] = bs.screen(it)
    return it


def table(rows):
    return pd.DataFrame(rows).set_index(["entity", "variable"])["value"]


def days(month, n):
    return [f"{month}-{d:02d}" for d in range(1, n + 1)]


class Supply(unittest.TestCase):
    def setUp(self):
        # AAA imports from BBB (BBB reports the same flow as its export) and exports to CCC, every day of June 2026
        rows = []
        for d in days("2026-06", 30):
            rows += [("AAA", "BBB", d, -100.0), ("BBB", "AAA", d, 100.0), ("AAA", "CCC", d, 40.0), ("CCC", "AAA", d, -40.0)]
        self.it = pairs(rows)
        self.ti = pd.DataFrame({"ba": "AAA", "day": days("2026-06", 30), "v": -60.0})
        self.bal = {"AAA": pd.DataFrame({"d": 1000.0, "ng": 940.0}, index=days("2026-06", 30))}

    def test_pair_shares_sum_to_the_pair_sum_total(self):
        t = table(bs.build(self.it, self.ti, self.bal, "2026-06-30"))
        a = t[("eia930:AAA-BBB", "net_import_share_pct")] + t[("eia930:AAA-CCC", "net_import_share_pct")]
        self.assertAlmostEqual(a, t[("eia930:AAA", "net_import_pairs_share_pct")], places=6)
        self.assertAlmostEqual(t[("eia930:AAA-BBB", "net_import_mwh")] + t[("eia930:AAA-CCC", "net_import_mwh")], t[("eia930:AAA", "net_import_pairs_mwh")], places=6)
        self.assertEqual(t[("eia930:AAA-BBB", "net_import_mwh")], 3000.0)   # positive: the neighbour supplied AAA
        self.assertEqual(t[("eia930:AAA-CCC", "net_import_mwh")], -1200.0)  # negative: AAA supplied CCC
        self.assertAlmostEqual(t[("eia930:AAA", "net_import_pairs_share_pct")], 6.0, places=6)
        self.assertAlmostEqual(t[("eia930:AAA", "net_import_total_interchange_share_pct")], 6.0, places=6)
        self.assertAlmostEqual(t[("eia930:AAA", "net_import_balance_share_pct")], 6.0, places=6)

    def test_a_pair_reported_by_both_sides_agrees_in_sign(self):
        t = table(bs.build(self.it, self.ti, self.bal, "2026-06-30"))
        for n in ("BBB", "CCC"):
            mine, theirs = t[(f"eia930:AAA-{n}", "net_import_mwh")], t[(f"eia930:AAA-{n}", "neighbor_report_mwh")]
            self.assertEqual(mine > 0, theirs > 0)
            self.assertEqual(mine, theirs)
            self.assertEqual(t[(f"eia930:AAA-{n}", "neighbor_report_days")], 30)
        # and BBB's own rows read the same flow the other way round
        self.assertEqual(t[("eia930:BBB-AAA", "net_import_mwh")], -3000.0)

    def test_a_thin_month_is_marked_and_a_missing_month_is_counted(self):
        rows = [("AAA", "BBB", d, -100.0) for d in days("2026-05", 31)] + [("AAA", "BBB", d, -100.0) for d in days("2026-07", 8)]
        out = pd.DataFrame(bs.build(pairs(rows), self.ti.iloc[0:0], {}, "2026-07-31"))
        thin = out[(out["entity"] == "eia930:AAA") & (out["variable"] == "thin_month")].sort_values("ts_utc")["value"].tolist()
        self.assertEqual(thin, [0, 1, 1])  # May whole, June empty, July 8 days of 31
        june = out[(out["entity"] == "eia930:AAA") & (out["ts_utc"] == "2026-06-01T00:00:00Z")].set_index("variable")["value"]
        self.assertEqual(june["days_held"], 0)        # nothing reported in June: counted as left out, not skipped
        self.assertEqual(june["days_left_out"], 30)
        self.assertNotIn("net_import_pairs_mwh", june.index)  # no held day: no flow row, never a zero
        july = out[(out["entity"] == "eia930:AAA") & (out["ts_utc"] == "2026-07-01T00:00:00Z")].set_index("variable")["value"]
        self.assertEqual(july["days_held"], 8)
        self.assertEqual(july["thin_month"], 1)

    def test_a_day_missing_a_regular_neighbour_is_left_out(self):
        rows = []
        for d in days("2026-06", 30):
            rows.append(("AAA", "BBB", d, -100.0))
            if d != "2026-06-15":
                rows.append(("AAA", "CCC", d, 40.0))
        t = table(bs.build(pairs(rows), self.ti.iloc[0:0], {}, "2026-06-30"))
        self.assertEqual(t[("eia930:AAA", "days_held")], 29)
        self.assertEqual(t[("eia930:AAA-BBB", "net_import_mwh")], 2900.0)

    def test_the_screening_rule_on_made_up_data(self):
        rows = [("AAA", "BBB", d, -100.0 - i) for i, d in enumerate(days("2026-06", 30))]
        rows[20] = ("AAA", "BBB", "2026-06-21", -2_159_056.0)
        it = pairs(rows)
        self.assertEqual(it.loc[it["bad"], "day"].tolist(), ["2026-06-21"])
        t = table(bs.build(it, self.ti.iloc[0:0], {}, "2026-06-30"))
        self.assertEqual(t[("eia930:AAA", "days_held")], 29)

    def test_the_known_bad_pair_day_is_screened(self):
        path = os.path.join(OUT, "eia930_daily_interchange.csv")
        if not os.path.exists(path):
            self.skipTest("eia930_daily_interchange is not on this machine")
        it = pd.read_csv(path, comment="#", usecols=["entity", "ts_utc", "value", "ba", "x_to_ba"], dtype=str)
        it = it[it["entity"].isin(["eia930:SWPP-MISO", "eia930:MISO-SWPP"])]
        it = pd.DataFrame({"entity": it["entity"], "day": it["ts_utc"].str[:10], "v": pd.to_numeric(it["value"])})
        bad = it[bs.screen(it)]
        self.assertIn("2026-07-21", set(bad.loc[bad["entity"] == "eia930:SWPP-MISO", "day"]))
        self.assertLess(len(bad), 0.01 * len(it))


class Pulls(unittest.TestCase):
    def test_ceilings(self):
        self.assertEqual(ti.CEILING, 300_000)
        self.assertEqual(ev.CEILING, 400_000)

    def test_event_windows_are_the_stories(self):
        w = {e["event"]: e for e in ev.EVENTS}
        self.assertEqual((w["uri_2021"]["start"], w["uri_2021"]["end"]), ("2021-02-07", "2021-02-24"))
        self.assertEqual((w["east_heat_2025"]["start"], w["east_heat_2025"]["end"]), ("2025-06-20", "2025-06-28"))
        a, b, p0, p1 = ev.window(w["uri_2021"])
        self.assertEqual(int((b - a) / pd.Timedelta(hours=1)), 432)
        self.assertEqual(p0, "2021-02-07T07")  # EIA's period is the hour's end: the first hour starts 06:00Z (midnight Central)

    def test_event_rows_are_never_filled(self):
        e = ev.EVENTS[1]
        a, b, _, _ = ev.window(e)
        x = pd.DataFrame({"period": ["2025-06-20T05", "2025-06-20T06"], "fromba": ["PJM", "PJM"], "toba": ["NYIS", "NYIS"],
                          "value": ["100", ""], "_url": "u", "_retrieved": "r"})
        d = pd.DataFrame({"period": ["2025-06-20T05"], "respondent": ["PJM"], "value": ["90000"], "_url": "u", "_retrieved": "r"})
        rows, n = ev.to_rows(x, d, e, a, b)
        self.assertEqual(n["interchange_no_value"], 1)
        self.assertEqual(len(rows[rows["variable"] == "interchange_mw"]), 1)
        self.assertEqual(rows["event"].unique().tolist(), ["east_heat_2025"])


class Stories(unittest.TestCase):
    def test_a_pair_is_counted_once_by_the_network_rule(self):
        base = {"nodes": [{"id": "AAA"}, {"id": "BBB"}]}
        hours = pd.date_range("2025-06-20T04:00:00Z", periods=216, freq="h").strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = [dict(entity="eia930:BBB-AAA", variable="interchange_mw", ts_utc=hours[0], value="50", event="east_heat_2025"),
                dict(entity="eia930:AAA-BBB", variable="interchange_mw", ts_utc=hours[1], value="-70", event="east_heat_2025"),
                dict(entity="eia930:BBB-AAA", variable="interchange_mw", ts_utc=hours[1], value="65", event="east_heat_2025")]
        x = pd.DataFrame(rows)
        empty = pd.DataFrame(columns=["ba", "day", "value", "ts_utc"])
        s = ns.build("east_heat_2025", ns.EVENTS["east_heat_2025"], x, base, empty, empty, {})
        self.assertEqual(len(s["links"]), 1)
        link = s["links"][0]
        self.assertEqual((link["a"], link["b"]), ("AAA", "BBB"))
        self.assertEqual(link["mw"][0], -50.0)   # only BBB reported: its report, the sign flipped
        self.assertEqual(link["mw"][1], -70.0)   # AAA reported: AAA's report wins
        self.assertIsNone(link["mw"][2])         # neither reported: blank, never filled
        self.assertEqual(s["missing"]["link_hours"], 214)
        self.assertEqual(s["missing"]["link_hours_from_other_side"], 1)


if __name__ == "__main__":
    unittest.main()
