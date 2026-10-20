"""Session 319: cold_2026, the events page, and the stale faults of session 270 (the chain of 19 October, daytime).
What is held to:

  /events/cold-2026 is built on the cold_2025 template for the data machine's window of 23 January to 2 February 2026
    (session 308; the window is in lib/eventstudy.ts), with its six grids, its five hubs, the baseline the same
    weekdays 364 and 728 days earlier, the event study and the shared chart components; the events index carries its
    card; the value and route checks read the page;
  /prices: a day-ahead cell with no row for the hour says what the table holds (the fault was the data: four grids'
    day-ahead tables held no row of the last day on 19 October), the hour asked being the render time's as before;
  /deals and the companies tab: a select is no wider than the page, so nothing scrolls sideways at a phone's width;
  /board: up and down are not colored as good and bad (docs/brand.md): both tokens are the ink, the sign is written;
  no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = ["site/app/events/cold-2026/page.tsx", "site/app/events/page.tsx", "site/app/prices/page.tsx", "site/app/deals/DealsTable.tsx", "site/app/companies/CompaniesTable.tsx",
         "site/app/tokens.css", "site/scripts/check-values.mjs", "site/scripts/check-routes.mjs", "tests/test_session319.py"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheColdOf2026(unittest.TestCase):
    def test_the_page_is_on_the_cold_2025_template_for_the_data_machines_window(self):
        page = src("site", "app", "events", "cold-2026", "page.tsx")
        model = src("site", "app", "events", "cold-2025", "page.tsx")
        self.assertIn('const EV = "cold_2026";', page)
        self.assertIn('start="2026-01-23"', page)
        self.assertIn('end="2026-02-02"', page)
        self.assertIn('const inWin = (d: string) => d >= "2026-01-23" && d <= "2026-02-02";', page)
        self.assertIn('cold_2026: ["2026-01-23", "2026-02-02"]', src("site", "lib", "eventstudy.ts"))
        for bit in ('hub="ercot:HB_HUBAVG"', '{ entity: "miso:INDIANA.HUB", name: "MISO Indiana Hub", rtNote: "an hour" }', '{ entity: "nyiso:N.Y.C.", name: "NYISO New York City", rtNote: "15 minutes, time-weighted" }',
                    '{ entity: "isone:.H.INTERNAL_HUB", name: "ISO-NE Internal Hub", rtNote: "15 minutes" }', '{ entity: "spp:SPPNORTH_HUB", name: "SPP North Hub", rtNote: "15 minutes" }'):
            self.assertIn(bit, page, bit)
            self.assertIn(bit, model, bit)
        for g in ("eia930:PJM", "eia930:MISO", "eia930:SWPP", "eia930:NYIS", "eia930:ISNE", "eia930:ERCO"):
            self.assertIn(f'{{ entity: "{g}"', page, g)
        self.assertIn('<EventStudy event="cold_2026" grids={["eia930:PJM", "eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:NYIS", "eia930:SWPP"]} primary="eia930:PJM" price />', page)
        self.assertIn("<EventWindow", page)
        self.assertNotIn("echarts", page)
        # the words name the days the data machine's note names (docs/methods/events.md, session 308)
        note = src("docs", "methods", "events.md")
        self.assertIn("## Session 308: the late January 2026 cold (`cold_2026`)", note)
        for d in ("26 January 2026", "25 January", "27 January", "29 January", "7 February"):
            self.assertIn(d, page, d)

    def test_the_index_carries_the_ninth_card_and_the_checks_read_the_page(self):
        idx = src("site", "app", "events", "page.tsx")
        self.assertIn('{ href: "/events/cold-2026", title: "The late January 2026 cold: six grids", dates: "2026-01-23 to 2026-02-02"', idx)
        self.assertIn('event: "cold_2026"', idx)
        self.assertEqual(idx.count('href: "/events/'), 9)
        self.assertIn('"/events/cold-2026",   // session 319', src("site", "scripts", "check-values.mjs"))
        self.assertIn('"/events/cold-2026",  // session 319', src("site", "scripts", "check-routes.mjs"))


class TheThreeFaultsOf270(unittest.TestCase):
    def test_prices_a_missing_day_ahead_cell_says_what_the_table_holds(self):
        p = src("site", "app", "prices", "page.tsx")
        self.assertIn("function daWhy(rows: SeriesRow[], table: string, since: string): string {", p)
        self.assertIn("its newest hour held is", p)
        self.assertIn("data-da-missing={e}", p)
        self.assertIn("function daNow(rows: SeriesRow[], now: number): SeriesRow | null {", p)   # the hour asked is unchanged
        self.assertIn("if (t <= now && now < t + 3_600_000) return r;", p)

    def test_deals_and_companies_selects_are_no_wider_than_the_page(self):
        d = src("site", "app", "deals", "DealsTable.tsx")
        self.assertIn('<label className="flex min-w-0 max-w-full flex-col gap-1 text-xs text-muted">', d)
        self.assertIn('className="max-w-full border border-rule bg-panel px-2 py-1 text-sm text-ink"', d)
        c = src("site", "app", "companies", "CompaniesTable.tsx")
        self.assertIn('className="mt-1 max-w-full border border-rule bg-panel px-2 py-1 text-sm text-ink"', c)

    def test_board_up_and_down_take_the_ink(self):
        css = src("site", "app", "tokens.css")
        ink = re.search(r"--color-ink: (#[0-9A-Fa-f]{6});", css).group(1)
        self.assertEqual(re.search(r"--color-up: (#[0-9A-Fa-f]{6});", css).group(1), ink)
        self.assertEqual(re.search(r"--color-down: (#[0-9A-Fa-f]{6});", css).group(1), ink)
        self.assertNotIn("#175E54", css)
        self.assertIn("Up and down are never colored as good and bad", src("docs", "brand.md"))
        # the sign is still written beside a move
        self.assertIn("signed(m.ch, row.unit)", src("site", "components", "board", "BoardView.tsx"))


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
