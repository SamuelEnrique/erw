"""Session 1027 (chain 071): ERCOT's planning reserve margin in the All grids tab's headroom column, from
ercot_cdr_reserve_margins (ERCOT's Capacity, Demand and Reserves report, public): the first summer after the tab file's
build day at the peak load hour, keyed allgrids|reservemargin|<row>; the other grids drawn "reserve margin not held". The
builder's function is read on a three-season file written here (its shape, not ERCOT's figures); the tab's file holds the
figures the builder wrote from the table. No request, no model call."""
import importlib.util
import json
import os
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


HEAD = "entity,variable,ts_utc,value,unit,freq,geo,market,node,source,source_url,retrieved_at,vintage,x_hour,x_report\n"


def row(season, hour, ts, var, v, label):
    h = 17 if hour == "peak_load" else 21
    return (f"ercot_cdr:{season}:{hour},{var},{ts},{v},MW,P3M,US-TX,ercot,\"{label}, {hour.replace('_', ' ')} hour {h}\",ercot:cdr,"
            f"https://www.ercot.com/gridinfo/resource,2026-10-23T01:40:30Z,2025-12-19T00:00:00Z,{h},CDR.xlsx\n")


class Builder(unittest.TestCase):
    def test_the_first_summer_after_the_day_and_the_first_season_below_zero(self):
        m = load("siting_page_1027", "warehouse", "derived", "siting_page.py")
        lines = [HEAD]
        for season, ts, label, pct in (("summer", "2026-06-01T00:00:00Z", "Summer 2026", 20.0), ("winter", "2026-12-01T00:00:00Z", "Winter 2026/2027", -3.0),
                                        ("summer", "2027-06-01T00:00:00Z", "Summer 2027", 11.0)):
            for hour in ("peak_load", "peak_net_load"):
                lines += [row(season, hour, ts, "reserve_margin", pct - (1 if hour == "peak_net_load" else 0), label),
                          row(season, hour, ts, "total_capacity", 100.0, label), row(season, hour, ts, "firm_peak_load", 90.0, label)]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "ercot_cdr_reserve_margins.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# a test file\n" + "".join(lines))
            r = m.reserve_margins(p, today="2026-10-23")
        e = r["grids"]["ercot"]
        self.assertEqual(list(r["grids"]), ["ercot"])
        self.assertEqual(e["start"], "2027-06-01")
        self.assertEqual((e["peak"]["label"], e["peak"]["x_hour"], e["peak"]["pct"]), ("Summer 2027", 17, 11.0))
        self.assertEqual((e["net"]["x_hour"], e["net"]["pct"]), (21, 10.0))
        self.assertEqual((e["first_below_zero"]["label"], e["first_below_zero"]["pct"]), ("Winter 2026/2027", -3.0))
        self.assertEqual((r["table"], r["as_of"], r["report"]), ("ercot_cdr_reserve_margins", "2026-10-23", "CDR.xlsx"))


class TheFile(unittest.TestCase):
    def test_the_tab_file_holds_ercot_s_margin(self):
        h = json.loads(src("site", "data", "siting", "headroom.json"))
        r = h["reserve"]
        self.assertEqual(r["table"], "ercot_cdr_reserve_margins")
        e = r["grids"]["ercot"]
        self.assertGreater(e["start"], r["as_of"])
        self.assertEqual(e["start"][5:], "06-01")                      # a summer
        self.assertTrue(e["peak"]["label"].startswith("Summer"))
        self.assertTrue(-50 < e["peak"]["pct"] < 100)
        cap, firm = e["peak"]["capacity_mw"], e["peak"]["firm_peak_mw"]
        self.assertAlmostEqual(100 * (cap - firm) / firm, e["peak"]["pct"], delta=0.01)   # ERCOT's own definition
        if e["first_below_zero"]:
            self.assertLess(e["first_below_zero"]["pct"], 0)


class ThePage(unittest.TestCase):
    def test_the_cell_the_key_and_the_column(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        s = src("site", "lib", "siting.ts")
        self.assertIn('data-headroom-reserve="1"', v)
        self.assertIn("allgrids|reservemargin|${r.id}", v)
        self.assertIn('words="reserve margin not held"', v)
        self.assertIn("raw={m.peak.pct}>{two(m.peak.pct)}</Num>", v)  # two decimals, check-values' rule (the landing's fix)
        self.assertIn('p[1] === "reservemargin"', s)
        self.assertIn('"ercot_cdr_reserve_margins"]', s)                # the headroom column's tables
        self.assertNotIn("fetch(", v[v.index("function HeadroomTd"):v.index("function CarbonTd")])


class TheReplication(unittest.TestCase):
    def test_the_first_summer_after_the_file_s_day(self):
        m = load("repl_siting_1027", "warehouse", "replication", "siting.py")
        as_of = json.loads(src("site", "data", "siting", "headroom.json"))["reserve"]["as_of"]
        y = int(as_of[:4])
        rows = [{"ts_utc": f"{y - 1}-06-01T00:00:00Z", "value": "1"}, {"ts_utc": f"{y + 2}-06-01T00:00:00Z", "value": "3"},
                {"ts_utc": f"{y + 1}-06-01T00:00:00Z", "value": "2"}]
        got = m.reserve_figures(ROOT, rows)                               # the year before is past; the next is first
        self.assertEqual(got, {"allgrids|reservemargin|ercot:HB_HUBAVG": 2.0})
        self.assertEqual(m.reserve_figures(ROOT, []), {})


if __name__ == "__main__":
    unittest.main()
