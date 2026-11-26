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

/** Session 10218 (docs/reviews/prices-model-audit-2026-11-26.md, finding 5): the day the colors are of, and when the
 *  file was built. "The newest day" is the newest whole day the file held when it was built: on 26 November 2026 the
 *  file of 19 November colored the map by 16 November, and the legend gave no date (only each area's hover did). */
export function whenOf(m: PricesMap, k: PriceMeasure): string {
  const days = Object.entries(m.bas).filter(([id, b]) => typeof b.day === "string" && priceValue(m, id, k) !== null).map(([, b]) => b.day as string);
  return [...new Set(days)].sort().join(",");
}
export function whenWords(m: PricesMap, k: PriceMeasure): string {
  const days = whenOf(m, k).split(",").filter(Boolean);
  const built = (m.built ?? "").slice(0, 10);
  const span = k.startsWith("day") ? "day-ahead of" : `day-ahead, the ${k.includes("30d") ? "30" : "365"} days to`;
  const when = days.length === 0 ? "" : days.length === 1 ? `${span} ${days[0]}` : `${span} each area's own day (${days.join(", ")}: the colors set different days side by side)`;
  return `${when}${when && built ? ", " : ""}${built ? `from the price file built ${built}` : ""}`;
}
const fmt = (v: number, k: PriceMeasure) => (unitOf(k) === "percent" ? `${v.toFixed(2)} percent of hours` : `${v.toFixed(2)} USD/MWh`);

/** The hover line of an area while the map is colored by price. */
export function priceLine(m: PricesMap, id: string, k: PriceMeasure): string {
  const b = m.bas[id];
  if (!b) return "Price: no public hub or zone price of this authority in the warehouse";
  if (b.state === "held") return "Price: license needed";
  if (b.state === "paused") return `Price: not shown (${b.grid}'s terms are under review)`;
  const v = priceValue(m, id, k);
  const why = (k.endsWith("30d") || k.endsWith("30d_pct") ? b.window_30d_why : k.endsWith("12m") || k.endsWith("12m_pct") ? b.window_12m_why : k === "day_on_peak" ? b.day_on_peak_why : null) as string | null | undefined;
  // Session 9601 (chain 620): a figure over thirty days or twelve months names its window, the days ending on the
  // file's day (docs/methods/prices_map.md). Without it the map's "twelve months" (ERCOT 34.86, the 365 days to 16
  // November 2026) read as a different figure from /prices/compare's (34.59, the twelve calendar months to October).
  const span = k.startsWith("day") ? `, ${b.day}` : b.day ? `, the ${k.includes("30d") ? "30" : "365"} days to ${b.day}` : "";
  return v === null ? `Price: not held (${why ?? "no figure for this measure"})` : `Price: ${fmt(v, k)} at ${b.hub?.split(":")[1] ?? "its main hub"}, day-ahead${span}`;
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
            {m === null ? "Reading the prices..." : m === "none" ? "The price file is not on the site yet." : r ? <>Green {fmt(r[0], measure)} to red {fmt(r[1], measure)}, each grid&apos;s main hub (the price board&apos;s), <span data-map-price-when={whenOf(m, measure)}>{whenWords(m, measure)}</span>. </> : "No area holds this measure. "}
            {held.length ? <span className="cursor-help border-b border-dotted border-muted" title="A grid whose prices docs/licenses.md holds for a license is drawn blank, its hover saying license needed; MISO is paused; an authority with no public hub price in the warehouse is blank too.">Blank: {held.join(", ")} (license needed or paused), and areas with no public price</span> : null}
          </span>
          <details className="w-full text-xs" data-decisions="map-price">
            <summary className="cursor-pointer text-accent">Decisions behind the price colors (session 8013)</summary>
            <ul className="mt-1 list-disc space-y-0.5 pl-5">
              {PRICE_DECISIONS.map((d) => <li key={d.key} data-decision={d.key} title={`Default: ${d.def}. Source: ${d.source}`} className="cursor-help">{d.text}</li>)}
            </ul>
          </details>
        </>
      ) : null}
    </div>
  );
}

/** The choices that move the price colors, each with its default and source (the form of the five tools' decisions). */
export const PRICE_DECISIONS = [
  { key: "main-hub", text: "An authority's area takes its grid's main hub, the one the price board shows first.", def: "the main hub of site/data/markets.json (ERCOT HB_HUBAVG, CAISO SP15, SPP North)", source: "warehouse/derived/price_board.py, MAIN" },
  { key: "day-ahead", text: "Day-ahead prices only: the market a buyer locks in a day before.", def: "day-ahead", source: "docs/methods/prices_map.md" },
  { key: "newest-day", text: "The day is the newest local day before the file was built that holds every hour.", def: "the newest whole day held; the hover names it", source: "warehouse/derived/prices_map.py" },
  { key: "on-peak", text: "On-peak hours begin 06:00 to 21:00 local, Monday to Friday (CAISO to Saturday), NERC holidays off.", def: "the price board's rule", source: "warehouse/derived/price_board.py, is_peak" },
  { key: "coverage", text: "A 30-day or twelve-month figure is drawn only when 95 percent of its hours are held; otherwise the area is blank and the hover gives the count.", def: "95 percent", source: "warehouse/derived/price_compare.py, NEAR_HOURS" },
  { key: "held", text: "A grid held for a license is blank with \"license needed\"; MISO is paused; an authority with no public hub price is blank.", def: "no figure is drawn for them", source: "docs/licenses.md and warehouse/metadata/license_status.py" },
  { key: "scale", text: "Green is the cheapest area shown and red the dearest, for the measure chosen; the legend gives both ends.", def: "the carbon color's own scale", source: "app/network/Network.tsx, colorOf" },
];
