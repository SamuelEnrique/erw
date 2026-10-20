"""Session 328 (the chain of 20 October 2026, night): /board and /prices finished to the five tools' standard, lighter
(roadmap v3 of 13 October 2026). The shared downloads of a page's public tables (components/tool/TableDownloads.tsx and
the Python and Stata readers of /api/download), the board's threshold default in grey with a Reset, the first tab of
/prices with its method note, and the two notes brought up to date. Energy Research Warehouse (ERW)."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheDownloads(unittest.TestCase):
    def setUp(self):
        self.c = src("site", "components", "tool", "TableDownloads.tsx")
        self.r = src("site", "app", "api", "download", "route.ts")

    def test_the_component_offers_three_files_a_public_table_and_says_why_not_otherwise(self):
        c = self.c
        self.assertIn("const cat = await attempt(catalogue);", c)
        self.assertIn(".filter((t) => live.has(t))", c)                      # a name not in the public catalogue is left out
        for kind in ('data-download="csv"', 'data-download="python"', 'data-download="stata"'):
            self.assertEqual(c.count(kind), 1, kind)
        self.assertIn("href={`/api/download?table=${t}&as=py`}", c)
        self.assertIn("href={`/api/download?table=${t}&as=do`}", c)
        self.assertIn('data-not-held="license"', c)                          # held, as /data says it
        self.assertIn('data-not-held="live-set"', c)                         # not in the live set: on Redivis
        self.assertIn("<Link href=\"/data\">Data and methods</Link>", c)     # a failed read sends the reader to /data

    def test_the_route_answers_a_reader_only_after_its_own_checks(self):
        r = self.r
        at = r.index('if (as === "py" || as === "do") return reader(table, as, new URL(req.url).origin);')
        self.assertGreater(at, r.index("is not in the site's live set"))      # the license, the limit, public and live first
        self.assertGreater(at, r.index('const lim = await limited(req, "download", 60, 3600);'))
        self.assertNotIn("export function readerText", r)                      # a route file exports route fields only
        self.assertIn('"Content-Disposition": `attachment; filename="erw_${table}.${as}"`', r)

    def test_the_readers_skip_the_provenance_and_compute_nothing(self):
        r = self.r
        body = r[r.index("function readerText("):r.index("const reader = ")]
        self.assertIn('while n < len(lines) and lines[n].startswith(\\"#\\"):', body)
        self.assertIn("pd.read_csv(io.StringIO", body)
        self.assertIn("if substr(`\\\"`macval(line)'\\\"', 1, 1) != \\\"#\\\" continue, break", body)
        self.assertIn("import delimited using `raw', varnames(`=`n' + 1')", body)
        for op in (" * ", " / ", ".sum(", ".mean(", "collapse", "egen"):
            self.assertNotIn(op, body.replace("/api/download", ""), op)


class TheBoard(unittest.TestCase):
    def test_the_page_passes_its_tables_to_the_foot_of_the_board(self):
        page = src("site", "app", "board", "page.tsx")
        self.assertIn("<BoardView file={file} footer={<TableDownloads tables={TABLES} />} />", page)
        tables = re.findall(r'"([a-z0-9_]+)"', page[page.index("const TABLES"):page.index("export default")])
        self.assertEqual(len(tables), 15)
        view = src("site", "components", "board", "BoardView.tsx")
        self.assertIn("export function BoardView({ file, footer }: { file: BoardFile; footer?: ReactNode }) {", view)
        self.assertIn("      </div>\n      {footer}\n    </div>\n  );\n}", view)

    def test_the_threshold_says_its_default_as_the_library_sets_it(self):
        bench = src("site", "components", "board", "Workbench.tsx")
        lib = src("site", "lib", "board.ts")
        self.assertIn('row?.unit === "USD/MWh" ? 100 : NaN', lib)               # benchOf's rule
        self.assertIn('const thDefault = row.unit === "USD/MWh" ? 100 : NaN;', bench)
        self.assertIn('data-default="th">Default: {row.unit === "USD/MWh" ? "USD 100 per MWh for a power price" : "halfway from the window\'s mean to its high"}', bench)
        self.assertIn('data-reset="th" aria-label="Reset the threshold" onClick={() => set({ th: thDefault })}', bench)
        self.assertIn("if (Number.isFinite(b.th) && b.th !== base.th) q.set(\"th\", String(b.th));", lib)   # the default leaves the address

    def test_the_note_says_what_the_page_draws_today(self):
        note = src("docs", "methods", "price_board.md")
        self.assertIn("## As the page stands (session 328, 20 October 2026)", note)
        self.assertIn("USD 100 per MWh for a power price", note)


class ThePrices(unittest.TestCase):
    def test_both_tabs_offer_their_tables_and_the_first_names_its_method(self):
        page = src("site", "app", "prices", "page.tsx")
        self.assertIn('<Link href="/data/methods/power_prices">Method</Link>', page)
        self.assertIn('tab === "ercot" ? ["ercot_peak_premium_annual", "ercot_peak_premium_monthly"] : MARKETS.flatMap((m) => [m.rt?.table, m.da.table])', page)
        self.assertIn("export const revalidate = 900;", page)

    def test_the_method_note_matches_the_page(self):
        note = src("docs", "methods", "power_prices.md")
        self.assertIn("(`revalidate = 900`)", note)
        self.assertIn("`latest_prices`", note)
        self.assertIn('*/15 * * * *', src(".github", "workflows", "latest-prices.yml"))   # the 15 minutes the note says
        for iso in ("ERCOT", "CAISO", "NYISO", "MISO", "SPP", "ISO-NE"):
            self.assertIn(f'"iso": "{iso}"', src("site", "data", "markets.json"))
        premium = src("docs", "methods", "ercot_peak_premium.md")
        self.assertIn("## On the site (session 328, 20 October 2026)", premium)


class TheBoxPlot(unittest.TestCase):
    def test_a_label_past_the_edge_is_written_inside_it(self):
        s = src("site", "components", "svgchart.tsx")
        self.assertIn("const far = px(mx) + 6 + textWidth(num(md), 11) > W - 2;", s)
        self.assertIn('<text x={far ? W - 2 : px(mx) + 6} y={far ? y - 13 : y + 4} textAnchor={far ? "end" : undefined}', s)

    def test_the_caption_says_what_the_svg_chart_does(self):
        e = src("site", "app", "explorer", "ercot-peak-premium", "Explorer.tsx")
        self.assertNotIn("drag the slider", e)
        self.assertIn("a whisker that reaches\n              past it stops at its edge", e)


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "components", "tool", "TableDownloads.tsx"), ("site", "app", "api", "download", "route.ts"), ("site", "app", "board", "page.tsx"),
                      ("site", "app", "prices", "page.tsx"), ("site", "components", "board", "Workbench.tsx"), ("site", "components", "board", "BoardView.tsx"),
                      ("docs", "methods", "power_prices.md"), ("docs", "methods", "price_board.md"), ("docs", "methods", "ercot_peak_premium.md"),
                      ("tests", "test_session328.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
