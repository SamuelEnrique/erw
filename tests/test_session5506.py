"""Session 5506 (chain 269, portable laptop window P1): the close-out note, docs/state/note_2026-11-14_portable_p1.md.

The old laptop's chain 271 takes the five tools' build-free fault rows once this note is on main, so the note must name
every row still open in the five faults files of 13 November, by tool, with whose it is. The tests hold the note to
the files, to the chain's own rule (a close-out: no next file for window P1), and to the house rules.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = ("docs", "state", "note_2026-11-14_portable_p1.md")
TOOLS = {"battery": "battery", "generator": "generator", "datacenter-cost": "datacenter", "analysis": "Automated Analysis", "grid": "Grid"}


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def open_rows(tool):
    rows = []
    for line in read("docs", "reviews", f"{tool}-faults-2026-11-13.md").splitlines():
        m = re.match(r"^\| (\d+) \|", line)
        if m:
            state = line.rstrip(" |").rsplit("|", 1)[-1].strip()
            if not state.startswith("fixed") and state != "not a fault":
                rows.append((int(m.group(1)), state))
    return rows


class TheNote(unittest.TestCase):
    def test_every_open_row_is_named_with_whose_it_is(self):
        note = read(*NOTE)
        section = note.split("**The old laptop, chain 271**", 1)[1].split("\n- **", 1)[0]
        for tool, words in TOOLS.items():
            for n, state in open_rows(tool):
                if state == "data machine":
                    self.assertRegex(section, rf"window A's \([^)]*{re.escape(words)}[^)]*\b{n}\b", (tool, n))
                elif state == "ruling":
                    self.assertRegex(section, rf"rulings \({re.escape(words)}[^)]*\b{n}\b", (tool, n))
                else:
                    self.assertRegex(section, rf"{re.escape(words)} {n}\b", (tool, n))

    def test_the_rows_fixed_this_chain_are_fixed(self):
        fixed = {"battery": (12, 13), "generator": (4,), "datacenter-cost": (5,), "analysis": (7,), "grid": (6, 7)}
        for tool, ns in fixed.items():
            states = {n: s for n, s in ((int(m.group(1)), line.rstrip(" |").rsplit("|", 1)[-1].strip())
                                        for line in read("docs", "reviews", f"{tool}-faults-2026-11-13.md").splitlines()
                                        for m in [re.match(r"^\| (\d+) \|", line)] if m)}
            for n in ns:
                self.assertRegex(states[n], r"^fixed \(session 550[15]\)$", (tool, n))

    def test_a_close_out_with_no_next_file(self):
        note = read(*NOTE)
        self.assertIn("**No next file.**", note)
        self.assertIn("**Row 31** (`wip/5500-closeout`", note)
        chain = read("queue", "done", "269-night-14-november-portable-p1-closeout.md")
        self.assertIn("**No next file.**", chain)
        nxt = os.path.join(ROOT, "queue", "next")
        for name in os.listdir(nxt):
            if name.endswith(".md"):
                self.assertNotIn("machine: portable-laptop-window1", read("queue", "next", name), name)

    def test_the_rulings_and_the_requests(self):
        note = read(*NOTE)
        for n in range(1, 10):
            self.assertRegex(note, rf"\n{n}\. ", n)
        self.assertIn("G1, new", note)
        self.assertIn("docs/reviews/five-tools-signature-pack-2026-11-14.md", note)
        self.assertIn("(4) and (5) `price_years_by_window`", note)

    def test_no_dash(self):
        for rel in (NOTE, ("tests", "test_session5506.py"), ("archive", "sessions", "SESSION_5506_REPORT.md")):
            text = read(*rel)
            self.assertNotIn(chr(0x2014), text, rel)
            self.assertNotIn(chr(0x2013), text, rel)


if __name__ == "__main__":
    unittest.main()
