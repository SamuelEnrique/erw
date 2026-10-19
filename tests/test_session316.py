"""Session 316: the hunt's fourth test and its floor (the Research pack's ruling 2a), and the publisher's figure beside
a record of EIA's newest month (ruling 4b); the owner's rulings of 19 October 2026, the chain of 19 October (daytime).
What is held to:

  test_claim runs five tests: the three of session 233, half the change remains without the first year, and a floor
    of one typical yearly move; the stored series of the four spike drafts of 13 October fail the floor and ERCOT's
    night wind of 14 October fails the fourth test, so none would have been drafted; the three strong drafts of
    13 October still pass;
  a scanner record on an EIA table needs the publisher's figure before approval: the route refuses "approved" without
    card.publisher, the review page shows the figure beside ours, and publisher_figure.py's pure parts build EIA's
    request from the series' entity, read the period's row, convert as the connector does and compare;
  the two methods notes say the rules; the data machine runs the hunt and the read; no em dash.

No request, no model call, no database; the environment is read, never set."""
import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = ["warehouse/analysis/findings/hunt.py", "warehouse/analysis/findings/publisher_figure.py", "site/app/internal/findings/state/route.ts",
         "site/app/internal/findings/page.tsx", "site/lib/scanner.ts", "site/lib/findings.ts", "docs/methods/automated_analysis_findings.md",
         "docs/methods/automated_analysis_scanner.md", "tests/test_session233.py", "tests/test_session316.py"]
FINDINGS = os.path.join(ROOT, "warehouse", "analysis", "findings")
sys.path.insert(0, FINDINGS)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(FINDINGS, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def verified(folder, name):
    return json.load(open(os.path.join(ROOT, "docs", "reviews", folder, name), encoding="utf-8"))


def pattern(hunt, name):
    return next(P for P in hunt.PATTERNS if P["name"] == name)


def series_of(row):
    return {y: (float(v[0]), float(v[1])) for y, v in row["series"].items()}


class TheFourthTestAndTheFloor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hunt = load("hunt")

    def test_five_tests_and_the_floor_is_one_typical_move(self):
        self.assertEqual(self.hunt.STRENGTH_FLOOR, 1.0)
        s = {str(2019 + i): (float(v), 8760.0) for i, v in enumerate([1.0, 2.0, 2.5, 3.0, 4.0, 5.0])}
        P = {"n_floor": 8000, "decimals": 1, "unit": "x"}
        c = self.hunt.test_claim(s, P, 2026)
        self.assertEqual([t["name"] for t in c["tests"]], ["holds in more than one year", "survives a change of window", "sample large enough",
                                                           "half the change remains without the first year", "at least one typical yearly move"])
        self.assertTrue(c["passed"])
        self.assertAlmostEqual(c["remains_without_first"], 3.0 / 4.0)

    def test_a_claim_that_leans_on_its_first_year_fails_the_fourth_test(self):
        s = {str(2019 + i): (float(v), 8760.0) for i, v in enumerate([1.0, 5.0, 5.1, 5.2, 5.3, 5.4])}
        c = self.hunt.test_claim(s, {"n_floor": 8000, "decimals": 1, "unit": "x"}, 2026)
        t = {x["name"]: x for x in c["tests"]}
        self.assertFalse(t["half the change remains without the first year"]["passed"])
        self.assertIn("percent of the change from 2019", t["half the change remains without the first year"]["words"])
        self.assertFalse(c["passed"])

    def test_two_full_years_cannot_leave_the_first_out(self):
        s = {"2024": (1.0, 8760.0), "2025": (2.0, 8760.0), "2026": (3.0, 2000.0)}
        c = self.hunt.test_claim(s, {"n_floor": 8000, "decimals": 1, "unit": "x"}, 2026)
        t = {x["name"]: x for x in c["tests"]}
        self.assertFalse(t["half the change remains without the first year"]["passed"])
        self.assertIn("three are needed", t["half the change remains without the first year"]["words"])

    def test_the_four_spike_drafts_of_13_october_would_not_have_been_drafted(self):
        rows = {r["id"][-12:]: r for r in verified("findings-verified-2026-10-13", "verify_hunt.json")}
        stopped = {}
        for tail in ("4bee49d6e8c5", "8c67230bc8b7", "346d3337bb15", "f732d699c6b7"):
            r = rows[tail]
            P = pattern(self.hunt, r["pattern"])
            c = self.hunt.test_claim(series_of(r), P, 2026)
            t = {x["name"]: x for x in c["tests"]}
            self.assertFalse(c["passed"], tail)
            self.assertFalse(t["at least one typical yearly move"]["passed"], tail)
            self.assertLess(c["strength"], 1.0, tail)
            stopped[tail] = c["strength"]
        self.assertEqual(sorted(round(v, 4) for v in stopped.values()), [0.4317, 0.4926, 0.4974, 0.5098])

    def test_ercots_night_wind_of_14_october_would_not_have_been_drafted_and_the_strong_three_still_would(self):
        rows = {r["id"][-12:]: r for r in verified("findings-verified-2026-10-13-session251", "verify_251.json")}
        wind = rows["81c8eceefbb2"]
        P = pattern(self.hunt, "wind_night_share")
        c = self.hunt.test_claim(series_of(wind), P, 2026)
        t = {x["name"]: x for x in c["tests"]}
        self.assertFalse(c["passed"])
        self.assertFalse(t["half the change remains without the first year"]["passed"])
        self.assertLess(c["remains_without_first"], 0.02)                     # 1.5 percent of the change remains without 2019
        self.assertTrue(t["at least one typical yearly move"]["passed"])       # its strength, 3.6, was never the fault
        strong = {r["id"][-12:]: r for r in verified("findings-verified-2026-10-13", "verify_hunt.json")}
        for tail in ("e5fe5b80e074", "f5c8f78e8cf0", "bbb2fe2a3844"):
            r = strong[tail]
            c = self.hunt.test_claim(series_of(r), pattern(self.hunt, r["pattern"]), 2026)
            self.assertTrue(c["passed"], tail)
            self.assertGreaterEqual(c["remains_without_first"], 0.5, tail)


class ThePublishersFigure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pf = load("publisher_figure")

    def test_the_request_is_built_from_the_entity_as_the_connector_reads_it(self):
        pf = self.pf
        route, q, data = pf.request_of("eia_retail_electricity_prices", {"entity": "eia:retail_price:DC:IND"}, "2026-07-01")
        self.assertEqual((route, data), ("electricity/retail-sales", "price"))
        self.assertIn(("facets[stateid][]", "DC"), q)
        self.assertIn(("facets[sectorid][]", "IND"), q)
        self.assertIn(("start", "2026-07"), q)
        route, q, data = pf.request_of("eia_state_generation_monthly", {"entity": "eia:generation:WY:NG"}, "2026-07-15")
        self.assertEqual((route, data), ("electricity/electric-power-operational-data", "generation"))
        self.assertIn(("facets[location][]", "WY"), q)
        self.assertIn(("facets[fueltypeid][]", "NG"), q)
        self.assertIn(("facets[sectorid][]", "99"), q)
        route, q, data = pf.request_of("eia_retail_sales_monthly", {"entity": "eia:customers:DC:IND"}, "2026-07-01")
        self.assertEqual(data, "customers")
        with self.assertRaises(ValueError):
            pf.request_of("eia_retail_electricity_prices", {"entity": "ercot:HB_NORTH"}, "2026-07-01")
        self.assertNotIn("api_key", json.dumps(q))

    def test_the_figure_is_read_converted_and_compared_and_never_made_up(self):
        pf = self.pf
        rows = [{"period": "2026-06", "price": "30.1", "price-units": "cents per kilowatt-hour"}, {"period": "2026-07", "price": "32.15", "price-units": "cents per kilowatt-hour"}]
        self.assertEqual(pf.figure_of(rows, "price", "2026-07"), (32.15, "cents per kilowatt-hour"))
        self.assertIsNone(pf.figure_of(rows, "price", "2026-08"))
        self.assertEqual(pf.convert(32.15, "cents per kilowatt-hour"), (321.5, "USD/MWh"))
        v, u = pf.convert(1028.747, "thousand megawatthours")
        self.assertAlmostEqual(v, 1028747.0)
        self.assertEqual(u, "MWh")
        self.assertEqual(pf.convert(5.0, "something new"), (5.0, "something new"))
        self.assertTrue(pf.compare(321.5, 321.5000001))
        self.assertFalse(pf.compare(321.5, 322.0))
        self.assertFalse(pf.compare(None, 1.0))
        self.assertTrue(pf.is_eia_record({"rule": "record", "table_name": "eia_state_generation_monthly"}))
        self.assertFalse(pf.is_eia_record({"rule": "record", "table_name": "ercot_hub_prices_daily"}))
        self.assertFalse(pf.is_eia_record({"rule": "spike", "table_name": "eia_state_generation_monthly"}))
        s = src("warehouse", "analysis", "findings", "publisher_figure.py")
        self.assertIn("raise RuntimeError(f\"EIA {route}: no row for {period}\")", s)     # no figure is made up
        self.assertIn("return 1 if failed else 0", s)

    def test_the_route_refuses_approval_without_the_figure_and_the_page_shows_it(self):
        route = src("site", "app", "internal", "findings", "state", "route.ts")
        self.assertIn('if (needsPublisher(draft) && !draft.card.publisher) return json({ ok: false, reason: "a record of an EIA table is approved only with EIA\'s own figure beside ours', route)
        self.assertLess(route.index('if (state === "approved") {'), route.index("const r = await setDraftState(id, state, requestId);"))
        sc = src("site", "lib", "scanner.ts")
        self.assertIn('export const needsPublisher = (d: Pick<Draft, "rule" | "table_name">) => d.rule === "record" && /^eia_/.test(d.table_name);', sc)
        page = src("site", "app", "internal", "findings", "page.tsx")
        self.assertIn("<PublisherLine d={d} />", page)
        self.assertIn('data-publisher="missing"', page)
        self.assertIn('data-publisher={p.same ? "same" : "differs"}', page)
        self.assertIn("publisher?: { source: string; period: string; value: number; unit: string;", src("site", "lib", "findings.ts"))

    def test_the_notes_say_the_rules(self):
        self.assertIn("## The hunt's fourth test and its floor (session 316, 19 October 2026)", src("docs", "methods", "automated_analysis_findings.md"))
        self.assertIn("## The publisher's figure beside a record (session 316, 19 October 2026)", src("docs", "methods", "automated_analysis_scanner.md"))


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
