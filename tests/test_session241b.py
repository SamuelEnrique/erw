"""Session 241, batch B: the pages of words on the brand.

The owner's task for session 241 (the chain prompt of 12 October 2026): the brand on every remaining page, through the
tokens and the shared components only; this session changes how a page looks, not what it says. Batch B is /about,
/terms, /privacy, /data with the data standard, the faults page and the method notes, the digest, the Roundup, the
email form, Ask, Thesis Builder, the two draft reports, the page a visitor is shown for a page in review, and the
internal pages.

  TheWrapper        each page of the batch wraps what it draws in <Brand> (components/Brand.tsx)
  NoColorOfItsOwn   no color literal and no font in a page's own files: the tokens only
  TheProse          rendered markdown takes the brand once, in app/tokens.css, for every page that carries prose-erw
  TheBlock          the session's block of app/tokens.css: scoped to the wrapper, named for markup and never for a page
  TheWordsStay      the page in review, the email form and Ask keep their words, their fields and their addresses
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = chr(0x2014)
APP = ("site", "app")

# every page of the batch: the file, and how many times it opens the wrapper (a page with two returns opens it twice)
PAGES = {
    ("about", "page.tsx"): 1,
    ("terms", "page.tsx"): 1,
    ("privacy", "page.tsx"): 1,
    ("data", "page.tsx"): 1,
    ("data", "standard", "page.tsx"): 1,
    ("data", "faults", "page.tsx"): 1,
    ("data", "methods", "[slug]", "page.tsx"): 1,
    ("digest", "page.tsx"): 1,
    ("digest", "[date]", "page.tsx"): 2,
    ("roundup", "page.tsx"): 2,
    ("roundup", "[week]", "page.tsx"): 1,
    ("subscribe", "page.tsx"): 1,
    ("_retired", "ask-original", "page.tsx"): 1,   # session 299: /ask is a redirect to the Grid tool's panel (no markup); the page of the batch is kept here
    ("ask", "ercot", "page.tsx"): 1,
    ("thesis", "page.tsx"): 1,
    ("reports", "draft", "ai-gigawatts", "page.tsx"): 1,
    ("reports", "draft", "shape-premium", "page.tsx"): 1,
    ("in-review", "page.tsx"): 1,
    ("internal", "ask", "page.tsx"): 1,
    ("internal", "costs", "page.tsx"): 1,
    ("internal", "findings", "page.tsx"): 2,
    ("internal", "health", "page.tsx"): 1,
    ("internal", "open", "page.tsx"): 1,
    ("internal", "usage", "page.tsx"): 2,
    ("internal", "waits", "page.tsx"): 2,
}
# files a page of the batch draws with and that are no other page's: they hold no color of their own either
OWN = [("site", "app", "ask", "AskForm.tsx"), ("site", "app", "ask", "ercot", "AskErcot.tsx")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def code(text):
    """A source file without its comments (line comments and JSX comments), for a search of what is drawn."""
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", text)


def block():
    """The session's block of app/tokens.css: from its heading to the next session's heading or the file's end."""
    css = src("site", "app", "tokens.css")
    start = css.index("/* ---- session 241b")
    rest = css[start + 10:]
    nxt = re.search(r"\n/\* ---- session (?!241b)", rest)
    return css[start:start + 10 + nxt.start()] if nxt else css[start:]


def selectors(css):
    """Every selector of a block of CSS, comments and at-rules' own lines left out."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    for head in re.findall(r"([^{}]+)\{", css):
        head = head.strip()
        if not head or head.startswith("@"):
            continue
        out += [s.strip() for s in head.split(",\n") if s.strip()]
    return out


class TheWrapper(unittest.TestCase):
    def test_every_page_of_the_batch_is_wrapped_in_the_brand(self):
        for name, opens in PAGES.items():
            page = src(*APP, *name)
            where = "/".join(name)
            self.assertIn('import { Brand } from "@/components/Brand";', page, where)
            self.assertEqual(len(re.findall(r"<Brand(?: noUsage)?>", page)), opens, where)
            self.assertEqual(page.count("</Brand>"), opens, where)

    def test_every_return_that_draws_is_inside_the_wrapper(self):
        # the page's own component (the default export) draws nothing outside the wrapper: each of its returns of JSX
        # opens with it
        for name in PAGES:
            page = src(*APP, *name)
            body = page[page.index("export default"):]
            for m in re.finditer(r"(?m)^(?:  |    )return \(\n\s*<([A-Za-z]*)", body):
                self.assertEqual(m.group(1), "Brand", "/".join(name))

    def test_a_page_whose_inputs_are_never_counted_says_so_on_the_wrapper(self):
        # the two internal pages that carried data-no-usage on their own root keep it there and say it on the wrapper
        for name in (("internal", "open", "page.tsx"), ("internal", "waits", "page.tsx")):
            page = src(*APP, *name)
            self.assertIn("<Brand noUsage>", page, "/".join(name))
            self.assertNotIn("<Brand>", page, "/".join(name))
            self.assertIn("data-no-usage", page, "/".join(name))

    def test_the_home_page_carries_the_wrapper_since_session_300(self):
        # session 241 left the home page outside the brand; session 300 (the owner's ruling of 18 October 2026) built it in the brand
        self.assertIn("<Brand>", src("site", "app", "page.tsx"))

    def test_the_wrapper_is_the_one_of_session_235(self):
        brand = src("site", "components", "Brand.tsx")
        self.assertIn("brand-a", brand)
        self.assertIn("data-no-usage={noUsage ? \"1\" : undefined}", brand)


class NoColorOfItsOwn(unittest.TestCase):
    def files(self):
        out = [("site", "app", *name) for name in PAGES] + OWN
        thesis = os.path.join(ROOT, "site", "components", "thesis")
        out += [("site", "components", "thesis", f) for f in sorted(os.listdir(thesis)) if f.endswith(".tsx")]
        return out

    def test_no_color_literal_in_a_page_of_the_batch(self):
        for name in self.files():
            text = code(src(*name))
            where = "/".join(name)
            self.assertEqual(re.findall(r"#[0-9A-Fa-f]{3,8}\b", text), [], where)
            self.assertNotRegex(text, r"rgba?\(|hsla?\(", where)

    def test_no_font_of_its_own(self):
        for name in self.files():
            self.assertNotRegex(code(src(*name)), r"fontFamily|font-family", "/".join(name))

    def test_the_tab_in_view_names_a_token(self):
        report = src("site", "components", "thesis", "Report.tsx")
        self.assertIn('style={{ color: on ? "var(--color-surface)" : "var(--color-ink)" }}', report)
        self.assertIn("--color-surface:", src("site", "app", "tokens.css"))

    def test_the_charts_of_thesis_builder_read_the_tokens_at_their_own_box(self):
        charts = src("site", "components", "thesis", "ThesisCharts.tsx")
        self.assertEqual(charts.count("baseStyle(el)"), 2)
        self.assertNotIn("baseStyle()", charts)
        self.assertNotRegex(charts, r'token\("[a-z-]+"\)')
        echarts = src("site", "components", "echarts.ts")
        self.assertIn("export function token(name: string, from?: Element | null)", echarts)
        self.assertIn("export function baseStyle(from?: Element | null)", echarts)

    def test_a_forms_one_action_is_the_brands(self):
        # cardinal with white words, as the battery form's button (docs/brand.md, section 2: a control in its active state)
        battery = src("site", "app", "cost-of-power", "battery", "BatteryForm.tsx")
        self.assertIn('className="border border-accent bg-accent px-4 py-1.5 text-white"', battery)
        subscribe = src(*APP, "subscribe", "page.tsx")
        self.assertEqual(len(re.findall(r'<button type="submit" className="border border-accent bg-accent px-4 py-1\.5 (?:text-sm )?text-white">', subscribe)), 2)
        self.assertIn('<button type="submit" className="border border-accent bg-accent px-4 py-2 text-white">Open the internal view</button>', src(*APP, "internal", "open", "page.tsx"))


class TheProse(unittest.TestCase):
    def test_the_rules_of_rendered_markdown_are_written_once_under_the_wrapper(self):
        b = block()
        for rule in (".brand-a .prose-erw {", ".brand-a .prose-erw > * {", ".brand-a .prose-erw h1 {", ".brand-a .prose-erw h2 {", ".brand-a .prose-erw h3 {",
                     ".brand-a .prose-erw th {", ".brand-a .prose-erw code {", ".brand-a .prose-erw pre {"):
            self.assertIn(rule, b)
        self.assertIn("max-width: 68ch;", b)                                   # the measure
        th = b[b.index(".brand-a .prose-erw th {"):]
        th = th[:th.index("}")]
        self.assertIn("background: transparent;", th)                          # no band
        self.assertIn("border-bottom: 1px solid var(--color-ink);", th)        # one dark rule under the header
        codeRule = b[b.index(".brand-a .prose-erw code {"):]
        self.assertIn("font-family: var(--font-mono);", codeRule[:codeRule.index("}")])

    def test_the_sites_own_rules_for_markdown_stand_as_they_were(self):
        # the pages outside the wrapper (the Games content links to none, the home page draws none) and any page not
        # yet on the brand keep the rules of app/globals.css; the brand's are added, scoped, in app/tokens.css
        g = src("site", "app", "globals.css")
        self.assertIn(".prose-erw { line-height: 1.6; max-width: 72ch; }", g)
        self.assertNotIn(".brand-a", g)

    def test_every_page_that_draws_markdown_in_the_batch_is_wrapped(self):
        for name in PAGES:
            page = src(*APP, *name)
            if "prose-erw" in page:
                self.assertIn("<Brand", page, "/".join(name))


class TheBlock(unittest.TestCase):
    def test_the_block_is_in_the_brand_section_after_session_211s(self):
        css = src("site", "app", "tokens.css")
        self.assertEqual(css.count("/* ---- session 241b"), 1)
        self.assertLess(css.index("/* ---- session 211"), css.index("/* ---- session 241b"))

    def test_every_rule_is_scoped_to_the_wrapper(self):
        for s in selectors(block()):
            self.assertTrue(s.startswith(".brand-a"), s)

    def test_no_rule_is_named_for_a_page(self):
        b = re.sub(r"/\*.*?\*/", "", block(), flags=re.S)
        for word in ("in-review", "data-thesis", "data-privacy", "data-faults", "data-health", "data-usage", "data-waits", "data-drafts", "digest", "roundup", "subscribe", "about"):
            self.assertNotIn(word, b, word)

    def test_no_color_literal_in_the_block(self):
        b = re.sub(r"/\*.*?\*/", "", block(), flags=re.S)
        self.assertEqual(re.findall(r"#[0-9A-Fa-f]{3,8}\b", b), [])
        self.assertNotRegex(b, r"rgba?\(")

    def test_the_rules_before_the_block_are_session_211s(self):
        # no existing rule of the brand was changed: the lines the battery page takes its look from stand as they were
        css = src("site", "app", "tokens.css")
        head = css[:css.index("/* ---- session 2", css.index("/* ---- session 211") + 10)]
        self.assertIn(".brand-a p,\n.brand-a figcaption,\n.brand-a [data-default] {\n  text-wrap: pretty;\n}\n", head)
        self.assertIn(".brand-a thead tr,\n.brand-a [data-scenario-table] thead tr {\n  background: transparent;\n  color: var(--color-muted);\n  border-bottom: 1px solid var(--color-ink);\n}", head)


class TheWordsStay(unittest.TestCase):
    def test_the_page_in_review_says_what_it_said(self):
        page = src(*APP, "in-review", "page.tsx")
        self.assertIn('<h1 className="mb-2 font-serif text-3xl text-accent">{path ? nameOf(path) : "This tool"}</h1>', page)
        self.assertIn('<p className="mb-6 text-base">This tool is in review and will open when it is approved.</p>', page)
        self.assertLess(page.index("This tool is in review"), page.index('<ToolSection title="Open now">'))
        self.assertIn('<ToolSection title="Open now">', page)
        self.assertIn('<li><Link href="/">Home</Link></li>', page)
        self.assertIn('<li key={p.href}><Link href={p.href}>{p.label}</Link><span className="text-muted">: {p.line}</span></li>', page)
        self.assertIn('data-in-review="1"', page)
        self.assertIn('robots: { index: false, follow: false }', page)

    def test_the_shared_section_draws_its_title_before_its_list(self):
        tool = src("site", "components", "tool", "ToolPage.tsx")
        section = tool[tool.index("export function ToolSection"):tool.index("export function HeadlineNumber")]
        self.assertLess(section.index("{title}</h2>"), section.index("{children}"))

    def test_the_email_form_sends_what_it_sent(self):
        page = src(*APP, "subscribe", "page.tsx")
        for piece in ('<form method="post" action="/api/subscribe"', '<form method="post" action="/api/unsubscribe"', 'name="email" type="email" required maxLength={254}',
                      '<input type="checkbox" name="daily" defaultChecked />', '<input type="checkbox" name="weekly" />', '<input type="checkbox" name="topic" value={t.id} defaultChecked />',
                      '<input name="website" type="text" tabIndex={-1} autoComplete="off" />', '<input type="hidden" name="confirm" value="yes" />'):
            self.assertIn(piece, page)

    def test_ask_keeps_its_form(self):
        form = src(*APP, "ask", "AskForm.tsx")
        self.assertIn('{busy ? "Querying the warehouse" : "Ask"}', form)
        self.assertNotIn("<Brand", form)                                         # the page wraps it

    def test_no_em_dash_in_what_the_session_wrote(self):
        files = [("site", "app", *name) for name in PAGES] + [("site", "app", "tokens.css"), ("tests", "test_session241b.py"),
                 ("site", "components", "thesis", "Report.tsx"), ("site", "components", "thesis", "ThesisCharts.tsx")]
        for name in files:
            self.assertNotIn(DASH, src(*name), "/".join(name))


if __name__ == "__main__":
    unittest.main()
