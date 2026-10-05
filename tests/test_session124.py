"""Session 124: the network, version 3, to launch-ready (/network/v3, in review; the live page /network is as it was).

Energy Research Warehouse (ERW). No request leaves the machine. What these tests hold:

- the newest complete hour: every reporting pair holds it, a pair that stopped is named and not waited for;
- trace the power against two cases worked by hand from EIA's daily interchange with pandas, apart from the site's
  code: California over 2021, and Texas during Winter Storm Uri (where they are on this machine);
- the replay's builder keeps a screened pair-day that the record itself confirms, and only those;
- the replay's files say how many pairs each day holds, and the days that hold few;
- every change to the shared component is behind its v3 prop: the live page passes none, and opens as it did;
- MISO's price is not shown on the new page, and the page says why.

    python -m unittest tests.test_session124 -v
"""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("ERW_LOCK_EXEMPT", "1")
for p in ("warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import network_daily as nd  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
PUB = os.path.join(ROOT, "site", "public", "network")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module"], input=js, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180, encoding="utf-8")
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheNewestCompleteHour(unittest.TestCase):
    def run_it(self, links, n=72, quiet=48):
        hours = [f"2026-10-0{1 + h // 24}T{h % 24:02d}:00:00Z" for h in range(n)]
        return node(f"""
import {{ completeHour }} from "./lib/networkV3.ts";
console.log(JSON.stringify(completeHour({json.dumps(hours)}, {json.dumps(links)}, {quiet})));
"""), hours

    def test_it_is_the_newest_hour_every_reporting_pair_holds(self):
        full = [1.0] * 72
        late = [1.0] * 70 + [None, None]              # this pair's last two hours have not arrived
        r, hours = self.run_it([{"a": "A", "b": "B", "mw": full}, {"a": "A", "b": "C", "mw": late}])
        self.assertEqual((r["index"], r["hour"]), (69, hours[69]))
        self.assertEqual((r["pairs"], r["reporting"], r["silent"]), (2, 2, []))
        self.assertEqual((r["newest"], r["newestPairs"]), (hours[71], 1))

    def test_a_pair_that_stopped_is_named_and_not_waited_for(self):
        full = [1.0] * 72
        stopped = [1.0] * 10 + [None] * 62            # nothing for 62 hours
        never = [None] * 72
        r, hours = self.run_it([{"a": "A", "b": "B", "mw": full}, {"a": "S", "b": "T", "mw": stopped}, {"a": "N", "b": "O", "mw": never}])
        self.assertEqual((r["index"], r["reporting"], r["pairs"]), (71, 1, 3))
        self.assertEqual(r["silent"], [{"a": "N", "b": "O", "last": None}, {"a": "S", "b": "T", "last": hours[9]}])

    def test_a_hole_in_the_middle_does_not_hide_a_later_complete_hour(self):
        a = [1.0] * 72
        b = [1.0] * 50 + [None] * 5 + [1.0] * 17
        r, _ = self.run_it([{"a": "A", "b": "B", "mw": a}, {"a": "A", "b": "C", "mw": b}])
        self.assertEqual(r["index"], 71)

    def test_no_reporting_pair_no_hour(self):
        r, _ = self.run_it([{"a": "A", "b": "B", "mw": [None] * 72}])
        self.assertEqual((r["index"], r["hour"], r["reporting"]), (-1, None, 0))

    def test_on_the_committed_week_it_is_an_hour_every_reporting_pair_holds(self):
        r = node("""
import fs from "node:fs";
import { completeHour } from "./lib/networkV3.ts";
const s = JSON.parse(fs.readFileSync("data/grid_network.json", "utf8"));
const c = completeHour(s.hours, s.links);
const quiet = new Set(c.silent.map((x) => `${x.a}-${x.b}`));
const rep = s.links.filter((l) => !quiet.has(`${l.a}-${l.b}`));
console.log(JSON.stringify({ c, at: c.index >= 0 ? rep.every((l) => l.mw[c.index] !== null) : null, later: c.index >= 0 ? s.hours.slice(c.index + 1).filter((_, k) => rep.every((l) => l.mw[c.index + 1 + k] !== null)).length : null,
  n: s.links.length, rep: rep.length }));
""")
        self.assertTrue(r["at"])
        self.assertEqual(r["later"], 0)                                # no later hour is complete
        self.assertEqual((r["c"]["pairs"], r["c"]["reporting"]), (r["n"], r["rep"]))


class TraceThePower(unittest.TestCase):
    LINKS = [{"a": "CEN", "b": "ERCO", "mw": [100.0, 100.0, None, 100.0]}, {"a": "CEN", "b": "CISO", "mw": [-50.0, -50.0, -50.0, -50.0]},
             {"a": "ERCO", "b": "SWPP", "mw": [-300.0, -300.0, None, -300.0]}, {"a": "MISO", "b": "SWPP", "mw": [500.0, 500.0, 500.0, 500.0]}]

    def run_it(self, a=0, b=4, grid="ERCO"):
        return node(f"""
import {{ trace, monthSpan, ISLANDS, PAUSED_PRICE }} from "./lib/networkV3.ts";
const days = ["2021-01-30", "2021-01-31", "2021-02-01", "2021-02-02", "2021-02-28", "2021-03-01"].map((d) => d + "T12:00:00Z");
console.log(JSON.stringify({{ t: trace({json.dumps(self.LINKS)}, {a}, {b}, "{grid}", () => 24), spans: [monthSpan(days, 0), monthSpan(days, 3), monthSpan(days, 5)], islands: Object.keys(ISLANDS), paused: Object.keys(PAUSED_PRICE) }}));
""")

    def test_nothing_is_traced_through_mexico(self):
        r = self.run_it()
        rows = {x["id"]: x for x in r["t"]["rows"]}
        self.assertEqual(sorted(rows), ["CEN", "SWPP"])
        self.assertEqual(rows["CEN"]["via"], [])                        # before session 124: "CEN supplied by CISO, 100 percent"
        self.assertIn("separate systems", rows["CEN"]["island"])
        self.assertEqual([x["id"] for x in rows["SWPP"]["via"]], ["MISO"])
        self.assertEqual(r["islands"], ["CEN"])

    def test_it_says_how_many_frames_hold_a_flow_for_the_grid(self):
        t = self.run_it()["t"]
        self.assertEqual((t["frames"], t["held"]), (4, 3))              # the third frame holds none of Texas's ties
        self.assertEqual(t["inMwh"], 3 * 24 * 400.0)
        self.assertAlmostEqual(next(x for x in t["rows"] if x["id"] == "SWPP")["share"], 75.0)

    def test_the_month_of_a_day(self):
        r = self.run_it()
        self.assertEqual(r["spans"], [[0, 2], [2, 5], [5, 6]])
        self.assertEqual(r["paused"], ["MISO"])


@unittest.skipUnless(os.path.exists(os.path.join(OUT, "eia930_daily_interchange.csv")), "eia930_daily_interchange is not on this machine")
class WorkedByHand(unittest.TestCase):
    """Two cases from EIA's daily interchange with pandas alone, set against the site's trace on the replay's file."""

    @classmethod
    def setUpClass(cls):
        import ba_supply
        import iso_prices as ip
        p = os.path.join(OUT, "eia930_daily_interchange.csv")
        it = pd.read_csv(p, skiprows=ip.header_rows(p), usecols=["entity", "variable", "ts_utc", "value"])
        it = it[it["variable"] == "interchange_mwh"].assign(v=lambda z: z["value"].astype(float), day=lambda z: z["ts_utc"].str[:10],
                                                            fr=lambda z: z["entity"].str[7:].str.split("-").str[0], to=lambda z: z["entity"].str[7:].str.split("-").str[1])
        it["bad"] = ba_supply.screen(it)
        hp = os.path.join(OUT, nd.EVENT_HOURS + ".csv")
        hourly = None
        if os.path.exists(hp):
            hourly = pd.read_csv(hp, skiprows=ip.header_rows(hp), usecols=["entity", "variable", "ts_utc", "value"])
            hourly = hourly[hourly["variable"] == "interchange_mw"]
        it["kept"], cls.how = nd.confirmed(it, hourly)
        it["out"] = it["bad"] & ~it["kept"]
        cls.it, cls.hourly = it, hourly
        cls.nodes = {n["id"] for n in json.load(open(os.path.join(ROOT, "site", "data", "grid_network.json"), encoding="utf-8"))["nodes"]}

    def by_hand(self, grid, a, b):
        """Net MWh into the grid from each neighbour over the days a to b: each tie read once, from the balancing authority
        whose code sorts first as it reported the day; on a day it did not, from the other's report."""
        it = self.it
        d = it[(it["day"] >= a) & (it["day"] <= b) & ((it["fr"] == grid) | (it["to"] == grid)) & it["fr"].isin(self.nodes) & it["to"].isin(self.nodes)]
        out = {}
        for other in sorted((set(d["fr"]) | set(d["to"])) - {grid}):
            first, second = sorted([grid, other])
            f = d[(d["fr"] == first) & (d["to"] == second)].set_index("day")
            s = d[(d["fr"] == second) & (d["to"] == first)].set_index("day")
            into = 1 if second == grid else -1                       # a report is the reporter's export to the other
            total = 0.0
            for day in sorted(set(f.index) | set(s.index)):
                if day in f.index:
                    total += 0.0 if f.loc[day, "out"] else f.loc[day, "v"] * into
                elif not s.loc[day, "out"]:
                    total += -s.loc[day, "v"] * into
            out[other] = total
        return out

    def traced(self, a, b, grid):
        return node(f"""
import fs from "node:fs";
import {{ trace, easternHours }} from "./lib/networkV3.ts";
const f = JSON.parse(fs.readFileSync("public/network/daily_{a[:4]}.json", "utf8"));
const hrs = f.days.map(easternHours);
console.log(JSON.stringify(trace(f.links, f.days.indexOf("{a}"), f.days.indexOf("{b}") + 1, "{grid}", (h) => hrs[h])));
""")

    def agree(self, grid, a, b):
        hand = {k: v for k, v in self.by_hand(grid, a, b).items() if v > 0}
        t = self.traced(a, b, grid)
        rows = {r["id"]: r for r in t["rows"]}
        self.assertEqual(sorted(rows), sorted(hand))
        total = sum(hand.values())
        self.assertAlmostEqual(t["inMwh"], total, delta=max(100.0, 1e-5 * total))        # the file holds a day's average MW to one decimal
        for k, v in hand.items():
            self.assertAlmostEqual(rows[k]["share"], 100 * v / total, places=2, msg=k)
        return hand, t

    def test_california_over_2021(self):
        hand, t = self.agree("CISO", "2021-01-01", "2021-12-31")
        self.assertEqual((t["held"], t["frames"]), (365, 365))
        self.assertEqual(max(hand, key=hand.get), "BPAT")
        self.assertGreater(len(hand), 6)

    def test_texas_during_uri(self):
        hand, t = self.agree("ERCO", "2021-02-12", "2021-02-19")
        self.assertEqual(sorted(hand), ["CEN", "SWPP"])
        # the three days the rule would have left out: Texas took 23,387 MWh from Mexico on them, and the replay holds it
        cen = self.it[(self.it["entity"] == "eia930:ERCO-CEN") & self.it["day"].isin(["2021-02-12", "2021-02-13", "2021-02-14"])]
        self.assertTrue(cen["bad"].all())
        if self.hourly is not None:
            self.assertTrue(cen["kept"].all())
            self.assertAlmostEqual(-cen["v"].sum(), 23387.0)
            self.assertGreater(hand["CEN"], 23387.0 - 1)
        rows = {r["id"]: r for r in t["rows"]}
        self.assertEqual(rows["CEN"]["via"], [])
        self.assertIn("MISO", [x["id"] for x in rows["SWPP"]["via"]])

    def test_both_operators_reports_of_miso_to_spp_agree_and_the_days_are_kept(self):
        it = self.it
        days = ["2021-02-15", "2021-02-16", "2021-02-17"]
        a = it[(it["entity"] == "eia930:MISO-SWPP") & it["day"].isin(days)].set_index("day")
        b = it[(it["entity"] == "eia930:SWPP-MISO") & it["day"].isin(days)].set_index("day")
        self.assertTrue(a.loc["2021-02-15", "bad"] and a.loc["2021-02-15", "kept"])
        self.assertLess(abs(a.loc["2021-02-15", "v"] + b.loc["2021-02-15", "v"]) / a.loc["2021-02-15", "v"], 0.01)
        f = json.load(open(os.path.join(PUB, "daily_2021.json"), encoding="utf-8"))
        link = next(k for k in f["links"] if (k["a"], k["b"]) == ("MISO", "SWPP"))
        for d in days:
            self.assertIsNotNone(link["mw"][f["days"].index(d)], d)
        self.assertAlmostEqual(link["mw"][f["days"].index("2021-02-15")] * 24, a.loc["2021-02-15", "v"], delta=2.0)

    def test_most_of_what_the_rule_leaves_out_is_confirmed_by_the_other_side(self):
        self.assertEqual(int(self.it["bad"].sum()), 2732)
        self.assertGreater(self.how["both_sides"], 1800)
        self.assertGreater(int(self.it["out"].sum()), 500)             # what neither test confirms stays out


class TheBuildersTest(unittest.TestCase):
    def frame(self, rows):
        return pd.DataFrame(rows, columns=["fr", "to", "day", "v", "bad"])

    def test_two_reports_that_agree_keep_the_day_and_two_that_do_not_leave_it_out(self):
        it = self.frame([("A", "B", "2021-02-15", 95060.0, True), ("B", "A", "2021-02-15", -95390.0, True),      # 0.3 percent apart
                         ("A", "B", "2021-02-16", 95060.0, True), ("B", "A", "2021-02-16", -60000.0, False),     # the other side says something else
                         ("A", "C", "2021-02-15", 50000.0, True),                                               # nobody else reported it
                         ("A", "B", "2021-02-17", 100.0, False), ("B", "A", "2021-02-17", -100.0, False)])
        kept, how = nd.confirmed(it)
        self.assertEqual(kept.tolist(), [True, True, False, False, False, False, False])
        self.assertEqual(how, {"both_sides": 2, "by_hours": 0})

    def test_a_one_sided_day_is_kept_only_when_no_hour_is_above_the_ties_own_hours(self):
        it = self.frame([("E", "M", "2021-02-13", -9000.0, True), ("E", "M", "2021-02-11", -2500.0, False), ("E", "M", "2021-02-20", -30000.0, True)])
        def hours(day, values):
            return [("eia930:E-M", f"{day}T{h + 5:02d}:00:00Z" if h < 19 else f"{pd.Timestamp(day) + pd.Timedelta(days=1):%Y-%m-%d}T{h - 19:02d}:00:00Z", v) for h, v in enumerate(values)]
        rec = hours("2021-02-11", [-382.0] * 6 + [-10.0] * 18) + hours("2021-02-13", [-382.0] * 24) + hours("2021-02-20", [-1250.0] * 24)
        hourly = pd.DataFrame(rec, columns=["entity", "ts_utc", "value"])
        kept, how = nd.confirmed(it, hourly)
        self.assertEqual(kept.tolist(), [True, False, False])           # the 13th ran at the level of the 11th's hours; the 20th is above anything the tie carried
        self.assertEqual(how, {"both_sides": 0, "by_hours": 1})
        short = hourly[~((hourly["ts_utc"] >= "2021-02-13T10") & (hourly["ts_utc"] < "2021-02-13T12"))]
        self.assertEqual(nd.confirmed(it, short)[0].tolist(), [False, False, False])   # a day whose hourly record is not whole proves nothing


class TheReplaysFiles(unittest.TestCase):
    def test_every_day_says_how_many_pairs_it_holds(self):
        index = json.load(open(os.path.join(PUB, "daily_index.json"), encoding="utf-8"))
        for year, meta in index["years"].items():
            f = json.load(open(os.path.join(PUB, f"daily_{year}.json"), encoding="utf-8"))
            self.assertEqual(len(f["pairs_held"]), len(f["days"]), year)
            for i in (0, len(f["days"]) // 2, len(f["days"]) - 1):
                self.assertEqual(f["pairs_held"][i], sum(k["mw"][i] is not None for k in f["links"]), (year, i))
            thin = sum(n < 0.5 * f["pairs_usual"] for n in f["pairs_held"])
            self.assertEqual((meta["thin_days"], meta["pair_days_confirmed"]), (thin, f["missing"]["pair_days_confirmed"]), year)
        self.assertLessEqual(index["last_complete"], index["last"])
        self.assertEqual(index["pair_days_rule"], 2732)
        self.assertEqual(index["years"]["2025"]["thin_days"], 47)       # EIA's file is blank from 5 November to 10 December and from 21 to 31 December 2025

    def test_a_year_holds_no_fewer_flows_than_before_the_days_were_kept(self):
        f = json.load(open(os.path.join(PUB, "daily_2021.json"), encoding="utf-8"))
        link = next(k for k in f["links"] if (k["a"], k["b"]) == ("CEN", "ERCO"))
        got = [link["mw"][f["days"].index(d)] for d in ("2021-02-12", "2021-02-13", "2021-02-14")]
        self.assertTrue(all(v is not None and v > 280 for v in got), got)   # Mexico to Texas, the day's average MW


class TheLivePageIsAsItWas(unittest.TestCase):
    def test_every_change_to_the_component_is_behind_v3(self):
        s = src("site", "app", "network", "Network.tsx")
        self.assertIn("const openHour = v3?.complete && v3.complete.index >= 0 ? v3.complete.index : snap.hours.length - 1;", s)
        self.assertIn("const priceOf = (view: View, v3on: boolean, id: string, h: number) => (v3on && PAUSED_PRICE[id] ? null : view.price(id, h));", s)
        self.assertEqual(s.count("view.price("), 1)                     # only inside priceOf: every reader of a price goes through it
        self.assertIn("{v3 && view.key === \"live\" && v3.complete ? (", s)
        self.assertIn("{v3 && PAUSED_PRICE[pick.id] ? ", s)
        self.assertIn("const thin = isDayView && view.pairsHeld", s)    # the replay is v3's alone
        live = src("site", "app", "network", "page.tsx")
        self.assertNotIn("v3=", live)
        self.assertNotIn("completeHour", live)
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/network": "live"', rel)
        self.assertIn('"/network/v3": "review"', rel)

    def test_the_new_page_says_which_hour_and_that_miso_is_paused(self):
        page = src("site", "app", "network", "v3", "page.tsx")
        for words in ("Newest hour complete for every reporting pair", "data-silent-pairs", "MISO has no ring: it is paused.", "A day the record confirms is kept.",
                      "Nothing is traced through Mexico.", "A day with few pairs or none says so.", "v3={{ index, complete }}"):
            self.assertIn(words, page)
        self.assertIn("miso", src("warehouse", "metadata", "paused_sources.csv").lower())

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("site", "lib", "networkV3.ts"), ("site", "app", "network", "Network.tsx"), ("site", "app", "network", "v3", "page.tsx"), ("warehouse", "derived", "network_daily.py"),
                      ("docs", "methods", "grid_network_v3.md"), ("tests", "test_session124.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
