"""Session 355 (the chain of 20 October 2026, night): the battery's node band (ERCOT's storage nodes against the hub,
node_basis_summary) and, on /research, the statistics the data machine's session 361 wrote into each card: Newey-West
errors beside HC1, the round's multiple-comparisons line with the card's q-values, and a hunt draft's step-versus-trend
flag. Beside the figures, never one of them. Energy Research Warehouse (ERW)."""
import glob
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBatteryBand(unittest.TestCase):
    def test_the_band_is_read_weighted_and_added_to_nothing(self):
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertIn('export const STORAGE_VARS = ["spread_4h_p10", "spread_4h_p50", "spread_4h_p90", "hub_spread_4h", "share_wider_pct", "days"] as const;', src("site", "lib", "nodebasisread.ts"))
        self.assertEqual(page.count("rest<"), 0)   # the page's own reads stay read.ts's (tests 148 and 178)
        self.assertIn('asked.grid === "ercot" && g.entity === "ercot:HB_HUBAVG" && l12m.length === 12', page)
        self.assertIn("nodeMonths.reduce((a, r) => a + r[v] * r.days, 0) / nodeDays", page)   # weighted by the days held
        self.assertIn("Added to no figure (node_basis_summary).", page)
        self.assertIn("`series|node_basis_summary|ercot:HB_HUBAVG|dam_storage_${v}|${r.ts}`", page)


class TheCards(unittest.TestCase):
    def test_every_library_card_carries_what_the_page_reads(self):
        cards = [p for p in glob.glob(os.path.join(ROOT, "site", "data", "findings", "*.json")) if not p.endswith("catalogue.json")]
        self.assertTrue(cards)
        seen_nw = 0
        for p in cards:
            with open(p, encoding="utf-8") as f:
                st = json.load(f).get("statistics")
            if st is None:
                continue
            rd = st["round"]
            self.assertGreaterEqual(rd["claims_tested"], rd["claims_passing"], p)
            for r in (st.get("newey_west") or {}).get("rows", []):
                seen_nw += 1
                for k in ("label", "numbers_key", "se_hc1", "p_hc1", "se_nw", "p_nw", "nw_lag"):
                    self.assertIn(k, r, p)
        self.assertGreater(seen_nw, 0)

    def test_the_component(self):
        comp = src("site", "components", "analysis", "FindingCard.tsx")
        self.assertIn("{!render && card.statistics ? <Statistics st={card.statistics} /> : null}", comp)   # the PNG renderer's frame is unchanged
        self.assertIn('data-step-flag={String(sh.break_year)}', comp)
        self.assertIn("data-multiple-comparisons={rd.claims_tested}", comp)
        self.assertIn("data-newey-west={nw.length}", comp)
        self.assertIn("statistics?: CardStatistics;", src("site", "lib", "findings.ts"))

    def test_no_em_dash(self):
        for parts in (("site", "components", "analysis", "FindingCard.tsx"), ("site", "lib", "findings.ts"), ("site", "app", "cost-of-power", "battery", "page.tsx"), ("tests", "test_session355.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
