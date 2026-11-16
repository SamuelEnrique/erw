"""Session 7001 (chain 301): the company database's data faults, rows 17 to 23 of docs/reviews/companies-faults-2026-11-11.md.

Energy Research Warehouse (ERW). On names and rows written here (test fixtures, not the warehouse's rows): EIA-861's state
tag dropped by the normalization (row 17), "Conn" read as Connecticut (row 17), the reviewed aliases of Callaway,
Millstone, NextEra's holding company and EDP (rows 17 and 18), the split of an EIA number that carries a power marketer
and another firm's plants (row 19), the kind and segment of the public rows alone on the pages (row 20), EIA-861's RTO
flags read as a grid only inside the RTO's footprint (row 21), the power marketer kind and the capital view's buyer
count (row 22), and owned_mw in the index (row 23). No network, no data lock.

    python -m unittest tests.test_session7001_companies -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import capital_page as K  # noqa: E402
import companies as C  # noqa: E402
import companies_page as P  # noqa: E402


def m(table, row, role, raw, anchor="", **kw):
    return C.mention(table, row, role, raw, anchor, **kw)


def resolve(ms, reviewed=()):
    out, _, _ = C.resolve(ms, list(reviewed), [])
    return {(x["table"], x["row_id"], x["role"]): (x["cid"], x["rule"]) for x in out}


class Row17Names(unittest.TestCase):
    def test_the_state_tag_is_dropped(self):
        self.assertEqual(C.norm("Union Electric Co - (MO)"), "union electric")
        self.assertEqual(C.norm("Union Electric Co - (MO)"), C.norm("Union Electric Co."))
        self.assertEqual(C.norm("Duke Energy Progress - (NC)"), C.norm("Duke Energy Progress, LLC"))
        self.assertEqual(C.norm("City of Aberdeen - (MS)"), "city of aberdeen")

    def test_conn_is_connecticut(self):
        self.assertEqual(C.norm("Dominion Energy Nuclear Conn Inc"), C.norm("Dominion Energy Nuclear Connecticut, Inc."))

    def test_the_nrc_licensee_joins_eia_s_company(self):
        got = resolve([m("eia861_utility_data", "u", "utility", "Duke Energy Progress - (NC)", "3046"),
                       m("nrc_power_reactors", "r", "licensee", "Duke Energy Progress, LLC")])
        self.assertEqual(got[("nrc_power_reactors", "r", "licensee")], ("company:eia-3046", "anchored_name"))

    def test_the_repository_aliases(self):
        rev = C.read_reviewed()
        by = {r["alias"]: r for r in rev}
        for a in ("Ameren UE", "AmerenUE", "Union Electric Co."):
            self.assertEqual(by[a]["eia_utility_id"], "19436")
        self.assertEqual(by["Dominion Energy Nuclear Connecticut, Inc."]["eia_utility_id"], "5221")
        self.assertEqual(by["EDP Renewables North America LLC"]["eia_utility_id"], "61785")
        self.assertEqual(C.norm(by["NextEra Energy Resources Interconnection Holding, LLC"]["canonical"]),
                         "nextera energy resources interconnection holdings")
        got = resolve([m("eia860m_operating_generators", "g", "operator", "Union Electric Co - (MO)", "19436"),
                       m("nrc_power_reactors", "r", "operator", "Ameren UE"),
                       m("nrc_power_reactors", "r", "parent", "AmerenUE")], rev)
        self.assertEqual(got[("nrc_power_reactors", "r", "operator")][0], "company:eia-19436")
        self.assertEqual(got[("nrc_power_reactors", "r", "parent")][0], "company:eia-19436")


class Row19Split(unittest.TestCase):
    def test_a_marketer_and_another_firm_s_plant_are_two_companies(self):
        ms = [m("eia861_utility_data", "u", "utility", "PBF Power Marketing LLC", "56982", extra="Retail Power Marketer"),
              m("eia860m_operating_generators", "g", "operator", "Kern Community College District", "56982")]
        self.assertEqual(C.split_anchors(ms), {"56982"})
        got = resolve(ms)
        self.assertEqual(got[("eia861_utility_data", "u", "utility")][0], "company:eia-56982")
        self.assertEqual(got[("eia860m_operating_generators", "g", "operator")][0], "company:eia-56982-860")

    def test_a_rename_that_shares_a_word_stays_one(self):
        ms = [m("eia861_utility_data", "u", "utility", "Calpine Energy Solutions", "1", extra="Retail Power Marketer"),
              m("eia860m_operating_generators", "g", "operator", "Calpine Corp", "1")]
        self.assertEqual(C.split_anchors(ms), set())

    def test_a_utility_is_never_split(self):
        ms = [m("eia861_utility_data", "u", "utility", "Georgia Power Co", "7140", extra="Investor Owned"),
              m("eia860m_operating_generators", "g", "operator", "Plant Vogtle Partners", "7140")]
        self.assertEqual(C.split_anchors(ms), set())

    def test_the_split_company_keeps_its_eia_number(self):
        ms = [m("eia861_utility_data", "u", "utility", "DRW Energy Trading", "67114", extra="Wholesale Power Marketer"),
              m("eia860m_operating_generators", "g", "operator", "Santa Teresa Solar", "67114", mw="150", fuel="solar")]
        out, rk, rp = C.resolve(ms, [], [])
        comp, _, _ = C.build(out, rk, rp, [], {"eia861_utility_data": "public", "eia860m_operating_generators": "public"})
        by = dict(zip(comp["entity_id"], comp.to_dict("records")))
        self.assertEqual(by["company:eia-67114-860"]["name"], "Santa Teresa Solar")
        self.assertEqual(by["company:eia-67114-860"]["eia_utility_id"], "67114")
        self.assertEqual(by["company:eia-67114"]["name"], "DRW Energy Trading")
        self.assertEqual(by["company:eia-67114"]["kind"], "power marketer")


class Row21Grids(unittest.TestCase):
    def row(self, state, **flags):
        base = {c: "" for c in C.RTO_COLS}
        base.update(flags)
        return dict(entity_id="eia861:x", name="X", x_utility_number="9", x_year="2025", x_state=state,
                    x_ownership="Investor Owned", **base)

    def test_a_flag_outside_the_footprint_is_not_a_grid(self):
        d = pd.DataFrame([self.row("FL", x_rto_pjm="Y", x_rto_miso="Y"), self.row("AZ", x_rto_ercot="Y"),
                          self.row("MO", x_rto_miso="Y"), self.row("TX", x_rto_ercot="Y", x_rto_spp="Y")])
        self.assertEqual([x["grid"] for x in C.m_861(d)], ["", "", "MISO", "ERCOT;SPP"])


class Row20PublicKind(unittest.TestCase):
    def test_a_held_row_does_not_set_the_kind(self):
        pub = [dict(input_table="eia860m_operating_generators", role="operator", name_as_written="Acme Power",
                    detail="plant 1", mw="6", fuel="solar", input_row="g1")]
        kind, basis, seg, seg_basis = P.public_kind({"name": "Acme Power"}, pub, [], {})
        self.assertEqual((kind, basis), ("other", "no rule"))
        self.assertEqual((seg, seg_basis), ("solar", "most MW"))

    def test_the_reviewed_kind_holds(self):
        kind, basis, _, _ = P.public_kind({"name": "Google"}, [], [], {"google": "lab or hyperscaler"})
        self.assertEqual((kind, basis), ("lab or hyperscaler", "reviewed_aliases.csv"))


class Row22And23(unittest.TestCase):
    def test_power_marketer_is_a_kind(self):
        self.assertIn("power marketer", C.KIND_ORDER)
        self.assertLess(C.KIND_ORDER.index("power marketer"), C.KIND_ORDER.index("other"))
        k, b = C.kind_for([m("eia861_utility_data", "u", "utility", "X", "1", extra="Retail Power Marketer")], "x", {})
        self.assertEqual((k, b), ("power marketer", "EIA-861 ownership Retail Power Marketer"))

    def test_the_capital_view_counts_buyers_a_kind(self):
        deals = pd.DataFrame([dict(event_id="d1", event_date="2026-01-01", deal_type="debt", buyer="A", seller="",
                                   asset="", technology="", dollars="1", mw="", story_urls=""),
                              dict(event_id="d2", event_date="2026-01-02", deal_type="debt", buyer="B", seller="",
                                   asset="", technology="", dollars="2", mw="", story_urls=""),
                              dict(event_id="d3", event_date="2026-01-03", deal_type="debt", buyer="A", seller="",
                                   asset="", technology="", dollars="3", mw="", story_urls="")])
        links = pd.DataFrame([dict(input_table="energy_deals", role="buyer", input_row=e, company_id=c)
                              for e, c in (("d1", "company:a"), ("d2", "company:b"), ("d3", "company:a"))])
        directory = pd.DataFrame([dict(entity_id="company:a", kind="lender or investor"),
                                  dict(entity_id="company:b", kind="lender or investor")])
        k = {x["kind"]: x for x in K.compute(deals, links, directory)["kinds"]}
        self.assertEqual(k["lender or investor"]["rows"], 3)
        self.assertEqual(k["lender or investor"]["buyers"], 2)

    def test_owned_mw_is_an_index_column(self):
        self.assertIn("owned_mw", P.INDEX_COLS)


if __name__ == "__main__":
    unittest.main()
