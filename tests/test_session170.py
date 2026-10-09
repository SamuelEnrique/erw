"""Session 170: Automated Analysis, the foundation and the first three findings.

The findings package (warehouse/analysis/findings/): each finding's Python reproduces every number on its card from the
card's own CSV download (numbers_from_rows against the committed card JSON); the do-files follow the owner's rules; the
queue worker takes a queued row and writes the card or the plain reason; the Roundup takes a chosen finding and falls
back, labeled; roundup.yml restores the findings' tables; the page and the route hold what the part asked. No network.
The full recomputation against the warehouse tables runs only with ERW_FINDINGS_FULL=1 and the tables present.
"""
import importlib
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
CARDS = os.path.join(ROOT, "site", "data", "findings")
DOWNLOADS = os.path.join(ROOT, "site", "public", "findings")
sys.path.insert(0, FIND)
import common  # noqa: E402
import run_finding  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def card(cid):
    with open(os.path.join(CARDS, cid + ".json"), encoding="utf-8") as f:
        return json.load(f)


def close(a, b, places=6):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) or isinstance(b, str):
        return str(a) == str(b)
    return abs(float(a) - float(b)) <= 10 ** -places * max(1.0, abs(float(b)))


class EveryNumberOnTheCardIsReproduced(unittest.TestCase):
    """The card's numbers, recomputed from the CSV download by the finding's own Python."""

    def reproduce(self, name):
        mod = importlib.import_module(name)
        c = card(name)
        rows = common.read_rows_csv(os.path.join(DOWNLOADS, c["downloads"]["csv"]))
        got = mod.numbers_from_rows(rows, c["params"])
        n = got[0] if isinstance(got, tuple) else got
        for k, v in c["numbers"].items():
            self.assertIn(k, n, f"{name}: {k} not recomputed")
            self.assertTrue(close(n[k], v), f"{name}: {k} recomputed {n[k]!r}, card {v!r}")
        return c, n

    def test_batteries_lunch(self):
        c, n = self.reproduce("batteries_lunch")
        # the thesis's 2025 values at HB_HUBAVG, to the cent (docs/methods/ercot_peak_premium.md)
        self.assertAlmostEqual(n["median_last"], 25.68, places=2)
        self.assertAlmostEqual(n["p999_last"], 311.80, places=2)
        self.assertEqual(c["kind"], "econometric")
        self.assertEqual([r["coef_per_gw"] for r in c["effect_table"]["rows"]][0], c["numbers"]["reg_multiple_coef"])

    def test_gas_sets_price(self):
        c, n = self.reproduce("gas_sets_price")
        self.assertEqual(c["kind"], "visual")
        self.assertEqual([p["words"] for p in c["placeholders"]], ["MISO", "PJM"])

    def test_queue_divorce(self):
        c, n = self.reproduce("queue_divorce")
        self.assertGreater(n["requested_gw"], 3000)
        self.assertEqual(n["cdc_marriage_rate"], 6.1)
        self.assertEqual(n["cdc_divorce_rate"], 2.4)

    def test_every_callout_and_sentence_number_is_in_the_numbers(self):
        # each callout's text is a number of card["numbers"] formatted, or a period: nothing typed by hand
        for name in run_finding.FINDINGS:
            c = card(name)
            pool = {common.fmt(v, nd) for v in c["numbers"].values() if isinstance(v, (int, float)) for nd in (0, 1, 2)}
            pool |= {str(v) for v in c["numbers"].values()}
            for co in c["callouts"]:
                for side in ("before", "after"):
                    text = co[side]["text"]
                    nums = re.findall(r"[\d,]+\.?\d*", text)
                    for x in nums:
                        self.assertTrue(x in pool or x.replace(",", "") in {p.replace(",", "") for p in pool}, f"{name}: callout number {x!r} in {text!r} is not a card number")

    def test_the_csv_hash_matches_the_download(self):
        import hashlib
        for name in run_finding.FINDINGS:
            c = card(name)
            with open(os.path.join(DOWNLOADS, c["downloads"]["csv"]), "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), c["csv_sha256"], name)


class TheDoFiles(unittest.TestCase):
    """The owner's rules: no line continuation; one empty line between commands outside loops and none inside; every
    variable destrung with force; per-variable sentinel recoding before any reshape loop; study_year_topic_word.csv."""

    def test_rules(self):
        for name in run_finding.FINDINGS:
            mod = importlib.import_module(name)
            text = mod.stata({})
            self.assertNotIn("///", text, name)
            self.assertNotIn("/*", text, name)
            blocks = text.strip().split("\n\n")
            for b in blocks:
                lines = b.splitlines()
                if len(lines) > 1:
                    self.assertTrue(lines[0].rstrip().endswith("{") and lines[-1].strip() == "}", f"{name}: a multi-line block that is not a loop: {b!r}")
                    self.assertNotIn("", [ln.strip() for ln in lines], f"{name}: an empty line inside a loop")
            m = re.search(r'import delimited "([^"]+)"', text)
            self.assertTrue(m and re.fullmatch(r"[a-z]+_\d{4}_[a-z]+(_[a-z]+)+\.csv", m.group(1)), f"{name}: file name {m and m.group(1)!r}")
            destrung = re.findall(r"destring (\w+), replace force", text)
            self.assertTrue(destrung, name)
            for v in destrung:
                self.assertIn(f"replace {v} = . if {v} == -999", text, f"{name}: no sentinel recoding for {v}")
            first_loop = text.find("foreach")
            last_sentinel = text.rfind("== -999")
            if first_loop >= 0:
                self.assertLess(last_sentinel, first_loop, f"{name}: sentinel recoding after a loop")
            csv_name = m.group(1)
            self.assertEqual(csv_name, mod.CSV_NAME)


class TheCatalogueAndTheCards(unittest.TestCase):
    def test_catalogue_declares_inputs_and_kind(self):
        cat = json.load(open(os.path.join(CARDS, "catalogue.json"), encoding="utf-8"))
        self.assertEqual([c["id"] for c in cat], run_finding.FINDINGS)
        for c in cat:
            self.assertIn(c["kind"], ("visual", "econometric"))
            for k, inp in c["inputs"].items():
                self.assertIn(inp["default"], inp["choices"], f"{c['id']}.{k}")
        hub = next(c for c in cat if c["id"] == "batteries_lunch")["inputs"]["hub"]
        self.assertEqual(hub["words"]["HB_NORTH"], "ERCOT North Hub")

    def test_card_id_names_non_default_inputs(self):
        mod = importlib.import_module("batteries_lunch")
        self.assertEqual(run_finding.card_id("batteries_lunch", {"hub": "HB_HUBAVG", "first_year": 2019}, mod), "batteries_lunch")
        self.assertEqual(run_finding.card_id("batteries_lunch", {"hub": "HB_NORTH", "first_year": 2019}, mod), "batteries_lunch__hub-HB_NORTH")

    def test_a_bad_input_is_refused(self):
        mod = importlib.import_module("batteries_lunch")
        with self.assertRaises(ValueError):
            run_finding.coerce(mod, {"hub": "HB_NOWHERE"})

    def test_no_em_dash_in_the_cards_or_the_words(self):
        for name in run_finding.FINDINGS:
            self.assertNotIn("—", json.dumps(card(name), ensure_ascii=False), name)
            self.assertNotIn("—", src("warehouse", "analysis", "findings", name + ".py"), name)
        self.assertNotIn("—", src("docs", "voice.md"))

    def test_causal_words_stay_within_the_design(self):
        c = card("batteries_lunch")
        words = (c["why"] + " " + c["subtitle"]).lower()
        self.assertIn("association", words)
        self.assertNotIn("caused", words)
        self.assertNotIn("because of batteries", words)

    def test_the_marriage_statistic_is_quoted_with_its_definition(self):
        c = card("queue_divorce")
        self.assertIn("per 1,000", c["footnote"])
        self.assertIn("45 reporting states", c["footnote"].lower())
        self.assertIn("not the share of marriages that end in divorce", c["footnote"])
        self.assertEqual(c["cdc"]["url"], "https://www.cdc.gov/nchs/fastats/marriage-divorce.htm")


class TheWorker(unittest.TestCase):
    """A queued row (as a file) is taken, run, and ends done with its card or failed with a plain reason."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="erw170-")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_a_request_without_the_tables_fails_plainly_and_stays_recorded(self):
        import worker
        q = os.path.join(self.d, "queue")
        os.makedirs(q)
        row = {"id": "20261009T090000Z-abc123", "kind": "run", "finding": "queue_divorce", "params": {"first_year": "2000", "last_year": "2020"},
               "status": "queued", "asked_at": "2026-10-09T09:00:00Z", "note": ""}
        with open(os.path.join(q, row["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(row, f)
        empty = os.path.join(self.d, "no-tables")
        os.makedirs(empty)
        code = worker.main(["--once", "--local-dir", q, "--in-dir", empty, "--card-dir", os.path.join(self.d, "cards"), "--download-dir", os.path.join(self.d, "dl"), "--machine", "test"])
        self.assertEqual(code, 0)
        got = json.load(open(os.path.join(q, row["id"] + ".json"), encoding="utf-8"))
        self.assertEqual(got["status"], "failed")
        self.assertIn("not on the data machine", got["note"])
        self.assertEqual(got["machine"], "test")

    def test_a_request_with_the_table_ends_done_with_its_card(self):
        import worker
        table = os.path.join(common.DEFAULT_IN_DIR, "lbnl_interconnection_queue.csv")
        if not os.path.exists(table):
            raise unittest.SkipTest("lbnl_interconnection_queue is not on this machine")
        q = os.path.join(self.d, "queue")
        os.makedirs(q)
        row = {"id": "20261009T090100Z-def456", "kind": "run", "finding": "queue_divorce", "params": {"first_year": "2010", "last_year": "2020"},
               "status": "queued", "asked_at": "2026-10-09T09:01:00Z", "note": ""}
        with open(os.path.join(q, row["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(row, f)
        code = worker.main(["--once", "--local-dir", q, "--in-dir", common.DEFAULT_IN_DIR, "--card-dir", os.path.join(self.d, "cards"), "--download-dir", os.path.join(self.d, "dl"), "--machine", "test"])
        self.assertEqual(code, 0)
        got = json.load(open(os.path.join(q, row["id"] + ".json"), encoding="utf-8"))
        self.assertEqual(got["status"], "done", got.get("note"))
        self.assertEqual(got["card_id"], "queue_divorce__first_year-2010")
        self.assertEqual(got["card"]["params"], {"first_year": 2010, "last_year": 2020})
        self.assertTrue(os.path.exists(os.path.join(self.d, "cards", "queue_divorce__first_year-2010.json")))
        self.assertTrue(os.path.exists(os.path.join(self.d, "dl", "erw_2026_queue_outcomes_technology__first_year-2010.csv")))


class TheRoundup(unittest.TestCase):
    def test_the_chosen_finding_comes_first_and_the_fallback_is_labeled(self):
        text = src("warehouse", "news", "roundup.py")
        self.assertIn("roundup_pick.chosen(label, log)", text)
        self.assertIn("(the rule's pick; no finding was chosen for this week)", text)
        self.assertLess(text.find("roundup_pick.chosen"), text.find("chart_of_the_week.json"))

    def test_the_choice_lines_hold_the_cards_words(self):
        import roundup_pick
        c = card("queue_divorce")
        L = roundup_pick.lines(c, "2026-W41")
        self.assertIn("chosen for this Roundup", L[0])
        self.assertIn(c["why"], L)
        self.assertTrue(any("/analysis/card/queue_divorce" in ln for ln in L))

    def test_no_choice_without_credentials_falls_back(self):
        import roundup_pick
        old = {k: os.environ.pop(k, None) for k in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY")}
        try:
            sys.path.insert(0, os.path.join(ROOT, "warehouse"))
            import lock
            saved = lock.env
            lock.env = lambda name: ""
            try:
                self.assertIsNone(roundup_pick.chosen("2026-W41", log=lambda m: None))
            finally:
                lock.env = saved
        finally:
            for k, v in old.items():
                if v is not None:
                    os.environ[k] = v

    def test_the_workflow_restores_the_findings_tables_and_a_failure_does_not_stop_it(self):
        y = src(".github", "workflows", "roundup.yml")
        self.assertIn("run_finding.py --tables", y)
        self.assertIn("the findings, not every table could be restored", y)
        self.assertLess(y.find("run_finding.py --tables"), y.find("warehouse/news/roundup.py;"))

    def test_the_tables_pattern_names_the_histories(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run_finding.main(["--tables"])
        pat = buf.getvalue().strip()
        for t in ("ercot_all_hub_prices_history", "isone_zone_prices_history", "lbnl_interconnection_queue", "storage_buildout_monthly"):
            self.assertRegex(t, pat)


class ThePageAndTheRoute(unittest.TestCase):
    def test_the_page_is_built_around_the_cards_and_the_w40_chart_is_not_drawn(self):
        p = src("site", "app", "analysis", "page.tsx")
        self.assertIn("FindingCard", p)
        self.assertIn("RequestForm", p)
        self.assertNotIn("ChartOfWeekView", p)
        self.assertNotIn("robust z = |value minus the median", p)  # the old rule's footnote
        self.assertIn("ranked among the same measure", p)

    def test_the_week_page_keeps_the_chart_of_the_week(self):
        self.assertIn("ChartOfWeekView", src("site", "app", "analysis", "[week]", "page.tsx"))

    def test_the_card_has_no_model_name_or_cost(self):
        f = src("site", "components", "analysis", "FindingCard.tsx")
        self.assertNotIn("note_by", f)
        self.assertNotIn("USD 0.", f)

    def test_the_route_answers_only_the_internal_view(self):
        r = src("site", "app", "api", "analysis", "route.ts")
        self.assertIn("internalOk", r)
        self.assertIn("analysis_request", r)
        self.assertIn("analysis_requests_list", r)

    def test_the_gallery_has_human_labels(self):
        self.assertIn("ERCOT North Hub", src("site", "lib", "findingwords.ts"))
        self.assertIn("paramWords", src("site", "components", "AnalysisGallery.tsx"))

    def test_the_migration_is_internal_and_counts_the_day(self):
        m = src("warehouse", "supabase", "migrations", "026_analysis_requests.sql")
        self.assertIn("enable row level security", m)
        self.assertIn("revoke all on public.analysis_requests from public, anon, authenticated", m)
        self.assertIn("internal_costs_token", m)
        self.assertIn("'reason', 'day'", m)

    def test_the_renderer_fails_on_a_missing_font(self):
        r = src("site", "scripts", "render-cards.mjs")
        self.assertIn("fontsPresent", r)
        self.assertIn("no render is made in a fallback font", r)
        self.assertIn("font fallback", r)

    def test_the_voice_page_holds_the_card(self):
        v = src("docs", "voice.md")
        self.assertIn("## The finding card (session 170)", v)
        self.assertIn("the joke bends to the data", v)

    def test_release_keeps_analysis_in_review(self):
        self.assertIn('"/analysis": "review"', src("site", "lib", "release.ts"))


@unittest.skipUnless(os.environ.get("ERW_FINDINGS_FULL") == "1", "the full recomputation runs only with ERW_FINDINGS_FULL=1")
class TheFullRecomputation(unittest.TestCase):
    def test_each_finding_recomputes_to_its_card(self):
        for name in run_finding.FINDINGS:
            mod = importlib.import_module(name)
            if any(not os.path.exists(os.path.join(common.DEFAULT_IN_DIR, t + ".csv")) for t in mod.TABLES):
                raise unittest.SkipTest(f"{name}: a table is not on this machine")
            c = card(name)
            rows, meta = mod.compute(c["params"], common.DEFAULT_IN_DIR)
            fresh = mod.card(rows, c["params"], meta)
            for k, v in c["numbers"].items():
                self.assertTrue(close(fresh["numbers"][k], v), f"{name}: {k} {fresh['numbers'][k]!r} vs {v!r}")


if __name__ == "__main__":
    unittest.main()
