// Energy Research Warehouse (ERW) site, session 7534 (chain 304): the decisions of the problem sets (/learn/problems and
// each set's page), in the form the battery awards page and the trackers carry: one fold at the foot of the page, one
// line a choice that moves a figure or an answer, and on hover, tap or focus its default, its source and the session or
// ruling that made it. The sets have no input: every choice is fixed. A set's page draws the choices of that set; the
// index draws them all. Words only: no figure reads this list, and it is drawn whether or not the tables could be read.
// docs/methods/problem_sets.md, "The decisions", carries the same list; site/scripts/test-problem-sets-render.mjs holds
// the two to one list.
import { Tip } from "@/components/tool/ToolPage";
import { DECISIONS as REPORT_DECISIONS } from "@/lib/problemsets/a-forecasts-report-card";

export type ProblemDecision = { key: string; sets: string[]; text: string; def: string; source: string; session: string };

const A = "know-your-grid", B = "prices-and-your-bill", C = "when-the-grid-broke", D = "storage-and-taxes", E = "networks-and-money";
// session 8901 (chain 507, part C): the four sets of the whole country
const T = "who-trades-with-whom", S = "storm-across-the-country", R = "under-the-ground-and-in-the-wind", W = "where-energy-goes";
// session 8905 (chain 590, part C): the fifth, a balancing authority's own facts
const Y = "your-own-balancing-authority";

export const PROBLEM_DECISIONS: ProblemDecision[] = [
  { key: "live", sets: [A, B, C, D, E],
    text: "A live set asks its questions of the newest rows the live set holds when the page is built, at most an hour old; a dated edition keeps the numbers of its day.",
    def: "Live, rebuilt at most once an hour; the edition of 15 October 2026 for a class.",
    source: "docs/methods/problem_sets.md, \"How an answer is made\" and \"Dated editions\"; Samuel's ruling 8a of 14 October 2026.", session: "sessions 44 and 293" },
  { key: "full-day", sets: [A],
    text: "Questions 1 and 2 take the newest UTC day both the demand and the generation tables hold in full: 24 hours, both grids, every variable asked. The worked example takes the day before when both grids' demand holds its 24 hours.",
    def: "The newest whole UTC day of both tables. A day with an hour missing in either grid is passed over, never filled.",
    source: "EIA, Hourly Electric Grid Monitor (Form EIA-930), as eia930_all_demand and eia930_all_generation hold it; site/lib/gridday.ts.", session: "session 369" },
  { key: "battery-day", sets: [A, D],
    text: "A battery question takes the latest day the daily cycle table holds for the grids it asks about (each grid's local day), whether or not that day's hours were all in when the table was built.",
    def: "The latest day held. The table holds no count of the hours behind a day, so a day built from part of its hours cannot be told apart.",
    source: "storage_daily_cycle, from EIA-930's battery series (ERCOT) and CAISO's own battery data; docs/methods/eia930_all_storage.md.", session: "sessions 44 and 7534" },
  { key: "local-day", sets: [A],
    text: "Question 5 adds ERCOT's hourly demand over the battery day's Central-time day, from one local midnight to the next in UTC, and asks only when every hour of it is held.",
    def: "Central time (America/Chicago), 23, 24 or 25 hours by the clock change; no sum over a day that is not whole.",
    source: "docs/methods/problem_sets.md; ERCOT's battery day is a local day in storage_daily_cycle.", session: "session 149" },
  { key: "complete-month", sets: [B, D],
    text: "A month question takes the latest month that is complete for the hub: its real-time hours equal the month's hours. The hour-of-day profile, which counts no hours, takes the latest profile month complete for ERCOT's hub average.",
    def: "rt_hours equal to hours_in_month in cost_of_power_monthly; the worked example takes the complete month before.",
    source: "docs/methods/problem_sets.md, ruling 5a of 14 October 2026; docs/methods/cost_of_power.md.", session: "session 288" },
  { key: "public-hubs", sets: [B],
    text: "Question 2 ranks the hubs whose rows are public, in the latest month each holds at least 95 percent of its hours, and names any hub short of its hours with them.",
    def: "The public rows' hubs (ISO-NE's, MISO's and NYISO's rows are held for a license and never reach the page); 95 percent.",
    source: "docs/methods/problem_sets.md, ruling 4 of 14 October 2026; the hold: site/lib/license.ts.", session: "sessions 288 and 7534" },
  { key: "bill", sets: [B],
    text: "Questions 3 and 4 take the default bills of /learn/bill as they stand, and value their kWh at the latest complete month's load-weighted real-time price of the bill's own hub.",
    def: "600 kWh. PG&E E-TOU-C in winter, 20 percent at peak, territory T, Income Tier 3; Oncor with the retailer's energy charge set so the bill matches EIA's Texas average. NP15 for PG&E, ERCOT's hub average for Oncor.",
    source: "site/data/bill_rules.json, each rate quoted from its tariff; docs/methods/bill.md.", session: "sessions 43 and 288" },
  { key: "baseline", sets: [C],
    text: "An event question sets the storm's window against its baseline: the same days, or the same weekdays, of the earlier years the event table names.",
    def: "The baseline of event_window_daily; Uri against the same days of 2019 and 2020.",
    source: "docs/methods/event_window.md and docs/methods/events.md.", session: "session 44" },
  { key: "seven-days", sets: [D],
    text: "Question 1 adds the seven latest days the daily cycle table holds for ERCOT in the last 45 days, so a gap in the table is passed over; with fewer than seven held it says how many.",
    def: "Seven days held, not seven calendar days; 45 days back.", source: "storage_daily_cycle; this page's fault of 16 November 2026 (six days summed as seven).", session: "session 7534" },
  { key: "game-battery", sets: [D],
    text: "The battery questions use the home battery game's battery and its fictional fleet, assumptions and not measurements, and one full cycle at the month's cheapest and dearest average hours.",
    def: "13.5 kWh, 90 percent round trip (the square root of 0.9 each way), 10,000 homes.",
    source: "docs/methods/battery_game.md (ruling 3a for the fleet).", session: "session 46" },
  { key: "tax", sets: [D],
    text: "A tax is the state's production tax at its base rate on the month's mean of EIA's daily spot price; fees are left out. Louisiana's well was completed before July 2025; New Mexico's well has no district ad valorem; a gas price per MMBtu is applied per Mcf.",
    def: "The rates of site/data/severance_rules.json, each quoted from its statute or agency page; New Mexico's rates are those the file states for 1 April to 31 August 2026, the newest it holds.",
    source: "site/data/severance_rules.json; docs/methods/severance.md; EIA, spot prices (eia_fuel_spot_prices).", session: "sessions 46 and 7534" },
  { key: "credit", sets: [D],
    text: "Question 5's credit is set by the Texas Comptroller's certified price for the month, not by the well's own price, at the latest held month that has one.",
    def: "The certified price in 2005 dollars and its tier: no credit above USD 3.50, 25, 50 or 100 percent below.",
    source: "Texas Comptroller, low-producing gas well credit, as site/data/severance_rules.json quotes it; Tax Code Sec. 201.059.", session: "session 46" },
  { key: "network-hour", sets: [E],
    text: "Questions 1 and 2 take the newest hour of the hourly network snapshot in which ERCOT's ties report a flow. A net export is the sum of a balancing authority's tie flows; EIA's regions and country totals are left out, since they repeat the same flows.",
    def: "The snapshot in Supabase Storage, else the committed site/data/grid_network.json; EIA's sign, positive when the reporting balancing authority exports.",
    source: "EIA-930 interchange (eia930_all_interchange); site/lib/network.ts.", session: "sessions 55 and 102" },
  { key: "seller", sets: [E],
    text: "The money questions use the seller's model at its defaults: a plant at ERCOT's hub average selling every MWh at the real-time price, a month counted when it holds 90 percent of its hours (a battery's days), and the battery one cycle a day with perfect foresight, an upper bound.",
    def: "100 MW solar; 100 MW / 400 MWh battery; Lazard's midpoint costs, 60 percent debt at 8 percent over the life.",
    source: "docs/methods/cost_of_power.md (the seller's tab); site/data/merchant_snapshot.json; Lazard, Levelized Cost of Energy+, June 2025.", session: "sessions 51 and 55" },
  { key: "storm-days", sets: [E],
    text: "Question 5 sets what the plant earned over the storm's window against as many normal days: the mean baseline day of the same event times the window's days.",
    def: "As many days as the storm, not one week.", source: "docs/methods/problem_sets.md, ruling 6a of 14 October 2026.", session: "session 288" },
  // session 8901 (chain 507, part C)
  { key: "page-file", sets: [T, S, R, W, Y],
    text: "Every figure of these sets is read from a committed page file of the site, with a key that names the file and the path into it, so the value checker reads the same file again. The figures move when the data machine rebuilds a file, not each hour.",
    def: "The page files as committed; a path that leads to no number gives no figure, and the set says it could not be computed.",
    source: "site/lib/pagefile.ts (the pf| key); docs/methods/problem_sets.md, \"The whole country\".", session: "session 8901" },
  { key: "trade-month", sets: [T],
    text: "The month asked of is the newest month of Tennessee's trade file that had ended when the file was built; a pair's years are those both sides reported in all twelve months; the year of the Mid-Atlantic and Tennessee is the one whose gap is largest in size.",
    def: "The file's own built stamp sets the month; the matrix's months_held and months_in_year set the years.",
    source: "site/data/regions/trade/ten.json and site/data/regions/trade_matrix.json (EIA, Form EIA-930); docs/methods/interchange_pairs.md.", session: "session 8901" },
  { key: "storm-hour", sets: [S],
    text: "A storm question takes a region's highest hour of demand in the event's window, the hour the page's table calls Highest hour, and reads the baseline, generation and flows at that same hour.",
    def: "The first such hour when two are equal; the baseline as the file names it (Elliott: the same weekday 364 and 728 days earlier; Uri: the same calendar days of 2019 and 2020).",
    source: "site/data/regions/events/elliott_2022.json and uri_2021.json (EIA, Form EIA-930); docs/methods/regions_pages.md.", session: "session 8901" },
  { key: "layer-by-id", sets: [R],
    text: "A layer is found in the list of layers by its id; its legend's range is the one the map draws, from the lowest low to the highest high over the layer's parts (the contiguous states, and Alaska and Hawaii where the list gives them); its statistics and its totals are read as the list gives them; no value is read from the map's cells.",
    def: "The list of layers site/data/resources/manifest.json; each layer's unit as its publisher states it.",
    source: "site/data/resources/manifest.json (warehouse/connectors/resource_layers.py); docs/methods/resources.md.", session: "session 8901" },
  { key: "industry-pick", sets: [W],
    text: "The month asked of is the newest the industry file holds a total for, beside the same month a year before; the industries are the first two of the file's ranking; the states' year is the newest both hold.",
    def: "The ranking of the 2022 Manufacturing Energy Consumption Survey by total fuel, at three digits of NAICS.",
    source: "site/data/industry.json (EIA: Monthly Energy Review, 2022 MECS, State Energy Data System); docs/methods/industry_page.md.", session: "session 8901" },
  // session 8905 (chain 590, part C)
  { key: "authority-pick", sets: [Y],
    text: "The worked answers read the Tennessee Valley Authority's file; its largest plant is the first of the file's ten, the retirement and the addition asked about are the rows with the most megawatts, and the partner is the one with the largest gross exchange. The carbon question reads ERCOT's and CAISO's files, since the Tennessee Valley Authority's holds no estimate and says why.",
    def: "The first of equal rows when two are equal; EIA's hourly CO2 estimates cover the seven grid operators and the lower 48 only.",
    source: "site/data/regions/authority/tva.json, erco.json and ciso.json (EIA-860M, Form EIA-930, ba_trade_partners, large_load_public); docs/methods/authority_facts.md.", session: "session 8905" },
  // ready branch of session 11408: the forecast's report card, listed, brings its three choices (they were a waiting set's)
  ...REPORT_DECISIONS,
];

export function ProblemDecisions({ slug, waiting }: { slug?: string; waiting?: ProblemDecision[] }) {
  // session 10404 (chain 720, part E): a waiting set's page draws its own choices, handed in by the page (`waiting`);
  // the index draws the list above alone, so it names no choice of a set it does not list
  const list = slug ? [...PROBLEM_DECISIONS, ...(waiting ?? [])].filter((d) => d.sets.includes(slug)) : PROBLEM_DECISIONS;
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions={slug ?? "problem-sets"}>
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({list.length}): each choice that moves a figure or an answer, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={list.length}>
        {list.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-problems-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
              <span className="block" data-decision-session={d.key}><strong>Made in:</strong> {d.session}.</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
