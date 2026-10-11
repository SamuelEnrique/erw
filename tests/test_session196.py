"""Session 196: the three decision pages against what others publish. What is held to:

  the two defaults the owner ruled on, each with its citation: the hurdle rate is Lazard's weighted cost, 9.6 percent
    (0.6 x 8 + 0.4 x 12), on the three pages; a battery's degradation is Lazard's 2.6 percent a year, on the battery
    page and for the generator page's battery, and for no other asset;
  each of the three Method notes ends with a section "Cross-checks": one table, one row a comparison, with our figure,
    the published figure, its source, the gap and the reason; no row lacks a reason, and every published figure names
    where it was read;
  each page's source line says "Checked against:" with the count of rows of its note's table and a link to the section;
  nothing of a publisher is copied into the site: site/public holds no file of theirs;
  the three pages stay in review.

No request, no model call; the environment is read, never set."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
NOTES = {
    "battery_earns_algorithm": ("site/app/cost-of-power/battery/page.tsx", 9),
    "generator_earns_algorithm": ("site/app/cost-of-power/seller/page.tsx", 10),
    "datacenter_pays_algorithm": ("site/app/cost-of-power/page.tsx", 6),
}
FILES = [f"docs/methods/{n}.md" for n in NOTES] + [p for p, _ in NOTES.values()] + [
    "site/lib/battery/finance.ts", "site/lib/seller/finance.ts", "site/lib/datacenter/finance.ts", "site/app/cost-of-power/seller/SellerScenarios.tsx",
    "tests/test_session196.py", "archive/sessions/SESSION_196_REPORT.md"]


def src(rel):
    with open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


def table(note):
    """The rows of the note's Cross-checks table, each a list of five cells."""
    part = note[note.index("\n## Cross-checks"):]
    rows = [line for line in part.split("\n") if line.startswith("| ")]
    cells = [[c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))] for line in rows]
    return cells[0], cells[1:]


class TheDefaults(unittest.TestCase):
    def test_the_hurdle_rate_is_lazards_weighted_cost_on_the_three_pages(self):
        for lib in ("battery", "seller"):
            text = src(f"site/lib/{lib}/finance.ts")
            self.assertIn("export const HURDLE = 9.6;", text, lib)
            self.assertIn('"60% debt at an 8% interest rate and 40% equity at a 12% cost". The default is that weighted cost, 0.6 x 8 + 0.4 x 12 = ${HURDLE} percent', text, lib)
            self.assertIn("hurdle: HURDLE };", text, lib)
        dc = src("site/lib/datacenter/finance.ts")
        self.assertIn("export const LIFE = 20, HURDLE = 9.6;", dc)
        self.assertIn('"60% debt at an 8% interest rate and 40% equity at a 12% cost". The default is that weighted cost, 0.6 x 8 + 0.4 x 12 = 9.6 percent', dc)
        self.assertAlmostEqual(0.6 * 8 + 0.4 * 12, 9.6)

    def test_a_batterys_degradation_is_lazards_and_no_other_assets(self):
        battery = src("site/lib/battery/finance.ts")
        self.assertIn("export const DEG = 2.6;", battery)
        self.assertIn("deg: DEG, life: 20, hurdle: HURDLE };", battery)
        self.assertIn("(LCOS v10.0): battery degradation of 2.6 percent a year in its utility-scale cases of 2 and 4 hours", battery)
        seller = src("site/lib/seller/finance.ts")
        self.assertIn("export const BATTERY_DEG = 2.6;", seller)
        self.assertIn("deg: costs.deg ?? 0,", seller)
        self.assertIn("The model has no loss of output with age. No cited rate is held, so the default is none", seller)   # solar, wind, a peaker
        page = src("site/app/cost-of-power/seller/page.tsx")
        self.assertIn('...(asked.asset === "battery" ? { deg: BATTERY_DEG, degSource: BATTERY_DEG_SOURCE } : {})', page)


class TheCrossChecks(unittest.TestCase):
    def test_each_note_ends_with_the_section_and_its_anchor(self):
        for name in NOTES:
            note = src(f"docs/methods/{name}.md")
            self.assertEqual(note.count("\n## Cross-checks\n"), 1, name)
            self.assertTrue(note.rstrip().split("\n## ")[-1].startswith("Cross-checks"), name)             # the last section
            self.assertIn('<a id="cross-checks"></a>\n\n## Cross-checks\n', note, name)
            self.assertIn("Every published figure was read on 11 October 2026 from the address given, after the host's robots file and terms", note, name)

    def test_one_row_a_comparison_with_a_gap_and_a_reason(self):
        for name, (_, count) in NOTES.items():
            head, rows = table(src(f"docs/methods/{name}.md"))
            self.assertEqual(head, ["Our figure", "Published figure", "Source and date", "Gap", "Reason"], name)
            self.assertEqual(len(rows), count, name)
            for r in rows:
                self.assertEqual(len(r), 5, f"{name}: {r[0][:50]}")
                for cell in r:
                    self.assertTrue(cell, f"{name}: an empty cell in {r[0][:50]}")
                self.assertGreater(len(r[4]), 30, f"{name}: the reason of {r[0][:50]}")              # a gap without a reason is not written
                # the source is linked, or it is the warehouse's own table of the publisher's data, or "the same" as the row above
                self.assertTrue("](https://" in r[2] or "`ercot_storage_dam_awards_monthly`" in r[2] or r[2] == "the same", f"{name}: {r[2][:60]}")

    def test_the_sources_are_the_ones_read(self):
        every = "".join(src(f"docs/methods/{n}.md") for n in NOTES)
        for address in ("https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf", "https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage",
                        "https://atb.nlr.gov/electricity/2025/utility-scale_pv", "https://atb.nlr.gov/electricity/2025/land-based_wind",
                        "https://www.caiso.com/documents/2024-special-report-on-battery-storage-may-29-2025.pdf", "https://www.eia.gov/electricity/wholesale/",
                        "https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a"):
            self.assertIn(address, every, address)
        for host in ("pjm.com", "misoenergy.org"):
            self.assertNotIn(host, every, host)

    def test_each_page_says_what_it_was_checked_against(self):
        for name, (page, count) in NOTES.items():
            text = src(page)
            self.assertEqual(text.count("data-checked-against="), 1, name)
            self.assertIn(f'<span data-checked-against="{count}">Checked against: {count} published figures (', text, name)
            self.assertIn(f'<Link href="/data/methods/{name}#cross-checks">Each comparison, with its gap and the reason</Link>', text, name)

    def test_nothing_of_a_publisher_is_copied_into_the_site(self):
        for d, _, files in os.walk(os.path.join(ROOT, "site", "public")):
            for f in files:
                self.assertNotRegex(f.lower(), r"lazard|lcoe|special-report-on-battery|ice_electric|epm_table|land-based_wind|utility-scale_", os.path.join(d, f))
        self.assertIn("runs/", src(".gitignore"))                                                     # the saved reads are not in git

    def test_the_three_pages_stay_in_review(self):
        rel = src("site/lib/release.ts")
        for page in ("/cost-of-power/battery", "/cost-of-power/seller", "/cost-of-power"):
            self.assertIn(f'"{page}": "review",', rel, page)


class House(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            if os.path.exists(os.path.join(ROOT, *f.split("/"))):
                self.assertNotIn(EM, src(f), f)


if __name__ == "__main__":
    unittest.main()
