"""Session 2240 (chain 156): the AI-power view of the deals (site/lib/dealsai.ts, site/app/deals/ai/view.tsx).

Node runs the pure functions on rows shaped as the live set serves them: only AI-tagged deals count; a sum is of the
stated figures with the count that state each; the kind of supply is read from the kind and the technology; the ten
largest by MW and by US dollars; the keys check-values recomputes.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def row(i, date, ai, mw=None, usd=None, **x):
    extra = {"ai_power": "true" if ai else "false", "story_urls": f"https://example.org/{i}", **x}
    if usd is not None:
        extra["dollars"] = str(usd)
    return {"event_id": f"deal:{i}", "event_date": f"{date}T00:00:00Z", "status": "signed", "mw": "" if mw is None else str(mw),
            "price": "", "currency": "", "parties": "", "source": "x", "source_url": f"https://example.org/{i}", "extra": extra}


ROWS = [
    row(1, "2026-10-19", True, 960, None, deal_type="ppa", buyer="Amazon", seller="AEP", seller_name="American Electric Power",
        state="IN", kind="smr"),
    row(2, "2026-09-30", True, 190, None, deal_type="ppa", buyer="Amazon", seller="Constellation", state="MD", technology="nuclear"),
    row(3, "2026-07-02", True, 1200, 800000000, deal_type="other", seller="BKV", state="TX", kind="gas_buildout"),
    row(4, "2026-05-06", True, None, 38000000000, deal_type="offtake", buyer="OpenAI", seller="Amazon", kind="compute_capacity"),
    row(5, "2026-08-01", True, None, None, deal_type="ppa", buyer="Google", seller="NextEra", technology="solar", state="TX"),
    row(6, "2026-08-02", False, 5000, 9000000000, deal_type="m_and_a", buyer="Devon", seller="Coterra"),
]


class TheView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        js = ("const D = await import('./lib/deals2.ts'); const A = await import('./lib/dealsai.ts');"
              f"const ds = {json.dumps(ROWS)}.map(D.toDeal);"
              "console.log(JSON.stringify({buyer: A.aiCells(ds, 'buyer'), supply: A.aiCells(ds, 'supply'),"
              " grid: A.aiCells(ds, 'grid'), quarter: A.aiCells(ds, 'quarter'),"
              " mw: A.largest(ds, 'mw').map((d) => d.id), usd: A.largest(ds, 'usd').map((d) => d.id),"
              " key: A.aiKey('with_mw', 'grid', ''), supplies: ds.map(A.supplyOf)}));")
        cls.r = node(js)

    def cell(self, dim, value):
        return next(c for c in self.r[dim] if c["value"] == value)

    def test_only_ai_tagged_deals(self):
        self.assertEqual(sum(c["deals"] for c in self.r["buyer"]), 5)   # Devon and Coterra is not AI-tagged

    def test_a_sum_of_the_stated_figures_with_its_count(self):
        amazon = self.cell("buyer", "Amazon")
        self.assertEqual((amazon["deals"], amazon["mw"], amazon["withMw"], amazon["usd"], amazon["withUsd"]), (2, 1150, 2, None, 0))
        tx = self.cell("grid", "ERCOT")
        self.assertEqual((tx["deals"], tx["mw"], tx["withMw"]), (2, 1200, 1))   # Google's solar PPA states no MW: counted, not added

    def test_the_kind_of_supply(self):
        self.assertEqual(self.r["supplies"], ["nuclear", "nuclear", "gas", "compute", "renewables_storage", "capital"])
        self.assertEqual(self.cell("supply", "nuclear")["mw"], 1150)

    def test_the_quarters_in_time_order(self):
        self.assertEqual([c["value"] for c in self.r["quarter"]], ["2026-Q2", "2026-Q3", "2026-Q4"])

    def test_the_largest(self):
        self.assertEqual(self.r["mw"], ["deal:3", "deal:1", "deal:2"])
        self.assertEqual(self.r["usd"], ["deal:4", "deal:3"])

    def test_the_key(self):
        self.assertEqual(self.r["key"], "deals|ai_with_mw|grid|-")


class TheSources(unittest.TestCase):
    def test_the_page_and_the_check(self):
        with open(os.path.join(SITE, "app", "deals", "page.tsx"), encoding="utf-8") as f:
            page = f.read()
        self.assertIn('const aiView = sp.view === "ai";', page)
        with open(os.path.join(SITE, "scripts", "check-values.mjs"), encoding="utf-8") as f:
            check = f.read()
        self.assertIn('String(p[1]).startsWith("ai_")', check)
        with open(os.path.join(SITE, "app", "deals", "ai", "view.tsx"), encoding="utf-8") as f:
            view = f.read()
        self.assertIn("aiKey(\"with_mw\", by, c.value)", view)
        self.assertNotIn("—", view)


if __name__ == "__main__":
    unittest.main()
