"""Sessions 3707 to 3709 (chain 208): roadmap item 2's cross-check tables, one file a tool under docs/methods/crosschecks/.
Each sets the tool's headline figures (its replication package's page_figures.json) against figures named publishers
state: every headline figure is named, with a published figure and a gap, or said to have none. No network, no model.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CC = os.path.join(ROOT, "docs", "methods", "crosschecks")
TOOLS = {"battery": "battery", "generator": "generator", "datacenter": "datacenter", "automated_analysis": "analysis", "grid": "grid"}


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def rows(text):
    """The table rows of a file, as lists of cells (a header and its rule left out)."""
    out = []
    for line in text.splitlines():
        if not line.startswith("| ") or set(line.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if cells[0] in ("Headline figure", "Headline figure (`page_figures.json` field)", "Card and figure", "Card"):
            continue
        out.append(cells)
    return out


class TheFiles(unittest.TestCase):
    def test_one_file_a_tool(self):
        for name in TOOLS:
            self.assertTrue(os.path.exists(os.path.join(CC, name + ".md")), name)

    def test_every_row_is_whole(self):
        for name in TOOLS:
            for r in rows(read("docs", "methods", "crosschecks", name + ".md")):
                if len(r) == 3:   # the analysis file's list of figures with none: card, figures, why
                    self.assertTrue(all(r), (name, r))
                    continue
                self.assertEqual(len(r), 6, (name, r[0][:60]))
                self.assertTrue(r[0] and r[2] and r[5], (name, r[0][:60]))
                if not r[2].lower().startswith("no "):
                    # a published figure names where it was read, and a gap or why there is none
                    self.assertTrue(r[3], (name, r[0][:60]))
                    self.assertTrue(r[4], (name, r[0][:60]))

    def test_every_headline_figure_of_the_three_decision_tools_is_named(self):
        for name in ("battery", "generator", "datacenter"):
            text = read("docs", "methods", "crosschecks", name + ".md")
            page = json.loads(read("replication", name, "page_figures.json"))
            for f in page["figures"]:
                self.assertIn(f"`{f['field']}`", text, (name, f["field"]))

    def test_every_card_of_research_is_named(self):
        text = read("docs", "methods", "crosschecks", "automated_analysis.md")
        page = json.loads(read("replication", "analysis", "page_figures.json"))
        for card in {f["card"] for f in page["figures"] if f["card"] != "chart_of_the_week"}:
            self.assertIn(f"`{card}`", text, card)
        self.assertIn("This week's chart", text)

    def test_the_grid_file_covers_each_tab(self):
        text = read("docs", "methods", "crosschecks", "grid.md")
        for title in ("## The network", "## The gravity shape", "## Carbon intensity", "## The Mix tab", "## The Ask panel"):
            self.assertIn(title, text)

    def test_the_quoted_conversions(self):
        # eGRID's lb/MWh in kg: 1 lb = 0.45359237 kg
        text = read("docs", "methods", "crosschecks", "grid.md")
        for lb, kg in (("733.862", "332.87"), ("539.275", "244.61"), ("428.464", "194.35"), ("767.209", "348.00")):
            self.assertIn(lb, text)
            self.assertIn(kg, text)
            self.assertAlmostEqual(float(lb) * 0.45359237, float(kg), delta=0.005)

    def test_no_em_or_en_dash(self):
        for name in TOOLS:
            text = read("docs", "methods", "crosschecks", name + ".md")
            self.assertNotIn(chr(0x2014), text, name)
            self.assertNotIn(chr(0x2013), text, name)


if __name__ == "__main__":
    unittest.main()
