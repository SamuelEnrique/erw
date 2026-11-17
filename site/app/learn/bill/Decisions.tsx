import { SiteLink as Link } from "@/components/SiteLink";
import { Tip } from "@/components/tool/ToolPage";

// Session 7533 (chain 304): the decisions of "What is on an electricity bill", in the form the battery pages, /severance
// and /contracts carry: one fold, closed to start, one line a choice that moves a figure of the page, each with its
// default and its source on hover, tap or focus (the page standard: no grey note under the line). The list is kept here,
// in the tool's own folder, and exported so site/scripts/test-bill-render.mjs, tests/test_session7533_bill.py and the
// method note (docs/methods/bill.md, "The choices that move a figure") can be checked against it. Words only: nothing on
// the page is computed from this list. Every choice a reader can change is changed in place, in the calculator's field
// the line names; the others are said to be fixed.
export type BillDecision = { key: string; text: string; def: string; source: string };

export const BILL_DECISIONS: BillDecision[] = [
  { key: "kwh",
    text: "How much electricity the home uses in the month. Every line charged per kWh moves with it, and in Texas the fixed charges weigh more per kWh at low use. Change it in the field \"Electricity used this month\".",
    def: "600 kWh, for all five bills.",
    source: "An assumption of session 43. EIA's Electric Sales, Revenue, and Average Price for 2024 (Table 5A, released October 2025) gives an average residential month of 503 kWh in California and 1,096 kWh in Texas; its Table 6 gives about 500 kWh for a PG&E bundled home, 506 for SCE and 365 for SDG&E (sales over customers, over twelve months)." },
  { key: "peak-share",
    text: "The share of the month's use that falls from 4 to 9 p.m., the peak hours of all three California rates. Change it in the field \"Share of use from 4 to 9 p.m.\".",
    def: "20 percent, for PG&E, SCE and SDG&E.",
    source: "PG&E Electric Schedule E-TOU-C, Sheet 1: its own example of pro-rating (\"if twenty percent of a customer's usage is in the peak period\"). Taken for SCE and SDG&E as the same assumption; neither tariff gives an example." },
  { key: "super-share",
    text: "The share of use in super off-peak hours: SCE's 8 a.m. to 4 p.m. in winter (none in summer), SDG&E's midnight to 6 a.m. on weekdays and to 2 p.m. on weekends. The share of 4 to 9 p.m. and this one together hold at most 100 percent. Change it in the field \"Share in super off-peak hours\".",
    def: "SCE 33.33 percent (8 of 24 hours); SDG&E 34.52 percent (58 of the week's 168 hours).",
    source: "Use spread evenly over the hours: an assumption (site/data/bill_rules.json). The hours are SCE's Schedule TOU-D, Special Conditions 1, and SDG&E's TOU-DR1 sheet as posted (dated 2018; its old rates are not used). Samuel's ruling 10b of 14 October 2026 holds the two shares at 100 together." },
  { key: "weekdays",
    text: "In an SCE summer, 4 to 9 p.m. is on-peak on weekdays and mid-peak on weekends; the page splits the share of 4 to 9 p.m. by the share of days that are weekdays. Not a field.",
    def: "5 of 7 days (71.43 percent); holidays ignored.",
    source: "An assumption of session 52 (site/data/bill_rules.json)." },
  { key: "season",
    text: "Summer or winter, which sets the rates of every time-of-use line in California. Change it in the field \"Season\".",
    def: "Winter, for the three California bills.",
    source: "Samuel's ruling of 14 October 2026: every California default in the season of 1 October 2026, when the tariffs were read. PG&E's winter is October 1 to May 31 (E-TOU-C); SCE's summer ends at midnight on October 1 (TOU-D, Special Conditions 1); SDG&E's date was not read." },
  { key: "baseline",
    text: "The baseline allowance, the use that earns the baseline credit: PG&E's by territory and SCE's by region, a daily quantity times the bill's days; SDG&E's the reader's own, from the bill, up to 130 percent of it. Change it in the field \"Baseline territory\", \"Baseline region\" or \"Your baseline allowance\".",
    def: "PG&E territory T (San Francisco), 7.5 kWh a day in winter; SCE Region 9, 12.0 kWh a day in winter; SDG&E 0 kWh, so no credit.",
    source: "PG&E E-TOU-C, Sheet 5 (Code B, basic quantities) and Preliminary Statement Part A (San Francisco is all T); SCE Preliminary Statement Part H; SDG&E's allowances by climate zone were not found as text, so the SDG&E default bill carries no baseline credit and is that much too high (USD 25.68 at 240 kWh, for one)." },
  { key: "income-tier",
    text: "PG&E's Base Services Charge is set by household income: Tier 1 and 2 are the CARE and FERA households. Change it in the field \"Income tier\".",
    def: "Income Tier 3, USD 0.79343 a day.",
    source: "PG&E E-TOU-C, Sheet 2 (Advice 7921-E, effective June 1, 2026). SCE and SDG&E have one Base Services Charge on the sheets read: USD 0.794 and 0.79343 a day." },
  { key: "days",
    text: "The days the bill covers: the daily charges and the baseline allowance are per day. Not a field.",
    def: "30 days.",
    source: "An assumption of session 43." },
  { key: "climate-credit",
    text: "The California Climate Credit, a credit per household twice a year. Change it with the box \"This bill carries the California Climate Credit\" (PG&E and SCE).",
    def: "Off: the default bills are months without it.",
    source: "PG&E E-TOU-C, Sheet 2: USD 36.18; SCE TOU-D, Sheet No. 91197-E: USD 36.00. SDG&E's is not in the rules file, so its bill offers no box." },
  { key: "texas-energy",
    text: "In Oncor's and CenterPoint's areas the power is sold by a retail electric provider at the price of the plan the customer chose. The page cannot know it: it is a field. Change it in the field \"Your plan's energy charge\".",
    def: "Oncor USD 0.0907 per kWh; CenterPoint USD 0.0853 per kWh.",
    source: "EIA's average Texas residential price for July 2026, 158.8 USD/MWh (the ERW table eia_retail_electricity_prices, as read on 30 September 2026), less each wires company's delivery charges at 600 kWh, so that each default bill at 600 kWh equals that average. EIA's figure is all customers of all retailers; a plan's price is on its Electricity Facts Label." },
  { key: "wholesale-zone",
    text: "The wholesale price each bill is set against: one zone or hub of the bill's grid, its hourly real-time prices weighted by the whole grid's demand.",
    def: "PG&E: CAISO's NP15 zone. SCE and SDG&E: CAISO's SP15 zone. Oncor and CenterPoint: ERCOT's hub average.",
    source: "The ERW table cost_of_power_monthly (docs/methods/cost_of_power.md), which holds each grid's main hubs, not ERCOT's load zones (Oncor's homes are mostly in the North zone, CenterPoint's in the Houston zone). EIA-930 holds no demand for Northern or Southern California alone, so both CAISO zones are weighted by CAISO's whole demand." },
  { key: "wholesale-month",
    text: "The month of that price: the latest complete month (one with a price in every hour), else the latest month held, said to be partial.",
    def: "The latest complete month in the table.",
    source: "A rule of session 43. On 16 November 2026 the table holds 48 hours of October 2026, so September 2026 is used." },
  { key: "wholesale-energy",
    text: "The wholesale energy of a bill is the kWh on the meter times that price. The energy lost on the wires between the plant and the home, the grid's reserves and other services, and capacity payments are not counted in it: they are inside the other lines.",
    def: "Metered kWh times the price.",
    source: "A choice of session 43. EIA (Frequently Asked Questions, \"How much electricity is lost in electricity transmission and distribution in the United States?\", updated November 7, 2023) puts the losses at about 5 percent of the electricity transmitted and distributed in 2018 through 2022, so a wholesale share with the losses counted would be about a twentieth larger." },
  { key: "left-out",
    text: "Not on any bill here: taxes and local fees in either state, SCE's Modified Cost Allocation Mechanism charge, and SCE's Regions 15 and 16. Every California bill is bundled service: the utility buys the power.",
    def: "Left out.",
    source: "The page's own line: \"taxes and local fees are not included\"; the SCE note in site/data/bill_rules.json says why the charge and the two regions are left out." },
];

export function BillDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7533">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={BILL_DECISIONS.length}>
        {BILL_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-7533-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
      <p className="mt-2 max-w-3xl text-sm">
        Each is described in <Link href="/data/methods/bill" prefetch={false}>the method note</Link>, with the arithmetic of every figure.
      </p>
    </details>
  );
}
