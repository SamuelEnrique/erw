// Energy Research Warehouse (ERW) site, session 238: what the Research page (/research; Automated
// Analysis until session 238) derives for its findings library and its two charts on top. Server only: it reads the
// committed cards, the files beside them and the bundled Roundups. Nothing here computes a number.
//
// A finding's grids and topics. A card carries no "grid" and no "topic" field, so both are read from fields it does
// carry, by the rules below, and from nothing else:
//   grids   the seven grid names (ERCOT, CAISO, PJM, MISO, SPP, NYISO, ISO-NE) found in the card's own `tables` (a
//           table's name starts with the grid: ercot_, caiso_, nyiso_, isone_, ...), in the words of its inputs
//           (`inputs_words`, for example "ERCOT, CAISO, NYISO, ISO-NE, SPP") and in the names of its chart's series and categories (`chart.series`, `chart.x`);
//           a grid the card itself lists as not held (`placeholders`) is left out. A card that names none of the seven
//           is filed under "Not one grid" (the interconnection queue of every region, a storm across balancing areas).
//   topics  the kinds of table the card read (`tables`): each table gives one topic, by the first rule of TOPIC_RULES
//           its name matches. A topic is therefore a statement about the data a finding used, not a judgment of
//           what it is about.
import "server-only";
import { DOCS, weeklyWeeks } from "@/lib/markdown";
import { loadCard, type Card } from "@/lib/findings";

export { GRIDS, NO_GRID, OTHER_TOPIC, TOPIC_RULES, gridLabel, gridsOf, topicLabel, topicsOf } from "./researchrules";
import { chartSectionOf, chosenCardOf } from "./researchrules";

export type Held = { csv: boolean; python: boolean; stata: boolean };
/** Which of a card's three files the site holds (public/findings/, listed at build by scripts/build-content.mjs): a
 *  file that is not there is named "not held". */
export function filesHeld(card: Card): Held {
  const held = new Set(DOCS.findings_files ?? []);
  const has = (f?: string) => Boolean(f) && held.has(f as string);
  return { csv: has(card.downloads?.csv), python: has(card.downloads?.python), stata: has(card.downloads?.stata) };
}

/** The Roundup's own section "ERW's Chart of the Week" of one week, as its markdown; "" when the week has none. */
export function roundupChartSection(week: string): string {
  return chartSectionOf(DOCS.weeklies?.[week] ?? "");
}

export type WeekChart = { week: string; card: Card | null; chosen: boolean };
/** The chart the Roundup of a week carried: a finding's card when one was chosen for it (the section's picture is the
 *  card's, docs/analysis/findings/<card>_1600x900.png) and the site holds that card; else the rule's pick of the week. */
export function roundupChart(week: string): WeekChart {
  const id = chosenCardOf(roundupChartSection(week));
  return { week, card: id ? loadCard(id) : null, chosen: Boolean(id) };
}

/** The newest week whose Roundup holds a chart section; else the newest week with a chart of the rule; else null. */
/** The ISO week of a day, "2026-W47". */
export function isoWeekOf(d: Date): string {
  const t = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  const dow = t.getUTCDay() || 7;
  t.setUTCDate(t.getUTCDate() + 4 - dow);   // the week's Thursday names its year
  const y = t.getUTCFullYear();
  const w = Math.ceil(((t.getTime() - Date.UTC(y, 0, 1)) / 86400000 + 1) / 7);
  return `${y}-W${String(w).padStart(2, "0")}`;
}
/** Session 7564 (the Research read, row 3): the weekly chart's heading. A Roundup's chart is of the week just ended, so
 *  "This week's chart" stands while the newest is of this ISO week or the one before; an older one (the Roundup paused,
 *  2026-W45 on 17 November 2026) is named for what it is. */
export function weekChartTitle(week: string | null, now: Date = new Date()): string {
  if (!week) return "This week's chart";
  const prev = isoWeekOf(new Date(now.getTime() - 7 * 86400000));
  return week >= prev ? `This week's chart, ${week}` : `The newest weekly chart, ${week}: none since`;
}

export function newestChartWeek(): string | null {
  return weeklyWeeks().find((w) => roundupChartSection(w)) ?? Object.keys(DOCS.analysis?.weeks ?? {}).sort().reverse()[0] ?? null;
}
