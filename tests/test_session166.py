"""Session 166, part F: the datacenter tracker's accuracy fixes.

1. The merge rule of the news extractor (warehouse/datacenters/extract.py, same_site): a model's same_as is accepted
   only when the two facilities name the same operator or developer, the same site, or the same county or city in the
   same state. The Utah pair (the 2025 story of a USD 2B Utah datacenter, no operator and no county; the 2026 Valar
   Atomics 9.4 GW story) is never joined: the two share the word "Utah" and nothing else.
2. The facilities builder (warehouse/derived/datacenter_facilities.py): country is "US" only where a US state is
   stated; geo is "US-<state>" for such a row and empty otherwise, never "US" on no source's word.
3. The page's reading of the held table, where the table is on this machine: the cleaned status words only, and the
   counts the totals use (US rows not cancelled), computed as site/lib/largeload.ts does, against the table.

No model call, no request, no write outside a temporary directory. Skips cleanly without the tables.
"""

import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.environ.get("ERW_TABLES", os.path.join(ROOT, "warehouse", "output"))
HELD = os.path.join(OUT, "datacenter_facilities.csv")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(path):
    with open(path, encoding="utf-8") as f:
        n = sum(1 for line in f if line.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


class MergeRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        cls.x = load("dc_extract_166", os.path.join(ROOT, "warehouse", "datacenters", "extract.py"))

    def test_utah_pair_is_not_joined(self):
        utah_2025 = dict(operator="", developer="", site_name="", state="UT", county="", city="")
        valar_2026 = dict(operator="", developer="Valar Atomics", site_name="", state="UT", county="", city="")
        self.assertFalse(self.x.same_site(utah_2025, valar_2026))
        self.assertFalse(self.x.same_site(valar_2026, utah_2025))

    def test_a_state_alone_joins_nothing(self):
        a = dict(operator="Meta", developer="", site_name="", state="TX", county="", city="")
        b = dict(operator="Google", developer="", site_name="", state="TX", county="", city="")
        self.assertFalse(self.x.same_site(a, b))
        self.assertFalse(self.x.same_site(dict(operator="", developer="", site_name="", state="TX", county="", city=""), b))

    def test_same_operator_or_developer_joins(self):
        held = dict(operator="Meta", developer="", site_name="", state="LA", county="Richland", city="")
        self.assertTrue(self.x.same_site(held, dict(operator="Meta Platforms", developer="", site_name="", state="LA", county="", city="")))
        self.assertTrue(self.x.same_site(held, dict(operator="", developer="Meta", site_name="", state="", county="", city="")))
        self.assertTrue(self.x.same_site(dict(operator="", developer="Valar Atomics", site_name="", state="UT", county="", city=""),
                                         dict(operator="Valar Atomics", developer="", site_name="", state="UT", county="", city="")))

    def test_same_site_name_or_place_joins(self):
        self.assertTrue(self.x.same_site(dict(operator="", developer="", site_name="Project Southgate", state="", county="", city=""),
                                         dict(operator="Firmus", developer="", site_name="Project Southgate", state="", county="", city="")))
        self.assertTrue(self.x.same_site(dict(operator="", developer="", site_name="", state="TX", county="Bexar", city=""),
                                         dict(operator="", developer="", site_name="", state="TX", county="Bexar County", city="")))
        self.assertFalse(self.x.same_site(dict(operator="", developer="", site_name="", state="TX", county="Bexar", city=""),
                                          dict(operator="", developer="", site_name="", state="OH", county="Bexar", city="")))


class Country(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        cls.b = load("dc_facilities_166", os.path.join(ROOT, "warehouse", "derived", "datacenter_facilities.py"))

    def test_country_only_where_a_us_state_is_stated(self):
        self.assertEqual(self.b.country_of("TX"), "US")
        self.assertEqual(self.b.country_of("DC"), "US")
        self.assertEqual(self.b.country_of(""), "")
        self.assertEqual(self.b.country_of("TAS"), "")
        self.assertEqual(self.b.country_of("PR"), "US")  # Puerto Rico is in the gazetteer's list and is US
        self.assertEqual(self.b.US_STATES, HeldTable.US)

    def test_facility_geo_and_country(self):
        m = dict(kind="news", id="datacenter:abc", name="", operator="Firmus", developer="", state="", county="", city="",
                 lat="", lon="", mw="1600", mw_span="", status="withdrawn", project_status="cancelled", site_type="",
                 geo_precision="none", geo_note="", source="x", source_url="u", urls=["u"], queue_mw="",
                 **{f: "" for f in self.b.NEWS_ONLY})
        r = self.b.facility([m], "2026-10-09T00:00:00Z")
        self.assertEqual((r["country"], r["geo"], r["status"]), ("", "", "withdrawn"))
        r = self.b.facility([dict(m, state="UT")], "2026-10-09T00:00:00Z")
        self.assertEqual((r["country"], r["geo"]), ("US", "US-UT"))


@unittest.skipUnless(os.path.exists(HELD), "datacenter_facilities.csv is not on this machine")
class HeldTable(unittest.TestCase):
    """What the page shows, read from the held table (read only)."""

    VOCAB = {"", "planned", "under_construction", "operating", "withdrawn", "completed", "active"}
    US = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA",
          "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX",
          "UT", "VT", "VA", "WA", "WV", "WI", "WY", "PR"}  # the builder's list: the states, DC and Puerto Rico

    def test_page_list_is_the_builders(self):
        """site/lib/largeload.ts holds the same codes, for the pages' fallback before the table is reloaded."""
        with open(os.path.join(ROOT, "site", "lib", "largeload.ts"), encoding="utf-8") as f:
            src = f.read()
        block = src[src.index("US_STATES = new Set(["):]
        codes = set(__import__("re").findall(r'"([A-Z]{2})"', block[:block.index("]);")]))
        self.assertEqual(codes, self.US)

    def test_cleaned_status_holds_no_raw_field(self):
        d = read(HELD)
        self.assertTrue(set(d["status"]) <= self.VOCAB, sorted(set(d["status"]) - self.VOCAB))
        self.assertFalse(d["status"].str.contains("inDevelopment").any())

    def test_firmus_leaves_the_totals(self):
        d = read(HELD)
        country = d["country"] if "country" in d.columns else d["state"].map(lambda s: "US" if s in self.US else "")
        counted = d[(country == "US") & ~d["status"].isin(["withdrawn", "cancelled"])]
        self.assertFalse((counted["operator"] == "Firmus").any())
        self.assertLess(len(counted), len(d))


if __name__ == "__main__":
    unittest.main()
