// Energy Research Warehouse (ERW) site, session 7505 (chain 304): the decisions of /cost-of-power/battery/awards, in the
// form the five tools and the trackers carry (components/tool/DecisionsBlock.tsx): one fold at the foot of the page, one
// line a choice that moves a figure of the page, and on hover, tap or focus its default, its source and the session
// that made it. The page has no input: every choice here is fixed, and the line says what the figure would do under
// the other choice where the tables can say. The list lives here, in the tool's own folder (the shared list,
// lib/decisions.ts, is being edited on other branches), and is drawn with the same marks, so a test reads it as it
// reads the others. Words only: no figure of the page reads it, and it is drawn whether or not the tables could be
// read, since it describes the method and no row. docs/methods/battery_awards.md, section 6, carries the same list;
// site/scripts/test-battery-awards-render.mjs holds the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type AwardsDecision = { key: string; text: string; session: string; ruling?: string; def: string; source: string };

export const AWARDS_DECISIONS: AwardsDecision[] = [
  { key: "fleet", session: "session 115",
    text: "The fleet is every Energy Storage Resource with a row in ERCOT's file in the month, awarded or not, a resource that was out or testing included.",
    def: "Every resource in the file. In July 2026: 332 resources, of which 252 held a day-ahead award of any kind.",
    source: "ERCOT, 60-Day DAM Disclosure Reports (NP3-966-ER), the file 60d_DAM_ESR_Data, one row a resource and hour." },
  { key: "per-kw", session: "session 115",
    text: "Per kW is per kW of the fleet's MW: the sum of each resource's highest limit (High Sustained Limit) in the month, a resource with no award included. A figure over nameplate, or over the awarded resources only, would be higher.",
    def: "The highest limit of the month, every resource. July 2026: 21,365 MW. The EIA's monthly inventory lists 18,070 MW of batteries operating in ERCOT that month.",
    source: "ERCOT's file, the column HSL; the EIA's figure is Form EIA-860M as the table storage_buildout_monthly holds it (docs/methods/battery_awards.md, section 5)." },
  { key: "energy-price", session: "session 115",
    text: "A day-ahead energy award is valued at the day-ahead price ERCOT prints on the same row, at the resource's own settlement point. A purchase, which is charging, is taken off.",
    def: "The resource's own settlement point, net of charging. An award without its price stops the build; it is never valued at another price.",
    source: "ERCOT Nodal Protocols, sections 4.6.2.1 (Day-Ahead Energy Payment) and 4.6.2.2 (Day-Ahead Energy Charge), as read on 5 October 2026." },
  { key: "ancillary-price", session: "session 115",
    text: "An ancillary service award is valued at that service's day-ahead clearing price for capacity of the same hour. Responsive Reserve is its three kinds of award together at its one price.",
    def: "The day-ahead clearing price, five services: Regulation Up, Regulation Down, Responsive Reserve, ECRS and Non-Spin.",
    source: "ERCOT Nodal Protocols, section 4.6.4.1 (Payments for Ancillary Services Procured in the DAM); the prices are on the rows of ERCOT's file." },
  { key: "month", session: "session 115",
    text: "A month is the Central calendar month of the operating day. A day that is not held adds nothing, and a month whose days are not all held is marked partial and is never scaled to a whole one.",
    def: "No filling, no scaling. December 2025 holds 26 of 31 days (the file begins on 6 December 2025).",
    source: "The days are ERCOT's own Delivery Date; the file's first day is in docs/methods/ercot_storage_dam_awards.md, \"The source\"." },
  { key: "year", session: "session 115",
    text: "A year's figure is the sum of its months' figures per kW, each month over its own MW, over the days held.",
    def: "The months added up. The fleet grew from 17,180 MW in January 2026 to 21,365 MW in July, so one MW for the year would give another figure.",
    source: "docs/methods/ercot_storage_dam_awards.md, \"Rules\"." },
  { key: "model", session: "sessions 115 and 116",
    text: "The model's figure beside the awards is the battery page's day-ahead schedule for one 2-hour battery at the hub average, and stands beside the awards only over months both hold whole.",
    // ruling alternative 3 (wip/alt-battery-awards-3, not a default on main): both durations of the fleet, the monitor's and the EIA's
    def: "2 hours, the day-ahead schedule, HB_HUBAVG. ERCOT's market monitor puts the fleet at more than 17,000 MW and 31,500 MWh at the end of 2025, 1.85 hours. The EIA's monthly inventory gives 1.55 hours in December 2025 and 1.65 in July 2026, the figure /storage draws: 0.20 hours under the monitor's.",
    source: "The model: docs/methods/battery_stack.md. The fleet's size: Potomac Economics, 2025 State of the Market Report for the ERCOT Electricity Markets, June 2026, page ii; Form EIA-860M as the table storage_buildout_monthly holds it (MWh per MW of the batteries operating in ERCOT)." },
  { key: "never-offered", session: "session 116",
    text: "Of the gap between the model and the awards, the part \"never offered\" is the model's figure times the share of the fleet's limit-hours that carried no day-ahead offer of any kind. It is an allocation, not a measurement.",
    def: "The model's average on every limit-hour that offered nothing. January to July 2026: 32.2 percent of limit-hours, 6.5 points of them resources on outage.",
    source: "The offers: ERCOT's files 60d_DAM_ESR_Data (the Energy Bid/Offer Curves) and 60d_DAM_ESR_ASOffers; the rule: docs/methods/ercot_storage_dam_offers.md, \"The gap in three parts\"." },
  { key: "price-part", session: "session 116",
    text: "The part \"price\" is energy only: the MWh the fleet sold day-ahead times the difference between what the model nets on each MWh it discharges and what the fleet netted on each MWh it sold. \"Offered and not awarded\" is what is left, so the three parts add up to the gap.",
    def: "Energy only; ancillary services have no price part, since every awarded MW is paid the hour's one clearing price.",
    source: "docs/methods/ercot_storage_dam_offers.md, \"The gap in three parts\"." },
  { key: "offers-counted", session: "session 116",
    text: "An offer is counted at any price, at the market's cap too, and as power offered hour by hour, not energy. A block priced for several services is counted under each of them.",
    def: "Counted as printed, not capped. January to July 2026: 88 percent of what the curves offered to sell was priced above USD 1,000 per MWh.",
    source: "ERCOT's two files; the check that the curve is read as ERCOT clears it (98.5 percent of resource-hours) is in docs/methods/ercot_storage_dam_offers.md." },
  { key: "hub-price", session: "session 120",
    text: "Real-time energy is valued at the hub average's real-time price, not at each battery's own node, where ERCOT settles it. Charging is valued at the same price.",
    def: "HB_HUBAVG, every 15-minute interval. The node price of a disclosed day is not public: ERCOT's list keeps seven days and the disclosure is 60 days old.",
    source: "ERCOT Nodal Protocols, section 6.6.3.1 (Real-Time Energy Imbalance Payment or Charge at a Resource Node); the hub prices are ERCOT's Settlement Point Prices (NP6-905-CD)." },
  { key: "deviation", session: "session 120",
    text: "What is valued in real time is the deviation from the day-ahead position: for each resource and 15-minute interval, the energy it put out less a quarter of its day-ahead award of that hour.",
    def: "Output less the day-ahead position. Energy sold day-ahead and delivered adds nothing in real time.",
    source: "ERCOT Nodal Protocols, section 6.6.3.1; the output is the Telemetered Net Output of the file 60d_ESR_Data_in_SCED (NP3-965-ER)." },
  { key: "telemetry", session: "session 120",
    text: "Real-time energy is telemetry held from one dispatch run to the next, about five minutes apart, not the settlement meter.",
    def: "Telemetry. ERCOT's metered file in the same disclosure does not hold the storage resources.",
    source: "docs/methods/ercot_storage_realtime.md, \"From SCED runs to hours\"." },
  { key: "rt-ancillary", session: "session 120",
    text: "Real-time ancillary awards are shown as quantities and are not valued: their real-time prices are in neither file.",
    def: "No dollar figure. The set point deviation charges, make-whole payments and fees of the settlement statement are left out too.",
    source: "ERCOT Nodal Protocols, sections 6.7.2.1 to 6.7.2.6 and 6.6.5.5; docs/methods/ercot_storage_realtime.md, \"What it still leaves out\"." },
  { key: "node-days", session: "sessions 120 and 7505",
    text: "The distance of the batteries' own nodes from the hub is measured on the days of node prices held and is applied to no figure: a day's four dearest hours of real-time prices less its four cheapest, at each storage settlement point and at the hub average.",
    def: "Sixteen 15-minute intervals each side, whole days only, the points' median beside the hub.",
    source: "ERCOT, Settlement Point Prices at Resource Nodes, Hubs and Load Zones (NP6-905-CD), as the table ercot_storage_node_basis holds them." },
];

export function AwardsDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="battery-awards">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({AWARDS_DECISIONS.length}): each choice that moves a figure, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={AWARDS_DECISIONS.length}>
        {AWARDS_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-awards-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
              <span className="block" data-decision-session={d.key}><strong>Made in:</strong> {d.session}{d.ruling ? `; ${d.ruling}` : ""}.</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
