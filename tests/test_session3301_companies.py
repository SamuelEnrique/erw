"""Session 3301 (chain 200): the company database's resolution rules (warehouse/derived/companies.py).

Energy Research Warehouse (ERW). The normalization, the party splitting, the descriptions, the possessive and the NRC's
parent field, the anchors, the reviewed aliases, the company-word rule and the licenses, on names written here (test
fixtures, not the warehouse's rows). No network, no data lock (nothing is written under warehouse/output).

    python -m unittest tests.test_session3301_companies -v
"""

import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import companies as C  # noqa: E402


def m(table, row, role, raw, anchor="", **kw):
    return C.mention(table, row, role, raw, anchor, **kw)


class Normalize(unittest.TestCase):
    def test_suffixes_and_punctuation(self):
        self.assertEqual(C.norm("Duke Energy Carolinas, LLC"), "duke energy carolinas")
        self.assertEqual(C.norm("NRG Energy, Inc."), "nrg energy")
        self.assertEqual(C.norm("Entergy Nuclear Operations, Inc."), "entergy nuclear operations")
        self.assertEqual(C.norm("Brady Power Partners, L.P."), "brady power partners")
        self.assertEqual(C.norm("The Southern Company"), "southern")
        self.assertEqual(C.norm("  "), "")

    def test_ampersand_and_eia_abbreviations(self):
        self.assertEqual(C.norm("Virginia Electric & Power Co"), "virginia electric and power")
        self.assertEqual(C.norm("Tri-County Elec Coop, Inc"), "tri county electric cooperative")
        self.assertEqual(C.norm("Victory Electric Coop Assn Inc"), "victory electric cooperative association")
        self.assertEqual(C.norm("American Mun Power-Ohio, Inc"), "american municipal power ohio")

    def test_co_inside_a_name_is_company(self):
        self.assertEqual(C.norm("Public Service Co of Colorado"), C.norm("Public Service Company of Colorado"))
        self.assertEqual(C.norm("Northern States Power Co - Minnesota"), "northern states power company minnesota")

    def test_case_and_accents(self):
        self.assertEqual(C.norm("Tempus Power management LLC"), C.norm("Tempus power management LLC"))
        self.assertEqual(C.norm("AtkinsRéalis"), "atkinsrealis")

    def test_core_drops_one_company_word(self):
        self.assertEqual(C.core("constellation energy"), "constellation")
        self.assertEqual(C.core("nextera energy"), "nextera")
        self.assertIsNone(C.core("american energy"))       # a common word is not a company
        self.assertIsNone(C.core("bp energy"))             # shorter than four letters
        self.assertIsNone(C.core("first solar"))           # no company word at the end


class Parties(unittest.TestCase):
    def test_split(self):
        self.assertEqual(C.split_parties("Apollo and Blackstone"), ["Apollo", "Blackstone"])
        self.assertEqual(C.split_parties("Nvidia, Amazon and Microsoft"), ["Nvidia", "Amazon", "Microsoft"])
        self.assertEqual(C.split_parties("Google;RWE"), ["Google", "RWE"])
        self.assertEqual(C.split_parties("Babcock & Wilcox"), ["Babcock & Wilcox"])
        got = C.split_parties("Bank of China, Industrial and Commercial Bank of China Limited (ICBC), and China "
                              "Construction Bank (Asia)")
        self.assertEqual(got, ["Bank of China", "Industrial and Commercial Bank of China Limited (ICBC)",
                               "China Construction Bank (Asia)"])

    def test_descriptions(self):
        for d in ("investors", "new strategic and institutional investors", "South Korea", "United States",
                  "Amazon data center unit", "Japanese firms", "Meta-backed data centre", "Blackstone vehicle",
                  "CHIPS Act", "Standard Lithium-Equinor JV", "State of Indiana", "Belgian state",
                  "Poland's Ministry of Energy", "Wall Street banks", "Fusion Startup"):
            self.assertTrue(C.is_description(d), d)
        for n in ("Google", "Blue Owl", "Matter Venture Partners", "PowerHouse Data Centers", "Bank of China",
                  "Energy Capital Partners", "Related Digital"):
            self.assertFalse(C.is_description(n), n)

    def test_possessive(self):
        self.assertEqual(C.split_possessive("Blackstone's QTS"), ("QTS", "Blackstone"))
        self.assertEqual(C.split_possessive("ADNOC's XRG"), ("XRG", "ADNOC"))
        self.assertEqual(C.split_possessive("Google"), ("Google", ""))

    def test_nrc_licensee_field_with_several_names(self):
        # session 3304: the NRC joins licensees by "<br>", each with its part after an en dash
        en = chr(0x2013)
        got = C.nrc_names(f"Calvert Cliffs Nuclear Power Plant, LLC {en} Owner<br> Constellation Energy Generation, LLC {en} Operator")
        self.assertEqual(got, ["Calvert Cliffs Nuclear Power Plant, LLC", "Constellation Energy Generation, LLC"])
        self.assertEqual(C.nrc_names("Tennessee Valley Authority"), ["Tennessee Valley Authority"])
        self.assertEqual(C.nrc_names(f"Northern States Power Company {en} Minnesota"), [f"Northern States Power Company {en} Minnesota"])

    def test_nrc_parent_field(self):
        self.assertEqual(C.parse_parent("NextEra Energy, Inc. with principal subsidiaries Florida Power & Light Co. "
                                        "and NextEra Energy Resources, LLC"), ("NextEra Energy, Inc.", []))
        self.assertEqual(C.parse_parent("Northern States Power Company Minnesota doing business as Xcel Energy"),
                         ("Xcel Energy", []))
        self.assertEqual(C.parse_parent("DTE Electric Company (DTE)"), ("DTE Electric Company", ["DTE"]))
        self.assertEqual(C.parse_parent(""), ("", []))


class Resolve(unittest.TestCase):
    def run_it(self, ms, reviewed=(), pairs=()):
        out, rk, rp = C.resolve(ms, list(reviewed), list(pairs))
        return {(x["table"], x["row_id"], x["role"]): (x["cid"], x["rule"], x["confidence"]) for x in out}

    def test_an_eia_id_is_one_company_whatever_its_name(self):
        got = self.run_it([m("eia861_utility_data", "u1", "utility", "Georgia Power Co", "7140"),
                           m("eia860m_operating_generators", "g1", "operator", "Georgia Power Company", "7140")])
        self.assertEqual(got[("eia861_utility_data", "u1", "utility")], ("company:eia-7140", "eia_id", 1.0))
        self.assertEqual(got[("eia860m_operating_generators", "g1", "operator")][0], "company:eia-7140")

    def test_two_ids_are_never_merged_by_name(self):
        got = self.run_it([m("eia861_utility_data", "a", "utility", "City of Richmond", "15955"),
                           m("eia861_utility_data", "b", "utility", "City of Richmond", "40229"),
                           m("energy_deals", "d1", "buyer", "City of Richmond")])
        self.assertNotEqual(got[("eia861_utility_data", "a", "utility")][0], got[("eia861_utility_data", "b", "utility")][0])
        # a name without an id that two anchored companies share joins neither
        self.assertEqual(got[("energy_deals", "d1", "buyer")], ("company:city-of-richmond", "name", 0.85))

    def test_a_name_joins_the_one_anchored_company_of_that_name(self):
        got = self.run_it([m("eia860m_operating_generators", "g1", "operator", "Invenergy Services LLC", "49893"),
                           m("ercot_interconnection_queue", "q1", "interconnection_customer", "Invenergy Services, LLC")])
        self.assertEqual(got[("ercot_interconnection_queue", "q1", "interconnection_customer")],
                         ("company:eia-49893", "anchored_name", 0.9))

    def test_reviewed_alias_and_its_id(self):
        rev = [dict(alias="TVA", canonical="Tennessee Valley Authority", parent="", kind="utility",
                    eia_utility_id="18642", evidence="news:x")]
        got = self.run_it([m("eia861_utility_data", "u", "utility", "Tennessee Valley Authority", "18642"),
                           m("energy_deals", "d", "seller", "TVA")], rev)
        self.assertEqual(got[("energy_deals", "d", "seller")], ("company:eia-18642", "reviewed_alias", 0.95))

    def test_company_word(self):
        got = self.run_it([m("energy_deals", "d1", "seller", "Constellation"),
                           m("nrc_power_reactors", "r1", "parent", "Constellation Energy Corporation")])
        self.assertEqual(got[("energy_deals", "d1", "seller")], ("company:constellation", "name", 0.85))
        self.assertEqual(got[("nrc_power_reactors", "r1", "parent")], ("company:constellation", "company_word", 0.7))

    def test_company_word_never_joins_an_anchored_name(self):
        got = self.run_it([m("eia860m_operating_generators", "g", "operator", "Southern Power Co", "17650"),
                           m("energy_deals", "d", "seller", "Southern")])
        self.assertEqual(got[("energy_deals", "d", "seller")][0], "company:southern")

    def test_reviewed_file_needs_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["alias", "canonical", "parent", "kind", "eia_utility_id", "evidence", "note"])
                w.writerow(["X", "Y", "", "", "", "", ""])
            with self.assertRaises(ValueError):
                C.read_reviewed(p)

    def test_the_repository_file_reads_and_every_kind_is_known(self):
        rows = C.read_reviewed()
        self.assertGreater(len(rows), 50)
        for r in rows:
            self.assertIn(r["kind"] or "other", C.KINDS, r)
            self.assertTrue(r["evidence"].strip())


class Build(unittest.TestCase):
    def test_kinds_footprint_and_license(self):
        ms = [m("eia861_utility_data", "u", "utility", "Alpha Power Co", "1", extra="Investor Owned", date="2024-01-01"),
              m("eia860m_operating_generators", "g1", "operator", "Alpha Power Co", "1", mw="100", fuel="gas",
                extra="plant 9", date="1990-05-01", grid="PJM"),
              m("eia860m_operating_generators", "g2", "operator", "Alpha Power Co", "1", mw="50", fuel="solar",
                extra="plant 9", date="2020-01-01", grid="PJM"),
              m("energy_deals", "d", "buyer", "Beta Capital", mw="", usd="1000000", extra="debt", date="2026-01-02"),
              m("energy_deals", "d", "seller", "Alpha Power Co", mw="200", usd="1000000", extra="debt",
                date="2026-01-02")]
        ms, rk, rp = C.resolve(ms, [], [])
        comp, aliases, links = C.build(ms, rk, rp, [], {"eia861_utility_data": "public",
                                                        "eia860m_operating_generators": "public",
                                                        "energy_deals": "internal"})
        a = comp.set_index("entity_id").loc["company:eia-1"]
        self.assertEqual(a["kind"], "utility")
        self.assertEqual(a["n_plants"], 1)
        self.assertEqual(a["plants_mw"], 150.0)
        self.assertEqual(a["mw_gas"], 100.0)
        self.assertEqual(a["segment"], "gas")
        self.assertEqual(a["n_deals"], 1)
        self.assertEqual(a["license"], "mixed")
        self.assertEqual(a["first_seen"], "1990-05-01")
        self.assertEqual(a["grids"], "PJM")
        b = comp.set_index("entity_id").loc["company:beta-capital"]
        self.assertEqual(b["kind"], "lender or investor")
        self.assertEqual(b["license"], "internal")
        self.assertEqual(set(links["license"]), {"public", "internal"})
        self.assertEqual(len(links), 5)
        self.assertTrue(links["entity_id"].is_unique)
        self.assertTrue(aliases["entity_id"].is_unique)

    def test_name_priority(self):
        ms = [m("energy_deals", "d1", "seller", "AEP"), m("energy_deals", "d2", "seller", "AEP"),
              m("energy_deals", "d3", "buyer", "American Electric Power")]
        rev = [dict(alias="AEP", canonical="American Electric Power", parent="", kind="utility", eia_utility_id="",
                    evidence="news:x")]
        ms, rk, rp = C.resolve(ms, rev, [])
        self.assertEqual(C.name_for(ms, {"american electric power": "American Electric Power"}),
                         "American Electric Power")
        ms2 = [m("energy_deals", "d1", "seller", "Xcel"), m("energy_deals", "d2", "seller", "Xcel"),
               m("nrc_power_reactors", "r", "parent", "Xcel Energy")]
        for x in ms2:
            x["key"] = "xcel"
        self.assertEqual(C.name_for(ms2), "Xcel Energy")

    def test_licenses_read_license_status(self):
        with tempfile.TemporaryDirectory() as d:
            cov, st = os.path.join(d, "c.csv"), os.path.join(d, "s.csv")
            with open(cov, "w", encoding="utf-8", newline="") as f:
                f.write("table,license\na,public\nb,internal\nc,public\n")
            with open(st, "w", encoding="utf-8", newline="") as f:
                f.write("table,status,from,publishers,verdict,permission,permission_ref,note\n"
                        "c,license needed,2026-10-21,X,needs written permission,,,\n")
            self.assertEqual(C.licenses(["a", "b", "c"], cov, st), {"a": "public", "b": "internal", "c": "internal"})


if __name__ == "__main__":
    unittest.main()
