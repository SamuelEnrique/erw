"""Session 7204 (chain 302): the policy monitor read as a regulator's staffer would read it, for ten states, and the
site faults the read found.

The read is docs/reviews/policy-read-2026-11-16.md. Its site rows are fixed in the laws block (site/app/policy/
StateLaws.tsx), the monitor's State filter and the All grids tab's changes; the drawn pages are held by Node
(site/scripts/test-large-load-render.mjs and test-large-load-rules.mjs, which tests/test_session7201_large_load_on_site.py
runs). This file holds the read itself and the fixes' place in the source.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheRead(unittest.TestCase):
    def test_every_row_is_fixed_requested_or_written_for_a_ruling(self):
        doc = src("docs", "reviews", "policy-read-2026-11-16.md")
        rows = re.findall(r"(?m)^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (site|data machine|ruling) \| ([^|]+) \|$", doc)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, 12)), "eleven rows, numbered in order")
        for n, _, _, _, kind, state in rows:
            if kind == "site":
                self.assertTrue(state.strip().startswith("fixed"), f"row {n}: a site fault is fixed")
            elif kind == "data machine":
                self.assertRegex(state, r"requested \(row \d+\)", f"row {n}: a data fault names its request")
            else:
                self.assertIn("default", state, f"row {n}: a ruling is written with its default")
        self.assertEqual(sorted(int(x) for r in rows for x in re.findall(r"requested \(row (\d+)\)", r[5])), [26, 27, 28, 29])

    def test_the_ten_states_counts_are_the_files(self):
        """The table of the read: each state's rules read, as the page file counts them."""
        with open(os.path.join(ROOT, "site", "data", "siting", "large_load_rules.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        n = lambda st: sum(1 for r in f["rules"] + f["held_rules"] if st in re.findall(r"\b[A-Z]{2}\b", r["state"]))  # noqa: E731
        self.assertEqual([n(s) for s in ("TX", "VA", "AZ", "OH", "GA", "UT", "AK", "WV", "KY", "MI")], [11, 8, 3, 4, 1, 1, 0, 1, 4, 6])
        doc = src("docs", "reviews", "policy-read-2026-11-16.md")
        for state, cell in (("Texas", "11, with 13 changes in 90 days"), ("Virginia", "8"), ("Arizona", "3"), ("Ohio", "4"), ("Georgia", "1"), ("Kentucky", "4"), ("Michigan", "6")):
            self.assertRegex(doc, rf"(?m)^\| {state} \|.*\| {re.escape(cell)} \|$", state)
        searches = {x["state"]: x["kind"] for x in f["law_searches"]}
        self.assertEqual((searches["TX"], searches["GA"], searches["KY"], searches["AZ"], searches.get("AK")), ("withheld", "not read", "not read", "none found", None))


class TheFixes(unittest.TestCase):
    def test_a_state_with_no_law_is_never_said_to_have_none(self):
        s = src("site", "app", "policy", "StateLaws.tsx")
        self.assertNotIn("was read for", s)
        self.assertNotIn("are held for other states", s)
        self.assertIn("lawSearchOf(file.searches, s)", s)
        self.assertIn("data-law-withheld={w.state}", s)
        self.assertIn("label={NOT_SHOWN}", s, "a bill withheld for a robots file is not called license needed")
        lib = src("site", "lib", "largeloadrules.ts")
        self.assertIn('"none found": "none found where searched"', lib)
        self.assertIn("It is not proof that none exists.", lib)

    def test_no_lead_from_the_news_reaches_the_page(self):
        b = src("warehouse", "derived", "large_load_rules_page.py")
        self.assertIn('"words": "" if LEAD.search(words) else words', b)

    def test_a_chosen_state_links_its_utilities_rules_and_the_changes_follow_the_state(self):
        s = src("site", "app", "policy", "StateLaws.tsx")
        self.assertIn("<SiteLink href={rulesHref(s)} gate=\"plain\" data-laws-rules-state={s}>", s)
        t = src("site", "app", "cost-of-power", "LargeLoadRules.tsx")
        self.assertIn("filterChanges(FILE.changes, region ? [region] : [], st ? [st] : [])", t)

    def test_the_state_filter_says_what_a_record_is(self):
        m = src("site", "app", "policy", "MonitorView.tsx")
        self.assertIn("a state commission's own dockets are not records here", m)

    def test_a_repeated_topic_is_numbered(self):
        self.assertIn("same > 1 ? `${p.topic} (${nth} of ${same})` : p.topic", src("site", "app", "policy", "StateLaws.tsx"))

    def test_no_em_or_en_dash(self):
        for parts in (("docs", "reviews", "policy-read-2026-11-16.md"), ("tests", "test_session7204_policy_read.py"), ("site", "app", "policy", "StateLaws.tsx")):
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
            self.assertNotIn(EN_DASH, text, parts)


if __name__ == "__main__":
    unittest.main()
