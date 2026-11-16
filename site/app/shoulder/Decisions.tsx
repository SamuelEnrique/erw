import { Tip } from "@/components/tool/ToolPage";

// Session 7503 (chain 304): the choices "The shoulder hours" makes that move its figures, in the form of the tools at
// the done line (components/tool/DecisionsBlock.tsx, and the default and source on hover that chain 303 gave it): one
// line a choice, its default and its source in a tip. The list is this page's own file, not lib/decisions.ts, which
// several tools share. Words only: no figure of the page is computed from it (the page does no arithmetic; every number
// is a row of shoulder_hours_monthly), so no choice is editable in place. docs/methods/shoulder.md, section 6, lists
// the same keys, and tests/test_session7503_shoulder.py holds the two to one list.
export type ShoulderDecision = { key: string; text: string; def: string; source: string };

export const SHOULDER_DECISIONS: ShoulderDecision[] = [
  { key: "level",
    text: "The evening shoulder is measured against net load's daily mean: it lasts while net load is above the mean of the day's 24 hours.",
    def: "The daily mean. A higher level gives a shorter shoulder: the second measure on this page uses the midpoint between the mean and the evening peak.",
    source: "Session 75; docs/methods/shoulder_hours.md, \"On the average day\". The term is this page's, not an industry standard." },
  { key: "start",
    text: "The shoulder starts at the first hour after solar's highest hour in which solar is below half of that highest value.",
    def: "Half of the day's highest solar hour.",
    source: "Session 75; solar is EIA-930's SUN plus SNB (solar with storage), or CAISO's own solar." },
  { key: "end",
    text: "It ends at the first hour, after net load has risen above the mean, in which net load is back at or below it; when that never comes it is cut at midnight, and the page says so.",
    def: "Cut at midnight, not carried into the next day. In California every month held, and in Texas every month of 2026 and eleven of the twelve of 2025, the shoulder is cut.",
    source: "Session 75; the flag shoulder_runs_to_midnight of shoulder_hours_monthly." },
  { key: "energy",
    text: "The shoulder's energy counts only the hours in which net load is above the mean; its length counts every hour from its start.",
    def: "An early hour of the shoulder below the mean adds nothing and takes nothing away.",
    source: "Session 75's builder; stated in the note by session 7503, which recomputed it." },
  { key: "second",
    text: "The second measure is the run of hours around the evening's highest net load in which net load is above the midpoint between its daily mean and that peak.",
    def: "The midpoint (half of the rise from the mean to the peak), starting no earlier than the first shoulder.",
    source: "Session 80; docs/methods/shoulder_hours.md, \"The second measure and the worst days\"." },
  { key: "average-day",
    text: "A month is its average day: each local hour's mean over the month's complete days. A month with fewer than 90 percent of its days complete is not shown.",
    def: "90 percent of the month's days; a complete day holds every hour of demand, solar and wind. Nothing is filled.",
    source: "Session 75; EIA Form EIA-930, the per-balancing-authority workbooks (Adjusted columns)." },
  { key: "net-load",
    text: "Net load is demand less solar and wind.",
    def: "Solar is SUN plus SNB and wind is WND plus WNB in EIA-930. Imports, hydro, gas and batteries are not subtracted.",
    source: "Session 75; EIA Form EIA-930." },
  { key: "local-time",
    text: "Hours are the grid's own clock hours, daylight saving included. A day of 23 or 25 hours enters the month's average and is never ranked.",
    def: "Central time for ERCOT, Pacific time for CAISO; an hour is named by its start.",
    source: "Sessions 75 and 80." },
  { key: "surplus",
    text: "The midday surplus is the run of hours around net load's lowest hour of the day in which net load is below its mean, wherever that hour falls.",
    def: "The lowest hour of the whole day. In California it is between 09:00 and 14:00 in every month held; in Texas it was between 01:00 and 04:00 in 60 of the 93 months, the last of them May 2024, and the run there was mostly the night's; since July 2024 it is between 09:00 and 14:00.",
    source: "Session 75; counted from shoulder_hours_monthly by session 7503." },
  { key: "fleet",
    text: "The fleet is the batteries operating that month in EIA's monthly generator inventory: their MW and their MWh. A grid operator's own count is larger.",
    def: "EIA-860M, operating units. At the end of 2025: ERCOT 13,909 MW and 21,579 MWh here, against more than 17,000 MW and 31,500 MWh in its market monitor's report; California 15,760 MW here, against over 17 GW in its market monitor's.",
    source: "storage_buildout_monthly (EIA-860M). Potomac Economics, 2025 State of the Market Report for the ERCOT Electricity Markets, June 2026, page ii; CAISO Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance, June 2026, page 23." },
  { key: "covered-needed",
    text: "Hours covered is the smaller of the shoulder's length and the fleet's duration (its MWh over its MW). Hours needed is the shoulder's energy over the fleet's MW.",
    def: "The batteries alone, at rated power, full at the shoulder's start, with no losses and no transmission limit.",
    source: "Session 75; docs/methods/shoulder_hours.md, \"The fleet against it\"." },
  { key: "worst-days",
    text: "The worst days are the ten days of each year with the most shoulder energy above the day's own mean, among complete days of 24 hours that have a shoulder.",
    def: "Ten days a grid and local year, each measured on its own hours; the year's figure is their mean, or is not given when a day lacks the fleet.",
    source: "Session 80." },
  { key: "california",
    text: "California is shown from two sources, never mixed: EIA-930 to November 2025, and CAISO's own supply by fuel from June 2025.",
    def: "Two grids in the panel. In CAISO's own data, demand is the sum of its thirteen sources, imports and batteries included.",
    source: "Session 80; docs/methods/eia930_caiso_break.md (EIA's California series changed in December 2025)." },
  { key: "late-hours",
    text: "California's EIA-930 values from 1 November 2023 to 2 December 2025 are read one hour earlier than EIA stamps them.",
    def: "One hour, over that period only. EIA's solar matches CAISO's own 5-minute solar at that shift on each of 182 days, and at none after.",
    source: "Session 82; docs/methods/eia930_caiso_break.md, \"The late hours\"." },
  { key: "impossible-hours",
    text: "An hour of demand that could not have happened is a blank, and its day is not a complete day.",
    def: "Held, above zero, within 25 percent of the median of the four hours around it, and between one third of and three times the grid's median.",
    source: "Sessions 103 and 118; docs/methods/impossible_hours.md, rule A." },
  { key: "texas-batteries",
    text: "Texas's battery output is EIA-930's series as published: discharge only from 23 October 2024 to 15 December 2025, net of charging from then.",
    def: "Not adjusted. A Texas month before December 2025 shows no charging because the series held none.",
    source: "EIA Form EIA-930, ERCO, the column Adjusted BAT Gen, read by session 7503." },
  { key: "curtailment",
    text: "California's curtailment is CAISO's own count, curtailed solar plus curtailed wind, a day of the month held. Texas's is not held.",
    def: "The month's total over its days held; no estimate where a grid publishes none.",
    source: "caiso_curtailment_daily: CAISO, Production and curtailments data, and its Daily Renewable Report." },
  { key: "opening",
    text: "With no month named, a grid opens on the latest month that holds every figure of the summary and the headline numbers.",
    def: "The newest month usually lacks the fleet, which EIA publishes a month or two behind; it stays in the panel.",
    source: "Session 90." },
];

export function ShoulderDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7503">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={SHOULDER_DECISIONS.length}>
        {SHOULDER_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-7503-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
