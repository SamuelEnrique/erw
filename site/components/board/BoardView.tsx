"use client";
// Energy Research Warehouse (ERW) site, session 132: the price board (/board), one page for every price held.
//
// The tables are dense on purpose: every row carries its latest value and date, the move over a day, a week, a month
// and a year, its 7-day and 30-day means, a trend line of its last 30 points that answers the mouse, and a bar placing
// the latest value in its one-year range. A click on a row opens the markets workbench beside the tables
// (components/board/Workbench.tsx); the row, the filters and the workbench's view are kept in the address. The page
// face carries no method: a number that is missing is a short placeholder with its reason on hover, and everything
// else is in the Method note (docs/methods/price_board.md).
// Session 168: before any row is clicked, the workbench's place holds a quiet empty panel (BenchPlaceholder): the same
// box the workbench takes, docked on the right on wide screens and above the tables on narrow ones, the faint outline of
// a chart drawn in SVG, and one line. A click on a row puts the workbench in that box, exactly as before.
import { useCallback, useEffect, useMemo, useState, useSyncExternalStore } from "react";
import { usePathname } from "next/navigation";
import { SiteLink } from "@/components/SiteLink";
import { Workbench } from "@/components/board/Workbench";
import {
  FREQ_WORDS, MOVES, PLACEHOLDER, benchOf, benchQuery, dateWords, fmt, gridExtremes, noMove, pct, rangeExtremes, rowsOf, shortDate, signed, sparkOf,
  type Bench, type BoardFile, type Group, type Row, type WeekRow,
} from "@/lib/board";

const METHOD = "/data/methods/price_board";
const PERCENT = (r: Row) => !r.formula && r.unit !== "USD/MWh" && r.unit !== "USD/MW-hour" && r.unit !== "percent";

/** The aside the workbench is docked in: on the right from the xl width, above the tables below it. One string, so the
 *  placeholder and the workbench take the same box (session 168). */
const BENCH_ASIDE = "min-w-0 max-xl:order-first xl:sticky xl:top-2 xl:max-h-[calc(100vh-1rem)] xl:self-start xl:overflow-y-auto";
const BENCH_GRID = "grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(460px,42%)]";

/** Session 168: the workbench's place before a row is clicked: an empty panel with the outline of a chart (axes and
 *  three light grid lines, drawn, not a picture) and one small line. Its height is the workbench's own as it opens
 *  (the chart panel's 340 px with the header, the controls and the figures around it), so nothing moves on a click. */
function BenchPlaceholder() {
  return (
    <div className="relative flex h-[46rem] flex-col border border-rule bg-paper/30 p-3 text-sm xl:h-[calc(100vh-1rem)]" data-bench-placeholder="1">
      <p className="text-[11px] text-muted">Click any row to open the markets workbench here.</p>
      <svg aria-hidden="true" className="mt-3 w-full flex-1 text-rule" viewBox="0 0 400 240" preserveAspectRatio="none" data-outline="1">
        <g stroke="currentColor" strokeWidth="1" vectorEffect="non-scaling-stroke" fill="none">
          <line x1="34" y1="60" x2="392" y2="60" strokeDasharray="3 4" opacity="0.7" vectorEffect="non-scaling-stroke" />
          <line x1="34" y1="110" x2="392" y2="110" strokeDasharray="3 4" opacity="0.7" vectorEffect="non-scaling-stroke" />
          <line x1="34" y1="160" x2="392" y2="160" strokeDasharray="3 4" opacity="0.7" vectorEffect="non-scaling-stroke" />
          <polyline points="34,12 34,210 392,210" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
        </g>
      </svg>
    </div>
  );
}

/** The last 30 points as a line that answers the mouse: the nearest point's value, date and series. */
function Spark({ row }: { row: Row }) {
  const pts = useMemo(() => sparkOf(row), [row]);
  const [at, setAt] = useState<number | null>(null);
  if (pts.length < 2) return <span className="text-[11px] text-muted" title="A trend line needs two points held.">not held yet</span>;
  const W = 112, H = 26, pad = 3;
  const vs = pts.map((p) => p.v), lo = Math.min(...vs), hi = Math.max(...vs);
  const x = (i: number) => pad + (i * (W - 2 * pad)) / (pts.length - 1);
  const y = (v: number) => (hi === lo ? H / 2 : pad + ((hi - v) * (H - 2 * pad)) / (hi - lo));
  const p = at === null ? null : pts[at];
  return (
    <span className="relative inline-block align-middle" data-spark={row.id}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" className="block"
        aria-label={`${row.label}, ${row.at}: last ${pts.length} ${FREQ_WORDS[row.freq]} values, ${fmt(pts[0].v, row.unit)} on ${dateWords(pts[0].t, row.freq)} to ${fmt(pts[pts.length - 1].v, row.unit)} on ${dateWords(pts[pts.length - 1].t, row.freq)}`}
        onMouseMove={(e) => { const b = e.currentTarget.getBoundingClientRect(); setAt(Math.max(0, Math.min(pts.length - 1, Math.round(((e.clientX - b.left - pad) / (b.width - 2 * pad)) * (pts.length - 1))))); }}
        onMouseLeave={() => setAt(null)}>
        {lo < 0 && hi > 0 ? <line x1={pad} x2={W - pad} y1={y(0)} y2={y(0)} stroke="var(--color-rule)" strokeWidth={1} /> : null}
        <polyline points={pts.map((q, i) => `${x(i).toFixed(1)},${y(q.v).toFixed(1)}`).join(" ")} fill="none" stroke="var(--color-accent)" strokeWidth={1.3} strokeLinejoin="round" />
        <circle cx={x(at ?? pts.length - 1)} cy={y((p ?? pts[pts.length - 1]).v)} r={2.2} fill="var(--color-accent)" />
        {at !== null ? <line x1={x(at)} x2={x(at)} y1={0} y2={H} stroke="var(--color-muted)" strokeWidth={0.6} /> : null}
      </svg>
      {p ? (
        <span role="tooltip" className="pointer-events-none absolute bottom-full right-0 z-20 mb-1 whitespace-nowrap border border-rule bg-white px-2 py-1 text-left text-[11px] leading-tight text-ink shadow-sm">
          <span className="block text-muted">{row.label}{row.at ? `, ${row.at}` : ""}</span>
          <span className="block"><strong>{fmt(p.v, row.unit)}</strong> {row.unit} on {dateWords(p.t, row.freq)}</span>
        </span>
      ) : null}
    </span>
  );
}

/** Where the latest value sits between the lowest and highest of its last 365 days. */
function RangeBar({ row }: { row: Row }) {
  const r = row.range;
  if (!r || r.pos === null) return <span className="text-[11px] text-muted" title="The one-year range is drawn once enough of the last 365 days are held.">not held yet</span>;
  const W = 84, x = 4 + r.pos * (W - 8);
  const words = `${row.label}${row.at ? `, ${row.at}` : ""}: ${fmt(row.last!.v, row.unit)} ${row.unit} on ${dateWords(row.last!.t, row.freq)}, between ${fmt(r.lo, row.unit)} and ${fmt(r.hi, row.unit)} over the ${r.n} values held of the last 365 days`;
  return (
    <span className="inline-flex items-center gap-1.5 whitespace-nowrap" title={words} data-range={row.id}>
      <span className="text-[10px] text-muted" data-n={`${row.id}|lo`}>{fmt(r.lo, row.unit)}</span>
      <svg viewBox={`0 0 ${W} 12`} width={W} height={12} role="img" aria-label={words}>
        <line x1={4} x2={W - 4} y1={6} y2={6} stroke="var(--color-rule)" strokeWidth={3} strokeLinecap="round" />
        <circle cx={x} cy={6} r={3.6} fill="var(--color-accent)" stroke="#fff" strokeWidth={1.2} />
      </svg>
      <span className="text-[10px] text-muted" data-n={`${row.id}|hi`}>{fmt(r.hi, row.unit)}</span>
    </span>
  );
}

/** The futures curve beside a spot row. No free source publishes contracts 1 to 4 today: the shape is greyed. */
function Curve({ row }: { row: Row }) {
  if (!row.curve) return null;
  return (
    <span className="inline-flex items-center gap-1 whitespace-nowrap text-[10px] text-muted" title={row.curve.note} data-curve={row.id}>
      <svg viewBox="0 0 44 14" width={44} height={14} aria-hidden="true">
        <polyline points="3,10 15,7 28,5.5 41,4.5" fill="none" stroke="var(--color-rule)" strokeWidth={1.4} strokeDasharray="3 2" />
        {[3, 15, 28, 41].map((cx, i) => <circle key={cx} cx={cx} cy={[10, 7, 5.5, 4.5][i]} r={1.6} fill="#fff" stroke="var(--color-rule)" />)}
      </svg>
      {PLACEHOLDER[row.curve.status as "licensed"]}
    </span>
  );
}

function MoveCell({ row, k }: { row: Row; k: "d" | "w" | "m" | "y" }) {
  const m = row.moves?.[k];
  if (!m) {
    return noMove(row.freq, k)
      ? <span className="text-[10px] text-muted" title={`A ${FREQ_WORDS[row.freq]} series has no move over a ${k === "d" ? "day" : "week"}.`}>{FREQ_WORDS[row.freq]}</span>
      : <span className="text-[10px] text-muted" title="The value this move is measured from is not held.">not held yet</span>;
  }
  const cls = m.ch > 0 ? "text-up" : m.ch < 0 ? "text-down" : "";
  return (
    <span className={`whitespace-nowrap ${cls}`} title={`against ${fmt(m.v, row.unit)} ${row.unit} on ${dateWords(m.t, row.freq)}`}>
      <span data-n={`${row.id}|${k}`}>{signed(m.ch, row.unit)}</span>
      {m.pct !== null && PERCENT(row) ? <span className="ml-1 text-[10px] text-muted">{pct(m.pct)}</span> : null}
    </span>
  );
}

function PriceRow({ row, group, open, onOpen, file }: { row: Row; group: Group; open: boolean; onOpen: (id: string) => void; file: BoardFile }) {
  const name = (
    <th scope="row" className="whitespace-nowrap py-1 pl-2 pr-3 text-left font-normal">
      <span className={row.status === "ok" ? "text-ink" : "text-muted"} title={[row.code ? `Code: ${row.code}` : "", row.formula ? `Formula: ${row.formula}` : "", row.source !== undefined ? `Source: ${file.sources[row.source]}` : ""].filter(Boolean).join("\n") || undefined}>
        {row.label}{row.formula ? <sup className="ml-0.5 text-[9px] text-muted">f</sup> : null}
      </span>
      {row.at ? <span className="ml-1.5 text-[11px] text-muted">{row.at}</span> : null}
    </th>
  );
  const cols = 11 + (group.curve ? 1 : 0);
  if (row.status !== "ok") {
    return (
      <tr className="border-b border-rule/70" data-row={row.id} data-status={row.status}>
        {name}
        <td colSpan={cols} className="py-1 pr-2 text-left text-[11px] italic text-muted"><span title={row.note} className="cursor-help border-b border-dotted border-muted">{PLACEHOLDER[row.status]}</span></td>
      </tr>
    );
  }
  const last = row.last!;
  return (
    <tr className={`cursor-pointer border-b border-rule/70 hover:bg-paper ${open ? "bg-paper outline outline-1 -outline-offset-1 outline-accent" : ""}`} data-row={row.id} tabIndex={0} aria-selected={open}
      onClick={() => onOpen(row.id)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onOpen(row.id); } }}>
      {name}
      <td className="py-1 pr-3 text-right font-semibold"><span data-n={`${row.id}|last`}>{fmt(last.v, row.unit)}</span><span className="ml-1 text-[10px] font-normal text-muted">{row.unit}</span></td>
      <td className="whitespace-nowrap py-1 pr-3 text-right text-[11px] text-muted" title={`${dateWords(last.t, row.freq)}${row.freq !== "D" ? `, a ${FREQ_WORDS[row.freq]} series` : ""}`}>
        {shortDate(last.t, row.freq)}{row.freq !== "D" ? <span className="ml-1 rounded-sm border border-rule px-0.5 text-[9px] uppercase">{FREQ_WORDS[row.freq]}</span> : null}
      </td>
      {MOVES.map(([k]) => <td key={k} className="py-1 pr-3 text-right text-xs"><MoveCell row={row} k={k} /></td>)}
      <td className="py-1 pr-3 text-right text-xs">{row.avg7 ? <span title={`the mean of the ${row.avg7.n} values held in the 7 days to ${dateWords(last.t)}`} data-n={`${row.id}|avg7`}>{fmt(row.avg7.v, row.unit)}</span> : <span className="text-[10px] text-muted" title={`A ${FREQ_WORDS[row.freq]} series has no 7-day mean.`}>{FREQ_WORDS[row.freq]}</span>}</td>
      <td className="py-1 pr-3 text-right text-xs">{row.avg30 ? <span title={`the mean of the ${row.avg30.n} values held in the 30 days to ${dateWords(last.t)}`} data-n={`${row.id}|avg30`}>{fmt(row.avg30.v, row.unit)}</span> : <span className="text-[10px] text-muted" title={`A ${FREQ_WORDS[row.freq]} series has no 30-day mean.`}>{FREQ_WORDS[row.freq]}</span>}</td>
      <td className="whitespace-nowrap py-1 pr-3 text-right text-[11px] text-muted">{row.lo30 !== undefined ? <span title="the lowest and highest value of the last 30 days">{fmt(row.lo30, row.unit)} to {fmt(row.hi30!, row.unit)}</span> : null}</td>
      <td className="py-0.5 pr-3 text-right" onClick={(e) => e.stopPropagation()}><Spark row={row} /></td>
      <td className="py-1 pr-2 text-right"><RangeBar row={row} /></td>
      {group.curve ? <td className="py-1 pr-2 text-left"><Curve row={row} /></td> : null}
    </tr>
  );
}

function GroupTable({ file, group, chosen, pick, open, onOpen }: { file: BoardFile; group: Group; chosen: Record<string, string>; pick: (key: string, v: string) => void; open: string | null; onOpen: (id: string) => void }) {
  const rows = rowsOf(file, group, chosen);
  return (
    <section id={group.id} className="mb-6 scroll-mt-4" aria-label={group.title} data-group={group.id}>
      <div className="mb-1 flex flex-wrap items-baseline gap-x-4 gap-y-1 border-b border-accent pb-0.5">
        <h2 className="font-serif text-lg text-accent">{group.title}</h2>
        <span className="text-[11px] text-muted" data-count={group.id}>{rows.length} {rows.length === 1 ? "row" : "rows"}</span>
        {group.filters.map((f) => (
          <span key={f.key} className="flex flex-wrap items-center gap-1 text-[11px]" role="group" aria-label={f.label}>
            <span className="text-muted">{f.label}</span>
            {f.options.map(([v, label]) => {
              const on = (chosen[f.key] ?? f.default) === v;
              return <button key={v} type="button" aria-pressed={on} onClick={() => pick(f.key, v)} data-filter={`${group.id}.${f.key}.${v}`}
                className={`border px-1.5 py-px ${on ? "border-accent bg-accent text-white" : "border-rule bg-white text-ink hover:border-accent"}`}>{label}</button>;
            })}
          </span>
        ))}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[1180px] border-collapse text-sm tabular-nums">
          <thead>
            <tr className="border-b border-rule text-[10px] uppercase tracking-wide text-muted">
              <th className="py-1 pl-2 text-left font-normal">Price</th>
              <th className="pr-3 text-right font-normal">Latest</th>
              <th className="pr-3 text-right font-normal">Its date</th>
              {MOVES.map(([k, n]) => <th key={k} className="pr-3 text-right font-normal">{n}</th>)}
              <th className="pr-3 text-right font-normal">7-day avg</th>
              <th className="pr-3 text-right font-normal">30-day avg</th>
              <th className="pr-3 text-right font-normal">30-day low to high</th>
              <th className="pr-3 text-right font-normal">Last 30</th>
              <th className="pr-2 text-right font-normal">One-year range</th>
              {group.curve ? <th className="pr-2 text-left font-normal">Futures 1 to 4</th> : null}
            </tr>
          </thead>
          <tbody>{rows.map((r) => <PriceRow key={r.id} row={r} group={group} open={open === r.id} onOpen={onOpen} file={file} />)}</tbody>
        </table>
      </div>
    </section>
  );
}

const WEEK_COLS: [string, string][] = [["da_mean_usd", "Day-ahead"], ["da_onpeak_mean_usd", "On-peak DA"], ["da_offpeak_mean_usd", "Off-peak DA"], ["da_rt_spread_mean_usd", "RT minus DA"], ["implied_heat_rate", "Heat rate"]];
const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** The week by hub, as the markets page had it: the week's means with their change on the week before, the largest
 *  real-time premium, the hours real time ran 50 above day-ahead, and 30-day volatility. */
function WeekTable({ file, grid, pick, onOpen }: { file: BoardFile; grid: string; pick: (v: string) => void; onOpen: (id: string) => void }) {
  const grids = [...new Set(file.week.map((w) => w.grid))];
  const rows = file.week.filter((w) => grid === "all" || w.grid === grid);
  const cell = (w: WeekRow, k: string) => {
    const m = w.means[k];
    if (!m) return <span className="text-[10px] text-muted" title="A week's mean needs the measure on all 7 days.">not held yet</span>;
    return <span title={`the 7 days to ${dateWords(m.end)}${m.ch !== null ? "; the change is on the 7 days before" : ""}`}><span data-n={`week|${w.hub}|${k}`}>{two(m.v)}</span>{m.ch !== null ? <span className={`ml-1 text-[10px] ${m.ch > 0 ? "text-up" : m.ch < 0 ? "text-down" : "text-muted"}`}>{m.ch > 0 ? "+" : m.ch < 0 ? "−" : ""}{two(Math.abs(m.ch))}</span> : null}</span>;
  };
  return (
    <section id="week" className="mb-6 scroll-mt-4" aria-label="The week, by hub" data-group="week">
      <div className="mb-1 flex flex-wrap items-baseline gap-x-4 gap-y-1 border-b border-accent pb-0.5">
        <h2 className="font-serif text-lg text-accent">The week, by hub</h2>
        <span className="text-[11px] text-muted">{rows.length} rows</span>
        <span className="flex flex-wrap items-center gap-1 text-[11px]" role="group" aria-label="Grid">
          <span className="text-muted">Grid</span>
          {["all", ...grids].map((g) => <button key={g} type="button" aria-pressed={grid === g} onClick={() => pick(g)} className={`border px-1.5 py-px ${grid === g ? "border-accent bg-accent text-white" : "border-rule bg-white text-ink hover:border-accent"}`}>{g === "all" ? "All grids" : g}</button>)}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[980px] border-collapse text-sm tabular-nums">
          <thead>
            <tr className="border-b border-rule text-[10px] uppercase tracking-wide text-muted">
              <th className="py-1 pl-2 text-left font-normal">Hub or zone</th>
              <th className="pr-3 text-right font-normal">Day-ahead, latest</th>
              {WEEK_COLS.map(([k, n]) => <th key={k} className="pr-3 text-right font-normal">{n}, week</th>)}
              <th className="pr-3 text-right font-normal">Largest RT minus DA</th>
              <th className="pr-3 text-right font-normal">Hours RT over DA + 50</th>
              <th className="pr-2 text-right font-normal">30-day volatility</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((w) => (
              <tr key={w.hub} className="cursor-pointer border-b border-rule/70 hover:bg-paper" tabIndex={0} onClick={() => onOpen(`${w.hub}-da`)} onKeyDown={(e) => { if (e.key === "Enter") onOpen(`${w.hub}-da`); }}>
                <th scope="row" className="py-1 pl-2 pr-3 text-left font-normal"><span title={`Code: ${w.code}`}>{w.label}</span></th>
                <td className="pr-3 text-right">{w.last_da ? <span title={dateWords(w.last_da.t)}><span data-n={`week|${w.hub}|last`}>{two(w.last_da.v)}</span><span className="ml-1 text-[10px] text-muted">{shortDate(w.last_da.t)}</span></span> : <span className="text-[10px] text-muted">not held yet</span>}</td>
                {WEEK_COLS.map(([k]) => <td key={k} className="pr-3 text-right">{cell(w, k)}</td>)}
                <td className="pr-3 text-right">{w.max_spread ? <span title={`${dateWords(w.max_spread.start)} to ${dateWords(w.max_spread.end)}`}>{two(w.max_spread.v)}</span> : <span className="text-[10px] text-muted" title="Needs a real-time price on each of the week's 7 days.">not held yet</span>}</td>
                <td className="pr-3 text-right">{w.hours50 ? <span title={`${dateWords(w.hours50.start)} to ${dateWords(w.hours50.end)}`}>{w.hours50.v.toLocaleString("en-US")}</span> : <span className="text-[10px] text-muted" title="Needs a real-time price on each of the week's 7 days.">not held yet</span>}</td>
                <td className="pr-2 text-right">{w.vol ? <span title={`as of ${dateWords(w.vol.t)}`}>{two(w.vol.v)}</span> : <span className="text-[10px] text-muted" title="Needs 31 days of day-ahead prices.">not held yet</span>}</td>
              </tr>
            ))}
            {(grid === "all" || grid === "MISO") ? <tr className="border-b border-rule/70"><th scope="row" className="py-1 pl-2 pr-3 text-left font-normal text-muted">MISO hubs</th><td colSpan={8} className="text-left text-[11px] italic text-muted"><span className="cursor-help border-b border-dotted border-muted" title="MISO's prices are paused while its terms are reviewed; no MISO value is shown.">{PLACEHOLDER.paused}</span></td></tr> : null}
            {(grid === "all" || grid === "PJM") ? <tr className="border-b border-rule/70"><th scope="row" className="py-1 pl-2 pr-3 text-left font-normal text-muted">PJM hubs</th><td colSpan={8} className="text-left text-[11px] italic text-muted"><span className="cursor-help border-b border-dotted border-muted" title="PJM publishes its prices under a license the ERW does not hold.">{PLACEHOLDER.licensed}</span></td></tr> : null}
          </tbody>
        </table>
      </div>
      <h3 className="mb-1 mt-3 text-xs uppercase tracking-wide text-muted">The week&apos;s highest real-time intervals</h3>
      <ol className="grid gap-x-8 text-xs tabular-nums sm:grid-cols-2 xl:grid-cols-3">
        {file.spikes.filter((s) => grid === "all" || s.grid === grid).slice(0, 30).map((s) => (
          <li key={`${s.hub}${s.t}`} className="flex cursor-pointer justify-between border-b border-rule/60 py-0.5 hover:bg-paper" onClick={() => onOpen(`${s.hub}-rt`)}
            title={`${s.label} (${s.code}), interval starting ${new Intl.DateTimeFormat("en-GB", { timeZone: s.tz, dateStyle: "medium", timeStyle: "short" }).format(new Date(s.t))} local time, ${s.freq === "PT1H" ? "hourly" : "15-minute"} price`}>
            <span>{s.label} <span className="text-muted">{new Intl.DateTimeFormat("en-GB", { timeZone: s.tz, day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(s.t))}</span></span>
            <span data-n={`spike|${s.hub}|${s.t}`}>{two(s.v)}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}

function Headline({ file, market, setMarket, onOpen }: { file: BoardFile; market: "da" | "rt"; setMarket: (m: "da" | "rt") => void; onOpen: (id: string) => void }) {
  const ex = gridExtremes(file, market), rx = rangeExtremes(file);
  const row = (id: string) => file.rows.find((r) => r.id === id && r.status === "ok");
  const cells: { k: string; label: string; r?: Row; v?: number; note: string }[] = [];
  if (ex) {
    cells.push({ k: "low", label: `Lowest grid, ${market === "da" ? "day-ahead" : "real time"}`, r: ex.low.row, v: ex.low.v, note: `${ex.low.row.label}, ${dateWords(ex.day)}` });
    cells.push({ k: "high", label: `Highest grid, ${market === "da" ? "day-ahead" : "real time"}`, r: ex.high.row, v: ex.high.v, note: `${ex.high.row.label}, ${dateWords(ex.day)}` });
  }
  for (const [id, label] of [["eia-henry-hub-spot", "Henry Hub gas"], ["eia-wti-cushing-spot", "WTI crude"], ["eia-brent-spot", "Brent crude"], ["erw-brent-minus-wti", "Brent minus WTI"]] as const) {
    const r = row(id);
    if (r) cells.push({ k: id, label, r, v: r.last!.v, note: dateWords(r.last!.t) });
  }
  if (rx) {
    cells.push({ k: "top", label: "Highest in its year's range", r: rx.top, v: rx.top.last!.v, note: `${rx.top.label}, ${rx.top.at}: ${Math.round(rx.top.range!.pos! * 100)}% of the way up` });
    cells.push({ k: "bottom", label: "Lowest in its year's range", r: rx.bottom, v: rx.bottom.last!.v, note: `${rx.bottom.label}, ${rx.bottom.at}: ${Math.round(rx.bottom.range!.pos! * 100)}% of the way up` });
  }
  return (
    <div className="mb-4" data-headline="1">
      <div className="mb-1 flex items-center gap-1 text-[11px]">
        <span className="text-muted">Power market</span>
        {(["da", "rt"] as const).map((m) => <button key={m} type="button" aria-pressed={market === m} onClick={() => setMarket(m)} className={`border px-1.5 py-px ${market === m ? "border-accent bg-accent text-white" : "border-rule bg-white hover:border-accent"}`}>{m === "da" ? "Day-ahead" : "Real time"}</button>)}
      </div>
      <div className="grid grid-cols-2 gap-px border border-rule bg-rule sm:grid-cols-4 xl:grid-cols-8">
        {cells.map((c) => (
          <button key={c.k} type="button" onClick={() => c.r && onOpen(c.r.id)} className="bg-white px-2 py-1.5 text-left hover:bg-paper" title={c.r ? `${c.r.label}${c.r.at ? `, ${c.r.at}` : ""}. Open in the workbench.` : undefined}>
            <span className="block text-[10px] uppercase tracking-wide text-muted">{c.label}</span>
            <span className="block font-serif text-xl tabular-nums" data-n={`head|${c.k}`}>{c.r && c.v !== undefined ? fmt(c.v, c.r.unit) : ""}<span className="ml-1 font-sans text-[10px] text-muted">{c.r?.unit}</span></span>
            <span className="block truncate text-[10px] text-muted">{c.note}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

// The address's query as the page's state. The server draws the board as it opens with nothing chosen (so the whole
// board is in the page's HTML); the browser then reads what the address asks for.
const listeners = new Set<() => void>();
function subscribe(cb: () => void) {
  listeners.add(cb);
  window.addEventListener("popstate", cb);
  return () => { listeners.delete(cb); window.removeEventListener("popstate", cb); };
}

export function BoardView({ file }: { file: BoardFile }) {
  const search = useSyncExternalStore(subscribe, () => window.location.search, () => "");
  const params = useMemo(() => new URLSearchParams(search), [search]);
  const path = usePathname();
  const [ready, setReady] = useState(false);       // the page answers the mouse once this is set: the browser check waits for it
  useEffect(() => setReady(true), []);
  const bench = useMemo(() => benchOf(new URLSearchParams(params.toString()), file), [params, file]);
  const market: "da" | "rt" = params.get("mk") === "rt" ? "rt" : "da";
  const chosenOf = useCallback((g: Group) => Object.fromEntries(g.filters.map((f) => [f.key, params.get(`${g.id}.${f.key}`) ?? f.default])), [params]);
  /** Write a state to the address without a navigation, so a view can be copied and the page does not reload. */
  const write = useCallback((q: URLSearchParams | string) => {
    const s = q.toString();
    window.history.replaceState(null, "", `${s ? `${path}?${s}` : path}${window.location.hash}`);
    listeners.forEach((l) => l());
  }, [path]);
  const setBench = useCallback((patch: Partial<Bench>) => {
    const cur = new URLSearchParams(window.location.search);
    const next = { ...benchOf(cur, file), ...patch };
    // a new row opens with its own defaults: only the panel's width is carried over
    const q = patch.s !== undefined && patch.s !== benchOf(cur, file).s
      ? benchQuery({ ...benchOf(new URLSearchParams(patch.s ? { s: patch.s } : {}), file), x: next.x }, file, cur)
      : benchQuery(next, file, cur);
    write(q);
  }, [file, write]);
  const setParam = useCallback((k: string, v: string, dflt: string) => {
    const q = new URLSearchParams(window.location.search);
    if (v === dflt) q.delete(k); else q.set(k, v);
    write(q);
  }, [write]);
  const onOpen = useCallback((id: string) => { if (file.rows.some((r) => r.id === id && r.status === "ok")) setBench({ s: id }); }, [file, setBench]);
  const openRow = bench.s ? file.rows.find((r) => r.id === bench.s) ?? null : null;
  const tables = (
    <div className="min-w-0">
      {file.groups.map((g) => (
        <GroupTable key={g.id} file={file} group={g} chosen={chosenOf(g)} open={bench.s} onOpen={onOpen}
          pick={(key, v) => setParam(`${g.id}.${key}`, v, g.filters.find((f) => f.key === key)!.default)} />
      )).flatMap((el, i) => (file.groups[i].id === "as" ? [el, <WeekTable key="week" file={file} grid={params.get("week.grid") ?? "all"} pick={(v) => setParam("week.grid", v, "all")} onOpen={onOpen} />] : [el]))}
    </div>
  );
  return (
    <div className="relative left-1/2 w-[min(calc(100vw-2rem),1800px)] -translate-x-1/2 border border-rule bg-white px-3 py-4 text-ink sm:px-5" data-board="1" data-ready={ready ? "1" : undefined}>
      <header className="mb-3 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-2">
        <h1 className="font-serif text-3xl text-accent">Price board</h1>
        <p className="text-xs text-muted">
          <SiteLink href={METHOD}>Method, sources and gaps</SiteLink>
          {" | "}
          <SiteLink href="/explorer/ercot-peak-premium">ERCOT since 2015: the peak premium explorer</SiteLink>
          {" | "}
          <span title={`The board's files were built at ${file.built}.`}>built {dateWords(file.built)}</span>
        </p>
      </header>
      <Headline file={file} market={market} setMarket={(m) => setParam("mk", m, "da")} onOpen={onOpen} />
      <nav aria-label="Sections" className="mb-4 flex flex-wrap gap-x-3 gap-y-1 text-[11px]">
        <span className="text-muted">Jump to</span>
        {file.groups.flatMap((g) => (g.id === "as" ? [g, { id: "week", title: "The week, by hub" }] : [g])).map((g) => <a key={g.id} href={`#${g.id}`} className="underline decoration-rule underline-offset-2 hover:text-accent">{g.title}</a>)}
      </nav>
      <p className="mb-3 text-[11px] text-muted">Click any row to open it in the markets workbench.</p>
      {openRow && bench.x ? <div className="mb-6"><Workbench file={file} bench={bench} row={openRow} set={setBench} /></div> : null}
      <div className={!openRow || !bench.x ? BENCH_GRID : ""}>
        {tables}
        {openRow && !bench.x ? (
          <aside className={BENCH_ASIDE} aria-label="Markets workbench">
            <Workbench file={file} bench={bench} row={openRow} set={setBench} />
          </aside>
        ) : !openRow ? (
          <aside className={BENCH_ASIDE} aria-label="Markets workbench">
            <BenchPlaceholder />
          </aside>
        ) : null}
      </div>
    </div>
  );
}
