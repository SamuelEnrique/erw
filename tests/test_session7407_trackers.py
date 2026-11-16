"""Session 7407 (chain 303): the two trackers' signature pack and the chain's closing note.

The pack's expected values and its "ours" figures are held to the day's figures of the two replications, and each
tool's five choices to the decisions the page draws, so the pack a person signs from cannot drift from the files.
"""

import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def figures(tool):
    return {f["key"]: f["page"] for f in json.loads(src("replication", tool, "page_figures.json"))["figures"]}


whole = lambda v: f"{round(v):,}"
PACK = ("docs", "reviews", "trackers-signature-pack-2026-11-16.md")


class ThePack(unittest.TestCase):
    def test_per_tool_what_is_signed_five_choices_the_cross_check_and_the_stata_commands(self):
        p = src(*PACK)
        for head in ("## 1. The datacenter power tracker (`/datacenters`)", "## 2. The deal tracker (`/deals`)", "## 3. What waits for your ruling, with the default each stands on",
                     "## 4. What needs the key"):
            self.assertIn("\n" + head, p, head)
        for tool, note in (("datacenter_tracker", "docs/methods/datacenter_tracker.md"), ("deals", "docs/methods/deal_tracker.md")):
            self.assertIn(f"**You sign:** `{note}`, section \"Sign-off\".", p)
            self.assertIn(f'cd "C:\\path\\to\\erw\\replication\\{tool}"', p)
            self.assertTrue(os.path.exists(os.path.join(ROOT, *note.split("/"))))
            self.assertIn("## Sign-off", src(*note.split("/")))
        self.assertEqual(p.count("**The five choices that matter most**"), 2)
        self.assertEqual(p.count("do replicate.do"), 2)
        for part in p.split("**The five choices that matter most**")[1:]:
            rows = [l for l in part.split("**Cross-checks**")[0].split("\n") if l.startswith("| ") and not l.startswith("| Choice")]
            self.assertEqual(len(rows), 5)                                    # five, each with a default and a source
            for r in rows:
                self.assertEqual(r.count(" | "), 2, r[:60])

    def test_the_expected_values_are_the_days_figures(self):
        p, dc, de = src(*PACK), figures("datacenter_tracker"), figures("deals")
        for line in (f"- 1. facilities held: {whole(dc['datacenters|count'])}",
                     f"- 2. counted in the sums (a named US state, not cancelled): {whole(dc['datacenters|counted'])}",
                     f"- 3. megawatts stated by the counted facilities: {whole(dc['datacenters|mw_total'])}",
                     f"- 4. counted facilities that state megawatts: {whole(dc['datacenters|n_with_mw'])}",
                     "- 5. ERCOT, megawatts approved to energize, newest report (2026-06-19): 8,927",
                     f"- 1. deals held, the register's folded pairs counted once: {whole(de['tracker|deals'])}",
                     f"- 2. deals that state a size in MW: {whole(de['tracker|with_mw'])}",
                     f"- 3. megawatts stated by them: {whole(de['tracker|mw'])}",
                     f"- 4. deals that state a value in US dollars: {whole(de['tracker|with_dollars'])}",
                     f"- 5. deals tagged AI power: {whole(de['tracker|view|ai'])}",
                     f"- 6. deals that state a price in US dollars per MWh: {whole(de['tracker|with_price'])}",
                     "**454 of 454 inside the tolerance**", "**1,123 of 1,124 inside the tolerance; the one difference is named**"):
            self.assertIn(line, p, line)
        self.assertEqual(dc["series|ercot_large_load_status|ercot:large_load|approved_to_energize_mw|2026-06-19T00:00:00Z"], 8927)
        # the pack's lines are the do-files' own expected lines
        for tool in ("datacenter_tracker", "deals"):
            do = src("replication", tool, "replicate.do")
            for n, words in re.findall(r"\*   (\d)\. ([^\n]+)", do):
                self.assertIn(f"- {n}. {words}", p, words)

    def test_the_rulings_and_the_costs_are_the_reports(self):
        p = src(*PACK)
        self.assertEqual(len(re.findall(r"(?m)^\d+\. ", p.split("## 3. What waits for your ruling")[1].split("## 4.")[0])), 13)
        self.assertIn("USD 3.0 for the 814 stories behind those rows; USD 10.6 for every story the extraction has checked (2,899)", p)
        self.assertIn("**about USD 4 for the two narrow readings; about USD 13.5 for both tables whole**", p)
        self.assertAlmostEqual(2899 * 0.00365 + 1077 * 0.00273, 13.5, delta=0.1)

    def test_the_note_says_each_tool_against_its_done_line(self):
        n = src("docs", "state", "note_2026-11-17_portable_c303.md")
        for said in ("**Model spend: USD 0.**", "## Each tool against its done line", "454 of 454", "1,123 of 1,124", "## What needs the key (not run; costs summed)",
                     "## What waits for you (each with its default; the work stands on the default)", "## What waits for the data machine", "**No next file**"):
            self.assertIn(said, n, said)

    def test_no_em_or_en_dash(self):
        for parts in (PACK, ("docs", "state", "note_2026-11-17_portable_c303.md"), ("tests", "test_session7407_trackers.py")):
            for ch in (chr(0x2014), chr(0x2013)):
                self.assertNotIn(ch, src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
