import { SiteLink as Link } from "@/components/SiteLink";
import { Tip } from "@/components/tool/ToolPage";

// Session 7504 (chain 304): the decisions of "What a battery saves a customer", in the form the battery page, /deals,
// /impact and /severance carry: one fold, closed to start, one line a choice that moves a figure of the calculator,
// each with its default and its source on hover, tap or focus (the page standard: no grey note under the line). The
// list is kept here, in the tool's own folder, and exported so site/scripts/test-battery-customer-page.mjs,
// tests/test_session7504_battery_customer.py and the method note (docs/methods/battery_customer.md, "The choices that
// move a figure") can be checked against it. Words only: nothing on the page is computed from this list. It is drawn
// by the server, the same for everyone, and it makes no request: the page's promise that nothing typed is sent or
// stored is untouched (the tips are CSS alone, and the one link does not prefetch on this page). Every choice a reader
// can change is changed in place, in the field the line names.
// Session 7513 (chain 304, part B): two sources say more. The hours: the period a demand charge counts is not the
// peak-rate hours (Seattle City Light's is 18 hours long). The round trip: the site's three battery pages set side by
// side (86 here and on What a battery earns, 90 in the home battery game, lib/battery.ts), held by
// site/scripts/test-battery-customer-read.mjs.
export type CustomerBatteryDecision = { key: string; text: string; def: string; source: string };

export const CUSTOMER_BATTERY_DECISIONS: CustomerBatteryDecision[] = [
  { key: "peak-hours",
    text: "The battery must hold its discharge through the whole of your peak. What comes off the peak is the smallest of three: the battery's power, its energy divided by the hours the peak lasts, and the peak itself. Change the hours in the field \"How long your peak lasts\".",
    def: "2 hours.",
    source: "No published source: a starting value of session 88. The peak-rate hours of the tariffs read for the replication are longer: 4 hours at Seattle City Light (5 p.m. to 9 p.m.), 5 at Salt River Project (5 p.m. to 10 p.m.). The hours a demand charge counts can be longer still: Seattle City Light's peak demand charge counts 6 a.m. to midnight, Monday to Saturday. The hours to type are those your own demand stays near its highest inside them." },
  { key: "knows-the-peak",
    text: "The battery knows when the peak comes and is full when it does, in every month: all of the smallest of the three comes off the meter's peak, and the load outside the peak's hours is taken to be lower than the peak by at least that much.",
    def: "All of it: a battery of 4 hours takes its whole power off a peak of 4 hours or less.",
    source: "A choice of session 88. On the measured loads of 98 buildings, the National Renewable Energy Laboratory found about 85 percent of a 4 hour battery's power a reasonable expectation, and less for a shorter battery (Neubauer and Simpson, Deployment of Behind-The-Meter Energy Storage for Demand Charge Reduction, NREL/TP-5400-63162, January 2015, page 16)." },
  { key: "one-demand-charge",
    text: "One demand charge on one monthly peak. Where a tariff charges each kW of the same peak twice, type the sum; where it has a second charge on another peak (the highest demand of the other hours, a ratchet), that charge is not lowered here.",
    def: "The one number typed in \"Demand charge\".",
    source: "Austin Energy's tariff of October 1, 2026 puts a demand charge and a regulatory charge on each billed kW. Salt River Project's E-32 price plan charges the on-peak kW and the highest kW of the other hours apart." },
  { key: "two-rates",
    text: "Two energy rates: the battery discharges at the peak-hours rate and charges at the off-peak rate, and charging sets no new peak. A tariff with a third rate between them is typed as the two the battery would use.",
    def: "The two numbers typed.",
    source: "Seattle City Light's time of use rate has peak, mid-peak and off-peak prices; Salt River Project's E-32 has on-peak, shoulder and off-peak prices." },
  { key: "round-trip",
    text: "Of each kWh put into the battery, the share that comes back out. The energy bought off-peak is the energy discharged divided by it. Change it in the field \"Round trip\".",
    def: "86 percent.",
    source: "Lazard, Levelized Cost of Energy+, June 2025 (storage, page 43): 86 percent is the low end of its range. The Annual Technology Baseline 2025 of the National Laboratory of the Rockies gives 85 percent. Both are figures for batteries on the grid, the same 86 percent as on What a battery earns. The home battery game of this site starts at 90 percent, inside the 88 to 91 percent the same Lazard report gives for a home battery standing alone. No figure for a commercial customer's battery was read." },
  { key: "days",
    text: "The days a month the battery runs: the days that have peak-rate hours. Change them in the field \"Days a month it runs\".",
    def: "21 days.",
    source: "The calendar: 2026 has 261 weekdays, 21.75 a month, and about 21 once a tariff's holidays are out. Tariffs differ: Salt River Project's E-32 counts Monday to Friday, Seattle City Light's rates Monday to Saturday, about 26 days a month." },
  { key: "one-cycle",
    text: "When moving energy pays, the battery makes one full cycle on each day it runs: all of its energy out in the peak-rate hours, whatever the building uses in those hours, and that much divided by the round trip back in off-peak.",
    def: "One full cycle a day.",
    source: "A choice of session 88. The National Renewable Energy Laboratory calls a cycle on every day a worst case for the energy used (Neubauer and Simpson, 2015, page 9)." },
  { key: "when-shifting-pays",
    text: "Moving energy is counted only when it pays: when the peak rate is above the off-peak rate divided by the round trip. When it does not, the battery cycles only what the peak needs on each day it runs, and the energy lost on the way is counted as a cost.",
    def: "Decided by the two rates typed. With one price for every hour it never pays.",
    source: "Arithmetic, stated in the method note. Austin Energy's secondary voltage rates of October 1, 2026 have one price for every hour." },
  { key: "twelve-months",
    // ruling alternative 2 (wip/alt-battery-customer-2, not a default on main): the year by the plan's own seasons
    text: "The year is the sum over your plan's seasons: type up to two other seasons under the fields, each its months and its three rates; the rates in the fields hold for the months left. With no other season typed it is the month twelve times.",
    def: "Twelve months alike until another season is typed (on the site: twelve months alike, no season to type).",
    source: "A choice of session 88, and the ruling's other choice. Salt River Project's E-32 prices two summer peak months, four summer months and six winter months; on the replication's case, twelve of its July are 52 percent more than the year added by season." },
  { key: "bill-only",
    text: "The saving is the saving on the bill. The battery's price, its upkeep and its wear are not counted, nor taxes, riders, fixed charges, solar on the same meter or a utility program's payment.",
    def: "Left out.",
    source: "A choice of session 88, listed on the page under \"What it leaves out\"." },
];

export function CustomerBatteryDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7504">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={CUSTOMER_BATTERY_DECISIONS.length}>
        {CUSTOMER_BATTERY_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-7504-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
      <p className="mt-2 max-w-3xl text-sm">
        Each is described in <Link href="/data/methods/battery_customer" prefetch={false}>the method note</Link>, with the arithmetic of every figure.
      </p>
    </details>
  );
}
