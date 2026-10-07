"""Session 142: the tie of a company to a trend is a rule in code (warehouse/thesis/tie.py), not a model's opinion.

On saved real evidence of the session's runs (tests/fixtures/session142/evidence.json, cut down to a few companies):
the scoring redone by hand, the tie-break, the same evidence giving the same landscape twice in the same order, the
rule for duplicate names, what a change of evidence does and how the run's record names it, that nothing a reader
receives holds the rule's mechanics, and that a stage that does not fit under the ceiling is refused before it
starts. No model call and no database.
"""
import copy
import importlib.util
import json
import os
import random
import re
import sys
import tempfile
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_LEDGER_BEFORE = []


def setUpModule():
    """The ledger is off while this module's tests run and is put back after them: set at import it stayed off for
    the whole suite, and session 30's ledger test, which runs later, recorded nothing (the first push of this session
    failed its checks on that; session 36A met the same fault)."""
    _LEDGER_BEFORE.append(os.environ.get("ERW_LEDGER"))
    os.environ["ERW_LEDGER"] = "0"


def tearDownModule():
    old = _LEDGER_BEFORE.pop()
    if old is None:
        os.environ.pop("ERW_LEDGER", None)
    else:
        os.environ["ERW_LEDGER"] = old


def load(name, *parts):
    """By path, under a name of its own: the suite already holds other modules named run and build."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


R = load("erw_thesis_run", "warehouse", "thesis", "run.py")
tie, tb = R.tie, R.tb
FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "session142", "evidence.json"), encoding="utf-8"))
NICHE, TRENDS = FIX["store"]["niche"], FIX["trends"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def judged(store=None, warehouse=None, read="pages"):
    """Session 147: the rule's web tier reads saved pages. This fixture was cut before any page was saved, so by the
    rule as it now stands its quoted sentences decide nothing; read="quotes" is session 142's reading, kept in tie.py
    for comparison, and the by-hand cases below that rest on a quotation ask for it by name."""
    return tie.judge(store if store is not None else copy.deepcopy(FIX["store"]), warehouse if warehouse is not None else FIX["warehouse"], NICHE, TRENDS, read=read)


def by_name(rows):
    return {c["name"]: c for c in rows}


class Saved:
    """A researcher that holds sources and makes no call."""

    def __init__(self):
        self.sources, self.erw = {}, []

    source = tb.Researcher.source
    texts_of = tb.Researcher.texts_of


def report_of(store_path=None):
    """The report a reader receives, from the fixture's evidence, by the run's own path after the model's calls."""
    r = Saved()
    for url, s in FIX["store"]["sources"].items():
        r.source(url, s["title"], s.get("page_age", ""))
    last = FIX["store"]["rows"][-1]["run_id"]
    orgs = []
    ids = {s["url"]: s["id"] for s in r.sources.values()}
    for x in FIX["store"]["rows"]:
        if x["run_id"] != last:
            continue
        o = dict(x["row"], independent_sources=1, tam="")
        o["sources"] = [ids[u] for u in x["row"]["source_urls"] if u in ids]
        o["evidence"] = [{"quote": q["text"], "source": ids[q["address"]]} for q in FIX["store"]["quotes"] if q["key"] == x["key"] and q["address"] in ids]
        orgs.append(o)
    land = {"fact": "", "fact_sources": [], "organisations": orgs}
    a = {"scope": {"definition": "", "definition_sources": [], "value_chain": [], "excluded": [], "definitions": []},
         "trends": [dict(t, fact="", table={"columns": [], "rows": []}, chart={"kind": "none", "title": "", "category_column": 0, "value_columns": []}, unit="", sources=[]) for t in TRENDS]}
    log = lambda s: None
    real = R.warehouse_rows
    R.warehouse_rows = lambda: FIX["warehouse"]
    try:
        rows, ctx = R.tied_rows(r, "test-run", NICHE, FIX["store"]["stage"], FIX["store"]["geography"], TRENDS, land, store_path, log)
        report, placed = R.build_report(NICHE, FIX["store"]["stage"], FIX["store"]["geography"], r, a, dict(land, organisations=rows), {}, None, R.query_plan(NICHE, "United States", TRENDS), log)
        tied = R.tie_done(ctx, placed, log)
    finally:
        R.warehouse_rows = real
    request = R.pitchbook_request("20261007T000000Z-abc123", NICHE, FIX["store"]["geography"], placed, TRENDS, "k" * 43)
    return report, placed, tied, request


class Terms(unittest.TestCase):
    def test_a_trends_own_terms_come_from_its_title_and_phrases(self):
        t = {"title": "AI prospecting for blind geothermal systems", "search_phrases": ["AI geothermal exploration", "blind geothermal discovery"]}
        terms, phrases = tie.trend_terms("Geothermal mapping and sensing, the technologies", t)
        self.assertEqual(terms, ["ai", "prospecting", "blind", "exploration", "discovery"])       # no "geothermal" (the niche's), no "systems" (too general)
        self.assertEqual([p for p, _ in phrases], ["AI geothermal exploration", "blind geothermal discovery"])

    def test_a_short_word_counts_only_in_capitals_and_plurals_fold(self):
        terms, _ = tie.trend_terms("x niche", {"title": "DOE grants and the das tests", "search_phrases": []})
        self.assertEqual(terms, ["doe", "grant", "test"])

    def test_a_sentence_supports_a_trend_with_two_terms_or_a_whole_phrase(self):
        terms, phrases = tie.trend_terms(NICHE, TRENDS[0])
        self.assertEqual(tie.support("It uses AI to find heat.", terms, phrases), (["ai"], ""))
        m, p = tie.support("An AI-led exploration company.", terms, phrases)
        self.assertEqual((m, p), (["ai", "exploration"], ""))
        m, p = tie.support("AI-powered geothermal exploration in Nevada.", terms, phrases)
        self.assertEqual(p, "AI geothermal exploration")

    def test_a_word_of_the_companys_own_name_is_not_a_term_for_it(self):
        terms, phrases = tie.trend_terms(NICHE, TRENDS[2])
        self.assertIn("resource", terms)
        self.assertEqual(tie.support("AlterG Resources won a DOE award.", terms, phrases, own={"alterg", "resource"})[0], ["doe"])

    def test_the_points(self):
        self.assertEqual(tie.TIERS, {"warehouse": 3, "fetched": 2, "web": 1})
        self.assertEqual(tie.TIER_ORDER, ["warehouse", "fetched", "web"])
        self.assertEqual((tie.MIN_TERMS, tie.STRONG_TERMS, tie.STRONG_POINT, tie.TIE_MIN, tie.MAX_ADDRESSES), (2, 3, 1, 2, 3))


class Names(unittest.TestCase):
    def test_eden_and_eden_geopower_are_one_company_under_its_longest_name(self):
        c = tie.clusters([("Eden", ""), ("Eden GeoPower", "edengeopower.com")], ["geothermal", "mapping", "sensing"])
        self.assertEqual(c["eden"], ("eden geopower", "Eden GeoPower"))
        self.assertEqual(c["eden geopower"], ("eden geopower", "Eden GeoPower"))

    def test_generic_last_words_do_not_make_two_companies(self):
        c = tie.clusters([("Zanskar", ""), ("Zanskar Geothermal & Minerals, Inc.", ""), ("Quaise", ""), ("Quaise Energy", "")], ["geothermal"])
        self.assertEqual(len(set(c.values())), 2)
        self.assertEqual(c["zanskar"][1], "Zanskar Geothermal & Minerals, Inc.")

    def test_a_short_name_that_leads_two_different_companies_is_merged_with_none(self):
        c = tie.clusters([("Terra", ""), ("Terra Watts", ""), ("Terra Reach", "")], [])
        self.assertEqual(len(set(c.values())), 3)

    def test_different_websites_keep_two_names_apart(self):
        c = tie.clusters([("Eden", "eden.io"), ("Eden GeoPower", "edengeopower.com")], [])
        self.assertEqual(len(set(c.values())), 2)

    def test_names_of_generic_words_only_are_not_cut_down(self):
        self.assertEqual(tie.core_of("geothermal technologies", ["geothermal"]), "geothermal technologies")
        self.assertEqual(tie.core_of("zanskar geothermal minerals", ["geothermal"]), "zanskar")
        c = tie.clusters([("Geothermal Technologies", ""), ("Geothermal Radar", ""), ("Geothermal Strategy Partners", "")], ["geothermal"])
        self.assertEqual(len(set(c.values())), 3)

    def test_the_order_of_the_names_does_not_matter(self):
        names = [("Eden", ""), ("Eden GeoPower", ""), ("Quaise Energy", ""), ("Quaise", ""), ("Mazama Energy", ""), ("Sage Geosystems", "")]
        one = tie.clusters(names, ["geothermal"])
        for seed in range(5):
            random.Random(seed).shuffle(names)
            self.assertEqual(tie.clusters(names, ["geothermal"]), one)

    def test_the_key_is_the_builders(self):
        for x in FIX["store"]["rows"]:
            self.assertEqual(tie.name_key(x["row"]["name"]), tb.name_key(x["row"]["name"]))

    def test_a_one_word_name_needs_the_niche_beside_it(self):
        al = [("bedrock energy", "bedrock")]
        self.assertTrue(tie.names_it("Bedrock Energy raises a Series A", al, ["geothermal"]))
        self.assertTrue(tie.names_it("Bedrock brings geothermal to offices", al, ["geothermal"]))
        self.assertFalse(tie.names_it("Drilling through bedrock is slow", al, ["geothermal"]))


class Determinism(unittest.TestCase):
    def test_the_same_saved_evidence_gives_the_same_landscape_twice_in_the_same_order(self):
        one, two = judged(), judged()
        self.assertEqual(json.dumps(one, sort_keys=True), json.dumps(two, sort_keys=True))
        self.assertEqual([c["name"] for c in one], [c["name"] for c in two])

    def test_the_order_the_evidence_was_saved_in_does_not_matter(self):
        base = [(c["name"], c["trends"], c["tie"], c["tier"]) for c in judged()]
        for seed in range(6):
            s = copy.deepcopy(FIX["store"])
            rnd = random.Random(seed)
            rnd.shuffle(s["quotes"])
            rnd.shuffle(s["rows"])
            s["sources"] = dict(rnd.sample(sorted(s["sources"].items()), len(s["sources"])))
            wh = {k: rnd.sample(v, len(v)) for k, v in FIX["warehouse"].items()}
            self.assertEqual([(c["name"], c["trends"], c["tie"], c["tier"]) for c in judged(s, wh)], base, seed)

    def test_the_tie_break_is_score_then_tier_then_name(self):
        rows = judged()
        self.assertEqual(rows, sorted(rows, key=lambda c: (-c["tie"], tie.TIER_ORDER.index(c["tier"]) if c["tier"] else 3, c["key"])))
        mk = lambda key, t, tier: {"key": key, "tie": t, "tier": tier}
        order = sorted([mk("b co", 4, "web"), mk("a co", 4, "web"), mk("c co", 4, "fetched"), mk("z co", 7, "web"), mk("d co", 4, "warehouse"), mk("e co", 0, "")], key=tie.order_key)
        self.assertEqual([c["key"] for c in order], ["z co", "d co", "c co", "a co", "b co", "e co"])

    def test_the_funnel_and_the_report_follow_that_order(self):
        report, placed, _, _ = report_of()
        want = [c["name"] for c in judged() if c["trends"]]
        on = [o["name"] for o in sorted(placed, key=R.rank) if o["reached"] in ("trend", "pipeline")]
        self.assertEqual(on, [n for n in want if n in on])
        self.assertEqual([c["name"] for c in report["landscape"]["companies"]], [R.clean(n) for n in on])
        again, _, _, _ = report_of()
        self.assertEqual([c["name"] for c in again["landscape"]["companies"]], [c["name"] for c in report["landscape"]["companies"]])
        self.assertEqual([c["name"] for c in again["pipeline"]["companies"]], [c["name"] for c in report["pipeline"]["companies"]])


class Changes(unittest.TestCase):
    """A run differs from the one before only because a source was added, changed or disappeared, and its record says which."""

    def snap(self, store, warehouse=None, run="r"):
        rows = judged(store, warehouse)
        return tie.snapshot(run, rows, {c["key"]: ("trend" if c["trends"] else "fits", 60) for c in rows}), rows

    def test_no_change_of_evidence_no_change_of_landscape(self):
        s = copy.deepcopy(FIX["store"])
        a, _ = self.snap(s, run="a")
        b, _ = self.snap(copy.deepcopy(s), run="b")
        d = tie.diff(a, b)
        self.assertEqual((d["new_companies"], d["gone_companies"], d["moved"], d["evidence_changes"]), ([], [], [], 0))

    def test_a_warehouse_row_that_disappears_is_named(self):
        rows = judged()
        c = next(c for c in rows if c["tier"] == "warehouse")
        a, _ = self.snap(copy.deepcopy(FIX["store"]), run="a")
        wh = {"energy_companies": [x for x in FIX["warehouse"]["energy_companies"] if tie.name_key(x["name"]) not in c["aliases"]], "energy_deals": FIX["warehouse"]["energy_deals"]}
        b, after = self.snap(copy.deepcopy(FIX["store"]), wh, run="b")
        d = tie.diff(a, b)
        removed = [e for m in d["moved"] if m["name"] == c["name"] for e in m["removed"]]
        now = by_name(after)[c["name"]]
        if now["trends"] != c["trends"]:
            self.assertTrue(removed and all(e[0] == "warehouse" and e[1].startswith("erw:energy_companies/") for e in removed))
            self.assertTrue(all(m["explained"] for m in d["moved"]))
        self.assertGreater(d["evidence_changes"], 0)
        self.assertFalse(any(e["tier"] == "warehouse" and e["address"].startswith("erw:energy_companies/") for e in now["evidence"]))

    def test_a_new_source_ties_a_company_and_the_record_names_the_source(self):
        s = copy.deepcopy(FIX["store"])
        target = next(c for c in judged() if not c["trends"])
        a, _ = self.snap(copy.deepcopy(s), run="a")
        url = "https://example.org/a-page-added-by-this-test"
        s["sources"][url] = {"title": "t", "cited": [], "page_age": "", "fetched": "2026-10-07", "sha": "", "first_run": "b", "last_run": "b", "history": []}
        # session 147 (changed on purpose): the new source is a saved PAGE whose sentence names the company, not a sentence the model quoted
        sentence = f"TEST SENTENCE, NOT A SOURCE: {target['name']} of the geothermal trade runs a distributed acoustic sensing array on optic fiber for monitoring."
        s.setdefault("pages", {})[url] = {"state": "fetched", "status": 200, "truncated": False, "fetched": "2026-10-07", "text": "A heading of the page\n" + sentence}
        b, after = self.snap(s, run="b")
        d = tie.diff(a, b)
        m = next(m for m in d["moved"] if m["name"] == target["name"])
        self.assertEqual((m["from"], m["to"], m["trends_to"]), ("fits", "trend", [2]))
        self.assertEqual(m["added"], [["web", url, tie.sha(sentence)]])
        self.assertTrue(m["explained"])
        line = by_name(after)[target["name"]]["ties"][2]["lines"][0]
        self.assertEqual((line["tier"], line["points"], line["phrase"]), ("web", 2, "distributed acoustic sensing"))

    def test_a_fetched_title_that_changes_is_recorded(self):
        s = copy.deepcopy(FIX["store"])
        url, old = next((u, x["title"]) for u, x in sorted(s["sources"].items()) if x["title"])
        changed = tie.add_run(s, "later", "2026-10-08", [{"url": url, "title": old + " (updated)", "cited": [], "page_age": "", "retrieved": "2026-10-08"}], [])
        self.assertEqual(changed, [url])
        self.assertEqual(s["sources"][url]["history"][0]["title"], old)
        self.assertEqual(s["sources"][url]["fetched"], "2026-10-08")
        self.assertEqual(tie.add_run(s, "later 2", "2026-10-09", [{"url": url, "title": old + " (updated)", "cited": [], "page_age": "", "retrieved": "2026-10-09"}], []), [])

    def test_a_sentence_is_saved_once_with_its_address_hash_and_date(self):
        s = tie.empty_store()
        org = {"name": "Some Co", "kind": "private company", "source_urls": ["https://a.example/x"],
               "evidence": [{"quote": "It maps heat under the ground with fiber.", "address": "https://a.example/x"}, {"quote": "no address", "address": ""}, {"quote": "short", "address": "https://a.example/x"}]}
        tie.add_run(s, "one", "2026-10-07", [{"url": "https://a.example/x", "title": "A page", "cited": [], "page_age": "", "retrieved": "2026-10-07"}], [org])
        tie.add_run(s, "two", "2026-10-08", [], [org])
        self.assertEqual(len(s["quotes"]), 1)
        q = s["quotes"][0]
        self.assertEqual((q["address"], q["fetched"], q["first_run"], q["sha"]), ("https://a.example/x", "2026-10-07", "one", tie.sha("It maps heat under the ground with fiber.")))
        self.assertEqual(s["sources"]["https://a.example/x"]["sha"], tie.sha("A page"))

    def test_a_companys_first_saved_facts_stand_and_a_later_reading_is_a_disagreement_on_record(self):
        row = lambda seq, kind, urls, stage="", country="": {"key": "x", "seq": seq, "run_id": f"run {seq}", "row": {"name": "X", "kind": kind, "country": country, "location": "", "fits_stage": "", "stage": stage, "source_urls": urls}}
        r = tie.resolve([row(2, "university or national laboratory", ["b", "c", "d"]), row(1, "private company", ["a"])])
        self.assertEqual(r["kind"], "private company")                  # the model's later opinion, however many sources its row cites, moves nothing
        self.assertEqual(r["disagreements"], [{"field": "kind", "kept": "private company", "said": "university or national laboratory", "run_id": "run 2"}])
        self.assertEqual(tie.resolve([row(1, "private company", ["a"], "Seed"), row(2, "private company", ["a"], "Series A")])["stage"], "Seed")
        r = tie.resolve([row(1, "private company", ["a"]), row(2, "private company", ["b"], country="United States")])
        self.assertEqual((r["country"], r["disagreements"]), ("United States", []))      # a fact not yet stated is filled by a later run
        self.assertEqual(tie.resolve([row(1, "private company", ["a"])])["country"], "not stated")

    def test_a_company_that_gains_a_longer_name_is_the_same_company_in_the_record(self):
        mk = lambda key, name, aliases, ev: {key: {"name": name, "aliases": aliases, "reached": "found", "trends": [], "tie": 0, "facts": {}, "evidence": ev}}
        before = {"run_id": "a", "companies": mk("nrel", "NREL", ["nrel"], [["web", "https://x.example/1", "aa"]])}
        after = {"run_id": "b", "companies": mk("nrel national laboratory", "NREL National Laboratory", ["nrel", "nrel national laboratory"], [["web", "https://x.example/1", "aa"]])}
        d = tie.diff(before, after)
        self.assertEqual((d["new_companies"], d["gone_companies"], d["moved"], d["evidence_changes"]), ([], [], [], 0))


class Reader(unittest.TestCase):
    """Nothing a reader receives states the scoring, the points, the thresholds, the order of evidence or the tie-break."""

    MECHANICS = ("points", "tier", "threshold", "tie-break", "tie break", "MIN_TERMS", "TIE_MIN", "STRONG", "MAX_ADDRESSES", "warehouse first",
                 "order of evidence", "under 60", "60 or more", "at most ten", "the 10 ", "evidence store", "normalized name")

    def strings(self, x):
        if isinstance(x, dict):
            for k, v in x.items():
                yield from self.strings(k)
                yield from self.strings(v)
        elif isinstance(x, list):
            for v in x:
                yield from self.strings(v)
        elif isinstance(x, str):
            yield x

    def test_the_report_holds_none_of_the_rules_mechanics(self):
        report, _, _, _ = report_of()
        self.assertTrue(report["landscape"]["companies"], "the fixture puts no company on the landscape")
        own = [t for c in judged() for e in c["evidence"] for t in [e["text"]]]             # a source's own words may hold any word
        for s in self.strings(report):
            if any(s.strip('"') in t or t in s for t in own):
                continue
            for w in self.MECHANICS:
                self.assertNotIn(w.lower(), s.lower(), (w, s[:120]))

        def keys(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    yield k
                    yield from keys(v)
            elif isinstance(x, list):
                for v in x:
                    yield from keys(v)
        for k in ("tie", "tier", "tier_rank", "ties", "evidence", "model_trends", "terms", "phrase", "trace", "diff", "aliases"):
            self.assertNotIn(k, set(keys(report)), k)

    def test_a_company_row_carries_only_what_the_page_draws(self):
        report, _, _, _ = report_of()
        self.assertEqual(set(report["landscape"]["companies"][0]), {"name", "website", "description", "founders", "stage", "raised", "location", "signal", "trends", "reason", "sources", "confidence", "confidence_note", "sourcing"})
        self.assertEqual(set(report["funnel"]["companies"][0]), {"name", "reached", "stopped", "score", "sourcing", "sources"})
        self.assertEqual(set(report["landscape"]), {"fact", "rule", "companies"})

    def test_why_a_company_is_here_is_a_sources_own_sentence(self):
        report, _, _, _ = report_of()
        texts = {e["text"].strip().rstrip(".") for c in judged() for e in c["evidence"]}
        for c in report["landscape"]["companies"]:
            m = re.match(r'^"(.*)" \((.+)\)', c["reason"])
            self.assertIsNotNone(m, c["reason"])
            self.assertTrue(any(R.clean(t) == m.group(1) or R.clean(t) in c["reason"] for t in texts), c["reason"])
            self.assertTrue(c["sources"], c["name"])

    def test_a_reason_for_stopping_gives_no_number(self):
        orgs = [dict(name=f"Co {i:02d}", kind="private company", country="United States", location="Reno, Nevada", fits_stage="yes", trends=[1], trend_reason="x", sources=["S1"],
                     independent_sources=3, latest_source_year="2026", stage_primary=True, raised_primary=True, stage="Seed", raised="") for i in range(12)]
        orgs.append(dict(orgs[0], name="Weak", independent_sources=1, latest_source_year="2019", stage_primary=False, raised_primary=False))
        orgs.append(dict(orgs[0], name="No trend", trends=[], trend_reason=""))
        stopped = {o["stopped"] for o in R.select(orgs, "startups", "United States", 5, {"S1"}) if o["stopped"]}
        self.assertEqual(stopped, {"its confidence is too low for the pipeline map", "the pipeline map is full", "no fetched source ties it to one of the five trends"})
        for s in stopped | {R.RULE}:
            self.assertIsNone(re.search(r"\d", s), s)

    def test_the_line_above_the_landscape_says_what_the_map_is_and_no_more(self):
        for w in self.MECHANICS + ("score", "phrase", "sentence", "term"):
            self.assertNotIn(w.lower(), R.RULE.lower(), w)

    def test_the_pitchbook_request_is_as_it_was_and_holds_none_of_it(self):
        _, placed, _, q = report_of()
        self.assertEqual(set(q), {"format", "run_id", "companies", "discover", "paste_text"})
        self.assertEqual(q["format"], "erw-pitchbook-1")
        self.assertEqual(set(q["companies"][0]), {"name", "website", "lookups"})
        text = json.dumps(q)
        for w in self.MECHANICS + ("confidence", "score", "Q1"):
            self.assertNotIn(w.lower(), text.lower(), w)

    def test_the_readers_note_and_the_page_hold_none_of_it(self):
        files = [("docs", "methods", "thesis.md"), ("site", "components", "thesis", "Report.tsx"), ("site", "components", "thesis", "PitchbookPanel.tsx"),
                 ("site", "components", "thesis", "RunWatch.tsx"), ("site", "components", "thesis", "RunForm.tsx"), ("site", "app", "thesis", "page.tsx"), ("site", "lib", "thesis", "view.ts")]
        for parts in files:
            text = src(*parts).lower()
            for w in ("tie-break", "tie break", "min_terms", "tie_min", "order of evidence", "warehouse first", "evidence tier", "3 points", "2 points", "1 point", "evidence store", "under 60", "60 or more"):
                self.assertNotIn(w, text, (parts[-1], w))

    def test_the_rule_is_not_in_the_published_methods(self):
        for name in os.listdir(os.path.join(ROOT, "docs", "methods")):
            if name.endswith(".md") and name != "thesis_builder.md":          # thesis_builder.md is internal and not built into the site (session 135)
                text = src("docs", "methods", name)
                for w in ("tie.py", "TIE_MIN", "MIN_TERMS", "STRONG_TERMS"):
                    self.assertNotIn(w, text, (name, w))

    def test_no_em_dash_in_the_sessions_files(self):
        for parts in (("warehouse", "thesis", "tie.py"), ("warehouse", "thesis", "run.py"), ("warehouse", "thesis", "eval", "stability.py"), ("tests", "test_session142.py"),
                      ("tests", "fixtures", "session142", "evidence.json")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


class Spending(unittest.TestCase):
    """Session 135's lesson: a stage is refused before it starts when it does not fit; a paid answer is never thrown away."""

    def args(self, tmp, spent, cap=5.5, max_usd=1.4):
        json.dump({"usd": spent}, open(os.path.join(tmp, "spent.json"), "w"))
        return types.SimpleNamespace(max_usd=max_usd, spent_file=os.path.join(tmp, "spent.json"), session_cap=cap, landscape_from="saved.json", searches=8, retrend=False,
                                     landscape_only=False, state_dir=os.path.join(tmp, "state"), evidence_dir=os.path.join(tmp, "evidence"), no_evidence=False)

    def test_a_run_that_does_not_fit_under_the_sessions_stop_is_not_started(self):
        made, lines = [], []
        real = R.Careful
        R.Careful = lambda *a, **k: made.append(1) or (_ for _ in ()).throw(AssertionError("a researcher was made: a call could follow"))
        try:
            with tempfile.TemporaryDirectory() as tmp:
                need = R.STAGE_USD["landscape"] + R.STAGE_USD["structure landscape"]
                usd = R.one(None, "run-x", NICHE, "startups", "United States", self.args(tmp, 5.5 - need + 0.01), lines.append)
                self.assertEqual(usd, 0.0)
                self.assertEqual(json.load(open(os.path.join(tmp, "spent.json")))["usd"], round(5.5 - need + 0.01, 4))
        finally:
            R.Careful = real
        self.assertEqual(made, [])
        self.assertIn("not started", lines[-1])

    def test_a_stage_that_does_not_fit_is_refused_before_it_starts(self):
        r = R.Careful.__new__(R.Careful)
        r.cost, r.max_usd, r.log = 0.80, 1.10, lambda s: None
        with self.assertRaises(tb.Budget) as e:
            r.guard("structure landscape")
        self.assertIn("not started", str(e.exception))
        r.cost = 1.10 - R.STAGE_USD["structure landscape"]
        r.guard("structure landscape")                    # fits exactly: no exception
        self.assertGreaterEqual(R.STAGE_USD["structure landscape"], 0.26)

    def test_every_stage_still_asks_first_and_the_rule_makes_no_call(self):
        code = src("warehouse", "thesis", "run.py")
        body = code.split("def execute(")[1].split("\ndef ")[0]
        self.assertEqual(body.count("r.guard("), 7)
        self.assertEqual(body.count("r.research(") + body.count("r.structure(") + body.count("r.structure_groups("), 7)
        rule = src("warehouse", "thesis", "tie.py").split('"""', 2)[2]
        for w in ("anthropic", "llm", "requests", "urllib", "client", "import iso_prices", "pandas"):
            self.assertNotIn(w, rule, w)
        for fn in ("def tied_rows(", "def tie_done("):
            part = code.split(fn)[1].split("\ndef ")[0]
            for w in ("r.research(", "r.structure(", "r.client", "messages.create"):
                self.assertNotIn(w, part, (fn, w))

    def test_research_already_paid_for_is_kept_when_a_later_stage_is_refused(self):
        class Paid:
            def __init__(self, log, cap):
                self.cost, self.calls, self.searches, self.max_usd = 0.71, 1, 22, cap

        def execute(r, *a, **k):
            r.partial = {"run_id": "run-y", "notes_b": "the notes this run paid for"}
            raise tb.Budget("structure landscape needs up to USD 0.34 and USD 0.2900 is left; not started")
        real = R.Careful, R.execute
        R.Careful, R.execute = Paid, execute
        lines = []
        try:
            with tempfile.TemporaryDirectory() as tmp:
                usd = R.one(None, "run-y", NICHE, "startups", "United States", self.args(tmp, 0.0), lines.append)
                kept = json.load(open(os.path.join(tmp, "state", "partial_run-y.json"), encoding="utf-8"))
                self.assertEqual(kept["notes_b"], "the notes this run paid for")
                self.assertEqual(json.load(open(os.path.join(tmp, "spent.json")))["usd"], 0.71)
        finally:
            R.Careful, R.execute = real
        self.assertEqual(usd, 0.71)
        self.assertTrue(any("is kept" in s for s in lines))


class Stability(unittest.TestCase):
    def test_the_comparison_names_what_changed_and_what_is_not_explained(self):
        st = load("erw_thesis_stability", "warehouse", "thesis", "eval", "stability.py")
        mk = lambda rid, names, pipe, d=None: {"run_id": rid, "niche": "n", "funnel": [{"name": n, "reached": "pipeline" if n in pipe else "trend"} for n in names], "tie": {"diff": d} if d else None}
        d = {"new_companies": [{"name": "C Co", "reached": "trend", "evidence": [["web", "https://x.example/c", "abc"]]}], "gone_companies": [],
             "moved": [{"name": "B Co", "from": "fits", "to": "trend", "trends_from": [], "trends_to": [2], "added": [["fetched", "https://x.example/b", "def"]], "removed": [], "facts": {}, "explained": True},
                       {"name": "D Co", "from": "trend", "to": "fits", "trends_from": [1], "trends_to": [], "added": [], "removed": [], "facts": {}, "explained": False}]}
        lines = st.explain([mk("1", ["A Co"], ["A Co"]), mk("2", ["A Co", "B Co", "C Co"], ["A Co"], d)])
        self.assertIn("run 2: NEW C Co", lines[0])
        self.assertIn("added fetched https://x.example/b [def]", lines[1])
        self.assertTrue(lines[2].endswith("NOT EXPLAINED"))
        self.assertEqual(st.pipeline_of(mk("1", ["Alpha Geo", "Beta Geo"], ["Alpha Geo"])), {"alpha geo"})


class ByHand(unittest.TestCase):
    """The scoring redone by hand from the saved sentences. Each case: the company, the trend, and for every line that
    counts its tier, its address, the terms a reader finds in the sentence, and its points; then the sum."""

    CASES = [
        # Zanskar, trend 1: the warehouse's own row (3) holding a whole phrase (+1), and two fetched titles (2 each), each holding a whole phrase (+1): 4 + 3 + 3
        ("Zanskar Geothermal & Minerals", 1, [
            ("warehouse", "erw:energy_companies/Zanskar Geothermal & Minerals", ["ai", "exploration"], "AI geothermal exploration", 4),
            ("fetched", "https://baytobaynews.com/daily-state-news/stories/zanskar-reveals-big-blind-the-discovery-of-the-first-blind-geothermal-system-in-the-us-by,275569",
             ["blind", "discovery"], "blind geothermal discovery", 3),
            ("fetched", "https://energynews.pro/en/zanskar-raises-115m-to-accelerate-ai-powered-geothermal-exploration-in-the-united-states", ["ai", "exploration"], "AI geothermal exploration", 3)], 10, True),
        # XGS Energy, trend 3: a reported sentence (1) with four terms and a whole phrase (+1), and a second reported sentence from another address with two terms (1)
        ("XGS Energy", 3, [
            ("web", "https://renewablesnow.com/news/xgs-tapped-for-doe-funding-for-geothermal-drilling-project-in-new-mexico-1302041/", ["grant", "doe", "field", "test"], "DOE geothermal field tests", 2),
            ("web", "https://energycapitalhtx.com/fervo-quaise-xgs-geothermaldoe-funding", ["field", "test"], "", 1)], 3, True),
        # Geothermal Radar, trend 4: one reported sentence (1), strong by its three terms and its whole phrase (+1)
        ("Geothermal Radar", 4, [("web", "https://venturewell.org/rose-rock-ascend-2024/", ["modeling", "assessment", "digital"], "geothermal digital modeling", 2)], 2, True),
        # Thermofilic, trend 4: one reported sentence (1), strong by three terms (+1), no phrase
        ("Thermofilic", 4, [("web", "https://bizwest.com/2024/02/06/innosphere-ventures-selects-2024-cleantech-cohort/", ["prediction", "investment", "decision"], "", 2)], 2, True),
        # Geothermal Strategy Partners, trend 4: one reported sentence with two terms (1). The same sentence stands on a second page of the same university: not counted again. 1 is under 2: not tied
        ("Geothermal Strategy Partners (GSP)", 4, [("web", "https://attheu.utah.edu/research/university-startups/u-spinout-launches-to-support-next-generation-geothermal-development/", ["risk", "assessment"], "", 1)], 1, False),
        # Quaise Energy, trend 3: its sentences hold one term at most ("DOE"): no sentence supports the trend
        ("Quaise Energy", 3, [], 0, False),
        # Bedrock Energy, trend 4: the warehouse's row says "subsurface modeling", one term: not enough
        ("Bedrock Energy", 4, [], 0, False),
    ]

    def test_the_same_sentence_on_two_addresses_counts_once(self):
        c = by_name(judged(read="quotes"))["Geothermal Strategy Partners (GSP)"]          # session 147 (changed on purpose): the two sentences are quotations
        same = [e for e in c["evidence"] if e["text"].startswith("GSP specializes in risk assessment")]
        self.assertEqual(len(same), 2)
        self.assertEqual(len({e["address"] for e in same}), 2)
        self.assertEqual(len({e["sha"] for e in same}), 1)
        self.assertEqual((c["ties"][4]["score"], c["ties"][4]["tied"], len(c["ties"][4]["lines"])), (1, False, 1))

    def test_quotations_decide_nothing_by_the_rule_as_it_now_stands(self):
        """Session 147: with no saved page, no company of this fixture has a web line, and the four tied by quotations
        alone are no longer tied; the warehouse's and the fetched titles' ties stand as they were."""
        now, then = by_name(judged()), by_name(judged(read="quotes"))
        self.assertFalse(any(e["tier"] == "web" for c in now.values() for e in c["evidence"]))
        for name in ("XGS Energy", "Geothermal Radar", "Thermofilic"):
            self.assertTrue(then[name]["trends"])
            self.assertEqual(now[name]["trends"], [], name)
        self.assertEqual(now["Zanskar Geothermal & Minerals"]["ties"][1]["score"], 10)
        self.assertEqual(now["Zanskar Geothermal & Minerals"]["trends"], then["Zanskar Geothermal & Minerals"]["trends"])

    def test_a_single_term_is_never_a_tie(self):
        quaise = by_name(judged(read="quotes"))["Quaise Energy"]
        self.assertTrue(any("DOE" in e["text"] for e in quaise["evidence"]))
        self.assertEqual(quaise["trends"], [])

    def test_each_case(self):
        rows = by_name(judged(read="quotes"))          # session 147 (changed on purpose): four of the seven cases rest on quotations; tests/test_session147.py scores saved pages by hand
        self.assertTrue(self.CASES, "no case was written by hand")
        for name, trend, lines, score, tied in self.CASES:
            t = rows[name]["ties"][trend]
            got = [(x["tier"], x["address"], x["terms"], x["phrase"], x["points"]) for x in t["lines"]]
            self.assertEqual(got, lines, (name, trend))
            self.assertEqual((t["score"], t["tied"]), (score, tied), (name, trend))
            for tier, address, terms, phrase, points in lines:
                self.assertEqual(points, tie.TIERS[tier] + (1 if phrase or len(terms) >= 3 else 0))
                sentence = next(x["text"] for x in t["lines"] if x["address"] == address)
                have = set(tie.tokens(sentence))
                self.assertTrue(all(w in have for w in terms), (name, terms, sentence))


if __name__ == "__main__":
    unittest.main()
