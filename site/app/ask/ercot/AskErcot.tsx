"use client";
// Energy Research Warehouse (ERW) site, session 92: Ask ERCOT, the reference version (/ask/ercot, in review).
// Session 137: the box and the answer panel are one component that any page can place, with the grid as a parameter
// (components/ask/AskPanel.tsx). What sessions 92 and 121 built here moved there, attribute for attribute: the
// conversation, what is being read while the answer is prepared, the series with its chart and its rows, a refusal's
// nearest tables, a contradicted premise, the follow-up questions. This file keeps the name the page imports.
import { AskPanel, keySeconds, type Context } from "@/components/ask/AskPanel";

export { keySeconds };
export type { Context };

export function AskErcot({ initial = "", context = null }: { initial?: string; context?: Context | null }) {
  return <AskPanel grid="ercot" initial={initial} context={context} />;
}
