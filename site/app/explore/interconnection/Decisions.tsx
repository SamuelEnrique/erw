import { Tip } from "@/components/tool/ToolPage";

// Session 7509 (chain 304): the choices the interconnection queue explorer rests on that move its figures, in the form
// of the tools at the done line (components/tool/DecisionsBlock.tsx, and the default and source on hover that chain 303
// gave it): one line a choice, its default and its source in a tip. The list is this page's own file, not
// lib/decisions.ts, which several tools share. Words only: the page does no arithmetic (every number is one row of
// iso_queue_statistics, or the one count its header states), so no choice is editable in place: the queue, the count
// and the two entry years are the filters at the top. docs/methods/interconnection_explorer.md, "The decisions on the
// page", lists the same keys, and tests/test_session7509_interconnection.py holds the two to one list.
export type InterconnectionDecision = { key: string; text: string; def: string; source: string };

export const INTERCONNECTION_DECISIONS: InterconnectionDecision[] = [
  { key: "snapshot",
    text: "A queue is the grid operator's public report as the ERW pulled it on one day, the pull the table was last built from: one row a position, in the state the report gives it on that day. It is not a history of the queue.",
    def: "One pull, named with its day in the line under the title. The ERW pulls the queues again each Monday, and the table moves only when it is rebuilt. A position an operator has dropped from its report is in no figure, so an early entry year can hold fewer withdrawn positions here than in a count kept year by year (Berkeley Lab's Queued Up).",
    source: "Each operator's queue report (CAISO's Public Queue Report, ERCOT's Generation Interconnection Status report, SPP's Generation Interconnection queue summary), read by warehouse/connectors/iso_queues.py; docs/methods/energy_projects.md, \"Queue statistics\"." },
  { key: "statuses",
    text: "Each position is counted in one of four statuses, read from the operator's own status word: reached operation, withdrawn, still waiting, or status not stated.",
    def: "Reached operation: COMPLETED (CAISO), IA FULLY EXECUTED/COMMERCIAL OPERATION (SPP). Withdrawn: WITHDRAWN (CAISO), WITHDRAWN and TERMINATED (SPP). Still waiting: every other status word, a suspended position included. A position with no status word is \"status not stated\". ERCOT's report has no word for a plant in operation: the library the ERW reads it through writes \"Completed\" when the report gives a position a day its interconnection agreement was signed, so for ERCOT the first group is headed \"Agreement signed\" and the third \"No agreement yet\" (session 7518).",
    source: "docs/methods/energy_projects.md, \"What counts, in each ISO's own words\"; the connector's map of status words, which stops on a word it does not know." },
  { key: "entry-year",
    text: "A position belongs to the year of its queue date. A position with no queue date is in no year; the table's header counts them and the page prints that count.",
    def: "The calendar year of the operator's queue date. On the table as built on 21 October 2026: no CAISO position, 1 of ERCOT's and 48 of SPP's have no queue date.",
    source: "docs/methods/energy_projects.md, \"Queue statistics\"; the header line \"Positions with no queue date\" of iso_queue_statistics." },
  { key: "ercot-withdrawn",
    text: "ERCOT's report lists active and completed positions only, so ERCOT has no withdrawn count and no withdrawn share; its third headline number is the positions with no signed agreement yet.",
    def: "\"not held\" in ERCOT's Withdrawn column and in the share. Nothing is estimated in its place.",
    source: "ERCOT's Generation Interconnection Status report; docs/methods/energy_projects.md, \"What counts, in each ISO's own words\"." },
  { key: "share",
    text: "The withdrawn share is the withdrawn positions over the positions entered that year, by count, written as a fraction of 1 (0.80 is 80 in 100). It is not a share of MW.",
    def: "By count, in positions and in MW view alike. A recent year's share is not final: its positions have had less time to be withdrawn.",
    source: "docs/methods/energy_projects.md, \"Queue statistics\" (the withdrawal rate)." },
  { key: "wait",
    text: "The median wait is the middle value of the years from the queue date to the in-service date (days over 365.25), over the year's positions that reached operation and hold both dates in that order. \"Waits counted\" says how many.",
    def: "A median, with its count beside it; a year in which no operating position holds both dates is \"not held\". SPP's date is its Commercial Operation Date, which its queue also fills for positions not yet built: for an operating position it may be the date requested, not achieved. ERCOT's wait runs from the day the screening study started to the day of approval to synchronize. A position still waiting is in no wait, so a recent entry year's median stands on its fastest positions and is not final.",
    source: "docs/methods/energy_projects.md, \"Queue statistics\" (the wait); the queue tables' queue_date and actual_in_service_date." },
  { key: "mw",
    text: "MW is the capacity the queue states for a position, added up over the positions of the status. A position that states no capacity is in the positions and not in the MW.",
    def: "The operator's requested capacity, as stated. Where no position of a status states a capacity, most often because the year has no position in that status, the table has no MW row and the cell reads \"not held\", while the same cell in positions reads 0.",
    source: "docs/methods/energy_projects.md, \"Queue statistics\" (MW); docs/methods/interconnection_explorer.md, \"When a cell reads not held\"." },
  { key: "no-sum",
    text: "Every number on the page is one row of the table, or the one count its header states. The page adds nothing up: no total over years, over statuses or over queues.",
    def: "No total. The four statuses of a year make up its positions entered (checked for every queue and year by replication/interconnection/replicate.py).",
    source: "Session 405; site/scripts/check-values.mjs reads each figure's row again on the built site." },
  { key: "years",
    text: "With no year named the page draws every entry year the queue holds, to the newest one that is over. An entry year at or after the year the queue was pulled is marked partial and is never the default last year.",
    def: "The first year held to the newest complete year. CAISO's dated positions end with those that entered in 2023, so CAISO opens on 2023; ERCOT and SPP open on 2025.",
    source: "Session 405; the header line \"Inputs read\" of iso_queue_statistics gives the day each queue was pulled." },
  { key: "queues",
    text: "The page opens on CAISO and offers six queues. PJM is not among them: the ERW holds no PJM queue table. A queue whose publisher asks for permission is not read and reads \"license needed\".",
    def: "CAISO, in positions. Held since 21 October 2026: NYISO, MISO and ISO-NE. Shown: CAISO, ERCOT and SPP.",
    source: "Session 405; docs/licenses.md and the owner's ruling of 12 October 2026 (site/data/license_status.json)." },
  { key: "rounding",
    text: "A count of positions is written whole; MW, the share and the wait are written with two decimals. The table holds six.",
    def: "Two decimals, a whole value included (550.00 MW, a share of 1.00).",
    source: "Session 7509; until then a value that happened to be whole was written without its decimals." },
  { key: "freshness",
    text: "How old the table is comes from the site's catalogue and from the table's own header; the page calls a table stale when it was last computed more than eight days ago.",
    def: "Eight days: the queues are pulled once a week, on Mondays, so eight days is a missed pull (the other explorers use three). The table is rebuilt on the data machine, not in the daily cloud run that pulls the queues, so it can be older than the queue tables it was built from.",
    source: "Session 403 (the explorers' shared frame) and session 7509 (eight days); warehouse/run_daily.sh; the header lines \"Retrieved\" and \"Inputs read\" of iso_queue_statistics." },
];

export function InterconnectionDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7509">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={INTERCONNECTION_DECISIONS.length}>
        {INTERCONNECTION_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-7509-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
