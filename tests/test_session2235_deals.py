"""Session 2235 (chain 156): the deal tracker's figures cross-checked against the headlines (warehouse/deals/crosscheck.py).

Each case is a stored headline (news_stories) with the record the extraction made of it, or a record of the audit's
classes. A flag is written, never a figure changed or dropped. No model, no network.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(ROOT, "warehouse", "deals"), os.path.join(ROOT, "warehouse", "deals", "eval")):
    if p not in sys.path:
        sys.path.insert(0, p)

import crosscheck as xc  # noqa: E402
import fixture  # noqa: E402


class Headlines(unittest.TestCase):
    def test_what_a_headline_states(self):
        s = xc.stated("AEP signs 960-MW Indiana nuclear pact with Amazon, X-energy")
        self.assertEqual(s["mw"], [960.0])
        s = xc.stated("Zelestra and EDP expand solar-plus-storage PPA partnership with another 462MWh of batteries in Spain")
        self.assertEqual(s["mwh"], [462.0])
        self.assertEqual(s["mw"], [])
        self.assertEqual(xc.stated("Liberty Inks 1.2-GW 'Critical Milestone' Deal")["mw"], [1200.0])
        self.assertEqual(xc.stated("BKV Takes Big Step Toward Hyperscaler PPA with $800MM Texas Power Deal")["usd"], [8e8])

    def test_a_valuation_or_a_company_wide_sum_is_not_the_deals(self):
        self.assertEqual(xc.stated("Nvidia, Dell Back AI Cloud Startup Volta at $2.4 Billion Value")["usd"], [])
        self.assertEqual(xc.stated("Devon, Coterra will merge to create $58 billion US shale giant")["usd"], [])
        self.assertEqual(xc.stated("Google to invest $15 billion in AI infrastructure and buy nuclear power in Finland")["usd"], [])
        self.assertEqual(xc.stated("Switch in talks to raise funds at $50 billion-plus valuation")["usd"], [])
        self.assertEqual(xc.stated("Devon Energy to Buy Coterra for $21.5 Billion to Create Shale Giant")["usd"], [21.5e9])


class Flags(unittest.TestCase):
    def test_a_headline_figure_the_record_lacks(self):
        f = xc.flags({"mw": ""}, ["AEP signs 960-MW Indiana nuclear pact with Amazon, X-energy"])
        self.assertEqual(f, ["headline: 960 MW; record: none"])

    def test_a_headline_figure_the_record_contradicts(self):
        f = xc.flags({"mw": "2100"}, ["TotalEnergies, KKR Add 700 MW to US Solar JV"])
        self.assertEqual(f, ["headline: 700 MW; record: 2100 MW"])

    def test_the_record_equal_to_one_headline_of_two_is_not_flagged(self):
        f = xc.flags({"dollars": "21500000000"}, ["Devon Energy to Buy Coterra for $21.5 Billion",
                                                  "Devon Agrees to Buy US Shale Rival Coterra for $21.4 Billion"])
        self.assertEqual(f, [])   # 21.4 and 21.5 are within the 2 percent of rounding

    def test_mw_and_mwh_never_confused(self):
        f = xc.flags({"mw": "462"}, ["Zelestra and EDP expand solar-plus-storage PPA partnership with another 462MWh of batteries"])
        self.assertIn("mw 462 is a figure the headline states in MWh", f)

    def test_usd_and_usd_per_mwh_never_confused(self):
        self.assertIn("usd_per_mwh 4200000000 is above the bound of 1000: a sum, not a price?",
                      xc.flags({"usd_per_mwh": "4200000000"}, []))
        f = xc.flags({"usd": "68"}, ["Utility signs solar PPA"], "at $68 per MWh for 20 years")
        self.assertIn("usd 68 is under 1,000 where the words state a price per MWh: a price, not a sum?", f)

    def test_a_term_in_months_is_flagged_not_converted(self):
        f = xc.flags({"term_years": ""}, ["Shell signs 18-month LNG supply contract with Uniper"])
        self.assertIn("term stated in months (18-month): term_years left empty", f)

    def test_a_figure_above_a_bound_is_flagged_not_dropped(self):
        f = xc.flags({"mw": "50000"}, ["Utility signs 50 GW PPA"])
        self.assertIn("mw 50000 above the bound 20000", f)
        self.assertEqual(xc.flags({"mwh": "3300000"}, ["TotalEnergies signs 3.3TWh power contract with Airbus"]), [])


class OnTheFixture(unittest.TestCase):
    def test_the_extractor_writes_the_flags(self):
        rows, log = fixture.replay("2232")
        self.assertIn("cross-check:", log)
        self.assertIn("flags", rows.columns)
        # every figure the replayed rows hold agrees with its headlines, save where a headline states two
        bad = rows[rows["flags"].str.contains("record: ") & ~rows["flags"].str.contains("record: none")]
        self.assertEqual(len(bad), 0, bad[["buyer", "seller", "flags"]].to_dict("records"))


if __name__ == "__main__":
    unittest.main()
