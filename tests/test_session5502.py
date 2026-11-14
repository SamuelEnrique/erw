"""Session 5502 (chain 269, portable laptop window P1): the signature pack of the five tools,
docs/reviews/five-tools-signature-pack-2026-11-14.md.

The pack tells Samuel what each do-file should print. These tests hold it to the files the do-files compare against
(replication/<tool>/page_figures.json), so a later rebuild of a page's figures that moves a number shows here first; to
each note's sign-off block, which is what he signs and which no session fills; and to the commands that run each
do-file from its own folder.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "docs", "reviews", "five-tools-signature-pack-2026-11-14.md")
NOTES = {"battery": "battery_earns_algorithm", "generator": "generator_earns_algorithm", "datacenter": "datacenter_pays_algorithm",
         "analysis": "automated_analysis", "grid": "grid_network"}


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def shown(v):
    """A figure as the pack writes it: whole numbers with commas, the rest as the page shows them."""
    if float(v).is_integer():
        return f"{int(v):,}"
    return f"{v:,.2f}" if abs(v) >= 1 else f"{v:.4f}"


class TheExpectedValues(unittest.TestCase):
    # the page_figures.json fields the pack quotes under each economics tool's "Expected"
    QUOTED = {
        "battery": ["bs|l12_kw:total", "scenario A's debt payment", "bs|cover", "scenario A's NPV", "scenario A's breakeven toll", "bs|p10_36",
                    "bs|year:2024:energy", "bs|year:2024:ancillary", "bs|year:2025:energy", "bs|year:2025:ancillary"],
        "generator": ["ms|G|twelve|revenue", "ms|G|three|revenue", "ms|G|every|revenue", "mr|G|ds", "mr|G|ttm_last", "ms|G|twelve|energy",
                      "scenario A's contract price", "scenario A's NPV", "scenario A's breakeven PPA price", "scenario A's worst month"],
        "datacenter": ["a|price, l12_per", "a|bill", "a|gpu", "l12_per on ?buy=da", "a|bad", "dc|...|scarce:hours", "dc|...|scarce:flat_usd",
                       "dc|...|co2:l12:kg:flat", "dc|...|co2:l12:tonnes:flat", "dc|...|co2:window:hours", "dc|...|co2:window:flat"],
    }

    def section(self, n):
        pack = read("docs", "reviews", "five-tools-signature-pack-2026-11-14.md")
        parts = re.split(r"\n## (\d)\. ", pack)
        return dict(zip(parts[1::2], parts[2::2]))[str(n)]

    def test_each_quoted_figure_is_the_page_s(self):
        for n, tool in ((1, "battery"), (2, "generator"), (3, "datacenter")):
            text = self.section(n).split("**Expected", 1)[1]
            figs = {f["key"]: f for f in json.loads(read("replication", tool, "page_figures.json"))["figures"]}
            for key in self.QUOTED[tool]:
                page = figs[key]["page"]
                forms = {shown(page), f"{page:,.2f}", f"{page}"}
                if key == "scenario A's NPV" and tool == "battery":
                    forms.add(f"{page:,.2f}")
                self.assertTrue(any(f in text for f in forms), (tool, key, page, forms))

    def test_the_mirror_counts(self):
        pack = read("docs", "reviews", "five-tools-signature-pack-2026-11-14.md")
        for words in ("**22 of 22 inside the tolerance.**", "**13 of 13 inside the tolerance.**", "**14 of 14 inside the tolerance.**",
                      '"inside the tolerance: 62"', '"met: 85"', "**85 of 85 computed figures met**"):
            self.assertIn(words, pack)
        for tool, n in (("battery", 22), ("generator", 13), ("datacenter", 14)):
            self.assertEqual(len(json.loads(read("replication", tool, "page_figures.json"))["figures"]), n, tool)


class TheCommands(unittest.TestCase):
    def test_each_do_file_is_run_from_its_folder_with_a_log(self):
        pack = read("docs", "reviews", "five-tools-signature-pack-2026-11-14.md")
        for tool in ("battery", "generator", "datacenter", "analysis", "grid"):
            self.assertIn(f'cd "C:\\path\\to\\erw\\replication\\{tool}"\nlog using "{tool}_stata_2026-11-14.log", text replace\ndo replicate.do\nlog close', pack, tool)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "replication", tool, "replicate.do")), tool)
        self.assertIn("do replicate_ask.do", read("replication", "grid", "replicate.do"))


class TheSignatures(unittest.TestCase):
    def test_every_block_is_named_and_none_is_filled(self):
        pack = read("docs", "reviews", "five-tools-signature-pack-2026-11-14.md")
        for tool, note in NOTES.items():
            self.assertIn(f"`docs/methods/{note}.md`, section \"Sign-off\"", pack, tool)
            text = read("docs", "methods", f"{note}.md")
            block = text.split("## Sign-off", 1)[1].split("\n## ", 1)[0]
            self.assertRegex(block, r"\n- Signed off by:\s*\n- Date:\s*\n", note)

    def test_the_rulings_and_no_dash(self):
        pack = read("docs", "reviews", "five-tools-signature-pack-2026-11-14.md")
        for n in range(1, 9):
            self.assertRegex(pack, rf"\n{n}\. \*\*", n)
        self.assertIn("**G1. The Grid page's \"Checked against\" line.**", pack)
        self.assertNotIn(chr(0x2014), pack)
        self.assertNotIn(chr(0x2013), pack)


if __name__ == "__main__":
    unittest.main()
