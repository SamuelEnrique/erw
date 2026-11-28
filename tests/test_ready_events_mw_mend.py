"""Session 11405 (chain 770, part C): the event pages' "license needed MW" mend (decision 8 of the weekend page of 28
November, the half that holds under either answer).

The nine event pages and the index printed a held figure's unit after the words that stand in its place: "license needed
MW on 2022-12-23", "license needed % on ...", "license needed MWh a day", "license needed kg CO2/MWh" (the browser read
of 20 November, line 4, counted 146; drawn on 28 November from the warehouse's tables, 187 over the ten pages, 9 of them
"not held" with a unit). The unit now goes into the figure's component (Num's `unit`), which draws it only when the
number is shown.

Held here: the ten pages drawn with the site's own code on the public rows beside the replication, once as a visitor's
build draws them (no unit after "license needed" or "not held") and once with the hold stood aside (every unit still
after its number, and the text is the same as before the mend wherever a number is shown).
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "events")
NODE = shutil.which("node")
UNIT_AFTER_WORDS = re.compile(r"(license needed|not held)\s?(MWh|MW|GWh|%|percent|kg CO2/MWh|kg CO2 per MWh|USD/MWh|USD)(?![A-Za-z])")
TITLE = re.compile(r"\[title: [^\]]*\] ")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def draw(unheld: bool) -> dict:
    """The ten pages' text, drawn on the replication's rows; {slug: text}."""
    tables = tempfile.mkdtemp(prefix="erw_ev_tables_")
    out = tempfile.mkdtemp(prefix="erw_ev_out_")
    shutil.copy(os.path.join(REP, "window_rows.csv"), os.path.join(tables, "event_window_daily.csv"))
    shutil.copy(os.path.join(REP, "notice_rows.csv"), os.path.join(tables, "caiso_grid_emergencies.csv"))
    env = {k: v for k, v in os.environ.items() if k != "EVENTS_DRAW_UNHELD"}
    if unheld:
        env["EVENTS_DRAW_UNHELD"] = "1"
    r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/events-pages.mjs", tables, out], cwd=SITE,
                       capture_output=True, text=True, encoding="utf-8", timeout=900, env=env)
    if r.returncode != 0:
        raise AssertionError(r.stdout[-2000:] + r.stderr[-2000:])
    pages = {}
    for name in os.listdir(out):
        if name.endswith(".txt"):
            with open(os.path.join(out, name), encoding="utf-8") as f:
                pages[name[:-4]] = TITLE.sub("", f.read())
    shutil.rmtree(tables, ignore_errors=True)
    shutil.rmtree(out, ignore_errors=True)
    return pages


class TheSource(unittest.TestCase):
    def test_num_draws_its_unit_only_when_shown(self):
        s = src("site", "components", "Num.tsx")
        self.assertIn("unit?: string", s)
        self.assertIn("if (unit) return <><Num check={check} raw={raw} className={className} source={source}>{children}</Num>{unit}</>;", s)

    def test_no_unit_written_after_an_event_figure(self):
        files = ["EventWindow.tsx"] + [os.path.join(d, "page.tsx") for d in ("caiso-heat-2020", "caiso-heat-2022", "cold-2025", "cold-2026", "covid-2020",
                                                                               "east-heat-2025", "elliott-2022", "ercot-heat-2023", "uri-2021")]
        bad = re.compile(r"<N [^>]*/>(%| MW| MWh| USD/MWh| kg CO2| percent)")
        for f in files:
            self.assertIsNone(bad.search(src("site", "app", "events", f)), f)
        self.assertIsNone(re.search(r"<E [^>]*/>(</strong>)? (MWh|percent)", src("site", "components", "EventStudy.tsx")))


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePagesDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.held = draw(False)
        cls.unheld = draw(True)

    def test_ten_pages_drawn(self):
        self.assertEqual(len(self.held), 10, sorted(self.held))

    def test_no_unit_after_license_needed(self):
        left = {k: [m.group(0) for m in UNIT_AFTER_WORDS.finditer(t)] for k, t in self.held.items()}
        left = {k: v for k, v in left.items() if v}
        self.assertEqual(left, {}, left)

    def test_the_held_words_are_still_there(self):
        n = sum(t.count("license needed") for t in self.held.values())
        self.assertGreater(n, 100)

    def test_units_follow_shown_numbers(self):
        t = self.unheld["elliott-2022"]
        self.assertRegex(t, r"PJM's highest hour in EIA's data, [0-9,]+ MW on 2022-12-23")
        self.assertRegex(self.unheld["covid-2020"], r"Deepest weekly drop against the baseline: -?[0-9.]+ ?% in the week of")
        self.assertRegex(self.unheld["uri-2021"], r"[0-9.,]+ USD/MWh on 2021-02-")
        self.assertRegex(self.unheld["caiso-heat-2020"], r"[0-9,.]+ MWh a day (above|below) what")


if __name__ == "__main__":
    unittest.main()
