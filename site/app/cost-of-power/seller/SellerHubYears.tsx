"use client";
// Session 162: (b) the capture price by hub and year on /cost-of-power/seller: one table, every public hub and zone
// of every grid as rows, the years as columns, solar or wind and day-ahead or real time by a switch, sorted by a
// click on a year. Every value arrives from the server (page.tsx; lib/capture.ts, hubYears, over
// data/seller/capture.json); each cell answers the mouse with the hub's simple average, the capture ratio, the hours
// held of the year and the source. A year not held is a short placeholder with its reason; a partial year says so.
// MISO and PJM are rows of words. No method on the face: docs/methods/cost_of_power.md, "Session 162".
import { useMemo, useState } from "react";

/** A held cell: [capture price, simple average, hours used, months counted]; a cell not held: the index of its reason. */
export type HyCell = [number, number, number, number] | number;
export type HyRow = {
  grid: string; gridName: string; id: string; name: string; main: boolean; src: { rt?: string; da?: string };
  c: Record<"rt" | "da", Record<"solar" | "wind", HyCell[]>>;
  t: Record<"rt" | "da", Record<"solar" | "wind", [number, number, number, string, string] | number>>;
};
export type HyTable = { years: string[]; rows: HyRow[]; whys: string[]; blank: { id: string; name: string; words: string; why: string }[]; generation: Record<string, string> };

const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const whole = (v: number) => v.toLocaleString("en-US");
const hoursIn = (y: string) => { const n = Number(y); return (n % 4 === 0 && n % 100 !== 0) || n % 400 === 0 ? 8784 : 8760; };
const MARKET = { da: "Day-ahead", rt: "Real time" } as const;
const FUEL = { solar: "Solar", wind: "Wind" } as const;
const shade = (ratio: number) => (ratio < 100 ? `rgba(140,21,21,${Math.min(0.42, ((100 - ratio) / 100) * 0.7).toFixed(3)})` : `rgba(46,45,41,${Math.min(0.2, ((ratio - 100) / 100) * 0.4).toFixed(3)})`);

export function SellerHubYears({ table, fuel0, hub }: { table: HyTable; fuel0: "solar" | "wind"; hub: string }) {
  const [fuel, setFuel] = useState<"solar" | "wind">(fuel0);
  const [market, setMarket] = useState<"rt" | "da">("da");
  const [sort, setSort] = useState<{ col: number; down: boolean } | null>(null);  // col: a year's index; years.length is the last twelve months
  const n = table.years.length;
  const rows = useMemo(() => {
    if (!sort) return table.rows;
    const value = (r: HyRow) => { const c = sort.col === n ? r.t[market][fuel] : r.c[market][fuel][sort.col]; return typeof c === "number" ? null : c[0]; };
    return [...table.rows].sort((a, b) => {
      const x = value(a), y = value(b);
      if (x === null || y === null) return x === null ? (y === null ? 0 : 1) : -1;
      return sort.down ? y - x : x - y;
    });
  }, [table.rows, sort, market, fuel, n]);
  const click = (col: number) => setSort((s) => (!s || s.col !== col ? { col, down: true } : s.down ? { col, down: false } : null));
  const arrow = (col: number) => (sort && sort.col === col ? (sort.down ? " ↓" : " ↑") : "");
  const pick = <T extends string>(now: T, set: (v: T) => void, options: Record<T, string>, name: string) => (
    <span className="inline-flex items-baseline gap-1" role="group" aria-label={name}>
      {(Object.keys(options) as T[]).map((k) => (
        <button key={k} type="button" aria-pressed={now === k} onClick={() => set(k)} data-hy-switch={`${name}|${k}`}
          className={`border px-2 py-0.5 text-xs ${now === k ? "border-accent bg-accent text-white" : "border-rule bg-white"}`}>{options[k]}</button>
      ))}
    </span>
  );
  const missing = (why: string) => <span className="cursor-help whitespace-nowrap border-b border-dotted border-muted text-[11px] italic text-muted" title={why} data-missing="1">not held</span>;
  const source = (r: HyRow) => `Generation: ${table.generation[r.grid]}, the grid's whole ${fuel} fleet by hour. Prices: ${r.src[market] ?? "none"}.`;
  return (
    <div data-hub-years="1" data-hy-fuel={fuel} data-hy-market={market}>
      <p className="mb-2 flex flex-wrap items-baseline gap-x-4 gap-y-1 text-xs">
        {pick(fuel, setFuel, FUEL, "fuel")}
        {pick(market, setMarket, MARKET, "prices")}
        <span className="text-muted">USD per MWh. A click on a year sorts by it.</span>
      </p>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 700 }}>
          <caption className="sr-only">{`Capture price of ${fuel} by hub and year, ${MARKET[market].toLowerCase()} prices, USD per MWh`}</caption>
          <thead>
            <tr className="bg-accent text-white">
              <th scope="col" className="px-2 py-1.5 font-normal"><button type="button" onClick={() => setSort(null)} className="text-left" title="The grids in the page's order, each grid's main hub first">Hub or zone</button></th>
              {table.years.map((y, i) => (
                <th key={y} scope="col" className="px-1.5 py-1.5 text-right font-normal" aria-sort={sort?.col === i ? (sort.down ? "descending" : "ascending") : undefined}>
                  <button type="button" onClick={() => click(i)} data-hy-sort={y} title={`Sort by ${y}`}>{y}{arrow(i)}</button>
                </th>
              ))}
              <th scope="col" className="px-1.5 py-1.5 text-right font-normal"><button type="button" onClick={() => click(n)} data-hy-sort="twelve" title="Sort by the last twelve months">Last 12 months{arrow(n)}</button></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const t = r.t[market][fuel];
              return (
                <tr key={`${r.grid}|${r.id}`} className={`border-b border-rule ${r.id === hub ? "bg-paper font-semibold" : ""}`} data-hy-row={`${r.grid}|${r.id}`}>
                  <th scope="row" className="px-2 py-1 font-normal leading-tight" style={{ maxWidth: 200 }}><span className="text-xs text-muted">{r.gridName}</span> {r.name}</th>
                  {table.years.map((y, i) => {
                    const c = r.c[market][fuel][i];
                    if (typeof c === "number") return <td key={y} className="px-1.5 py-1 text-right">{missing(`${r.name} (${r.gridName}), ${y}, ${fuel}, ${MARKET[market].toLowerCase()}. ${table.whys[c]}`)}</td>;
                    const [price, flat, hours, months] = c;
                    const ratio = flat > 0 ? (100 * price) / flat : null;
                    const partial = months < 12;
                    const title = `${r.name} (${r.gridName}), ${y}, ${fuel}, ${MARKET[market].toLowerCase()}: capture price ${two(price)} USD per MWh. The hub's simple average over the same hours: ${two(flat)}. Capture ratio: ${ratio === null ? "none, the average is not above zero" : `${ratio.toFixed(1)} percent`}. Hours held: ${whole(hours)} of the year's ${whole(hoursIn(y))}${partial ? `, a partial year, ${months} of 12 months counted` : ""}. ${source(r)}`;
                    return (
                      <td key={y} className={`cursor-help px-1.5 py-1 text-right ${partial ? "text-muted" : ""}`} title={title} style={ratio === null ? undefined : { backgroundColor: shade(ratio) }}>
                        <span data-hy={`${r.id}|${market}|${fuel}|${y}`}>{two(price)}</span>
                        {partial ? <span className="block text-[10px] italic leading-none" data-hy-partial="1">partial</span> : null}
                      </td>
                    );
                  })}
                  <td className="px-1.5 py-1 text-right">
                    {typeof t === "number" ? missing(`${r.name} (${r.gridName}), last twelve months, ${fuel}, ${MARKET[market].toLowerCase()}. ${table.whys[t]}`) : (
                      <span className="cursor-help" data-hy={`${r.id}|${market}|${fuel}|twelve`}
                        title={`${r.name} (${r.gridName}), ${t[3]} to ${t[4]}, ${fuel}, ${MARKET[market].toLowerCase()}: capture price ${two(t[0])} USD per MWh. The hub's simple average over the same hours: ${two(t[1])}. Capture ratio: ${t[1] > 0 ? `${((100 * t[0]) / t[1]).toFixed(1)} percent` : "none"}. Hours held: ${whole(t[2])}. ${source(r)}`}>{two(t[0])}</span>
                    )}
                  </td>
                </tr>
              );
            })}
            {table.blank.map((b) => (
              <tr key={b.id} className="border-b border-rule text-muted" data-hy-blank={b.id}>
                <th scope="row" className="px-2 py-1 font-normal">{b.name}</th>
                <td colSpan={n + 1} className="px-2 py-1"><span className="cursor-help border-b border-dotted border-muted text-xs italic" title={b.why} data-missing="1">{b.words}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-1 flex flex-wrap gap-x-4 text-xs text-muted">
        <span><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5" style={{ backgroundColor: shade(60) }} />Below the hub&apos;s simple average</span>
        <span><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5" style={{ backgroundColor: shade(140) }} />Above it</span>
        <span>The row in bold is the hub chosen.</span>
      </p>
    </div>
  );
}
