"""Session 466: the deal tracker's comparables view (/deals?view=comparables).

Part one runs comparables() of site/lib/deals2.ts in Node on the table's rows (git holds energy_deals) and computes
the same cells here: the deals of each group, those that state a price in USD per MWh and a size in MW, and the
median of each only where three or more state it. Part two reads the view, the page's routing, check-values' key and
the method note.
"""

import json
import os
import re
import shutil
import statistics
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_session113 import dup, live_rows, node, src, table  # noqa: E402

DASHES = (chr(0x2014), chr(0x2013))
DIMS = ("type", "technology", "grid", "year")
FILES = [("site", "lib", "deals2.ts"), ("site", "app", "deals", "comparables", "view.tsx"), ("site", "app", "deals", "page.tsx"),
         ("site", "scripts", "check-values.mjs"), ("docs", "methods", "energy_deals.md"), ("tests", "test_session466.py")]


def num(v):
    return float(v) if v != "" else None


def median3(xs):
    return statistics.median(xs) if len(xs) >= 3 else None


class TheCells(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            d = table("energy_deals")
        except FileNotFoundError:
            raise unittest.SkipTest("energy_deals is not on this machine")
        folds = dup.register()
        folds = folds[folds["ruling"] == "fold"]
        cls.d = d[~d["event_id"].isin(folds["duplicate_event_id"])].copy()
        cls.n_raw = len(d)
        grid = dict(re.findall(r"(\w\w): \"([A-Z-]+)\"", re.search(r"STATE_GRID: Record<string, string> = \{(.*?)\};", src("site", "lib", "deals2.ts"), re.S).group(1)))
        cls.d["grid"] = cls.d["state"].str.upper().map(grid).fillna("")
        cls.d["year"] = cls.d["event_date"].str[:4]
        cls.d["type"] = cls.d["deal_type"]
        tmp = tempfile.mkdtemp(prefix="erw466_")
        cls.addClassCleanup(shutil.rmtree, tmp, True)
        path = os.path.join(tmp, "rows.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(live_rows(d), f)
        cls.got = node(
            "const fs = (await import('node:fs')).default; const m = await import('./lib/deals2.ts');"
            f"const rows = JSON.parse(fs.readFileSync({json.dumps(path)}, 'utf-8'));"
            "const pairs = JSON.parse(fs.readFileSync('data/deal_duplicates.json', 'utf-8')).pairs;"
            "const all = m.fold(rows.map(m.toDeal), pairs);"
            f"const out = Object.fromEntries({json.dumps(DIMS)}.map((k) => [k, m.comparables(all, k).map((c) => ({{ ...c, shown: m.shown(c) }}))]));"
            "const keys = [m.compKey('median_mw', 'type', 'ppa'), m.compKey('deals', 'grid', '')];"
            "const med = [m.medianOf([1, 2]), m.medianOf([3, 1, 2]), m.medianOf([4, 1, 3, 2])];"
            "console.log(JSON.stringify({ out, keys, med, fewer: m.FEWER, min: m.MIN_DISCLOSED }));")

    def want(self, dim):
        out = {}
        for v, g in self.d.groupby(dim):
            prices = [x for x in map(num, g["price"]) if x is not None]
            mws = [x for x in map(num, g["mw"]) if x is not None]
            out[v] = {"deals": len(g), "withPrice": len(prices), "withMw": len(mws), "medianPrice": median3(prices), "medianMw": median3(mws)}
        return out

    def test_every_cell_of_every_dimension(self):
        for dim in DIMS:
            got = {c["value"]: c for c in self.got["out"][dim]}
            want = self.want(dim)
            self.assertEqual(set(got), set(want), dim)
            for v, w in want.items():
                for k, x in w.items():
                    if x is None or got[v][k] is None:
                        self.assertEqual(got[v][k], x, (dim, v, k))
                    else:
                        self.assertAlmostEqual(got[v][k], x, places=6, msg=(dim, v, k))
            self.assertEqual(sum(c["deals"] for c in got.values()), len(self.d), dim)

    def test_nothing_from_fewer_than_three(self):
        self.assertEqual((self.got["min"], self.got["fewer"]), (3, "fewer than three"))
        self.assertEqual(self.got["med"], [None, 2, 2.5])
        for dim in DIMS:
            for c in self.got["out"][dim]:
                self.assertEqual(c["medianPrice"] is None, c["withPrice"] < 3, (dim, c["value"]))
                self.assertEqual(c["medianMw"] is None, c["withMw"] < 3, (dim, c["value"]))
                s = c["shown"]
                want = "price" if c["medianPrice"] is not None else "mw" if c["medianMw"] is not None else "none"
                self.assertEqual(s["what"], want, (dim, c["value"]))

    def test_not_stated_is_last_and_the_rest_by_deals(self):
        for dim in DIMS:
            cs = self.got["out"][dim]
            vals = [c["value"] for c in cs]
            if "" in vals:
                self.assertEqual(vals[-1], "", dim)
                self.assertEqual(cs[-1]["label"], "not stated")
            stated = [c["deals"] for c in cs if c["value"] != ""]
            self.assertEqual(stated, sorted(stated, reverse=True), dim)

    def test_the_keys(self):
        self.assertEqual(self.got["keys"], ["deals|comp_median_mw|type|ppa", "deals|comp_deals|grid|-"])

    def test_the_table_of_20_october(self):
        # 492 rows, extracted 2026-10-20T06:17:34Z: no deal states a price, so no group has a median price
        if self.n_raw != 492:
            raise unittest.SkipTest("energy_deals has moved since 20 October")
        for dim in DIMS:
            self.assertTrue(all(c["medianPrice"] is None for c in self.got["out"][dim]), dim)
            self.assertEqual(sum(c["withMw"] for c in self.got["out"][dim]), int((self.d["mw"] != "").sum()), dim)


class ThePage(unittest.TestCase):
    def test_the_address_and_the_tab(self):
        p = src("site", "app", "deals", "page.tsx")
        self.assertIn('const comparablesView = sp.view === "comparables";', p)
        self.assertIn('const tab = comparablesView ? "tracker" : tabOf("/deals", sp.tab);', p)
        self.assertIn("<ComparablesView sp={sp} />", p)
        self.assertIn('href="/deals?view=comparables"', src("site", "app", "deals", "v2", "view.tsx"))

    def test_every_figure_is_keyed_and_the_hold_shows_nothing_of_a_row(self):
        v = src("site", "app", "deals", "comparables", "view.tsx")
        for stat in ("deals", "with_price", "with_mw", "median_price", "median_mw"):
            self.assertIn(f'compKey("{stat}", by, c.value)', v)
        self.assertIn("<DealsHeld />", v)
        self.assertLess(v.index("isLicenseReason(read.reason)"), v.index("<Bars cells"))
        self.assertIn("{FEWER}", v)

    def test_check_values_reads_the_keys_with_the_page_functions(self):
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "deals" && String(p[1]).startsWith("comp_"))', c)
        self.assertIn('await import("../lib/deals2.ts")', c)
        self.assertIn('"/deals?view=comparables"', c)
        floor = json.loads(src("site", "scripts", "check-values-floor.json"))["floor"]
        self.assertEqual(floor["/deals?view=comparables"], 0)

    def test_the_method_note_names_every_key(self):
        n = src("docs", "methods", "energy_deals.md")
        for stat in ("comp_deals", "comp_with_price", "comp_median_price", "comp_with_mw", "comp_median_mw"):
            self.assertIn(f"`deals|{stat}|<dimension>|<value>`", n)
        self.assertIn("Nothing is computed from fewer than three disclosed deals", n)

    def test_no_dash(self):
        for f in FILES:
            s = src(*f)
            for ch in DASHES:
                self.assertNotIn(ch, s, f)


if __name__ == "__main__":
    unittest.main()
