"use client";
// Energy Research Warehouse (ERW) site, session 132: the markets workbench, the analyzer of the price board.
//
// Opens beside the tables when a row is clicked, and at full width on request. Any window from a week to the whole
// history; a second series laid over the first, chosen from everything on the board; the spread or the ratio between
// the two as its own line with its average and range (two hubs give a basis, power over gas a heat rate, a product
// over crude a crack); this year against the same dates in prior years, with the five years before as a band; a
// distribution block; and a CSV of the rows shown. A power hub opens on its last seven days by the hour, real time
// against day-ahead, with on-peak and off-peak means and the week's spikes, which is what the markets page showed.
// Every chart answers the mouse with the value, the hour or date and the series. Nothing is filled: an hour or a day
// that is not held is a gap in the line. The state is the address (lib/board.ts, benchOf).
import { useEffect, useMemo, useState } from "react";
import { TimeChart, type TimeSeries } from "@/components/TimeChart";   // session 318: the three charts through the shared SVG set
import { CategoryChart } from "@/components/svgchart";
import {
  FREQ_WORDS, SLOTS, WINDOWS, csv, dateWords, distribution, fmt, histogram, hourlyOf, isoDay, isoHour, joined, localHour, pointsOf, seasonal, slotLabel, summary, volatility, windowed,
  type Bench, type BoardFile, type HourlyFile, type Point, type Row, type SeriesFile,
} from "@/lib/board";

const cache = new Map<string, Promise<unknown>>();
function load<T>(url: string): Promise<T> {
  if (!cache.has(url)) cache.set(url, fetch(url).then((r) => { if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`); return r.json(); }).catch((e) => { cache.delete(url); throw e; }));
  return cache.get(url) as Promise<T>;
}
type Loaded<T> = { data: T | null; error: string | null };
function useFile<T>(url: string | null): Loaded<T> {
  const [state, setState] = useState<{ url: string | null; data: T | null; error: string | null }>({ url: null, data: null, error: null });
  useEffect(() => {
    let alive = true;
    if (!url) return;
    load<T>(url).then((data) => { if (alive) setState({ url, data, error: null }); }, (e: Error) => { if (alive) setState({ url, data: null, error: e.message }); });
    return () => { alive = false; };
  }, [url]);
  return state.url === url ? { data: state.data, error: state.error } : { data: null, error: null };
}
const nameOf = (r: Row) => `${r.label}${r.at ? `, ${r.at}` : ""}`;
const marketOf = (r: Row): "da" | "rt" => (r.tags.market === "rt" ? "rt" : "da");
/** A finer series as the means of each calendar month it holds points in, to set beside a monthly one. */
function monthly(p: Point[]): Point[] {
  const by = new Map<number, { s: number; n: number }>();
  for (const x of p) { const d = new Date(x.t); const k = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1); const c = by.get(k) ?? { s: 0, n: 0 }; c.s += x.v; c.n += 1; by.set(k, c); }
  return [...by.entries()].sort((a, b) => a[0] - b[0]).map(([t, c]) => ({ t, v: c.s / c.n }));
}

function Btn({ on, onClick, children, title }: { on?: boolean; onClick: () => void; children: React.ReactNode; title?: string }) {
  return <button type="button" aria-pressed={on} title={title} onClick={onClick} className={`border px-1.5 py-0.5 text-xs ${on ? "border-accent bg-accent text-white" : "border-rule bg-white text-ink hover:border-accent"}`}>{children}</button>;
}

type Lines = { hourly: boolean; freq: "D" | "W" | "M" | "H"; a: Point[]; b: Point[] | null; nameA: string; nameB: string; unitA: string; unitB: string; fileA: HourlyFile | null; fileB: HourlyFile | null; note: string };

function PriceChart({ lines, calc, mode, tz }: { lines: Lines; calc: Point[] | null; mode: Bench["m"]; tz: string | null }) {
  // session 318: the two series on one time chart (the second on its own axis when its unit differs), the calculation
  // under it on a second, with its average as a named line; the range slider is gone, the table holds every point
  const sameUnit = !lines.b || lines.unitA === lines.unitB;
  const series: TimeSeries[] = [{ name: lines.nameA, color: "accent", points: lines.a.map((p): [number, number | null] => [p.t, p.v]) }];
  if (lines.b) series.push({ name: lines.nameB, color: "fuel-gas", points: lines.b.map((p): [number, number | null] => [p.t, p.v]), y2: !sameUnit || undefined });
  const x = lines.hourly ? "minute" : lines.freq === "M" ? "month" : "day";
  const two = calc !== null && calc.length > 0;
  const cs = two ? summary(calc!) : null;
  const calcName = mode === "ratio" ? `${lines.nameA} over ${lines.nameB}` : `${lines.nameA} minus ${lines.nameB}`;
  return (
    <div data-chart="price" role="group" aria-label={`${lines.nameA}${lines.b ? ` against ${lines.nameB}` : ""}${tz ? `, ${tz}` : ""}`}>
      <TimeChart series={series} unit={lines.unitA} unit2={sameUnit ? "" : lines.unitB} ariaLabel={`${lines.nameA}${lines.b ? ` against ${lines.nameB}` : ""}`} height={two ? 240 : 320} x={x} />
      {two ? (
        <div className="mt-2" data-chart="calc">
          <TimeChart series={[{ name: calcName, color: "ink", points: calc!.map((p): [number, number | null] => [p.t, p.v]) }]} unit={mode === "ratio" ? "ratio" : "spread"} ariaLabel={calcName} height={200} x={x}
            refLines={cs ? [{ value: cs.mean, name: `average ${cs.mean.toFixed(2)}`, dashed: true }] : undefined} />
        </div>
      ) : null}
    </div>
  );
}

function SeasonChart({ p, freq, name, unit }: { p: Point[]; freq: "D" | "W" | "M"; name: string; unit: string }) {
  const s = useMemo(() => seasonal(p, freq), [p, freq]);
  // session 318: the years as lines over the season's slots, the newest in the accent and the earlier ones in the five
  // greys (app/tokens.css, --color-season-1 to 5), the range of the years before as a band
  const labels = Array.from({ length: SLOTS[freq] }, (_, i) => slotLabel(i, freq));
  const newest = s.years[s.years.length - 1];
  const shown = s.years.slice(-6);
  const greys = [1, 2, 3, 4, 5].map((i) => `season-${i}`);
  const band = s.bandYears.length ? `${s.bandYears[0]} to ${s.bandYears[s.bandYears.length - 1]} range` : "";
  const series = shown.map((y, i) => ({ name: String(y), color: y === newest ? "accent" : greys[Math.max(0, greys.length - (shown.length - 1) + i)] ?? greys[0], values: s.lines[y], kind: "line" as const, width: y === newest ? 2 : 1 }));
  return (
    <div data-chart="season">
      <CategoryChart id="board-season" x={labels} series={series} unit={unit} label={`${name}: this year against the same dates in prior years`} height={360} zero={false} every={freq === "D" ? 31 : freq === "W" ? 4 : 1}
        band={band ? { lo: s.lo, hi: s.hi, name: band } : undefined} nameOf={(i) => `${name}, ${labels[i]}`} />
    </div>
  );
}

function HistChart({ p, name, unit }: { p: Point[]; name: string; unit: string }) {
  const bins = useMemo(() => histogram(p, 30), [p]);
  return (
    <div data-chart="dist">
      <CategoryChart id="board-dist" x={bins.map((b) => b.lo.toFixed(b.hi - b.lo < 1 ? 2 : 0))} unit="observations" label={`${name}: distribution of the window's values`} height={240}
        series={[{ name: `${name}, ${unit}`, color: "accent", values: bins.map((b) => b.n), kind: "bar" }]} notes={bins.map((b) => `${b.lo.toFixed(2)} to ${b.hi.toFixed(2)} ${unit}`)} />
    </div>
  );
}

function Stat({ label, value, title }: { label: string; value: React.ReactNode; title?: string }) {
  return <div className="bg-white px-2 py-1" title={title}><div className="text-xs uppercase tracking-wide text-muted">{label}</div><div className="text-sm tabular-nums">{value}</div></div>;
}
const NOT = <span className="text-xs text-muted">not held yet</span>;

export function Workbench({ file, bench, row, set }: { file: BoardFile; bench: Bench; row: Row; set: (patch: Partial<Bench>) => void }) {
  const over = bench.o ? file.rows.find((r) => r.id === bench.o && r.status === "ok") ?? null : null;
  const canHourly = !!row.hourly && (!over || !!over.hourly);
  const hourly = bench.r === "h" && canHourly;
  const sA = useFile<SeriesFile>(`/board/s/${row.id}.json`);
  const sB = useFile<SeriesFile>(over ? `/board/s/${over.id}.json` : null);
  const hA = useFile<HourlyFile>(row.hourly ? `/board/h/${row.hourly}.json` : null);
  const hB = useFile<HourlyFile>(over?.hourly ? `/board/h/${over.hourly}.json` : null);
  const error = sA.error ?? sB.error ?? (hourly ? hA.error ?? hB.error : null);
  const ready = hourly ? !!hA.data && (!over || !!hB.data) : !!sA.data && (!over || !!sB.data);

  const lines: Lines | null = useMemo(() => {
    if (!ready) return null;
    if (hourly) {
      const a = windowed(hourlyOf(hA.data!, marketOf(row)), bench.w, bench.from, bench.to);
      // the second series over the same span: from the first's first hour on (day-ahead runs a day past real time)
      const first = a.length ? a[0].t : 0;
      const all = over ? hourlyOf(hB.data!, marketOf(over)) : null;
      const b = all ? (bench.from || bench.to ? windowed(all, bench.w, bench.from, bench.to) : all.filter((p) => p.t >= first)) : null;
      return { hourly: true, freq: "H", a, b, nameA: nameOf(row), nameB: over ? nameOf(over) : "", unitA: row.unit, unitB: over?.unit ?? "", fileA: hA.data, fileB: hB.data, note: "" };
    }
    let a = pointsOf(sA.data!), b = over ? pointsOf(sB.data!) : null;
    let freq: "D" | "W" | "M" = sA.data!.freq, nameA = nameOf(row), nameB = over ? nameOf(over) : "";
    if (b && sA.data!.freq !== sB.data!.freq) {
      // two series of different steps are set side by side by the month: the finer one as its monthly mean
      if (sA.data!.freq !== "M") { a = monthly(a); nameA += " (monthly mean)"; }
      if (sB.data!.freq !== "M") { b = monthly(b); nameB += " (monthly mean)"; }
      freq = "M";
    }
    a = windowed(a, bench.w, bench.from, bench.to);
    if (b) b = bench.from || bench.to ? windowed(b, bench.w, bench.from, bench.to) : b.filter((p) => a.length > 0 && p.t >= a[0].t);
    return { hourly: false, freq, a, b, nameA, nameB, unitA: row.unit, unitB: over?.unit ?? "", fileA: null, fileB: null, note: "" };
  }, [ready, hourly, hA.data, hB.data, sA.data, sB.data, row, over, bench.w, bench.from, bench.to]);

  const pairs = useMemo(() => (lines?.b ? joined(lines.a, lines.b) : []), [lines]);
  const calc: Point[] | null = useMemo(() => {
    if (!lines?.b || bench.m === "none") return null;
    return bench.m === "ratio" ? pairs.filter((x) => x.ratio !== null).map((x) => ({ t: x.t, v: x.ratio as number })) : pairs.map((x) => ({ t: x.t, v: x.spread }));
  }, [lines, pairs, bench.m]);
  const calcName = lines?.b ? (bench.m === "ratio" ? `${lines.nameA} over ${lines.nameB}` : `${lines.nameA} minus ${lines.nameB}`) : "";
  const calcUnit = bench.m === "ratio" ? (row.unit === "USD/MWh" && over?.unit === "USD/MMBtu" ? "MMBtu/MWh" : "ratio") : row.unit === over?.unit ? row.unit : "difference";
  // the series the seasons and the distribution are about: the computed line when there is one, else the row
  const active = calc && calc.length ? { p: calc, name: calcName, unit: calcUnit } : lines ? { p: lines.a, name: lines.nameA, unit: lines.unitA } : null;
  const whole: Point[] | null = useMemo(() => {
    if (!sA.data) return null;
    if (!over || bench.m === "none" || !sB.data) return pointsOf(sA.data);
    let a = pointsOf(sA.data), b = pointsOf(sB.data);
    if (sA.data.freq !== sB.data.freq) { if (sA.data.freq !== "M") a = monthly(a); if (sB.data.freq !== "M") b = monthly(b); }
    const j = joined(a, b);
    return bench.m === "ratio" ? j.filter((x) => x.ratio !== null).map((x) => ({ t: x.t, v: x.ratio as number })) : j.map((x) => ({ t: x.t, v: x.spread }));
  }, [sA.data, sB.data, over, bench.m]);
  const wholeFreq: "D" | "W" | "M" = sA.data && sB.data && over && sA.data.freq !== sB.data.freq ? "M" : sA.data?.freq ?? "D";
  const tz = hourly ? hA.data?.tz ?? null : null;
  const when = (t: number) => (hourly ? (tz ? `${localHour(t, tz)} local` : isoHour(t)) : dateWords(isoDay(t), lines?.freq === "M" ? "M" : "D"));
  const sumA = lines ? summary(lines.a) : null, sumB = lines?.b ? summary(lines.b) : null, sumC = calc ? summary(calc) : null;
  const th = Number.isFinite(bench.th) ? bench.th : sumA ? Number((sumA.mean + (sumA.max - sumA.mean) / 2).toFixed(2)) : 0;
  const dist = active ? distribution(active.p, th, hourly && !(calc && calc.length) ? lines!.fileA ?? undefined : undefined) : null;
  const distA = lines && hourly ? distribution(lines.a, th, lines.fileA ?? undefined) : null;
  const distB = lines?.b && hourly ? distribution(lines.b, th, lines.fileB ?? undefined) : null;
  const vol = whole ? volatility(windowed(whole, "all"), 30) : null;
  const week = file.week.find((w) => w.hub === row.hourly);
  const spikes = file.spikes.filter((s) => s.hub === row.hourly);
  const rtLine = lines && hourly ? (marketOf(row) === "rt" ? { p: lines.a, name: lines.nameA } : over && marketOf(over) === "rt" && lines.b ? { p: lines.b, name: lines.nameB } : { p: lines.a, name: lines.nameA }) : null;
  const top = rtLine ? distribution(rtLine.p, th).top : null;

  const download = () => {
    if (!lines) return;
    let text = "";
    if (bench.v === "season" && whole) {
      const s = seasonal(whole, wholeFreq);
      text = csv(["slot", ...s.years.map(String), "band_low", "band_high"], Array.from({ length: SLOTS[wholeFreq] }, (_, i) => [slotLabel(i, wholeFreq), ...s.years.map((y) => s.lines[y][i]), s.lo[i], s.hi[i]]));
    } else if (lines.b) {
      const times = [...new Set([...lines.a.map((p) => p.t), ...lines.b.map((p) => p.t)])].sort((x, y) => x - y);
      const ma = new Map(lines.a.map((p) => [p.t, p.v])), mb = new Map(lines.b.map((p) => [p.t, p.v])), mc = new Map((calc ?? []).map((p) => [p.t, p.v]));
      text = csv([hourly ? "hour_utc" : "date", `${lines.nameA} (${lines.unitA})`, `${lines.nameB} (${lines.unitB})`, ...(calc ? [`${calcName} (${calcUnit})`] : [])],
        times.map((t) => [hourly ? new Date(t).toISOString() : isoDay(t), ma.get(t) ?? null, mb.get(t) ?? null, ...(calc ? [mc.get(t) ?? null] : [])]));
    } else {
      text = csv([hourly ? "hour_utc" : "date", `${lines.nameA} (${lines.unitA})`], lines.a.map((p) => [hourly ? new Date(p.t).toISOString() : isoDay(p.t), p.v]));
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type: "text/csv" }));
    a.download = `erw-board-${row.id}${over ? `-vs-${over.id}` : ""}-${bench.v}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const groupsOf = file.groups.map((g) => ({ g, rows: file.rows.filter((r) => r.group === g.id && r.status === "ok" && r.id !== row.id) })).filter((x) => x.rows.length);
  const n2 = (v: number | null | undefined, unit = "") => (v === null || v === undefined ? NOT : <>{fmt(v, unit)}</>);
  return (
    <div className="border border-accent bg-paper/40 p-3 text-sm" data-workbench={row.id}>
      <div className="mb-2 flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="text-xs uppercase tracking-wide text-muted">Markets workbench</div>
          <h2 className="font-serif text-xl leading-tight text-accent" title={row.code ? `Code: ${row.code}` : undefined}>{row.label}</h2>
          <div className="text-xs text-muted">{row.at}{row.at ? " · " : ""}{row.last ? <>{fmt(row.last.v, row.unit)} {row.unit} on {dateWords(row.last.t, row.freq)}</> : null}{row.formula ? <span className="ml-1 cursor-help border-b border-dotted border-muted" title={row.formula}>formula</span> : null}</div>
        </div>
        <div className="flex gap-1">
          <Btn onClick={download} title="Download the rows shown as a CSV">CSV</Btn>
          <Btn onClick={() => { void navigator.clipboard?.writeText(window.location.href); }} title="Copy this view's address">Copy link</Btn>
          <Btn on={bench.x} onClick={() => set({ x: !bench.x })} title={bench.x ? "Back beside the tables" : "Expand to full width"}>{bench.x ? "Dock" : "Expand"}</Btn>
          <Btn onClick={() => set({ s: null })} title="Close the workbench">Close</Btn>
        </div>
      </div>

      <div className="mb-2 grid gap-2 border-y border-rule py-2 text-xs">
        <div className="flex flex-wrap items-center gap-1">
          <span className="w-16 text-muted">View</span>
          <Btn on={bench.v === "price"} onClick={() => set({ v: "price" })}>Prices</Btn>
          <Btn on={bench.v === "season"} onClick={() => set({ v: "season" })} title="This year against the same dates in prior years, with the five years before as a band">Prior years</Btn>
          <Btn on={bench.v === "dist"} onClick={() => set({ v: "dist" })}>Distribution</Btn>
        </div>
        <div className="flex flex-wrap items-center gap-1">
          <span className="w-16 text-muted">Window</span>
          {WINDOWS.map(([k, label]) => <Btn key={k} on={!bench.from && !bench.to && bench.w === k} onClick={() => set({ w: k, from: "", to: "" })}>{label}</Btn>)}
          <label className="ml-1 flex items-center gap-1">from <input type="date" value={bench.from} onChange={(e) => set({ from: e.target.value })} className="border border-rule bg-white px-1 py-0.5" /></label>
          <label className="flex items-center gap-1">to <input type="date" value={bench.to} onChange={(e) => set({ to: e.target.value })} className="border border-rule bg-white px-1 py-0.5" /></label>
        </div>
        <div className="flex flex-wrap items-center gap-1">
          <span className="w-16 text-muted">Step</span>
          <Btn on={hourly} onClick={() => set({ r: "h" })} title={canHourly ? "Hourly prices" : row.hourly ? "The second series is not held by the hour" : "This series is not held by the hour"}>Hourly</Btn>
          <Btn on={!hourly} onClick={() => set({ r: "d" })}>{row.freq === "D" ? "Daily" : row.freq === "W" ? "Weekly" : "Monthly"}</Btn>
          {!canHourly ? <span className="text-muted" title={row.hourly ? "The second series is not held by the hour, so both are shown by the day." : "Only power hubs and ancillary services are held by the hour."}>{FREQ_WORDS[row.freq]} only</span> : null}
        </div>
        <div className="flex flex-wrap items-center gap-1">
          <span className="w-16 text-muted">Overlay</span>
          <select value={over?.id ?? ""} onChange={(e) => set({ o: e.target.value || null })} className="w-full max-w-[22rem] border border-rule bg-white px-1 py-0.5" aria-label="A second series, from everything on the board" data-overlay="1">
            <option value="">None</option>
            {groupsOf.map(({ g, rows }) => <optgroup key={g.id} label={g.title}>{rows.map((r) => <option key={r.id} value={r.id}>{nameOf(r)} ({r.unit})</option>)}</optgroup>)}
          </select>
          {over ? <>
            <span className="ml-1 text-muted">between them</span>
            <Btn on={bench.m === "spread"} onClick={() => set({ m: "spread" })} title="The first less the second, on the times both hold">Spread</Btn>
            <Btn on={bench.m === "ratio"} onClick={() => set({ m: "ratio" })} title="The first over the second: power over gas is a heat rate">Ratio</Btn>
            <Btn on={bench.m === "none"} onClick={() => set({ m: "none" })}>Off</Btn>
          </> : null}
        </div>
      </div>

      {error ? <p role="status" className="border border-rule bg-white px-2 py-1 text-xs">The series could not be read: {error}</p> : null}
      {!ready && !error ? <p className="py-10 text-center text-xs text-muted" role="status">Reading the series.</p> : null}
      {ready && lines && !lines.a.length ? <p role="status" className="border border-rule bg-white px-2 py-1 text-xs">No value of this series is held in the window chosen.</p> : null}

      {ready && lines && lines.a.length ? (
        <>
          {bench.v === "price" ? <PriceChart lines={lines} calc={calc} mode={bench.m} tz={tz} /> : null}
          {bench.v === "season" && whole ? <SeasonChart p={whole} freq={wholeFreq} name={over && bench.m !== "none" ? calcName : nameOf(row)} unit={over && bench.m !== "none" ? calcUnit : row.unit} /> : null}
          {bench.v === "dist" && active ? <HistChart p={active.p} name={active.name} unit={active.unit} /> : null}

          <div className="mt-2 overflow-x-auto">
            <table className="w-full border-collapse text-xs tabular-nums" data-stats="1">
              <thead><tr className="border-b border-rule text-xs uppercase tracking-wide text-muted">
                <th className="py-0.5 text-left font-normal">In the window</th><th className="px-2 text-right font-normal">Mean</th><th className="px-2 text-right font-normal">Low</th><th className="px-2 text-right font-normal">High</th>
                {hourly ? <><th className="px-2 text-right font-normal">On-peak</th><th className="px-2 text-right font-normal">Off-peak</th><th className="px-2 text-right font-normal">Hours below 0</th></> : null}
                <th className="px-2 text-right font-normal">{hourly ? "Hours" : "Values"}</th>
              </tr></thead>
              <tbody>
                {[[lines.nameA, sumA, distA, lines.unitA], ...(lines.b ? [[lines.nameB, sumB, distB, lines.unitB]] : []), ...(calc ? [[`${calcName}`, sumC, null, calcUnit]] : [])].map((x, i) => {
                  const [name, s, d, unit] = x as [string, ReturnType<typeof summary>, ReturnType<typeof distribution> | null, string];
                  return (
                    <tr key={i} className="border-b border-rule/60" data-stat-row={i}>
                      <th scope="row" className="py-0.5 text-left font-normal">{name} <span className="text-muted">{unit}</span></th>
                      <td className="px-2 text-right" data-stat="mean">{n2(s?.mean)}</td>
                      <td className="px-2 text-right" title={s ? when(s.minT) : undefined}>{n2(s?.min)}</td>
                      <td className="px-2 text-right" title={s ? when(s.maxT) : undefined}>{n2(s?.max)}</td>
                      {hourly ? <><td className="px-2 text-right" data-stat="peak">{d ? n2(d.peakMean) : ""}</td><td className="px-2 text-right" data-stat="offpeak">{d ? n2(d.offMean) : ""}</td><td className="px-2 text-right">{d ? d.negative.toLocaleString("en-US") : ""}</td></> : null}
                      <td className="px-2 text-right">{s ? s.n.toLocaleString("en-US") : 0}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {bench.v === "dist" && dist && active ? (
            <div className="mt-3" data-dist="1">
              <div className="mb-1 flex flex-wrap items-center gap-2 text-xs">
                <label className="flex items-center gap-1 text-muted" title="By default halfway from the window's mean to its high">Threshold <input type="number" value={Number.isFinite(th) ? th : 0} step="any" onChange={(e) => set({ th: Number(e.target.value) })} className="w-24 border border-rule bg-white px-1 py-0.5 text-ink" /> {active.unit}</label>
              </div>
              <div className="grid grid-cols-2 gap-px border border-rule bg-rule sm:grid-cols-4">
                <Stat label={`${hourly ? "Hours" : "Values"} above ${fmt(th, active.unit)}`} value={`${dist.above.toLocaleString("en-US")} of ${dist.n.toLocaleString("en-US")}`} />
                <Stat label={`${hourly ? "Hours" : "Values"} below zero`} value={dist.negative.toLocaleString("en-US")} />
                <Stat label="On-peak mean" value={hourly && distA ? n2(distA.peakMean) : <span className="text-xs text-muted" title="On-peak and off-peak means are computed from hourly prices: choose the hourly step on a power hub.">hourly step only</span>} />
                <Stat label="Off-peak mean" value={hourly && distA ? n2(distA.offMean) : <span className="text-xs text-muted" title="On-peak and off-peak means are computed from hourly prices: choose the hourly step on a power hub.">hourly step only</span>} />
                <Stat label="Median" value={n2(summary(active.p)?.median)} />
                <Stat label="30-day volatility" value={vol === null ? NOT : vol.toFixed(2)} title="The standard deviation of the last 30 changes between consecutive values of the series at its own step." />
              </div>
            </div>
          ) : null}

          {(bench.v === "dist" || hourly) && (top || dist) ? (
            <div className="mt-3" data-spikes="1">
              <h3 className="mb-1 text-xs uppercase tracking-wide text-muted">The ten highest {hourly ? "hours" : "values"} in the window{rtLine && hourly ? `, ${rtLine.name}` : ""}</h3>
              <ol className="grid gap-x-6 text-xs tabular-nums sm:grid-cols-2">
                {(hourly && top ? top : dist!.top).map((p) => <li key={p.t} className="flex justify-between border-b border-rule/60 py-0.5"><span className="text-muted">{when(p.t)}</span><span>{p.v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></li>)}
              </ol>
            </div>
          ) : null}

          {hourly && row.group === "power" && (week || spikes.length) ? (
            <div className="mt-3 border-t border-rule pt-2" data-week={row.hourly}>
              {week ? (
                <div className="grid grid-cols-2 gap-px border border-rule bg-rule sm:grid-cols-4">
                  {([["da_mean_usd", "Day-ahead, week"], ["da_onpeak_mean_usd", "On-peak DA, week"], ["da_offpeak_mean_usd", "Off-peak DA, week"], ["da_rt_spread_mean_usd", "RT minus DA, week"], ["implied_heat_rate", "Heat rate, week"]] as const).map(([k, label]) => {
                    const m = week.means[k];
                    return <Stat key={k} label={label} title={m ? `the 7 days to ${dateWords(m.end)}; the change is on the 7 days before` : "A week's mean needs the measure on all 7 days."}
                      value={m ? <>{m.v.toFixed(2)}{m.ch !== null ? <span className={`ml-1 text-xs ${m.ch > 0 ? "text-up" : m.ch < 0 ? "text-down" : "text-muted"}`}>{m.ch > 0 ? "+" : m.ch < 0 ? "−" : ""}{Math.abs(m.ch).toFixed(2)}</span> : null}</> : NOT} />;
                  })}
                  <Stat label="Largest RT minus DA" value={week.max_spread ? week.max_spread.v.toFixed(2) : NOT} title={week.max_spread ? `${dateWords(week.max_spread.start)} to ${dateWords(week.max_spread.end)}` : undefined} />
                  <Stat label="Hours RT over DA + 50" value={week.hours50 ? week.hours50.v.toLocaleString("en-US") : NOT} title={week.hours50 ? `${dateWords(week.hours50.start)} to ${dateWords(week.hours50.end)}` : undefined} />
                  <Stat label="30-day volatility, DA" value={week.vol ? week.vol.v.toFixed(2) : NOT} title={week.vol ? `as of ${dateWords(week.vol.t)}` : "Needs 31 days of day-ahead prices."} />
                </div>
              ) : null}
              {spikes.length ? (
                <>
                  <h3 className="mb-1 mt-2 text-xs uppercase tracking-wide text-muted">The week&apos;s highest real-time intervals at this hub</h3>
                  <ol className="grid gap-x-6 text-xs tabular-nums sm:grid-cols-2">
                    {spikes.map((s) => <li key={s.t} className="flex justify-between border-b border-rule/60 py-0.5"><span className="text-muted">{localHour(Date.parse(s.t), s.tz)} local</span><span>{s.v.toFixed(2)}</span></li>)}
                  </ol>
                </>
              ) : null}
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
