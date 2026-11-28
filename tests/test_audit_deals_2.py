"""Audit of the energy deal tracker, finding 2 (session 10215, docs/reviews/deals-model-audit-2026-11-26.md): the
decisions under every tab of /deals say that, from 21 October 2026, "every view draws the hold's sentence and the count of
rows it covers, and nothing of a row". The companies tab, drawn above those decisions, reads energy_companies, which is
not held: 541 of its 562 rows (25 November 2026) are the held deals' buyers, sellers and other parties, each with its
deals' types and technologies as tags, the place a deal states (195 rows) and the stories' links.

1. The site's license file holds energy_deals ("license needed") and not energy_companies, and the companies tab reads
   energy_companies (site/lib/data.ts, companies()). Passes on main.
2. The fix on this branch, words only: decision 13 (site/lib/decisions.ts and the method note, word for word) says every
   view of the deals draws nothing of a row and the companies tab, not held, shows the deals' parties with their tags,
   places and links; the method note's hold paragraph counts them. Whether those rows are held with the deals is for the
   owner's ruling. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheCompaniesTabAndTheHold(unittest.TestCase):
    def test_the_deals_are_held_and_the_companies_are_not(self):
        tables = json.loads(src("site", "data", "license_status.json"))["tables"]
        self.assertEqual(tables["energy_deals"]["status"], "license needed")
        self.assertNotEqual(tables.get("energy_companies", {}).get("status"), "license needed")
        data = flat(src("site", "lib", "data.ts"))
        self.assertIn('table_name: "eq.energy_companies"', data)
        self.assertIn("<CompaniesView />", src("site", "app", "deals", "page.tsx"))

    def test_decision_13_says_what_the_companies_tab_shows(self):
        # session 11405 (wip/ready-held-out, the weekend page's decision 1): the deal-seeded rows are held with the deals
        text = ("From 21 October 2026 the deals are held whole for a license: every view of the deals draws the hold's sentence and the count "
                "of rows it covers, and nothing of a row. The companies tab reads energy_companies without the rows seeded from the deals' "
                "parties while the deals are held: those rows carry the deals' types and technologies, the place a deal states and the "
                "stories' links, so only the Thesis Builder's researched companies are shown.")
        default = "Held whole; no deal's row is shown, nor the companies seeded from the deals' parties."
        self.assertIn(f'text: "{text}"', src("site", "lib", "decisions.ts"))
        self.assertIn(f'def: "{default}"', src("site", "lib", "decisions.ts"))
        note = src("docs", "methods", "deal_tracker.md")
        self.assertIn(f"13. {text} **Default:** {default} **Source:**", note)
        self.assertIn("541 of its 562 rows (25 November 2026) are the deals' buyers, sellers and other parties", flat(note))


if __name__ == "__main__":
    unittest.main()
