"use client";
// Session 8602 (chain 504): each balancing authority's EIA region, handed from the server (components/grid/NetworkView.tsx,
// from the whole country's index, lib/gridregions.ts regionOfBa) to the network component, which reads it for the
// panel's line "EIA region" and the map's hover. A context, so the line that draws the network keeps the props it has
// always had. With no index on the server the value is undefined, and the panel and the hover are as they were.
import { createContext, useContext, type ReactNode } from "react";

export type BaRegionsMap = Record<string, { code: string; name: string }>;
const BaRegionsContext = createContext<BaRegionsMap | undefined>(undefined);

export function BaRegions({ value, children }: { value: BaRegionsMap | undefined; children: ReactNode }) {
  return <BaRegionsContext.Provider value={value}>{children}</BaRegionsContext.Provider>;
}
export const useBaRegions = () => useContext(BaRegionsContext);
