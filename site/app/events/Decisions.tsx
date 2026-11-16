// Energy Research Warehouse (ERW) site, session 7531 (chain 304): the decisions of /events and its nine event pages, in
// the form the battery awards page carries (app/cost-of-power/battery/awards/Decisions.tsx): one fold at the foot of the
// page, one line a choice that moves a figure of the page, and on hover, tap or focus its default, its source and the
// session that made it. The pages have no input: every choice is fixed when the table is built or the page is drawn,
// so nothing here is editable, and the line says what the other choice would do where the notes can say. An event page
// draws the shared choices and its own (`events`); the index draws the shared ones. Words only: no figure reads this
// list, and it is drawn whether or not the table could be read. docs/methods/events.md, section "The decisions on the
// pages", carries the same list in the same order; site/scripts/test-events-render.mjs holds the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type EventDecision = { key: string; text: string; session: string; def: string | Record<string, string>; source: string; events?: string[] };

const WINDOW: Record<string, string> = {
  uri_2021: "2021-02-07 to 2021-02-24, eighteen days: the week before the storm, the storm and the week after.",
  covid_2020: "2020-03-01 to 2020-05-31, ninety-two days.",
  caiso_heat_2020: "2020-08-10 to 2020-08-24.",
  caiso_heat_2022: "2022-08-31 to 2022-09-09.",
  elliott_2022: "2022-12-19 to 2022-12-29.",
  ercot_heat_2023: "2023-08-01 to 2023-09-10.",
  cold_2025: "2025-01-17 to 2025-01-26, chosen from EIA's hourly data: the days of the highest winter hours of September 2024 to August 2025.",
  east_heat_2025: "2025-06-20 to 2025-06-28, chosen from EIA's hourly data: the days of the highest hours of September 2024 to August 2025.",
  cold_2026: "2026-01-23 to 2026-02-02, chosen from EIA's hourly data: the days of the highest winter hours of November 2025 to March 2026.",
};

export const EVENT_DECISIONS: EventDecision[] = [
  { key: "window", session: "sessions 36B to 308",
    text: "Each event is a fixed window of local days, both ends included. Every \"highest\" and \"lowest\" of the page is taken inside it; a longer or shorter window could move the day and the figure picked, and moves every estimate.",
    def: WINDOW, source: "docs/methods/events.md, each event's section; the dates the pages cite are the operators' and the government's accounts named in the framing." },
  { key: "baseline", session: "sessions 36B, 36C and 49",
    text: "An event day is set against the same days of earlier years: the same weekday 364 and 728 days earlier, so a Monday meets a Monday. A calendar-day baseline would set a Sunday against a Monday.",
    def: { uri_2021: "The same calendar days of 2019 and 2020 (the first event, before the weekday rule).", covid_2020: "The same weekday of 2019 and 2018 for the seven ISO grids; the Lower 48, 2019 alone (EIA's 2018 file does not hold it).", "": "The same weekday 364 and 728 days earlier, both years held." },
    source: "docs/methods/events.md, \"Baseline: weekday-aligned\" and \"Session 49\"." },
  { key: "local-day", session: "session 36C",
    text: "A day is the grid's own local day: Central for ERCOT and SPP, Eastern for PJM, NYISO, ISO-NE and the Lower 48, Pacific for CAISO, and Eastern Standard Time all year for MISO, its market day. A day in UTC would move an evening peak to the next day.",
    def: "Each grid's own zone. SPP's highest hour of Winter Storm Elliott, 18:00 Central on 2022-12-22, is 00:00 UTC on 2022-12-23.",
    source: "docs/methods/events.md, \"The second event: COVID-19\", Days." },
  { key: "complete", session: "sessions 36B and 36C",
    text: "A day's value is written only when every interval of it is held: 24 EIA-930 hours, 96 real-time intervals, 24 day-ahead hours (23 and 92 on the spring change). A day with one hour missing has no point and no comparison; nothing is filled.",
    def: "Complete days only. CAISO's 2020-08-10, MISO's 2021-12-27 and ISO-NE's 2025-06-25 are among the days left out.",
    source: "docs/methods/events.md, \"Complete days only\" and each event's \"Left out\"." },
  { key: "served", session: "session 36B",
    text: "Demand is demand served (EIA-930's hourly demand), not what customers would have used. During rotating outages the load that was shed is not in it, so a figure of those days is a floor.",
    def: "EIA-930 demand served, from EIA's per-balancing-authority workbooks (the 2018 baseline from EIA's six-month file).",
    source: "docs/methods/events.md, \"Demand during load shed is load served\"." },
  { key: "peak-hour", session: "session 39",
    text: "The peak hour against the baseline is the day's highest hour over the mean of the baseline days' highest hours, minus one, in percent: each day's own peak, whatever hour it fell in.",
    def: "demand_max_pct_vs_baseline; a day needs the event day and at least one baseline day complete.",
    source: "docs/methods/events.md, \"Session 39\", the variables max_vs." },
  { key: "pick", session: "session 39",
    text: "A figure under a chart is a row of the table picked by the rule its sentence states (the highest, the lowest, or a named day); of two equal values the earlier day is taken. The page computes no value of its own outside the estimates.",
    def: "The first of equal values in day order.",
    source: "site/app/events/EventWindow.tsx; replication/events/replicate.py recomputes each pick from the rule (docs/methods/events.md, \"The figures on the pages\")." },
  { key: "intensity", session: "session 36B",
    text: "Carbon intensity is the day's CO2 from generation (EIA's estimates) times 1,000 over its net generation, in kg CO2 per MWh generated: not per MWh consumed, and imports carry none.",
    def: "carbon_intensity_daily's formula, over the grid's local day.",
    source: "docs/methods/events.md, \"Sources and variables\"; eia930_all_emissions." },
  { key: "price", session: "sessions 36B and 64",
    text: "Price is ERCOT's hub average (HB_HUBAVG): the day's mean and highest 15-minute real-time price and the day-ahead mean and highest hour. Since the January 2025 cold, four other hubs from 2024-09-01, with no baseline days; MISO's real-time price is hourly.",
    def: "ERCOT HB_HUBAVG; MISO Indiana Hub, NYISO N.Y.C., ISO-NE Internal Hub, SPP North Hub. PJM's prices are internal and not used.",
    source: "docs/methods/events.md, \"Sources and variables\" and \"Session 64\"; ERCOT NP6-785-ER and NP4-180-ER; iso_hub_prices_history." },
  { key: "spec", session: "session 47",
    text: "The estimate is a regression of each day's value on the event days, six weekday indicators (Monday the reference) and the baseline years coded to sum to zero; the event year takes none, so its counterfactual is the average baseline year. Growth since the baseline years counts as effect.",
    def: "dow_year_mean_v1. A linear trend in place of the year effects (dow_trend_v1) is in the table, not on the page.",
    source: "docs/methods/event_study.md, \"Specification\" and \"Identification and what it assumes\"." },
  { key: "inference", session: "session 47",
    text: "Intervals are 95 percent, normal: estimate plus or minus 1.96 robust (HC1) standard errors; a single day's error adds the baseline fit's residual variance. A t interval would be somewhat wider on baselines of 22 to 92 days.",
    def: "HC1, z = 1.96.",
    source: "docs/methods/event_study.md, \"Inference\"." },
  { key: "temperature", session: "session 49",
    text: "The second estimate adds the day's heating and cooling degree days at 65 F and their squares, the mean over the grid's airports, the day's mean taken as (max + min) / 2; days without weather are left out of it. Events with no station held have no second estimate.",
    def: "ERCOT DFW and IAH, CAISO SAC and LAX, PJM PHL and ORD, MISO MSP, NYISO JFK, ISO-NE BOS, SPP OKC; none for the Lower 48, the January 2025 cold, the June 2025 heat and the January 2026 cold.",
    source: "docs/methods/event_study.md, \"Temperature-controlled specification\"; NOAA NCEI ISD (noaa_isd_hourly)." },
  { key: "weather-share", session: "session 49",
    text: "The share the weather terms account for, 1 minus the controlled estimate over the first, is printed only when the two share a sign and the controlled one is no larger in size; otherwise the page says no share can be put down to weather.",
    def: "Printed only under that condition.",
    source: "docs/methods/event_study.md, \"What the pages say\"." },
  { key: "after-order", session: "session 36C", events: ["covid_2020"],
    text: "Beside each grid's deepest weekly drop, the deepest from the week of 2020-03-22 on, the first whole week after California's order of 2020-03-19; the index's card reads from that week too. A drop before any order is not the pandemic's.",
    def: "The week of 2020-03-22 (Sunday to Saturday).",
    source: "Office of the Governor of California, Executive Order N-33-20, 2020-03-19; docs/methods/events.md, \"What the page reads\"." },
  { key: "weeks", session: "session 36C", events: ["covid_2020"],
    text: "A week is Sunday to Saturday, dated by its Sunday: its seven days' demand over the seven baseline days' demand, written only when every day of the week and of its baseline is complete. 2020-05-31 begins a week the window does not finish, so it has no weekly row.",
    def: "Thirteen whole weeks, 2020-03-01 to 2020-05-30.",
    source: "docs/methods/events.md, \"Weeks\"." },
];

/** The choices an event's page draws: the shared ones and its own; the index (no event) draws the shared ones. */
export function decisionsOf(event?: string): EventDecision[] {
  return EVENT_DECISIONS.filter((d) => !d.events || (event !== undefined && d.events.includes(event)));
}

/** A choice's default for an event: its own line where it has one, else the line for every other event. */
export function defaultOf(d: EventDecision, event?: string): string {
  if (typeof d.def === "string") return d.def;
  if (event !== undefined && d.def[event]) return d.def[event];
  if (d.def[""]) return d.def[""];
  return Object.entries(d.def).map(([e, v]) => `${e}: ${v}`).join(" ");
}

export function EventDecisions({ event }: { event?: string }) {
  const list = decisionsOf(event);
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions={event ?? "events"}>
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({list.length}): each choice that moves a figure, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={list.length}>
        {list.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-events-${event ?? "index"}-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {defaultOf(d, event)}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
              <span className="block" data-decision-session={d.key}><strong>Made in:</strong> {d.session}.</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
