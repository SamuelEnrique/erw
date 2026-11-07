"""Session 2241 (chain 156): the deals' charts, every figure keyed and traced (site/app/deals/charts/view.tsx,
site/lib/dealsai.ts figures(), scripts/check_deals.py).

check_deals.py recomputes each figure with its own Python and compares it with the page's functions run by node; here
on a small table written for the test (a folded pair, a deal with no MW, an AI deal, a priced PPA) and, where this
checkout holds it, on energy_deals itself. The view's source is read for the brand's colors, the hover titles and
the keys on every mark.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import check_deals  # noqa: E402

COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
        "source_url", "deal_type", "buyer", "seller", "technology", "state", "ai_power", "kind", "buyer_name", "seller_name"]


def table(rows):
    d = tempfile.mkdtemp(prefix="erw_s2241_")
    pd.DataFrame([{c: r.get(c, "") for c in COLS} for r in rows], columns=COLS).to_csv(
        os.path.join(d, "energy_deals.csv"), index=False)
    return d


ROWS = [
    {"event_id": "deal:6d416fb10be3a6f0", "event_date": "2026-09-30T00:00:00Z", "mw": "190", "deal_type": "ppa", "buyer": "Amazon",
     "seller": "Constellation", "technology": "nuclear", "ai_power": "true", "source": "x", "source_url": "https://example.org/1"},
    # folded into the row above by the register (warehouse/deals/duplicates.csv, session 2233)
    {"event_id": "deal:3768a40d6f7e3242", "event_date": "2026-10-06T00:00:00Z", "mw": "890", "deal_type": "ppa", "buyer": "Amazon",
     "seller": "Constellation Energy", "technology": "nuclear", "ai_power": "true", "source": "x", "source_url": "https://example.org/2"},
    {"event_id": "deal:b", "event_date": "2026-10-19T00:00:00Z", "mw": "960", "deal_type": "ppa", "buyer": "Amazon", "seller": "AEP",
     "seller_name": "American Electric Power", "kind": "smr", "ai_power": "true", "source": "x", "source_url": "https://example.org/3"},
    {"event_id": "deal:c", "event_date": "2026-11-02T00:00:00Z", "mw": "", "deal_type": "m_and_a", "buyer": "Devon", "seller": "Coterra",
     "ai_power": "false", "source": "x", "source_url": "https://example.org/4"},
    {"event_id": "deal:d", "event_date": "2026-08-01T00:00:00Z", "mw": "100", "price": "68", "deal_type": "ppa", "buyer": "Google",
     "seller": "NextEra", "technology": "solar", "state": "TX", "ai_power": "true", "source": "x", "source_url": "https://example.org/5"},
    {"event_id": "deal:e", "event_date": "2026-08-15T00:00:00Z", "mw": "1200", "deal_type": "other", "seller": "BKV",
     "kind": "gas_buildout", "ai_power": "false", "source": "x", "source_url": "https://example.org/6"},
]


class TheTrace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("node"):
            raise unittest.SkipTest("node is not on this machine")
        cls.dir = table(ROWS)
        d, folded = check_deals.deals_of(os.path.join(cls.dir, "energy_deals.csv"))
        cls.page, cls.mine = check_deals.page_figures(d), check_deals.recompute(d, folded)

    def test_every_figure_agrees(self):
        lines, bad = check_deals.compare(self.page, self.mine)
        self.assertEqual(bad, 0, "\n".join(x for x in lines if not x.startswith("ok")))
        self.assertGreater(len(lines), 10)

    def test_the_figures(self):
        m = self.mine
        self.assertEqual(m["deals|chart_mw|2026-Q3|nuclear"], 190)        # the folded repeat of 890 MW is not added
        self.assertEqual(m["deals|chart_mw|2026-Q4|nuclear"], 960)
        self.assertEqual(m["deals|chart_mw|2026-Q4|without"], 1)          # Devon and Coterra, counted, not drawn
        self.assertEqual(m["deals|chart_mw|2026-Q3|gas"], 1200)
        self.assertEqual(m["deals|chart_ai|2026-Q3|share"], round(1000 * 290 / 1490) / 10)
        self.assertEqual(m["deals|chart_price|deal:d|price"], 68)
        self.assertEqual(m["deals|chart_party|Amazon|mw"], 1150)
        self.assertEqual(m["deals|chart_party|American Electric Power|mw"], 960)

    def test_a_disagreement_fails(self):
        lines, bad = check_deals.compare({**self.page, "deals|chart_party|Amazon|mw": 1}, self.mine)
        self.assertEqual(bad, 1)
        self.assertTrue(any(x.startswith("FAIL") for x in lines))


class TheWarehouse(unittest.TestCase):
    def test_the_stored_deals_trace(self):
        path = os.path.join(ROOT, "warehouse", "output", "energy_deals.csv")
        if not os.path.exists(path) or not shutil.which("node"):
            raise unittest.SkipTest("energy_deals or node is not on this machine")
        self.assertEqual(check_deals.main(["--quiet"]), 0)


class TheView(unittest.TestCase):
    def test_brand_colors_hovers_and_keys(self):
        with open(os.path.join(ROOT, "site", "app", "deals", "charts", "view.tsx"), encoding="utf-8") as f:
            s = f.read()
        for c in ("var(--chart-ink)", "var(--color-accent)", "var(--chart-blue)", "var(--chart-grey)", "var(--chart-light)"):
            self.assertIn(c, s + open(os.path.join(ROOT, "site", "lib", "dealsai.ts"), encoding="utf-8").read())
        self.assertGreaterEqual(s.count("<title>"), 5)   # every mark has its hover
        for chart in ("chart_mw", "chart_price", "chart_ai", "chart_party"):
            self.assertIn(f"data-check={{`deals|{chart}|", s)
        self.assertIn('stroke="#FFFFFF" strokeWidth="1"', s)   # touching fills parted by a 1 px white line
        self.assertIn("The figures as a table", s)
        self.assertNotIn("—", s)


if __name__ == "__main__":
    unittest.main()
