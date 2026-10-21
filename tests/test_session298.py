"""Session 298: the generator and datacenter pages, the section 9 rulings of 18 October 2026 (the chain prompt of 19
October). What is held to:

  1a: the CAISO peaker's run rule counts the carbon cost of the fuel: the merchant library's rule, the snapshot's
    series for CAISO (hourly, USD per MMBtu, the latest current auction's settlement price times 53.06 kg per MMBtu)
    and none for ERCOT, the builder's own reader of the allowance table, the page's words with the source, and no
    settlement price in the page's downloads (the table is internal);
  4d: check-seller-deeper.mjs is retired with the other two; 5a: the PPA term's default is the asset's life;
  6a: Potomac's 2024 net revenue is a cross-check row with its page and figure, and the page counts 21;
  7a: solar's degradation default is the ATB's 0.7 percent, with its source, and the note and the page state what moved;
  datacenter 5c: the line under the headline for a load that runs in under a tenth of the hours; 8a: the shared
    field's own clamp words; the fold and the tip carried to the other two pages;
  no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = [
    "site/lib/merchant.ts", "site/lib/seller/finance.ts", "site/app/cost-of-power/seller/model.ts", "site/app/cost-of-power/seller/page.tsx",
    "site/app/cost-of-power/seller/SellerScenarios.tsx", "site/app/cost-of-power/LoadScenarios.tsx", "site/app/cost-of-power/page.tsx",
    "site/components/decisions/ScenarioBlock.tsx", "site/components/tool/ToolPage.tsx", "warehouse/derived/merchant_revenue.py",
    "site/scripts/_retired/README.md", "docs/methods/generator_earns_algorithm.md", "docs/methods/datacenter_pays_algorithm.md",
    "docs/reviews/packs/generator.md", "tests/test_session298.py",
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCarbonCost(unittest.TestCase):
    def test_the_rule_the_series_and_the_factor(self):
        lib = src("site", "lib", "merchant.ts")
        self.assertIn("export const CO2_PER_MMBTU = 0.05306;", lib)
        self.assertIn("const c = (g + (s.co2?.[i] ?? 0)) * hr + vom;", lib)
        self.assertIn('if (k === "peaker" && (x.hr !== HEAT_RATE || x.vom !== VOM || s.co2)) {', lib)
        self.assertIn("co2?: (number | null)[]; co2_source?: string;", lib)

    def test_the_snapshot_carries_caiso_series_and_no_other(self):
        with open(os.path.join(ROOT, "site", "data", "merchant_snapshot.json"), encoding="utf-8") as f:
            snap = json.load(f)
        caiso, ercot = snap["isos"]["caiso"], snap["isos"]["ercot"]
        self.assertIn("co2", caiso)
        self.assertNotIn("co2", ercot)
        self.assertEqual(len(caiso["co2"]), len(caiso["price"]))
        held = [v for v in caiso["co2"] if v is not None]
        self.assertEqual(len(held), len(caiso["co2"]))                       # every hour held is after the first auction
        self.assertTrue(all(1.0 < v < 3.0 for v in held), (min(held), max(held)))   # USD per MMBtu: 20 to 55 per tonne times 0.05306
        self.assertIn("53.06 kg CO2 per MMBtu", caiso["co2_source"])
        self.assertIn("carb_auction_allowance_prices", caiso["co2_source"])
        # the table on the machine (the code machine holds a copy): the series is its latest current-auction price times the factor
        table = os.path.join(ROOT, "warehouse", "output", "carb_auction_allowance_prices.csv")
        if not os.path.exists(table):
            self.skipTest("the allowance table is not on this machine")
        prices = []
        for line in open(table, encoding="utf-8"):
            if line.startswith("carb:current_auction,settlement_price,"):
                parts = line.split(",")
                prices.append((parts[2][:10], float(parts[3])))
        latest = max(prices)[1]
        self.assertAlmostEqual(caiso["co2"][-1], round(latest * 0.05306, 4), places=4)

    def test_the_builder_reads_the_table_and_the_page_says_so(self):
        py = src("warehouse", "derived", "merchant_revenue.py")
        for words in ("CO2_PER_MMBTU = 0.05306", 'CO2_GRIDS = {"caiso"}', "def allowance(log):", 'carb:current_auction', 'cost = (x["hh"] + x["co2"].fillna(0)) * HEAT_RATE + VOM', 's["co2_source"] = CO2_SOURCE'):
            self.assertIn(words, py, words)
        model = src("site", "app", "cost-of-power", "seller", "model.ts")
        self.assertIn("const co2Last = (snap.isos[iso]?.co2 ?? [])", model)
        self.assertIn("the settlement prices are held internal and are in no download", model)
        for route in ("months.csv", "tables.csv"):
            self.assertNotIn("co2", src("site", "app", "cost-of-power", "seller", route, "route.ts"))


class TheOtherRulings(unittest.TestCase):
    def test_4d_the_script_is_retired(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "site", "scripts", "check-seller-deeper.mjs")))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "scripts", "_retired", "check-seller-deeper.mjs")))
        self.assertIn("| `check-seller-deeper.mjs` | session 162 | session 298, 19 October 2026", src("site", "scripts", "_retired", "README.md"))

    def test_5a_the_ppa_term_is_the_life(self):
        self.assertIn("ppa: costs.life, itc: 0, ptc: 0 };", src("site", "lib", "seller", "finance.ts"))   # session 353: the tax credits after the PPA term

    def test_6a_potomac_is_a_cross_check_row_and_the_page_counts_21(self):
        note = src("docs", "methods", "generator_earns_algorithm.md")
        self.assertIn("| ERCOT gas peaker, 2024: a margin over fuel of USD 34.01 per MWh run", note)
        self.assertIn("[Potomac Economics, 2024 State of the Market Report for the ERCOT Electricity Markets, June 2025, page 80, \"1. Interpreting Single-Year Net Revenues\" and Figure 56](https://www.potomaceconomics.com/wp-content/uploads/2025/06/2024-State-of-the-Market-Report.pdf)", note)
        self.assertIn("averaged only $68 per MWh", note)
        page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        self.assertIn('<span data-checked-against="34">Checked against: 34 published figures', page)   # session 463: 21 until then
        self.assertIn("Potomac Economics", page)

    def test_7a_solar_takes_the_atbs_rate_and_the_page_states_what_moved(self):
        fin = src("site", "lib", "seller", "finance.ts")
        self.assertIn("export const SOLAR_DEG = 0.7;", fin)
        self.assertIn("NREL, Annual Technology Baseline 2025, utility-scale PV: a degradation rate of 0.7 percent a year", fin)
        model = src("site", "app", "cost-of-power", "seller", "model.ts")
        self.assertIn('asked.asset === "solar" ? { deg: SOLAR_DEG, degSource: SOLAR_DEG_SOURCE } : {}', model)
        page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        self.assertIn('<span data-decisions="298">', page)
        self.assertIn("USD -74.16 million to -76.66 million", page)
        note = src("docs", "methods", "generator_earns_algorithm.md")
        self.assertIn("| Degradation, solar: 0.7 percent a year (session 298; none until then) | 0.7 percent a year |", note)
        self.assertIn("NPV from USD -74.16 million to -76.66 million", note)


class TheDatacenterRulings(unittest.TestCase):
    def test_5c_the_line_under_the_headline(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn("(s12.held - s12.down) / s12.held < 0.1", page)
        self.assertIn("data-runs-little=", page)
        self.assertIn("fewer than one in ten", page)
        self.assertIn("**5c:**", src("docs", "methods", "datacenter_pays_algorithm.md"))

    def test_8a_the_shared_field_says_a_clamped_value_itself(self):
        block = src("site", "components", "decisions", "ScenarioBlock.tsx")
        self.assertIn("const words = f.clamp ?? ((t: number, u: number) =>", block)
        self.assertIn("was typed: the field runs from", block)

    def test_the_fold_and_the_tip_are_carried(self):
        block = src("site", "components", "decisions", "ScenarioBlock.tsx")
        self.assertIn("fold?: { id: string; title: string; summary: (a: Values, view: View) => ReactNode };", block)
        self.assertIn('import { SettingsFold } from "@/components/tool/ToolPage";', block)
        self.assertIn('fold={{ id: "financing", title: "Financing"', src("site", "app", "cost-of-power", "seller", "SellerScenarios.tsx"))
        self.assertIn('fold={{ id: "assumptions", title: "Assumptions"', src("site", "app", "cost-of-power", "LoadScenarios.tsx"))
        tp = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn("tip?: ReactNode; children: ReactNode }) {", tp)
        page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        self.assertEqual(page.count("<Tip id="), 2)
        self.assertNotIn("note={<>Per kW of nameplate, priced at {at}. {atHub", page)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
