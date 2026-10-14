"""Session 260: how it works, refreshed.

Energy Research Warehouse (ERW). docs/howitworks/ holds one note a tool (tests/test_session249.py holds their seven
parts and the order). Session 249 wrote the Grid tool's and Research's notes from branches, before either page had
landed. This session rewrote both from the pages as they stand on main and read the other three against today's pages.

What is held here: each of the five notes has the five parts the owner named (what it is for, how it computes, every
assumption with its source, the five-minute demo path, the ten hardest questions); the Grid tool's and Research's
questions are ten, numbered, each a question with an answer under it; those two notes say they were written from main
and name no branch; every address a demo path names is a route that exists under site/app; every file a note cites
exists; California is in the battery and generator notes as session 257 put it on the pages; no em dash. No number of
a note is held here: the notes' numbers are the methods' and the pages', which move.
Nothing here sets the environment, reads a table or makes a request.
"""

import glob
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "docs", "howitworks")
APP = os.path.join(ROOT, "site", "app")

ALL_NOTES = {
    "battery": "/cost-of-power/battery",
    "generator": "/cost-of-power/seller",
    "datacenter": "/cost-of-power",
    "grid": "/grid",
    "research": "/research",
}
# session 262: a tool whose review pack is written (docs/reviews/packs/<tool>.md, tests/test_session262.py) no longer
# has its note here; what is held below is held for the notes that remain, and for California in the packs
PACKS = os.path.join(ROOT, "docs", "reviews", "packs")
NOTES = {k: v for k, v in ALL_NOTES.items() if not os.path.exists(os.path.join(PACKS, k + ".md"))}
REWRITTEN = tuple(k for k in ("grid", "research") if k in NOTES)

# the owner's five parts, and the heading of the note that holds each
FIVE = {
    "what it is for": "## 1. What it is for, and for whom",
    "how it computes": "## 2. The model, in numbered steps",
    "every assumption with its source": "## 3. Every assumption, its default and its source",
    "the ten hardest questions": "## 6. The ten hardest questions",
    "the five-minute demo path": "## 7. A five-minute demo, click by click",
}

SITE = "https://erw-flame.vercel.app"
# a cited path begins with one of the repository's folders; warehouse/output is not in git (CLAUDE.md), nor is runs/
FOLDERS = ("docs/", "site/", "warehouse/", "tests/", "archive/", "package/", "scripts/", ".github/")
NOT_IN_GIT = ("warehouse/output/", "site/.next/", "site/node_modules/")


def note(name):
    with open(os.path.join(DIR, name + ".md"), encoding="utf-8") as f:
        return f.read()


def note_or_pack(name):
    """The tool's note, or its review pack once the pack has replaced it (session 262)."""
    pack = os.path.join(PACKS, name + ".md")
    if os.path.exists(pack):
        with open(pack, encoding="utf-8") as f:
            return f.read()
    return note(name)


def part(text, heading):
    """The lines under one heading, to the next heading of the same level."""
    lines = text.split("\n")
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1:end]


def ticked(text):
    """Every stretch of the text written as code."""
    return re.findall(r"`([^`\n]+)`", text)


def route_exists(path):
    """True when site/app holds a page or a route handler for the path (a folder in brackets stands for any word, a
    folder in parentheses is a group and names no part of the address)."""
    here = [APP]
    for seg in [s for s in path.split("/") if s]:
        nxt = []
        for d in here:
            for name in os.listdir(d):
                full = os.path.join(d, name)
                if not os.path.isdir(full):
                    continue
                if name == seg or (name.startswith("[") and name.endswith("]")):
                    nxt.append(full)
        here = nxt
        if not here:
            return False
    return any(os.path.exists(os.path.join(d, f)) for d in here for f in ("page.tsx", "page.ts", "route.ts", "route.tsx"))


def addresses(lines):
    """The addresses of the site a stretch of a note names: written as code, on production, on a local build or bare."""
    out = []
    for t in ticked("\n".join(lines)):
        if t.startswith(SITE):
            t = t[len(SITE):] or "/"
        elif re.match(r"^http://localhost:\d+", t):
            t = re.sub(r"^http://localhost:\d+", "", t) or "/"
        elif not t.startswith("/"):
            continue
        out.append(re.split(r"[?#]", t)[0] or "/")
    return out


def cited(text):
    """The repository paths a note cites, written as code."""
    out = []
    for t in ticked(text):
        t = t.strip().rstrip(".,;:")
        if " " in t or "<" in t or "..." in t or not t.startswith(FOLDERS) or t.startswith(NOT_IN_GIT):
            continue
        out.append(t)
    return out


class TheFiveParts(unittest.TestCase):
    def test_each_note_has_the_five_parts_and_none_is_thin(self):
        for name in NOTES:
            text = note(name)
            for what, heading in FIVE.items():
                self.assertIn("\n" + heading + "\n", text, f"{name}: {what}")
                body = [line for line in part(text, heading) if line.strip()]
                self.assertGreaterEqual(len(body), 5, f"{name}: {what}")

    def test_every_assumption_has_a_source(self):
        for name in NOTES:
            rows = [line for line in part(note(name), FIVE["every assumption with its source"]) if line.startswith("|")]
            heads = [r for r in rows if r.startswith("| Assumption")]
            self.assertGreaterEqual(len(heads), 1, name)
            for h in heads:
                self.assertTrue(h.rstrip().endswith("| Source |"), f"{name}: {h}")
            body = [r for r in rows if r not in heads and not set(r) <= set("|- ")]
            self.assertGreaterEqual(len(body), 20, name)
            for r in body:
                cells = [c.strip() for c in r.strip().strip("|").split(" | ")]
                self.assertGreaterEqual(len(cells), 4, f"{name}: {r[:60]}")
                self.assertTrue(cells[-1], f"{name}: no source: {r[:60]}")

    def test_the_demo_is_five_minutes_in_order(self):
        for name in NOTES:
            demo = "\n".join(part(note(name), FIVE["the five-minute demo path"]))
            starts = [int(m) for m in re.findall(r"Minute (\d) to \d", demo)]
            self.assertEqual(starts, sorted(starts), name)
            self.assertEqual(starts[0], 0, name)
            self.assertEqual(max(int(m) for m in re.findall(r"Minute \d to (\d)", demo)), 5, name)
            self.assertIn("Say this first", demo, name)


class TheTwoRewritten(unittest.TestCase):
    def test_ten_questions_numbered_each_with_an_answer(self):
        for name in REWRITTEN:
            lines = part(note(name), FIVE["the ten hardest questions"])
            asked = [(i, re.match(r"^### (\d+)\. (.+)$", line)) for i, line in enumerate(lines)]
            asked = [(i, int(m.group(1)), m.group(2)) for i, m in asked if m]
            self.assertEqual([n for _, n, _ in asked], list(range(1, 11)), name)
            for k, (i, n, words) in enumerate(asked):
                self.assertTrue(words.rstrip().endswith("?"), f"{name} question {n}")
                end = asked[k + 1][0] if k + 1 < len(asked) else len(lines)
                answer = " ".join(line for line in lines[i + 1:end] if line.strip())
                self.assertGreater(len(answer), 150, f"{name} question {n}: the answer")

    def test_they_are_written_from_main_and_name_no_branch(self):
        for name in REWRITTEN:
            text = note(name)
            opening = text[:text.index(FIVE["what it is for"])]
            self.assertIn("**Written from:** `main`", opening, name)
            self.assertIn("session 260", opening, name)
            self.assertNotIn("wip/", text, name)                      # no branch: the page is on main
            self.assertNotIn("Not from `main`", text, name)
            self.assertNotIn("(branch)", text, name)

    def test_the_index_says_all_five_are_on_main(self):
        index = note("README")
        self.assertIn("All five pages are on `main`", index)
        self.assertNotIn("not on `main`", index)
        self.assertIn("tests/test_session260.py", index)


class WhatTheNotesPointAt(unittest.TestCase):
    def test_the_resolver_knows_a_route_from_a_word(self):
        self.assertTrue(route_exists("/grid"))
        self.assertTrue(route_exists("/internal/open"))
        self.assertTrue(route_exists("/research/card/any_card"))       # a folder in brackets
        self.assertFalse(route_exists("/no-such-page-of-the-site"))
        self.assertFalse(route_exists("/grid/no/such/depth"))

    def test_every_address_of_a_demo_path_is_a_route_of_the_site(self):
        for name, own in NOTES.items():
            found = addresses(part(note(name), FIVE["the five-minute demo path"]))
            self.assertGreaterEqual(len(found), 3, name)
            self.assertIn(own, found, f"{name}: the demo never names the tool's own address")
            self.assertTrue(any(a.startswith("/internal/") for a in found), f"{name}: the internal view")
            for a in found:
                self.assertTrue(route_exists(a), f"{name}: {a} is no route under site/app")

    def test_every_file_a_note_cites_exists(self):
        for name in list(NOTES) + ["README"]:
            paths = cited(note(name))
            if name != "README":
                self.assertGreaterEqual(len(paths), 10, name)
                self.assertTrue(any(p.startswith("docs/methods/") for p in paths), f"{name}: no method note cited")
            for p in paths:
                full = os.path.join(ROOT, *p.split("/"))
                held = bool(glob.glob(full)) if "*" in p else os.path.exists(full.rstrip("/\\"))
                self.assertTrue(held, f"{name}: {p} is cited and is not in the repository")

    def test_a_computed_text_a_note_quotes_is_kept(self):
        for name in NOTES:
            for p in cited(note(name)):
                if p.startswith("docs/howitworks/computed/"):
                    self.assertTrue(os.path.exists(os.path.join(ROOT, *p.rstrip("/").split("/"))), p)

    def test_california_is_in_the_two_notes_as_the_pages_have_it(self):
        # session 257 (merged into this session's branch): the battery page's line for CAISO beside its market monitor,
        # its stress days by their days, and the generator page's count of published figures
        def src(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
                return f.read()
        lib, page = src("site", "lib", "batterystack.ts"), src("site", "app", "cost-of-power", "battery", "page.tsx")
        battery, generator = note_or_pack("battery"), note_or_pack("generator")
        self.assertIn("FLEET_BESIDE", lib)
        self.assertIn("for a {fleet.dur}-hour battery on the day-ahead schedule, this model takes USD", page)
        self.assertIn("for a 4-hour battery on the day-ahead schedule, this model takes USD", battery)
        self.assertNotIn("there is no awards line for CAISO", battery)
        self.assertNotIn("does not yet print that line for CAISO", battery)
        words = "the days of CAISO's system-wide notices"
        self.assertIn(words, lib)
        self.assertIn(words, battery)
        seller = src("site", "app", "cost-of-power", "seller", "page.tsx")
        count = re.search(r'data-checked-against="(\d+)"', seller).group(1)
        self.assertIn(f"Checked against: {count} published figures", generator)
        self.assertNotIn("not among the ten the page counts", generator)
        # what session 257 did not do is not claimed: the peaker's rule is as it was, and the note says a ruling is awaited
        self.assertIn("const c = g * hr + vom;", src("site", "lib", "merchant.ts"))
        self.assertIn("adding the allowance waits for a ruling", generator)

    def test_no_em_dash_in_what_the_session_wrote(self):
        files = sorted(glob.glob(os.path.join(DIR, "*.md")))
        files += [os.path.join(ROOT, "tests", "test_session260.py"), os.path.join(ROOT, "archive", "sessions", "SESSION_260_REPORT.md")]
        for f in files:
            if os.path.exists(f):
                with open(f, encoding="utf-8") as fh:
                    self.assertEqual(fh.read().count(chr(0x2014)), 0, f)


if __name__ == "__main__":
    unittest.main()
