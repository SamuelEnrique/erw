"""Session 120, the page: the real-time side, one section of /cost-of-power/battery/awards.

Energy Research Warehouse (ERW). No request leaves the machine. The section reads ercot_storage_rt_monthly and
ercot_storage_node_basis beside the model's rows of battery_stack_monthly. These tests hold:

- the page is still in review, the method page too, and no live page knows of the section or its tables;
- the section comes last, and says what it leaves out before it shows a number;
- the words: real-time dollars are said to be at the hub average's price wherever they stand, the real-time ancillary
  quantities are said not to be valued, the week of node prices is said to be one week and applied to nothing, and
  the figures are never called what a battery earned or made;
- no figure is written into the section: each is computed by site/lib/storagerealtime.ts (run in Node) from the rows; a
  partial month is never set beside the model or in the whole-month sums; a table that is not read gives no number;
- on the tables of this machine, when they are here, the library gives what the same arithmetic gives in Python.

The rows of the arithmetic tests are made for the tests (round numbers, never shown anywhere): they test the sums, not
the data. The tables' own tests are in tests/test_session120.py.

    python -m unittest tests.test_session120_page -v
"""

import csv
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = ("site", "app", "cost-of-power", "battery", "awards", "page.tsx")
SECTION = ("site", "app", "cost-of-power", "battery", "awards", "RealTime.tsx")
LIB = ("site", "lib", "storagerealtime.ts")
LIVE = ["site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/battery/BatteryForm.tsx", "site/app/cost-of-power/battery/Contract.tsx",
        "site/app/page.tsx", "site/app/storage/page.tsx", "site/app/network/page.tsx", "site/app/about/page.tsx", "site/app/cost-of-power/seller/page.tsx"]
SERVICES = ["regup", "regdn", "rrs", "ecrs", "nspin"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    # the script on standard input: a table's rows do not fit on a Windows command line
    r = subprocess.run([exe, "--input-type=module"], input=js, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, encoding="utf-8")
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def visible(text):
    """What a reader can see: the comments of a file are not the page."""
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def month(m, days, in_month, da, dev, mw=1000.0, extra=None):
    """A month of made rows: day-ahead USD per MW, the deviation at the hub price, and their total."""
    v = {"days_held": days, "days_in_month": in_month, "mw": mw, "resources": 300, "intervals": 1000, "intervals_priced": 990,
         "revenue_da_usd_per_mw": da, "revenue_rt_deviation_hub_usd_per_mw": dev, "revenue_market_hub_usd_per_mw": da + dev,
         "rt_discharge_mwh": 40000.0, "rt_charge_mwh": 50000.0, "da_sold_mwh": 10000.0, "da_bought_mwh": 5000.0,
         "da_node_minus_hub_sold": 3.5, "da_node_minus_hub_bought": -2.25}
    for s in SERVICES:
        v.update({f"as_rt_{s}_mwh": 700.0, f"as_da_{s}_mwh": 500.0, f"as_imbalance_{s}_mwh": 200.0})
    v.update(extra or {})
    return [{"variable": k, "ts_utc": f"{m}-01T00:00:00Z", "value": x} for k, x in v.items() if x is not None]


def model(m, total, days, in_month):
    return [{"variable": "dayahead_2h_" + k, "ts_utc": f"{m}-01T00:00:00Z", "value": x}
            for k, x in (("revenue_total_usd_per_mw", total), ("days_held", days), ("days_in_month", in_month))]


def run(rows, mod, basis=None):
    return node(f"""
import {{ rtMonthsOf, rtTotal, rtEnergy, rtAncillary, basisOf }} from "./lib/storagerealtime.ts";
const ms = rtMonthsOf({json.dumps(rows)}, {json.dumps(mod)});
console.log(JSON.stringify({{ ms, total: rtTotal(ms), energy: rtEnergy(ms), anc: rtAncillary(ms), basis: basisOf({json.dumps(basis or [])}) }}));
""")


class Release(unittest.TestCase):
    def test_the_page_and_its_method_are_in_review_and_no_live_page_knows_of_them(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/cost-of-power/battery/awards": "review"', rel)
        self.assertNotIn("ercot_storage_realtime", rel)                       # a method page is in review unless it is named live
        for f in LIVE:
            if not os.path.exists(os.path.join(ROOT, *f.split("/"))):
                continue
            text = src(*f.split("/"))
            for word in ("storagerealtime", "ercot_storage_rt_monthly", "ercot_storage_node_basis", "RealTime", "battery/awards"):
                self.assertNotIn(word, text, f"{f} names {word}")
        self.assertIn('"/data/methods/ercot_storage_realtime"', src("site", "scripts", "check-routes.mjs"))

    def test_the_section_is_the_last_and_the_earlier_ones_stand(self):
        page = src(*PAGE)
        self.assertLess(page.index("<OffersSection"), page.index("<RealTimeSection"))
        self.assertLess(page.index('data-awards-not="1"'), page.index("<RealTimeSection"))
        for word in ('title="By month"', 'title="By year"', 'title="Why the two differ"', "data-awards-summary", "<MonthBars ms={ms} />"):
            self.assertIn(word, page)

    def test_a_table_that_is_not_read_does_not_take_the_page_down(self):
        page, sec = src(*PAGE), src(*SECTION)
        self.assertIn("attempt(realTimeRows)", page)
        self.assertIn("attempt(basisRows)", page)
        for state in ('data-rt-state="unread"', 'data-rt-state="not-loaded"', "so no number is shown in this section", "so no number is shown here"):
            self.assertIn(state, sec)


class Words(unittest.TestCase):
    def setUp(self):
        self.sec = visible(src(*SECTION))

    def test_what_it_leaves_out_comes_first(self):
        s = self.sec
        self.assertIn("What this still leaves out.", s)
        # in what the section returns, the list of what is left out stands above the numbers
        tail = s[s.index("<ToolSection title={TITLE}"):]
        self.assertLess(tail.index("{leftOut}"), tail.index("{body}"))
        block = s[s.index('data-rt-not="1"'):s.index("let body")]
        for word in ("Contracts.", "own node", "Real-time ancillary service money.", "Charges and credits", "The meter."):
            self.assertIn(word, block)

    def test_a_real_time_dollar_is_always_said_to_be_at_the_hub_price(self):
        s = self.sec
        self.assertGreaterEqual(s.count("at the hub average&apos;s price"), 4)
        head = s[s.index('caption="Day-ahead awards and real-time deviations by month"'):s.index("rows={[...ms].reverse()")]
        self.assertEqual(head.count("hub average&apos;s price"), 2)           # the two columns that rest on it
        self.assertIn("a stand-in", s)

    def test_nothing_is_called_what_a_battery_earned(self):
        s = self.sec
        self.assertIn("It is still not what any battery earned.", s)
        for claim in ("the fleet earned", "batteries earned", "the fleet made USD", "what the fleet made", "what batteries made", "actual revenue", "true revenue"):
            self.assertNotIn(claim, s)

    def test_the_ancillary_quantities_are_said_not_to_be_valued_and_the_week_is_one_week(self):
        s = self.sec
        self.assertIn("held, and not valued", s)
        self.assertIn("with no dollar figure put on it", s)
        self.assertIn("One week is one week.", s)
        self.assertIn("it is not applied to any figure above", s)
        self.assertIn("nothing stands in for them", s)                         # the weeks before the months that fit the ceiling

    def test_no_figure_is_written_into_the_section(self):
        s = self.sec
        self.assertIsNone(re.search(r">\s*-?\d+\.\d+\s*<", s))
        self.assertIsNone(re.search(r"USD \d", s), "a dollar figure in the words")
        self.assertEqual(re.findall(r"\b\d{2,}(?:\.\d+)?%", s), [])


class Arithmetic(unittest.TestCase):
    def test_whole_months_only_stand_beside_the_model(self):
        rows = month("2026-06", 30, 30, 2000.0, 500.0) + month("2026-07", 31, 31, 3000.0, -250.0) + month("2026-08", 5, 31, 400.0, 80.0)
        mod = model("2026-06", 2500.0, 30, 30) + model("2026-07", 3500.0, 31, 31) + model("2026-08", 3600.0, 31, 31)
        r = run(rows, mod)
        self.assertEqual([m["m"] for m in r["ms"]], ["2026-06", "2026-07", "2026-08"])
        self.assertEqual([m["complete"] for m in r["ms"]], [True, True, False])
        t = r["total"]
        self.assertEqual(t["months"], ["2026-06", "2026-07"])
        self.assertEqual((t["dayAhead"], t["deviationHub"], t["marketHub"], t["model"]), (5000.0, 250.0, 5250.0, 6000.0))

    def test_a_model_month_that_is_partial_gives_no_model_figure(self):
        rows = month("2026-06", 30, 30, 2000.0, 500.0) + month("2026-07", 31, 31, 3000.0, -250.0)
        r = run(rows, model("2026-06", 2500.0, 30, 30) + model("2026-07", 3500.0, 20, 31))
        self.assertIsNone(r["total"]["model"])
        self.assertEqual(r["total"]["marketHub"], 5250.0)
        self.assertIsNone(run(rows, [])["total"]["model"])

    def test_no_whole_month_no_total(self):
        self.assertIsNone(run(month("2026-08", 5, 31, 400.0, 80.0), model("2026-08", 3600.0, 31, 31))["total"])
        self.assertEqual(run([], []), {"ms": [], "total": None, "energy": None, "anc": [], "basis": None})

    def test_a_month_without_one_of_its_three_sums_is_left_out_not_shown_as_zero(self):
        rows = month("2026-06", 30, 30, 2000.0, 500.0) + [x for x in month("2026-07", 31, 31, 3000.0, -250.0) if x["variable"] != "revenue_rt_deviation_hub_usd_per_mw"]
        self.assertEqual([m["m"] for m in run(rows, [])["ms"]], ["2026-06"])

    def test_the_energy_sums(self):
        rows = month("2026-06", 30, 30, 2000.0, 500.0) + month("2026-07", 31, 31, 3000.0, -250.0, mw=2000.0)
        e = run(rows, [])["energy"]
        self.assertEqual((e["days"], e["discharged"], e["sold"], e["charged"], e["bought"]), (61, 80000.0, 20000.0, 100000.0, 10000.0))
        self.assertAlmostEqual(e["soldOfDischarged"], 0.25)
        self.assertAlmostEqual(e["outOverIn"], 0.8)
        self.assertAlmostEqual(e["dischargedPerMwDay"], (40000 / 1000 + 40000 / 2000) / 61)   # each month's MWh over its own MW
        self.assertAlmostEqual(e["pricedShare"], 0.99)
        missing = month("2026-06", 30, 30, 2000.0, 500.0, extra={"rt_charge_mwh": None})
        self.assertIsNone(run(missing, [])["energy"])                           # a sum with a month missing is not a sum

    def test_the_ancillary_quantities_add_up_and_a_service_a_month_lacks_is_not_listed(self):
        rows = month("2026-06", 30, 30, 2000.0, 500.0) + month("2026-07", 31, 31, 3000.0, -250.0, extra={"as_rt_ecrs_mwh": None})
        a = {x["key"]: x for x in run(rows, [])["anc"]}
        self.assertEqual(sorted(a), ["nspin", "regdn", "regup", "rrs"])
        self.assertEqual((a["regup"]["realTime"], a["regup"]["dayAhead"], a["regup"]["imbalance"]), (1400.0, 1000.0, 400.0))

    def test_the_week_of_node_prices(self):
        b = [{"variable": k, "ts_utc": "2026-09-28T00:00:00Z", "value": v} for k, v in
             (("nodes", 200), ("nodes_with_spread", 190), ("whole_days", 7), ("spread_hub", 30.5), ("spread_node_median", 41.25), ("spread_node_p10", 28.0),
              ("spread_node_p90", 77.0), ("nodes_spread_above_hub", 150), ("mean_abs_difference_median", 4.75))]
        r = run([], [], b)["basis"]
        self.assertEqual((r["from"], r["nodes"], r["nodesWithSpread"], r["wholeDays"], r["spreadHub"], r["spreadMedian"], r["aboveHub"], r["meanAbsDifference"]),
                         ("2026-09-28", 200, 190, 7, 30.5, 41.25, 150, 4.75))
        self.assertIsNone(run([], [], [x for x in b if x["variable"] != "nodes"])["basis"])


class OnThisMachine(unittest.TestCase):
    """The library on the tables of this machine, when they are here, against the same sums in Python."""

    def rows(self, table, entity):
        path = os.path.join(ROOT, "warehouse", "output", table + ".csv")
        if not os.path.exists(path):
            raise unittest.SkipTest(f"{table} is not on this machine")
        with open(path, encoding="utf-8", newline="") as f:
            lines = [ln for ln in f if not ln.startswith("#")]
        return [{"variable": r["variable"], "ts_utc": r["ts_utc"], "value": r["value"]} for r in csv.DictReader(lines) if r["entity"] == entity]

    def test_the_library_reads_the_table_as_python_does(self):
        rows = self.rows("ercot_storage_rt_monthly", "ercot:esr_fleet")
        mod = [r for r in self.rows("battery_stack_monthly", "ercot:HB_HUBAVG") if r["variable"].startswith("dayahead_2h_")]
        r = run(rows, mod)
        by = {}
        for x in rows:
            by.setdefault(x["ts_utc"][:7], {})[x["variable"]] = float(x["value"])
        self.assertEqual([m["m"] for m in r["ms"]], sorted(by))
        full = [m for m in sorted(by) if by[m]["days_held"] == by[m]["days_in_month"]]
        self.assertTrue(full, "the table holds no whole month")
        t = r["total"]
        self.assertEqual(t["months"], full)
        self.assertAlmostEqual(t["marketHub"], sum(by[m]["revenue_market_hub_usd_per_mw"] for m in full), places=6)
        self.assertAlmostEqual(t["dayAhead"] + t["deviationHub"], t["marketHub"], delta=0.001 * len(full))   # each month's figures are rounded to four places
        for m in r["ms"]:
            g = by[m["m"]]
            self.assertAlmostEqual(m["marketHub"], g["revenue_da_usd_per_mw"] + g["revenue_rt_deviation_hub_usd_per_mw"], delta=0.001)
            self.assertEqual(len(m["ancillary"]), 5)
        self.assertAlmostEqual(r["energy"]["discharged"], sum(g["rt_discharge_mwh"] for g in by.values()), places=3)

    def test_the_week_of_node_prices_is_read(self):
        b = run([], [], self.rows("ercot_storage_node_basis", "ercot:esr_nodes"))["basis"]
        self.assertIsNotNone(b)
        self.assertGreater(b["nodes"], 50)
        self.assertLessEqual(b["nodesWithSpread"], b["nodes"])
        self.assertLessEqual(b["aboveHub"], b["nodesWithSpread"])
        self.assertLessEqual(b["spreadP10"], b["spreadMedian"])
        self.assertLessEqual(b["spreadMedian"], b["spreadP90"])


if __name__ == "__main__":
    unittest.main()
