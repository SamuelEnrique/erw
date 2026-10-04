"""Session 102: the landing of sessions 91 to 101.

What this session added of its own: a table loaded for a page in review is in Supabase and in no count a visitor
sees (live_set.yaml review_hold, the loader's flag, the site's catalogue reader); the battery page's sentence under
the ERCOT chart no longer says what the warehouse does not measure; the durations of SPP and New York carry the
operators' own rules where session 100 found them. No network, no table read.
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ReviewHold(unittest.TestCase):
    def test_a_review_table_is_loaded_and_flagged(self):
        import load
        live = {"storage_owners_monthly", "energy_deals"}
        self.assertEqual(load.live_flag("storage_owners_monthly", live, review={"storage_owners_monthly"}), "review")
        self.assertEqual(load.live_flag("energy_deals", live, review={"storage_owners_monthly"}), "yes")
        self.assertEqual(load.live_flag("not_loaded", live, review={"not_loaded"}), "no")   # held and not loaded says "no"

    def test_every_review_table_has_a_rule_and_is_not_also_held_out(self):
        import load
        review = load.LIVE["review_hold"]
        held = set(load.LIVE["catalogue_hold"])
        self.assertEqual(sorted(review), sorted(set(review)))
        for t in review:
            self.assertIsNotNone(load.live_rule(t), t)       # loaded: a live-set rule matches it
            self.assertNotIn(t, held, t)                     # and the catalogue hold would keep it out of Supabase
        for t in ("caiso_curtailment_intervals", "spp_as_quantities"):   # in coverage and Redivis only
            self.assertIn(t, held)
            self.assertNotIn(t, review)

    def test_the_ercot_tables_of_session_92_have_rules(self):
        import load
        for t in ("ercot_all_hub_prices_history", "ercot_as_prices", "lbnl_interconnection_queue",
                  "merchant_revenue_monthly", "storage_owners_monthly"):
            self.assertEqual(load.live_rule(t), ("full", None), t)
        # the yearly ERCOT history tables stay out of the recent rule (session 19), and the internal EQR tables are not loaded
        for t in ("ferc_eqr_buyer_names", "ferc_eqr_buyer_doubtful", "ferc_eqr_party_totals"):
            self.assertIsNone(load.live_rule(t), t)

    def test_the_site_leaves_review_tables_out_of_every_count(self):
        data = src("site", "lib", "data.ts")
        self.assertIn('rows.filter((r) => r.license === "public" && r.in_live_set !== "review")', data)
        tools = src("site", "lib", "chat", "tools.ts")
        self.assertIn('c.in_live_set !== "yes" && c.in_live_set !== "review"', tools)   # Ask, in review itself, reads them
        home = src("site", "app", "page.tsx")
        self.assertIn("required(catalogue)", home)           # the home page's counts come through that reader


class Coverage(unittest.TestCase):
    def test_every_new_table_has_a_sector(self):
        import importlib.util   # by path: warehouse/validate holds a script of the same name that runs the builder
        spec = importlib.util.spec_from_file_location("erw_build_coverage", os.path.join(ROOT, "warehouse", "metadata", "build_coverage.py"))
        bc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bc)
        for t in ("generation_mix_hourly_profile", "generation_mix_records", "interconnection_queue_summary",
                  "hub_price_comparison", "eia930_demand_growth", "caiso_curtailment_intervals", "caiso_curtailment_profile",
                  "ferc_eqr_buyer_names", "ferc_eqr_buyer_doubtful", "ferc_eqr_party_totals", "spp_as_quantities"):
            self.assertTrue(bc.sector_of(t), t)

    def test_a_derived_from_line_names_tables_only(self):
        # build_coverage.py reads the line as table names; a note inside it failed the build in session 102
        for f in ("queue_summary.py", "eqr_buyers.py"):
            line = [l for l in src("warehouse", "derived", f).splitlines() if 'f"Derived from: ' in l]
            self.assertEqual(len(line), 1, f)
            self.assertRegex(line[0], r'f"Derived from: \{INPUT\}",')


class BatteryPage(unittest.TestCase):
    def test_the_sentence_under_the_ercot_chart(self):
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertIn("This is an upper bound: before 2024 it is mostly payment for holding reserves, to a battery longer "
                      "than any Texas then had, and 2021 is one week of February. Recent years are the ones to read.", page)
        self.assertNotIn("show more than real batteries earned", page)
        self.assertNotIn("show more than real batteries earned", src("site", "scripts", "test-battery-stack.mjs"))

    def test_the_durations_carry_the_operators_rules(self):
        import battery_stack as bs
        self.assertFalse(hasattr(bs, "SPP_ASSUMED"))
        notes = {(iso, p["key"]): p["hours"] for iso, m in bs.REVIEW_MARKETS.items() for p in m["products"]}
        for k in ("regup", "regdn", "spin", "supp"):
            (_, h, s), = notes[("spp", k)]
            self.assertEqual(h, 1.0)
            self.assertIn("Revision 119", s)
            self.assertIn("section 4.2.2", s)
        (_, h, s), = notes[("nyiso", "spin")]
        self.assertEqual(h, 1.0)
        self.assertIn("section 4.4.2.1", s)
        (_, h, s), = notes[("nyiso", "reg")]
        self.assertEqual(h, 1.0)
        self.assertTrue(s.startswith("assumed: one hour"))
        self.assertIn("15.3.2.1(e)", s)
        lib = src("site", "lib", "batterystack.ts")
        self.assertRegex(lib, r'spp: \[\s*\{ product: "Regulation Up, Regulation Down, Spinning Reserve, Supplemental Reserve", rule: "60 minutes", source: "SPP Integrated Marketplace Protocols, Revision 119, section 4\.2\.2", assumed: false \}')
        self.assertIn('{ product: "Regulation Capacity", rule: "1 hour", source: "the tariff states no time', lib)

    def test_spp_and_new_york_stay_closed(self):
        lib = src("site", "lib", "batterystack.ts")
        for g in ("nyiso", "spp"):
            m = re.search(r'\{[^{}]*id: "%s"[^{}]*\}' % g, lib)
            self.assertIsNotNone(m, g)
            self.assertIn("review: true", m.group(0), g)
            self.assertNotRegex(m.group(0), r"ready: true", g)


if __name__ == "__main__":
    unittest.main()
