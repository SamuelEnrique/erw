// Energy Research Warehouse (ERW) site, session 1171 (chain 078): the Grid pack's blind spot 9 (docs/reviews/packs/grid.md,
// section 6), revisions. EIA calls EIA-930's hourly data preliminary and revises an hour after it first publishes it; on
// 13 October 2026 one revised hour moved two of MISO's figures between a page's read and the value checker's. Each tab of
// the Grid tool (Network, Mix, Clean, Gravity) says so in its data line, in these words and no others, so the four cannot
// drift. The page's drawing time is written into the words where the tab already says it (the Network and Gravity tabs,
// under the network: "hours before this page was drawn"); every tab carries it as data-eia930-drawn, which
// site/scripts/check-values.mjs reads to tell a revised hour from a wrong figure (site/scripts/check-revised.mjs, the rule
// in docs/methods/grid_network.md, "Revisions, said and checked").

/** The words before the drawing time. */
const HEAD = "EIA-930's hourly figures are preliminary and EIA revises them: a figure here is the value the warehouse held when this page was drawn";
/** The words after it. */
const TAIL = ", so a later read of the same hour can differ.";

/** The attribute that carries the page's drawing time (an ISO timestamp, UTC) on the sentence's element. */
export const DRAWN_ATTR = "data-eia930-drawn";

/** The sentence, with the drawing time ("2026-10-24 09:15 UTC") after "drawn" when one is given. */
export function preliminaryText(drawnUtc?: string | null): string {
  return `${HEAD}${drawnUtc ? ` (${drawnUtc})` : ""}${TAIL}`;
}

/** The sentence without a time: the words every tab shares. */
export const EIA930_PRELIMINARY = preliminaryText();

/** A drawing time as the tabs write their clocks: "YYYY-MM-DD HH:MM UTC". */
export function drawnUtc(at: Date): string {
  return `${at.toISOString().slice(0, 16).replace("T", " ")} UTC`;
}
