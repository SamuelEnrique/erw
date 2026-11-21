"""Session 9601 (chain 620, 20 November 2026): a method page's long word breaks instead of widening a phone's page.

Energy Research Warehouse (ERW). All 609 method pages were opened at 390 px on production. Six scrolled sideways, each
over one long unbroken word of the note's own text outside a code span: a file's path, a table's column
(`resources` 544 px wide over a 61-character file name; `interconnection_queue_summary` 421; `amm_guatemala_generation_monthly`
417; `ercot_dam_esr_awards` 411; `makstat_macedonia_electricity_monthly` 401; `statcan_oil_gas_supply_monthly` 392).
Session 22 had made code spans break and tables scroll inside themselves; plain text did neither.

Held here, on the source: the prose style breaks a word that does not fit its line, in paragraphs and list items; the
rule is the gentle one (a word that fits is laid out as before, and a table's columns are not squeezed); session 22's
two rules stand. With the rule put on production's pages in a browser, the six are 390 px wide and their tables keep
their widths. Nothing here sets the environment, reads a table or makes a request.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheProseStyle(unittest.TestCase):
    def setUp(self):
        self.g = src("site", "app", "globals.css")

    def test_a_word_that_does_not_fit_breaks_in_paragraphs_and_list_items(self):
        self.assertIn(".prose-erw p, .prose-erw li, .prose-erw dd { overflow-wrap: break-word; }", self.g)

    def test_it_is_the_gentle_rule_so_tables_keep_their_columns(self):
        rule = [l for l in self.g.splitlines() if l.startswith(".prose-erw p, .prose-erw li, .prose-erw dd {")]
        self.assertEqual(len(rule), 1)
        self.assertNotIn("anywhere", rule[0])
        self.assertNotIn("break-all", rule[0])
        self.assertNotIn("td", rule[0])

    def test_session_22s_rules_stand(self):
        self.assertIn("code { overflow-wrap: anywhere; }", self.g)
        self.assertIn(".prose-erw table { display: block; max-width: 100%; overflow-x: auto; }", self.g)
        self.assertIn(".prose-erw a { word-break: break-word; }", self.g)

    def test_the_method_page_draws_its_note_in_that_style(self):
        self.assertIn('<article className="prose-erw"', src("site", "app", "data", "methods", "[slug]", "page.tsx"))

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.g)
        self.assertNotIn(EM, src("tests", "test_session9601_method_pages_phone.py"))


if __name__ == "__main__":
    unittest.main()
