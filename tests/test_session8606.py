"""Session 8606 (chain 504, 19 November 2026): the done line of the Grid tool's regions, its cross-check.

Energy Research Warehouse (ERW). replication/grid/crosscheck_regions.py sets the region files' hours beside EIA's own
published regional series (Form EIA-930, the open data API). What is held here: the folding of EIA's energy source
codes is the contract's, the latest hour is found by the page's rule, a source EIA returns no code for is not held
(never zero), the key is never written, and the output on the branch says what it found.
Nothing here makes a request or reads a key.
"""

import csv
import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def module():
    spec = importlib.util.spec_from_file_location("crosscheck_regions", os.path.join(ROOT, "replication", "grid", "crosscheck_regions.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheFolding(unittest.TestCase):
    def test_it_is_the_contracts(self):
        m = module()
        self.assertEqual(m.SOURCES, ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"])
        self.assertEqual(m.ONE["hydro"], ["WAT", "PS"])
        self.assertEqual(m.ONE["storage"], ["BAT", "OES", "UES"])
        self.assertEqual(m.ONE["other"], ["OIL", "GEO", "OTH", "UNK"])
        self.assertEqual((m.ONE["solar"], m.ONE["wind"]), (["SUN", "SNB"], ["WND", "WNB"]))
        contract = src("docs", "state", "page_files_regions.md")
        self.assertIn("`hydro` is EIA's hydropower excluding pumped storage plus pumped storage", contract)
        self.assertIn("`storage` is battery, other and unknown energy storage", contract)
        self.assertIn("`other` is petroleum, geothermal, other and unknown fuel sources", contract)
        self.assertIn('Solar and wind include EIA\'s "with integrated battery storage" columns', contract)

    def test_every_code_of_the_connector_is_in_one_source(self):
        m = module()
        folded = sorted(c for cs in m.ONE.values() for c in cs)
        self.assertEqual(len(folded), len(set(folded)))
        connector = src("warehouse", "connectors", "eia930.py")
        for code in folded:
            self.assertIn(f'"{code}":', connector, code)


class TheHours(unittest.TestCase):
    def test_the_latest_hour_is_the_newest_with_a_net_generation(self):
        m = module()
        self.assertEqual(m.latest({"net_generation": [1, 2, None, 4, None, None]}), 3)
        self.assertIsNone(m.latest({"net_generation": [None, None]}))
        self.assertIsNone(m.latest({}))

    def test_an_hour_and_its_period(self):
        m = module()
        t = m.hour_of({"start": "2026-10-13T05:00:00Z", "step_hours": 1}, 840)
        self.assertEqual(m.period(t), "2026-11-17T05")

    def test_a_value_not_held_is_none(self):
        m = module()
        self.assertIsNone(m.at({"wind": [1.0, None]}, "wind", 1))
        self.assertIsNone(m.at({"wind": [1.0]}, "wind", 5))
        self.assertIsNone(m.at({}, "wind", 0))
        self.assertEqual(m.at({"wind": [0]}, "wind", 0), 0.0)


class TheScript(unittest.TestCase):
    def setUp(self):
        self.s = src("replication", "grid", "crosscheck_regions.py")

    def test_the_key_is_sent_and_never_written(self):
        self.assertIn('shown = API + route + "/data/?" + urllib.parse.urlencode(params)', self.s)
        self.assertIn('"source_url": (fuel_url if', self.s)
        self.assertNotIn("print(k", self.s)
        self.assertNotIn("print(key", self.s)

    def test_a_source_eia_returns_no_code_for_is_not_held(self):
        self.assertIn("eia[s] = sum(part) if part else None", self.s)
        self.assertIn('"not held" if e_v is None', self.s)

    def test_the_period_is_read_both_ways(self):
        self.assertIn("for shift in (0, 1):", self.s)
        self.assertIn("the hour's end", self.s)

    def test_no_em_dash(self):
        for p in (("replication", "grid", "crosscheck_regions.py"), ("tests", "test_session8606.py")):
            self.assertNotIn(EM, src(*p), p)


class TheOutput(unittest.TestCase):
    """The file on the branch, as the run of 19 November wrote it."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "replication", "grid", "crosscheck_regions.csv")
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        cls.head = [l for l in lines if l.startswith("#")]
        cls.rows = list(csv.DictReader(l for l in lines if not l.startswith("#")))

    def test_the_header_names_the_source_and_the_time(self):
        text = "".join(self.head)
        self.assertIn("Form EIA-930", text)
        self.assertIn("# Retrieved: 2026-11-", text)
        self.assertNotIn("api_key", text + "".join(r["source_url"] for r in self.rows))

    def test_thirteen_regions_three_hours_each(self):
        regions = sorted({r["region"] for r in self.rows})
        self.assertEqual(len(regions), 13)
        for reg in regions:
            self.assertEqual(len({r["which"] for r in self.rows if r["region"] == reg}), 3, reg)

    def test_the_files_hour_is_eias_period_at_the_hours_end(self):
        d = [r for r in self.rows if r["figure"] == "demand" and r["same"]]
        end = [r for r in d if r["eia_period_is"] == "the hour's end"]
        start = [r for r in d if r["eia_period_is"] == "the hour's start"]
        self.assertGreaterEqual(sum(r["same"] == "yes" for r in end), 30)
        self.assertEqual(sum(r["same"] == "yes" for r in start), 0)

    def test_most_figures_are_eias_to_one_megawatt_and_the_rest_are_written(self):
        end = [r for r in self.rows if r["eia_period_is"] == "the hour's end" and r["same"]]
        same = sum(r["same"] == "yes" for r in end)
        self.assertGreaterEqual(len(end), 400)
        self.assertGreaterEqual(same / len(end), 0.85)
        self.assertTrue(all(r["difference_mw"] != "" for r in end))            # a figure that differs keeps its difference


def replication():
    spec = importlib.util.spec_from_file_location("replicate_regions", os.path.join(ROOT, "replication", "grid", "replicate_regions.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheReplicationOfTheRegionTabs(unittest.TestCase):
    """replication/grid/replicate_regions.py: the page's figures computed again from the files, without the page's code."""

    def test_a_figure_as_printed_is_read_as_a_number_and_not_held_as_none(self):
        m = replication()
        self.assertEqual(m.num("27,649 MW"), 27649.0)
        self.assertEqual(m.num("+5,141 MW"), 5141.0)
        self.assertEqual(m.num("-0.0%"), 0.0)
        self.assertIsNone(m.num("not held"))
        self.assertIsNone(m.num(""))
        self.assertIsNone(m.num(None))

    def test_the_months_not_held_by_its_own_count(self):
        m = replication()
        mix = {"built": "2026-03-19T12:02:00Z", "months": {k: {} for k in ("2025-08", "2025-10", "2025-11")}}
        self.assertEqual(m.months_not_held(mix), (4, ["2025-09"], ["2025-12", "2026-01", "2026-02"]))
        self.assertEqual(m.months_not_held({"months": {}}), (0, [], []))

    def test_a_figure_held_on_one_side_only_is_not_met(self):
        m = replication()
        t = m.Tally()
        self.assertTrue(t.check("X", "a", None, None, 0.5))
        self.assertFalse(t.check("X", "b", 0.0, None, 0.5))            # the page draws zero, the file holds nothing
        self.assertFalse(t.check("X", "c", None, 12.0, 0.5))
        self.assertTrue(t.check("X", "d", 12.0, 12.4, 0.5))
        self.assertFalse(t.check("X", "e", 12.0, 12.6, 0.5))

    def test_the_run_kept_on_the_branch_met_every_figure(self):
        path = os.path.join(ROOT, "replication", "grid", "regions_figures_met.csv")
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        rows = list(csv.DictReader(l for l in lines if not l.startswith("#")))
        self.assertGreaterEqual(len(rows), 1300)
        self.assertEqual({r["met"] for r in rows}, {"yes"})
        self.assertEqual(len({r["region"] for r in rows}), 13)
        self.assertIn("# Retrieved: the page read 2026-11-", "".join(lines[:5]))

    def test_an_altered_figure_is_caught(self):
        import json
        import tempfile
        m = replication()
        page_path = os.path.join(ROOT, "replication", "grid", "regions_page_figures.json")
        with open(page_path, encoding="utf-8") as f:
            page = json.load(f)
        with open(os.path.join(ROOT, "site", "data", "regions", "index.json"), encoding="utf-8") as f:
            index = json.load(f)
        if page.get("index_built") != index.get("built"):
            self.skipTest("the region files were rebuilt since the page was read: regions_figures.mjs is to be run again")
        first = sorted(page["regions"])[0]
        demand = page["regions"][first]["mix"]["figures"]["Demand"]
        page["regions"][first]["mix"]["figures"]["Demand"] = f"{int(m.num(demand)) + 2:,} MW"
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "altered.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(page, f)
            import contextlib
            import io
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = m.main(["--page", p])
        self.assertEqual(code, 1)
        self.assertIn("NOT MET", out.getvalue())
        self.assertIn("latest hour: Demand, MW", out.getvalue())

    def test_the_figures_are_read_from_the_page_only(self):
        s = src("replication", "grid", "regions_figures.mjs")
        self.assertIn("data-region-figure", s)
        self.assertNotIn("lib/gridregions", s)                          # the harvest uses none of the page's own functions
        r = src("replication", "grid", "replicate_regions.py")
        self.assertNotIn("subprocess", r)
        self.assertNotIn(EM, s + r)


def map_replication():
    spec = importlib.util.spec_from_file_location("replicate_map", os.path.join(ROOT, "replication", "grid", "replicate_map.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheReplicationOfTheMap(unittest.TestCase):
    """replication/grid/replicate_map.py: what the map draws, computed again from the snapshot and the boundary file."""

    LINKS = [{"a": "A", "b": "B", "mw": [5, None, 10, -4]}, {"a": "A", "b": "C", "mw": [1, 2, 0, 3]}, {"a": "B", "b": "D", "mw": [None, None, None, None]}]

    def test_the_hour_the_week_opens_on(self):
        m = map_replication()
        hours = ["h0", "h1", "h2", "h3"]
        # a pair reports when it held a flow in the last `quiet` hours: two of these four hours here, 48 of the week's 168 on the page
        self.assertEqual(m.complete_hour(hours, self.LINKS, 2), (3, 3, 2))             # the pair that never reported is not waited for
        late = [{"a": "A", "b": "B", "mw": [5, 6, 7, None]}, {"a": "A", "b": "C", "mw": [1, 2, None, 3]}]
        self.assertEqual(m.complete_hour(hours, late, 2), (1, 2, 2))                    # the newest hour both hold
        self.assertEqual(m.complete_hour(hours, [{"a": "A", "b": "B", "mw": [None] * 4}], 2), (None, 1, 0))

    def test_a_tie_runs_from_its_exporter_and_a_zero_flow_is_not_drawn(self):
        m = map_replication()
        self.assertEqual(m.flows_at(self.LINKS, 3), {"B>A": 4.0, "A>C": 3.0})
        self.assertEqual(m.flows_at(self.LINKS, 2), {"A>B": 10.0})                      # A-C is zero in that hour
        self.assertEqual(m.flows_at(self.LINKS, 1), {"A>C": 2.0})

    def test_a_regions_net_exchange_counts_a_zero_flow_as_a_tie(self):
        m = map_replication()
        self.assertEqual(m.net_of(self.LINKS, "A", 3), (1.0, 2))                        # 4 in from B, 3 out to C
        self.assertEqual(m.net_of(self.LINKS, "A", 2), (-10.0, 2))
        self.assertEqual(m.net_of(self.LINKS, "C", 2), (0.0, 1))
        self.assertEqual(m.net_of(self.LINKS, "D", 3), (None, 0))

    def test_it_is_the_pages_own_rule_read_in_its_code(self):
        net = src("site", "app", "network", "Network.tsx")
        self.assertIn("l.mw[h] !== 0).map((l) => {", net)
        self.assertIn("source: v > 0 ? l.a : l.b, target: v > 0 ? l.b : l.a, mw: Math.abs(v)", net)
        lib = src("site", "lib", "networkMap.ts")
        self.assertIn("net += l.a === id ? -v : v; ties += 1;", lib)

    def test_the_run_kept_on_the_branch_met_every_figure(self):
        with open(os.path.join(ROOT, "replication", "grid", "map_figures_met.csv"), encoding="utf-8") as f:
            lines = f.readlines()
        rows = list(csv.DictReader(l for l in lines if not l.startswith("#")))
        self.assertGreaterEqual(len(rows), 400)
        self.assertEqual({r["met"] for r in rows}, {"yes"})
        names = [r["figure"] for r in rows]
        self.assertEqual(sum(1 for n in names if n.endswith(": net exchange, MW")), 60 - sum(1 for n in names if n.endswith(": no tie reported this hour")))
        self.assertIn("# Retrieved: the page read 2026-11-", "".join(lines[:5]))

    def test_an_altered_figure_is_caught(self):
        import contextlib
        import io
        import json
        import tempfile
        m = map_replication()
        with open(os.path.join(ROOT, "replication", "grid", "map_page_figures.json"), encoding="utf-8") as f:
            page = json.load(f)
        page["page"]["ties"][0]["mw"] += 2
        page["page"]["width_key"] += 9
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "altered.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(page, f)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = m.main(["--page", p])
        self.assertEqual(code, 1)
        self.assertEqual(out.getvalue().count("NOT MET"), 2)

    def test_the_harvest_reads_the_page_and_the_snapshot_it_drew(self):
        s = src("replication", "grid", "map_figures.mjs")
        self.assertIn('const OBJECT = "storage/v1/object/public/erw-public/network/grid_network.json";', s)
        self.assertIn('export const NETWORK_OBJECT = "storage/v1/object/public/erw-public/network/grid_network.json";', src("site", "lib", "network.ts"))
        self.assertIn("The hour rolled between the two: run again.", s)
        self.assertNotIn("lib/networkMap", s)
        self.assertNotIn(EM, s + src("replication", "grid", "replicate_map.py"))


class TheMapsCrossCheck(unittest.TestCase):
    """replication/grid/crosscheck_map.py and the file it wrote on 19 November."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "replication", "grid", "crosscheck_map.csv"), encoding="utf-8") as f:
            lines = f.readlines()
        cls.head = "".join(l for l in lines if l.startswith("#"))
        cls.rows = list(csv.DictReader(l for l in lines if not l.startswith("#")))

    def test_every_pair_is_the_report_eia_publishes(self):
        pairs = [r for r in self.rows if r["what"].startswith("a pair's flow")]
        self.assertEqual(len(pairs), 159)
        self.assertEqual({r["same"] for r in pairs}, {"yes"})

    def test_the_net_exchange_is_not_the_authoritys_own_total_and_the_file_says_by_how_much(self):
        nets = [r for r in self.rows if r["what"].startswith("an authority's net exchange")]
        compared = [r for r in nets if r["same"]]
        self.assertEqual((len(compared), sum(r["same"] == "yes" for r in compared)), (60, 39))
        pjm = next(r for r in nets if r["which"] == "PJM")
        self.assertEqual((pjm["snapshot_mw"], pjm["eia_mw"]), ("811", "82"))

    def test_the_header_and_the_key(self):
        self.assertIn("Form EIA-930", self.head)
        self.assertIn("# Retrieved: 2026-11-", self.head)
        self.assertIn("the hour's end", self.head)
        self.assertNotIn("api_key", self.head + "".join(r["source_url"] for r in self.rows))
        s = src("replication", "grid", "crosscheck_map.py")
        self.assertIn('("api_key", k)', s)
        self.assertNotIn("print(k", s)
        self.assertNotIn(EM, s)


class TheDecisionsOnThePage(unittest.TestCase):
    def test_the_maps_block_is_inside_the_maps_frame_and_every_line_has_a_rule_and_a_source(self):
        d = src("site", "app", "network", "MapDecisions.tsx")
        self.assertEqual(d.count('  { what: "'), 9)
        self.assertEqual(d.count('    rule: "'), 9)
        self.assertEqual(d.count('    source: "'), 9)
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn("<MapDecisions />", m)
        self.assertNotIn("MapDecisions", src("site", "app", "network", "Network.tsx"))      # the Network shape is as it was
        self.assertNotIn("MapDecisions", src("site", "components", "grid", "NetworkView.tsx"))
        self.assertNotIn(EM, d)

    def test_the_maps_figures_are_the_cross_checks(self):
        d = src("site", "app", "network", "MapDecisions.tsx")
        self.assertIn("each of the 159 pairs is the report EIA publishes, to 1 MW", d)
        self.assertIn("for 21 of the 60 authorities EIA holds a total for", d)
        self.assertIn("PJM's pairs sum to 811 MW exported; its own total is 82 MW exported.", d)

    def test_the_regions_block_says_the_later_choices(self):
        r = src("site", "app", "grid", "RegionTool.tsx")
        for key in ("hours", "months", "part-month", "storage", "crosscheck"):
            self.assertIn(f'data-decision="{key}"', r)
        # the count on the page is the kept file's own (the cross-check was read again on the rebuilt files in session 8613)
        with open(os.path.join(ROOT, "replication", "grid", "crosscheck_regions.csv"), encoding="utf-8") as f:
            end = [x for x in csv.DictReader(l for l in f if not l.startswith("#")) if x["eia_period_is"] == "the hour's end" and x["same"]]
        self.assertIn(f"{sum(x['same'] == 'yes' for x in end)} of {len(end)} figures are the same to 1 MW", r)
        self.assertIn('data-decisions="8602"', r)                                            # the fold session 8602 pinned still stands


if __name__ == "__main__":
    unittest.main()
