"""Session 135: Thesis Builder as a tool of the site. The stated query plan, the coded selection rule, the report's
shape, the PitchBook request, and the walls around the run: an internal table, no public table written, the method
kept off everything a reader receives. No model call and no database: the pipeline's pure parts are exercised."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "thesis"))
import run as R  # noqa: E402
import build as tb  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


TRENDS = [{"title": f"Trend {i}", "search_phrases": [f"phrase {i} a", f"phrase {i} b"]} for i in range(1, 6)]


def org(name, **kw):
    o = dict(name=name, website="", description="", kind="private company", country="United States", location="Reno, Nevada",
             founders="", stage="Seed", raised="", signal="", fits_stage="yes", trends=[1], trend_reason="It maps heat.",
             tam="", sources=["S1"], found_by=["Q1"], independent_sources=2, latest_source_year="2026", stage_primary=True, raised_primary=False)
    o.update(kw)
    return o


class Plan(unittest.TestCase):
    def test_six_niche_queries_and_two_a_trend_in_a_fixed_order(self):
        plan = R.query_plan("geothermal mapping and sensing, the technologies (imaging)", "United States", TRENDS)
        self.assertEqual([p[0] for p in plan], [f"Q{i}" for i in range(1, 17)])
        self.assertTrue(all(p[1].startswith("geothermal mapping and sensing ") for p in plan[:6]))
        self.assertEqual([p[2] for p in plan[6:]], [f"trend {i}" for i in range(1, 6) for _ in (0, 1)])
        self.assertIn("phrase 3 a", plan[10][1])
        self.assertIn("phrase 3 b", plan[11][1])

    def test_the_same_inputs_give_the_same_plan(self):
        a = R.query_plan("battery storage software", "", TRENDS)
        self.assertEqual(a, R.query_plan("battery storage software", "", TRENDS))
        self.assertFalse(any("United States" in q for _, q, _ in a))

    def test_a_trend_without_phrases_uses_its_title(self):
        plan = R.query_plan("x niche", "", [{"title": "Cheaper drilling", "search_phrases": []}])
        self.assertIn("Cheaper drilling startup", plan[6][1])


class Geography(unittest.TestCase):
    def test_the_united_states(self):
        self.assertIs(R.geo_fits("United States", "United States", ""), True)
        self.assertIs(R.geo_fits("US", "Canada", "Calgary, Alberta"), False)
        self.assertIs(R.geo_fits("United States", "not stated", "Houston, Texas, USA"), True)
        self.assertIs(R.geo_fits("United States", "", "Salt Lake City, Utah"), True)

    def test_what_the_sources_do_not_say_is_not_guessed(self):
        self.assertIsNone(R.geo_fits("US", "", ""))
        self.assertIsNone(R.geo_fits("US", "not stated", "not disclosed"))
        self.assertIsNone(R.geo_fits("US", "", "Calgary"))

    def test_no_geography_asked_for_fits_everything(self):
        self.assertIs(R.geo_fits("", "Iceland", "Reykjavik"), True)


class Selection(unittest.TestCase):
    def rows(self, orgs, stage="startups", geo="United States"):
        return {o["name"]: o for o in R.select(orgs, stage, geo, 5, {"S1", "S2", "E1"})}

    def test_each_stage_of_the_funnel_and_its_reason(self):
        r = self.rows([
            org("On the map"),
            org("Listed Co", kind="public company"),
            org("Lab", kind="university or national laboratory"),
            org("Abroad", country="Iceland", location="Reykjavik"),
            org("Nowhere", country="not stated", location=""),
            org("Too late", fits_stage="no"),
            org("No trend", trends=[], trend_reason=""),
            org("No reason", trend_reason=" "),
            org("No source", sources=["S99"]),
        ])
        self.assertEqual(r["On the map"]["reached"], "pipeline")
        self.assertEqual((r["Listed Co"]["reached"], r["Lab"]["reached"]), ("found", "found"))
        self.assertIn("not a private company", r["Listed Co"]["stopped"])
        self.assertEqual(r["Abroad"]["reached"], "private")
        self.assertIn("outside the geography", r["Abroad"]["stopped"])
        self.assertIn("no fetched source gives its location", r["Nowhere"]["stopped"])
        self.assertIn("outside the stage", r["Too late"]["stopped"])
        self.assertEqual(r["No trend"]["reached"], "fits")
        self.assertIn("ties it to one of the five trends", r["No trend"]["stopped"])
        self.assertEqual(r["No reason"]["reached"], "fits")
        self.assertIn("no fetched source is cited", r["No source"]["stopped"])

    def test_a_trend_number_outside_the_five_does_not_count(self):
        r = self.rows([org("A", trends=[0, 6, 9])])
        self.assertEqual(r["A"]["reached"], "fits")

    def test_the_pipeline_takes_confidence_60_or_more_most_trends_first_and_at_most_ten(self):
        weak = org("Weak", independent_sources=1, latest_source_year="2019", stage_primary=False)
        many = [org(f"Co {i:02d}", trends=[1, 2] if i < 3 else [1]) for i in range(14)]
        r = self.rows(many + [weak])
        self.assertEqual(r["Weak"]["reached"], "trend")
        self.assertIn("confidence under 60", r["Weak"]["stopped"])
        on = [n for n, o in r.items() if o["reached"] == "pipeline"]
        self.assertEqual(len(on), 10)
        self.assertTrue({"Co 00", "Co 01", "Co 02"} <= set(on))
        self.assertIn("beyond the 10", r["Co 13"]["stopped"])

    def test_the_same_company_twice_is_one_row(self):
        r = R.select([org("Zanskar Geothermal & Minerals, Inc."), org("Zanskar Geothermal & Minerals", sources=["S1", "S2"])], "", "", 5, {"S1", "S2"})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["sources"], ["S1", "S2"])

    def test_the_rule_does_not_depend_on_the_order_found(self):
        a = [org(f"Co {i}", trends=[1, 2] if i % 2 else [3]) for i in range(8)]
        one = {o["name"]: o["reached"] for o in R.select(a, "", "", 5, {"S1"})}
        two = {o["name"]: o["reached"] for o in R.select(list(reversed(a)), "", "", 5, {"S1"})}
        self.assertEqual(one, two)


class Reader(unittest.TestCase):
    """What a reader receives says nothing of how the work is done."""

    def test_the_confidence_line_is_plain_and_holds_no_arithmetic(self):
        note = R.confidence_note(org("A"))
        self.assertEqual(note, "2 independent sources, the latest from 2026; its stage is confirmed by the company or an investor.")
        for o in (org("A"), org("B", independent_sources=0, latest_source_year="", stage_primary=False)):
            self.assertIsNone(re.search(r"point|score|\+|\d+ for|weight|x \d", R.confidence_note(o)))

    def test_sourcing_names_the_kind_of_source_and_never_a_query(self):
        plan = R.query_plan("geothermal mapping", "United States", TRENDS)
        s = R.sourcing_of(org("A", found_by=["Q4", "Q9", "E3"]), plan)
        self.assertEqual(s, ["Web search: federal awards", "Web search: trend 2", "ERW companies and deals tables"])
        for _, q, _ in plan:
            self.assertNotIn(q, " ".join(s))

    def test_the_readers_method_note_holds_no_plan_prompt_or_scoring(self):
        note = src("docs", "methods", "thesis.md")
        for words in ("20 points", "10 points", "points", "prompt", "query plan", "DOE OR ARPA-E", "three agentic passes", "max_uses", "Sonnet", "USD"):
            self.assertNotIn(words, note, words)
        for words in ("A number is written only if it appears in a fetched source", "PitchBook pending", "labeled \"PitchBook\"", "not published"):
            self.assertIn(words, note, words)
        self.assertNotIn(chr(0x2014), note)

    def test_the_internal_method_note_is_not_published_on_the_site(self):
        build = src("site", "scripts", "build-content.mjs")
        self.assertIn("thesis_builder", build)
        self.assertRegex(build, r"INTERNAL_METHODS[^\n]*thesis_builder")

    def test_a_missing_cell_is_a_placeholder_with_its_reason(self):
        class Rr:
            def texts_of(self, ids):
                return ["Zanskar raised $115 million in a Series C round in 2026."]
        log = lambda s: None
        self.assertEqual(R.cell("not disclosed", Rr(), ["S1"], log, "x"), {"missing": "not_disclosed", "note": R.NOTE["not_disclosed"]})
        self.assertEqual(R.cell("", Rr(), ["S1"], log, "x")["missing"], "not_disclosed")
        self.assertEqual(R.cell("$115 million", Rr(), ["S1"], log, "x"), "$115 million")
        self.assertEqual(R.cell("$240 million", Rr(), ["S1"], log, "x")["missing"], "not_confirmed")


class PitchBook(unittest.TestCase):
    def request(self):
        orgs = R.select([org("Zanskar (Zanskar Geothermal & Minerals)", website="https://zanskar.us"), org("Listed Co", kind="public company")], "", "", 5, {"S1"})
        return R.pitchbook_request("20261006T200000Z-abc123", "geothermal mapping and sensing, the technologies", "United States", orgs, TRENDS, "k" * 43)

    def test_the_request_names_the_companies_the_lookups_and_a_discovery_search(self):
        q = self.request()
        self.assertEqual(q["format"], "erw-pitchbook-1")
        self.assertEqual([c["name"] for c in q["companies"]], ["Zanskar"])          # the public company is not asked for
        self.assertEqual(len(q["companies"][0]["lookups"]), 5)
        self.assertEqual(q["discover"]["hq"], "United States")
        self.assertEqual(q["discover"]["keywords"][0], "geothermal mapping and sensing")

    def test_the_paste_text_carries_the_run_the_key_and_the_return_format(self):
        t = self.request()["paste_text"]
        for words in ("Run: 20261006T200000Z-abc123", "Key: " + "k" * 43, '"format": "erw-pitchbook-1"', '"found": false', "1. Zanskar (https://zanskar.us)",
                      "report only what PitchBook shows", "do not estimate", "additional_companies", "millions of US dollars"):
            self.assertIn(words, t, words)
        block = t.split("```json")[1].split("```")[0]
        self.assertEqual(json.loads(block)["run_id"], "20261006T200000Z-abc123")
        self.assertNotIn(chr(0x2014), t)

    def test_the_request_holds_no_trend_text_score_or_plan(self):
        q = json.dumps(self.request())
        for words in ("confidence", "score", "Q1", "DOE OR"):
            self.assertNotIn(words, q, words)


class Walls(unittest.TestCase):
    def test_the_table_is_internal(self):
        sql = src("warehouse", "supabase", "migrations", "024_thesis.sql")
        self.assertIn("alter table public.thesis_runs enable row level security;", sql)
        self.assertIn("revoke all on public.thesis_runs from public, anon, authenticated;", sql)
        self.assertNotIn("create policy", sql.lower())
        for fn in ("thesis_submit", "thesis_list", "thesis_get"):
            body = sql.split(f"function public.{fn}(")[1].split("$$;")[0]
            self.assertIn("thesis_token_ok(p_token)", body, fn)
        accept = sql.split("function public.thesis_pitchbook_accept(")[1].split("$$;")[0]
        self.assertIn("pitchbook_key = null", accept)                # one time
        self.assertIn("r.pitchbook_key <> p_key", accept)
        self.assertNotIn("usd", sql.split("function public.thesis_get(")[1].split("$$;")[0])    # the spend is the owner's, not the page's

    def test_the_table_is_in_no_live_set_and_no_download(self):
        self.assertNotIn("thesis_runs", src("warehouse", "supabase", "live_set.yaml"))
        self.assertNotIn("thesis_runs", src("warehouse", "redivis", "config.yaml"))

    def test_a_run_writes_no_public_table_and_no_site_file(self):
        code = src("warehouse", "thesis", "run.py")
        body = code.split('"""', 2)[2]
        for words in ("merge_companies", "write_book", "energy_companies.csv", "os.path.join(ROOT, \"site\"", "os.path.join(ROOT, \"docs\"", "redivis"):
            self.assertNotIn(words, body, words)

    def test_the_workflow_runs_only_when_asked(self):
        wf = src(".github", "workflows", "thesis.yml")
        trigger = wf.split("\non:")[1].split("\npermissions:")[0]
        self.assertNotIn("schedule", trigger)
        self.assertNotIn("cron", trigger)
        self.assertIn("workflow_dispatch", wf)
        self.assertIn("contents: read", wf)
        self.assertNotIn("git push", wf)

    def test_the_spending_stops(self):
        self.assertLessEqual(R.RUN_USD, 2.0)
        self.assertLessEqual(R.DAY_USD, 8.0)
        sql = src("warehouse", "supabase", "migrations", "024_thesis.sql")
        self.assertIn("p_per_day integer default 6", sql)

    def test_no_em_dash_in_the_new_files(self):
        for parts in (("warehouse", "thesis", "run.py"), ("warehouse", "thesis", "eval", "stability.py"), ("warehouse", "supabase", "migrations", "024_thesis.sql"),
                      (".github", "workflows", "thesis.yml"), ("docs", "methods", "thesis.md")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


class Spending(unittest.TestCase):
    """The run of 6 October that paid for every stage and was then thrown away must not happen again."""

    def researcher(self, cost, cap):
        r = R.Careful.__new__(R.Careful)
        r.cost, r.max_usd, r.lines = cost, cap, []
        r.log = r.lines.append
        return r

    def test_a_stage_that_does_not_fit_is_refused_before_it_is_paid_for(self):
        r = self.researcher(0.50, 1.11)
        with self.assertRaises(tb.Budget) as e:
            r.guard("landscape")
        self.assertIn("not started", str(e.exception))
        self.researcher(0.40, 1.11).guard("landscape")       # fits: no exception

    def test_a_paid_answer_is_never_discarded(self):
        r = self.researcher(1.20, 1.11)
        parent = tb.Researcher.charge
        tb.Researcher.charge = lambda self, resp, what: (_ for _ in ()).throw(tb.Budget("over"))
        try:
            r.charge(object(), "structure (landscape)")           # must not raise
        finally:
            tb.Researcher.charge = parent
        self.assertIn("the answer is kept", r.lines[0])

    def test_every_stage_asks_first(self):
        code = src("warehouse", "thesis", "run.py")
        body = code.split("def execute(")[1].split("\ndef ")[0]
        self.assertEqual(body.count("r.guard("), 7)
        self.assertEqual(body.count("r.research(") + body.count("r.structure(") + body.count("r.structure_groups("), 7)
        self.assertIn("r = Careful(log, cap)", code)


class Stability(unittest.TestCase):
    def test_overlap_of_runs(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "thesis", "eval"))
        import stability as st
        c = st.compare([{"a", "b", "c"}, {"a", "b", "d"}, {"a", "b", "c"}])
        self.assertEqual((c["counts"], c["core"], c["union"]), ([3, 3, 3], 2, 4))
        self.assertEqual(c["jaccard"], [0.5, 1.0, 0.5])
        self.assertEqual(c["mean_jaccard"], 0.667)


if __name__ == "__main__":
    unittest.main()
