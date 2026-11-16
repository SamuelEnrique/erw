"""Session 7515 (chain 304, part B): the forecast tool, Local impact (/impact), read as the reader it is for.

Energy Research Warehouse (ERW). What is held to:

  the one figure the read corrected (docs/reviews/impact-read-2026-11-16.md, row 1): Nevada's abatement (NRS 701A.370)
    takes 55 percent off the tax, not off the value, so the replication's taxable value of an abated year is the whole
    value while its tax stays the 45 percent; a statute that exempts value (Florida) keeps the taxed share as the value;
  the rule file marks Nevada's rule, and only it, as an abatement of the tax, and the page's trim of the rule file
    keeps the mark (the browser reads the trimmed rules);
  where the table nlr_jedi_multipliers is on the machine and node is there: the page's own view is drawn to HTML and
    the table by year's cells are read (site/scripts/test-impact-read.mjs). Skipped on a machine without them;
  the read's file names its reader, its five cases and its rows, counts its rows by kind as its table holds them, and
    carries no dash the repository forbids.

No request, no model call, no site build. The environment is read, never set."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLES = os.environ.get("ERW_TABLES_DIR") or os.environ.get("ERW_TABLES") or os.path.join(ROOT, "warehouse", "output")
JEDI = os.path.join(TABLES, "nlr_jedi_multipliers.csv")
EM, EN = chr(0x2014), chr(0x2013)
NEVADA = {"tech": "geothermal", "state": "nv", "mw": "36", "cost": "4956.83", "start": "2026", "own": "1.0917", "ownyears": "60"}


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def replicate_module():
    spec = importlib.util.spec_from_file_location("erw_impact_replicate_7515", os.path.join(ROOT, "replication", "impact", "replicate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheTaxableValue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = replicate_module()
        cls.P = cls.m.Params()

    def scenario(self, query):
        tech, state, given = self.m.scenario_values(query, "a")
        return self.m.inputs(self.P, tech, state, given)

    def test_nevada_abates_the_tax_and_not_the_value(self):
        on = self.scenario({**NEVADA, "iaval": "1"})
        off = self.scenario(NEVADA)
        cost = 4956.83 * 36 * 1000
        for i in (0, 10, 17):
            tax_on, value_on, _ = self.m.property_tax(self.P, on, i)
            tax_off, value_off, _ = self.m.property_tax(self.P, off, i)
            share = 1 - i / 60
            self.assertAlmostEqual(value_on, cost * share, delta=1e-3)
            self.assertAlmostEqual(value_on, value_off, delta=1e-6)
            self.assertAlmostEqual(tax_on, 0.45 * tax_off, delta=1e-6)
        # the nineteenth and later operating years are past the 20 years counted from the first construction year
        tax_on, value_on, _ = self.m.property_tax(self.P, on, 18)
        tax_off, value_off, _ = self.m.property_tax(self.P, off, 18)
        self.assertAlmostEqual(tax_on, tax_off, delta=1e-6)
        self.assertAlmostEqual(value_on, value_off, delta=1e-6)

    def test_an_exemption_of_value_keeps_the_taxed_share(self):
        fl = self.scenario({"tech": "utility_pv", "state": "fl", "mw": "100", "cost": "1500", "start": "2027", "own": "1", "ownyears": "30"})
        tax, value, _ = self.m.property_tax(self.P, fl, 0)
        self.assertAlmostEqual(value, 150e6 * 0.2, delta=1e-3)
        self.assertAlmostEqual(tax, 150e6 * 0.2 * 0.01, delta=1e-3)

    def test_the_rule_file_marks_nevada_alone_and_the_trim_keeps_the_mark(self):
        rules = json.loads(read("site", "data", "forecast", "property_rules.json"))
        marked = [(s, r["id"]) for s, v in rules["states"].items() for r in v["rules"] if r.get("abates") == "tax"]
        self.assertEqual(marked, [("nv", "nv_renewable_abatement")])
        self.assertIn("NRS 701A.370", rules["states"]["nv"]["rules"][0]["quote"])
        self.assertIn("55 percent of the taxes", rules["states"]["nv"]["rules"][0]["quote"])
        self.assertIn("abates: r.abates", read("site", "lib", "forecastdata.ts"))
        self.assertIn('ex?.abates === "tax"', read("site", "lib", "forecast.ts"))


class ThePageDrawn(unittest.TestCase):
    def test_the_table_by_year_shows_the_whole_value(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(ROOT, "site", "node_modules")) or not os.path.exists(JEDI):
            raise unittest.SkipTest("node, the site's modules or the table are not here")
        r = subprocess.run([node, "--import", "./scripts/tsx-register.mjs", "scripts/test-impact-read.mjs", JEDI],
                           cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("10 of 10 passed", r.stdout)


class TheRead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("docs", "reviews", "impact-read-2026-11-16.md")
        cls.rows = re.findall(r"^\| (\d+) \| .* \| (site|ruling|data machine|browser|license|key) \| [^|]+ \|$", cls.text, flags=re.M)

    def test_the_reader_the_cases_and_the_rows(self):
        for words in ("**The reader.**", "**The five cases.**", "**How it was read.**", "Lone Mountain Geothermal", "Grant Solar", "Silver Queen Wind Farm",
                      "CPV Basin Ranch Energy Center", "Cape Generating Station", "## What this reader still cannot get from the tool, and why"):
            self.assertIn(words, self.text)
        self.assertEqual([int(n) for n, _ in self.rows], list(range(1, len(self.rows) + 1)))
        self.assertGreaterEqual(len(self.rows), 10)

    def test_the_counts_by_kind_are_the_tables(self):
        counts = {}
        for _, kind in self.rows:
            counts[kind] = counts.get(kind, 0) + 1
        for kind, n in counts.items():
            self.assertRegex(self.text, rf"(?m)^- `{kind}`: {n}\b", kind)
        self.assertEqual(counts.get("site"), 1)

    def test_no_forbidden_dash(self):
        for parts in (("docs", "reviews", "impact-read-2026-11-16.md"), ("site", "scripts", "impact-read.mjs"), ("site", "scripts", "test-impact-read.mjs")):
            t = read(*parts)
            self.assertNotIn(EM, t, parts[-1])
            self.assertNotIn(EN, t, parts[-1])


if __name__ == "__main__":
    unittest.main()
