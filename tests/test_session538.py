"""Session 538: the Grid's and Research's cross-checks read by the check (chain 024, 21 to 22 October 2026).

Energy Research Warehouse (ERW). Session 381 wrote the section "Cross-checks" of the Grid tool's note
(docs/methods/grid_network.md, 11 rows) and of Research's (docs/methods/automated_analysis_findings.md, 4 rows), and
site/scripts/check-cross-checks.mjs read only the three decision pages. Since session 538 the script reads the two
sections too: the five columns, no empty cell, a reason in every row, every source a link, "the same" or an ERW Method
note that opens, as many rows as the note's markdown and never fewer than session 381 wrote; and where a row names a
figure by its key (a finding card, the Network view's replication file) the figure's own source equals the row and the
gap is ours less theirs. On a built site it also reads each card page's callout by its check key.

What is held here: the script's file mode (--files, no browser, no server, no request) passes on the repository; each
planted fault in a copy of the files it reads (a gap, an empty reason, a row taken away, a source without a link, a
card's figure, the replication file's demand, a thesis figure) makes it exit 1 and names the fault; the script keeps
the three decision pages' checks; no em dash in the files this session wrote. Nothing here sets the environment, reads
a warehouse table or makes a request.

    python -m unittest tests.test_session538 -v
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "site", "scripts", "check-cross-checks.mjs")
NODE = shutil.which("node")
READ = ["docs/methods/grid_network.md", "docs/methods/automated_analysis_findings.md", "docs/methods/ercot_peak_premium.md",
        "site/data/findings/batteries_lunch_grids.json", "site/data/findings/queue_divorce.json",
        "site/public/grid/erw_2026_grid_replication.csv"]
WRITTEN = ["site/scripts/check-cross-checks.mjs", "tests/test_session538.py", "archive/sessions/SESSION_538_REPORT.md"]


def src(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def run(root=None):
    args = [NODE, SCRIPT, "--files"] + (["--root", root] if root else [])
    return subprocess.run(args, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)


@unittest.skipUnless(NODE, "no node on this machine: the script cannot be run here")
class TheFileMode(unittest.TestCase):
    def test_it_passes_on_the_repository(self):
        p = run()
        self.assertEqual(p.returncode, 0, p.stdout[-3000:] + p.stderr[-2000:])
        m = re.search(r"check-cross-checks --files: all (\d+) passed", p.stdout)
        self.assertIsNotNone(m, p.stdout[-800:])
        self.assertGreaterEqual(int(m.group(1)), 55)
        for line in ("grid_network: the table has the 11 rows of the note's markdown (never fewer than 11)",
                     "automated_analysis_findings: the table has the 4 rows of the note's markdown (never fewer than 4)",
                     "grid_network: NYISO: the gap is ours less theirs: 9",
                     "automated_analysis_findings: the published figure is the thesis's in the note the row cites (ercot_peak_premium, all_p999, 2025): 311.80 and 311.8"):
            self.assertIn(line, p.stdout)
        self.assertNotIn("FAIL", p.stdout)


@unittest.skipUnless(NODE, "no node on this machine: the script cannot be run here")
class APlantedFaultIsCaught(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw538-")
        for rel in READ:
            dst = os.path.join(self.tmp, *rel.split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(ROOT, *rel.split("/")), dst)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def edit(self, rel, old, new, count=1):
        path = os.path.join(self.tmp, *rel.split("/"))
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        self.assertIn(old, text, rel)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text.replace(old, new, count))

    def fails(self, *expected):
        p = run(self.tmp)
        self.assertEqual(p.returncode, 1, p.stdout[-3000:] + p.stderr[-2000:])
        fails = [ln for ln in p.stdout.splitlines() if ln.startswith("FAIL")]
        for e in expected:
            self.assertTrue(any(e in ln for ln in fails), f"{e!r} not among {fails}")

    def test_the_copy_unchanged_passes(self):
        p = run(self.tmp)
        self.assertEqual(p.returncode, 0, p.stdout[-3000:])

    def test_a_gap_that_is_not_ours_less_theirs(self):
        self.edit("docs/methods/grid_network.md", "| 0, 0, +9 MW |", "| 0, 0, +8 MW |")
        self.fails("grid_network: NYISO: the gap is ours less theirs")

    def test_an_empty_reason(self):
        self.edit("docs/methods/grid_network.md", "| The three grids whose ties close EIA's balance |", "|  |")
        self.fails("grid_network: every row has our figure, the published figure, its source, the gap and a reason")

    def test_a_row_taken_away(self):
        path = os.path.join(self.tmp, "docs", "methods", "automated_analysis_findings.md")
        with open(path, encoding="utf-8", newline="") as f:
            lines = f.read().split("\n")
        i = next(k for k, ln in enumerate(lines) if ln.startswith("| The marriage and divorce rates"))
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(lines[:i] + lines[i + 1:]))
        self.fails("automated_analysis_findings: the table has the 3 rows of the note's markdown (never fewer than 4)",
                   'automated_analysis_findings: the row "The marriage and divorce rates" is in the table')

    def test_a_source_without_a_link(self):
        self.edit("docs/methods/automated_analysis_findings.md", '[CDC/NCHS FastStats, "Marriage and Divorce"](https://www.cdc.gov/nchs/fastats/marriage-divorce.htm)',
                  'CDC/NCHS FastStats, "Marriage and Divorce"')
        self.fails('automated_analysis_findings: every source is a link, "the same", or an ERW Method note that opens')

    def test_a_card_figure_that_moved(self):
        path = os.path.join(self.tmp, "site", "data", "findings", "batteries_lunch_grids.json")
        with open(path, encoding="utf-8") as f:
            card = json.load(f)
        card["numbers"]["ercot_median_last"] = 25.7
        with open(path, "w", encoding="utf-8") as f:
            json.dump(card, f)
        self.fails("automated_analysis_findings: the card's figure (numbers.ercot_median_last) is the row's")

    def test_the_replication_file_disagrees(self):
        self.edit("site/public/grid/erw_2026_grid_replication.csv", "demand,ERCO,,2026-10-12T03:00:00Z,60735,MW", "demand,ERCO,,2026-10-12T03:00:00Z,60736,MW")
        self.fails("grid_network: ERCOT: EIA-930's demand less net generation is the row's published figure")

    def test_a_thesis_figure_the_note_does_not_hold(self):
        self.edit("docs/methods/ercot_peak_premium.md", "| all_median | 20.49 | 25.68 |", "| all_median | 20.49 | 25.69 |")
        self.fails("automated_analysis_findings: the published figure is the thesis's in the note the row cites (ercot_peak_premium, all_median, 2025)")


class TheScript(unittest.TestCase):
    def test_it_keeps_the_three_decision_pages(self):
        s = src("site/scripts/check-cross-checks.mjs")
        for page, note in (("/cost-of-power/battery", "battery_earns_algorithm"), ("/cost-of-power/seller", "generator_earns_algorithm"), ("/cost-of-power", "datacenter_pays_algorithm")):
            self.assertIn(f'["{page}", "{note}"]', s)
        self.assertIn('["Our figure", "Published figure", "Source and date", "Gap", "Reason"]', s)   # test_session448 reads these two
        self.assertIn("r[4].text.length > 30", s)

    def test_it_reads_the_two_notes_and_their_card_keys(self):
        s = src("site/scripts/check-cross-checks.mjs")
        self.assertIn('{ note: "grid_network", floor: 11, page: "/grid" }', s)
        self.assertIn('{ note: "automated_analysis_findings", floor: 4, page: "/research" }', s)
        for key in ("finding|batteries_lunch_grids|callout|0|after|ercot", "finding|queue_divorce|callout|0|before|-",
                    "finding|queue_divorce|callout|2|before|-", "finding|queue_divorce|callout|2|after|-"):
            self.assertIn(key, s)

    def test_the_card_keys_are_the_ones_the_card_draws(self):
        # components/analysis/FindingCard.tsx: finding|<card>|callout|<i>|before or after|<grid of the period and label>
        fc = src("site/components/analysis/FindingCard.tsx")
        self.assertIn("`finding|${card.card_id}|callout|${i}|${side}|${gridOfWords(`${c[side].period} ${c.label}`)}`", fc)
        lunch = json.loads(src("site/data/findings/batteries_lunch_grids.json"))
        self.assertIn("ERCOT", lunch["callouts"][0]["label"])
        self.assertEqual(lunch["callouts"][0]["after"]["period"], "2025")
        queue = json.loads(src("site/data/findings/queue_divorce.json"))
        for i in (0, 2):
            words = queue["callouts"][i]["label"] + " " + queue["callouts"][i]["before"]["period"] + " " + queue["callouts"][i]["after"]["period"]
            self.assertIsNone(re.search(r"\b(ERCOT|CAISO|PJM|MISO|SPP|NYISO|ISO-NE)\b", words), words)

    def test_no_page_changed(self):
        # the script changes no page: no "Checked against" line on /grid or /research (session 381's ruling item)
        for rel in ("site/app/grid/page.tsx", "site/app/research/page.tsx"):
            self.assertNotIn("data-checked-against", src(rel), rel)

    def test_no_em_dash(self):
        for rel in WRITTEN:
            p = os.path.join(ROOT, *rel.split("/"))
            if os.path.exists(p):
                self.assertNotIn(chr(0x2014), src(rel), rel)


if __name__ == "__main__":
    unittest.main()
