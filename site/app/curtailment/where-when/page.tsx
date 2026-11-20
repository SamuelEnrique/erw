import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Brand } from "@/components/Brand";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { LineChart, type Line } from "@/components/LineChart";
import { ChartFrame, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { ALL, MONTHS, curtailCells, maxOf, newestYear, priceCells, shareOf, type CurtailmentPlace, type PricePlace, type WhereWhen } from "@/lib/wherewhen";
import raw from "@/data/curtailment/where_when.json";
import { WhereWhenDecisions } from "./Decisions";

// Session 8014 (chain 581, part C): "Where and when", a new view of the curtailment tool. For a chosen place, a grid of
// the hour of the day against the month, colored by the energy the operator curtailed or by the share of hours priced
// below zero; the places ranked; the trend by year; two places side by side. It shows where and when power went unused
// or unpaid, from the operators' own figures and the public prices. It gives no advice on where to put a load. The
// page /curtailment as it is does not change. Reads data/curtailment/where_when.json (warehouse/derived/where_when.py,
// contract docs/state/page_files_curtailment.md, method docs/methods/where_when.md). In review, in no menu.
export const metadata: Metadata = { title: "Where and when power is spare", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const F = raw as unknown as WhereWhen;
type Query = Record<string, string | string[] | undefined>;
const one = (q: Query, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
const NONE = "none";
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const pct = (v: number) => `${v.toFixed(1)}%`;
const gwh = (v: number) => (v / 1e3).toLocaleString("en-US", { maximumFractionDigits: 1 });

type Place = { kind: "curtailment"; c: CurtailmentPlace } | { kind: "price"; p: PricePlace };
const placeOf = (id: string): Place | null => {
  const c = F.curtailment.find((x) => x.id === id);
  if (c) return { kind: "curtailment", c };
  const p = F.prices.find((x) => x.id === id);
  return p ? { kind: "price", p } : null;
};
const nameOf = (pl: Place) => (pl.kind === "curtailment" ? `${pl.c.name}: curtailment` : `${pl.p.grid_name} ${pl.p.name}: hours below zero`);
const yearsOf = (pl: Place) => (pl.kind === "curtailment" ? pl.c.years : pl.p.years);

function Fig({ v, src, k, fmt, reason }: { v: number | null | undefined; src: string; k: string; fmt: (v: number) => string; reason?: string }) {
  if (v === null || v === undefined) return <span className="cursor-help text-muted" title={reason ?? `Not held in the file. ${src}`} data-not-held={k}>not held</span>;
  return <span className="cursor-help" title={src} data-fig={k}>{fmt(v)}</span>;
}

/** The hour of the day against the month: each cell shaded by its figure over the grid's largest, its figure on hover. */
function Heat({ cells, label, src, fmt, k, note }: { cells: (number | null)[][]; label: string; src: (i: number, h: number) => string; fmt: (v: number) => string; k: string; note: ReactNode }) {
  const max = maxOf(cells);
  return (
    <div className="my-3" data-heat={k}>
      <div className="overflow-x-auto">
        <table className="min-w-[760px] border-collapse text-[11px]" aria-label={label}>
          <caption className="mb-1 text-left text-sm text-ink">{label}</caption>
          <thead><tr><th className="px-1 text-left font-normal text-muted">Month</th>{Array.from({ length: 24 }, (_, h) => <th key={h} className="w-7 px-0 text-center font-normal text-muted">{h}</th>)}</tr></thead>
          <tbody>
            {cells.map((row, i) => (
              <tr key={i}>
                <th className="px-1 text-left font-normal text-muted">{MONTHS[i]}</th>
                {row.map((v, h) => {
                  const share = v === null || max <= 0 ? 0 : Math.max(0, v) / max;
                  return <td key={h} className="h-6 w-7 cursor-help border border-white p-0 text-center" title={`${MONTHS[i]}, hour ${h}: ${v === null ? "not held" : fmt(v)}. ${src(i, h)}`}
                    style={{ background: v === null ? "var(--color-panel)" : `color-mix(in srgb, var(--color-accent) ${Math.round(share * 100)}%, white)` }} data-cell={`${k}-${i}-${h}`} />;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-xs text-muted">{note} The darkest cell is the grid&apos;s largest figure{max > 0 ? `, ${fmt(max)}` : ""}; a pale grey cell holds no figure.</p>
    </div>
  );
}

function PlaceView({ pl, year, fuel, tag }: { pl: Place; year: string; fuel: string; tag: string }) {
  if (pl.kind === "price") {
    const p = pl.p;
    const m = priceCells(p, year);
    if (!m) return <p className="text-sm text-muted">No hour of {p.name} is held for {year}.</p>;
    const cells = m.negative.map((r, i) => r.map((n, h) => shareOf(n, m.held[i][h])));
    const src = (i: number, h: number) => `${m.negative[i][h]} of ${m.held[i][h]} hours held priced below zero (${m.basis === "rt" ? "real time" : m.basis === "da" ? "day-ahead" : m.basis}), ${p.time}. ${p.grid_name}'s prices as the ERW's tables ${[...new Set(Object.values(p.tables).flat())].join(", ")} hold them.`;
    return <Heat cells={cells} k={`${tag}-price`} label={`${p.grid_name} ${p.name}: the share of hours priced below zero, ${year === ALL ? `every year held (${p.years[0]} to ${p.years[p.years.length - 1]})` : year}`} src={src} fmt={pct} note={<>Hours of the day and months in {p.time}. {F.hour_rule}</>} />;
  }
  const c = pl.c;
  if (!c.by_hour) {
    const y = year === ALL ? null : year;
    const vars = ["curtailed_wind_mwh", "curtailed_solar_mwh"];
    const months = (c.months ?? []).filter((mo) => (y ? mo.startsWith(y) : true));
    return (
      <>
        <p className="my-2 text-sm text-muted" data-no-hour={c.id}>{c.by_hour_reason}. Its months instead:</p>
        <ToolTable minWidth={420} caption={`${c.name}: curtailed by month, ${y ?? "every month held"} (MWh)`} head={["Month", "Wind", "Solar"]}
          rows={months.slice(-24).map((mo) => ({ key: mo, cells: [mo, ...vars.map((v) => <Fig key={v} v={c.monthly?.[v]?.[mo] ?? null} src={`${c.source}.`} k={`${tag}-m-${mo}-${v}`} fmt={whole} />)] }))} />
      </>
    );
  }
  const cells = curtailCells(c, year, fuel);
  if (!cells) return <p className="text-sm text-muted">No month of {c.name} is held for {year}.</p>;
  const fuelWords = fuel === "both" ? "wind and solar" : fuel;
  return <Heat cells={cells} k={`${tag}-curt`} label={`${c.name}: ${fuelWords} curtailed, MWh, ${year === ALL ? `every year held (${c.years[0]} to ${c.years[c.years.length - 1]})` : year}`} src={() => `MWh curtailed in that hour of the day over the month's days. ${c.source}.`} fmt={whole} note={<>Hours of the day in {c.time}.</>} />;
}

/** A place's trend by year: share of hours below zero, or curtailed GWh, whole years only. */
function trend(pl: Place, fuel: string): { t: number; v: number }[] {
  const t = (y: string) => Date.UTC(Number(y), 0, 1) / 1000;
  if (pl.kind === "price") return pl.p.years.map((y) => ({ y, v: pl.p.by_year[y]?.share_negative_pct ?? null })).filter((r) => r.v !== null).map((r) => ({ t: t(r.y), v: r.v as number }));
  const keys = pl.c.by_hour ? (fuel === "both" ? ["solar", "wind"] : [fuel]) : (fuel === "both" ? ["curtailed_solar_mwh", "curtailed_wind_mwh"] : [`curtailed_${fuel}_mwh`]);
  return pl.c.years.map((y) => {
    const r = pl.c.by_year[y];
    const vals = keys.map((k) => r?.[k]);
    return { y, v: r?.whole && vals.every((v) => typeof v === "number") ? (vals as number[]).reduce((a, b) => a + b, 0) / 1e3 : null };
  }).filter((r) => r.v !== null).map((r) => ({ t: t(r.y), v: r.v as number }));
}

export default async function WhereWhenPage({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const ids = [...F.curtailment.map((c) => c.id), ...F.prices.map((p) => p.id)];
  const a = ids.includes(one(q, "a") ?? "") ? (one(q, "a") as string) : "caiso";
  const bRaw = one(q, "b");
  const b = bRaw && bRaw !== NONE && ids.includes(bRaw) && bRaw !== a ? bRaw : NONE;
  const A = placeOf(a) as Place;
  const B = b !== NONE ? placeOf(b) : null;
  const years = [...new Set([...yearsOf(A), ...(B ? yearsOf(B) : [])])].sort();
  const dflt = A.kind === "curtailment" ? newestYear(A.c.years, A.c.by_year) : newestYear(A.p.years, A.p.by_year);
  const year = one(q, "year") === ALL || years.includes(one(q, "year") ?? "") ? (one(q, "year") as string) : (dflt ?? ALL);
  const fuel = ["solar", "wind", "both"].includes(one(q, "fuel") ?? "") ? (one(q, "fuel") as string) : "solar";
  const options = [
    ...F.curtailment.map((c) => ({ value: c.id, label: `${c.name}: curtailment` })),
    ...F.prices.map((p) => ({ value: p.id, label: `${p.grid_name} ${p.name}: hours below zero${p.kind === "average" ? " (an average)" : ""}` })),
  ];
  const keep = (omit: string[]) => Object.fromEntries(Object.entries({ a, b, year, fuel }).filter(([k]) => !omit.includes(k)));
  const places = [A, ...(B ? [B] : [])];
  const priceTrend: Line[] = places.filter((p) => p.kind === "price").map((p, i) => ({ label: nameOf(p), color: i ? "series-3" : "accent", points: trend(p, fuel) }));
  const curtTrend: Line[] = places.filter((p) => p.kind === "curtailment").map((p, i) => ({ label: nameOf(p), color: i ? "series-5" : "series-1", points: trend(p, fuel) }));
  const tables = F.tables;

  return (
    <Brand>
    <ToolPage>
      <div data-where-when="1">
      <ToolHeader
        title="Where and when power is spare"
        crumb={<a href="/curtailment" className="underline">Curtailment</a>}
        lead={<>Where and when power went unused or unpaid: the wind and solar energy the grid operators curtailed, by hour of the day and month, and the hours each hub and zone priced below zero, over every year held. Two places can stand side by side. {" "}
          <Hint words="What it does not say" why="The view shows what the operators and the prices recorded. It gives no advice on where to put a load, and it makes no estimate of its own." /></>}
        under={<p className="mt-2 text-xs text-muted" data-license-line="1">License: public. File built {F.built.slice(0, 10)}.</p>}
      />

      <form method="get" action="/curtailment/where-when#view" className="mb-3 flex flex-wrap items-end gap-3 text-sm [&_label]:max-w-full [&_select]:max-w-full" data-where-form="1">
        <AutoSubmitSelect name="a" value={a} options={options} label="Place" />
        <AutoSubmitSelect name="b" value={b} options={[{ value: NONE, label: "No second place" }, ...options.filter((o) => o.value !== a)]} label="Side by side with" />
        <AutoSubmitSelect name="year" value={year} options={[{ value: ALL, label: "Every year held" }, ...[...years].reverse().map((y) => ({ value: y, label: y }))]} label="Year" />
        <AutoSubmitSelect name="fuel" value={fuel} options={[{ value: "solar", label: "Solar" }, { value: "wind", label: "Wind" }, { value: "both", label: "Wind and solar" }]} label="Curtailed energy of" />
        <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
      </form>

      <ToolSection title="When in the day and the year" id="view">
        {places.map((pl, i) => <PlaceView key={i} pl={pl} year={year} fuel={fuel} tag={i ? "b" : "a"} />)}
      </ToolSection>

      <ToolSection title="The trend by year" id="trend">
        {priceTrend.length ? (
          <ChartFrame title="Share of hours priced below zero, by whole year" tip={<Hint words=" (source)" why={`${F.whole_year_rule} ${F.hour_rule}`} />}>
            <LineChart lines={priceTrend} unit="%" x="year" ariaLabel="Share of hours priced below zero by year" />
          </ChartFrame>
        ) : null}
        {curtTrend.length ? (
          <ChartFrame title={`${fuel === "both" ? "Wind and solar" : fuel === "solar" ? "Solar" : "Wind"} curtailed, GWh a whole year`} tip={<Hint words=" (source)" why={`${F.whole_year_rule} ${F.curtailment.map((c) => c.source).join("; ")}.`} />}>
            <LineChart lines={curtTrend} unit="GWh" x="year" ariaLabel="Curtailed energy by year" />
          </ChartFrame>
        ) : null}
      </ToolSection>

      <ToolSection title="The places ranked" id="ranked">
        <ToolTable
          minWidth={560}
          caption="Hubs and zones by the share of hours priced below zero, in each one's newest whole year"
          head={["Place", "Grid", "Year", "Hours below zero", "Share"]}
          rows={F.ranked_negative.map((r, i) => ({ key: r.id, highlight: r.id === a || r.id === b, cells: [<a key="n" className="underline" href={`/curtailment/where-when?a=${encodeURIComponent(r.id)}&year=${r.year}`} data-rank={i + 1}>{i + 1}. {r.name}</a>,
            r.grid.toUpperCase(), r.year, <Fig key="n2" v={r.negative} src={`of ${whole(r.hours_held)} hours held.`} k={`rk-${r.id}-n`} fmt={whole} />,
            <Fig key="s" v={r.share_negative_pct} src={`${r.negative} of ${r.hours_held} hours held. ${F.hour_rule}`} k={`rk-${r.id}-s`} fmt={pct} />] }))}
        />
        <ToolTable
          minWidth={480}
          caption="The operators that publish curtailment, by whole year (GWh)"
          head={["Operator", ...[...new Set(F.curtailment.flatMap((c) => c.years))].sort().slice(-5)]}
          rows={F.curtailment.map((c) => { const ys = [...new Set(F.curtailment.flatMap((x) => x.years))].sort().slice(-5); return { key: c.id, cells: [c.name, ...ys.map((y) => {
            const r = c.by_year[y]; const ks = c.by_hour ? ["solar", "wind"] : ["curtailed_solar_mwh", "curtailed_wind_mwh"];
            const v = r?.whole ? ks.reduce((s, k) => s + (typeof r[k] === "number" ? (r[k] as number) : 0), 0) : null;
            return <Fig key={y} v={v} src={`Wind and solar, the year's total. ${c.source}.`} k={`ct-${c.id}-${y}`} fmt={gwh} reason={r ? "Fewer than 90 percent of the year's days are held." : "No day of the year is held."} />; })] }; })}
        />
        <p className="mt-2 text-sm" data-not-drawn="1">Not drawn: {Object.entries(F.price_blank).map(([k, v]) => <span key={k} className="mr-2 cursor-help text-muted underline decoration-dotted" title={`${v.words}${v.regions.length ? ` Its places: ${v.regions.join(", ")}.` : ""}`}>{v.name} prices</span>)}
          {Object.entries(F.curtailment_not_held).map(([k, v]) => <span key={k} className="mr-2 cursor-help text-muted underline decoration-dotted" title={v}>{k.toUpperCase()} curtailment</span>)}</p>
      </ToolSection>

      <WhereWhenDecisions />
      <TableDownloads tables={tables} />
      <SourceLine tables={tables} note={<>Method: <a href="/data/methods/where_when">the view&apos;s method note</a>. The operators&apos; figures and the hub and zone prices as published; the view counts hours, sums months and years, and computes only the shares it names.</>} />
      </div>
    </ToolPage>
    </Brand>
  );
}
