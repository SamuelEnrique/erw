import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { LineChart, type Line } from "@/components/LineChart";
import { ChartFrame, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { STATES } from "@/lib/regions";
import raw from "@/data/storage/places.json";
import { PlacesDecisions } from "./Decisions";

// Session 8014 (chain 581, part F1): batteries by balancing authority and by state, any one or two side by side,
// beside the seven grids' figures /storage has. Reads data/storage/places.json (warehouse/derived/storage_places.py,
// method docs/methods/storage_places.md): every battery unit of EIA-860M (prime mover BA, the units /storage counts),
// placed by its own authority and state. Nothing is estimated: MWh only where EIA gives it. In review, in no menu.
export const metadata: Metadata = { title: "Batteries in every authority and state", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Year = { mw: number | null; mwh?: number | null; units: number; under_construction_mw?: number | null };
type Place = { operating_mw: number | null; operating_units: number; operating_mwh: number | null; operating_mw_with_mwh: number | null; units_without_mwh: number;
  planned_mw: number | null; planned_units: number; by_year_of_start: Record<string, Year>; planned_by_year: Record<string, Year>;
  code?: string; name?: string | null; region?: string | null; grid?: string | null; state?: string };
type File = { built: string; method: string; tables: string[]; source: string; vintage: string; units: string; rule: string; us: Place;
  authorities: Record<string, Place>; states: Record<string, Place> };
const F = raw as unknown as File;
type Query = Record<string, string | string[] | undefined>;
const one = (q: Query, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const SRC = `${F.source}, edition ${F.vintage}, as the ERW's tables eia860m_operating_generators and eia860m_planned_generators hold it. ${F.rule}`;

const ids = ["us", ...Object.keys(F.authorities).map((c) => `ba:${c}`), ...Object.keys(F.states).map((s) => `st:${s}`)];
const placeOf = (id: string): Place => (id === "us" ? F.us : id.startsWith("ba:") ? F.authorities[id.slice(3)] : F.states[id.slice(3)]);
const nameOf = (id: string): string => {
  if (id === "us") return "United States";
  if (id.startsWith("ba:")) { const p = F.authorities[id.slice(3)]; return p.code === "not named" ? "No authority named in EIA-860M" : `${p.name ?? p.code} (${p.code})${p.grid ? `, ${p.grid}` : ""}`; }
  return STATES[id.slice(3)] ?? id.slice(3);
};

function Fig({ v, k, src, fmt = whole, reason }: { v: number | null | undefined; k: string; src: string; fmt?: (v: number) => string; reason?: string }) {
  if (v === null || v === undefined) return <span className="cursor-help text-muted" title={reason ?? `Not held. ${src}`} data-not-held={k}>not held</span>;
  return <span className="cursor-help" title={src} data-fig={k}>{fmt(v)}</span>;
}

/** Operating MW by the end of each year of start, summed from the units operating today (a unit retired since is not in it). */
function cumulative(p: Place): { t: number; v: number }[] {
  let s = 0;
  return Object.entries(p.by_year_of_start).filter(([y]) => /^\d{4}$/.test(y)).map(([y, r]) => { s += r.mw ?? 0; return { t: Date.UTC(Number(y), 11, 31) / 1000, v: s }; });
}

export default async function StoragePlaces({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const a = ids.includes(one(q, "a") ?? "") ? (one(q, "a") as string) : "ba:ERCO";
  const b = ids.includes(one(q, "b") ?? "") && one(q, "b") !== a ? (one(q, "b") as string) : "ba:CISO";
  const A = placeOf(a), B = placeOf(b);
  const options = ids.map((id) => ({ value: id, label: `${id === "us" ? "" : id.startsWith("ba:") ? "Authority: " : "State: "}${nameOf(id)}` }));
  const years = [...new Set([...Object.keys(A.planned_by_year), ...Object.keys(B.planned_by_year)])].sort();
  const lines: Line[] = [{ label: nameOf(a), color: "accent", points: cumulative(A) }, { label: nameOf(b), color: "series-3", points: cumulative(B) }];
  const rows = (pairs: [string, string, (p: Place) => number | null, string?][]) => pairs.map(([key, label, get, more]) => ({ key, cells: [label,
    <Fig key="a" v={get(A)} k={`sp-a-${key}`} src={`${more ?? ""} ${SRC}`} />, <Fig key="b" v={get(B)} k={`sp-b-${key}`} src={`${more ?? ""} ${SRC}`} />] }));
  const ranked = Object.values(F.authorities).filter((p) => p.code !== "not named").sort((x, y) => (y.operating_mw ?? 0) - (x.operating_mw ?? 0));
  const rankedSt = Object.values(F.states).sort((x, y) => (y.operating_mw ?? 0) - (x.operating_mw ?? 0));

  return (
    <Brand>
    <ToolPage>
      <div data-storage-places="1">
      <ToolHeader
        title="Batteries in every authority and state"
        crumb={<a href="/storage" className="underline">Battery storage</a>}
        lead={<>Every battery of EIA&apos;s monthly generator inventory, by the balancing authority and the state EIA gives it: what operates, in power and energy, when it started, and what is planned. Any two side by side; the seven grids are among the authorities, as{" "}
          <a className="underline" href="/storage">the storage page</a> counts them. <Hint words="What is counted" why={F.rule} /></>}
        under={<p className="mt-2 text-xs text-muted" data-license-line="1">License: public (EIA). EIA-860M edition {F.vintage}; file built {F.built.slice(0, 10)}.</p>}
      />
      <form method="get" action="/storage/places#side" className="mb-3 flex flex-wrap items-end gap-3 text-sm [&_label]:max-w-full [&_select]:max-w-full" data-storage-places-form="1">
        <AutoSubmitSelect name="a" value={a} options={options} label="Place A" />
        <AutoSubmitSelect name="b" value={b} options={options.filter((o) => o.value !== a)} label="Place B" />
        <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
      </form>

      <ToolSection title="Side by side" id="side">
        <ToolTable minWidth={520} caption={`${nameOf(a)} and ${nameOf(b)}`} head={["", `A: ${nameOf(a)}`, `B: ${nameOf(b)}`]}
          rows={[
            ...rows([["mw", "Operating, MW", (p) => p.operating_mw], ["units", "Operating units", (p) => p.operating_units],
              ["mwh", "Operating energy, MWh (where EIA gives it)", (p) => p.operating_mwh, "Summed over the units that give an energy capacity."],
              ["mwwith", "MW of the units that give MWh", (p) => p.operating_mw_with_mwh], ["planned", "Planned and under construction, MW", (p) => p.planned_mw],
              ["punits", "Planned units", (p) => p.planned_units]]),
          ]} />
        <ChartFrame title="Operating battery MW by year of start (units operating today)" tip={<Hint words=" (source)" why={`Each year adds the MW of the units operating today that started in it; a unit retired since is not counted. ${SRC}`} />}>
          <LineChart lines={lines} unit="MW" x="year" ariaLabel={`Operating battery MW by year of start, ${nameOf(a)} and ${nameOf(b)}`} />
        </ChartFrame>
        <ToolTable minWidth={420} caption="Planned battery MW by EIA's planned year" head={["Year", `A: ${nameOf(a)}`, `B: ${nameOf(b)}`]}
          rows={years.map((y) => ({ key: y, cells: [y,
            <Fig key="a" v={A.planned_by_year[y]?.mw ?? null} k={`pl-a-${y}`} src={`Of which under construction: ${A.planned_by_year[y]?.under_construction_mw ?? 0} MW. ${SRC}`} reason="None planned for this year." />,
            <Fig key="b" v={B.planned_by_year[y]?.mw ?? null} k={`pl-b-${y}`} src={`Of which under construction: ${B.planned_by_year[y]?.under_construction_mw ?? 0} MW. ${SRC}`} reason="None planned for this year." />] }))} />
      </ToolSection>

      <ToolSection title="Every authority" id="authorities">
        <ToolTable minWidth={640} caption="Balancing authorities by operating battery MW" head={["Authority", "Grid", "Operating MW", "MWh (where given)", "Planned MW"]}
          rows={ranked.map((p, i) => ({ key: p.code ?? String(i), highlight: `ba:${p.code}` === a || `ba:${p.code}` === b, cells: [
            <a key="n" className="underline" href={`/storage/places?a=ba:${p.code}&b=${b === `ba:${p.code}` ? a : b}`} data-rank={i + 1}>{i + 1}. {p.name ?? p.code} ({p.code})</a>,
            p.grid ?? "none of the seven", <Fig key="m" v={p.operating_mw} k={`ba-${p.code}-mw`} src={SRC} />, <Fig key="h" v={p.operating_mwh} k={`ba-${p.code}-mwh`} src={SRC} reason="No unit here gives an energy capacity." />,
            <Fig key="p" v={p.planned_mw} k={`ba-${p.code}-pl`} src={SRC} />] }))} />
        <p className="mt-1 text-xs text-muted">Units with no authority in EIA-860M: <Fig v={F.authorities["not named"]?.operating_mw ?? null} k="ba-none-mw" src={SRC} reason="None." /> MW operating.</p>
      </ToolSection>

      <ToolSection title="Every state" id="states">
        <ToolTable minWidth={560} caption="States by operating battery MW" head={["State", "Operating MW", "MWh (where given)", "Planned MW"]}
          rows={rankedSt.map((p, i) => ({ key: p.state ?? String(i), cells: [
            <a key="n" className="underline" href={`/storage/places?a=st:${p.state}&b=${b}`}>{i + 1}. {STATES[p.state ?? ""] ?? p.state}</a>,
            <Fig key="m" v={p.operating_mw} k={`st-${p.state}-mw`} src={SRC} />, <Fig key="h" v={p.operating_mwh} k={`st-${p.state}-mwh`} src={SRC} reason="No unit here gives an energy capacity." />,
            <Fig key="p" v={p.planned_mw} k={`st-${p.state}-pl`} src={SRC} />] }))} />
      </ToolSection>

      <PlacesDecisions />
      <TableDownloads tables={F.tables} />
      <SourceLine tables={F.tables} note={<>Method: <a href="/data/methods/storage_places">the page&apos;s method note</a>. EIA-860M&apos;s figures summed by place; nothing estimated.</>} />
      </div>
    </ToolPage>
    </Brand>
  );
}
