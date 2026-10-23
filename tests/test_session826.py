"""Session 826: the tracker's A and B (chain 080). The pair from the address, USD per MW, the page's code. No request."""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_session822 import node  # noqa: E402


class LibTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.got = node(
            "const m = await import('./lib/dealspublic.ts'); const ids = ['deal:1', 'deal:2', 'deal:3'];"
            "console.log(JSON.stringify({"
            " ok: m.abPair({a: 'deal:1', b: 'deal:2'}, ids), same: m.abPair({a: 'deal:1', b: 'deal:1'}, ids), none: m.abPair({}, ids),"
            " held: m.abPair({a: 'deal:1', b: 'deal:9'}, ids), one: m.abPair({a: 'deal:3'}, ids),"
            " per: [m.usdPerMw({mw: 433, dollars: 4200000000}), m.usdPerMw({mw: null, dollars: 1}), m.usdPerMw({mw: 0, dollars: 1}), m.usdPerMw({mw: 5, dollars: null})],"
            " key: m.abKey('deal:1', 'usd_per_mw')}));"
        )

    def test_pair(self):
        self.assertEqual(self.got["ok"], {"a": "deal:1", "b": "deal:2", "why": ""})
        self.assertEqual(self.got["same"]["b"], None)
        self.assertIn("same deal", self.got["same"]["why"])
        self.assertEqual(self.got["none"], {"a": None, "b": None, "why": "Choose two of the shown deals above."})
        self.assertIn("not one of the shown rows", self.got["held"]["why"])   # a held id in the address draws nothing
        self.assertEqual(self.got["held"]["b"], None)
        self.assertEqual(self.got["one"]["a"], "deal:3")
        self.assertIsNone(self.got["one"]["b"])

    def test_usd_per_mw(self):
        self.assertAlmostEqual(self.got["per"][0], 4200000000 / 433)
        self.assertEqual(self.got["per"][1:], [None, None, None])
        self.assertEqual(self.got["key"], "dealpub|ab|deal:1|usd_per_mw")


class PageCodeTest(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_compare_on_the_page(self):
        page = self.read("site", "app", "deals", "page.tsx")
        self.assertIn("<DealsCompare rows={PUBLIC.shown.map(toPublicDeal)} sp={sp} />", page)
        c = self.read("site", "app", "deals", "Compare.tsx")
        for s in ('name="a"', 'name="b"', "What differs, B against A", 'abKey(d.id, "usd_per_mw")', "dealpub|${d.id}|mw", "No sentence here judges"):
            self.assertIn(s, c, s)
        self.assertIn("/deals?a=deal%3A70bf30d372e1d674&b=deal%3Ad6eda0ffd6db76cd", self.read("site", "scripts", "check-values.mjs"))
        self.assertIn('p[1] === "ab"', self.read("site", "scripts", "check-values.mjs"))
        self.assertIn("dealpub|ab|<deal>|usd_per_mw", self.read("docs", "methods", "energy_deals.md"))

    def test_no_em_dash(self):
        for p in (("site", "app", "deals", "Compare.tsx"), ("site", "lib", "dealspublic.ts"), ("tests", "test_session826.py")):
            self.assertNotIn(chr(0x2014), self.read(*p), p)


if __name__ == "__main__":
    unittest.main()
