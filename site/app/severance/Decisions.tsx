import { SiteLink as Link } from "@/components/SiteLink";
import { Tip } from "@/components/tool/ToolPage";

// Session 7502 (chain 304): the severance tool's decisions, in the form the battery page, /deals and /impact carry: one
// fold, closed to start, one line a choice that moves a figure of the calculator or the lease tool, each with its
// default and its source on hover, tap or focus (the page standard: no grey note under the line). The list is kept
// here, in the tool's own folder, and exported so tests/test_session7502_severance.py and the method note
// (docs/methods/severance.md, "The choices that move a figure") can be checked against it. Words only: nothing on the
// page is computed from this list, and it draws no request (the page's promise that nothing typed or loaded is sent).
// Every choice the calculator makes is already changed in place, in the box or the list the line names.
export type SeveranceDecision = { key: string; text: string; def: string; source: string };

export const SEVERANCE_DECISIONS: SeveranceDecision[] = [
  { key: "hub-price",
    text: "The price a month opens on is a hub price, not the value at the well, which is what the states tax. Type the lease's own price in the price box, or in the price columns of a lease file.",
    def: "The mean of EIA's daily spot price over the latest complete calendar month: WTI Cushing for oil and condensate, Henry Hub for gas. In a lease file, a blank price is the mean of the production month.",
    source: "EIA daily spot prices, the table eia_fuel_spot_prices (series RWTC and RNGWHHD), offered as a CSV under both tabs." },
  { key: "mcf-mmbtu",
    text: "Gas is priced per Mcf with Henry Hub's price per MMBtu, as if one Mcf held one MMBtu. A richer or leaner gas is worth more or less: type its price per Mcf.",
    def: "1 Mcf counted as 1 MMBtu.",
    source: "A choice of session 40, stated in the method note; no statute sets it." },
  { key: "tx-oil-floor",
    text: "Texas oil owes 4.6 percent of market value or 4.6 cents a barrel, whichever is greater. Texas condensate owes 4.6 percent with no floor per barrel.",
    def: "The greater of the two for oil; the percentage alone for condensate.",
    source: "Texas Tax Code Sec. 202.052(a) for oil; Sec. 201.055(b) and the Comptroller's Natural Gas Production Tax page for condensate, which states no amount per barrel." },
  { key: "one-reduced-rate",
    text: "One reduced rate or exemption applies to a well and month, and it replaces the first tax of the state's list (New Mexico's other three taxes stay). Texas's low-producing oil lease credit is the one rule that stacks: it is taken after the reduced rate.",
    def: "None ticked: the tax at the base rate.",
    source: "The Comptroller's Natural Gas Production Tax page (one incentive per well per report period) and its Low-Producing Oil Leases page (the credit combines with Types 05 and 14)." },
  { key: "certified-price",
    text: "A Texas low-producing credit is 0, 25, 50 or 100 percent by the Comptroller's certified price of the report period, which is in 2005 dollars, never by the price typed. Choose the report period under the rule.",
    def: "The latest report period the rules file holds, August 2026: gas USD 1.36 per Mcf (100 percent credit), oil USD 53.55 per barrel (no credit). In a lease file, the production month's; a month not held earns no credit.",
    source: "Texas Comptroller, the certified average taxable prices on its low-producing wells and leases pages, read 30 September 2026; Tax Code Secs. 201.059(b) and 202.058(c)." },
  { key: "high-cost-gas",
    text: "Texas high-cost gas is taxed at 7.5 percent less 7.5 percent times half the well's cost ratio, never below zero. The limit of 50 percent of drilling and completion costs in savings is not tracked. Type the ratio under the rule, or in a lease file's hcg_cost_ratio.",
    def: "A cost ratio of 1.0, the median well: 3.75 percent.",
    source: "Texas Tax Code Sec. 201.057(c); the Comptroller's Natural Gas Production Tax page (Type 5)." },
  { key: "la-completion",
    text: "Louisiana oil is taxed at 12.5 percent from a well completed before July 1, 2025 and at 6.5 percent from one completed on or after. Choose the completion in the list, or give completion_date in a lease file.",
    def: "Completed before July 1, 2025: 12.5 percent. A lease file with no date takes the same.",
    source: "La. R.S. 47:633, as amended through Acts 2025, No. 373." },
  { key: "la-gas-rate",
    text: "Louisiana gas is taxed by volume, not value, at the rate the Department of Revenue sets each July 1, and its horizontal well exemption follows the price the department publishes for the fiscal year.",
    def: "15.14 cents per Mcf for July 1, 2026 to June 30, 2027; horizontal wells 80 percent exempt for oil and 100 percent for gas in fiscal year 2027.",
    source: "Louisiana Department of Revenue, RIB No. 26-013 (June 2, 2026) and RIB No. 26-014 (August 3, 2026)." },
  { key: "deductions",
    text: "A deduction is computed only where the state's rule states it: Louisiana's trucking, barging and pipeline fees on oil and condensate, and New Mexico's royalties to the United States, the state or a tribe and its trucking. Texas's marketing costs for gas are not computed. Type each in its box.",
    def: "No deduction: every box opens on 0.",
    source: "La. R.S. 47:633; New Mexico Taxation and Revenue Department, Oil and Gas Production Taxes." },
  { key: "nm-district",
    text: "New Mexico's ad valorem production tax is the rate of the production unit's county, district and suffix. With no district chosen it is left out, and the total is the other three taxes. Choose the district in the list.",
    def: "Not chosen: ad valorem left out (the 35 rows of the table run from 0.7105 to 1.7249 percent).",
    source: "New Mexico Taxation and Revenue Department, the rate table effective April 1 to August 31, 2026, its latest when read on 30 September 2026." },
  { key: "no-rounding",
    text: "Each tax is computed to the fraction of a cent and the total is rounded once for display. New Mexico's return rounds each of its four taxes to the cent on its own, so a return can differ from the total here by a cent or two.",
    def: "No rounding of a single tax.",
    source: "New Mexico Taxation and Revenue Department, OGT Return Tax Due Calculation Method (Rev. 1, 2017)." },
  { key: "fees-apart",
    text: "Texas's two regulatory fees (USD 0.00625 a barrel of oil, USD 0.000667 per Mcf of gas) are shown on their own line and are in neither the tax nor the savings.",
    def: "Shown apart.",
    source: "Texas Comptroller, Crude Oil Production Tax and Natural Gas Production Tax pages." },
  { key: "may-qualify",
    text: "In the lease tool a rule is flagged when the file's own numbers meet its thresholds, and a well's potential savings take, for each month and product, the one flagged rule that saves the most. The state still certifies or designates the well. Tick or untick each rule under the well.",
    def: "Nothing ticked unless the file's exemptions column claims it.",
    source: "The thresholds of each rule as its cited page states them; the tests on the file's numbers are in the method note." },
  { key: "gas-three-months",
    text: "A Texas gas well is tested as low-producing on the three months before the month, at 90 Mcf a day or less, when it produced gas in each of them; otherwise on the month itself, so a new well's first short month does not count.",
    def: "The three months before, when the file holds gas in each.",
    source: "The Comptroller's Low-Producing Gas Wells page for the 90 Mcf a day over three months; the rule for a new well is a choice of session 57." },
];

export function SeveranceDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7502">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={SEVERANCE_DECISIONS.length}>
        {SEVERANCE_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-7502-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
      <p className="mt-2 max-w-3xl text-sm">
        Each is described in <Link href="/data/methods/severance" prefetch={false}>the method note</Link>, with the arithmetic of every figure.
      </p>
    </details>
  );
}
