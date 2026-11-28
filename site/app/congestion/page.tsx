import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Brand } from "@/components/Brand";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { Num } from "@/components/Num";
import { pfKey, type Segment } from "@/lib/pagefile";
import { LineChart, type Line } from "@/components/LineChart";
import { ChartFrame, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { ALL, MONTHS, maxAbs, monthT, yearOf, type Congestion, type Constraint, type Place } from "@/lib/congestion";
import raw from "@/data/conditions/congestion.json";
import { CongestionDecisions } from "./Decisions";

// Session 9000 (chain 601, part C): "Congestion", a new page. The binding transmission constraints that the grid
// operators publish, with their day-ahead shadow prices: which bound most and cost most, by operator and year; when in
// the day and the year a chosen constraint binds; the hubs and zones where congestion adds most to the price and takes
// most off it; two places side by side. A constraint is named as the operator names it, with no guess at where it is.
// Reads data/conditions/congestion.json (warehouse/derived/congestion_page.py, contract
// docs/state/page_files_conditions.md, method docs/methods/grid_congestion.md). In review, in no menu.
export const metadata: Metadata = { title: "Congestion", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const F = raw as unknown as Congestion;
type Query = Record<string, string | string[] | undefined>;
const one = (q: Query, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
const NONE = "none";
const usd = (v: number) => `${v.toFixed(2)} USD/MWh`;
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const pct = (v: number) => `${v.toFixed(1)}%`;
// Session 10220 (congestion audit, finding 3): the window a figure covers, in the operator's own days (the file's time
// stamps are UTC; an SPP hour from 18:00 Central standard time is the next day in UTC).
const TZ: Record<string, string> = { spp: "America/Chicago", caiso: "America/Los_Angeles" };
const localDay = (ts: string, op: string) => new Intl.DateTimeFormat("en-CA", { timeZone: TZ[op] ?? "UTC", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(ts));
const SHOWN = F.operators.filter((o) => o.status === "shown" && F.constraints[o.id]);
const PLACES: Place[] = Object.values(F.places).flat();
const placeOf = (id: string) => PLACES.find((p) => p.id === id) ?? null;
const PF = "conditions/congestion.json";
const opOf = (id: string) => F.operators.find((o) => o.id === id.split(":")[0]);
// Session 9001, row H2: SPP's places are named "SPP North hub" in the file, so the operator is not written twice.
const placeLabel = (op: string | undefined, name: string) => (op && !name.startsWith(`${op} `) ? `${op} ${name}` : name);
const labelOf = (p: Place) => placeLabel(opOf(p.id)?.name, p.name);
// Session 10220 (congestion audit, finding 1): each operator splits its price against its own reference (the energy part
// is the same at every place of one operator in every hour), so a congestion part compares places of one operator only.
const REFERENCE_WORDS ="Each operator splits its price against its own reference: the energy part is the same at every place of one operator, so a congestion part says how far congestion put a place above or below that operator's reference price, not what the place's price would have been with no congestion. Places of one operator compare with each other; SPP's and CAISO's places are ranked in one table here, but each is measured against its own operator's reference, so a rank across the two operators means nothing. For two places of one operator, the difference of their congestion parts, with the difference of their loss parts (in the file, not drawn), is their day-ahead price spread.";

// Session 9001 (part H): a figure given its page-file key (lib/pagefile.ts) renders through Num, so check-values reads
// it again from site/data/conditions/congestion.json on its own.
function Fig({ v, src, k, fmt, reason, check }: { v: number | null | undefined; src: string; k: string; fmt: (v: number) => string; reason?: string; check?: string }) {
  if (v === null || v === undefined) return <span className="cursor-help text-muted" title={reason ?? `Not held in the file. ${src}`} data-not-held={k}>not held</span>;
  if (check) return <span className="cursor-help" data-fig={k}><Num check={check} raw={v} source={src}>{fmt(v)}</Num></span>;
  return <span className="cursor-help" title={src} data-fig={k}>{fmt(v)}</span>;
}

/** The hour of the day against the month. Positive figures shade in the accent, negative in the second series color. */
function Heat({ cells, label, src, fmt, k, note }: { cells: (number | null)[][]; label: string; src: (i: number, h: number) => string; fmt: (v: number) => string; k: string; note: ReactNode }) {
  const max = maxAbs(cells);
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
                  const share = v === null || max <= 0 ? 0 : Math.abs(v) / max;
                  const color = v !== null && v < 0 ? "var(--color-series-3)" : "var(--color-accent)";
                  return <td key={h} className="h-6 w-7 cursor-help border border-white p-0 text-center" title={`${MONTHS[i]}, hour ${h}: ${v === null ? "not held" : fmt(v)}. ${src(i, h)}`}
                    style={{ background: v === null ? "var(--color-panel)" : `color-mix(in srgb, ${color} ${Math.round(share * 100)}%, white)` }} data-cell={`${k}-${i}-${h}`} />;
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

// Session 10220 (congestion audit, finding 4): SPP's files name its western balancing area (SWPW) from 1 April 2026, the
// day its market took in the west (docs/methods/spp_dam_cleared_energy.md), and the page set SPP's years side by side.
const SPP_WEST_WORDS = "SPP's market took in its western area on 1 April 2026 (SPP's files name the area SWPW from that day), so SPP's constraints and price parts from April 2026 may be those of a larger market than before. The page sets SPP's months and years side by side across that day with no mark, and whether SPP's hubs' congestion parts moved because of it is not known here.";

// Session 10220 (congestion audit, finding 2): SPP's files until November 2021 name no contingency, and from then the same
// element is listed under BASE, so one element stood on two rows with one label; a row with no contingency now says so.
// Session 11407 (the ruling readied for finding 2): the file's constraint is the element, its listings joined.
function constraintLabel(c: Constraint) {
  if (c.contingencies && c.contingencies.length > 1) return `${c.name} (${c.contingencies.length} listings joined)`;
  if (!c.contingency) return `${c.name} (no contingency named)`;
  return c.contingency !== "BASE" ? `${c.name} (contingency ${c.contingency})` : c.name;
}
const ELEMENT_WORDS = "A constraint here is one element (a line, a transformer, a flowgate, a nomogram), as the operator names it, with every contingency it was listed under joined: an hour it bound under two contingencies counts once, as one constraint-hour, its shadow price there the two summed. SPP's files until November 2021 name no contingency and later list the same element under BASE; the two listings are one row. A row marked \"listings joined\" says how many listings it holds.";

export default async function CongestionPage({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const op = SHOWN.some((o) => o.id === one(q, "op")) ? (one(q, "op") as string) : (SHOWN[0]?.id ?? "spp");
  const O = F.constraints[op];
  const years = O ? O.years : [];
  const year = one(q, "year") === ALL || years.includes(one(q, "year") ?? "") ? (one(q, "year") as string) : (years[years.length - 1] ?? ALL);
  const top = O?.top[year] ?? O?.top[ALL] ?? { by_hours: [], by_cost: [] };
  const keys = O ? Object.keys(O.constraints) : [];
  const ck = keys.includes(one(q, "c") ?? "") ? (one(q, "c") as string) : (top.by_cost[0] ?? keys[0] ?? "");
  const C = O?.constraints[ck];
  const placeIds = PLACES.map((p) => p.id);
  const a = placeIds.includes(one(q, "a") ?? "") ? (one(q, "a") as string) : (placeIds.find((p) => p.startsWith(`${op}:`)) ?? placeIds[0]);
  const bRaw = one(q, "b");
  const b = bRaw && bRaw !== NONE && placeIds.includes(bRaw) && bRaw !== a ? bRaw : NONE;
  const A = placeOf(a) as Place;
  const B = b !== NONE ? placeOf(b) : null;
  const pyears = [...new Set([...(A?.years ?? []), ...(B?.years ?? [])])].sort();
  const py = pyears.includes(one(q, "py") ?? "") ? (one(q, "py") as string) : (pyears[pyears.length - 1] ?? "");
  const src = F.sources[op];
  const yearWords = year === ALL ? `every year held (${years[0]} to ${years[years.length - 1]})` : year;
  const rowOf = (k: string, i: number) => {
    const c = O.constraints[k];
    const y = yearOf(c, year);
    const s = `${src.constraints}. ${F.sign_rule}`;
    const at = (f: string) => pfKey(PF, ["constraints", op, "constraints", k, ...(year === ALL ? [] : ["by_year", year]), f] as Segment[]);
    return { key: k, highlight: k === ck, cells: [
      <a key="n" className="break-all underline" href={`/congestion?op=${op}&year=${year}&c=${encodeURIComponent(k)}#when`} data-rank={i + 1}>{i + 1}. {constraintLabel(c)}</a>,
      <Fig key="h" v={y?.hours} src={`Hours it bound in the day-ahead market, ${yearWords}. ${s}`} k={`h-${i}`} check={at("hours")} fmt={whole} />,
      <Fig key="m" v={y?.abs_mean} src={`Mean size of its shadow price over the hours it bound. ${s}`} k={`m-${i}`} check={at("abs_mean")} fmt={usd} />,
      <Fig key="x" v={y?.abs_max} src={`Highest size of its shadow price. ${s}`} k={`x-${i}`} check={at("abs_max")} fmt={usd} />,
      <Fig key="c" v={y?.cost} src={`${F.cost_rule} ${s}`} k={`c-${i}`} check={at("cost")} fmt={whole} />,
    ] };
  };
  const head = ["Constraint, as the operator names it", "Hours bound", "Mean shadow price", "Highest", "Summed (USD/MWh x hours)"];
  const ranked = PLACES.filter((p) => p.by_year[py]).map((p) => ({ p, y: p.by_year[py] })).sort((x, z) => (z.y.congestion_mean ?? 0) - (x.y.congestion_mean ?? 0));
  // Session 10220 (congestion audit, finding 3): the days the places' year holds, so a year that is not whole says so.
  const spans = ranked.map(({ p }) => {
    const o = p.id.split(":")[0], a = localDay(p.first, o), z = localDay(p.last, o);
    return [a > `${py}-01-01` ? a : `${py}-01-01`, z < `${py}-12-31` ? z : `${py}-12-31`];
  });
  const pwin = spans.length && spans.every((s) => s[0] === spans[0][0] && s[1] === spans[0][1]) ? spans[0] : null;
  const spanOf = (id: string) => spans[ranked.findIndex(({ p }) => p.id === id)];
  const congLines: Line[] = [A, ...(B ? [B] : [])].map((p, i) => ({ label: labelOf(p), color: i ? "series-3" : "accent",
    points: p.monthly.filter((m) => m[4] !== null).map((m) => ({ t: monthT(m[0]), v: m[4] as number })) }));
  const shareLines: Line[] = [A, ...(B ? [B] : [])].map((p, i) => ({ label: labelOf(p), color: i ? "series-3" : "accent",
    points: p.monthly.filter((m) => m[7] !== null).map((m) => ({ t: monthT(m[0]), v: m[7] as number })) }));
  const hoursLine: Line[] = C ? [{ label: constraintLabel(C), color: "accent", points: C.monthly.map((m) => ({ t: monthT(m[0]), v: m[1] })) }] : [];
  const placeOptions = PLACES.map((p) => ({ value: p.id, label: labelOf(p) }));
  const blank = F.operators.filter((o) => o.status !== "shown");

  return (
    <Brand>
    <ToolPage>
      <div data-congestion="1">
      <ToolHeader
        title="Congestion"
        lead={<>Where the wires were full: the transmission constraints that bound in each operator&apos;s day-ahead market, with the shadow price the operator published, and the part of each hub&apos;s and zone&apos;s price that the operator puts down to congestion, measured against its own reference price. Two places can stand side by side. {" "}
          <Hint words="What it does not say" why="The page shows what the operators published. A constraint is named as the operator names it, with no guess at where it is on a map. It gives no advice and makes no estimate of its own." /></>}
        under={<p className="mt-2 text-xs text-muted" data-license-line="1">License: public. File built {F.built.slice(0, 10)}.</p>}
      />

      <form method="get" action="/congestion#top" className="mb-3 flex flex-wrap items-end gap-3 text-sm [&_label]:max-w-full [&_select]:max-w-full" data-congestion-form="1">
        <AutoSubmitSelect name="op" value={op} options={SHOWN.map((o) => ({ value: o.id, label: o.name }))} label="Operator" />
        <AutoSubmitSelect name="year" value={year} options={[{ value: ALL, label: "Every year held" }, ...[...years].reverse().map((y) => ({ value: y, label: y }))]} label="Year" />
        <AutoSubmitSelect name="c" value={ck} options={keys.map((k) => ({ value: k, label: constraintLabel(O.constraints[k]) }))} label="Constraint" />
        <AutoSubmitSelect name="a" value={a} options={placeOptions} label="Place" />
        <AutoSubmitSelect name="b" value={b} options={[{ value: NONE, label: "No second place" }, ...placeOptions.filter((o) => o.value !== a)]} label="Side by side with" />
        <AutoSubmitSelect name="py" value={py} options={[...pyears].reverse().map((y) => ({ value: y, label: y }))} label="Year of the places" />
        <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
      </form>

      <ToolSection title="The constraints that bound most and cost most" id="top">
        {O ? (
          <>
            <p className="mb-2 text-sm" data-held-line="1">{O.constraints_by_year[year] !== undefined ? <>{whole(O.constraints_by_year[year])} constraints bound in {whole(O.hours_by_year[year])} constraint-hours over {O.days_held[year]} days held in {year}{year === years[years.length - 1] ? <span data-window-line="1">, to {localDay(O.last, op)}, the newest day held; the year is not whole</span> : null}.</> : <>Every year held: {years.join(", ")}, the newest day held {localDay(O.last, op)}.</>} {" "}
              <Hint words="(what a constraint is)" why={ELEMENT_WORDS} /> {" "}
              <Hint words="(source)" why={`${src.constraints}. Hours in ${O.time}. ${F.sign_rule}`} /></p>
            {/* Session 9001, row H1: each list has a visible heading, so a reader can tell the two apart. */}
            <h3 className="mb-1 mt-4 font-serif text-base text-accent" data-list-heading="hours">Bound most: ranked by hours bound</h3>
            <ToolTable minWidth={720} caption={`${F.operators.find((o) => o.id === op)?.name}: the constraints that bound most hours, ${yearWords}`} head={head} rows={top.by_hours.map(rowOf)} />
            <h3 className="mb-1 mt-5 font-serif text-base text-accent" data-list-heading="cost">Cost most: ranked by shadow price summed over the hours bound</h3>
            <ToolTable minWidth={720} caption={`${F.operators.find((o) => o.id === op)?.name}: the constraints whose shadow price summed highest, ${yearWords}`} head={head} rows={top.by_cost.map(rowOf)} />
          </>
        ) : <p className="text-sm text-muted">No constraint of this operator is held.</p>}
        {/* Session 10220 (congestion audit, finding 4): SPP's market changed on 1 April 2026. */}
        {op === "spp" ? <p className="mt-2 max-w-3xl text-xs text-muted" data-spp-west="1">{SPP_WEST_WORDS}</p> : null}
        <p className="mt-2 text-sm" data-not-drawn="1">Not drawn: {blank.map((o) => <span key={o.id} className="mr-2 cursor-help text-muted underline decoration-dotted" title={`${o.status}: ${o.why ?? ""}`} data-blank={o.id}>{o.name} ({o.status})</span>)}</p>
      </ToolSection>

      <ToolSection title="When a constraint binds" id="when">
        {C ? (
          <>
            <p className="mb-1 text-sm" data-constraint={ck}><span className="font-medium break-all">{constraintLabel(C)}</span>{C.monitored ? <>: monitored element {C.monitored}</> : null}{C.type ? <>, type {C.type}</> : null}{C.nerc_id ? <>, NERC flowgate {C.nerc_id}</> : null}. Bound {whole(C.hours)} hours from {C.first.slice(0, 10)} to {C.last.slice(0, 10)} <span data-utc-days="1">(days in UTC, not the operator&apos;s clock)</span>. {" "}
              <Hint words="(source)" why={`${src.constraints}. ${F.sign_rule}`} /></p>
            <Heat cells={C.hod_month} k="c" label={`${constraintLabel(C)}: hours bound, by month and hour of the day, every year held`} src={() => `Hours it bound in that hour of the day in that month, every year held summed. ${src.constraints}.`} fmt={whole} note={<>Hours of the day in {O.time}.</>} />
            <ChartFrame title="Hours bound, by month" tip={<Hint words=" (source)" why={`${src.constraints}. A month with no point is a month it did not bind in the day-ahead market.`} />}>
              <LineChart lines={hoursLine} unit="hours" x="month" ariaLabel="Hours the constraint bound by month" />
            </ChartFrame>
          </>
        ) : <p className="text-sm text-muted">No constraint chosen.</p>}
      </ToolSection>

      <ToolSection title="Where congestion adds to the price and where it takes off" id="places">
        <ToolTable minWidth={680} caption={`Hubs and zones by their mean congestion part, ${py}${pwin ? ` (the hours held from ${pwin[0]} to ${pwin[1]})` : " (the days held differ by place: each place's on the hover of its mean LMP)"}, the largest addition first`} head={["Place", "Mean LMP", "Mean congestion part", "Share of the price", "Hours it added", "Hours it took off"]}
          rows={ranked.map(({ p, y }) => {
            const s = `${F.sources[p.id.split(":")[0]].prices}. ${p.time}.`;
            const at = (f: string) => pfKey(PF, ["places", p.id.split(":")[0], { id: p.id }, "by_year", py, f]);
            return { key: p.id, highlight: p.id === a || p.id === b, cells: [
              <a key="n" className="underline" href={`/congestion?op=${op}&year=${year}&c=${encodeURIComponent(ck)}&a=${encodeURIComponent(p.id)}&py=${py}#side`}>{labelOf(p)}</a>,
              <Fig key="l" v={y.lmp_mean} src={`Mean day-ahead LMP over ${y.hours} hours held, ${spanOf(p.id)[0]} to ${spanOf(p.id)[1]}. ${s}`} k={`pl-${p.id}`} check={at("lmp_mean")} fmt={usd} />,
              <Fig key="c" v={y.congestion_mean} src={`Mean congestion part over ${y.hours} hours held; highest ${y.congestion_max}, lowest ${y.congestion_min}. ${s}`} k={`pc-${p.id}`} check={at("congestion_mean")} fmt={usd} />,
              <Fig key="s" v={y.congestion_share_pct} src={`${F.share_rule} ${s}`} k={`ps-${p.id}`} check={at("congestion_share_pct")} fmt={pct} reason={`The mean LMP was not above zero. ${s}`} />,
              <Fig key="u" v={y.hours_congestion_up} src={`Hours whose congestion part was above zero. ${s}`} k={`pu-${p.id}`} check={at("hours_congestion_up")} fmt={whole} />,
              <Fig key="d" v={y.hours_congestion_down} src={`Hours whose congestion part was below zero. ${s}`} k={`pd-${p.id}`} check={at("hours_congestion_down")} fmt={whole} />,
            ] };
          })} />
        {/* Session 10220 (congestion audit, finding 1): what a congestion part is measured against. */}
        <p className="mt-2 max-w-3xl text-xs text-muted" data-reference-line="1">{REFERENCE_WORDS}</p>
      </ToolSection>

      <ToolSection title="Two places side by side" id="side">
        <ChartFrame title="Mean congestion part of the day-ahead price, by month (USD/MWh)" tip={<Hint words=" (source)" why={[A, ...(B ? [B] : [])].map((p) => F.sources[p.id.split(":")[0]].prices).join("; ")} />}>
          <LineChart lines={congLines} unit="USD/MWh" x="month" ariaLabel="Mean congestion part by month" />
        </ChartFrame>
        <p className="mb-2 text-xs text-muted" data-months-line="1">Each point is the mean of the hours held in its month, so the first and the newest month can hold part of a month: {[A, ...(B ? [B] : [])].map((p) => `${p.name} is held from ${localDay(p.first, p.id.split(":")[0])} to ${localDay(p.last, p.id.split(":")[0])}`).join("; ")}.</p>
        <ChartFrame title="Share of the price that was congestion, by month" tip={<Hint words=" (source)" why={F.share_rule} />}>
          <LineChart lines={shareLines} unit="%" x="month" ariaLabel="Congestion share of the price by month" />
        </ChartFrame>
        {[A, ...(B ? [B] : [])].map((p, i) => {
          const g = p.hod_month_congestion_mean[py];
          return g ? <Heat key={p.id} cells={g} k={i ? "pb" : "pa"} label={`${labelOf(p)}: mean congestion part by month and hour of the day, ${py} (USD/MWh)`} src={() => `${F.sources[p.id.split(":")[0]].prices}.`} fmt={usd} note={<>Hours of the day in {p.time}. Positive (adds to the price) in the accent color, negative (takes off) in the second color.</>} />
            : <p key={p.id} className="text-sm text-muted">No hour of {p.name} is held in {py}.</p>;
        })}
      </ToolSection>

      <CongestionDecisions />
      <TableDownloads tables={F.tables} />
      <SourceLine tables={F.tables} note={<>Method: <a href="/data/methods/grid_congestion">the page&apos;s method note</a>. The operators&apos; constraints, shadow prices and price parts as published; the page counts hours, sums and averages them, and computes only the shares it names.</>} />
      </div>
    </ToolPage>
    </Brand>
  );
}
