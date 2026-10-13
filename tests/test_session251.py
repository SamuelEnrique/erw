"""Session 251: the findings engine, from 7 patterns to 20.

The library (20 patterns, 13 of them measures of hunt_measures.py), session 252's two lessons (a one-interval
measure is never drafted; a draft names only its own region's tables), the second number printed beside a claim, a
family run through the hunt on made-up rows (test inputs, never data), and four of the measures computed on small
made-up tables written to a temporary directory. No network and no warehouse table.
"""
import datetime as dt
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
sys.path.insert(0, FIND)
import hunt  # noqa: E402
import hunt_measures as hm  # noqa: E402

EM = chr(0x2014)
BY = {p["name"]: p for p in hunt.PATTERNS}
HEAD = "entity,variable,ts_utc,value"


def write(d, name, lines, head=HEAD):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table: made-up rows, never data\n" + head + "\n" + "\n".join(lines) + "\n")


def by_year(got, region):
    return {r["year"]: r for r in got["rows"] if r["region"] == region}


class TheLibrary(unittest.TestCase):
    def test_twenty_patterns_thirteen_of_them_measures(self):
        self.assertEqual(len(hunt.PATTERNS), 20)
        fams = [p for p in hunt.PATTERNS if p.get("fn")]
        self.assertEqual(len(fams), 13)
        self.assertEqual({p["fn"] for p in fams}, set(hm.FAMILIES))
        for p in fams:
            self.assertEqual((p["module"], p["region_col"], p["year_col"], p["measure"], p["n_col"]), ("hunt_measures", "region", "year", "value", "n"))
            self.assertGreater(p["n_floor"], 0)
            self.assertNotIn(EM, p["label"] + p["title"])

    def test_the_two_spike_patterns_are_one_interval_and_no_measure_family_is(self):
        self.assertEqual({p["name"] for p in hunt.PATTERNS if p.get("one_interval")}, {"spikes_against_median", "spikes_against_median_grids"})

    def test_a_findings_pattern_names_only_its_own_grids_tables(self):
        every = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "iso_hub_prices_history", "iso_zone_prices_history", "storage_buildout_monthly",
                 "ercot_zone_load_hourly", "eia930_daily_demand", "eia_fuel_spot_prices"]
        self.assertEqual(hunt.region_tables(every, "ercot", "batteries_lunch_grids"), ["ercot_all_hub_prices_history", "iso_rtm_hub_prices"])
        self.assertEqual(hunt.region_tables(every, "HB_WEST", "batteries_lunch"), ["ercot_all_hub_prices_history", "iso_rtm_hub_prices"])
        self.assertEqual(hunt.region_tables(every, "caiso", "peak_hour_grids"), ["iso_hub_prices_history", "iso_rtm_hub_prices"])
        for module, grids in hunt.OWN_TABLES.items():
            for tables in grids.values():
                self.assertNotIn("iso_zone_prices_history", tables, module)     # NYISO's rows: no drafted region reads it


class AFamilyThroughTheHunt(unittest.TestCase):
    def setUp(self):
        self.saved = hunt.PATTERNS
        self.d = tempfile.TemporaryDirectory()

    def tearDown(self):
        hunt.PATTERNS = self.saved
        self.d.cleanup()

    def rows(self, region, values, context=None, first=2019, n=8760):
        return [{"region": region, "words": region.upper(), "year": first + i, "value": v, "n": float(n), "context": (context or {}).get(first + i)}
                for i, v in enumerate(values)]

    def test_a_region_of_a_blocked_grid_is_never_drafted_and_a_public_one_carries_its_context(self):
        P = BY["curtailment_share"]
        rise = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        got = {"rows": self.rows("caiso", rise, {2019: 100.0, 2024: 9000.0}) + self.rows("spp", rise),
               "tables": {"caiso": ["iso_curtailment_monthly", "storage_buildout_monthly"], "spp": ["iso_curtailment_monthly", "storage_buildout_monthly"]}}
        out = hunt.run_family(P, None, 2026, {"spp", "nyiso"}, log=lambda m: None, compute=lambda fn, in_dir: got)
        by = {o[0]: o for o in out}
        self.assertIn("never drafted", by["spp"][4])
        self.assertIsNone(by["spp"][3])
        region, words, series, claim, reason, card, tables = by["caiso"]
        self.assertTrue(claim["passed"])
        self.assertEqual(card["context"], {"2019": 100.0, "2024": 9000.0})
        d = hunt.build_draft(P, region, words, series, claim, "new", card, tables, self.d.name)
        c = d["card"]
        self.assertIn("Beside it, operating batteries at the year's end: 100 MW in 2019, 9,000 MW in 2024.", c["subtitle"])
        self.assertIn("That second number is stated, not tested.", c["footnote"])
        self.assertEqual(c["source_line"], "Source: the rows for CAISO of the ERW tables iso_curtailment_monthly, storage_buildout_monthly; computed by the "
                                           "hunt's measure curtailment_share (warehouse/analysis/findings/hunt_measures.py). Found by the weekly hunt.")
        self.assertEqual(c["tables"], ["iso_curtailment_monthly", "storage_buildout_monthly"])
        self.assertEqual((c["numbers"]["context_first"], c["numbers"]["context_last"]), (100.0, 9000.0))
        csv_lines = d["files"][d["id"] + ".csv"]["content"].splitlines()
        self.assertEqual(csv_lines[4], "region,year,value,n_observations,full_year,context_value")
        self.assertEqual(csv_lines[5], "caiso,2019,1.0,8760.0,1,100.0")
        self.assertEqual(csv_lines[6], "caiso,2020,2.0,8760.0,1,")
        self.assertIn("Beside it, operating batteries", c["hunt"]["caption"])
        self.assertNotIn(EM, str(d["card"]))

    def test_without_its_second_number_in_both_years_nothing_is_said_beside_the_claim(self):
        P = BY["curtailment_share"]
        got = {"rows": self.rows("caiso", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], {2019: 100.0}), "tables": {"caiso": ["iso_curtailment_monthly"]}}
        region, words, series, claim, reason, card, tables = hunt.run_family(P, None, 2026, set(), log=lambda m: None, compute=lambda fn, in_dir: got)[0]
        d = hunt.build_draft(P, region, words, series, claim, "new", card, tables, self.d.name)
        self.assertNotIn("Beside it", d["card"]["subtitle"])
        self.assertEqual(d["files"][d["id"] + ".csv"]["content"].splitlines()[4], "region,year,value,n_observations,full_year")

    def test_a_one_interval_pattern_passes_and_is_never_drafted(self):
        base = dict(BY["negative_prices"], name="one")
        hunt.PATTERNS = [dict(base, one_interval=True), dict(base, name="two")]
        saved = hunt.run_pattern

        def fake(Pn, in_dir, this_year, blocked, log=print, compute=None):
            s = {str(2019 + i): (v, 8760.0) for i, v in enumerate([1.0, 2.0, 3.0, 4.0, 5.0, 6.0 + (Pn["name"] == "two")])}
            return [("ercot_a", "ERCOT A", s, hunt.test_claim(s, Pn, this_year), None, {}, ["ercot_all_hub_prices_history"])]
        hunt.run_pattern = fake
        try:
            loaded = []
            s = hunt.hunt(in_dir=self.d.name, log=lambda m: None, now=dt.datetime(2026, 10, 17, tzinfo=dt.timezone.utc),
                          state_path=os.path.join(self.d.name, "state.json"), out_root=self.d.name,
                          load=lambda drafts, log: loaded.extend(drafts) or [x["id"] for x in drafts])
        finally:
            hunt.run_pattern = saved
        by = {r["key"]: r for r in s["results"]}
        self.assertEqual((s["passed"], s["drafts"]), (2, 1))
        self.assertFalse(by["one|ercot_a"]["drafted"])
        self.assertIn("one interval of a year", by["one|ercot_a"]["reason"])
        self.assertTrue(by["two|ercot_a"]["drafted"])


class TheMeasures(unittest.TestCase):
    def setUp(self):
        hm.clear_cache()
        self.t = tempfile.TemporaryDirectory()
        self.d = self.t.name

    def tearDown(self):
        hm.clear_cache()
        self.t.cleanup()

    def test_curtailment_is_curtailed_over_output_plus_curtailed_with_decembers_fleet_beside_it(self):
        lines = []
        for m in range(1, 13):
            ts = f"2024-{m:02d}-01T00:00:00Z"
            lines += [f"caiso:ISO,share_curtailed_mwh,{ts},10", f"caiso:ISO,share_output_mwh,{ts},90", f"caiso:ISO,share_hours_held,{ts},730"]
        write(self.d, "iso_curtailment_monthly", lines)
        write(self.d, "storage_buildout_monthly", ["iso:caiso,battery_operating_mw,2024-11-01T00:00:00Z,5000", "iso:caiso,battery_operating_mw,2024-12-01T00:00:00Z,6000",
                                                    "iso:caiso,battery_operating_mw,2025-06-01T00:00:00Z,7000"])
        got = hm.curtailment_share(self.d)
        r = by_year(got, "caiso")[2024]
        self.assertAlmostEqual(r["value"], 10.0)
        self.assertEqual((r["n"], r["context"], r["words"]), (8760.0, 6000.0, "CAISO"))
        self.assertEqual(got["tables"]["caiso"], ["iso_curtailment_monthly", "storage_buildout_monthly"])

    def test_scarcity_is_the_share_of_hours_with_the_adder_above_zero(self):
        adders = [f"ercot:system,rtorpa_mean,2024-07-01T{h:02d}:00:00Z,{1.5 if h < 6 else 0}" for h in range(24)]
        write(self.d, "ercot_rtm_price_adders", adders)
        write(self.d, "ercot_zone_load_hourly", ["ercot:system,load,2024-07-01T12:00:00Z,50000"])
        got = hm.scarcity_hours(self.d)
        r = by_year(got, "ercot")[2024]
        self.assertAlmostEqual(r["value"], 25.0)
        self.assertEqual((r["n"], r["context"]), (24.0, None))      # one hour of load is not a year's mean demand

    def test_stress_days_are_the_top_five_percent_by_demand_and_an_import_is_a_negative_interchange(self):
        demand, ti = [], []
        for i in range(40):
            day = (dt.date(2024, 1, 1) + dt.timedelta(days=i)).isoformat() + "T00:00:00Z"
            demand.append(f"eia930:CISO,demand_mwh,{day},{1000 + i}")
            ti.append(f"eia930:CISO,total_interchange_mwh,{day},{-100 if i >= 38 else 50}")
        write(self.d, "eia930_daily_demand", demand)
        write(self.d, "eia930_daily_total_interchange", ti)
        got = hm.stress_day_imports(self.d)
        r = by_year(got, "caiso")[2024]
        self.assertAlmostEqual(r["value"], 200 / (1038 + 1039) * 100)   # the two highest days of 40: both imported 100
        self.assertEqual(r["n"], 40.0)
        self.assertEqual(got["tables"]["caiso"], ["eia930_daily_demand", "eia930_daily_total_interchange"])

    def test_record_days_count_from_the_second_year_and_a_faulty_day_is_left_out(self):
        rows = [f"eia930:PJM,demand_mwh,2019-07-{d:02d}T00:00:00Z,{v}" for d, v in ((1, 100), (2, 110), (3, 105))]
        rows += [f"eia930:PJM,demand_mwh,2020-07-{d:02d}T00:00:00Z,{v}" for d, v in ((1, 111), (2, 109), (3, 120), (4, 5000))]
        write(self.d, "eia930_daily_demand", rows)
        got = hm.record_days(self.d)
        s = by_year(got, "pjm")
        self.assertEqual(sorted(s), [2020])
        self.assertEqual((s[2020]["value"], s[2020]["n"]), (2.0, 3.0))  # 111 and 120 stand above 110; the day of 5,000 is a fault

    def test_the_implied_heat_rate_is_the_median_day_and_the_spread_is_the_median_hour(self):
        head = "ts_utc,value,market,node"
        hub, gas = [], []
        for day, (rt, da, hh) in enumerate(((20.0, 26.0, 2.0), (30.0, 31.0, 3.0), (90.0, 80.0, 3.0)), start=1):
            for h in range(24):
                ts = (dt.datetime(2024, 3, day, 6) + dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")   # the local day in Chicago (CST)
                hub += [f"{ts},{rt},ercot_rtm,HB_NORTH", f"{ts},{da},ercot_dam,HB_NORTH"]
            gas.append(f"eia:henry_hub,spot_price,2024-03-{day:02d}T00:00:00Z,{hh}")
        write(self.d, "ercot_all_hub_prices_history", hub, head)
        write(self.d, "ercot_zone_prices_history", [], head)
        write(self.d, "iso_hub_prices_history", [], head)
        write(self.d, "iso_zone_prices_history", [], head)
        write(self.d, "eia_fuel_spot_prices", gas)
        r = by_year(hm.implied_heat_rate(self.d), "ercot_HB_NORTH")[2024]
        self.assertEqual((r["value"], r["n"], r["words"]), (10.0, 3.0, "ERCOT, North hub (HB_NORTH)"))   # 10, 10 and 30: the median day
        got = hm.da_rt_spread(self.d)
        e = by_year(got, "ercot_HB_NORTH_evening")[2024]
        self.assertEqual((e["value"], e["n"]), (1.0, 15.0))                                             # 6, 1 and -10: the median hour
        self.assertEqual(got["tables"]["ercot_HB_NORTH_evening"], ["ercot_all_hub_prices_history"])
        self.assertIn("4 PM to 9 PM", e["words"])


class TheVerifiedDrafts(unittest.TestCase):
    """The section appended to docs/reviews/findings-verified-2026-10-13.md is held to its result file, as session
    252's part is held to its two (tests/test_session252.py, which still finds its 16 blocks above this section)."""
    DOC = ("docs", "reviews", "findings-verified-2026-10-13.md")
    RESULT = ("docs", "reviews", "findings-verified-2026-10-13-session251", "verify_251.json")

    def section(self):
        with open(os.path.join(ROOT, *self.DOC), encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(text.count("## Session 251's twelve drafts, verified"), 1)
        self.assertLess(text.index("## What the list should learn from this"), text.index("## Session 251's twelve drafts, verified"))
        return text[text.index("## Session 251's twelve drafts, verified"):]

    def blocks(self):
        import re
        body = self.section()
        body = body[body.index("### The 12 drafts of session 251, strongest first"):body.index("### What the hunt should learn from these twelve")]
        return re.split(r"\n### \d+\. ", body)[1:]

    def results(self):
        import json
        with open(os.path.join(ROOT, *self.RESULT), encoding="utf-8") as f:
            return json.load(f)

    def test_twelve_blocks_each_with_its_seven_parts_and_no_forbidden_dash(self):
        bs = self.blocks()
        self.assertEqual(len(bs), 12)
        for b in bs:
            for part in ("- **Draft:**", "- **Claim:**", "- **Number:**", "- **Reproduced:** yes, exactly.", "- **Robust, the hunt's three tests, run again:** 3 of 3 pass.",
                         "- **Robust, five tests the hunt does not run:**", "- **Robust, the question asked another way:**", "- **License:**", "- **Verdict: "):
                self.assertIn(part, b, b[:80])
        self.assertNotIn(EM, self.section())
        self.assertNotIn(chr(0x2013), self.section())

    def test_the_blocks_are_the_drafts_of_the_result_file_and_every_one_reproduced(self):
        import re
        ids = [re.search(r"`(scan-hunt-[0-9a-f]{12})`", b).group(1) for b in self.blocks()]
        res = self.results()
        self.assertEqual(sorted(ids), sorted(r["id"] for r in res))
        self.assertEqual(len(set(ids)), 12)
        for r in res:
            self.assertEqual(r["problems"], [], r["id"])
            self.assertEqual(r["mirror_exit"], 0, r["id"])
            self.assertTrue(r["reproduced_from_own_csv"] and r["reproduced_from_tables_full_years"] and r["tables_are_the_measures_own"], r["id"])
            self.assertGreaterEqual(r["numbers_compared"], 45, r["id"])
            self.assertIn(r["measure"], hm.FAMILIES, r["id"])
            self.assertEqual(r["source_line"].count("ERW tables " + ", ".join(r["tables"]) + ";"), 1, r["id"])   # session 252: its own tables and no other

    def test_the_strongest_come_first_and_the_counts_said_are_the_counts_of_the_blocks(self):
        import re
        verdicts = []
        for b in self.blocks():
            m = re.search(r"- \*\*Verdict: (strong|usable|drop)\.\*\* (.+)", b)
            self.assertIsNotNone(m, b[:80])
            self.assertGreater(len(m.group(2)), 60, b[:80])
            verdicts.append(m.group(1))
        self.assertEqual(verdicts, sorted(verdicts, key={"strong": 0, "usable": 1, "drop": 2}.get))
        said = re.search(r"\*\*Verdicts of the 12: (\d+) strong, (\d+) usable, (\d+) drop\.\*\*", self.section())
        self.assertEqual(tuple(int(x) for x in said.groups()), tuple(verdicts.count(v) for v in ("strong", "usable", "drop")))

    def test_a_drop_leans_on_its_first_year_or_has_one_step_in_three_and_a_strong_one_does_neither(self):
        import re
        res = {r["id"]: r for r in self.results()}
        for b in self.blocks():
            r = res[re.search(r"`(scan-hunt-[0-9a-f]{12})`", b).group(1)]
            v = re.search(r"- \*\*Verdict: (\w+)\.", b).group(1)
            m = r["more"]
            weak = m["share_of_claim_without_first_year"] < 0.5 or m["steps_on_side"] * 3 <= m["steps"]
            if v == "drop":
                self.assertTrue(weak, r["id"])
            if v == "strong":
                self.assertFalse(weak, r["id"])
                self.assertGreaterEqual(m["share_of_claim_without_last_year"], 0.5, r["id"])
                self.assertTrue(all(c.get("same_direction", True) for c in r["cuts"]), r["id"])


if __name__ == "__main__":
    unittest.main()
