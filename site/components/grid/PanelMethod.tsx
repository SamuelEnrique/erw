// Energy Research Warehouse (ERW) site, session 1184 (chain 091): the line at the foot of a Grid panel that links its
// method, the section of its note that defines it (lib/gridAnchors.ts, METHOD_<PANEL>, gathered in GRID_METHOD), as the
// older blocks' source lines end with "Method". The link itself is written in the panel's own file,
// <Link href={METHOD_<PANEL>}>Method: ..., so scripts/check-methods.mjs reads it as the page's note where it is; this is
// only its line, named for the panel (data-grid-method), which scripts/test-grid-files.mjs finds in each drawn panel.
import type { ReactNode } from "react";
import type { GridAnchorKey } from "@/lib/gridAnchors";

export function PanelMethod({ at, children }: { at: GridAnchorKey; children: ReactNode }) {
  return <p className="mt-1 text-xs text-muted" data-grid-method={at}>{children}.</p>;
}
