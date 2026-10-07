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
        self.assertEqual(self.page.count("words={NOWHERE}"), 2)  # load in line by region; how long a new large load waits
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
