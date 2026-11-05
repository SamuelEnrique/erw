"""Session 2566: BCRPData's monthly series of Peru's electricity production by department (MINEM's figures).

Energy Research Warehouse (ERW). Tests warehouse/connectors/bcrp_peru_electricity.py on responses built here (made up for
the test, not BCRP's): three requests of ten, ten and five series, GWh to MWh, a department's name without its accent, an
"n.d." cell not written, the series code kept; a series not asked, a month missing, a cell that is not a figure and
departments that miss the total stopping the run; the sector rule and the registration. No network.

    python -m unittest tests.test_session2566 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import bcrp_peru_electricity as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}
TO = "2005-3"
NAMES = ["Amazonas", "Ancash", "Apur" + chr(0xED) + "mac"] + [f"Dep{i:02d}" for i in range(21)] + ["Total"]


def docs(names=NAMES, value=None, months=("Jan.2005", "Feb.2005", "Mar.2005"), total=24.0):
    out = []
    for i in range(0, 25, 10):
        chunk = names[i:i + 10]
        series = [{"name": P.PREFIX + n + " (gwh)"} for n in chunk]
        periods = []
        for m in months:
            vals = [str(total) if n == "Total" else (value(n, m) if value else "1.0") for n in chunk]
            periods.append({"name": m, "values": vals})
        out.append({"config": {"title": "t", "series": series}, "periods": periods})
    return out


class Parse(unittest.TestCase):
    def test_rows(self):
        def value(n, m):
            if n == "Ancash":
                return "n.d." if m == "Feb.2005" else "2.0"
            return "3.0" if (n, m) == ("Amazonas", "Feb.2005") else "1.0"
        t = P.parse(docs(value=value, total=25.0), BASE, TO)
        r = {(e, ts[:7]): v for e, ts, v in zip(t.entity, t.ts_utc, t.value)}
        self.assertEqual(r[("bcrp_pe:total", "2005-01")], 25000.0)
        self.assertEqual(r[("bcrp_pe:apurimac", "2005-03")], 1000.0)
        self.assertNotIn(("bcrp_pe:ancash", "2005-02"), r)
        self.assertEqual(len(t), 25 * 3 - 1)
        self.assertEqual(set(t.x_series_code), set(P.CODES))
        self.assertEqual(len(P.urls()), 3)

    def test_stops(self):
        bad = [docs(names=NAMES[:24] + ["Lima"]),
               docs(months=("Jan.2005", "Mar.2005")),
               docs(value=lambda n, m: "1,0" if n == "Dep03" else "1.0"),
               docs(total=30.0)]
        for d in bad:
            with self.assertRaises(RuntimeError):
                P.parse(d, BASE, TO)


class Registered(unittest.TestCase):
    def test_sector_and_registration(self):
        self.assertEqual(B.sector_of(P.NAME), "power")
        self.assertIn(P.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {P.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
