"use client";
// Session 8013 (chain 505, part C, 19 November 2026): a balancing authority's own facts, and its region's sum, under what
// the network's panel shows today (app/network/Network.tsx). The files are the data machine's (data/regions/authority/,
// docs/state/page_files_regions.md section 10; warehouse/derived/authority_facts.py), read one at a time from
// /grid/authority/<code> when the panel opens. Each block names its table and vintage on hover; a figure a source does
// not hold is said with the file's own reason, never drawn as a zero. Shown only where the whole country's index is on
// the server (the Grid tool), so the panel of /network is as it was.
import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";

type Num = number | null;
type Block = { table?: string; vintage?: string; source?: string; why?: string } & Record<string, unknown>;
type Plant = { plant_id: string; name: string; state: string | null; mw: number; technology_group: string; operator: string | null };
type Step = { year: number; technology_group: string; mw: number; generators: number };
type Partner = { code: string; name: string; exchange_gross_mwh?: number; net_import_mwh?: number; flow_mwh?: number; direction?: string };
type LoadRow = { date: string | null; group: string | null; row_kind: string | null; mw: Num; mw_low: Num; mw_high: Num; document_title: string | null; source_url: string | null };
export type Facts = {
  code: string; name: string; region: string; level: "ba" | "region"; bas?: string[];
  owns: Block & { total_mw?: Num; generators?: Num; capacity_mw?: Record<string, Num>; largest_plants?: Plant[]; basis?: string };
  coming: Block & { additions?: Step[]; retirements?: Step[] };
  burns: Block & { months?: string[]; share_pct?: Record<string, Num>; net_generation_mwh?: Num; co2?: Block & { intensity_kg_per_mwh?: Num } };
  trades: Block & { year?: number; partners?: Partner[]; net_import_share_of_demand_pct?: Num; net_imports_mwh?: Num };
  size: Block & { peak_mw?: Num; peak_local?: string | null; tz?: string | null; growth_year?: number | null; growth_since_2019_pct?: Num };
  large_loads: Block & { count?: number; rows?: LoadRow[] };
};

const SOURCE: Record<string, string> = { natural_gas: "gas", coal: "coal", nuclear: "nuclear", wind: "wind", solar: "solar", hydro: "hydro", storage: "storage", petroleum: "oil", biomass: "biomass", geothermal: "geothermal", other: "other" };
const word = (k: string) => SOURCE[k] ?? k.replace(/_/g, " ");
const mw = (v: number) => Math.round(v).toLocaleString("en-US");
const pct = (v: number) => (Math.abs(v) < 10 ? v.toFixed(1) : Math.round(v).toString());
const tip = (b: Block) => [b.table && `Table: ${b.table}`, b.vintage && `vintage ${b.vintage}`, b.source].filter(Boolean).join("; ");

function useFacts(stem: string | null) {
  const [state, setState] = useState<{ stem: string; facts: Facts | null } | null>(null);
  useEffect(() => {
    if (!stem) return;
    let live = true;
    fetch(`/grid/authority/${stem}`).then((r) => (r.ok ? r.json() : null)).then((j) => {
      if (live) setState({ stem, facts: j && j.code && j.owns ? (j as Facts) : null });
    }).catch(() => { if (live) setState({ stem, facts: null }); });
    return () => { live = false; };
  }, [stem]);
  return state && state.stem === stem ? state : null;
}

function Row({ label, block, children, data }: { label: string; block: Block; children: ReactNode; data: string }) {
  return (
    <div data-facts-block={data}>
      <dt className="cursor-help text-xs text-muted" title={tip(block)}>{label} <span className="text-[10px]">({block.vintage ?? "vintage not given"})</span></dt>
      <dd>{children}</dd>
    </div>
  );
}

const Why = ({ b }: { b: Block }) => <span className="italic text-muted" data-facts-why="1">Not held: {b.why ?? "the file gives no figure"}</span>;

function Body({ f }: { f: Facts }) {
  const caps = Object.entries(f.owns.capacity_mw ?? {}).filter((e): e is [string, number] => typeof e[1] === "number" && e[1] > 0).sort((a, b) => b[1] - a[1]);
  const year = new Date().getUTCFullYear();
  const sum = (s: Step[] | undefined) => {
    const by: Record<string, number> = {};
    for (const x of s ?? []) if (x.year >= year) by[x.technology_group] = (by[x.technology_group] ?? 0) + x.mw;
    return Object.entries(by).sort((a, b) => b[1] - a[1]);
  };
  const adds = sum(f.coming.additions), rets = sum(f.coming.retirements);
  const addAll = adds.reduce((s, [, v]) => s + v, 0), retAll = rets.reduce((s, [, v]) => s + v, 0);
  const lastYear = Math.max(...[...(f.coming.additions ?? []), ...(f.coming.retirements ?? [])].map((x) => x.year), year);
  const shares = Object.entries(f.burns.share_pct ?? {}).filter((e): e is [string, number] => typeof e[1] === "number" && Math.abs(e[1]) >= 0.05).sort((a, b) => b[1] - a[1]);
  const co2 = f.burns.co2;
  const partners = (f.trades.partners ?? []).slice(0, 5);
  const s = f.size;
  return (
    <dl className="space-y-1.5">
      <Row label="What it owns" block={f.owns} data="owns">
        {typeof f.owns.total_mw === "number" ? (
          <>
            {mw(f.owns.total_mw)} MW in {(f.owns.generators ?? 0).toLocaleString("en-US")} generators{caps.length ? <>: {caps.slice(0, 4).map(([k, v]) => `${word(k)} ${mw(v)}`).join(", ")}{caps.length > 4 ? ", and others" : ""}</> : null}.
            {f.owns.largest_plants?.length ? (
              <details className="text-xs" data-facts-plants={f.owns.largest_plants.length}>
                <summary className="cursor-pointer text-accent">The {f.owns.largest_plants.length} largest plants</summary>
                <ol className="mt-0.5 list-decimal space-y-0.5 pl-5 tabular-nums">
                  {f.owns.largest_plants.map((p) => <li key={p.plant_id}>{p.name}{p.state ? `, ${p.state}` : ""}: {mw(p.mw)} MW, {word(p.technology_group)}{p.operator ? <span className="text-muted"> ({p.operator})</span> : null}</li>)}
                </ol>
              </details>
            ) : null}
          </>
        ) : <Why b={f.owns} />}
      </Row>
      <Row label={`Coming and going, ${year} to ${lastYear}`} block={f.coming} data="coming">
        {f.coming.why && !adds.length && !rets.length ? <Why b={f.coming} /> : (
          <>
            Planned additions {mw(addAll)} MW{adds.length ? <> ({adds.slice(0, 3).map(([k, v]) => `${word(k)} ${mw(v)}`).join(", ")}{adds.length > 3 ? ", and others" : ""})</> : null}; planned retirements {mw(retAll)} MW{rets.length ? <> ({rets.slice(0, 3).map(([k, v]) => `${word(k)} ${mw(v)}`).join(", ")}{rets.length > 3 ? ", and others" : ""})</> : null}.
          </>
        )}
      </Row>
      <Row label={`What it generates${f.burns.months?.length ? `, ${f.burns.months[0]} to ${f.burns.months.at(-1)}` : ""}`} block={f.burns} data="burns">
        {shares.length ? <>{shares.slice(0, 4).map(([k, v]) => `${word(k)} ${pct(v)}%`).join(", ")}{shares.length > 4 ? ", and others" : ""}.</> : <Why b={f.burns} />}
        {co2 ? (
          <span className="block text-xs" data-facts-co2={typeof co2.intensity_kg_per_mwh === "number" ? co2.intensity_kg_per_mwh : "none"} title={tip(co2)}>
            {typeof co2.intensity_kg_per_mwh === "number" ? <>Carbon intensity over those months: {mw(co2.intensity_kg_per_mwh)} kg CO2/MWh (EIA&apos;s estimate).</> : <span className="italic text-muted">Carbon intensity not held: {co2.why ?? "the file gives none"}</span>}
          </span>
        ) : null}
      </Row>
      <Row label={`Whom it trades with${f.trades.year ? `, ${f.trades.year}` : ""}`} block={f.trades} data="trades">
        {partners.length ? (
          <>
            <ul className="tabular-nums">
              {partners.map((p) => (
                <li key={p.code} className="flex justify-between gap-2">
                  <span>{p.name} <span className="font-mono text-xs text-muted">{p.code}</span></span>
                  <span className="whitespace-nowrap">{typeof p.net_import_mwh === "number" ? (p.net_import_mwh >= 0 ? `${mw(p.net_import_mwh)} MWh in, net` : `${mw(-p.net_import_mwh)} MWh out, net`) : typeof p.flow_mwh === "number" ? `${mw(p.flow_mwh)} MWh ${p.direction ?? ""}` : ""}</span>
                </li>
              ))}
            </ul>
            <span className="block text-xs">{typeof f.trades.net_import_share_of_demand_pct === "number" ? <>Net imports met {pct(f.trades.net_import_share_of_demand_pct)} percent of its demand.</> : <span className="italic text-muted">No share of demand: {f.trades.why ?? "its demand is not held for the year"}</span>}</span>
          </>
        ) : <Why b={f.trades} />}
      </Row>
      <Row label="Its size" block={s} data="size">
        {typeof s.peak_mw === "number" ? (
          <>Record demand {mw(s.peak_mw)} MW{s.peak_local ? <>, {s.peak_local} local time</> : null}. {typeof s.growth_since_2019_pct === "number" ? <>Demand in {s.growth_year} was {s.growth_since_2019_pct >= 0 ? "up" : "down"} {pct(Math.abs(s.growth_since_2019_pct))} percent on 2019.</> : <span className="italic text-muted">No growth since 2019: {s.why ?? "2019 or a later whole year is not held"}.</span>}</>
        ) : <Why b={s} />}
      </Row>
      <Row label="What is said of large loads there" block={f.large_loads} data="large-loads">
        {f.large_loads.count ? (
          <details className="text-xs" data-facts-loads={f.large_loads.count}>
            <summary className="cursor-pointer text-accent">{f.large_loads.count} public row{f.large_loads.count === 1 ? "" : "s"}, newest first</summary>
            <ul className="mt-0.5 space-y-0.5">
              {[...(f.large_loads.rows ?? [])].sort((a, b) => (b.date ?? "").localeCompare(a.date ?? "")).slice(0, 8).map((r, i) => (
                <li key={i}>{r.date ?? "undated"}{r.group ? `, ${r.group}` : ""}: {r.source_url ? <a href={r.source_url} rel="noopener noreferrer" target="_blank">{r.document_title ?? "the document"}</a> : r.document_title ?? "a document"}{typeof r.mw === "number" ? ` (${mw(r.mw)} MW)` : typeof r.mw_low === "number" && typeof r.mw_high === "number" ? ` (${mw(r.mw_low)} to ${mw(r.mw_high)} MW)` : ""}</li>
              ))}
            </ul>
          </details>
        ) : <Why b={f.large_loads} />}
      </Row>
    </dl>
  );
}

/** The authority's facts and, in a fold, its region's sum. `code` is the authority's EIA-930 code, `region` its region's. */
export function AuthorityFacts({ code, region }: { code: string; region: string | null }) {
  const own = useFacts(code.toLowerCase());
  const reg = useFacts(region ? `region-${region.toLowerCase()}` : null);
  return (
    <div className="mt-2 border-t border-rule pt-2 text-sm" data-authority-facts={code}>
      <div className="mb-1 font-serif text-base text-accent">Its own facts</div>
      {!own ? <p className="text-xs text-muted">Reading its facts&hellip;</p> : own.facts ? <Body f={own.facts} /> : <p className="text-xs italic text-muted" data-facts-none={code}>Not held: the server has no facts file for {code}.</p>}
      {region && reg?.facts ? (
        <details className="mt-2 text-sm" data-region-facts={region}>
          <summary className="cursor-pointer text-accent">Its region, {reg.facts.name}, summed{reg.facts.bas?.length ? ` over ${reg.facts.bas.length} authorit${reg.facts.bas.length === 1 ? "y" : "ies"}` : ""}</summary>
          <div className="mt-1"><Body f={reg.facts} /></div>
        </details>
      ) : null}
      <p className="mt-1 text-[11px] text-muted">From EIA-860M, Form EIA-930 and the warehouse&apos;s public large-load rows; hover a heading for its table and vintage. Method: <Link href="/data/methods/authority_facts">authority facts</Link>.</p>
    </div>
  );
}
