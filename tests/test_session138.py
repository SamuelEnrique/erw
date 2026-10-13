"""Session 138: "What a datacenter pays" (/cost-of-power). The builder of the page's files on a real sample; the
arithmetic in node on the saved real samples (a flat load pays the mean of the hourly prices, a flexible load never
pays more, the contract matches the battery page's); the page's rules (one page, one address, the earlier tab kept
as a view, the grids shown and blanked, no method on the face, locked for visitors, the tab named alike on the three
pages since session 190). No request and no model call."""
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
        # session 140: ERCOT's six trading hubs and its eight load zones, where a load settles
        self.assertEqual(len(index["grids"]["ercot"]["regions"]), 14)
        self.assertEqual(sum(1 for r in index["grids"]["ercot"]["regions"] if r.get("kind") == "zone"), 8)
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
        self.assertIn("site/data/datacenter site/data/nyiso_load_queue.json", src(".github", "workflows", "daily-prices.yml"))   # session 140 added New York's load queue; session 144 the Texas file after it


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
        tables = src("site", "app", "cost-of-power", "tables.csv", "route.ts")   # session 213: the grid questions are the download
        self.assertIn("const noDemand = withheld ?", tables)
        self.assertIn("withheld ? noDemand", tables)
        self.assertIsNone(self.index["grids"]["spp"]["demand_source"])


class Delivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file = json.loads(src("site", "data", "datacenter", "texas_delivery.json"))

    def test_all_four_utilities_are_shown_as_public_regulatory_filings(self):
        # Session 138 showed Oncor's rows alone, by its reading of each utility's terms. The owner's ruling of session 140:
        # all four are shown, each row citing its tariff document, address and date, as public regulatory filings.
        self.assertEqual({r["utility"] for r in self.file["rows"]}, {"Oncor", "CenterPoint Energy Houston Electric", "AEP Texas", "Texas-New Mexico Power"})
        self.assertEqual(self.file["withheld"], [])
        self.assertEqual(list(dp.DELIVERY), ["oncor:retail_delivery_tariff", "centerpoint:retail_delivery_tariff", "aeptexas:retail_delivery_tariff", "tnmp:retail_delivery_tariff"])
        self.assertEqual(self.file["license"], "internal")
        for r in self.file["rows"]:
            self.assertIn("public regulatory filing", r["terms"])
        text = json.dumps(self.file)
        for factor in ("6.260839", "5.048210", "5.956038", "5.156858"):   # the four utilities' transmission factors, as printed
            self.assertIn(factor, text)

    def test_every_charge_shown_has_its_line_its_page_and_its_address(self):
        self.assertGreaterEqual(len(self.file["rows"]), 30)
        for r in self.file["rows"]:
            self.assertTrue(r["sentence"] and r["page"] and r["url"].startswith("https://") and r["unit"] and r["rate_class"].startswith("Transmission"), r)
            self.assertTrue(r["effective"] and r["document"], r)   # the date its sheet prints, and the tariff document
            self.assertIn(r["kind"], ("transmission", "distribution", "other"))
            digits = re.sub(r"[^0-9.]", "", r["value_as_written"])
            self.assertIn(digits, r["sentence"].replace(",", ""), r["charge"])

    def test_a_figure_from_a_many_column_row_is_shown_only_when_its_column_was_checked(self):
        many = [r for r in self.file["rows"] if r["column"]]
        self.assertEqual(sorted(r["charge"] for r in many), ["Distribution Cost Recovery Factor (DCRF)", "Rider MG amount", "Transmission Cost Recovery Factor (TCRF)"])
        # the energy efficiency factors the model read stand in non-profit columns (Oncor 0.000446, CenterPoint 0.000621): not shown
        text = json.dumps(self.file)
        self.assertNotIn("0.000446", text)
        self.assertNotIn("0.000621", text)
        tcrf = next(r for r in self.file["rows"] if r["utility"] == "Oncor" and "TCRF" in r["charge"])
        self.assertEqual((tcrf["value"], tcrf["unit"], tcrf["kind"]), (6.260839, "$/4CP kW", "transmission"))
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
        self.assertEqual(sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))), ["battery", "months.csv", "seller", "tables.csv"])   # session 213: the two downloads
        self.assertIn('action="/cost-of-power"', self.form)
        self.assertNotRegex(self.lib + self.page, r"/cost-of-power/(v\d|datacenter|load)")

    def test_what_the_tab_showed_stays_as_a_view(self):
        self.assertIn('x.view === "grids" ? <GridsView />', self.page)
        for kept in ("<RankBars", "<LineChart", "<HeatGrid", "<CostCarbon", "<Calculator", "cop|flat_cost|", "cop|cheap_cost|", "cop|energy|", "rt_shape_premium"):
            self.assertIn(kept, self.grids)
        self.assertIn('"/cost-of-power?view=grids"', src("site", "scripts", "check-values.mjs"))

    def test_the_tab_is_named_and_reads_alike_on_the_three_pages(self):
        # session 190: until then the battery page, open to visitors and under the freeze through 7 October 2026, kept
        # the words "What power costs to buy" on this tab; the freeze is over and that page is in review (session 166)
        tabs = src("site", "app", "cost-of-power", "Tabs.tsx")
        self.assertIn('LABEL = "What a datacenter pays"', tabs)
        self.assertIn('{tab("/cost-of-power", LABEL, active === "buy")}', tabs)
        self.assertNotIn("FROZEN_LABEL =", tabs)
        self.assertNotIn('"What power costs to buy"', tabs.split("const LABEL", 1)[1])
        self.assertIn('title="What a datacenter pays"', self.page)

    def test_the_page_is_locked_for_visitors(self):
        release = src("site", "lib", "release.ts")
        self.assertIn('"/cost-of-power": "review"', release)
        # session 166 (the owner's instruction of 8 October 2026): the three pages that were open are in review; no page is live
        for path in ("/cost-of-power/battery", "/network", "/storage"):
            self.assertIn(f'"{path}": "review"', release)
        self.assertEqual(re.findall(r'"(/[^"]*)": "live"', release), [])

    def test_the_inputs_the_owner_named(self):
        for name in ('name="grid"', 'name="region"', 'name="mw"', 'name="run"', 'name="n"', 'name="pct"', 'name="shift"', 'name="buy"'):
            self.assertIn(name, self.form)
        # session 195: the power per GPU and the overhead ratio are scenario A's assumptions, with the same cited
        # defaults; "Your load" no longer holds them, and says where they are set
        for name in ('name="gpu"', 'name="pue"'):
            self.assertNotIn(name, self.form)
        self.assertIn("scenario A gives the headline", self.form)
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn("gpuSource: ASSUMED.gpu.source, pueSource: ASSUMED.pue.source", src("site", "app", "cost-of-power", "model.ts"))   # session 213: the page's reads are model.ts
        for run in ("flat:", "hours:", "share:", "shift:"):
            self.assertIn(run, self.lib)
        self.assertIn("title={ASSUMED.gpu.source}", page)                          # the source line's two defaults, on hover
        self.assertIn("title={ASSUMED.pue.source}", page)
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
        # session 213 (the owner's chain prompt of 12 October 2026): the page asks the battery page's three questions; the three
        # grid questions are its download, tables.csv, written from the same files, with their placeholders' words in `note`
        for title in ('title="What will it pay?"', 'title="Which option is better?"', 'title="What matters most"'):
            self.assertIn(title, self.page)
        self.assertIn(">What will it cost</Sub>", self.page)
        model = src("site", "app", "cost-of-power", "model.ts")
        tables = src("site", "app", "cost-of-power", "tables.csv", "route.ts")
        self.assertIn('export const NOWHERE = "not published anywhere yet"', model)
        self.assertEqual(tables.count("${NOWHERE}"), 2)                               # the load in line by region, ERCOT and the rest
        for table in ('"power_there"', '"how_clean"', '"how_soon"', '"waits"', '"rules"', '"regions"', '"matrix"', '"ny_load"'):
            self.assertIn(table, tables, table)
        # session 149 (the owner's ruling of 7 October 2026): New York's load in line is written only when the connector's switch
        # puts it back; until then its placeholder's words and reason
        self.assertIn('if (NY_SHOWN) {', tables)
        self.assertIn('`${NY_HELD_WORDS}: ${NY_HELD_WHY}`', tables)
        self.assertIn('words = "not held yet"', self.page)
        self.assertIn('"Delivery charges"', self.page)
        for link in ("/mix?view=clean&grid=", "/mix?view=stress&grid=", "/demand?area=", "/queues?grid=", "/datacenters"):
            self.assertIn(link, self.page)

    def test_no_method_on_the_face_and_no_em_dash(self):
        face = self.page + self.form + self.contract + self.grids
        # session 213 (the owner's chain prompt of 12 October 2026, as session 208 on the battery): one sentence of what the model
        # cannot see stands under the cost table with a link to the note; it is the one paragraph of method on the face
        face = re.sub(r'<p className="mt-2 max-w-3xl text-xs text-muted" data-income-note="1">.*?</p>', "", face, flags=re.S)
        face = re.sub(r"\{/\*.*?\*/\}", "", face, flags=re.S)
        for word in ("upper bound", "price taker", "cannot see", "limitation", "caveat", "Wholesale energy only", "does not include"):
            self.assertNotIn(word, re.sub(r"//.*", "", face), word)
        self.assertIn("/data/methods/datacenter_cost", self.page)
        note = src("docs", "methods", "datacenter_cost.md")
        # session 140: the flexible figure is a rule's; the hours chosen with foresight stand beside it as "the most the load could have saved"
        for said in ("the most the load could have saved", "never on the price the hour settles at", "Wholesale energy only", "Standard time", "Nothing is filled", "not published anywhere yet", "A hub is not a site"):
            self.assertIn(said, note)
        for name in (("site", "app", "cost-of-power", "page.tsx"), ("site", "app", "cost-of-power", "LoadForm.tsx"), ("site", "app", "cost-of-power", "LoadContract.tsx"),
                     ("site", "app", "cost-of-power", "LoadCharts.tsx"), ("site", "app", "cost-of-power", "GridsView.tsx"), ("site", "lib", "datacenter.ts"),
                     ("site", "lib", "datacenterdata.ts"), ("site", "scripts", "test-datacenter.mjs"), ("warehouse", "derived", "datacenter_page.py"),
                     ("docs", "methods", "datacenter_cost.md"), ("tests", "test_session138.py")):
            self.assertNotIn(chr(0x2014), src(*name), "/".join(name))

    def test_the_price_files_reach_the_server(self):
        # session 183: the seller page's hub files joined the same setting, so the line is no longer this entry alone
        self.assertIn('outputFileTracingIncludes: { "/cost-of-power": ["./data/datacenter/*.json"]', src("site", "next.config.ts"))
        self.assertIn('export const dynamic = "force-dynamic"', self.page)


if __name__ == "__main__":
    unittest.main()
