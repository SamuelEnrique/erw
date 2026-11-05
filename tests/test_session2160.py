"""Session 2160: County Business Patterns for NAICS 518210 (data processing and hosting) by state.

Energy Research Warehouse (ERW). Tests warehouse/connectors/census_cbp_hosting.py on zipped files built here in the
Bureau's form (figures made up for the test, not the Bureau's): only NAICS 518210 and all legal forms ("-") taken, the
payroll in dollars, the noise flags and the NAICS edition kept, a file without an lfo column read whole; a header
without a needed column, a state given twice and a state code not in the map each stopping the run; the sector rule and
the holds. No network.

    python -m unittest tests.test_session2160 -v
"""

import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import census_cbp_hosting as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEAD = '"fipstate","naics","lfo","emp_nf","emp","qp1_nf","qp1","ap_nf","ap","est"'


def zipped(lines, head=HEAD):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("cbp22st.txt", "\n".join([head] + lines) + "\n")
    return b.getvalue()


def line(st="51", naics="518210", lfo="-", emp=1000, ap=90000, est=40, nf="G"):
    return f'"{st}","{naics}","{lfo}","{nf}",{emp},"G",20000,"H",{ap},{est}'


class Parse(unittest.TestCase):
    def test_file(self):
        rows = C.parse(zipped([line(), line(lfo="C", emp=700), line(naics="------", emp=99999), line(st="06", emp=5000, nf="J")]), 2022, BASE)
        self.assertEqual(len(rows), 6)
        va = {r["variable"]: r for r in rows if r["geo"] == "US-VA"}
        self.assertEqual((va["employment"]["value"], va["annual_payroll"]["value"], va["annual_payroll"]["unit"], va["establishments"]["value"]),
                         (1000.0, 90000 * 1000.0, "USD", 40.0))
        self.assertEqual((va["employment"]["x_emp_noise"], va["employment"]["x_ap_noise"], va["employment"]["x_naics_vintage"]), ("G", "H", "2022"))
        old = C.parse(zipped(['"51","518210","G",800,"G",1,"G",5000,30'], head='"fipstate","naics","emp_nf","emp","qp1_nf","qp1","ap_nf","ap","est"'),
                      2015, BASE)
        self.assertEqual((len(old), old[0]["x_naics_vintage"]), (3, "2017"))

    def test_stops(self):
        for content, words in [(zipped([line()], head='"fipstate","naics","lfo","emp","ap","est"'), "the header lacks"),
                               (zipped([line(), line()]), "given twice"), (zipped([line(st="72")]), "not in the map"),
                               (zipped([line(naics="------")]), "no line")]:
            with self.assertRaises(RuntimeError) as c:
                C.parse(content, 2022, BASE)
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.TABLE), "power;datacenters")
        self.assertIn(C.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
