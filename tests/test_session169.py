"""Session 169: Thesis Builder (warehouse/thesis), the owner's rulings of 8 October 2026.

Part A, the gate on the niche: "A Run anyway box, stored with the run and flagged on its report." The site decides
(site/lib/thesis/niche.ts, tested by site/scripts/test-thesis-niche.mjs); the runner reads what was stored
(thesis_runs.gate, migration 026) and flags the report.

Part B, the bug: "run.py:150-151 (words_of, [a-z][a-z-]{3,}) and :883 drop every word under four letters, so "oil"
and "gas" are never searched. Keep short domain words: oil, gas, ev, ai, lng, smr, ccs, dac, pv, h2, co2."

No network, no model call, no database. The tables a test reads are written by the test into a folder of its own
(every row there is made up for the test and says so); a machine without the warehouse's tables runs every test.
"""
import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_LEDGER_BEFORE = []


def setUpModule():
    """The ledger is off while this module's tests run and is put back after them (never set at import)."""
    _LEDGER_BEFORE.append(os.environ.get("ERW_LEDGER"))
    os.environ["ERW_LEDGER"] = "0"


def tearDownModule():
    old = _LEDGER_BEFORE.pop()
    if old is None:
        os.environ.pop("ERW_LEDGER", None)
    else:
        os.environ["ERW_LEDGER"] = old


def load(name, *parts):
    """By path, under a name of its own: the suite already holds other modules named run, build and store."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


R = load("erw_thesis_run", "warehouse", "thesis", "run.py")
tb = R.tb
SHORT = ["oil", "gas", "ev", "ai", "lng", "smr", "ccs", "dac", "pv", "h2", "co2"]
OLD = lambda text: [w for w in re.findall(r"[a-z][a-z-]{3,}", text.lower()) if w not in R.STOP]      # noqa: E731  words_of before session 169


class Quiet:
    def __init__(self):
        self.lines, self.erw, self.sources = [], [], {}

    def __call__(self, line):
        self.lines.append(line)


def write_table(folder, name, columns, rows):
    with open(os.path.join(folder, name + ".csv"), "w", encoding="utf-8", newline="") as f:
        f.write("# made up for tests/test_session169.py: no row here is a real company, deal or policy action\n")
        f.write(",".join(columns) + "\n")
        for r in rows:
            f.write(",".join('"' + str(r.get(c, "")).replace('"', '""') + '"' for c in columns) + "\n")


class ShortWords(unittest.TestCase):
    """Part B: the short words of the domain are kept, each as a whole word; every longer word is read as before."""

    def test_the_owners_list_is_the_list(self):
        self.assertEqual(sorted(R.SHORT), sorted(SHORT))
        self.assertEqual(sorted(tb.SHORT), sorted(SHORT))

    def test_each_short_word_is_kept(self):
        for w in SHORT:
            self.assertEqual(R.words_of(f"{w.upper()} monitoring"), [w, "monitoring"], w)
            self.assertIn(w, R.words_of(f"sensors for {w}"), w)

    def test_oil_and_gas_are_searched(self):
        self.assertEqual(R.words_of("oil & gas demand"), ["oil", "gas", "demand"])
        self.assertEqual(R.words_of("Methane leak detection for oil and gas operators"), ["methane", "leak", "detection", "oil", "gas", "operators"])
        self.assertEqual(R.words_of("CO2 capture, DAC and CCS hubs; H2 for LNG; SMR sites; PV for EV; AI"),
                         ["co2", "capture", "dac", "ccs", "hubs", "h2", "lng", "smr", "sites", "pv", "ev", "ai"])

    def test_a_short_word_inside_another_word_is_not_a_word(self):
        self.assertEqual(R.words_of("soil boiling maintain development gasket evening"), ["soil", "boiling", "maintain", "development", "gasket", "evening"])
        self.assertEqual(R.words_of("h2o co2e pvc evs"), [])                 # neither a short domain word nor four letters
        self.assertEqual(R.words_of("an old cat sat"), [])                    # other short words stay out, as before

    def test_longer_words_are_read_as_before(self):
        for text in ("Geothermal mapping and sensing, US startups", "Grid-scale battery storage software for merchant operators",
                     "Subsurface heat mapping for geothermal", "long-duration storage for data centers", "closed-loop well technology"):
            self.assertEqual(R.words_of(text), OLD(text), text)
        text = "oil-field services and bio-gas upgrading"      # a hyphenated word is one word, as before
        self.assertEqual(R.words_of(text), OLD(text))

    def test_the_stop_words_still_stop(self):
        self.assertEqual(R.words_of("energy and power for the market"), [])

    def test_a_short_word_matches_a_text_as_a_whole_word_only(self):
        self.assertTrue(R.has_word("methane sensors for oil and gas wells", "oil"))
        self.assertTrue(R.has_word("methane sensors for oil and gas wells", "gas"))
        self.assertTrue(R.has_word("oil/gas (upstream)", "gas"))
        self.assertFalse(R.has_word("soil moisture sensing", "oil"))
        self.assertFalse(R.has_word("las vegas gasoline", "gas"))
        self.assertFalse(R.has_word("project development", "ev"))
        self.assertFalse(R.has_word("maintain the air", "ai"))
        self.assertTrue(R.has_word("geothermal mapping", "therm"))           # a long word anywhere, as before

    def test_the_policy_words_hold_the_short_words(self):
        drop = {"merchant", "operators", "software", "mapping", "sensing"}
        self.assertEqual(tb.policy_words("oil & gas demand", drop), ["demand", "oil", "gas"])
        self.assertEqual(tb.policy_words("Methane leak detection for oil and gas operators", drop), ["methane", "detection", "oil", "gas"])
        self.assertEqual(tb.policy_words("Geothermal mapping and sensing", drop), ["geothermal"])      # as before
        self.assertEqual(tb.policy_words("AI for EV fleets"), ["fleets", "ai", "ev"])
        self.assertEqual(tb.policy_words("gas, gas and gas"), ["gas"])
        self.assertEqual(tb.policy_words("soil and boilers"), ["boilers"])

    def test_the_run_reads_its_words_through_the_one_reader(self):
        with open(os.path.join(ROOT, "warehouse", "thesis", "run.py"), encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn('re.findall(r"[a-z]{5,}"', text)                    # line 883 as it was
        self.assertNotIn('re.findall(r"[a-z][a-z-]{3,}", text.lower())', text)      # lines 150 to 151 as they were


class ShortWordsAgainstTables(unittest.TestCase):
    """The two places the words are used: the warehouse's own candidates and the policy candidates."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.before = (R.TABLE_DIR, tb.TABLE_DIR)
        R.TABLE_DIR = tb.TABLE_DIR = self.dir.name
        write_table(self.dir.name, "energy_companies", ["name", "description", "niche_tags", "sector", "stage", "raised", "location", "founders", "website", "source_url"], [
            {"name": "Test Row One", "description": "Methane sensors for oil and gas wells", "sector": "oil and gas"},
            {"name": "Test Row Two", "description": "Soil moisture sensing for farms, boiling point", "sector": "agriculture"},
            {"name": "Test Row Three", "description": "Gas turbine inspection", "sector": "power"},
        ])
        write_table(self.dir.name, "energy_deals", ["event_id", "event_date", "deal_type", "parties", "asset", "technology", "state", "country", "dollars", "status", "source", "source_url"], [
            {"event_id": "test:1", "technology": "oil", "asset": "a test asset"},
            {"event_id": "test:2", "technology": "solar", "asset": "Las Vegas gasoline depot"},
        ])
        write_table(self.dir.name, "policy_actions", ["event_id", "agency", "action_type", "event_date", "title", "abstract", "sector_tags", "significance", "source_url"], [
            {"event_id": "test:p1", "title": "A test rule on gas flaring", "significance": "3"},
            {"event_id": "test:p2", "title": "A test rule on soil carbon and gasoline", "significance": "9"},
            {"event_id": "test:p3", "title": "A test order on EV charging", "abstract": "development of chargers", "significance": "5"},
            {"event_id": "test:p4", "title": "A test notice on project development", "significance": "8"},
        ])

    def tearDown(self):
        R.TABLE_DIR, tb.TABLE_DIR = self.before
        self.dir.cleanup()

    def test_the_warehouse_candidates_of_an_oil_and_gas_niche(self):
        r = Quiet()
        rows = R.warehouse_candidates("oil and gas", r, r)
        names = [row.get("name") or row.get("event_id") for _, _, row in rows]
        self.assertEqual(names, ["Test Row One", "test:1"])                  # "oil" as a whole word; not "soil", not "boiling"
        self.assertEqual(R.words_of(R.head_of("oil and gas")), ["oil", "gas"])

    def test_before_the_fix_the_niche_had_no_word_at_all(self):
        self.assertEqual(OLD(R.head_of("oil and gas")), [])                  # so warehouse_candidates returned [] at once
        self.assertEqual(OLD(R.head_of("oil & gas demand")), ["demand"])

    def test_gas_alone(self):
        r = Quiet()
        rows = R.warehouse_candidates("gas, US startups", r, r)
        self.assertEqual([row.get("name") or row.get("event_id") for _, _, row in rows], ["Test Row One", "Test Row Three"])

    def test_the_policy_candidates_match_whole_short_words(self):
        got = lambda words: sorted(tb.policy_candidates(words)["event_id"])      # noqa: E731
        self.assertEqual(got(tb.policy_words("oil & gas")), ["test:p1"])     # not "gasoline", not "soil"
        self.assertEqual(got(tb.policy_words("EV charging")), ["test:p3"])   # "ev" is not in "development"; "charging" is a long word
        self.assertEqual(got(["EV"]), ["test:p3"])
        self.assertEqual(got(["develop"]), ["test:p3", "test:p4"])           # a long word anywhere, as before


class FakeConn:
    """The internal table, as far as gate_of reads it: one select, answered from a dict (or an error)."""

    def __init__(self, rows=None, error=None):
        self.rows, self.error, self.asked = rows or {}, error, []

    def execute(self, sql, params=()):
        self.asked.append((sql, params))
        if self.error:
            raise self.error
        row = self.rows.get(params[0])
        return type("Cur", (), {"fetchone": lambda _self: None if row is None else (row,)})()


class RunAnyway(unittest.TestCase):
    """Part A on the runner's side: a forced run's report carries the flag, read as data; every other run has none."""

    def test_a_forced_run_is_flagged(self):
        stored = {"forced": True, "why": "sector_only", "topic": "oil_gas", "at": "2026-10-09T08:00:00.000Z"}
        conn = FakeConn({"r1": stored})
        self.assertEqual(R.gate_of(conn, "r1"), stored)
        self.assertEqual(conn.asked, [("select gate from public.thesis_runs where run_id = %s", ("r1",))])
        self.assertEqual(R.gate_of(FakeConn({"r1": '{"forced": true, "why": "few_words", "topic": null}'}), "r1"), {"forced": True, "why": "few_words", "topic": None, "at": ""})

    def test_a_run_that_passed_has_no_flag(self):
        self.assertIsNone(R.gate_of(FakeConn({"r1": None}), "r1"))
        self.assertIsNone(R.gate_of(FakeConn({}), "r2"))
        self.assertIsNone(R.gate_of(None, "r1"))                             # a run started on the command line, no table

    def test_a_database_without_the_column_flags_nothing(self):
        self.assertIsNone(R.gate_of(FakeConn(error=RuntimeError('column "gate" does not exist')), "r1"))

    def test_the_stored_gate_is_read_as_data(self):
        self.assertIsNone(R.gate_flag({"forced": "true"}))
        self.assertIsNone(R.gate_flag({"forced": False, "why": "sector_only"}))
        self.assertIsNone(R.gate_flag("not json"))
        self.assertIsNone(R.gate_flag([1, 2]))
        odd = R.gate_flag({"forced": True, "why": "<script>", "topic": "Oil & Gas", "at": "yesterday", "extra": "dropped"})
        self.assertEqual(odd, {"forced": True, "why": "open", "topic": None, "at": ""})
        self.assertEqual(R.gate_flag({"forced": True, "why": "command_line"}), {"forced": True, "why": "command_line", "topic": None, "at": ""})

    def test_the_runner_writes_the_flag_on_the_report(self):
        with open(os.path.join(ROOT, "warehouse", "thesis", "run.py"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn('report["gate"] = flag', text)
        self.assertIn('ap.add_argument("--run-anyway"', text)
        self.assertEqual(R.main.__module__, R.__name__)


# ---------------------------------------------------------------------------------------------
# Part C: the market research is the ERW's; companies come from a connector
# ---------------------------------------------------------------------------------------------

SR = R.sr


class Usage:
    def __init__(self, i=100, o=50):
        self.input_tokens, self.output_tokens, self.cache_read_input_tokens, self.cache_creation_input_tokens, self.server_tool_use = i, o, 0, 0, None


class Block:
    def __init__(self, text):
        self.type, self.text = "text", text


class Resp:
    def __init__(self, obj):
        self.content, self.usage, self.stop_reason, self.model = [Block(json.dumps(obj))], Usage(), "end_turn", "stand-in"


class FakeClient:
    """Answers the three direct calls of the market run (series pick, writing, policy pick) with answers written for the test."""

    def __init__(self, answers):
        self.answers, self.asked = answers, []
        self.messages = self

    def create(self, **k):
        self.asked.append(k)
        name = next(n for n in self.answers if n in json.dumps(k["output_config"]["format"]["schema"]))
        return Resp(self.answers[name](k))


M1 = {"scope": {"definition": "Test niche: sensors that map heat underground, written for the test, 2 kinds.", "definition_sources": ["S1"],
                "in_scope": [{"item": "Test sensing hardware", "sources": ["S1"]}], "out_of_scope": [{"item": "Test drilling", "why": "written for the test"}],
                "sub_segments": [{"name": "Test segment", "what": "A sub-segment written for the test.", "sources": ["S1"]}],
                "definitions": [{"term": "Test term", "meaning": "A meaning written for the test.", "sources": ["S1"]}, {"term": "Unsourced", "meaning": "dropped", "sources": []}]},
      "trends": [{"title": f"Test trend {w}", "claim": f"The claim of trend {w}, written for the test.", "sources": ["S1"], "measure": "a test statistic"} for w in ("one", "two", "three", "four", "five")],
      "timing": {"stage": "being installed", "evidence": [{"text": "A pilot written for the test in 2025.", "sources": ["S1"]}]},
      "policy_fact": "No policy, written for the test."}
M2 = {"capital": {"fact": "", "fact_sources": [], "rounds": [{"date": "2025", "company": "Test Program", "kind": "grant", "amount": "12", "currency": "USD million",
                                                             "investors": "", "sources": ["S1"], "investors_spans": [], "date_span": ""}]},
      "incumbents": {"fact": "", "fact_sources": [], "players": [{"name": "Test Incumbent", "kind": "public company", "ticker": "", "metric": "Role in the niche", "value": "makes test sensors", "as_of": "", "sources": ["S1"]}]},
      "risks": {"risks": [{"risk": "A test risk", "how_it_breaks_the_thesis": "written for the test", "not_known": "", "sources": ["S1"]}]}}
SERIES = {"id": "eia:generation:GEO", "source": "EIA", "title": "geothermal (US net generation, geothermal, all sectors)", "unit": "thousand megawatthours", "freq": "annual",
          "url": "https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=annual", "retrieved": "2026-10-09",
          "points": [["2021", 15975.5], ["2022", 16087.0], ["2023", 16500.25]], "cut": False, "note": "EIA API v2"}      # values written for the test


class FakeR(R.Careful):
    """A Careful researcher with no client of its own: research and structure answer from the test's fixtures."""

    def __init__(self, client, cap=1.0):
        self.log, self.max_usd, self.cost, self.calls, self.searches = (lambda *_: None), cap, 0.0, 0, 0
        self.sources, self.erw, self.model, self.price, self.client = {}, [], "stand-in-sonnet", (2.0, 10.0), client
        self.guarded = []

    def guard(self, stage):
        self.guarded.append(stage)
        super().guard(stage)

    def charge(self, resp, what, model=None):
        self.calls += 1

    def research(self, what, system, prompt, max_searches, erw_tools=True, max_turns=24, model=None):
        self.research_args = {"model": model, "erw_tools": erw_tools, "max_searches": max_searches, "prompt": prompt}
        self.source("https://test.invalid/a", "A page written for the test", cited="2 kinds; 2025; 12 million; written for the test")
        return "notes written for the test [S1]"

    def structure(self, what, system, notes, schema, model=None):
        self.structure_models = getattr(self, "structure_models", []) + [model]
        return json.loads(json.dumps(M1 if "trends" in schema["properties"] else M2))


class MarketRun(unittest.TestCase):
    def setUp(self):
        self.real = (SR.pull, SR.catalog, R.tb.policy_candidates)
        SR.catalog = lambda table_dir, log=None: [dict(SR.BY_ID["eia:generation:GEO"])]
        SR.pull = lambda entry, count, table_dir=None, log=None, raw_dir=None: json.loads(json.dumps(SERIES))
        import pandas as pd
        R.tb.policy_candidates = lambda words: pd.DataFrame()
        self.client = FakeClient({
            "picks": lambda k: {"picks": [{"trend": 1, "series_id": "eia:generation:GEO", "why": "written for the test"}, {"trend": 2, "series_id": "not:in:catalog", "why": "x"},
                                          {"trend": 3, "series_id": "eia:generation:GEO", "why": "used twice"}]},
            "timing": lambda k: {"trends": [{"n": 1, "fact": "US geothermal generation was 16,500 thousand MWh in 2023, up from 15,976 in 2021."},
                                            {"n": 2, "fact": "The second trend grew by 99 percent."}], "timing": "The market is being installed: a pilot in 2025.",
                                 "capital": "A grant of 12 million.", "incumbents": "Test Incumbent makes test sensors."},
        })

    def tearDown(self):
        SR.pull, SR.catalog, R.tb.policy_candidates = self.real

    def run_it(self):
        r = FakeR(self.client)
        report, request, key, state = R.execute_market(r, "20261009T070000Z-test01", "Geothermal mapping and sensing", "", "US", lambda *_: None)
        return r, report, request, state

    def test_the_switch_is_off_and_the_old_run_is_kept(self):
        self.assertIs(R.COMPANY_SEARCH, False)
        self.assertTrue(callable(R.execute) and callable(R.tied_rows) and callable(R.select))      # kept whole, behind the switch
        self.assertEqual(R.RUN_USD, 1.0)
        self.assertEqual(R.SMALL, "claude-haiku-4-5")

    def test_no_company_is_searched_and_the_small_model_extracts(self):
        r, report, request, state = self.run_it()
        self.assertEqual(r.research_args["model"], R.SMALL)
        self.assertFalse(r.research_args["erw_tools"])
        self.assertIn("Do not search for lists of startups", r.research_args["prompt"])
        self.assertIn("never argues which company or approach will win", r.research_args["prompt"])
        self.assertEqual(r.structure_models, [R.SMALL, R.SMALL])
        models = [k["model"] for k in self.client.asked]
        self.assertEqual(models, [R.SMALL, "stand-in-sonnet"])                          # the pick on the small model, the writing on the run's
        self.assertEqual(r.guarded, ["market research", "market structure", "market structure rest", "series pick", "market write"])
        self.assertEqual(request["companies"], [])
        self.assertIn("This run names no company", request["paste_text"])
        self.assertIn("erw-pitchbook-1", request["paste_text"])
        self.assertFalse(state["company_search"])

    def test_the_report_keeps_every_key_and_empties_the_connector_tabs(self):
        _, report, _, _ = self.run_it()
        self.assertEqual(report["version"], 2)
        for k in ("sources", "scope", "trends", "landscape", "funnel", "pipeline", "capital", "incumbents", "risks", "policy", "timing", "connector_tabs"):
            self.assertIn(k, report)
        self.assertEqual((report["landscape"]["companies"], report["funnel"]["companies"], report["funnel"]["stages"], report["pipeline"]["companies"]), ([], [], [], []))
        self.assertEqual(report["connector_tabs"]["note"], "Connect PitchBook or Harmonic to fill this")
        self.assertEqual(report["connector_tabs"]["columns"]["landscape"], ["Company", "What it sells", "Founders", "Stage", "Raised", "Investors", "Founded", "Location", "Signal", "Source"])
        self.assertEqual(set(report["connector_tabs"]["columns"]), {"landscape", "funnel", "pipeline", "success", "investors"})
        self.assertEqual([d["term"] for d in report["scope"]["definitions"]], ["Test term"])      # an unsourced definition is left out
        self.assertEqual(report["scope"]["sub_segments"][0]["name"], "Test segment")
        self.assertEqual(report["timing"]["stage"], "being installed")

    def test_a_trend_is_drawn_only_with_a_real_series(self):
        _, report, _, state = self.run_it()
        t1, t2, t3 = report["trends"][:3]
        self.assertEqual(t1["chart"], {"kind": "line", "title": SERIES["title"], "category": 0, "values": [1], "unit": "thousand megawatthours"})
        self.assertEqual(t1["table"]["rows"], [["2021", "15975.5"], ["2022", "16087"], ["2023", "16500.25"]])      # as published, never rounded or filled
        self.assertEqual(t1["series"]["source_line"], "Source: U.S. Energy Information Administration (9 October 2026), geothermal (US net generation, geothermal, all sectors).")
        self.assertEqual(t1["series"]["url"], "https://www.eia.gov/opendata/browser/electricity/electric-power-operational-data")
        self.assertEqual(t1["no_series"], "")
        for t in (t2, t3):                                   # an id not in the catalog, and a series used twice, are none
            self.assertIsNone(t["series"])
            self.assertEqual(t["chart"]["kind"], "none")
            self.assertEqual(t["table"]["rows"], [])
            self.assertEqual(t["no_series"], R.NO_SERIES)
        self.assertEqual(state["picks"], {1: {"id": "eia:generation:GEO", "why": "written for the test"}})

    def test_the_literal_number_check_runs_on_the_written_text(self):
        _, report, _, _ = self.run_it()
        f1, f2 = report["trends"][0]["fact"]["text"], report["trends"][1]["fact"]["text"]
        self.assertEqual(f1, "US geothermal generation was 16,500 thousand MWh in 2023, up from 15,976 in 2021.")      # every number is in the series
        self.assertEqual(f2, "The claim of trend two, written for the test.")       # a written number no source holds: the cited claim stands instead
        self.assertEqual(report["trends"][2]["fact"]["text"], "The claim of trend three, written for the test.")      # no sentence written: the cited claim
        self.assertEqual(report["capital"]["fact"]["text"], "A grant of 12 million.")
        self.assertIn(report["trends"][0]["series"]["source_id"], report["trends"][0]["fact"]["sources"])

    def test_the_stages_fit_the_run_and_one_stops_before_it_starts(self):
        self.assertLessEqual(sum(R.MARKET_USD[k] for k in R.MARKET_STAGES), R.RUN_USD)
        r = FakeR(self.client, cap=0.30)
        with self.assertRaises(R.tb.Budget):
            R.execute_market(r, "20261009T070000Z-test02", "Geothermal mapping and sensing", "", "", lambda *_: None)
        self.assertEqual(r.guarded, ["market research"])


class CarefulCharge(unittest.TestCase):
    """Session 169's first paid run failed here: the careful researcher's charge did not take the call's model."""

    def test_a_call_on_another_model_is_charged_at_its_price(self):
        r = R.Careful.__new__(R.Careful)
        r.log, r.max_usd, r.cost, r.calls, r.searches, r.model, r.price = (lambda *_: None), 1.0, 0.0, 0, 0, "claude-sonnet-5-5", (2.0, 10.0)
        r.charge(Resp({}), "a call on the small model", "claude-haiku-4-5")      # 100 in, 50 out at USD 1 and 5 a million
        self.assertAlmostEqual(r.cost, (100 * 1.0 + 50 * 5.0) / 1e6)
        r.charge(Resp({}), "a call on the run's model")
        self.assertAlmostEqual(r.cost, (100 * 1.0 + 50 * 5.0) / 1e6 + (100 * 2.0 + 50 * 10.0) / 1e6)
        self.assertEqual(r.calls, 2)


class SeriesModule(unittest.TestCase):
    def test_the_contact_string_and_no_key_in_an_address(self):
        self.assertEqual(SR.UA, "ERW research project, github.com/SamuelEnrique/erw")
        self.assertEqual(SR.redact("https://api.eia.gov/v2/x/?a=1&api_key=SECRET&b=2"), "https://api.eia.gov/v2/x/?a=1&api_key=<key>&b=2")

    def test_the_ceiling_stops_before_the_request(self):
        c = SR.Count(None, ceiling=1)
        c.take("https://api.eia.gov/robots.txt")
        with self.assertRaises(SR.Ceiling):
            c.take("https://api.eia.gov/v2/")
        self.assertEqual(c.n["requests"], 1)

    def test_only_the_named_publishers_and_the_left_ones_are_said(self):
        self.assertEqual({e["source"] for e in SR.OUTSIDE}, {"EIA", "FRED"})      # session 175: FRED through fredgraph.csv
        self.assertEqual(set(SR.LEFT), {"BLS", "Census"})      # session 175: FRED is read through fredgraph.csv
        self.assertTrue(all(e["route"].startswith("https://api.eia.gov/v2/") for e in SR.OUTSIDE if e["source"] == "EIA"))      # session 175: FRED entries have no route

    def test_a_series_is_described_with_every_value(self):
        d = SR.describe(dict(SERIES))
        for v in ("2021: 15975.5", "2023: 16500.2", "3 values"):
            self.assertIn(v, d)
        self.assertNotIn("e+", SR.describe(dict(SERIES, points=[["1936", 392528.0], ["2024", 335163.0]])))

    def test_the_warehouse_catalog_skips_cleanly_without_the_tables(self):
        self.assertEqual(SR.warehouse_catalog(None), [])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(SR.warehouse_catalog(tmp), [])


if __name__ == "__main__":
    unittest.main()
