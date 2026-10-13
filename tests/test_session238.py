"""Session 238: Automated Analysis becomes Research, at /research (the owner's task of 12 October 2026).

What is held to: the page lives at site/app/research and /analysis with every address under it redirects there; the
menu names it Research under Analysis and no source of the site links the old address; the page's order is the
owner's (the request form, today's chart, this week's chart, the findings library, the archive); a card's grids and
topics are read from the card's own data by the stated rules, reproduced here in Python from the committed cards; the
chart a Roundup carried is read from the Roundup's own section; a file that is not held is never a link; the page
takes the brand through <Brand>, the shared components and class names app/tokens.css styles, with no color of its
own; and the charts' color literals each have a token to be drawn in. No test here sets the environment.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
CARDS = os.path.join(SITE, "data", "findings")
ORDER = ['id="ask"', 'id="requests"', 'id="today"', 'id="week"', 'id="library"', 'id="archive"']
GRIDS = [("ercot", "ERCOT"), ("caiso", "CAISO"), ("pjm", "PJM"), ("miso", "MISO"), ("spp", "SPP"), ("nyiso", "NYISO"), ("isone", "ISO-NE")]
TOPICS = [("fuel-prices", r"fuel_spot"), ("curtailment", r"curtailment"), ("batteries", r"storage|battery"), ("generation", r"fuel_supply"),
          ("queue", r"queue"), ("demand", r"load|demand"), ("interchange", r"interchange"), ("events", r"^event_"), ("generators", r"eia860m"),
          ("power-prices", r"prices")]
FILES = ["site/app/research/page.tsx", "site/app/research/[week]/page.tsx", "site/app/research/card/[id]/page.tsx", "site/components/research/Library.tsx",
         "site/lib/research.ts", "site/lib/researchrules.ts", "site/components/echarts.ts", "site/components/analysis/FindingCard.tsx", "site/app/tokens.css",
         "site/lib/markdown.ts", "site/scripts/build-content.mjs", "site/scripts/check-analysis.mjs", "site/next.config.ts", "site/lib/release.ts", "site/lib/pages.ts",
         "tests/test_session238.py", "docs/brand/review-238/README.md", "archive/sessions/SESSION_238_REPORT.md", "docs/methods/automated_analysis_findings.md"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def cards():
    out = []
    for f in sorted(os.listdir(CARDS)):
        if f.endswith(".json") and f != "catalogue.json":
            with open(os.path.join(CARDS, f), encoding="utf-8") as h:
                out.append(json.load(h))
    return out


def grids_of(card):
    """The rule of site/lib/researchrules.ts, written again: the grid names in the card's tables, input words, series and categories."""
    chart = card.get("chart") or {}
    words = " | ".join([str(v) for v in (card.get("inputs_words") or {}).values()] + [s.get("name", "") for s in chart.get("series") or []] + [str(x) for x in chart.get("x") or []])
    not_held = {p["grid"].lower() for p in card.get("placeholders") or []}
    found = []
    for gid, name in GRIDS:
        if gid in not_held:
            continue
        if any(t.startswith(gid + "_") for t in card.get("tables") or []) or re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", words, re.I):
            found.append(gid)
    return found or ["none"]


def topics_of(card):
    hit = set()
    for t in card.get("tables") or []:
        hit.add(next((tid for tid, rule in TOPICS if re.search(rule, t)), "other"))
    return [tid for tid, _ in TOPICS + [("other", "")] if tid in hit]


class TheAddress(unittest.TestCase):
    def test_the_page_moved_and_the_old_folder_is_gone(self):
        for p in (("page.tsx",), ("view.tsx",), ("[week]", "page.tsx"), ("card", "[id]", "page.tsx"), ("card", "render.css")):
            self.assertTrue(os.path.exists(os.path.join(SITE, "app", "research", *p)), p)
        self.assertFalse(os.path.exists(os.path.join(SITE, "app", "analysis")))          # moved, not copied: one page, one address
        self.assertTrue(os.path.exists(os.path.join(SITE, "app", "api", "analysis", "route.ts")))   # the request route is where it was

    def test_the_old_addresses_redirect_with_their_tail(self):
        cfg = src("site", "next.config.ts")
        self.assertIn('{ source: "/analysis", destination: "/research", permanent: true }', cfg)
        self.assertIn('{ source: "/analysis/:path*", destination: "/research/:path*", permanent: true }', cfg)
        self.assertNotIn('source: "/analysis-files', cfg)                                # the weekly files keep their address
        self.assertNotIn('source: "/api/analysis', cfg)

    def test_both_addresses_are_in_review(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/analysis": "review"', rel)
        self.assertIn('"/research": "review"', rel)

    def test_the_menu_names_it_research_under_analysis(self):
        pages = src("site", "lib", "pages.ts")
        at = pages.index('label: "Analysis",')
        group = pages[at:pages.index("\n  },", at)]
        self.assertIn('{ href: "/research", label: "Research", line: "', group)
        self.assertNotIn('href: "/analysis"', pages)
        self.assertNotIn("Automated Analysis", group)
        self.assertEqual(re.findall(r'href: "([^"]+)"', group), ["/research", "/ask", "/events", "/policy", "/thesis"])   # nothing else moved in the group

    def test_no_source_of_the_site_links_the_old_address(self):
        allowed = {os.path.join("lib", "release.ts"), os.path.join("lib", "markdown.ts"), "next.config.ts"}
        pat = re.compile(r"""(?<![\w@.])/analysis(?![-\w\\])""")   # the page's address; not /api/analysis, /analysis-files, a repository path or a pattern
        bad = []
        for base in ("app", "components", "lib"):
            for d, _, files in os.walk(os.path.join(SITE, base)):
                if "_retired" in d:
                    continue
                for f in files:
                    if not f.endswith((".ts", ".tsx", ".css")):
                        continue
                    rel = os.path.relpath(os.path.join(d, f), SITE)
                    if rel in allowed:
                        continue
                    with open(os.path.join(d, f), encoding="utf-8") as h:
                        for i, line in enumerate(h, 1):
                            if pat.search(line) and "session 238" not in line.lower() and "until session 238" not in line:
                                bad.append(f"{rel}:{i}")
        # the page's own header comment tells the move (two lines); nothing else names the old address
        self.assertEqual([b for b in bad if not b.startswith(os.path.join("app", "research", "page.tsx"))], [])
        for script in ("check-analysis.mjs", "check-analysis-flow.mjs", "check-findings-grids.mjs", "check-internal-findings.mjs", "render-cards.mjs"):
            s = src("site", "scripts", script)
            self.assertIn("/research", s, script)
        self.assertIn('await get("/research")', src("site", "scripts", "check-analysis.mjs"))
        routes = src("site", "scripts", "check-routes.mjs")
        for a in ('"/research"', '"/analysis"', '"/analysis/card/gas_sets_price"', '"/analysis/2026-W40"'):
            self.assertIn(a, routes)                                                      # the new address and the redirects are read at every landing

    def test_the_roundups_writers_and_held_roundups_point_at_the_new_address(self):
        self.assertIn("[/research](/research)", src("warehouse", "news", "roundup.py"))
        pick = src("warehouse", "analysis", "findings", "roundup_pick.py")
        self.assertIn("[/research/card/{cid}](/research/card/{cid})", pick)
        self.assertNotIn("(/analysis", pick)
        md = src("site", "lib", "markdown.ts")
        self.assertIn('if (token.type === "link" && /^\\/analysis(?=$|[/?#])/.test(t.href)) {', md)   # a Roundup written before the move
        self.assertIn('const to = t.href.replace(/^\\/analysis/, "/research");', md)


class ThePage(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "research", "page.tsx")

    def test_the_order_is_the_owners(self):
        at = [self.page.index(o) for o in ORDER]
        self.assertEqual(at, sorted(at))
        self.assertIn('<ToolHeader title="Research"', self.page)
        self.assertIn('export const metadata: Metadata = { title: "Research" };', self.page)

    def test_the_request_flow_is_the_one_it_was(self):
        self.assertIn("<RequestFlow catalogue={catalogue} templates={ofTheFlow(a.templates)} gallery={ofTheFlow(a.gallery.templates)} computedAt={a.gallery.computed_at} cards={defaults}", self.page)
        self.assertIn("<RequestForm catalogue={catalogue} listOnly />", self.page)
        # what a request sends and where it is stored were not touched by this session
        route = src("site", "app", "api", "analysis", "route.ts")
        self.assertIn("analysis_request", route)
        self.assertNotIn("238", route)
        self.assertNotIn("238", src("site", "components", "analysis", "RequestFlow.tsx").replace("/research", ""))

    def test_todays_chart_has_its_fact_its_date_and_its_source(self):
        for bit in ("data-today-chart={today.date}", "{day(today.date)}", 'data-today-fact="1">{today.fact}', 'data-today-source="1"', "{today.table}", "today.proof ?"):
            self.assertIn(bit, self.page, bit)
        build = src("site", "scripts", "build-content.mjs")
        self.assertIn("digest_charts: digestChartRecords,", build)
        self.assertIn("fact: r.fact ?? \"\"", build)                                      # the fact is the warehouse's own sentence, never rewritten
        self.assertIn("proof: r.proof === true", build)

    def test_the_records_of_the_daily_charts_are_whole(self):
        d = os.path.join(ROOT, "docs", "digest", "charts")
        days = sorted(f[:-5] for f in os.listdir(d) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", f))
        self.assertGreaterEqual(len(days), 1)
        for day in days:
            with open(os.path.join(d, day + ".json"), encoding="utf-8") as h:
                r = json.load(h)
            self.assertTrue(os.path.exists(os.path.join(d, day + ".png")), day)
            self.assertEqual(r["date"], day)
            self.assertTrue(r["fact"] and r["table"] and r["title"], day)

    def test_this_weeks_chart_is_the_roundups(self):
        for bit in ("const week = newestChartWeek();", "roundupChart(week)", "data-week-chart={wk.week} data-week-card={wk.card.card_id}", "<ChartOfWeekView c={ruleChart} />"):
            self.assertIn(bit, self.page, bit)
        # the card chosen for a Roundup is not drawn as a library card on top: a superseded card stays out of the list
        top = self.page[self.page.index('id="week"'):self.page.index('id="library"')]
        self.assertNotIn("<FindingCard", top)

    def test_nothing_the_page_showed_is_dropped(self):
        for bit in ("<ScannerFound />", "data-superseded={old.card_id}", "ranked among the same measure", "Skipped this week:", "<ImpactForm entry={impact} />", "export const revalidate = 3600;"):
            self.assertIn(bit, self.page, bit)

    def test_the_archive_is_last_and_lists_both(self):
        arch = self.page[self.page.index('id="archive"'):]
        self.assertIn("data-archive-daily={days.length}", arch)
        self.assertIn("data-archive-weekly={weeks.length}", arch)
        self.assertLess(arch.index("data-archive-daily"), arch.index("data-archive-weekly"))
        self.assertIn("href={`/digest-charts/${charts[d].image}`}", arch)                  # a daily chart opens its picture
        self.assertIn("href={`/research/${w}`}", arch)                                     # a week opens its page
        self.assertNotIn('id="', arch[20:])                                                # no section after it


class TheLibrary(unittest.TestCase):
    def test_every_card_has_a_screen_an_index_line_and_the_two_filters(self):
        lib = src("site", "components", "research", "Library.tsx")
        for bit in ('className="screen-card"', "id={`card-${i.id}`}", "href={`#card-${i.id}`}", 'aria-current={marked === i.id ? "true" : undefined}', "IntersectionObserver",
                    'row("grid", "grid", grids, grid)', 'row("topic", "topic", topics, topic)', "u.searchParams.set(key, v)", "window.history.replaceState(null, \"\", u.toString());",
                    'new URLSearchParams(window.location.search).get(key)', "hidden={!shown.includes(i)}", "data-finding-cards={items.length}"):
            self.assertIn(bit, lib, bit)
        self.assertNotIn("fetch(", lib)                                                    # the library asks no server anything

    def test_the_grids_and_topics_are_the_cards_own(self):
        expect = {c["card_id"]: (grids_of(c), topics_of(c)) for c in cards()}
        # read by eye from the cards on 13 October 2026, so that a change of rule is seen
        self.assertEqual(expect["queue_divorce"], (["none"], ["queue"]))
        self.assertEqual(expect["batteries_curtailment"], (["caiso"], ["curtailment", "batteries", "generation"]))
        self.assertEqual(expect["gas_sets_price"], (["ercot", "caiso", "spp", "nyiso", "isone"], ["fuel-prices", "power-prices"]))   # MISO and PJM are the card's own placeholders: not held
        self.assertEqual(expect["peak_hour_moved"], (["ercot", "caiso"], ["generators", "power-prices"]))
        for cid, (g, t) in expect.items():
            self.assertTrue(g and t, cid)
            self.assertNotIn("other", t, cid)                                              # every table a card reads has a topic rule

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_sites_rules_give_what_python_gives(self):
        code = ("import fs from 'node:fs'; const r = await import('./lib/researchrules.ts'); const out = { cards: {}, weeks: {} };"
                "for (const f of fs.readdirSync('data/findings')) { if (f === 'catalogue.json' || !f.endsWith('.json')) continue;"
                " const c = JSON.parse(fs.readFileSync('data/findings/' + f, 'utf8')); out.cards[c.card_id] = [r.gridsOf(c), r.topicsOf(c)]; }"
                "for (const f of fs.readdirSync('../docs/roundup')) { if (!/^\\d{4}-W\\d{2}\\.md$/.test(f)) continue;"
                " out.weeks[f.slice(0, 8)] = r.chosenCardOf(r.chartSectionOf(fs.readFileSync('../docs/roundup/' + f, 'utf8'))); }"
                "out.labels = [r.GRIDS.map((g) => g.id), r.TOPIC_RULES.map((t) => t.id)]; console.log(JSON.stringify(out));")
        r = subprocess.run([NODE, "--no-warnings", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(got["labels"], [[g for g, _ in GRIDS], [t for t, _ in TOPICS]])
        for c in cards():
            self.assertEqual(got["cards"][c["card_id"]], [grids_of(c), topics_of(c)], c["card_id"])
        # the chart a Roundup carried, from the Roundup's own section
        for week, chosen in got["weeks"].items():
            md = src("docs", "roundup", week + ".md")
            m = re.search(r"^## .*chart of the week\s*$", md, re.I | re.M)
            section = md[m.end():].split("\n## ")[0] if m else ""
            pic = re.search(r"\.\./analysis/findings/([a-z0-9_.-]+)_1600x900\.png", section)
            self.assertEqual(chosen, pic.group(1) if pic else None, week)
        self.assertEqual(got["weeks"].get("2026-W41"), "peak_hour_moved")
        self.assertIsNone(got["weeks"].get("2026-W39"))

    def test_a_file_that_is_not_held_is_never_a_link(self):
        card = src("site", "components", "analysis", "FindingCard.tsx")
        for kind, words in (("csv", "data (CSV): not held"), ("python", "Python: not held"), ("stata", "Stata do-file: not held")):
            self.assertIn('{held && !held.%s ? <span className="text-muted" data-not-held="%s">%s</span> : <a href=' % (kind, kind, words), card)
        self.assertIn("<FindingCard card={c} held={filesHeld(c)} fold />", src("site", "app", "research", "page.tsx"))
        rules = src("site", "lib", "research.ts")
        self.assertIn("const held = new Set(DOCS.findings_files ?? []);", rules)       # the list made at build, not a read of the public folder by a server function
        self.assertIn("findings_files: findingsFiles,", src("site", "scripts", "build-content.mjs"))
        # today every card holds its three files, so the page names none "not held" (check-analysis.mjs reads the page for it)
        for c in cards():
            for kind in ("csv", "python", "stata"):
                self.assertTrue(os.path.exists(os.path.join(SITE, "public", "findings", c["downloads"][kind])), (c["card_id"], kind))


class TheBrand(unittest.TestCase):
    def test_the_pages_take_the_brand_and_write_no_color(self):
        for rel in ("site/app/research/page.tsx", "site/app/research/[week]/page.tsx", "site/app/research/card/[id]/page.tsx"):
            s = src(*rel.split("/"))
            self.assertIn("<Brand>", s, rel)
            self.assertIn("<ToolPage>", s, rel)
            self.assertIn('data-chart-tokens="1"', s, rel)
        for rel in ("site/app/research/page.tsx", "site/components/research/Library.tsx", "site/lib/research.ts", "site/lib/researchrules.ts"):
            s = src(*rel.split("/"))
            self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,8}\b", s), [], rel)              # no color literal
            self.assertNotIn("style={{", s, rel)
            self.assertNotIn("fontFamily", s, rel)
        lib = src("site", "components", "research", "Library.tsx")
        names = set(" ".join(re.findall(r'className="([^"]+)"', lib)).split())
        self.assertEqual(names, {"filter-row", "filter-label", "filter-count", "with-index", "index-side", "index-title", "index-list", "index-none", "index-main", "screen-card"})

    def test_the_render_frame_is_not_branded(self):
        s = src("site", "app", "research", "card", "[id]", "page.tsx")
        frame = s[s.index("if (render) {"):s.index("<Brand>", s.index("if (render) {"))]
        self.assertIn('<div className="finding-render" data-render="1">', frame)
        self.assertNotIn("Brand", frame)

    def test_the_new_rules_are_generic_and_scoped_to_the_brand(self):
        css = src("site", "app", "tokens.css")
        block = css[css.index("/* ---- session 238 (/research)"):]
        for line in block.splitlines():
            if line.startswith(".") or line.startswith("@media"):
                self.assertTrue(line.startswith(".brand-a ") or line.startswith("@media"), line)
        for name in (".page-index", ".sub-title", ".lead-chart", ".filter-row", ".with-index", ".index-list", ".screen-card", ".chart-archive"):
            self.assertIn(".brand-a " + name, block, name)
        self.assertNotIn("research", block.replace("/* ---- session 238 (/research)", ""))   # no rule names the page
        self.assertNotIn("font-family: Georgia", block)
        colors = set(re.findall(r"#[0-9A-Fa-f]{3,8}\b", block))
        self.assertLessEqual(colors, {"#FFFFFF"})                                         # white, as the rules above write it; every other color is a token

    def test_every_color_literal_of_the_cards_charts_has_a_token(self):
        hook = src("site", "components", "echarts.ts")
        table = hook[hook.index("const LITERAL_TOKENS"):hook.index("function inTokens")]
        mapped = dict(re.findall(r'"(#[0-9a-f]{6})": "(--[a-z-]+)"', table))
        literals = set()
        for rel in ("site/lib/findingchart.ts", "site/lib/chartforms.ts", "site/lib/discoverychart.ts", "site/components/analysis/MultiChart.tsx"):
            literals |= {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b", src(*rel.split("/")))}
        self.assertGreaterEqual(len(literals), 9)
        self.assertEqual(sorted(literals - set(mapped)), [])
        css = src("site", "app", "tokens.css")
        brand = css[css.index("body:has(.brand-a) {"):]
        for tok in set(mapped.values()):
            self.assertIn(tok + ":", brand, tok)                                           # each is a token the brand defines
        self.assertIn('const scope = box.current.closest<HTMLElement>("[data-chart-tokens]");', hook)
        self.assertIn("build(scope ? inTokens(chart.current, scope) : chart.current, lib);", hook)   # outside the mark a chart is drawn as it was


class TheWords(unittest.TestCase):
    def test_no_em_dash_in_this_sessions_files(self):
        for rel in FILES:
            p = os.path.join(ROOT, *rel.split("/"))
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as h:
                self.assertNotIn(EM, h.read(), rel)

    def test_the_page_advises_nothing_and_names_no_model(self):
        page = src("site", "app", "research", "page.tsx")
        for word in ("ecommended", "you should", "we suggest", "claude", "Claude"):
            self.assertNotIn(word, page, word)


if __name__ == "__main__":
    unittest.main()
