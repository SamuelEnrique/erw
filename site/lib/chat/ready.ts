// Energy Research Warehouse (ERW) site, session 156: what the owner ruled on 8 October 2026, as Ask ERCOT's briefing
// and, where the tool can know it, as code.
//
// Pure functions, no imports (Node runs this file as it is, for site/scripts/test-ask-ready.mjs). Three things:
//
//   1. SOURCE PRECEDENCE. "Where two sources hold a figure, the operator's own data wins over a derived file and the
//      answer names both." A rule of the briefing (precedenceRule), and a list of the figures this tool can read from
//      two sources (TWICE_HELD): a result that holds one of them says which source is the operator's and which is
//      derived, and what to read beside it (precedenceOf, set on the tool result by lib/chat/ercot.ts).
//      THE CASE IN HAND, the year's highest hourly demand of ERCOT, 91,134 MW against 91,075 MW:
//        - 91,134 MW is THE OPERATOR'S OWN. It is the highest hour of ERCOT's own hourly load, the column ERCOT of its
//          Hourly Load Data Archives (table ercot_zone_load_hourly, entity ercot:system, tier source, source
//          ercot:load_hist; never a sum made by the ERW), on 22 July 2026, the hour from 17:00 Central daylight time.
//          That table is not in the site's live set, so Ask reads it through the file of the page built from it
//          (site/data/datacenter/index.json, page_file view "demand": the year's highest hour, unchanged).
//        - 91,075 MW is DERIVED. It is grid_stress_yearly's peak_demand_mw (tier derived, source erw:grid_stress): the
//          ERW's yearly figure from EIA's hourly demand (EIA-930), which EIA collects from the balancing authorities
//          and publishes: a second publisher's series, not ERCOT's own file. eia930_demand_growth holds the same
//          series for whole years. Why the two differ by 59 MW is not known to the ERW and is not explained here.
//      So the answer leads with 91,134 MW and names 91,075 MW with its table. Session 143 gave the second alone and
//      session 153 the first alone: each was said with its source, neither named the other.
//   2. WHICH SOURCE HOLDS TEXAS'S CURTAILMENT SHARE (curtailmentSentence): one sentence, taken from the page's Method
//      note (docs/methods/curtailment.md, "Texas: nine days, by the hour"). Session 153's one new failure (p14) read
//      the daily table for a percent it does not hold.
//   3. THE CLOSING WORDS OF A REFUSAL (CLOSING, closingRule, reworded). Until session 153 "this chat speaks for ERCOT
//      only" was true. Since then Ask ERCOT answers for the other grids what four pages show, and the two refusals of
//      that session still closed with the old words. The closing now names the tool as it is.
//
// lib/chat/spec_ercot.json, which warehouse/chat/ercot.py exports, is not touched: the Python reference loop reads no
// page file and still speaks for ERCOT only, so its words stay true where they are.

export const TOOL_NAME = "Ask ERCOT";

// ---------------------------------------------------------------------------------------------------------------------
// 1. source precedence
// ---------------------------------------------------------------------------------------------------------------------

export type Twice = {
  figure: string;
  /** the operator's own figure: where this tool reads it, and whose it is */
  operator: { table: string; tool: "page_file"; view: string; grid: string; field: string; whose: string };
  /** the same figure in tables the ERW derives: read with query */
  derived: { table: string; variable: string; entity: string; whose: string }[];
};
export const TWICE_HELD: Twice[] = [
  {
    figure: "ERCOT's highest hourly demand of a year",
    operator: { table: "site/data/datacenter/index.json", tool: "page_file", view: "demand", grid: "ercot", field: "highest_hour_mw",
      whose: "the operator's own: ERCOT's hourly load from its Hourly Load Data Archives (ercot_zone_load_hourly, entity ercot:system), as the page's file holds it" },
    derived: [
      { table: "grid_stress_yearly", variable: "peak_demand_mw", entity: "iso:ercot", whose: "derived by the ERW from EIA's hourly demand (EIA-930), not ERCOT's own file" },
      { table: "eia930_demand_growth", variable: "peak_demand_mw", entity: "eia930:ERCO", whose: "computed by the ERW from EIA's hourly demand (EIA-930), whole years only, not ERCOT's own file" },
    ],
  },
];
const RULE_SHORT = "The owner's ruling: where two sources hold a figure, the operator's own data wins over a derived file, and the answer names both.";

type Json = Record<string, unknown>;
/** What a tool result that holds a figure held twice is told about it: whose this source is, the other source and how
 * to read it, and which of the two leads. null for every other result. `tool` and `input` are the call's own. */
export function precedenceOf(tool: string, input: Json): Json | null {
  for (const t of TWICE_HELD) {
    const grid = String(input.grid ?? "ercot").toLowerCase();
    if (tool === t.operator.tool && input.view === t.operator.view && grid === t.operator.grid) {
      return { figure: t.figure, this_source: `${t.operator.table} (${t.operator.field}): ${t.operator.whose}`, leads: "this source",
        also_held_in: t.derived.map((d) => ({ table: d.table, variable: d.variable, entity: d.entity, whose: d.whose })),
        rule: `${RULE_SHORT} Lead with this figure; then name the other with its table, read with query in the same turn (${t.derived[0].table}, variable ${t.derived[0].variable}, entity ${t.derived[0].entity}), and say in a few words which is which. Never average the two.` };
    }
    const d = tool === "query" ? t.derived.find((x) => x.table === input.table && x.variable === input.variable) : undefined;
    if (d) {
      return { figure: t.figure, this_source: `${d.table} (${d.variable}): ${d.whose}`, leads: `${t.operator.table}, the operator's own`,
        also_held_in: [{ table: t.operator.table, read_with: `${t.operator.tool} view "${t.operator.view}", grid "${t.operator.grid}": ${t.operator.field} of the year`, whose: t.operator.whose }],
        rule: `${RULE_SHORT} This figure is the derived one: read the operator's own in the same turn and lead with it, then name this one with its table. If the operator's source does not hold the year asked, give this one and say that it is derived.` };
    }
  }
  return null;
}

/** The rule as the briefing gives it. */
export function precedenceRule(): string {
  const t = TWICE_HELD[0];
  return `
- SOURCE PRECEDENCE (the owner's ruling of 8 October 2026). Where two sources you can read hold the same figure, the operator's own data wins over a derived file, and the answer names both. The operator's own is what the grid operator itself published (a table of tier source from the operator, or a page's file built from the operator's own table); a derived figure is one the ERW computed, or one another agency republished. So: lead with the operator's figure and its source; then give the other figure with its table, in the same answer, and say in a few words which is which ("ERCOT's own hourly load", "derived by the ERW from EIA's hourly demand"). Never average the two, never give the derived one alone when the operator's is held, and never call them the same number. A tool result that holds such a figure says so under source_precedence: follow it. The two figures are both tool results of this turn: fetch both in the one reading turn.
- THE CASE IN HAND: ${t.figure} (the peak, "highest hourly demand so far this year"). The operator's own is ${t.operator.tool} view "${t.operator.view}", grid "${t.operator.grid}": ${t.operator.field} of the year, from ERCOT's own hourly load (cite "${t.operator.table}"); say how many hours of the year are held when the year is not whole. The derived one is ${t.derived[0].table}, variable ${t.derived[0].variable}, entity ${t.derived[0].entity}, the row dated 1 January of the year (the ERW's, from EIA's hourly demand). Call both at once, lead with the first, name the second: two figures, each with its source, in at most 50 words. Do not read eia930_all_demand for a year's highest hour: this site holds only its newest weeks.`;
}

// ---------------------------------------------------------------------------------------------------------------------
// 2. which source holds Texas's curtailment share
// ---------------------------------------------------------------------------------------------------------------------

/** One sentence, from the page's Method note (docs/methods/curtailment.md): the page's file is built from the hourly
 * reports and holds the share over whole Central days from 28 September 2026; the daily table holds megawatt-hours by
 * day from 19 September 2026 and no share. */
export function curtailmentSentence(): string {
  return `
- TEXAS'S CURTAILMENT SHARE. The share (the percent of the reported limit that Texas wind and solar output was below) is held only by the curtailment page's file, over its whole Central days from 28 September 2026 (page_file view "share", grid "ercot": cite "site/data/curtailment/ercot.json"), while ercot_wind_solar_hsl_daily holds the megawatt-hours below the limit by day from 19 September 2026 and no share: read the file for a percent or a share, the table for a day's megawatt-hours, and never make a percent yourself from two sums or with compare.`;
}

// ---------------------------------------------------------------------------------------------------------------------
// 3. the closing words of a refusal
// ---------------------------------------------------------------------------------------------------------------------

/** The sentence a refusal about another grid closes with: the tool by its own name, as it now is. */
export const CLOSING = `${TOOL_NAME} answers for the Texas grid, and for the other grids only what four pages of this site show: curtailment and free energy, what a datacenter pays, the capture price and the resource layers.`;
/** What the closing may no longer say. */
export const OLD_CLOSING = /(speaks|answers) for ERCOT only|ERCOT[- ]only (chat|panel|tool)/i;

/** The two sentences of the older prompts that say the chat speaks for one grid only, each with what replaces it. The
 * first is rule 3 of the exported spec (lib/chat/spec_ercot.json), the second the answer panel's (lib/chat/panel.ts). */
export function oldWords(iso: string): [string, string][] {
  return [
    [`This chat speaks for ${iso} only: for another grid, say so and that the general chat at /ask covers the whole warehouse.`,
      `For another grid, close as THE CLOSING WORDS OF A REFUSAL below say.`],
    [`This panel answers for ${iso} only.`,
      `This panel answers for ${iso}, and for the other grids only what FOUR PAGES OF THIS SITE below show; for everything else about another grid, refuse and close as THE CLOSING WORDS OF A REFUSAL below say.`],
  ];
}
/** The prompt with the two sentences reworded. `missing`: the sentences that were not found (a test holds it empty, so
 * that an edit of the older prompts cannot leave the old words standing unseen). */
export function reworded(system: string, iso: string): { system: string; missing: string[] } {
  const missing: string[] = [];
  let out = system;
  for (const [old, now] of oldWords(iso)) {
    if (!out.includes(old)) { missing.push(old); continue; }
    out = out.split(old).join(now);
  }
  return { system: out, missing };
}

export function closingRule(): string {
  return `
- THE CLOSING WORDS OF A REFUSAL. When you refuse a question about another grid or another country, never write that this chat, this panel or this tool "speaks for ERCOT only" or "answers for ERCOT only": since four pages were added that is not true. Say first what was asked about and why it is not answered (for a table held internally, "held, not shown" and why; for MISO, "paused while terms are reviewed"; for PJM, "licensed source needed"). Then close with this sentence, as it stands: "${CLOSING}" Then say where to look: the grid's own page, /grid/<slug>, when it is one of pjm, caiso, miso, nyiso, isone, spp, and the general chat at /ask, which covers the whole warehouse. A refusal for another reason (licensed data, a company's accounts, a forecast, advice) closes as before, without this sentence.`;
}

/** Everything of this file the briefing is given, in one block, after the guide of the four pages. */
export function readyGuide(): string {
  return `

SOURCES AND CLOSING WORDS (session 156, the owner's rulings of 8 October 2026). These lines add to the rules above and govern where they differ.${precedenceRule()}${curtailmentSentence()}${closingRule()}`;
}
