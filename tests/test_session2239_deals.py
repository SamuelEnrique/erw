"""Session 2239 (chain 156): the disclosed prices and a reader's deal placed against them (site/lib/deals2.ts,
site/app/deals/comparables/).

Node runs the pure functions on rows shaped as the live set serves them; the count is always given, the median, lowest
and highest only from three prices; the placement says how many prices are below, equal and above, in the first
scope with three; nothing a reader types is stored or sent (the component's source holds no storage and no request);
check-values recomputes every new key with the same functions.
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


def row(i, typ, tech, state, price, date="2026-05-01"):
    return {"event_id": f"deal:{i}", "event_date": f"{date}T00:00:00Z", "status": "signed", "mw": "100",
            "price": "" if price is None else str(price), "currency": "USD", "parties": "", "source": "x",
            "source_url": f"https://example.org/{i}",
            "extra": {"deal_type": typ, "technology": tech, "state": state, "buyer": f"Buyer {i}", "seller": f"Seller {i}"}}


ROWS = [row(1, "ppa", "solar", "TX", 40), row(2, "ppa", "solar", "TX", 50), row(3, "ppa", "solar", "TX", 60),
        row(4, "ppa", "solar", "CA", 70), row(5, "offtake", "wind", "TX", 45, "2025-03-01"),
        row(6, "m_and_a", "solar", "TX", 999), row(7, "ppa", "nuclear", "PA", None)]


class Prices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        js = ("const D = await import('./lib/deals2.ts');"
              f"const ds = {json.dumps(ROWS)}.map(D.toDeal);"
              "const strip = (cs) => cs.map(({records, ...c}) => ({...c, ids: records.map((r) => r.id)}));"
              "console.log(JSON.stringify({priced: D.priced(ds).map((d) => d.id),"
              " tech: strip(D.priceCells(ds, 'technology')), grid: strip(D.priceCells(ds, 'grid')), year: strip(D.priceCells(ds, 'year')),"
              " p1: D.place(ds, {technology: 'solar', grid: 'ERCOT', price: 50}),"
              " p2: D.place(ds, {technology: 'solar', grid: 'CAISO', price: 80}),"
              " p3: D.place(ds, {technology: 'wind', grid: '', price: 10}),"
              " key: D.priceKey('median', 'technology', 'solar'), keyNone: D.priceKey('count', 'grid', '')}));")
        cls.r = node(js)

    def test_only_ppas_and_offtakes_that_state_a_price(self):
        self.assertEqual(self.r["priced"], ["deal:1", "deal:2", "deal:3", "deal:4", "deal:5"])   # not the M&A, not the unpriced

    def test_the_count_always_and_the_rest_from_three(self):
        solar = next(c for c in self.r["tech"] if c["value"] == "solar")
        self.assertEqual((solar["count"], solar["median"], solar["low"], solar["high"]), (4, 55, 40, 70))
        wind = next(c for c in self.r["tech"] if c["value"] == "wind")
        self.assertEqual((wind["count"], wind["median"], wind["low"], wind["high"]), (1, None, None, None))
        ercot = next(c for c in self.r["grid"] if c["value"] == "ERCOT")
        self.assertEqual((ercot["count"], ercot["median"]), (4, 47.5))
        self.assertEqual(ercot["ids"], ["deal:1", "deal:5", "deal:2", "deal:3"])   # the hover's records, by price

    def test_the_placement(self):
        p1 = self.r["p1"]
        self.assertEqual(p1["scope"], "solar in ERCOT")
        self.assertEqual((p1["count"], p1["below"], p1["equal"], p1["above"], p1["median"]), (3, 1, 1, 1, 50))
        # one solar price in CAISO is fewer than three: the scope widens to solar
        self.assertEqual(self.r["p2"]["scope"], "solar")
        self.assertEqual((self.r["p2"]["count"], self.r["p2"]["below"]), (4, 4))
        # one wind price: the scope widens to every priced deal
        self.assertEqual(self.r["p3"]["scope"], "every PPA and offtake that states a price")

    def test_the_keys(self):
        self.assertEqual(self.r["key"], "deals|price_median|technology|solar")
        self.assertEqual(self.r["keyNone"], "deals|price_count|grid|-")


class TheSources(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(SITE, *p), encoding="utf-8") as f:
            return f.read()

    def test_nothing_typed_is_stored_or_sent(self):
        s = self.read("app", "deals", "comparables", "PlaceDeal.tsx")
        for w in ("localStorage", "sessionStorage", "fetch(", "indexedDB", "document.cookie", "navigator.sendBeacon"):
            self.assertNotIn(w, s)
        self.assertIn('autoComplete="off"', s)

    def test_check_values_recomputes_the_new_keys(self):
        s = self.read("scripts", "check-values.mjs")
        self.assertIn('String(p[1]).startsWith("price_")', s)
        self.assertIn("D.priceCells(", s)

    def test_the_view_draws_the_section(self):
        s = self.read("app", "deals", "comparables", "view.tsx")
        self.assertIn('id="prices"', s)
        self.assertIn("<PlaceDeal", s)
        self.assertIn("priceKey(", s)
        self.assertNotIn("18,358", s)   # a figure on a page carries its key, or is not on the page


if __name__ == "__main__":
    unittest.main()
