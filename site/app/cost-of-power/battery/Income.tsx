"use client";
// Session 296 (the owner's ruling of 15 October 2026, item 6): the income table of /cost-of-power/battery. Its
// columns are the calendar years the chart draws, the last twelve months, and one window the reader sets with two
// year pickers (no typing), leaving out, by a checkbox each, the stress events of the grid shown (ERCOT: Uri, Elliott,
// the 2023 heat; CAISO: the days of its own notices). No window is the ERW's: the columns "last three full years",
// "every year held" and "without the one month" are gone; the reader's window opens on every year held with nothing
// left out, which is the old average, so every figure at the default is what it was and carries the key it carried
// (bs|<inputs>|avg:<stream>). A year column carries yr:<year>:<stream>, a window the reader set win:<from>:<to>:<left
// out>:<stream>, each recomputed by scripts/check-values.mjs from its own read (lib/batterystack.ts, stat). The
// units toggle (item 2) shows the same figures per kW (the _kw keys). A Chart | Table toggle (item 9) draws the same
// columns as stacked bars. Computed from the months the page holds; nothing is requested.
import { useMemo, type ReactNode } from "react";
import { SeriesChart } from "@/components/tool/SeriesChart";
import { Tip, ToolTable } from "@/components/tool/ToolPage";
import { averageYear, lastTwelve, sumOf, usdShort, windowAverage, windowKey, yearStream, years, type EventMonth, type Inputs, type Month } from "@/lib/batterystack";
import { windowOf } from "@/lib/battery/view";
import { U, V } from "./nums";
import { useView } from "./ViewState";

const shortMonth = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });
export type EventChoice = { event: string; short: string; label: string };
type Col = { key: string; head: string; sub: string; usd: (s: string) => string; kw: (s: string) => string; value: (s: string) => number | null; partial?: boolean; label: string };

export function Income({ ms, x, pre, gridName, products, capacityWords, events, em }: {
  ms: Month[]; x: Inputs; pre: string; gridName: string; products: { key: string; label: string }[]; capacityWords: string;
  events: EventChoice[]; em: Record<string, Record<string, EventMonth>>;
}) {
  const { v, set } = useView();
  const held = useMemo(() => years(ms), [ms]);
  const heldYears = held.map((y) => y.y);
  const win = windowOf(v, heldYears);
  const out = v.out.filter((id) => events.some((e) => e.event === id));
  const whole = !!win && win.from === heldYears[0] && win.to === heldYears[heldYears.length - 1] && out.length === 0;
  const l12 = lastTwelve(ms);
  const scaled = (t: number | null) => (t === null ? null : Math.round(t * x.mw));
  const perKw = (t: number | null) => (t === null ? null : t / 1000);
  const cols: Col[] = [];
  if (l12) cols.push({ key: "l12", label: "Last twelve months", head: "Last twelve months", sub: `${shortMonth(l12[0].m)} to ${shortMonth(l12[11].m)}`,
    usd: (s) => `l12:${s}`, kw: (s) => `l12_kw:${s}`, value: (s) => sumOf(l12, s) });
  for (const y of held) cols.push({ key: y.y, label: y.y, head: y.y, sub: y.complete ? "calendar year" : `${y.months} ${y.months === 1 ? "month" : "months"}`, partial: !y.complete,
    usd: (s) => `yr:${y.y}:${s}`, kw: (s) => `yr_kw:${y.y}:${s}`, value: (s) => yearStream(ms, y.y, s) });
  if (win) {
    const wk = windowKey(win.from, win.to, out);
    const outWords = out.length ? `, without ${out.map((id) => events.find((e) => e.event === id)?.short ?? id).join(", ")}` : "";
    cols.push({ key: "win", label: "Your window", head: "Your window, a year", sub: `${win.from === win.to ? win.from : `${win.from} to ${win.to}`}${outWords}: the average year`,
      usd: (s) => (whole ? `avg:${s}` : `win:${wk}:${s}`), kw: (s) => (whole ? `avg_kw:${s}` : `win_kw:${wk}:${s}`),
      value: (s) => (whole ? averageYear(ms, s) : windowAverage(ms, win.from, win.to, out, em, s)) });
  }
  const unit = v.units === "kw" ? "USD per kW" : "USD";
  const cell = (c: Col, s: string): ReactNode => (v.units === "kw" ? <V pre={pre} s={c.kw(s)} v={perKw(c.value(s))} /> : <U pre={pre} s={c.usd(s)} v={scaled(c.value(s))} />);
  const line = (s: string) => cols.map((c) => <span key={c.key}>{cell(c, s)}</span>);
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const pick = (name: "from" | "to", value: string) => {
    const other = name === "from" ? win?.to ?? value : win?.from ?? value;
    const [from, to] = name === "from" ? [value, other] : [other, value];
    set({ from: from <= to ? from : to, to: from <= to ? to : from });
  };
  const sel = "border border-muted bg-white px-1.5 py-0.5 text-sm";
  return (
    <div data-income="1">
      <div className="mb-3 flex flex-wrap items-end justify-between gap-x-6 gap-y-2 border-t border-rule pt-3">
        <h3 className="font-serif text-lg">Income by stream<Tip id="income" label="the income table">For {size}, in {v.units === "kw" ? "USD per kW of rated power" : "US dollars"}, one column for each span: the last twelve months, each calendar year held, and your own window (its first and last year, and the stress events left out of it). An event left out takes its days out of the energy, ancillary and total rows; the products are not held by the day, so their cells are not held once an event is left out.</Tip></h3>
        <span className="inline-grid grid-cols-2 border border-muted text-xs" role="group" aria-label="Income by stream: table or chart" data-chart-table="income">
          {([["table", "Table"], ["chart", "Chart"]] as const).map(([k, label], i) => (
            <button key={k} type="button" aria-pressed={v.income === k} data-show={k} onClick={() => set({ income: k })}
              className={`px-2.5 py-0.5 ${i ? "border-l border-muted" : ""} ${v.income === k ? "bg-ink text-white" : "bg-white text-ink"}`}>{label}</button>
          ))}
        </span>
      </div>
      {win ? (
        <fieldset className="mb-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm" data-window="1">
          <legend className="sr-only">Your window</legend>
          <label className="inline-flex items-center gap-1.5">From
            <select className={sel} value={win.from} data-window-from="1" aria-label="Your window, first year" onChange={(e) => pick("from", e.target.value)}>{heldYears.map((y) => <option key={y} value={y}>{y}</option>)}</select>
          </label>
          <label className="inline-flex items-center gap-1.5">to
            <select className={sel} value={win.to} data-window-to="1" aria-label="Your window, last year" onChange={(e) => pick("to", e.target.value)}>{heldYears.map((y) => <option key={y} value={y}>{y}</option>)}</select>
          </label>
          {events.length ? (
            <span className="inline-flex flex-wrap items-center gap-x-3 gap-y-1">
              <span className="text-xs text-muted">Leave out</span>
              {events.map((e) => (
                <label key={e.event} className="inline-flex items-center gap-1.5" title={e.label}>
                  <input type="checkbox" checked={out.includes(e.event)} data-leave-out={e.event} className="accent-[var(--color-accent)]"
                    onChange={(ev) => set({ out: ev.target.checked ? [...out, e.event].sort() : out.filter((id) => id !== e.event) })} />
                  <span>{e.short}</span>
                </label>
              ))}
            </span>
          ) : null}
        </fieldset>
      ) : null}
      {v.income === "chart" ? (
        <SeriesChart id="income" title={`Income by stream, ${unit}`} unit={unit} scale={v.scale} kind="stacked" tableFirst={false}
          categories={cols.map((c) => ({ label: c.label, sub: c.sub, partial: c.partial }))}
          series={[
            { name: "Energy", color: "var(--color-accent)", values: cols.map((c) => (v.units === "kw" ? perKw(c.value("energy")) : scaled(c.value("energy")))) },
            { name: "Ancillary services", color: "var(--color-ink)", values: cols.map((c) => (v.units === "kw" ? perKw(c.value("ancillary")) : scaled(c.value("ancillary")))) },
          ]}
          fmt={(n) => (v.units === "kw" ? n.toLocaleString("en-US", { maximumFractionDigits: 2 }) : usdShort(Math.round(n)))} />
      ) : (
        <ToolTable caption="Income by stream" minWidth={Math.max(560, 200 + 120 * cols.length)}
          head={["Stream", ...cols.map((c) => <>{c.head}, {unit}<span className="mt-0.5 block text-xs opacity-80">{c.sub}</span></>)]}
          rows={[
            { key: "energy", cells: ["Energy (charge low, sell high)", ...line("energy")] },
            { key: "anc", cells: ["Ancillary services", ...line("ancillary")] },
            ...products.map((p) => ({ key: p.key, muted: true, cells: [<span key="n" className="pl-4">{p.label}</span>, ...line(p.key)] })),
            { key: "cap", cells: ["Capacity"], wide: capacityWords },
            { key: "total", highlight: true, cells: ["Total, split hour by hour with no double counting", ...line("total")] },
            ...(v.units === "kw" ? [] : [{ key: "kw", cells: ["Total, USD per kW", ...cols.map((c) => <span key={c.key}><V pre={pre} s={c.kw("total")} v={perKw(c.value("total"))} /></span>)] }]),
          ]} />
      )}
      <p className="sr-only" data-income-grid={gridName}>{gridName}</p>
    </div>
  );
}
