import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Brand } from "@/components/Brand";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { LineChart, type Line } from "@/components/LineChart";
import { ChartFrame, HeadlineNumber, HeadlineRow, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { FUEL_COLOR, FUEL_WORDS } from "@/lib/mixpage";
import {
  CO2_WORDS, GAS_WORDS, GEN_SOURCES, SECTORS, SEDS_WORDS, TECH_WORDS, atYear, byYearTable, genShare, gridRegion, lastCo2, lastWholeYear, monthPoints,
  readIndex, readState, sharePoints, wholeGenYears, yearOfMonths, yearPoints, type Arr, type StateFile,
} from "@/lib/states";
import { StatesDecisions } from "./Decisions";

// Session 8014 (chain 581, part B): "Every state on one page". A reader chooses a state, or two side by side, and sees
// what it runs on and how that changed since 2001, what its homes, businesses and industry buy and pay, what is built
// and what is coming, who operates its grid, its emissions, its natural gas and its total energy, and its large-load
// law and severance tax where the ERW holds one. The page reads data/states/<st>.json (the data machine's files:
// warehouse/derived/states_page.py; contract docs/state/page_files_states.md; method docs/methods/states_page.md) and
// draws the figures as they stand; every figure says its source on hover; a figure the file does not hold is "not
// held" with the reason. Monthly: no public source gives a state's generation by the hour, and the page says so once.
// Facts and no view. In review (no line in lib/release.ts), in no menu (chain 581).
export const metadata: Metadata = { title: "Every state", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Query = Record<string, string | string[] | undefined>;
const one = (q: Query, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
const NONE = "none";
const FROM_YEARS = ["2001", "2005", "2010", "2015", "2020"];

const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const one1 = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const twh = (v: number) => (v / 1e6).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const gw = (v: number) => (v / 1e3).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const pct = (v: number) => `${v.toFixed(1)}%`;
const cents = (v: number) => `${(v / 10).toFixed(2)}`;
const bn = (v: number) => `$${(v / 1e9).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} bn`;
const mt = (v: number) => (v / 1e6).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const bcf = (v: number) => (v / 1e3).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const monthWords = (m: string) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1, 1)).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
const span = (a: string, b: string) => `${monthWords(a)} to ${monthWords(b)}`;

/** A figure with its source on hover; "not held" with the reason where the file has none. */
function Fig({ v, src, k, fmt, reason }: { v: number | null | undefined; src: string; k: string; fmt: (v: number) => string; reason?: string }) {
  if (v === null || v === undefined || Number.isNaN(v)) return <span className="cursor-help text-muted" title={reason ?? `Not held in the file. ${src}`} data-not-held={k}>not held</span>;
  return <span className="cursor-help" title={src} data-fig={k}>{fmt(v)}</span>;
}

/** The words of a part's source with its ERW table and vintage, for a hover. */
const srcOf = (p: { source?: string; table: string; vintage?: string }, more?: string) =>
  `${p.source ?? ""}, as the ERW's table ${p.table} holds it${p.vintage ? ` (newest: ${p.vintage})` : ""}.${more ? ` ${more}` : ""}`;

function Form({ children, anchor, keep }: { children: ReactNode; anchor: string; keep: Record<string, string> }) {
  return (
    <form method="get" action={`/states#${anchor}`} className="mb-3 flex flex-wrap items-end gap-3 text-sm [&_label]:max-w-full [&_select]:max-w-full" data-states-form={anchor}>
      {Object.entries(keep).map(([k, v]) => <input key={k} type="hidden" name={k} value={v} />)}
      {children}
      <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
    </form>
  );
}

function Missing({ what, reason }: { what: string; reason?: string }) {
  return <p className="my-2 text-sm text-muted" data-part-missing={what} title={reason}>Not held for this place: {reason ?? "the file holds no figure"}.</p>;
}

// session 10223 (the states audit, findings 3 and 4): what the groups hold, and how a source with a month EIA withholds
// is summed (docs/methods/generation_mix.md: oil and other = PET + OOG + HPS + OTH; small-scale solar not included;
// not itemized = EIA's all-fuels total less the groups)
const WHAT_SOURCES_HOLD = "A source can be below zero: pumped storage uses more than it makes, and it is counted in Oil and other (EIA's code HPS), so that line can fall below zero. Solar is EIA's utility-scale solar: small-scale solar, such as rooftop panels, is not in EIA's state figures here.";
// session 11407 (finding 4 readied for Samuel's ruling): a source is printed for the twelve months only when all twelve
// of its months are held, as a whole year already is
const SUMMED_OVER_MONTHS = "A source is printed for the twelve months only when EIA prints it in all twelve: in a month EIA withholds a source, its generation is in Not itemized by EIA, and the source is not held for the twelve months. The total still counts every figure EIA prints.";
const NOT_ALL_TWELVE = (what: string, name: string) => `EIA does not print ${what} generation for ${name} in all twelve of these months (a month it withholds is in Not itemized by EIA).`;

/** What one place runs on: the stacked months and the last twelve months by source. */
function RunsOn({ f, from }: { f: StateFile; from: number }) {
  const g = f.generation;
  if (!g.months) return <Missing what="generation" reason={g.reason} />;
  const shown = GEN_SOURCES.filter((s) => (g.by_source[s] ?? []).some((v) => v !== null && v !== 0));
  const monthly: Line[] = shown.map((s) => ({ label: FUEL_WORDS[s] ?? s, color: FUEL_COLOR[s] ?? "muted", points: monthPoints(g.months, g.by_source[s], from, 1e-3), gap: 40 * 86400 }));
  const years = wholeGenYears(f);
  const yearly: Line[] = shown.map((s) => ({ label: FUEL_WORDS[s] ?? s, color: FUEL_COLOR[s] ?? "muted", points: yearPoints(years, years.map((y) => atYear(g.years, g.annual[s], y)), 1e-6) }));
  const src = srcOf(g);
  return (
    <>
      <ChartFrame title={`${f.name}: net generation by source, TWh a year`} tip={<Hint words=" (source)" why={`${src} Whole years only: a year is drawn for a source when all twelve of its months are held. ${WHAT_SOURCES_HOLD}`} />}>
        <LineChart lines={yearly} unit="TWh" x="year" ariaLabel={`Net generation by source by year, ${f.name}`} />
      </ChartFrame>
      <ChartFrame title={`${f.name}: net generation by source, GWh a month`} tip={<Hint words=" (source)" why={`${src} A month EIA prints no figure for a source is a gap in its line.`} />}>
        <LineChart lines={monthly} unit="GWh" x="month" ariaLabel={`Net generation by source by month, ${f.name}`} />
      </ChartFrame>
      <ToolTable
          minWidth={320}
          caption={`${f.name}: the last twelve months, ${span(g.last12.from, g.last12.to)}`}
        head={["Source", "TWh", "Share"]}
        rows={[...GEN_SOURCES.map((s) => ({ key: s, cells: [FUEL_WORDS[s] ?? s,
          <Fig key="v" v={g.last12.mwh[s]} src={src} k={`g12-${f.state}-${s}`} fmt={twh} reason={`${NOT_ALL_TWELVE((FUEL_WORDS[s] ?? s).toLowerCase(), f.name)} ${src}`} />,
          <Fig key="s" v={g.last12.share_pct[s]} src={`The source's twelve months over the twelve months' total. ${SUMMED_OVER_MONTHS} ${src}`} k={`g12s-${f.state}-${s}`} fmt={pct} reason={NOT_ALL_TWELVE((FUEL_WORDS[s] ?? s).toLowerCase(), f.name)} />] })),
          { key: "total", highlight: true, cells: ["All sources", <Fig key="v" v={g.last12.total_mwh} src={`The sum of every figure EIA prints for the twelve months, a source not held among them. ${src}`} k={`g12t-${f.state}`} fmt={twh} />, "100%"] }]}
      />
    </>
  );
}

/** How the mix changed: each source's share of a whole year, at chosen years since 2001. */
function Changed({ f }: { f: StateFile }) {
  const years = wholeGenYears(f);
  if (!years.length) return <Missing what="generation-years" reason={f.generation.reason} />;
  const pick = [years[0], "2005", "2010", "2015", "2020", years[years.length - 1]].filter((y, i, a) => years.includes(y) && a.indexOf(y) === i);
  const src = srcOf(f.generation, "A year is shown only when all twelve of its months are held.");
  return (
    <ToolTable
      minWidth={640}
      caption={`${f.name}: each source's share of the year's net generation`}
      head={["Source", ...pick]}
      rows={[...GEN_SOURCES.map((s) => ({ key: s, cells: [FUEL_WORDS[s] ?? s, ...pick.map((y) => <Fig key={y} v={genShare(f, s, y)} src={src} k={`gy-${f.state}-${s}-${y}`} fmt={pct} reason={`EIA prints no ${(FUEL_WORDS[s] ?? s).toLowerCase()} generation for ${f.name} in every month of ${y}.`} />)] })),
        { key: "total", highlight: true, cells: ["All sources, TWh", ...pick.map((y) => <Fig key={y} v={atYear(f.generation.years, f.generation.annual.total, y)} src={src} k={`gyt-${f.state}-${y}`} fmt={twh} />)] }]}
    />
  );
}

function Buys({ f }: { f: StateFile }) {
  const r = f.retail;
  if (!r.months) return <Missing what="retail" reason={r.reason} />;
  const src = srcOf(r, `EIA's average price as the ERW's table ${r.price_table} holds it. ${r.revenue_note}`);
  return (
    <ToolTable
      minWidth={640}
      caption={`${f.name}: what each sector bought and paid, ${span(r.last12.from, r.last12.to)}`}
      head={["Sector", "Sold (TWh)", "Paid", "Average price (cents a kWh)", `Customers, ${r.customers.month ? monthWords(r.customers.month) : ""}`]}
      rows={SECTORS.map((s) => { const b = r.last12.by_sector[s.key]; return { key: s.key, highlight: s.key === "all", cells: [s.label,
        <Fig key="s" v={b.sales_mwh} src={src} k={`r-${f.state}-${s.key}-s`} fmt={twh} />,
        <Fig key="r" v={b.revenue_usd} src={src} k={`r-${f.state}-${s.key}-r`} fmt={bn} />,
        <Fig key="p" v={b.price_usd_per_mwh} src={`The twelve months' revenue over their sales. ${src}`} k={`r-${f.state}-${s.key}-p`} fmt={cents} reason={b.sales_mwh === 0 ? "No sales in these months, so no price." : undefined} />,
        <Fig key="c" v={r.customers.by_sector[s.key]} src={src} k={`r-${f.state}-${s.key}-c`} fmt={whole} />] }; })}
    />
  );
}

function Built({ f }: { f: StateFile }) {
  const p = f.plants;
  if (!p.largest) return <Missing what="plants" reason={p.reason} />;
  const src = srcOf(p);
  const techs = Object.keys(p.capacity_by_technology);
  const coming = byYearTable(p.coming_by_year);
  const going = byYearTable(p.retiring_by_year);
  const gone = byYearTable(p.retired_by_year);
  const cell = (t: Record<string, Record<string, { nameplate_mw: number | null }>>, y: string, g: string, k: string, s: string) =>
    // session 8014 (part G, row G1): a year and source with no unit in EIA-860M is "none" (EIA lists no such unit), not
    // "not held" (which says the source does not cover it)
    t[y]?.[g] ? <Fig key={y} v={t[y][g].nameplate_mw ?? null} src={s} k={k} fmt={whole} /> : <span key={y} className="cursor-help text-muted" title={`EIA-860M lists no such unit for this year. ${s}`} data-none={k}>none</span>;
  return (
    <>
      <ToolTable
          minWidth={320}
          caption={`${f.name}: operating capacity by source, EIA-860M of ${p.vintage}`}
        head={["Source", "Nameplate (MW)", "Net summer (MW)", "Generators"]}
        rows={[...techs.map((t) => { const c = p.capacity_by_technology[t]; return { key: t, cells: [TECH_WORDS[t] ?? t,
          <Fig key="n" v={c.nameplate_mw} src={src} k={`c-${f.state}-${t}`} fmt={whole} />, <Fig key="s" v={c.net_summer_mw} src={src} k={`cs-${f.state}-${t}`} fmt={whole} />,
          `${c.generators.toLocaleString("en-US")}${c.energy_mwh ? ` (${whole(c.energy_mwh)} MWh)` : ""}`] }; }),
          { key: "all", highlight: true, cells: ["All sources", <Fig key="n" v={p.capacity_total_mw} src={src} k={`c-${f.state}-all`} fmt={whole} />, "", `${p.plants.toLocaleString("en-US")} plants`] }]}
      />
      <h3 className="mb-1 mt-5 font-serif text-base text-accent">The ten largest plants</h3>
      <ToolTable
        minWidth={720}
        caption={`${f.name}: the ten largest operating plants by nameplate capacity`}
        head={["Plant", "Mostly", "Nameplate (MW)", "County", "Operator", "Balancing authority"]}
        rows={p.largest.map((r, i) => ({ key: r.plant_id, cells: [<span key="n" title={`EIA plant ${r.plant_id}, ${r.generators} generators. ${src}`} data-plant-rank={i + 1}>{i + 1}. {r.name}</span>,
          TECH_WORDS[r.technology_group] ?? r.technology_group, <Fig key="m" v={r.nameplate_mw} src={src} k={`pl-${f.state}-${i}`} fmt={whole} />, r.county, r.operator, r.balancing_authority ?? "not named"] }))}
      />
      <h3 className="mb-1 mt-5 font-serif text-base text-accent">What is coming: planned and under construction, by planned year (MW)</h3>
      {coming.years.length ? <ToolTable minWidth={640} caption={`${f.name}: planned generators by the year EIA lists for their start`} head={["Source", ...coming.years]}
        rows={coming.groups.map((g) => ({ key: g, cells: [TECH_WORDS[g] ?? g, ...coming.years.map((y) => cell(p.coming_by_year, y, g, `cm-${f.state}-${g}-${y}`, `Nameplate MW, planned or under construction. ${srcOf({ ...p, table: p.planned_table })}`))] }))} />
        : <Missing what="coming" reason="EIA-860M lists no planned generator here" />}
      <h3 className="mb-1 mt-5 font-serif text-base text-accent">What is going: planned retirements by year (MW)</h3>
      {going.years.length ? <ToolTable minWidth={640} caption={`${f.name}: operating generators with a planned retirement date`} head={["Source", ...going.years]}
        rows={going.groups.map((g) => ({ key: g, cells: [TECH_WORDS[g] ?? g, ...going.years.map((y) => cell(p.retiring_by_year, y, g, `go-${f.state}-${g}-${y}`, `Nameplate MW with a planned retirement in the year. ${src}`))] }))} />
        : <Missing what="going" reason="EIA-860M lists no planned retirement here" />}
      {gone.years.length ? <p className="mt-2 text-xs text-muted">Retired already, in EIA-860M&apos;s retired sheet: {gone.years.map((y) => `${y}: ${gone.groups.filter((g) => p.retired_by_year[y][g]).map((g) => `${TECH_WORDS[g] ?? g} ${whole(p.retired_by_year[y][g].nameplate_mw ?? 0)} MW`).join(", ")}`).join("; ")}. <Hint words="(which retirements)" why={`${p.retired_note} ${srcOf({ ...p, table: p.retired_table })}`} /></p> : null}
    </>
  );
}

// session 10223 (the states audit, finding 1): EIA's state profile lists net interstate trade among the disposition, so
// it is out less in: positive where a state sent more to other states than it took in. The files' note (built before
// this) said the opposite; the page says it here until the files are rebuilt with the builder's corrected note.
const TRADE_NOTE = "Net interstate trade is EIA's figure, a line of the disposition: positive where the state sent more electricity to other states than it took in from them, below zero where it took in more.";

function Operates({ f }: { f: StateFile }) {
  const s = f.serving;
  if (!s.by_authority) return <Missing what="serving" reason={s.reason} />;
  const src = srcOf(s, s.basis);
  const d = f.disposition;
  const dy = d.years ? d.years.slice(-3) : [];
  return (
    <>
      <ToolTable
        minWidth={640}
        caption={`${f.name}: who operates the grid its people are on, by county population ${s.population_year}`}
        head={["Balancing authority", "One of the seven grids", "Counties", "Share of the people"]}
        rows={s.by_authority.map((a) => ({ key: a.code ?? "none", cells: [
          a.code ? <span key="n" title={`${a.name ?? a.code}, in EIA's region ${a.region ?? "not named"}. ${src}`}>{a.name ?? a.code} ({a.code})</span> : <span key="n" className="text-muted" title={a.reason ?? ""}>No authority named</span>,
          a.grid ?? "none", `${a.counties}${a.shared_counties ? ` (${a.shared_counties} shared)` : ""}`,
          <Fig key="s" v={a.share_pct} src={src} k={`sv-${f.state}-${a.code ?? "none"}`} fmt={pct} reason={a.reason ?? undefined} />] }))}
      />
      {d.years ? (
        <ToolTable
          caption={`${f.name}: where its electricity came from and went, the state profile`}
          head={["MWh a year", ...dy]}
          rows={[["total_net_generation", "Net generation in the state"], ["full_service_providers", "Sold by full-service providers"], ["energy_only_providers", "Sold by energy-only providers"], ["net_interstate_trade", "Net interstate trade (out less in)"], ["estimated_losses", "Estimated losses"]].map(([k, label]) => ({ key: k, cells: [label,
            ...dy.map((y) => <Fig key={y} v={atYear(d.years, d.values[k], y)} src={srcOf(d, TRADE_NOTE)} k={`dp-${f.state}-${k}-${y}`} fmt={whole} />)] }))}
        />
      ) : <Missing what="disposition" reason={d.reason} />}
    </>
  );
}

function Emissions({ f }: { f: StateFile }) {
  const c = f.co2;
  if (!c.years) return <Missing what="co2" reason={c.reason} />;
  const src = srcOf(c);
  const fuels = Object.keys(c.tons_by_fuel).filter((k) => k !== "all");
  const lines: Line[] = [{ label: "All fuels", color: "accent", points: yearPoints(c.years, c.tons_by_fuel.all, 1e-6) },
    ...fuels.map((k, i) => ({ label: CO2_WORDS[k] ?? k, color: ["series-1", "series-3", "series-5", "series-6"][i % 4], points: yearPoints(c.years, c.tons_by_fuel[k], 1e-6) }))];
  return (
    <ChartFrame title={`${f.name}: carbon dioxide from power plants, million metric tons a year`} tip={<Hint words=" (source)" why={src} />}>
      <LineChart lines={lines} unit="Mt CO2" x="year" ariaLabel={`Carbon dioxide from power by fuel by year, ${f.name}`} />
    </ChartFrame>
  );
}

function GasAndEnergy({ f }: { f: StateFile }) {
  const g = f.gas, e = f.energy;
  const gy = lastWholeYear(g.months);
  const gsrc = srcOf(g, `Production as the ERW's table ${g.production_table} holds it.`);
  const ey = e.years ? e.years[e.years.length - 1] : null;
  const esrc = srcOf(e, `Sectors from ${e.sector_tables.join(" and ")}.`);
  return (
    <>
      {g.months && gy ? (
        <ToolTable
          minWidth={320}
          caption={`${f.name}: natural gas used and produced, ${gy} (billion cubic feet)`}
          head={["", `${gy}`]}
          rows={[...Object.keys(GAS_WORDS).map((k) => ({ key: k, cells: [`Used by ${GAS_WORDS[k].toLowerCase()}`, <Fig key="v" v={yearOfMonths(g.months, g.consumption[k], gy)} src={`The year's twelve months summed. ${gsrc}`} k={`gas-${f.state}-${k}`} fmt={bcf} reason={g.consumption_reason[k] ?? "Not every month of the year is held."} />] })),
            { key: "prod", highlight: true, cells: ["Marketed production", <Fig key="v" v={yearOfMonths(g.months, g.marketed_production, gy)} src={`The year's twelve months summed. ${gsrc}`} k={`gas-${f.state}-prod`} fmt={bcf} reason={g.production_reason ?? "Not every month of the year is held."} />] }]}
        />
      ) : <Missing what="gas" reason={g.reason} />}
      {e.years && ey ? (
        <ToolTable
          minWidth={320}
          caption={`${f.name}: total energy consumed, ${ey} (trillion Btu)`}
          head={["", ey]}
          rows={[...Object.keys(SEDS_WORDS).map((k) => ({ key: k, highlight: k === "total", cells: [SEDS_WORDS[k], <Fig key="v" v={atYear(e.years, e.by_source[k], ey)} src={esrc} k={`seds-${f.state}-${k}`} fmt={one1} />] })),
            ...["residential", "industrial", "commercial", "transportation"].map((k) => ({ key: `sec-${k}`, cells: [`The ${k} sector`, <Fig key="v" v={atYear(e.years, e.by_sector[k], ey)} src={esrc} k={`seds-${f.state}-sec-${k}`} fmt={one1} reason={e.by_sector_reason[k]} />] }))]}
        />
      ) : <Missing what="energy" reason={e.reason} />}
    </>
  );
}

function LawsAndTax({ f }: { f: StateFile }) {
  const l = f.large_load_laws, s = f.severance;
  return (
    <>
      {l.laws.length ? (
        <ToolTable
          minWidth={720}
          caption={`${f.name}: state laws on large loads, as the ERW's research holds them`}
          head={["Law", "Status", "Date", "Threshold"]}
          rows={l.laws.map((r) => ({ key: r.law_id, cells: [<a key="b" href={r.url} title={`${r.title}. Read at the source on ${r.read ?? "a date not recorded"}. ${l.source ?? ""}`} className="underline">{r.bill}</a>,
            r.status, <span key="d" title={r.date_kind}>{r.date}</span>, <span key="t" title={r.requirements ?? ""}>{r.threshold ?? "not stated"}</span>] }))}
        />
      ) : <Missing what="laws" reason={l.reason} />}
      <p className="mt-2 text-sm" data-severance={s.in_tool ? "1" : "0"}>
        Severance tax: {s.in_tool && s.address ? <><a className="underline" href={s.address}>the severance tool</a> holds {f.name}&apos;s rules ({(s.products ?? []).join(", ")}).</> : <span className="text-muted">{s.reason}.</span>}
      </p>
    </>
  );
}

/** The two places' headline figures side by side. */
function Side({ a, b }: { a: StateFile; b: StateFile }) {
  const row = (label: string, k: string, va: number | null | undefined, vb: number | null | undefined, src: string, fmt: (v: number) => string) =>
    ({ key: k, cells: [label, <Fig key="a" v={va} src={src} k={`sd-a-${k}`} fmt={fmt} />, <Fig key="b" v={vb} src={src} k={`sd-b-${k}`} fmt={fmt} />] });
  const ca = lastCo2(a), cb = lastCo2(b);
  return (
    <ToolTable
      minWidth={560}
      caption={`${a.name} and ${b.name}`}
      head={["", `A: ${a.name}`, `B: ${b.name}`]}
      rows={[
        row("Net generation, last twelve months (TWh)", "gen", a.generation.last12?.total_mwh, b.generation.last12?.total_mwh, srcOf(a.generation), twh),
        ...GEN_SOURCES.slice(0, 6).map((s) => row(`${FUEL_WORDS[s]} share, last twelve months`, `sh-${s}`, a.generation.last12?.share_pct[s], b.generation.last12?.share_pct[s], srcOf(a.generation), pct)),
        ...SECTORS.filter((s) => s.key !== "transportation").map((s) => row(`Average price, ${s.label.toLowerCase()} (cents a kWh)`, `p-${s.key}`, a.retail.last12?.by_sector[s.key].price_usd_per_mwh, b.retail.last12?.by_sector[s.key].price_usd_per_mwh, srcOf(a.retail), cents)),
        row("Operating capacity (GW)", "cap", a.plants.capacity_total_mw, b.plants.capacity_total_mw, srcOf(a.plants), gw),
        row(`CO2 from power, ${ca?.year ?? ""} / ${cb?.year ?? ""} (million t)`, "co2", ca?.tons, cb?.tons, srcOf(a.co2), mt),
        row("CO2 per MWh generated (kg)", "rate", ca?.rate, cb?.rate, srcOf(a.co2), one1),
      ]}
    />
  );
}

export default async function StatesPage({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const index = readIndex();
  if (!index) {
    return <Brand><ToolPage><ToolHeader title="Every state" lead="The page's files are not on this server yet." /></ToolPage></Brand>;
  }
  const codes = index.states.map((r) => r.state);
  const optA = index.states.map((r) => ({ value: r.state, label: r.name })).sort((x, y) => (x.value === "US" ? 1 : y.value === "US" ? -1 : x.label.localeCompare(y.label)));
  const st = (v: string | undefined, dflt: string) => (v && codes.includes(v.toUpperCase()) ? v.toUpperCase() : dflt);
  const sa = st(one(q, "a"), "TX");
  const sbRaw = one(q, "b");
  const sb = sbRaw && sbRaw !== NONE ? st(sbRaw, NONE) : NONE;
  const from = FROM_YEARS.includes(one(q, "from") ?? "") ? (one(q, "from") as string) : "2015";
  const A = readState(index, sa);
  const B = sb !== NONE ? readState(index, sb) : null;
  if (!A) return <Brand><ToolPage><ToolHeader title="Every state" lead="This place's file is not on this server." /></ToolPage></Brand>;
  const keep = (omit: string[]) => Object.fromEntries(Object.entries({ a: sa, b: sb, from }).filter(([k]) => !omit.includes(k)));
  const places = [A, ...(B ? [B] : [])];
  const co2 = lastCo2(A);
  const g12 = A.generation.last12;
  const topSrc = g12 ? GEN_SOURCES.reduce((m, s) => ((g12.share_pct[s] ?? -1) > (g12.share_pct[m] ?? -1) ? s : m), GEN_SOURCES[0]) : null;
  const priceAll = A.retail.last12?.by_sector.all.price_usd_per_mwh ?? null;
  const region = gridRegion(A);
  const tables = index.tables;
  // the two places over time
  const shareSrc = one(q, "src") && (GEN_SOURCES as readonly string[]).includes(one(q, "src") as string) ? (one(q, "src") as string) : "natural_gas";
  const shareLines: Line[] = places.map((f, i) => ({ label: f.name, color: i ? "series-3" : "accent", points: sharePoints(f, shareSrc) }));
  const priceSector = (SECTORS.map((s) => s.key) as string[]).includes(one(q, "sector") ?? "") ? (one(q, "sector") as (typeof SECTORS)[number]["key"]) : "residential";
  const priceLines: Line[] = places.map((f, i) => ({ label: f.name, color: i ? "series-3" : "accent", points: monthPoints(f.retail.months, f.retail.price_usd_per_mwh?.[priceSector] as Arr, Number(from), 0.1) }));
  const salesLines: Line[] = SECTORS.filter((s) => s.key !== "all" && s.key !== "transportation").map((s, i) => ({ label: s.label, color: ["accent", "series-3", "series-5"][i], points: monthPoints(A.retail.months, A.retail.sales_mwh?.[s.key] as Arr, Number(from), 1e-3) }));

  return (
    <Brand>
    <ToolPage>
      <div data-states="1">
      <ToolHeader
        title="Every state"
        lead={<>What a state runs on and how that changed since 2001, what its homes, businesses and industry buy and pay, what is built and what is coming, who operates its grid, and its emissions: one state, or{" "}
          <Hint words="two side by side" why="Choose a second place under the first; every table and chart below then shows both, or the two in one chart." />, from EIA&apos;s monthly and annual figures.</>}
        under={<p className="mt-2 text-xs text-muted" data-license-line="1">License: public (<Hint words="EIA and the Census Bureau" why="U.S. Energy Information Administration and U.S. Census Bureau: their data are in the public domain, with credit to the source. Every table this page reads is public in the ERW's license register." />). Files built {index.built.slice(0, 10)}.</p>}
      />

      <Form anchor="top" keep={keep(["a", "b"])}>
        <AutoSubmitSelect name="a" value={sa} options={optA} label="State" />
        <AutoSubmitSelect name="b" value={sb} options={[{ value: NONE, label: "No second place" }, ...optA.filter((o) => o.value !== sa)]} label="Side by side with" />
      </Form>

      <HeadlineRow>
        <HeadlineNumber label="Net generation, last twelve months" value={<Fig v={g12?.total_mwh} src={srcOf(A.generation)} k="h-gen" fmt={twh} reason={A.generation.reason} />} unit="TWh" note={g12 ? span(g12.from, g12.to) : undefined} />
        <HeadlineNumber label="Largest source" value={<Fig v={topSrc && g12 ? g12.share_pct[topSrc] : null} src={srcOf(A.generation)} k="h-top" fmt={pct} reason={A.generation.reason} />} note={topSrc ? `${FUEL_WORDS[topSrc]}, of the twelve months' generation` : undefined} />
        <HeadlineNumber label="Average retail price, all sectors" value={<Fig v={priceAll} src={srcOf(A.retail, A.retail.revenue_note)} k="h-price" fmt={cents} reason={A.retail.reason} />} unit="cents a kWh" note="the last twelve months" />
        <HeadlineNumber label={`CO2 from power, ${co2?.year ?? ""}`} value={<Fig v={co2?.tons} src={srcOf(A.co2)} k="h-co2" fmt={mt} reason={A.co2.reason} />} unit="million t" note={co2?.rate ? `${one1(co2.rate)} kg per MWh generated` : undefined} />
      </HeadlineRow>

      <p className="my-3 border-l-2 border-rule pl-3 text-sm" data-monthly-note="1">
        Monthly, not hourly: no public source gives a state&apos;s generation by the hour. The hourly picture is kept by balancing authority, in{" "}
        <a className="underline" href={region ? `/grid?region=${region}` : "/grid"}>the Grid tool{region ? `, at ${A.name}'s largest authority's region` : ""}</a>.
      </p>

      {B ? (
        <ToolSection title="Side by side" id="side">
          <Side a={A} b={B} />
        </ToolSection>
      ) : null}

      <ToolSection title="What it runs on" id="runs-on">
        <Form anchor="runs-on" keep={keep(["from"])}>
          <AutoSubmitSelect name="from" value={from} options={FROM_YEARS.map((y) => ({ value: y, label: `From ${y}` }))} label="Months drawn" />
        </Form>
        {places.map((f) => <RunsOn key={f.state} f={f} from={Number(from)} />)}
      </ToolSection>

      <ToolSection title="How that changed since 2001" id="changed">
        {places.map((f) => <Changed key={f.state} f={f} />)}
        <Form anchor="changed" keep={keep([])}>
          <AutoSubmitSelect name="src" value={shareSrc} options={GEN_SOURCES.map((s) => ({ value: s, label: FUEL_WORDS[s] ?? s }))} label="Source" />
        </Form>
        <ChartFrame title={`${FUEL_WORDS[shareSrc]}'s share of net generation, by whole year`} tip={<Hint words=" (source)" why={srcOf(A.generation, "A year is shown only when all twelve of its months are held.")} />}>
          <LineChart lines={shareLines} unit="%" x="year" ariaLabel={`${FUEL_WORDS[shareSrc]} share of generation by year, ${places.map((p) => p.name).join(" and ")}`} />
        </ChartFrame>
      </ToolSection>

      <ToolSection title="What its homes, businesses and industry buy and pay" id="buys">
        {places.map((f) => <Buys key={f.state} f={f} />)}
        <Form anchor="buys" keep={keep([])}>
          <AutoSubmitSelect name="sector" value={priceSector} options={SECTORS.map((s) => ({ value: s.key, label: s.label }))} label="Price of" />
        </Form>
        <ChartFrame title={`Average retail price, ${SECTORS.find((s) => s.key === priceSector)?.label.toLowerCase()}, cents a kWh`} tip={<Hint words=" (source)" why={srcOf(A.retail)} />}>
          <LineChart lines={priceLines} unit="cents/kWh" x="month" ariaLabel={`Average retail price by month, ${places.map((p) => p.name).join(" and ")}`} />
        </ChartFrame>
        <ChartFrame title={`${A.name}: electricity sold by sector, GWh a month`} tip={<Hint words=" (source)" why={srcOf(A.retail)} />}>
          <LineChart lines={salesLines} unit="GWh" x="month" ariaLabel={`Electricity sold by sector by month, ${A.name}`} />
        </ChartFrame>
      </ToolSection>

      <ToolSection title="What is built and what is coming" id="built">
        {places.map((f) => <div key={f.state} className="mb-6"><Built f={f} /></div>)}
      </ToolSection>

      <ToolSection title="Who operates its grid" id="grid">
        {places.map((f) => <div key={f.state} className="mb-6"><Operates f={f} /></div>)}
      </ToolSection>

      <ToolSection title="Its emissions" id="emissions">
        {places.map((f) => <Emissions key={f.state} f={f} />)}
      </ToolSection>

      <ToolSection title="Natural gas and total energy" id="energy">
        {places.map((f) => <div key={f.state} className="mb-6"><GasAndEnergy f={f} /></div>)}
      </ToolSection>

      <ToolSection title="Large loads and severance tax" id="laws">
        {places.map((f) => <div key={f.state} className="mb-6"><LawsAndTax f={f} /></div>)}
      </ToolSection>

      <StatesDecisions />
      <TableDownloads tables={tables} />
      <SourceLine tables={tables} note={<>Method: <a href="/data/methods/states_page">the page&apos;s method note</a>. EIA&apos;s and the Census Bureau&apos;s figures as published; the page sums months into years and twelve-month windows and computes only the shares and the revenue it names.</>} />
      </div>
    </ToolPage>
    </Brand>
  );
}
