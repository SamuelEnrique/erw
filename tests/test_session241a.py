"""Session 241, batch A: the brand on eleven pages that were not built for it.

The owner's task of the chain of 12 to 13 October 2026: "the brand on every remaining page. Every page not yet on the
brand, except the Games content and the home page: through the tokens and shared components only." Batch A is
/supply, /contracts, /learn/bill, /battery/customer, /shoulder, /curtailment, /queues, /cost-of-power/battery/awards,
/grid/caiso/alerts, /events with its eight event pages, and /policy. This session changes how a page looks, not what
it says, so nothing here holds a number: the numbers are held by the tests that already pin each page.

  TheWrapper       every page of the batch draws inside <Brand> (components/Brand.tsx), each of its returns
  NoLookOfItsOwn   no color literal, no rounded corner, no shadow and no font in a page's own files
  ChartsReadTokens the two chart files of the batch read the tokens at the chart's own box, so the brand's are read
  TheOneRule       the block this session added to app/tokens.css: scoped to the wrapper, named for no page
  NoDash           no em dash in anything the session wrote
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DASH = chr(0x2014)

# the page of each address, and the files that are that page's own (its page, its client parts, its own chart file)
EVENTS = ["caiso-heat-2020", "caiso-heat-2022", "cold-2025", "covid-2020", "east-heat-2025", "elliott-2022", "ercot-heat-2023", "uri-2021"]
PAGES = {
    "/supply": ["app/supply/page.tsx", "components/supply/SupplyCharts.tsx"],
    "/contracts": ["app/contracts/page.tsx", "app/contracts/read.ts"],
    "/learn/bill": ["app/learn/bill/page.tsx", "app/learn/bill/BillCalc.tsx"],
    "/battery/customer": ["app/battery/customer/page.tsx", "app/battery/customer/Calc.tsx"],
    "/shoulder": ["app/shoulder/page.tsx", "app/shoulder/read.ts"],
    "/curtailment": ["app/curtailment/page.tsx", "app/curtailment/Sections.tsx", "app/curtailment/Charts.tsx"],
    "/queues": ["app/queues/page.tsx"],
    "/cost-of-power/battery/awards": ["app/cost-of-power/battery/awards/page.tsx", "app/cost-of-power/battery/awards/Offers.tsx", "app/cost-of-power/battery/awards/RealTime.tsx"],
    "/grid/caiso/alerts": ["app/grid/caiso/alerts/page.tsx"],
    "/events": ["app/events/page.tsx", "app/events/EventWindow.tsx", "components/EventStudy.tsx"],
    "/policy": ["app/policy/page.tsx", "app/policy/PolicyTable.tsx", "app/policy/WeekView.tsx"],
}
for _e in EVENTS:
    PAGES[f"/events/{_e}"] = [f"app/events/{_e}/page.tsx"]

# how many times each page opens the wrapper: one for each return of the page that draws (a page with two views or a
# branch for a table that could not be read has more than one)
OPENS = {"/policy": 3, "/grid/caiso/alerts": 2}


def src(*parts):
    with open(os.path.join(SITE, *parts), encoding="utf-8") as f:
        return f.read()


def code(text):
    """The file without its comments: a color named in a note is not a color written on the page."""
    text = re.sub(r"/\*[\s\S]*?\*/", " ", text)
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))


class TheWrapper(unittest.TestCase):
    def test_the_batch_is_the_eleven_pages_and_the_eight_events(self):
        self.assertEqual(len(PAGES), 11 + 8)
        on_disk = sorted(d for d in os.listdir(os.path.join(SITE, "app", "events")) if os.path.isfile(os.path.join(SITE, "app", "events", d, "page.tsx")))
        self.assertEqual(on_disk, sorted(EVENTS))            # an event page added later must be put on the brand too

    def test_every_page_imports_the_wrapper_and_draws_inside_it(self):
        for address, files in PAGES.items():
            page = src(*files[0].split("/"))
            with self.subTest(address=address):
                self.assertIn('import { Brand } from "@/components/Brand";', page)
                opens = len(re.findall(r"<Brand(?: noUsage)?>", page))
                self.assertEqual(opens, OPENS.get(address, 1))
                self.assertEqual(page.count("</Brand>"), opens)

    def test_every_return_of_a_page_is_inside_the_wrapper(self):
        # after "export default", each "return (" or "return <" that draws opens the wrapper first
        for address, files in PAGES.items():
            page = src(*files[0].split("/"))
            body = page[page.index("export default"):]
            body = body[:body.index("\n}") + 2]              # the default export only: the components after it draw inside it
            with self.subTest(address=address):
                draws = re.findall(r"^ {2,4}(?:if \([^\n]*\) )?return \(?\s*<([A-Za-z]*)", body, flags=re.M)
                self.assertTrue(draws, address)
                self.assertEqual(set(draws), {"Brand"}, draws)

    def test_only_the_page_that_sends_nothing_typed_takes_no_usage(self):
        for address, files in PAGES.items():
            page = src(*files[0].split("/"))
            with self.subTest(address=address):
                self.assertEqual("<Brand noUsage>" in page, address == "/battery/customer")
        self.assertIn("Nothing you type is sent or stored.", src("app", "battery", "customer", "page.tsx"))

    def test_the_wrapper_is_the_one_of_session_235(self):
        brand = src("components", "Brand.tsx")
        self.assertIn('className={`brand-a ${brandSerif.variable} ${brandSans.variable} ${brandMono.variable}`}', brand)
        self.assertIn('data-no-usage={noUsage ? "1" : undefined}', brand)


class NoLookOfItsOwn(unittest.TestCase):
    def files(self):
        return sorted({f for files in PAGES.values() for f in files})

    def test_no_color_literal(self):
        hexa = re.compile(r"#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3,4})\b")
        for f in self.files():
            shown = code(src(*f.split("/")))
            with self.subTest(file=f):
                self.assertEqual(hexa.findall(shown), [])
                for fn in ("rgb(", "rgba(", "hsl(", "hsla("):
                    self.assertNotIn(fn, shown)

    def test_a_color_in_a_style_or_a_chart_is_a_token(self):
        # every color written in a style, a fill or a stroke names a variable of app/tokens.css (or, for the shared line
        # chart, a token by its short name), or is none, transparent or the hatch pattern of the awards chart
        tokens = src("app", "tokens.css")
        for f in self.files():
            shown = code(src(*f.split("/")))
            with self.subTest(file=f):
                for value in re.findall(r'(?:fill|stroke|background|color)[=:] ?"([^"]+)"', shown):
                    self.assertTrue(value.startswith("var(--color-") or value in ("none", "transparent") or value.startswith("url(#")
                                    or f"--color-{value}:" in tokens, (f, value))
        for name in ("--color-surface", "--color-accent", "--color-ink", "--color-rule", "--color-muted"):
            self.assertIn(name + ":", tokens)

    def test_no_corner_no_shadow_and_no_font_of_its_own(self):
        for f in self.files():
            shown = code(src(*f.split("/")))
            with self.subTest(file=f):
                self.assertIsNone(re.search(r"\brounded(?:-[a-z0-9]+)?\b", shown))
                # a class of that name, not the chart library's pointer type "shadow"
                self.assertIsNone(re.search(r"\bshadow-(?:sm|md|lg|xl|2xl|inner)\b|(?<= )shadow(?=[ \"`])|(?<=[\"`])shadow(?= )", shown))
                self.assertNotIn("fontFamily", shown)
                self.assertNotIn("font-family", shown)

    def test_the_awards_chart_names_its_two_series_by_token(self):
        page = src("app", "cost-of-power", "battery", "awards", "page.tsx")
        self.assertIn('const ENERGY = "var(--color-accent)", ANCILLARY = "var(--color-ink)";', page)
        self.assertIn('const SHEET = "var(--color-surface)", RULE = "var(--color-rule)", MUTED = "var(--color-muted)";', page)
        # its legend still names the same three things, in the same order
        self.assertIn('legend={[{ label: "Energy, net of charging", color: ENERGY }, { label: "Ancillary services", color: ANCILLARY }, { label: "Partial month", color: ANCILLARY, hatch: true }]}', page)

    def test_the_tiles_of_free_energy_are_shaded_from_the_accent_token(self):
        s = src("app", "curtailment", "Sections.tsx")
        # the same shade as before: cardinal at an opacity of 0.06 to 0.90, now mixed from the token
        self.assertIn("background: `color-mix(in srgb, var(--color-accent) ${(100 * (0.06 + 0.84 * s)).toFixed(1)}%, transparent)`", s)
        self.assertIn('color: s > 0.5 ? "var(--color-surface)" : "var(--color-ink)"', s)


class ChartsReadTokens(unittest.TestCase):
    def test_the_two_chart_files_read_at_the_charts_own_box(self):
        for parts, charts in ((("app", "curtailment", "Charts.tsx"), 2), (("components", "supply", "SupplyCharts.tsx"), 1)):
            c = src(*parts)
            with self.subTest(file="/".join(parts)):
                self.assertNotIn("baseStyle()", c)
                self.assertEqual(c.count("const st = baseStyle(el);"), charts)
                self.assertEqual(c.count("const el: Element | null = box.current;"), charts)
                # no token is read at the page's root any more
                self.assertEqual(re.findall(r'token\("[a-z0-9-]+"\)', c), [])

    def test_the_chart_library_takes_an_element(self):
        e = src("components", "echarts.ts")
        self.assertIn("export function token(name: string, from?: Element | null): string {", e)
        self.assertIn("export function baseStyle(from?: Element | null) {", e)


class TheOneRule(unittest.TestCase):
    def block(self):
        css = src("app", "tokens.css")
        start = css.index("/* ---- session 241a")
        rest = css[start:]
        nxt = rest.find("/* ---- session", 10)
        return css, start, rest if nxt < 0 else rest[:nxt]

    def test_the_block_is_in_the_brand_section_and_scoped_to_the_wrapper(self):
        css, start, block = self.block()
        self.assertGreater(start, css.index("The brand, version 0"))
        self.assertGreater(start, css.index("text-wrap: pretty;"))          # after the last rule of session 211
        rules = re.sub(r"/\*[\s\S]*?\*/", "", block)
        selectors = [s.strip() for head in re.findall(r"([^{}]+)\{", rules) for s in head.split(",") if s.strip()]
        self.assertTrue(selectors)
        for s in selectors:
            self.assertTrue(s.startswith(".brand-a "), s)

    def test_the_rule_names_a_kind_of_markup_and_no_page(self):
        _, _, block = self.block()
        rules = re.sub(r"/\*[\s\S]*?\*/", "", block)
        self.assertIn('.brand-a [role="tooltip"]', rules)
        self.assertIn(".brand-a a.rounded", rules)
        for page in ("supply", "contracts", "bill", "customer", "shoulder", "curtailment", "queues", "awards", "alerts", "events", "policy"):
            self.assertNotIn(page, rules)
        self.assertIn(".brand-a tbody td.text-right.text-xs", rules)
        # it writes no color: a corner, a shadow, and the scale's small size for a cell the page set small
        self.assertEqual(sorted(set(re.findall(r"([a-z-]+):", rules))), ["border-radius", "box-shadow", "font-size"])
        self.assertEqual(re.findall(r"font-size: ([^;]+);", rules), ["12px"])

    def test_the_event_study_tables_scroll_inside_their_frame(self):
        e = src("components", "EventStudy.tsx")
        self.assertIn('<div className="overflow-x-auto">' + chr(10) + '      <table className="mb-2 w-full text-left text-sm">', e.replace(chr(13), ""))
        self.assertEqual(e.count('className="overflow-x-auto"'), 1)

    def test_the_rules_before_it_are_as_they_were(self):
        css, start, _ = self.block()
        before = css[:start]
        for words in (".brand-a h1 {", "font-size: 36px;", ".brand-a thead tr,", "border-bottom: 1px solid var(--color-ink);",
                      ".brand-a > div {", "--chart-blue: #3C6E9E;", ".brand-a .sm\\:grid-cols-3 > .border-t-2 {"):
            self.assertIn(words, before)


class NoDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        files = sorted({f for fs in PAGES.values() for f in fs}) + ["app/tokens.css"]
        for f in files:
            with self.subTest(file=f):
                self.assertNotIn(DASH, src(*f.split("/")))
        for parts in (("tests", "test_session241a.py"), ("archive", "sessions", "SESSION_241A_REPORT.md"), ("docs", "brand", "review-241a", "README.md")):
            path = os.path.join(ROOT, *parts)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    self.assertNotIn(DASH, f.read(), parts[-1])


if __name__ == "__main__":
    unittest.main()
