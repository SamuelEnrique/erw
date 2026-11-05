"""Session 2538: ERU's annual report on the Czech electricity system 2025, tables 3.1 to 3.3.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eru_czech_electricity.py on page texts built here (made up for
the test, not ERU's): the sections of table 3.1 and their technologies, a label that wraps (the own use rows), table
3.2's rows to its footnote and the chart's figures after it passed over, its repeated own use not taken twice, exports
written positive, table 3.3's second block a year, GWh to MWh; a row not in the map, a row missing, months not summing
to their year, technologies not summing to their total and a figure of another form stopping the run; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2538 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eru_czech_electricity as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
NL = chr(10)
R_ = chr(0x159)
T31 = "3.1 Bilance elekt" + R_ + "iny " + E.EN + " zdroje [GWh]"
T32 = "3.2 Bilance elekt" + R_ + "iny " + E.EN + " spot" + R_ + "eba [GWh]"
T33 = "3.3 V" + chr(0xFD) + "voj bilance a v" + chr(0xFD) + "roby elekt" + R_ + "iny [GWh]"
YEARS = "2016 2017 2018 2019 2020 2021 2022 2023 2024 2025"


def months(v, n=12):
    """n months of v GWh and their year."""
    cell = f"{v:.1f}".replace(".", ",")
    year = f"{v * n:,.1f}".replace(",", " ").replace(".", ",")
    return " ".join([cell] * n + [year])


def page31(extra=None, bad_total=False):
    lines = [T31, "Leden ... Celkem"]
    techs = list(E.TECH)
    lines.append(E.SECT31[0][0] + " " + months(8.0 if not bad_total else 9.0))
    lines += [t + " " + months(1.0) for t in techs]
    lines += ["Technologick" + chr(0xE1) + " vlastn" + chr(0xED) + " spot" + R_ + "eba", "elekt" + R_ + "iny na v" + chr(0xFD) + "robu elekt" + R_ + "iny",
              "(TVS ) " + months(8.0), "e"]
    lines += [t + " " + months(1.0) for t in techs]
    lines += ["Technologick" + chr(0xE1) + " vlastn" + chr(0xED) + " spot" + R_ + "eba", E.SECT31[2][0] + " " + months(4.0), "t"]
    lines += [t + " " + months(1.0) for t in techs[:4]]
    lines.append(E.SECT31[3][0] + " " + months(8.0))
    lines += [t + " " + months(1.0) for t in techs]
    if extra:
        lines.append(extra)
    return NL.join(lines + ["7"])


def page32(drop=None, extra=None):
    lines = [T32, "2025", "Leden ... Celkem"]
    for label in E.ROWS32:
        if label == drop:
            continue
        v = -2.0 if label.startswith("Export") else 2.0
        lines.append(label + " " + months(v))
    if extra:
        lines.append(extra)
    lines += ["*) zahrnuty " + chr(0xFA) + "daje PS", "Nezn" + chr(0xE1) + "m" + chr(0xFD) + " graf " + months(5.0), "8"]
    return NL.join(lines)


def page33(bad=False):
    first = " ".join(["83 306"] * 10)
    lines = [T33, "2025", YEARS, E.SECT31[0][0] + " " + first, YEARS]
    lines.append(E.SECT31[0][0] + " " + " ".join(["8,0"] * 9 + ["96,0" if not bad else "97,0"]))
    lines += [t + " " + " ".join(["1,0"] * 9 + ["12,0"]) for t in E.TECH]
    lines += ["Celkem Pomocn" + chr(0xE9) + " N" + chr(0xE1) + "r" + chr(0x16F) + "st", "9"]
    return NL.join(lines)


def pages(p31=None, p32=None, p33=None):
    toc = "OBSAH 3.1 Bilance elekt" + R_ + "iny - zdroje 7"
    return [toc, p31 or page31(), p32 or page32(), p33 or page33()]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = E.parse_pages(pages(), BASE)
        r = {(e, v, ts[:7]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("eru:cz:nuclear", "gross_generation", "2025-03")], 1000.0)
        self.assertEqual(r[("eru:cz:total", "own_use_power", "2025-12")], 8000.0)
        self.assertEqual(r[("eru:cz:steam", "own_use_heat", "2025-01")], 1000.0)
        self.assertNotIn(("eru:cz:wind", "own_use_heat", "2025-01"), r)
        self.assertEqual(r[("eru:cz:transmission", "exports", "2025-06")], 2000.0)
        self.assertEqual(r[("eru:cz:households", "consumption", "2025-06")], 2000.0)
        self.assertEqual(r[("eru:cz:solar", "annual_gross_generation", "2025-01")], 12000.0)
        self.assertEqual(r[("eru:cz:total", "annual_gross_generation", "2016-01")], 8000.0)
        self.assertEqual(len(t), (9 + 9 + 5 + 9) * 12 + (len(E.ROWS32) - 2) * 12 + 9 * 10)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [pages(p31=page31(extra="Jadern" + chr(0xE1) + " f" + chr(0xFA) + "ze " + months(1.0))),
               pages(p31=page31(bad_total=True)),
               pages(p32=page32(drop="Celkov" + chr(0xE9) + " ztr" + chr(0xE1) + "ty")),
               pages(p32=page32(extra="Dovoz " + months(1.0))),
               pages(p32=page32(extra=list(E.ROWS32)[0] + " " + " ".join(["1,0"] * 12) + " 99,0")),
               pages(p33=page33(bad=True)),
               pages(p31=page31().replace("1,0 1,0", "1.0 1,0", 1)),
               pages()[:3]]
        for p in bad:
            with self.assertRaises((RuntimeError, ValueError)):
                E.parse_pages(p, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
