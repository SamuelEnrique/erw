// Energy Research Warehouse (ERW) site, session 412 (the accessibility pass, docs/reviews/accessibility-2026-10-20.md).
import type { ReactNode } from "react";

/** A table cell with nothing in it. The shared tables (components/tool/ToolPage.tsx ToolTable, components/svgchart.tsx
 *  DataTable) draw such a header cell (the corner over a column of names, a row that is not ranked) as a plain cell,
 *  not an empty header, so a screen reader is not handed a header with no name (AccessLint, adaptable/empty-table-header).
 *  It keeps the first column's place when the table scrolls (app/tokens.css, data-empty-head). */
export const emptyCell = (c: ReactNode): boolean => c === "" || c === null || c === undefined || c === false;

/** Session 412: the attributes a shared table's scrolling frame is drawn with on the server, so that before the page's
 *  script runs (and without it) a keyboard can reach and scroll a table wider than its frame (WCAG 2.1.1): one stop of
 *  the keyboard, a region named by the table's caption. Once the script runs, components/ScrollRegions.tsx takes the
 *  three marks back from a frame that does not scroll or that holds a link or a control, so a table that fits is no
 *  extra stop. */
export function scrollRegion(name: string | undefined) {
  return { tabIndex: 0, role: "region", "aria-label": name || "Table", "data-scroll-focus": "1", "data-scroll-role": "1", "data-scroll-label": "1" } as const;
}
