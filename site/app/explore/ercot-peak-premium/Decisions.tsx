import { Tip } from "@/components/tool/ToolPage";

// Session 7507 (chain 304): the choices the ERCOT peak premium explorer makes that move its figures, in the form of the
// tools at the done line (components/tool/DecisionsBlock.tsx, and the default and source on hover that chain 303 gave
// it): one line a choice, its default and its source in a tip. The list is this page's own file, not lib/decisions.ts,
// which several tools share. Words only: no figure of the page is computed from it (the page does no arithmetic; every
// number is a row of ercot_peak_premium_annual or ercot_peak_premium_monthly), so no choice is editable in place: the
// hub, the period and the two years are the filters at the top. docs/methods/ercot_peak_premium.md, "The decisions on
// the page", lists the same keys, and tests/test_session7507_peak_premium.py holds the two to one list.
export type PeakPremiumDecision = { key: string; text: string; def: string; source: string };

export const PEAK_PREMIUM_DECISIONS: PeakPremiumDecision[] = [
  { key: "blocks",
    text: "The day is cut into three blocks by the local clock hour in which a 15-minute interval starts: overnight from 21:00 to 12:00, midday from 12:00 to 16:00, peak from 16:00 to 21:00.",
    def: "These hours on every day of the year, weekends and holidays included. It is not the industry's on-peak block (the 16 hours from 06:00 to 22:00 on weekdays), so no traded on-peak price compares with these figures.",
    source: "The thesis the chart was built for; docs/methods/ercot_peak_premium.md, \"Time-of-day blocks\". ERCOT's market monitor places the tightest hours at about 4 to 5 p.m. in the past and at 7 to 9 p.m. now (Potomac Economics, 2025 State of the Market Report for the ERCOT Electricity Markets, May 2026, page 5): both are inside the peak block." },
  { key: "premium",
    text: "The peak premium is read as two figures: the peak block's median less the midday block's median, and the peak block's interquartile range (its Q3 less its Q1).",
    def: "Medians and quartiles, not means. No mean is on this page: a mean is moved by a few very high intervals (at the hub average in 2021 the plain mean of all intervals is 148.19 USD/MWh and the median 24.60).",
    source: "docs/methods/ercot_peak_premium.md, \"Metrics\"; the mean of 2021 is computed by replication/ercot_peak_premium/from_hourly.py from the same 15-minute prices and is in no table." },
  { key: "percentile",
    text: "A quartile, a median and the 99.9th percentile are read from the sorted prices by linear interpolation at position (n - 1) times p over 100.",
    def: "The default of numpy.percentile. Another convention moves a figure by less than the gap between two neighbouring prices.",
    source: "docs/methods/ercot_peak_premium.md, \"Notation\"." },
  { key: "no-cap",
    text: "Every interval the source publishes is used: nothing is capped, floored or left out, negative prices and prices at the offer cap included.",
    def: "No exclusion. February 2021 (Winter Storm Uri) is in 2021's figures: 645 intervals at or above 1,000 USD/MWh at the hub average, and a 99.9th percentile of 9,000.85.",
    source: "docs/methods/ercot_peak_premium.md, \"Notation\" and \"Completeness\"; ercot_peak_premium_annual." },
  { key: "price",
    text: "The price is ERCOT's real-time settlement point price, one value every 15 minutes, as ERCOT settles it. It is not the day-ahead price and not a traded forward.",
    def: "Real time, each interval counted once whatever the load in it (time-weighted). ERCOT's market monitor reports load-weighted averages by load zone, which run higher: 31.91 USD/MWh for 2024 against a plain mean of 26.83 at the hub average.",
    source: "ERCOT reports NP6-785-ER (yearly history) and NP6-905-CD (the newest days). Potomac Economics, 2024 State of the Market Report for the ERCOT Electricity Markets, May 2025, Table 1, page 5." },
  { key: "hub",
    text: "The page opens on HB_HUBAVG, the average of ERCOT's four trading hubs, and offers each of the six hubs the tables hold.",
    def: "HB_HUBAVG, the hub of the thesis. The others: HB_BUSAVG, HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON. No load zone and no resource node.",
    source: "Session 403; the hubs are the entities of ercot_peak_premium_annual." },
  { key: "local-time",
    text: "A year and a month are ERCOT's own: the local (America/Chicago) year and calendar month in which an interval starts, daylight saving included.",
    def: "Central time. The day the clocks go forward has 92 intervals and the day they go back 100; only the overnight block changes.",
    source: "docs/methods/ercot_peak_premium.md, \"Input\" and \"Time-of-day blocks\"." },
  { key: "years",
    text: "With no year named the page sets the first year held against the newest complete one; a year or a month not yet over is marked partial and is never the default second year.",
    def: "2015 against the newest complete year (the thesis's comparison). A year is complete at 35,040 intervals (35,136 in a leap year); a month at its days times 96, four fewer in March and four more in November.",
    source: "Session 403; the month's exact count since session 7507 (before it a month up to an hour short was drawn as complete)." },
  { key: "thresholds",
    text: "Scarcity is counted as an interval at or above 1,000 USD/MWh, a negative price as an interval at or below 0 (an exact zero counts), and the worst-interval multiple is the 99.9th percentile over the median.",
    def: "1,000 USD/MWh and 0 USD/MWh. A count is of 15-minute intervals: four make an hour.",
    source: "docs/methods/ercot_peak_premium.md, \"Metrics\". The thresholds are the thesis's, not ERCOT's definitions." },
  { key: "rounding",
    text: "A price and a ratio are written with two decimals and a count whole; the tables hold six decimals.",
    def: "A value exactly halfway (37.035, a median between two prices a cent apart) is rounded away from zero: 37.04.",
    source: "Session 7507, which also writes a whole number of dollars with its two decimals (25.00, not 25)." },
  { key: "freshness",
    text: "How old the tables are is read from the site's catalogue and the tables' header, and the page calls them stale when they were last computed more than three days ago.",
    def: "Three days. The two tables are computed on the data machine, not in the daily cloud run, which does not hold the 15-minute history.",
    source: "Session 403; warehouse/run_daily.sh and warehouse/metadata/run_status.csv (the cloud run's rows say \"inputs absent in CI\")." },
];

export function PeakPremiumDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7507">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={PEAK_PREMIUM_DECISIONS.length}>
        {PEAK_PREMIUM_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-7507-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
