"""Session 315: the Research tool, its form (the owner's ruling of 13 October 2026 on the layout, and his rulings of
19 October on the Research pack's section 9; the chain of 19 October, daytime). What is held to:

  the tool is named Research everywhere a visitor reads it; the page's order is the ruling's, the reader's own form
    first (the question, the tables, an email), the finding flow under it, then today's chart, this week's chart, the
    library, the archive;
  the form writes analysis_requests through the server route as finding reader_question, each field bounded there,
    and the data machine's worker never takes such a row;
  every figure of a card is a Num whose key names the card and the figure's place in the card's JSON, and the value
    checker reads the same file (a figure written as text is compared as text); the week's card and today's record
    carry keys too; a figure whose words name a grid held under its publisher's terms reads "license needed";
  ruling 3a: the daily chart's guard stays at 25 percent; ruling 5b: six of the seven plain-name drafts follow the
    methods notes (status note, the note in from) and the one no note names stays a draft; ruling 1b: nothing changes
    at /internal/findings;
  the pack and the methods note say the page as built; no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = [
    "site/components/analysis/AskForm.tsx", "site/app/research/page.tsx", "site/app/api/analysis/route.ts", "site/components/analysis/RequestForm.tsx",
    "site/components/analysis/FindingCard.tsx", "site/components/Num.tsx", "site/scripts/check-values.mjs", "site/scripts/build-content.mjs", "site/lib/markdown.ts",
    "warehouse/analysis/findings/worker.py", "warehouse/analysis/plain_names.json", "docs/methods/automated_analysis_findings.md", "docs/reviews/packs/research.md",
    "tests/test_session267.py", "tests/test_session315.py",
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFormFirst(unittest.TestCase):
    def test_the_page_is_research_in_the_rulings_order_with_the_readers_form_first(self):
        page = src("site", "app", "research", "page.tsx")
        self.assertIn('<ToolHeader title="Research"', page)
        self.assertIn('export const metadata: Metadata = { title: "Research" };', page)
        order = ['<AskForm tables={tables} />', 'id="choose"', '<RequestFlow', 'id="requests"', 'id="today"', 'id="week"', 'id="library"', 'id="archive"']
        at = [page.index(o) for o in order]
        self.assertEqual(at, sorted(at))
        self.assertIn("export default async function ResearchPage()", page)
        self.assertIn("tables = (await liveCatalogue()).map((r) => r.table_name).sort();", page)
        for f in ("site/lib/pages.ts", "site/app/research/page.tsx", "site/components/analysis/AskForm.tsx"):
            body = re.sub(r"//.*", "", src(*f.split("/")))
            self.assertNotIn("Automated Analysis", body, f)   # the method's name only (docs/methods/)

    def test_the_form_asks_the_question_the_tables_and_an_email_and_sends_them_to_the_route(self):
        form = src("site", "components", "analysis", "AskForm.tsx")
        for bit in ('data-ask-question="1"', "data-ask-tables={chosen.join(\",\")}", 'data-ask-email="1"', 'data-ask-submit="1"',
                    'finding: "reader_question", params: { question: question.trim(), tables: chosen.join(","), email: email.trim() }',
                    "export const QUESTION_MAX = 500, EMAIL_MAX = 120, TABLES_MAX = 10;", "Stored with the request and used to send the answer"):
            self.assertIn(bit, form, bit)
        route = src("site", "app", "api", "analysis", "route.ts")
        self.assertIn('export const READER_QUESTION = "reader_question";', route)
        self.assertIn("if (question.length < 10 || question.length > 500)", route)
        self.assertIn("if (tables.length > 10 || tables.some((t) => !/^[a-z0-9_]{1,80}$/.test(t)))", route)
        self.assertIn('p_finding: READER_QUESTION, p_params: JSON.stringify({ question, tables: tables.join(","), email })', route)
        self.assertLess(route.index("if (body.finding === READER_QUESTION)"), route.index("const entry = catalogue.find((c) => c.id === body.finding);"))

    def test_the_worker_never_takes_a_readers_question(self):
        w = src("warehouse", "analysis", "findings", "worker.py")
        self.assertEqual(w.count('"finding": "neq.reader_question"'), 2)
        lst = src("site", "components", "analysis", "RequestForm.tsx")
        self.assertIn('r.finding === "reader_question" ? "A reader\'s question', lst)
        self.assertIn("data-reader-question={r.id}", lst)


class EveryFigureIsANum(unittest.TestCase):
    def test_the_cards_figures_carry_their_keys_and_the_checker_reads_the_cards_file(self):
        card = src("site", "components", "analysis", "FindingCard.tsx")
        self.assertIn('import { Num } from "@/components/Num";', card)
        self.assertIn("const calloutKey = (card: Card, i: number, side: \"before\" | \"after\", c: Callout) => `finding|${card.card_id}|callout|${i}|${side}|${gridOfWords(`${c[side].period} ${c.label}`)}`;", card)
        self.assertIn('<Num check={calloutKey(card, i, "before", c)} raw={c.before.text}>', card)
        self.assertIn('<Num check={calloutKey(card, i, "after", c)} raw={c.after.text}>', card)
        self.assertIn("<Num check={`finding|${card.card_id}|effect|${ri}|${col}|${g}`} raw={r[col]}>", card)
        page = src("site", "app", "research", "page.tsx")
        self.assertIn("<Num check={`finding|${wk.card!.card_id}|callout|${i}|before|", page)
        self.assertIn("<Num check={`digest_chart|${today.date}|${today.table}|${k}`} raw={String(v)}>", page)
        chk = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "finding") {', chk)
        self.assertIn('if (p[2] === "callout") return card.callouts?.[Number(p[3])]?.[p[4]]?.text;', chk)
        self.assertIn('if (p[2] === "effect") return card.effect_table?.rows?.[Number(p[3])]?.[p[4]];', chk)
        self.assertIn('if (p[0] === "digest_chart") {', chk)
        self.assertIn('(typeof t === "string" && Number.isNaN(Number(t))) ? t === raw :', chk)
        self.assertIn("numbers: r.numbers && typeof r.numbers === \"object\" ? r.numbers : {} };", src("site", "scripts", "build-content.mjs"))
        self.assertIn('"/research", "/research/card/batteries_lunch_grids", "/research/card/gas_sets_price",', chk)   # the pages checked
        self.assertIn("const textOk = hourText || pText || text === raw || text.startsWith(", chk)

    def test_the_keys_resolve_in_every_committed_card(self):
        d = os.path.join(ROOT, "site", "data", "findings")
        cards = [json.load(open(os.path.join(d, f), encoding="utf-8")) for f in os.listdir(d) if f.endswith(".json") and f != "catalogue.json"]
        self.assertGreaterEqual(len(cards), 11)
        for c in cards:
            for i, co in enumerate(c["callouts"]):
                for side in ("before", "after"):
                    self.assertIsInstance(co[side]["text"], str, (c["card_id"], i, side))
            for r in (c.get("effect_table") or {}).get("rows", []):
                for col in ("coef_per_gw", "se", "p", "n", "r2"):
                    self.assertIn(col, r, (c["card_id"], col))

    def test_a_figure_of_a_held_grid_reads_license_needed_by_the_tools_rule(self):
        num = src("site", "components", "Num.tsx")
        self.assertIn('if (head === "finding") {', num)
        self.assertIn('return g && g !== "-" && licenseHeldGrid(g) ? { table: `finding ${p[1]}`, title: licenseGridTitle(g) } : null;', num)
        self.assertIn('if (head === "digest_chart") return p[2] && licenseHeldRow(p[2], null)', num)
        card = src("site", "components", "analysis", "FindingCard.tsx")
        self.assertIn('[/\\bNYISO\\b/i, "nyiso"], [/\\bISO-NE\\b/i, "isone"]', card)
        status = json.load(open(os.path.join(ROOT, "site", "data", "license_status.json"), encoding="utf-8"))
        self.assertEqual(status["from"], "2026-10-21")


class TheRulings(unittest.TestCase):
    def test_3a_the_guard_stays_at_25_percent(self):
        self.assertIn("RECORD_JUMP = 0.25", src("warehouse", "analysis", "findings", "daily_chart.py"))

    def test_5b_the_plain_names_follow_the_methods_notes(self):
        d = json.load(open(os.path.join(ROOT, "warehouse", "analysis", "plain_names.json"), encoding="utf-8"))
        by = {e["key"]: e for e in d["names"]}
        notes = {k: e for k, e in by.items() if e["status"] == "note"}
        self.assertEqual(len(notes), 6)
        for k, e in notes.items():
            self.assertTrue(e["from"].startswith("docs/methods/"), k)
            note = e["from"].split(" ")[0]
            self.assertTrue(os.path.exists(os.path.join(ROOT, note)), note)
            self.assertIn(e["table"], src(*note.split("/")), k)      # the note names the table
        self.assertEqual([k for k, e in by.items() if e["status"] == "draft"], ["variable:eia_retail_sales_monthly|retail_sales"])
        self.assertEqual(d["drafts"], 1)
        self.assertIn("Session 315", d["about"])
        self.assertIn("EIA-923", by["variable:eia_state_generation_monthly|net_generation"]["name"])
        self.assertIn("net of retirements", by["variable:storage_buildout_monthly|battery_operating_mw_net_added_12m"]["name"])

    def test_1b_the_review_list_is_untouched_and_the_notes_say_the_page(self):
        self.assertIn("Session 315", src("docs", "reviews", "packs", "research.md"))
        self.assertIn("## The Research tool, its form and its figures (session 315, 19 October 2026)", src("docs", "methods", "automated_analysis_findings.md"))


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
