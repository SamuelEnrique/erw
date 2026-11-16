"""Sessions 7401 and 7402 (chain 303): the two trackers' method notes and their decisions blocks.

The decisions of a tracker are one list (site/lib/decisions.ts), drawn at the foot of its page by the shared block
(site/components/tool/DecisionsBlock.tsx) with each choice's default and source as a hover tip, and written word for
word in the tracker's method note. These tests hold the note to the list, the block to its form (a list without a
default or a source is drawn as before, so the five tools' pages do not change), and the page to one block a view.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def decisions(name):
    """(key, session, ruling, text, default, source) of each line of one of the trackers' lists, as the file writes it."""
    s = src("site", "lib", "decisions.ts")
    part = s[s.index(f"export const {name}"):]
    part = part[:part.index("\n];")]
    q = r'"((?:[^"\x5c]|\x5c.)*)"'
    pat = r'\{ key: "([^"]+)", session: "([^"]+)"(?:, ruling: "([^"]+)")?,\s*\n\s*text: ' + q + r',\s*\n\s*def: ' + q + r',\s*\n\s*source: ' + q + r' \}'
    un = lambda t: t.replace(chr(92) + '"', '"')
    return [(m.group(1), m.group(2), m.group(3), un(m.group(4)), un(m.group(5)), un(m.group(6))) for m in re.finditer(pat, part)]


def note_lines(*parts):
    return [l for l in src(*parts).split("\n") if re.match(r"^\d+\. .*\*\*Default:\*\* .*\*\*Source:\*\* ", l)]


def line_of(i, row):
    key, session, ruling, text, d, source = row
    return f"{i}. {text} **Default:** {d} **Source:** {source} ({session}{'; ' + ruling if ruling else ''})"


class TheSharedBlock(unittest.TestCase):
    def test_a_default_and_a_source_are_a_hover_tip_and_only_where_given(self):
        b = src("site", "components", "tool", "DecisionsBlock.tsx")
        self.assertIn('import { Tip } from "@/components/tool/ToolPage";', b)
        self.assertIn("{d.def || d.source ? (", b)
        self.assertIn("<Tip id={`decision-${id}-${d.key}`} label=\"this choice's default and source\">", b)
        self.assertIn("<strong>Default:</strong> {d.def}", b)
        self.assertIn("<strong>Source:</strong> {d.source}", b)
        # the line itself is as the five tools' pages draw it
        self.assertIn('{d.text} <span className="text-xs text-muted">({d.session}{d.ruling ? `; ${d.ruling}` : ""})</span>', b)
        self.assertIn("def?: string; source?: string", src("site", "lib", "decisions.ts"))

    def test_the_five_tools_lists_give_neither_so_their_pages_do_not_change(self):
        s = src("site", "lib", "decisions.ts")
        before = s[:s.index("// Session 7402 (chain 303): the two trackers' decisions")]
        self.assertNotRegex(before, r"\n\s+def: \"")
        self.assertNotRegex(before, r"\n\s+source: \"")


class TheDatacenterTracker(unittest.TestCase):
    NAME, NOTE = "DATACENTER_TRACKER_DECISIONS", ("docs", "methods", "datacenter_tracker.md")

    def test_every_choice_has_its_default_and_its_source(self):
        rows = decisions(self.NAME)
        self.assertGreaterEqual(len(rows), 8)
        self.assertLessEqual(len(rows), 14)                                   # a handful: the choices that move the figures
        self.assertEqual(len({r[0] for r in rows}), len(rows))
        s = src("site", "lib", "decisions.ts")
        part = s[s.index(f"export const {self.NAME}"):]
        self.assertEqual(part[:part.index("\n];")].count("{ key: "), len(rows))   # every entry of the list was read
        for key, session, ruling, text, d, source in rows:
            self.assertRegex(session, r"^sessions? \d{2,4}", key)
            self.assertGreater(len(text), 60, key)
            self.assertGreater(len(d), 15, key)
            self.assertGreater(len(source), 25, key)

    def test_the_note_carries_the_list_word_for_word(self):
        rows = decisions(self.NAME)
        self.assertEqual(note_lines(*self.NOTE), [line_of(i, r) for i, r in enumerate(rows, 1)])

    def test_the_page_draws_the_block_once_a_view_at_its_foot(self):
        p = src("site", "app", "datacenters", "page.tsx")
        self.assertEqual(p.count("<DecisionsBlock "), 1)
        self.assertIn('<DecisionsBlock id="7402" title="Decisions on this page (each with its default and its source on hover)" items={DATACENTER_TRACKER_DECISIONS} />', p)
        self.assertEqual(p.count("{decisions}"), 2)                           # the facilities view and the view by grid
        self.assertLess(p.index("<PowerSide read={queues} />"), p.rindex("{decisions}"))
        self.assertLess(p.rindex("{decisions}"), p.index("<LargeLoadSource />"))   # before the source line, as the battery page's
        self.assertIn('<Link href="/data/methods/datacenter_tracker" className="underline">the tracker&apos;s method note</Link>', p)

    def test_the_note_has_the_done_lines_parts(self):
        n = src(*self.NOTE)
        for head in ("## 1. The two views", "## 2. What a facility is", "## 3. What a sum counts", "## 4. Megawatts", "## 5. Status, and what \"operating\" and \"planned\" mean",
                     "## 6. The grid of a facility", "## 7. Every figure, in the order the page shows it", "## 8. How ERCOT's section is built",
                     "## 9. What the tracker does not hold", "## 10. The replication", "## 11. The cross-checks", "## 12. The decisions on the page",
                     "## 13. What waits for the owner", "## Sign-off"):
            self.assertIn("\n" + head + "\n", n, head)
        for line in ("- Signed off by:", "- Date:", "- Items of section 13 ruled, and how:"):
            self.assertIn("\n" + line, n)
        self.assertNotIn("DECISIONS-LIST", n)
        for name in ("datacenter_facilities.md", "datacenter_projects.md", "datacenter_operator_sites.md", "datacenter_tracker_rollups.md", "ercot_large_load_status.md"):
            self.assertIn(f"]({name})", n, name)                              # it points to the tables' notes
        for parts in (("replication", "datacenter_tracker", "replicate.py"), ("replication", "datacenter_tracker", "fetch_rows.py"),
                      ("site", "scripts", "datacenter-tracker-figures.mjs")):
            self.assertTrue(os.path.exists(os.path.join(ROOT, *parts)), parts[-1])

    def test_the_notes_figures_are_the_days_figures(self):
        import json
        figures = {f["key"]: f["page"] for f in json.loads(src("replication", "datacenter_tracker", "page_figures.json"))["figures"]}
        n = src(*self.NOTE)
        whole = lambda v: f"{round(v):,}"
        for key, words in (("datacenters|count", "{} rows"), ("datacenters|counted", "{} of the 458"), ("datacenters|no_us_state", "({}: sites outside"),
                           ("datacenters|mw_total", "({} MW); 253 state none"), ("datacenters|status_mw|planned", "planned {} MW"),
                           ("datacenters|n_first_story", "{} of 458"), ("datacenters|sites_mw", "{} MW, more than"),
                           ("datacenters|rollup_mw|grid|-", "{} MW)."), ("dcchart|power|none|facilities", "{} of 274"),
                           ("dcq|ercot|-|active_mw", "{} MW in ERCOT's")):
            self.assertIn(words.format(whole(figures[key])), n, key)


class NoEmDash(unittest.TestCase):
    def test_no_em_or_en_dash_in_what_the_sessions_wrote(self):
        s = src("site", "lib", "decisions.ts")
        files = [src("docs", "methods", "datacenter_tracker.md"), s[s.index("// Session 7402 (chain 303): the two trackers' decisions"):],
                 src("tests", "test_session7402_trackers.py")]
        for text in files:
            for ch in (chr(0x2014), chr(0x2013)):
                self.assertNotIn(ch, text)


if __name__ == "__main__":
    unittest.main()
