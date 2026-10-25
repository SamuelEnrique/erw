"""Session 2525: SORS's Energy Balances, 2024, table 1 (Serbia's balance of electricity).

Energy Research Warehouse (ERW). Tests warehouse/connectors/sors_serbia_electricity.py on a page text built here (made up
for the test, not SORS's): primary production by source from the first three columns, the electricity column's rows,
section rows setting the variable of the plant and sector rows under them, a footnote mark and a Latin E at a label's
start, decimal commas, GWh to MWh, rows of only "-" not written; a row not in the map, a row before its section, a skipped
row holding a figure and a page without the table stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2525 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import sors_serbia_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
NL = chr(10)
ROWS = ["Примарна производња енергије 162,680 1354,064 10511,634 -",
        "Увоз - - - 6936,172",
        "Салдо залиха - - - -",
        "Производња енергије трансформацијом - - - 12028,378",
        "Хидроелектране - - - 10511,634",
        "Ветроелектране - - - 1354,064",
        "Соларне електране - - - 162,680",
        "Топлане - - - -",
        "Сопствена потрошња у енергетском сектору1) - - - 105,295",
        "Хидроелектране - - - 86,835",
        "Ветроелектране - - - 18,460",
        "Губици - - - 3984,350",
        "Eнергија расположива за финалну потрошњу - - - 29554,924",
        "Финална потрошња за енергетске сврхе - - - 29554,924",
        "Индустрија2) - - - 9562,137",
        "Домаћинства - - - 13225,392"]


def page(rows=ROWS):
    return NL.join(["1." + S.TITLE + " / Balance of Electricity in 2024", "Electricity (total)", "GWh"] + rows + ["1) Укључена је ..."])


class Parse(unittest.TestCase):
    def test_rows(self):
        t = S.parse_text(page(), BASE)
        r = {(e, v): x for e, v, x in zip(t.entity, t.variable, t.value)}
        self.assertEqual(r[("sors:rs:solar", "primary_production")], 162680.0)
        self.assertEqual(r[("sors:rs:hydro", "primary_production")], 10511634.0)
        self.assertEqual(r[("sors:rs:total", "imports")], 6936172.0)
        self.assertEqual(r[("sors:rs:hydro", "gross_production")], 10511634.0)
        self.assertEqual(r[("sors:rs:hydro", "own_use")], 86835.0)
        self.assertEqual(r[("sors:rs:total", "own_use")], 105295.0)
        self.assertEqual(r[("sors:rs:total", "available_final")], 29554924.0)
        self.assertEqual(r[("sors:rs:industry", "final_consumption")], 9562137.0)
        self.assertNotIn(("sors:rs:district_heating", "gross_production"), r)
        self.assertEqual(len(t), 3 + 1 + 4 + 3 + 1 + 1 + 3)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [page(ROWS + ["Нуклеарне електране - - - 1,000"]),
               page(["Примарна производња енергије 1,0 1,0 1,0 -", "Хидроелектране - - - 1,000"] + ROWS[1:]),
               page(ROWS[:2] + ["Салдо залиха - - - 5,000"] + ROWS[3:]),
               "no table here"]
        for text in bad:
            with self.assertRaises(RuntimeError):
                S.parse_text(text, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
