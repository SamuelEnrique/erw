"""Session 351 (the chain of 20 October 2026, night, second part): the six answers of the owner's review of 19 October
(given on 20 October) and the words. /terms names the email a reader leaves on Research and who answers it, within a
week, with no promise of an analysis; the shared heat map takes a two-hue ramp where its figure is signed and keeps one
color for a magnitude; the day-ahead column and the hunt's floor are recorded as ruled. Energy Research Warehouse (ERW)."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheTerms(unittest.TestCase):
    def test_the_research_email_and_its_answer_are_named(self):
        t = src("site", "app", "terms", "page.tsx")
        self.assertIn('<Section title="Questions sent from Research" id="research">', t)
        self.assertIn("answers it by email within a week; an answer is\n          not a promise of an analysis.", t)
        self.assertIn("the email address left for\n          the answer", t)
        # the form's own words agree: the address is used for the answer alone and shown to no visitor
        self.assertIn("Stored with the request and used to send the answer; nothing else is done with it, and it is shown to no visitor.", src("site", "components", "analysis", "AskForm.tsx"))


class TheHeatMaps(unittest.TestCase):
    def test_a_signed_figure_takes_two_hues_and_a_magnitude_one(self):
        s = src("site", "components", "svgchart.tsx")
        self.assertIn("const signed = lo < 0 && hi > 0, far = Math.max(-lo, hi);", s)
        self.assertIn('const fillOf = (v: number) => (signed ? (v < 0 ? "var(--chart-blue)" : "var(--color-accent)") : "var(--color-accent)");', s)
        self.assertIn('data-heat-scale={signed ? "diverging" : "one"}', s)
        self.assertIn("--chart-blue:", src("site", "app", "tokens.css"))
        self.assertIn("**Heat maps** (the owner's ruling of 20 October 2026)", src("docs", "brand.md"))


class TheRulingsRecorded(unittest.TestCase):
    def test_the_floor_and_the_column(self):
        self.assertIn("**Ruled (20 October 2026).** The owner ruled that the floor stays at one typical yearly move", src("docs", "methods", "automated_analysis_findings.md"))
        self.assertIn("STRENGTH_FLOOR = 1.0", src("warehouse", "analysis", "findings", "hunt.py"))
        self.assertIn("The owner ruled on 20 October 2026\n  that the column stays", src("docs", "methods", "power_prices.md"))


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "app", "terms", "page.tsx"), ("site", "components", "svgchart.tsx"), ("docs", "brand.md"),
                      ("docs", "methods", "automated_analysis_findings.md"), ("docs", "methods", "power_prices.md"), ("tests", "test_session351.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
