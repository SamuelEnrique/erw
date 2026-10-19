"""Session 304: the replication packages verified, the code-side rulings of 14 October, and the review note (the chain
prompt of 19 October 2026). What is held to:

  the four replication packages (the battery, the datacenter, the generator, the grid) each have a CSV, a do-file and
    a Python mirror beside it, and each do-file states at its top the values it must display at the page's defaults
    (session 304, from the mirrors' runs of 19 October); the generator's NPV applies solar's degradation of 0.7 percent
    a year in both languages (the page's default since session 298); the grid check treats a figure not held as the same
    absent figure whichever way it is written;
  the rulings of 18 October on items 2, 4, 5 and 10 of docs/state/morning_2026-10-14.md: the board test allows 10 days;
    the tracker says beside its newest figures that ERCOT paused approvals to energize on 3 August 2026, cited to the
    Batch Zero deck; /policy and /contracts write "as filed" beside a date after today; every verdict carries its day
    and the twelve of 14 October are in findingverdicts.ts, the four to drop shown as dismissed, the eight others as
    "no verdict yet";
  the review note docs/state/review_2026-10-19_code.md names every session of the chain, every screenshot folder,
    every decision made without Samuel and every item waiting for him; no em dash in any file the session wrote."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = ["site/public/seller/erw_2026_generator_replication.py", "site/public/seller/erw_2026_generator_replication.do", "site/public/datacenter/erw_2026_datacenter_replication.do",
         "site/public/grid/erw_2026_grid_replication.do", "site/public/battery/erw_2026_battery_replication.do", "site/scripts/check-grid-replication.mjs", "site/scripts/test-board.mjs",
         "site/app/datacenters/LargeLoad.tsx", "site/app/policy/PolicyTable.tsx", "site/app/contracts/page.tsx", "site/lib/findingverdicts.ts", "site/app/internal/findings/page.tsx",
         "docs/state/review_2026-10-19_code.md", "tests/test_session304.py", "tests/test_session267_findings.py"]
PACKAGES = {
    "battery": ("erw_2026_battery_dispatch.csv", "erw_2026_battery_replication.do", "erw_2026_battery_replication.py"),
    "datacenter": ("erw_2026_datacenter_hourly.csv", "erw_2026_datacenter_replication.do", "erw_2026_datacenter_replication.py"),
    "seller": ("erw_2026_generator_hourly.csv", "erw_2026_generator_replication.do", "erw_2026_generator_replication.py"),
    "grid": ("erw_2026_grid_replication.csv", "erw_2026_grid_replication.do", "erw_2026_grid_replication.py"),
}


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheReplicationPackages(unittest.TestCase):
    def test_each_package_is_whole_and_its_do_file_states_its_expected_values(self):
        for folder, names in PACKAGES.items():
            for n in names:
                self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "public", folder, n)), f"{folder}/{n}")
            do = src("site", "public", folder, names[1])
            head = do[:3000]
            self.assertIn("* Expected values (session 304, 19 October 2026): what this file displays at the page's defaults, equal to the page value by value;", head, folder)
            self.assertGreaterEqual(len(re.findall(r"^\*   .+(?:: | = ).*\d", head, flags=re.M)), 9, folder)
        self.assertIn("*   NPV at the hurdle rate, USD million for 100 MW: -76.66", src("site", "public", "seller", "erw_2026_generator_replication.do"))
        self.assertIn("*   revenue, last twelve months, USD per kW: 59.85", src("site", "public", "seller", "erw_2026_generator_replication.do"))
        self.assertIn("*   market energy, a flat load, last twelve months, USD per MWh: 33.73", src("site", "public", "datacenter", "erw_2026_datacenter_replication.do"))
        self.assertIn("*   last twelve months, all streams, USD per kW: 81.40", src("site", "public", "battery", "erw_2026_battery_replication.do"))
        self.assertIn("*   hour_shown = 2026-10-12T03:00:00Z", src("site", "public", "grid", "erw_2026_grid_replication.do"))

    def test_the_generator_mirror_and_do_file_apply_solars_degradation(self):
        py = src("site", "public", "seller", "erw_2026_generator_replication.py")
        self.assertIn("DEG = 0.007", py)
        self.assertIn('npv_kw = -CAPEX_USD_KW * (1 - DEBT_SHARE) + sum((out["l12_kw"] * (1 - DEG) ** (t - 1) - FOM_USD_KW_YEAR - debt_kw) / (1 + HURDLE) ** t for t in range(1, LIFE_YEARS + 1))', py)
        do = src("site", "public", "seller", "erw_2026_generator_replication.do")
        self.assertIn("scalar s_deg = 0.007", do)
        self.assertIn("forvalues t = 1/35 {", do)
        self.assertIn("scalar s_npv_kw = s_npv_kw + (s_l12_usd_per_mw / 1000 * (1 - s_deg)^(`t' - 1) - s_fom_usd_kw_year - s_debt_kw) / (1 + s_hurdle)^`t'", do)
        self.assertEqual(do.count("forvalues t = 1/35 {"), 1)

    def test_the_grid_check_reads_an_absent_figure_as_absent(self):
        c = src("site", "scripts", "check-grid-replication.mjs")
        self.assertIn('const ABSENT = new Set(["", "not held", "none", "NaN", "null", "undefined"]);', c)
        self.assertIn("if (ABSENT.has(String(ours).trim()) && (page === undefined || page === null || ABSENT.has(String(page).trim())))", c)
        self.assertIn('g.share === null || g.share === "" ? "" : Number(g.share).toFixed(6)', c)


class TheRulings(unittest.TestCase):
    def test_2_the_board_test_allows_ten_days(self):
        t = src("site", "scripts", "test-board.mjs")
        self.assertIn('<= 10 * b.DAY, r.id + " is stale: " + r.last.t);   // within 10 days of the build', t)
        self.assertNotIn("<= 7 * b.DAY", t)

    def test_4_the_tracker_says_the_pause_beside_its_newest_figures(self):
        p = src("site", "app", "datacenters", "LargeLoad.tsx")
        self.assertIn('data-load-pause="2026-08-03"', p)
        self.assertIn("on 3 August 2026 ERCOT paused approvals to energize datacenters", p)
        self.assertIn("Batch_Zero_Update_TAC_08262026.pptx", p)
        self.assertLess(p.index("</HeadlineRow>"), p.index('data-load-pause="2026-08-03"'))
        self.assertLess(p.index('data-load-pause="2026-08-03"'), p.index('<ChartFrame title="MW, by report"'))

    def test_5_as_filed_beside_a_future_date(self):
        pol = src("site", "app", "policy", "PolicyTable.tsx")
        self.assertIn('const today = new Date().toISOString().slice(0, 10);', pol)
        self.assertIn('{r.event_date}{r.event_date > today ? <span className="font-sans text-muted" data-as-filed="1"> as filed</span> : null}', pol)
        con = src("site", "app", "contracts", "page.tsx")
        self.assertIn('const today = new Date().toISOString().slice(0, 10);', con)
        self.assertIn('<>{r.event_date}{r.event_date > today ? <span className="text-muted" data-as-filed="1"> as filed</span> : null}</>', con)

    def test_10_every_verdict_has_its_day_and_the_twelve_of_14_october_are_in(self):
        ts = src("site", "lib", "findingverdicts.ts")
        self.assertIn('day: "2026-10-13" | "2026-10-14" };', ts)
        entries = re.findall(r'"(scan-[a-z]+-[0-9a-f]{12})": \{ block: (\d+), verdict: "(\w+)", reason: "(?:[^"\\]|\\.)*", by: "(\d+)", day: "(\d{4}-\d\d-\d\d)" \}', ts)
        self.assertEqual(len(entries), 40)
        of14 = [e for e in entries if e[4] == "2026-10-14"]
        self.assertEqual(len(of14), 12)
        self.assertEqual(sorted(int(e[1]) for e in of14), list(range(29, 41)))
        self.assertEqual(sum(1 for e in of14 if e[2] == "drop"), 4)
        self.assertTrue(all(e[3] == "286" for e in of14))
        page = src("site", "app", "internal", "findings", "page.tsx")
        self.assertIn('const day = v.day === "2026-10-14" ? "14 October 2026" : "13 October 2026";', page)
        self.assertIn('data-draft-verdict="pending"', page)
        self.assertIn("<strong>no verdict yet</strong>", page)
        self.assertIn('<strong>{v.day === "2026-10-14" ? "dismissed" : v.verdict}</strong>', page)
        self.assertNotIn("Verdict of 13 October 2026 (session", page)


class TheReviewNote(unittest.TestCase):
    def test_it_names_every_session_folder_decision_and_item(self):
        note = src("docs", "state", "review_2026-10-19_code.md")
        for s in range(295, 305):
            self.assertIn(f"Session {s}", note)
        for folder in ("review-296", "review-297", "review-298", "review-299", "review-300", "review-303", "review-304"):
            self.assertIn(f"docs/brand/{folder}/", note)
        for words in ("## What landed", "## The screenshot folders", "## Decisions made without you", "## Waiting for you"):
            self.assertIn(words, note)
        self.assertIn("https://erw-flame.vercel.app/", note)

    def test_no_em_dash_in_any_file_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
