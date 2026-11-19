"use client";
// Session 8013 (chain 505, part E3): the "Price" color of the Grid tool's map of balancing authorities. The carbon color
// stays what opens (Samuel's ruling); price is a choice the reader makes. Each area takes its grid's main hub's day-ahead
// figure for the measure chosen, from data/regions/prices_map.json (warehouse/derived/prices_map.py, contract section
// 13), read from /grid/prices-map when the reader first chooses price. A grid held for a license is a blank whose hover
// says "license needed"; an area with no public price is a blank that says so. The flows are drawn over it as before.
import { useEffect, useState } from "react";

export type PriceMeasure = "day_avg" | "day_on_peak" | "day_off_peak" | "day_spread_top4_bottom4" | "avg_30d" | "avg_12m" | "negative_share_30d_pct" | "negative_share_12m_pct";
export const PRICE_MEASURES: [PriceMeasure, string, string][] = [
  ["day_avg", "Day-ahead, the newest day", "USD/MWh"],
  ["day_on_peak", "On-peak hours of that day", "USD/MWh"],
  ["day_off_peak", "Off-peak hours of that day", "USD/MWh"],
  ["day_spread_top4_bottom4", "That day's four dearest less four cheapest hours", "USD/MWh"],
  ["avg_30d", "Average over 30 days", "USD/MWh"],
  ["avg_12m", "Average over twelve months", "USD/MWh"],
  ["negative_share_30d_pct", "Hours below zero, 30 days", "percent"],
  ["negative_share_12m_pct", "Hours below zero, twelve months", "percent"],
];
type BaPrice = { grid: string; state: "shown" | "held" | "paused"; why?: string; hub?: string; day?: string } & Partial<Record<PriceMeasure, number | null>> & Record<string, unknown>;
export type PricesMap = { built: string; bas: Record<string, BaPrice> };

export function usePricesMap(on: boolean) {
  const [state, setState] = useState<PricesMap | null | "none">(null);
  useEffect(() => {
    if (!on || state !== null) return;
    let live = true;
    fetch("/grid/prices-map").then((r) => (r.ok ? r.json() : null)).then((j) => { if (live) setState(j && j.bas ? (j as PricesMap) : "none"); }).catch(() => { if (live) setState("none"); });
    return () => { live = false; };
  }, [on, state]);
  return state;
}

export function priceValue(m: PricesMap, id: string, k: PriceMeasure): number | null {
  const b = m.bas[id];
  const v = b && b.state === "shown" ? b[k] : null;
  return typeof v === "number" ? v : null;
}
export function priceRange(m: PricesMap, k: PriceMeasure): [number, number] | null {
  const vs = Object.keys(m.bas).map((id) => priceValue(m, id, k)).filter((v): v is number => v !== null);
  return vs.length ? [Math.min(...vs), Math.max(...vs)] : null;
}
const unitOf = (k: PriceMeasure) => PRICE_MEASURES.find((x) => x[0] === k)![2];
const fmt = (v: number, k: PriceMeasure) => (unitOf(k) === "percent" ? `${v.toFixed(2)} percent of hours` : `${v.toFixed(2)} USD/MWh`);

/** The hover line of an area while the map is colored by price. */
export function priceLine(m: PricesMap, id: string, k: PriceMeasure): string {
  const b = m.bas[id];
  if (!b) return "Price: no public hub or zone price of this authority in the warehouse";
  if (b.state === "held") return "Price: license needed";
  if (b.state === "paused") return `Price: not shown (${b.grid}'s terms are under review)`;
  const v = priceValue(m, id, k);
  const why = (k.endsWith("30d") || k.endsWith("30d_pct") ? b.window_30d_why : k.endsWith("12m") || k.endsWith("12m_pct") ? b.window_12m_why : k === "day_on_peak" ? b.day_on_peak_why : null) as string | null | undefined;
  return v === null ? `Price: not held (${why ?? "no figure for this measure"})` : `Price: ${fmt(v, k)} at ${b.hub?.split(":")[1] ?? "its main hub"}, day-ahead${k.startsWith("day") ? `, ${b.day}` : ""}`;
}

export function PriceControls({ on, setOn, measure, setMeasure, m }: { on: boolean; setOn: (v: boolean) => void; measure: PriceMeasure; setMeasure: (k: PriceMeasure) => void; m: PricesMap | null | "none" }) {
  const r = m && m !== "none" ? priceRange(m, measure) : null;
  const held = m && m !== "none" ? Object.values(m.bas).filter((b) => b.state !== "shown").map((b) => b.grid) : [];
  return (
    <div className="mb-2 flex flex-wrap items-center gap-2 text-sm" data-map-color={on ? "price" : "carbon"}>
      <span className="text-muted">Color the areas by:</span>
      <span role="group" aria-label="Color the areas by" className="inline-flex">
        <button type="button" aria-pressed={!on} onClick={() => setOn(false)} className={`border px-2 py-0.5 ${!on ? "border-ink bg-ink text-white" : "border-rule text-ink"}`}>Carbon</button>
        <button type="button" aria-pressed={on} onClick={() => setOn(true)} className={`border px-2 py-0.5 ${on ? "border-ink bg-ink text-white" : "border-rule text-ink"}`} data-map-price-switch="1">Price</button>
      </span>
      {on ? (
        <>
          <select value={measure} onChange={(e) => setMeasure(e.target.value as PriceMeasure)} className="border border-rule bg-panel px-2 py-0.5 text-sm" aria-label="The price measure" data-map-price-measure={measure}>
            {PRICE_MEASURES.map(([k, label]) => <option key={k} value={k}>{label}</option>)}
          </select>
          <span className="text-xs text-muted" data-map-price-range={r ? `${r[0]}-${r[1]}` : "none"}>
            {m === null ? "Reading the prices..." : m === "none" ? "The price file is not on the site yet." : r ? <>Green {fmt(r[0], measure)} to red {fmt(r[1], measure)}, each grid&apos;s main hub (the price board&apos;s). </> : "No area holds this measure. "}
            {held.length ? <span className="cursor-help border-b border-dotted border-muted" title="A grid whose prices docs/licenses.md holds for a license is drawn blank, its hover saying license needed; MISO is paused; an authority with no public hub price in the warehouse is blank too.">Blank: {held.join(", ")} (license needed or paused), and areas with no public price</span> : null}
          </span>
        </>
      ) : null}
    </div>
  );
}
