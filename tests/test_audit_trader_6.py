"""Audit of the trader view, finding 6 (session 10209, docs/reviews/trader-model-audit-2026-11-26.md): the notes
described the trader view as it was. docs/methods/trader_view.md named `/markets` as the page that reads the tables
(retired in session 132: it redirects to /board, whose "The week, by hub" is the table's face); said a week mean needs
all 7 days, where warehouse/derived/board_page.py takes the on-peak mean of one or more (`need = 1`); and said the top
intervals come from "the latest 7 local days", where the 7 can run over more calendar days (13 to 20 October 2026 for
ERCOT and CAISO on the snapshot of 21 October). docs/platform-tools.md named `/markets` and "SPP real time (no table)".

1. The code and the site as they are (read from the sources). Passes on main.
2. The fix on this branch, words only: the notes say so. Fails on main. No figure moves."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class NotesDescribeTheTraderViewAsItIs(unittest.TestCase):
    def test_the_code_and_the_site(self):
        self.assertIn('{ source: "/markets", destination: "/board", permanent: true }', read("site", "next.config.ts"))
        self.assertIn('need = 1 if v == "da_onpeak_mean_usd" else len(ds)', read("warehouse", "derived", "board_page.py"))
        self.assertIn("week = sorted(full)[-7:]", read("warehouse", "derived", "trader_view.py"))

    def test_the_notes_say_so(self):
        t = read("docs", "methods", "trader_view.md")
        self.assertIn("since then `/markets` redirects to the price board, `/board`", t)
        self.assertIn("## On the page (`/markets` until session 132; now the price board's \"The week, by hub\" at `/board`)", t)
        self.assertIn("The on-peak mean is the exception", t)
        self.assertIn("The 7 need not run in a row", t)
        self.assertNotIn('otherwise the cell says "no data"', t)
        p = read("docs", "platform-tools.md")
        self.assertNotIn("SPP real time (no table)", p)
        self.assertIn("since session 132 the price board's \"The week, by hub\" at `/board`", p)


if __name__ == "__main__":
    unittest.main()
