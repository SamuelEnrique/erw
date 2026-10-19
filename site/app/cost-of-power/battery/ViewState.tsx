"use client";
// Session 296: the reader's view of /cost-of-power/battery (lib/battery/view.ts), held above the page's sections with
// the two scenarios (Scenarios.tsx, BatteryDecisions) and written into the address with them.
import { createContext, useContext } from "react";
import type { View } from "@/lib/battery/view";

export type HeldView = { v: View; set: (p: Partial<View>) => void };
export const ViewCtx = createContext<HeldView | null>(null);
export function useView(): HeldView {
  const c = useContext(ViewCtx);
  if (!c) throw new Error("the view is read outside BatteryDecisions");
  return c;
}
