"""Session 884: the seven petroleum products in EIA's exports by destination.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_petroleum_exports.py with EIA's API replaced by pages
built here (figures made up for the test, not EIA's): crude oil and the total asked as before, the seven products asked
as a query of their own sorted by product, and a ceiling reached part way leaving out the product it cut, whole, named
in the header, never part of one. No network.

    python -m unittest tests.test_session884 -v
"""

import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_petroleum_exports as E  # noqa: E402


def recs(product, n, start=0):
    return [{"period": "2020-01", "duoarea": f"NUS-N{i:05d}", "area-name": f"A{i}", "product": product,
             "product-name": product, "units": "MBBL", "value": 1.0} for i in range(start, start + n)]


class FakeResponse:
    def __init__(self, url, body):
        self.url, self._body, self.status_code = url, body, 200

    def raise_for_status(self):
        pass

    def json(self):
        return self._body


def fake_get(more_pages, more_total):
    def get(url, timeout=None):
        if "EPC0" in url:
            return FakeResponse(url, {"response": {"total": 2, "data": recs("EPC0", 1) + recs("EPP0", 1)}})
        offset = int(url.split("offset=")[1].split("&")[0])
        return FakeResponse(url, {"response": {"total": more_total, "data": more_pages[offset // 5000]}})
    return get


class SevenProducts(unittest.TestCase):
    def run_with(self, pages, total, ceiling):
        written = {}

        def snap(s, name, header, log, cols):
            written["s"], written["header"] = s, header

        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(E.ip, "raw_cached", return_value=None), \
                mock.patch.object(E.ip, "load_key", return_value="k"), \
                mock.patch.object(E.ip.RAW, "open"), \
                mock.patch.object(E.ip, "write_snapshot", side_effect=snap), \
                mock.patch.object(E.time, "sleep"), \
                mock.patch.object(E.requests, "get", side_effect=fake_get(pages, total)):
            code = E.main(["--out-dir", tmp, "--ceiling", str(ceiling)])
        return code, written

    def test_all_seven_within_the_ceiling(self):
        pages = [recs("EPD0", 3000) + recs("EPJK", 2000), recs("EPJK", 10, 2000)]
        code, w = self.run_with(pages, 5010, 10)
        self.assertEqual(code, 0)
        products = set(w["s"]["entity"].str.split(":").str[-1])
        self.assertEqual(products, {"EPC0", "EPP0", "EPD0", "EPJK"})
        self.assertNotIn("left out whole", " ".join(w["header"]))
        self.assertIn("no record from EIA: EPM0F, EPLLPA, EPPR, EPLLEA, EPPC", " ".join(w["header"]))

    def test_a_ceiling_part_way_leaves_out_the_product_it_cut(self):
        pages = [recs("EPD0", 3000) + recs("EPJK", 2000), recs("EPJK", 5000, 2000), recs("EPJK", 1, 7000)]
        code, w = self.run_with(pages, 10001, 3)          # one for crude and the total, two pages of the products
        self.assertEqual(code, 0)
        s = w["s"]
        products = s["entity"].str.split(":").str[-1]
        self.assertEqual(set(products), {"EPC0", "EPP0", "EPD0"})
        self.assertEqual(int((products == "EPD0").sum()), 3000)
        self.assertIn("left out whole, the ceiling reached: EPM0F, EPJK, EPLLPA, EPPR, EPLLEA, EPPC", " ".join(w["header"]))

    def test_a_saved_page_keeps_its_own_retrieval_time(self):
        # session 891: a page reused from warehouse/raw carries the time it was really fetched, not the run's
        import json
        saved = json.dumps({"response": {"total": 2, "data": recs("EPC0", 1) + recs("EPP0", 1)}}).encode()
        hit = lambda c, url: (saved, {"retrieved_at": "2026-10-23T02:17:24Z"}) if "EPC0" in url else None  # noqa: E731
        written = {}
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(E.ip, "raw_cached", side_effect=hit), \
                mock.patch.object(E.ip, "load_key", return_value="k"), \
                mock.patch.object(E.ip.RAW, "open"), \
                mock.patch.object(E.ip, "write_snapshot", side_effect=lambda s, *a, **k: written.update(s=s)), \
                mock.patch.object(E.time, "sleep"), \
                mock.patch.object(E.requests, "get", side_effect=fake_get([recs("EPD0", 3)], 3)):
            self.assertEqual(E.main(["--out-dir", tmp, "--ceiling", "5"]), 0)
        s = written["s"]
        crude = s[s["entity"].str.endswith(":EPC0")]
        self.assertEqual(set(crude["retrieved_at"]), {"2026-10-23T02:17:24Z"})
        self.assertNotIn("2026-10-23T02:17:24Z", set(s[s["entity"].str.endswith(":EPD0")]["retrieved_at"]))

    def test_the_seven(self):
        self.assertEqual(E.MORE, ["EPD0", "EPM0F", "EPJK", "EPLLPA", "EPPR", "EPLLEA", "EPPC"])
        self.assertTrue(set(E.MORE).isdisjoint(E.PRODUCTS))


if __name__ == "__main__":
    unittest.main()
