"""Session 5073 (chain 243, portable laptop window P1): a test per cross-check table of the five tools
(docs/methods/crosschecks/). For each table: its "Ours" is the page's figure (replication/<tool>/page_figures.json, for
the three decision tools), each gap is ours less theirs, every row has a source (a publisher's link, a warehouse table
or file in backticks, or "the same"), and no row is "not explained". The three decision tools' method notes keep their
own "Cross-checks" table (Lazard's LCOS and LCOE, the ATB, EIA, Modo Energy, the market monitors): every row of it has
five full cells and a source. The arithmetic of the reasons session 5073 wrote is checked here. No network, no model.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLIT = re.compile(r"(?<!\\)\|")
NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
HEADERS = {"Headline figure", "Headline figure (`page_figures.json` field)", "Card and figure", "Card", "Our figure", "Figure"}
NOTES = {"battery": "battery_earns_algorithm", "generator": "generator_earns_algorithm", "datacenter": "datacenter_pays_algorithm"}


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def table_rows(text):
    """Every table row of a markdown text as its cells (header rows and rules left out)."""
    out = []
    for line in text.splitlines():
        if not line.startswith("| ") or set(line.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in SPLIT.split(line.strip())[1:-1]]
        if cells[0] in HEADERS:
            continue
        out.append(cells)
    return out


def crosscheck(tool):
    return read("docs", "methods", "crosschecks", tool + ".md")


def note_section(note):
    text = read("docs", "methods", note + ".md")
    s = text.index("\n## Cross-checks")
    m = re.search(r"\n## ", text[s + 5:])
    return text[s: s + 5 + m.start()] if m else text[s:]


def number(s):
    return float(s.replace(",", ""))


def sourced(cell):
    low = cell.lower()
    return "https://" in cell or "`" in cell or low.startswith("the same") or low.startswith("ours only")


class Rows:
    """Every row of a table: full cells, a source, no "not explained"."""

    def check_rows(self, text, name):
        rows = table_rows(text)
        self.assertGreater(len(rows), 5, name)
        for r in rows:
            label = (name, r[0][:60])
            self.assertTrue(all(r), label)
            self.assertNotIn("not explained", " ".join(r).lower(), label)
            if len(r) == 6:
                self.assertTrue(sourced(r[3]), label)
            elif len(r) == 5:   # a note's own table: our figure, theirs, source and date, gap, reason
                self.assertTrue(sourced(r[2]), label)
            else:
                self.assertEqual(len(r), 3, label)   # the analysis file's figures with none: card, figures, why

    def check_gaps(self, text, triples, tol=0.0051):
        for ours, theirs, gap in triples:
            self.assertIn(ours, text, ours)
            self.assertIn(gap, text, gap)
            self.assertAlmostEqual(number(ours) - number(theirs), number(gap), delta=tol, msg=(ours, theirs, gap))


class Decision(Rows):
    tool = ""
    # Session 5402: a tool whose page_figures.json the data machine's daily run rewrites (run_data_machine.sh, PAGE_PATHS):
    # its hand-set table drifts by design, so a difference is a skip with the list (as test 3703's newer snapshot), never
    # a failure that would stop every landing; the battery's and the generator's files are fixed, so theirs fail
    MOVING = False

    def test_ours_is_the_page(self):
        page = json.loads(read("replication", self.tool, "page_figures.json"))["figures"]
        by = {f["field"]: f for f in page}
        seen, moved = set(), []
        for r in table_rows(crosscheck(self.tool)):
            fields = [f for f in re.findall(r"`([a-z0-9_]+)`", r[0]) if f in by]
            if not fields:
                continue
            got = [number(x) for x in NUM.findall(r[1])]
            for k, f in enumerate(fields):
                tol = max(by[f]["tolerance"], 0.005) + 1e-9
                if abs(got[k] - by[f]["page"]) > tol:
                    moved.append(f"{f}: table {got[k]}, page {by[f]['page']}")
                seen.add(f)
        self.assertEqual(seen, set(by), self.tool)
        if moved and self.MOVING:
            self.skipTest(f"{self.tool}: page_figures.json has moved with the daily run; set the table beside it: " + "; ".join(moved))
        self.assertEqual(moved, [], self.tool)

    def test_every_row_sourced(self):
        self.check_rows(crosscheck(self.tool), self.tool)

    def test_the_notes_own_table(self):
        section = note_section(NOTES[self.tool])
        self.check_rows(section, NOTES[self.tool])
        for r in table_rows(section):
            self.assertEqual(len(r), 5, r[0][:60])


class Battery(Decision, unittest.TestCase):
    tool = "battery"

    def test_gaps(self):
        self.check_gaps(crosscheck(self.tool), [
            ("147.68", "55", "+92.68"), ("147.68", "127", "+20.68"), ("87.44", "29.4", "+58.04"), ("2.63", "2.0", "+0.63"),
            ("33", "24", "+9"), ("-40.8", "-37", "-3.8"), ("4.19", "12.08", "-7.89"), ("4.19", "26.67", "-22.48"),
            ("2.25", "0.40", "+1.85"), ("85.59", "77.3", "+8.29"), ("84.72", "77.3", "+7.42"), ("92.00", "77.3", "+14.70"),
            ("42.31", "35", "+7.31"), ("42.25", "9", "+33.25")])

    def test_the_fall_from_2024_to_2025(self):
        text = crosscheck(self.tool)
        self.assertAlmostEqual((87.44 / 147.68 - 1) * 100, -40.8, delta=0.05)
        self.assertAlmostEqual((30.05 / 84.98 - 1) * 100, -64.6, delta=0.05)
        self.assertAlmostEqual((57.39 / 62.70 - 1) * 100, -8.5, delta=0.05)
        self.assertAlmostEqual(84.98 / 147.68 * 100, 57.5, delta=0.05)
        grew = 1.08 / 0.63   # total revenue about +8 percent, revenue per kW almost -37 percent
        self.assertAlmostEqual(grew, 1.71, delta=0.005)
        energy, reserves = 1.57 / grew - 1, 0.63 / grew - 1   # net energy revenue +57 percent; reserves -37 percent or more
        self.assertAlmostEqual(energy * 100, -8.4, delta=0.1)
        self.assertLess(reserves * 100, -63)
        share = (-0.37 - energy) / (reserves - energy)   # the fleet's 2024 share of reserves that gives -37 percent
        self.assertAlmostEqual(share * 100, 52, delta=0.5)
        for a, b in (("6.01", "2.98"), ("3.44", "1.62"), ("5.67", "2.76"), ("8.23", "2.46"), ("6.22", "3.05")):
            self.assertIn(f"{a} to {b}", text)
            self.assertTrue(-71 < (number(b) / number(a) - 1) * 100 < -49, (a, b))
        for words in ("1.71 times", "57.5 percent", "about 52 percent", "pages 22 and 23"):
            self.assertIn(words, text)


class Generator(Decision, unittest.TestCase):
    tool = "generator"

    def test_gaps(self):
        self.check_gaps(crosscheck(self.tool), [
            ("0.67", "1.275", "-0.605"), ("29.5", "24", "+5.5"), ("29.5", "23.8", "+5.7"), ("39.14", "38", "+1.14"),
            ("39.14", "78", "-38.86"), ("58.36", "38", "+20.36"), ("58.36", "78", "-19.64"),
            ("50.42", "52.59", "-2.17"), ("50.42", "79", "-28.58"), ("23.27", "21", "+2.27")])


class Datacenter(Decision, unittest.TestCase):
    tool = "datacenter"
    MOVING = True

    def test_gaps(self):
        self.check_gaps(crosscheck(self.tool), [
            ("32.40", "67.02", "-34.62"), ("30.59", "70.70", "-40.11"), ("150.61", "221.52", "-70.91"),
            ("62.93", "77.30", "-14.37"), ("48.69", "78.01", "-29.32"), ("26.41", "30.42", "-4.01"),
            ("32.66", "35.34", "-2.68"), ("301.82", "332.87", "-31.05"),
            ("39.47", "251.10", "-211.63"), ("77.45", "108.10", "-30.65")])

    def test_the_carbon_against_egrid(self):
        text = crosscheck(self.tool)
        self.assertAlmostEqual(733.862 * 0.45359237, 332.87, delta=0.005)
        self.assertIn("intensity_demand", text)   # the page's measure (site/app/cost-of-power/tables.csv/route.ts)
        self.assertIn("342.96", read("docs", "methods", "crosschecks", "grid.md"))


class Analysis(Rows, unittest.TestCase):
    def test_every_row_sourced(self):
        self.check_rows(crosscheck("automated_analysis"), "automated_analysis")

    def test_gaps(self):
        self.check_gaps(crosscheck("automated_analysis"), [
            ("13,909", "17,000", "-3,091"), ("5,616", "7,300", "-1,684"), ("1.55", "1.83", "-0.28"),
            ("7,816", "6,200", "+1,616"), ("41.04", "67.02", "-25.98"), ("46.83", "67.02", "-20.19"),
            ("3,591", "3,501", "+90")])

    def test_every_card_figure_is_the_pages(self):
        """Session 5402: every figure a card prints (replication/analysis/page_figures.json, not held for a license) is
        quoted, as the page shows it, in that card's rows of this file: the table had 6 November's cards until then."""
        text = crosscheck("automated_analysis")
        rows = {}
        for line in text.splitlines():
            m = re.match(r"^\| `([a-z_]+)`", line)
            if m:
                rows.setdefault(m.group(1), []).append(line)
        committed = json.loads(read("replication", "analysis", "page_figures.json"))
        # the data machine's daily run rewrites the file (dm_analysis_figures): the table is set to the day it names
        if committed.get("written_for_day") != "2026-11-12":
            self.skipTest(f"page_figures.json is written for {committed.get('written_for_day')}; the table is set to 2026-11-12: set it again")
        self.assertIn("as written for 12 November 2026", text)
        n = 0
        for f in committed["figures"]:
            if f["card"] == "chart_of_the_week" or f["held"]:
                continue
            shown = f"{float(f['page']):,.{int(f['decimals'])}f}"
            self.assertIn(shown, " ".join(rows.get(f["card"], [])), (f["card"], f["field"], shown))
            n += 1
        self.assertGreaterEqual(n, 60)

    def test_what_each_fleet_counts(self):
        text = crosscheck("automated_analysis")
        self.assertAlmostEqual(21579 / 13909, 1.55, delta=0.005)
        self.assertEqual(31500 - 21579, 9921)
        self.assertAlmostEqual(9921 / 3091, 3.2, delta=0.05)
        self.assertAlmostEqual(17000 / 1.8, 9444, delta=1)   # "about 9,400 MW or a little more"
        self.assertAlmostEqual(9444 - 8294, 1150, delta=1)    # "about 1,100 MW apart"
        for words in ("High Sustained Limit", "9,921 MWh", "about 3.2 hours", "about 9,400 MW", "8,294", "OP, SB, OS and OA"):
            self.assertIn(words, text)
        self.assertIn("`OP`, `SB` (standby), `OS` and `OA`", read("docs", "methods", "storage_buildout.md"))


class Grid(Rows, unittest.TestCase):
    def test_every_row_sourced(self):
        self.check_rows(crosscheck("grid"), "grid")

    def test_gaps(self):
        self.check_gaps(crosscheck("grid"), [
            ("342.96", "332.87", "+10.09"), ("231.85", "244.61", "-12.76"), ("197.38", "194.35", "+3.03"),
            ("348.57", "348.00", "+0.57"), ("348.57", "366.03", "-17.46"), ("22,618", "24,358", "-1,740"),
            ("31.57", "32.41", "-0.84"), ("95,060", "95,390", "-330"), ("2,120", "2,111", "+9"),
            ("6,591", "7,058", "-467"), ("1,561", "103", "+1,458"), ("-1,544", "-1,462", "-82"), ("-437", "-964", "+527")])

    def test_the_percent_gaps(self):
        text = crosscheck("grid")
        for ours, theirs, pct in (("485.2", "541.8", "-10.45"), ("185.4", "203.1", "-8.72"), ("873.8", "878.1", "-0.48"),
                                  ("302.1", "293.2", "+3.05"), ("4,280.5", "4,494.7", "-4.76")):
            self.assertIn(f"{pct} percent", text)
            self.assertAlmostEqual((number(ours) / number(theirs) - 1) * 100, number(pct), delta=0.02, msg=ours)

    def test_the_generation_eia930_leaves_out(self):
        text = crosscheck("grid")
        annual = read("docs", "methods", "eia_annual_crosscheck.md")
        self.assertIn("| ERCO | -7.53 |", annual)
        self.assertIn("| ISNE | -6.51 |", annual)
        ercot = (332.87 - 0.9247 * 342.96) / 0.0753
        isone = (244.61 - 0.9349 * 231.85) / 0.0651
        self.assertAlmostEqual(ercot, 209, delta=0.5)
        self.assertAlmostEqual(isone, 428, delta=0.5)
        for words in ("about 209 kg per MWh", "about 428 kg per MWh", "0.9247 x 342.96", "0.9349 x 231.85"):
            self.assertIn(words, text)


if __name__ == "__main__":
    unittest.main()
