"""Session 138: "What a datacenter pays" (/cost-of-power). The builder of the page's files on a real sample; the
arithmetic in node on the saved real samples (a flat load pays the mean of the hourly prices, a flexible load never
pays more, the contract matches the battery page's); the page's rules (one page, one address, the earlier tab kept
as a view, the grids shown and blanked, no method on the face, locked for visitors, the live battery page's words
unchanged). No request and no model call."""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import datacenter_page as dp  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Builder(unittest.TestCase):
    def test_hours_are_counted_in_standard_time(self):
        # 06:00 UTC on 1 January is the first hour of the year in US Central standard time, and stays so in summer
        idx = pd.DatetimeIndex(["2025-01-01T06:00:00Z", "2025-07-01T06:00:00Z", "2025-01-01T05:00:00Z"])
        ys, hs = dp.to_std(idx, 6)
        self.assertEqual(list(ys), [2025, 2025, 2024])
        self.assertEqual(list(hs), [0, 181 * 24, 8784 - 1])
        self.assertEqual((dp.year_hours(2024), dp.year_hours(2025)), (8784, 8760))

    def test_a_series_is_trimmed_at_its_ends_and_never_filled(self):
        a = np.full(48, np.nan)
        a[5], a[6], a[9] = 10.0, 11.5, -3.0
        self.assertEqual(dp.trimmed(a), {"s": 5, "v": [10.0, 11.5, None, None, -3.0]})

    def test_the_real_sample_is_whole_and_to_the_cent(self):
        for y in (2021, 2025):
            f = json.loads(src("tests", "fixtures", "session138", f"ercot_HB_HUBAVG_{y}.json"))
            for side in ("rt", "da"):
                s = f["regions"]["HB_HUBAVG"][side]
                self.assertEqual((s["s"], len(s["v"])), (0, 8760))
                self.assertTrue(all(v is not None and round(v, 2) == v for v in s["v"]))
        # Winter Storm Uri is in the sample as it happened: real-time hours at the 9,000 dollar cap
        self.assertGreater(max(json.loads(src("tests", "fixtures", "session138", "ercot_HB_HUBAVG_2021.json"))["regions"]["HB_HUBAVG"]["rt"]["v"]), 8900)

    def test_the_grids_shown_and_the_grids_blanked(self):
        self.assertEqual(list(dp.GRIDS), ["ercot", "caiso", "nyiso", "isone", "spp"])
        self.assertEqual(dp.BLANK["miso"]["words"], "paused while terms are reviewed")
        self.assertEqual(dp.BLANK["pjm"]["words"], "licensed source needed")
        text = src("warehouse", "derived", "datacenter_page.py")
        self.assertIn("pc.licenses()", text)  # internal tables and paused publishers are left out by the registry, not by a list here
        self.assertNotIn("urlopen", text)
        self.assertNotIn("requests", text)

    def test_the_site_files_hold_every_grid_and_no_miso_number(self):
        d = os.path.join(ROOT, "site", "data", "datacenter")
        index = json.loads(src("site", "data", "datacenter", "index.json"))
        self.assertEqual(sorted(index["grids"]), sorted(dp.GRIDS))
        self.assertEqual(sorted(index["blank"]), ["miso", "pjm"])
        self.assertNotIn("miso_as_prices", index["tables"])
        for g, v in index["grids"].items():
            self.assertIn(v["main"], [r["id"] for r in v["regions"]])
            for y in v["years"]:
                self.assertTrue(os.path.exists(os.path.join(d, f"{g}_{y}.json")), f"{g}_{y}.json")
        self.assertFalse([f for f in os.listdir(d) if f.startswith(("miso", "pjm"))])
        self.assertEqual(len(index["grids"]["ercot"]["regions"]), 6)
        self.assertEqual(index["grids"]["ercot"]["years"][0], 2015)


class Merge(unittest.TestCase):
    def test_a_build_adds_hours_and_never_thins_a_kept_file(self):
        old = np.array([1.0, 2.0, np.nan, 4.0])
        new = np.array([np.nan, 2.5, 3.0, np.nan])
        self.assertEqual(list(dp.merged(old, new)), [1.0, 2.5, 3.0, 4.0])   # the new build's hour where it holds one, the kept hour elsewhere
        self.assertIs(dp.merged(None, new), new)
        self.assertIs(dp.merged(old, None), old)
        back = dp.untrimmed(dp.trimmed(np.array([np.nan, 5.0, np.nan, 7.0, np.nan])), 5)
        self.assertTrue(np.array_equal(back, np.array([np.nan, 5.0, np.nan, 7.0, np.nan]), equal_nan=True))
        self.assertEqual(dp.hour_utc(2025, 0, 6), "2025-01-01T06:00:00Z")

    def test_the_weekly_refresh_runs_it_and_the_run_commits_its_files(self):
        self.assertIn('--step "datacenter_page" -- "$PY" warehouse/derived/datacenter_page.py', src("warehouse", "refresh_supply.sh"))
        self.assertIn("site/data/datacenter)", src(".github", "workflows", "daily-prices.yml"))


class Demand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads(src("site", "data", "datacenter", "index.json"))

    def test_tight_hours_are_at_or_above_95_percent_of_the_years_peak(self):
        self.assertEqual((dp.TIGHT, self.index["tight"]), (0.95, 0.95))
        e = self.index["grids"]["ercot"]
        self.assertEqual(e["demand_source"], "ercot_zone_load_hourly (ercot:system)")
        f = json.loads(src("site", "data", "datacenter", "ercot_2025.json"))
        self.assertEqual(len(f["tight"]), e["demand"]["2025"]["tight_hours"])
        self.assertEqual(f["peak_mw"], e["demand"]["2025"]["peak_mw"])
        self.assertIn(f["peak_hour"], f["tight"])
        self.assertTrue(e["demand"]["2025"]["whole"] and not e["demand"]["2026"]["whole"])
        self.assertTrue(all(0 <= i < f["hours"] for i in f["tight"]))

    def test_new_york_is_the_sum_of_its_zones_and_its_zones_are_the_price_zones(self):
        n = self.index["grids"]["nyiso"]
        self.assertEqual(n["demand_source"], "nyiso_zone_load_hourly (the sum of its 11 zones)")
        self.assertEqual(sorted(n["zones"]), sorted(r["id"] for r in n["regions"]))

    def test_an_internal_demand_table_is_named_and_nothing_of_it_is_written(self):
        i = self.index["grids"]["isone"]
        self.assertEqual(i["demand_source"], "withheld:isone_zone_load_hourly")
        self.assertEqual((i["demand"], i["zones"]), ({}, {}))
        for y in i["years"]:
            f = json.loads(src("site", "data", "datacenter", f"isone_{y}.json"))
            self.assertFalse({"tight", "peak_mw", "demand_mean_mw"} & set(f))
        self.assertIn('withheld ? noDemand', src("site", "app", "cost-of-power", "page.tsx"))
        self.assertIsNone(self.index["grids"]["spp"]["demand_source"])


class Delivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file = json.loads(src("site", "data", "datacenter", "texas_delivery.json"))

    def test_only_a_utility_whose_terms_allow_it_is_shown(self):
        self.assertEqual({r["utility"] for r in self.file["rows"]}, {"Oncor"})
        self.assertEqual([(w["utility"], w["words"]) for w in self.file["withheld"]],
                         [("CenterPoint Energy Houston Electric", "licensed source needed"), ("AEP Texas", "held while terms are reviewed"),
                          ("Texas-New Mexico Power", "held while terms are reviewed")])
        self.assertEqual([k for k, v in dp.DELIVERY.items() if v["show"]], ["oncor:retail_delivery_tariff"])
        self.assertEqual(self.file["license"], "internal")
        text = json.dumps(self.file)
        for other in ("5.048210", "5.956038", "5.156858"):   # the other three utilities' transmission factors
            self.assertNotIn(other, text)

    def test_every_charge_shown_has_its_line_its_page_and_its_address(self):
        self.assertGreaterEqual(len(self.file["rows"]), 8)
        for r in self.file["rows"]:
            self.assertTrue(r["sentence"] and r["page"] and r["url"].startswith("https://") and r["unit"] and r["rate_class"] == "Transmission Service", r)
            digits = re.sub(r"[^0-9.]", "", r["value_as_written"])
            self.assertIn(digits, r["sentence"].replace(",", ""), r["charge"])

    def test_a_figure_from_a_many_column_row_is_shown_only_when_its_column_was_checked(self):
        many = [r for r in self.file["rows"] if r["column"]]
        self.assertEqual(sorted(r["charge"] for r in many), ["Distribution Cost Recovery Factor (DCRF)", "Rider MG amount", "Transmission Cost Recovery Factor (TCRF)"])
        # the energy efficiency factor the model read stands in the non-profit column: not shown
        self.assertFalse([r for r in self.file["rows"] if "EECRF" in r["charge"]])
        tcrf = next(r for r in self.file["rows"] if "TCRF" in r["charge"])
        self.assertEqual((tcrf["value"], tcrf["unit"]), (6.260839, "$/4CP kW"))
        self.assertTrue(tcrf["sentence"].endswith("6.260839"))   # the last column of its row: Transmission Service

    def test_delivery_is_never_mixed_into_the_market_cost(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        cell = page.split("function DeliveryCell", 1)[1].split("function ZoneCell", 1)[0]
        self.assertIn("(tcrf.value * 12000) / 8760", cell)
        self.assertNotIn("s12", cell)
        self.assertNotRegex(page, r"s12[^;\n]*tcrf|tcrf[^;\n]*s12")
        self.assertIn("Not added to the market cost above", cell)


class Arithmetic(unittest.TestCase):
    def test_the_node_tests_on_the_saved_real_samples(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "scripts/test-datacenter.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180, encoding="utf-8")
        if r.returncode != 0 and ("Unknown file extension" in r.stderr or "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr):
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("all passed", r.stdout)
        for words in ("a flat load pays the mean of the", "flexible loads pays more per MWh than the flat load", "as the battery page's contractResult computes them"):
            self.assertIn(words, r.stdout)
        self.assertNotIn("FAIL", r.stdout)


class Page(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = src("site", "app", "cost-of-power", "page.tsx")
        cls.form = src("site", "app", "cost-of-power", "LoadForm.tsx")
        cls.contract = src("site", "app", "cost-of-power", "LoadContract.tsx")
        cls.grids = src("site", "app", "cost-of-power", "GridsView.tsx")
        cls.lib = src("site", "lib", "datacenter.ts")

    def test_one_page_one_address_and_no_version_in_it(self):
        d = os.path.join(ROOT, "site", "app", "cost-of-power")
        self.assertEqual(sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))), ["battery", "seller"])
        self.assertIn('action="/cost-of-power"', self.form)
        self.assertNotRegex(self.lib + self.page, r"/cost-of-power/(v\d|datacenter|load)")

    def test_what_the_tab_showed_stays_as_a_view(self):
        self.assertIn('x.view === "grids" ? <GridsView />', self.page)
        for kept in ("<RankBars", "<LineChart", "<HeatGrid", "<CostCarbon", "<Calculator", "cop|flat_cost|", "cop|cheap_cost|", "cop|energy|", "rt_shape_premium"):
            self.assertIn(kept, self.grids)
        self.assertIn('"/cost-of-power?view=grids"', src("site", "scripts", "check-values.mjs"))

    def test_the_tab_is_named_and_the_live_battery_page_keeps_its_words(self):
        tabs = src("site", "app", "cost-of-power", "Tabs.tsx")
        self.assertIn('LABEL = "What a datacenter pays"', tabs)
        self.assertIn('active === "battery" ? FROZEN_LABEL : LABEL', tabs)
        self.assertIn('FROZEN_LABEL = "What power costs to buy"', tabs)
        self.assertIn('title="What a datacenter pays"', self.page)

    def test_the_page_is_locked_for_visitors(self):
        release = src("site", "lib", "release.ts")
        self.assertIn('"/cost-of-power": "review"', release)
        self.assertEqual(re.findall(r'"(/[^"]*)": "live"', release), ["/cost-of-power/battery", "/network", "/storage"])

    def test_the_inputs_the_owner_named(self):
        for name in ('name="grid"', 'name="region"', 'name="mw"', 'name="run"', 'name="n"', 'name="pct"', 'name="shift"', 'name="buy"', 'name="gpu"', 'name="pue"'):
            self.assertIn(name, self.form)
        for run in ("flat:", "hours:", "share:", "shift:"):
            self.assertIn(run, self.lib)
        self.assertIn("title={ASSUMED.gpu.source}", self.form)
        self.assertIn("title={ASSUMED.pue.source}", self.form)
        self.assertIn("NVIDIA DGX H100", self.lib)
        self.assertIn("Uptime Institute", self.lib)

    def test_the_contract_is_never_sent(self):
        # no form, no field name, no address, no storage, no request: the terms are this component's state
        self.assertNotIn("<form", self.contract)
        self.assertNotRegex(self.contract, r'\bname="')
        for never in ("fetch(", "localStorage", "sessionStorage", "document.cookie", "router.", "searchParams", "useRouter"):
            self.assertNotIn(never, self.contract)
        self.assertNotIn("share", [k for k in re.findall(r'"(\w+)"', re.search(r"const KEYS = \[(.*?)\]", self.form).group(1))])
        self.assertIn('"/cost-of-power"', src("site", "components", "SiteLink.tsx"))  # the shared links do not prefetch here

    def test_the_four_questions_and_their_placeholders(self):
        for title in ('title="What will it cost"', 'title="Will the power be there"', 'title="How clean"', 'title="How soon"'):
            self.assertIn(title, self.page)
        self.assertIn('const NOWHERE = "not published anywhere yet"', self.page)
        # how long a new large load waits: every grid. Load in line by region: every grid but NYISO, which publishes it
        # (its queue workbook's load sheets), so there the truth is "not held yet"
        self.assertEqual(self.page.count("words={NOWHERE}"), 3)
        self.assertRegex(self.page, r'x\.grid === "nyiso" \? <Missing key="m" why="NYISO publishes its load interconnection requests')
        self.assertIn('words = "not held yet"', self.page)
        self.assertIn('"Delivery charges"', self.page)
        for link in ("/mix?view=clean&grid=", "/mix?view=stress&grid=", "/demand?area=", "/queues?grid=", "/datacenters"):
            self.assertIn(link, self.page)

    def test_no_method_on_the_face_and_no_em_dash(self):
        face = self.page + self.form + self.contract + self.grids
        for word in ("upper bound", "price taker", "cannot see", "limitation", "caveat", "Wholesale energy only", "does not include"):
            self.assertNotIn(word, re.sub(r"//.*", "", face), word)
        self.assertIn("/data/methods/datacenter_cost", self.page)
        note = src("docs", "methods", "datacenter_cost.md")
        for said in ("most a load could have saved", "Wholesale energy only", "Standard time", "Nothing is filled", "not published anywhere yet", "A hub is not a site"):
            self.assertIn(said, note)
        for name in (("site", "app", "cost-of-power", "page.tsx"), ("site", "app", "cost-of-power", "LoadForm.tsx"), ("site", "app", "cost-of-power", "LoadContract.tsx"),
                     ("site", "app", "cost-of-power", "LoadCharts.tsx"), ("site", "app", "cost-of-power", "GridsView.tsx"), ("site", "lib", "datacenter.ts"),
                     ("site", "lib", "datacenterdata.ts"), ("site", "scripts", "test-datacenter.mjs"), ("warehouse", "derived", "datacenter_page.py"),
                     ("docs", "methods", "datacenter_cost.md"), ("tests", "test_session138.py")):
            self.assertNotIn(chr(0x2014), src(*name), "/".join(name))

    def test_the_price_files_reach_the_server(self):
        self.assertIn('outputFileTracingIncludes: { "/cost-of-power": ["./data/datacenter/*.json"] }', src("site", "next.config.ts"))
        self.assertIn('export const dynamic = "force-dynamic"', self.page)


if __name__ == "__main__":
    unittest.main()
