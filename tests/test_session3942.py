"""Session 3942 (chain 267): noaa_grid_weather's ISD-Lite address.

NOAA moved ISD-Lite to its Open Data Dissemination bucket on AWS. On 14 November 2026 the old address of a year's file
answered 200 with the bucket's HTML index page, and the connector's parser reads any bytes that are not gzip as text.
Held here: the new address, the old address read only for a file already saved from it, and a refusal of a body that is
not gzip. No network.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import noaa_grid_weather as g  # noqa: E402


class TheAddress(unittest.TestCase):
    def test_the_bucket(self):
        self.assertEqual(g.lite_url("722590", "03927", 2024),
                         "https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2024/722590-03927-2024.gz")

    def test_a_file_saved_from_the_old_address_is_reused(self):
        old = g.lite_url("722590", "03927", 2019, g.LITE_OLD)
        self.assertEqual(g.lite_source("722590", "03927", 2019, cached=lambda u: {"x": 1} if u == old else None), old)

    def test_otherwise_the_new_address(self):
        new = g.lite_url("722590", "03927", 2019)
        self.assertEqual(g.lite_source("722590", "03927", 2019, cached=lambda u: None), new)
        self.assertEqual(g.lite_source("722590", "03927", 2019, cached=lambda u: {"x": 1}), new)

    def test_an_html_page_is_not_a_file(self):
        self.assertFalse(g.is_gzip(b"<!DOCTYPE html>\r\n"))
        self.assertTrue(g.is_gzip(bytes([0x1F, 0x8B, 8, 8])))

    def test_the_connector_refuses_it(self):
        src = open(g.__file__, encoding="utf-8").read()
        self.assertIn("if not is_gzip(b):", src)
        self.assertNotIn('\nLITE = "https://www.ncei.noaa.gov', src)


if __name__ == "__main__":
    unittest.main()
