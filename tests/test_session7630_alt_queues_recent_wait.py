"""Session 7630: the other choice of the ruling on a second wait on /queues (branch wip/alt-queues-1, not landed). The
headline "Request to operation" gave one median over every year; under the other choice it also gives the median of the
requests that reached operation in the last three operation years, as the All grids tab counts them.

What is held to (site/data/siting/connect.json, the All grids tab's file, built from Berkeley Lab's 2026 edition):
  operation years 2023 to 2025, a grid drawn at 5 requests or more; the recent waits, in years: ERCOT 3.82 (45.8 months,
    227 requests), CAISO 8.33, NYISO 7.27 (5 requests), PJM 5.94 (71.3 months), and the others the file holds; each the
    impact file's figure, so /queues and the All grids tab agree on one figure;
  the median over every year (site/data/queues.json) is unchanged beside it: ERCOT 3.70, CAISO 6.02, PJM 3.15;
  the second wait is drawn for a grid's every-technology view only, and only where the file holds a median.

No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


class TheSecondWait(unittest.TestCase):
    def test_the_recent_waits(self):
        c = load("site", "data", "siting", "connect.json")
        self.assertEqual((c["from"], c["to"], c["min_n"]), (2023, 2025, 5))
        yrs = {k: round(v["median"] / 12, 2) for k, v in c["grids"].items() if v["median"] is not None}
        self.assertEqual((yrs["ercot"], yrs["caiso"], yrs["nyiso"], yrs["pjm"]), (3.82, 8.33, 7.27, 5.94))
        self.assertEqual((c["grids"]["ercot"]["n"], c["grids"]["ercot"]["median"], c["grids"]["pjm"]["median"]), (227, 45.8, 71.3))

    def test_the_page(self):
        with open(os.path.join(ROOT, "site", "app", "queues", "page.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('import connectJson from "@/data/siting/connect.json";', s)
        self.assertIn('return tech === "all" && g && g.median !== null && g.n >= CONNECT.min_n ? { n: g.n, median: g.median } : null;', s)
        self.assertIn("<strong>{(r.median / 12).toFixed(2)}</strong> years, median", s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
