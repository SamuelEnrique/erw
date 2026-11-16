"""Sessions 7405 and 7406 (chain 303): the deal tracker's method note, its decisions block, its cross-check and its
Stata do-file.

The decisions are one list (site/lib/decisions.ts, DEAL_TRACKER_DECISIONS), drawn by the shared block above session
465's list of every choice, and written word for word in the note. The note's and the cross-check's figures are held
to the day's figures (replication/deals/page_figures.json); the do-file's expected values are the same figures, and
its Python mirror gives the lines on deals made up for the test.
"""

import csv
import importlib.util
import json
import os
import re
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REP = os.path.join(ROOT, "replication", "deals")
NOTE = ("docs", "methods", "deal_tracker.md")
CROSS = ("docs", "methods", "crosschecks", "deal_tracker.md")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def decisions(name):
    s = src("site", "lib", "decisions.ts")
    part = s[s.index(f"export const {name}"):]
    part = part[:part.index("\n];")]
    q = r'"((?:[^"\x5c]|\x5c.)*)"'
    pat = r'\{ key: "([^"]+)", session: "([^"]+)"(?:, ruling: "([^"]+)")?,\s*\n\s*text: ' + q + r',\s*\n\s*def: ' + q + r',\s*\n\s*source: ' + q + r' \}'
    un = lambda t: t.replace(chr(92) + '"', '"')
    return part, [(m.group(1), m.group(2), m.group(3), un(m.group(4)), un(m.group(5)), un(m.group(6))) for m in re.finditer(pat, part)]


def figures():
    return {f["key"]: f["page"] for f in json.loads(src("replication", "deals", "page_figures.json"))["figures"]}


whole = lambda v: f"{round(v):,}"
two = lambda v: f"{v:,.2f}".rstrip("0").rstrip(".")


class TheDecisions(unittest.TestCase):
    def test_every_choice_has_its_default_and_its_source(self):
        part, rows = decisions("DEAL_TRACKER_DECISIONS")
        self.assertEqual(part.count("{ key: "), len(rows))                    # every entry of the list was read
        self.assertGreaterEqual(len(rows), 8)
        self.assertLessEqual(len(rows), 14)
        self.assertEqual(len({r[0] for r in rows}), len(rows))
        for key, session, ruling, text, d, source in rows:
            self.assertRegex(session, r"^sessions? \d{2,4}", key)
            self.assertGreater(len(text), 60, key)
            self.assertGreater(len(d), 10, key)
            self.assertGreater(len(source), 25, key)
        keys = {r[0] for r in rows}
        for asked in ("a-deal", "one-deal", "stated-only", "medians", "ai-power", "sure"):   # what the chain asked the note to say
            self.assertIn(asked, keys)

    def test_the_note_carries_the_list_word_for_word(self):
        _, rows = decisions("DEAL_TRACKER_DECISIONS")
        want = [f"{i}. {t} **Default:** {d} **Source:** {s} ({ses}{'; ' + r if r else ''})" for i, (_, ses, r, t, d, s) in enumerate(rows, 1)]
        got = [l for l in src(*NOTE).split("\n") if re.match(r"^\d+\. .*\*\*Default:\*\* .*\*\*Source:\*\* ", l)]
        self.assertEqual(got, want)

    def test_the_page_draws_the_shared_block_above_the_older_list(self):
        d = src("site", "app", "deals", "Decisions.tsx")
        self.assertEqual(d.count("<DecisionsBlock "), 1)
        self.assertIn('<DecisionsBlock id="7405" title="Decisions on this page (each with its default and its source on hover)" items={DEAL_TRACKER_DECISIONS} />', d)
        self.assertLess(d.index("<DecisionsBlock "), d.index("<Fold title="))
        self.assertIn("Every choice, with the session that made it (${DECISIONS.length})", d)
        self.assertGreaterEqual(len(re.findall(r'\{ choice: "', d)), 15)      # session 465's list is as it was
        self.assertIn('<Link href="/data/methods/deal_tracker" className="underline">the tracker&apos;s method note</Link>', d)
        self.assertIn("<DealsDecisions />", src("site", "app", "deals", "page.tsx"))


class TheNote(unittest.TestCase):
    def test_it_says_what_the_chain_asked(self):
        n = src(*NOTE)
        for head in ("## 1. The views", "## 2. What a deal is, and is not", "## 3. One deal, one row: how two stories are folded",
                     "## 4. How megawatts, US dollars and a price are read, and when they are empty", "## 5. How a deal is tagged AI power", "## 6. The grid of a deal",
                     "## 7. Every figure, view by view", "### 7.1 The table", "### 7.2 The tracker tab", "### 7.3 The comparables and the disclosed prices",
                     "### 7.4 The AI-power view", "### 7.5 The charts", "### 7.6 Capital flows", "## 8. What the tracker cannot see", "## 9. The replication and the cross-checks",
                     "## 10. What a second reading of the older rows would change (not run)", "## 11. The decisions on the page", "## 12. What waits for the owner", "## Sign-off"):
            self.assertIn("\n" + head, n, head)
        for said in ("**\"Sure\"** is the extraction's own confidence", "only where three or more deals of the group state the figure", "energy's where its asset is energy",
                     "written in no prompt and no rubric", "A join keeps the earliest date", "never replaces a figure held", "- Signed off by:", "- Items of section 12 ruled, and how:"):
            self.assertIn(said, n, said)
        self.assertNotIn("DECISIONS-LIST", n)
        for name in ("energy_deals.md", "deal_counterparties.md"):
            self.assertIn(f"]({name})", n, name)

    def test_the_rule_the_note_says_is_unwritten_is_unwritten(self):
        prompt = src("warehouse", "deals", "extract.py")
        self.assertNotRegex(prompt.lower(), r"asset is (not )?(an )?energy|energy asset")   # when the rule is written, the note and faults row 28 change

    def test_the_notes_figures_are_the_days_figures(self):
        f, n = figures(), src(*NOTE)
        for words in (f"({whole(f['table|rows'])} rows, the newest deal dated",
                      f"{whole(f['tracker|type|other'])} of the {whole(f['tracker|deals'])} deals",
                      f"{whole(f['tracker|with_mw'])} of the {whole(f['tracker|deals'])} deals state one ({whole(f['tracker|mw'])} MW in all)",
                      f"{whole(f['tracker|with_dollars'])} of the {whole(f['tracker|deals'])} state one",
                      f"{whole(f['table|with_flags'])} rows",
                      f"{whole(f['tracker|with_state'])} of the {whole(f['tracker|deals'])} deals name a US state",
                      f"{whole(f['deals|ai_tagged'])} of the {whole(f['tracker|deals'])} deals are tagged; {whole(f['deals|ai_deals|supply|capital'])} of them are capital deals",
                      f"{whole(f['deals|ai_deals|supply|compute'])} are compute capacity",
                      f"{whole(f['tracker|with_grid'])} of the {whole(f['tracker|deals'])} deals have one",
                      f"{whole(f['deals|month_count|2026-11'])} deals, {two(f['deals|month_mw|2026-11'])} MW from the {whole(f['table|month_with_mw|2026-11'])} that state it, {whole(f['deals|month_ai_pct|2026-11'])} percent",
                      f"from {f['table|sure_min']} to {f['table|sure_max']} on the rows held",
                      f"power purchases {two(f['deals|comp_median_mw|type|ppa'])} MW (of the {whole(f['deals|comp_with_mw|type|ppa'])} that state one)",
                      f"the year 2026 {two(f['deals|comp_median_mw|year|2026'])} MW (of {whole(f['deals|comp_with_mw|year|2026'])})",
                      "**1,123 of 1,124 inside the tolerance; the one difference is named**"):
            self.assertIn(words, n, words)
        self.assertEqual(sum(1 for k in f if k.startswith("deals|comp_median_mw|")), 14)        # "Fourteen groups have a median size"
        self.assertEqual(sum(1 for k in f if k.startswith("deals|comp_median_price|")), 0)      # "no median price is shown anywhere"
        self.assertEqual(f["deals|priced"], 0)
        ai_mw = sum(v for k, v in f.items() if k.startswith("deals|ai_mw|supply|"))
        self.assertIn(f"{two(ai_mw)} MW from the {whole(sum(v for k, v in f.items() if k.startswith('deals|ai_with_mw|supply|')))} that state them", n)


class TheCrossCheck(unittest.TestCase):
    def test_ours_is_the_days_figures(self):
        f, c = figures(), src(*CROSS)
        self.assertIn(f"{whole(f['table|rows'])} rows of `energy_deals`", c)
        self.assertIn(f"({whole(f['tracker|deals'])} deals)", c)
        self.assertIn(f"| 2026 (to 13 November) | {whole(f['tracker|year|2026'])} |", c)
        self.assertIn(f"| 2025 (January to April, October to December) | {whole(f['tracker|year|2025'])} |", c)
        self.assertIn(f"{whole(f['tracker|type|ppa'])}", f"{36 + 3}")                           # the two years' power purchases are the tracker's count
        self.assertIn(f"| 0 of {whole(f['tracker|deals'])} |", c)                             # a price in US dollars per MWh
        self.assertIn(f"{whole(f['deals|ai_deals|supply|nuclear'])} of them tagged AI power", c)
        year = lambda y, stat: sum(v for k, v in f.items() if k.startswith(f"deals|ai_{stat}|quarter|{y}-"))
        self.assertIn(f"| {whole(year('2026', 'deals'))} | {whole(year('2026', 'with_mw'))} | {two(year('2026', 'mw'))} |", c)
        self.assertIn(f"| {whole(year('2025', 'deals'))} | {whole(year('2025', 'with_mw'))} | {two(year('2025', 'mw'))} |", c)
        mw_2026 = sum(v for k, v in f.items() if k.startswith("deals|chart_mw|2026-") and not k.endswith("|without"))
        self.assertIn(f"| 38 | {whole(mw_2026)} |", c)

    def test_the_published_figures_have_their_publisher_and_date_and_no_quoted_text(self):
        c = src(*CROSS)
        for said in ("Corporate Energy Buyers Association (CEBA)", "17 March 2026", "BloombergNEF", "19 February 2026", "LevelTen Energy", "14 April 2026",
                     "No figure of the tracker was adjusted to match one.", "17 of the 20 figures are in a headline of their own story",
                     "They are not called wrong; they are not checked."):
            self.assertIn(said, c, said)
        table = c[c.index("| The tracker's figure |"):c.index("## 2. The twenty largest")]
        self.assertNotIn('"', table.replace('"other"', ""))                   # facts with a link; the one quoted word is the tracker's own kind
        for host in ("ceba.org", "about.bnef.com", "www.leveltenenergy.com"):
            self.assertIn(f"`{host}`", c, host)

    def test_the_faults_the_cross_check_names_are_in_the_faults_file(self):
        t = src("docs", "reviews", "deals-faults-2026-11-11.md")
        new = t[t.index("## Found by chain 303"):]
        for n in range(22, 30):
            self.assertIn(f"\n| {n} | ", new, n)
        self.assertEqual(len(re.findall(r"\| owner \| ruling \|", new)), 3)
        self.assertEqual(len(re.findall(r"\| desktop \| data machine \|", new)), 4)
        self.assertIn("### The three rows marked `ruling`, in plain words, with the default each stands on", new)


class TheDoFile(unittest.TestCase):
    def test_its_expected_values_are_the_days_figures(self):
        do, f = src("replication", "deals", "replicate.do"), figures()
        for line in (f"*   1. deals held, the register's folded pairs counted once: {whole(f['tracker|deals'])}",
                     f"*   2. deals that state a size in MW: {whole(f['tracker|with_mw'])}",
                     f"*   3. megawatts stated by them: {whole(f['tracker|mw'])}",
                     f"*   4. deals that state a value in US dollars: {whole(f['tracker|with_dollars'])}",
                     f"*   5. deals tagged AI power: {whole(f['tracker|view|ai'])}",
                     f"*   6. deals that state a price in US dollars per MWh: {whole(f['tracker|with_price'])}"):
            self.assertIn(line, do, line)
        self.assertIn("This do-file has not been run: Stata is not installed on the machine that wrote it.", do)
        self.assertIn('drop if folded_duplicate == "1"', do)

    def test_the_mirror_prints_the_lines_on_made_up_deals(self):
        spec = importlib.util.spec_from_file_location("deals_replicate_headline", os.path.join(REP, "replicate.py"))
        rep = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rep)
        head = ["event_id", "date", "deal_type", "kind", "status", "mw", "usd_per_mwh", "dollars", "ai_power", "state", "technology", "confidence", "folded_duplicate"]
        rows = [["t1", "2026-11-03", "ppa", "ppa", "signed", "100", "42.5", "", "true", "TX", "solar", "0.8", "0"],
                ["t2", "2026-08-02", "m_and_a", "m_and_a", "signed", "", "", "3800000000", "false", "", "gas", "0.8", "0"],
                ["t3", "2026-08-02", "m_and_a", "m_and_a", "rumored", "900", "", "", "false", "", "gas", "0.5", "1"],
                ["t4", "2025-12-15", "equity_raise", "", "", "", "", "120000000", "true", "", "fusion", "0.7", "0"]]
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "deals_slim.csv"), "w", encoding="utf-8", newline="") as fh:
                fh.write("# made up for the test\n")
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(head)
                w.writerows(rows)
            lines, by = rep.headline(tmp)
        self.assertEqual([v for _, v in lines], [3, 1, 100.0, 2, 2, 1])       # the folded duplicate's 900 MW leaves with its row
        self.assertEqual(by[("2026", "ppa")], (1, 1, 100.0))
        self.assertEqual(by[("2025", "other")], (1, 0, 0.0))                  # a kind left empty is "other"


class NoEmDash(unittest.TestCase):
    def test_no_em_or_en_dash_in_what_the_sessions_wrote(self):
        faults = src("docs", "reviews", "deals-faults-2026-11-11.md")
        s = src("site", "lib", "decisions.ts")
        for text in (src(*NOTE), src(*CROSS), src("replication", "deals", "replicate.do"), faults[faults.index("## Found by chain 303"):],
                     s[s.index("/** /deals, the deal tracker"):], src("tests", "test_session7405_trackers.py")):
            for ch in (chr(0x2014), chr(0x2013)):
                self.assertNotIn(ch, text)


if __name__ == "__main__":
    unittest.main()
