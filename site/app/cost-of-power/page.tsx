import type { Metadata } from "next";
import type { ReactNode } from "react";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import demandJson from "@/data/demand_growth.json";
import loadJson from "@/data/large_load_status.json";
import queuesJson from "@/data/queues.json";
import * as clean from "@/lib/clean";
import {
  ASSUMED, BUYS, badMonth, expand, gpuHour, gpus, hh, hrefOf, inputsOf, last36, lastTwelve, loadWords, monthName, monthsOf, monthsWords, shortMonth, span, two,
  usdShort, weights, whenOf, whole, years, type Inputs, type Month, type Span,
} from "@/lib/datacenter";
import { DELIVERY, INDEX, yearFiles } from "@/lib/datacenterdata";
import type { DemandFile } from "@/lib/demandgrowth";
import { SLUGS } from "@/lib/demandgrowth";
import { dayWords, span as loadSpan, type LoadFile } from "@/lib/largeload";
import { CLEAN, STRESS, type Slug } from "@/lib/mixdata";
import { viewOf, type QueueFile } from "@/lib/queues";
import * as stress from "@/lib/stress";
import { GridsView } from "./GridsView";
import { YearCost } from "./LoadCharts";
import { ContractInputs, ContractProvider, ContractResult } from "./LoadContract";
import { LoadForm } from "./LoadForm";
import { CostTabs } from "./Tabs";

// Session 138: "What a datacenter pays", the mirror of /cost-of-power/battery for a buyer. A load the reader describes
// (grid, region, size, how it runs, how it buys) and four questions: what it will cost, whether the power is there, how
// clean it is, how soon it can be had. The cost is computed here, on the server, by lib/datacenter.ts from the site's
// own files of hourly hub and zone prices (data/datacenter, warehouse/derived/datacenter_page.py); the contract is
// computed in the browser and never sent. The other three questions show headline numbers of the mix, demand and queue
// tools, read from those tools' own files, and link to them: nothing of theirs is rebuilt here. What the tab showed
// before session 138 is the view "Grid by grid" (GridsView.tsx). The page face carries no method: a figure that is
// missing is a short placeholder with its reason on hover, and the rest is in the Method note
// (docs/methods/datacenter_cost.md).
export const metadata: Metadata = { title: "What a datacenter pays" };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/datacenter_cost";
const DEMAND = demandJson as unknown as DemandFile;
const QUEUES = queuesJson as unknown as QueueFile;
const LOADS = loadJson as unknown as LoadFile;

/** A short placeholder with its reason on hover. */
function Missing({ why, words = "not held yet" }: { why: string; words?: string }) {
  return <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={why} data-missing="1">{words}</span>;
}
const NOWHERE = "not published anywhere yet";
const usd = (v: number | null, why: string) => (v === null ? <Missing why={why} /> : <>USD {usdShort(v)}</>);
const perMwh = (v: number | null, why: string) => (v === null ? <Missing why={why} /> : <>{two(v)}</>);
const day = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

function ViewNav({ x }: { x: Inputs }) {
  const item = (view: "load" | "grids", label: string) => (
    <Link href={hrefOf(x, { view })} scroll={false} aria-current={x.view === view ? "page" : undefined} data-view={view} style={{ color: x.view === view ? "#fff" : "var(--color-ink)" }}
      className={`border px-2 py-1 no-underline ${x.view === view ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{label}</Link>
  );
  return <nav aria-label="Views" className="mb-6 flex flex-wrap gap-1 text-xs" data-views="1">{item("load", "Your load")}{item("grids", "Grid by grid")}</nav>;
}

export default async function CostOfPower({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const x = inputsOf(Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined])), INDEX);
  return (
    <ToolPage>
      <ToolHeader
        title="What a datacenter pays"
        crumb={<CostTabs active="buy" />}
        lead={<>What a large load pays for power, whether the power is there when it is needed, how clean it is and how soon it can be had, for a load you describe. <Link href={METHOD}>Method note</Link>.</>}
      />
      <ViewNav x={x} />
      {x.view === "grids" ? <GridsView /> : <LoadView x={x} buyGiven={typeof sp.buy === "string"} />}
    </ToolPage>
  );
}

function LoadView({ x: asked, buyGiven }: { x: Inputs; buyGiven: boolean }) {
  let x = asked;
  const g = INDEX.grids[x.grid];
  let files: ReturnType<typeof yearFiles> = [], failed: string | null = null;
  try { files = yearFiles(x.grid); } catch (e) { failed = (e as Error).message; }
  const region = g?.regions.find((r) => r.id === x.region);
  let side = region?.[x.buy];
  let ms: Month[] = failed || !side ? [] : monthsOf(files, x.region, x.buy, x);
  let l12 = lastTwelve(ms);
  // the address named no market and real time holds no twelve complete months here: day-ahead is shown when it does
  if (!buyGiven && x.buy === "rt" && !l12 && !failed && region?.da) {
    const da = monthsOf(files, x.region, "da", x);
    if (lastTwelve(da)) { x = { ...x, buy: "da" }; side = region.da; ms = da; l12 = lastTwelve(da); }
  }
  const s12: Span | null = l12 ? span(l12) : null;
  const w36 = last36(ms);
  const bad = badMonth(w36?.months ?? []);
  const badPer = bad ? bad.cost / bad.energy : null;
  const ys = years(ms);
  const flex = x.run !== "flat", off = x.run === "hours" || x.run === "share";
  const place = `${x.region} in ${g?.name ?? x.grid}`;
  const market = BUYS[x.buy].toLowerCase();
  const heldFrom = side ? day(side.first) : "";
  const noYear = `Twelve complete months of ${market} prices are not held for ${x.region}: it is held from ${heldFrom || "no date"}. A month counts when at least 95 percent of its hours are held.`;
  const l12Span = l12 ? `${shortMonth(l12[0].m)} to ${shortMonth(l12[11].m)}` : null;
  const saved = s12 && s12.flat !== null && s12.per !== null ? s12.flat - s12.per : null;
  const gh = s12?.per != null ? gpuHour(s12.per, x.gpu, x.pue) : null;
  const nGpu = gpus(x.mw, x.gpu, x.pue);
  const size = `${x.mw.toLocaleString("en-US")} MW`;

  // the form's lists: every grid held, each region with what is held of it
  const grids = Object.fromEntries(Object.entries(INDEX.grids).map(([id, v]) => [id, { name: v.name,
    regions: v.regions.map((r) => { const s = r.rt ?? r.da!; return { id: r.id, held: `from ${shortMonth(s.first.slice(0, 7))}` }; }) }]));

  // every region of the grid over its own last twelve months, flat (the fold)
  const regionRows = (g?.regions ?? []).map((r) => {
    const s = r[x.buy];
    if (!s || failed) return { id: r.id, per: null as number | null, from: s?.first ?? null, hours: s?.hours ?? 0, sp: null as string | null };
    const m = monthsOf(files, r.id, x.buy, { run: "flat", n: 0, pct: 0, shift: 0 });
    const t = lastTwelve(m);
    return { id: r.id, per: t ? span(t).flat : null, from: s.first, hours: s.hours, sp: t ? `${shortMonth(t[0].m)} to ${shortMonth(t[11].m)}` : null };
  });

  // will the power be there: the grid's own figures from the mix, demand and (session 138) operator demand files
  const slug = x.grid as Slug;
  const sf = STRESS[slug], sy = sf ? stress.defaultYear(sf) : null;
  const peak = sf && sy ? stress.get(sf, sy, "peak_demand_mw") : null, peakAt = sf && sy ? stress.at(sf, sy, "peak_demand_mw") : null;
  const fuels = sf && sy ? stress.fuelRows(sf, sy).filter((f) => f.capacity !== null) : [];
  const ba = SLUGS[x.grid], area = ba ? DEMAND.areas[ba] : undefined;
  const growth = area?.years[String(DEMAND.last_year)];
  const tightYears = Object.entries(g?.demand ?? {}).filter(([, d]) => d.tight_hours !== undefined).sort(([a], [b]) => a.localeCompare(b));
  const tightRows = tightYears.map(([y, d]) => {
    const f = files.find((k) => k.year === Number(y));
    const when = f?.tight ? whenOf(Number(y), f.tight) : null;
    let down: number | null = null;
    if (f?.tight && flex && side && x.run !== "shift") {
      const p = expand(f, x.region, x.buy), w = weights(p, x);
      down = f.tight.filter((i) => p[i] !== null && w[i] === 0).length;
    }
    return { y, d, when, down };
  });
  const lastTight = [...tightRows].reverse().find((r) => r.d.whole) ?? tightRows.at(-1);
  const zones = g?.zones ?? {};
  // a demand table held internally (its publisher's terms restrict republishing) is named, and nothing of it is shown
  const withheld = !!g?.demand_source?.startsWith("withheld:");
  const noDemand = withheld
    ? <Missing words="licensed source needed" why={`${g?.name} publishes its hourly demand by zone, and its legal notice restricts duplication of its content. The table is held internally and nothing of it is shown here.`} />
    : <Missing why={`The operator's own hourly demand is not held for ${g?.name ?? x.grid}, so its tight hours are not counted.`} />;

  // how clean: the grid's figures from the tables behind /mix?view=clean
  const cf = CLEAN[slug], cy = cf ? clean.defaultYear(cf) : null, cv = cf && cy ? clean.yearView(cf, cy) : null;

  // how soon: the interconnection queue, and ERCOT's large-load status
  const qv = viewOf(QUEUES, x.grid, "all")?.whole ?? null;
  const ll = x.grid === "ercot" ? loadSpan(LOADS) : null;

  const delivery = x.grid === "ercot" ? DELIVERY.rows : [];
  const utilities = [...new Set(delivery.map((r) => r.utility))];

  return (
    <ContractProvider>
      <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Your load">
            <LoadForm key={hrefOf(x)} x={x} grids={grids} blank={INDEX.blank} />
          </InputPanel>
          <InputPanel title="Your contract (optional)">
            <ContractInputs />
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {failed ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The price files could not be read, so no number is shown: {failed}</p>
          ) : !side ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">{x.region}: <Missing why={`No ${market} price is held for ${place}.`} /></p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                {s12 && s12.per !== null ? (
                  <>{loadWords(x)} at {place}, buying {market}, paid USD <span data-stat="l12_per">{two(s12.per)}</span> per MWh over the last twelve months,
                    USD <span data-stat="l12_cost">{usdShort(s12.cost * x.mw)}</span> in all{flex && saved !== null ? <>, USD <span data-stat="l12_saved">{two(saved)}</span> per MWh less than a flat load</> : null}: USD <span data-stat="gpu_hour">{gh!.toFixed(4)}</span> per GPU-hour for power alone.</>
                ) : (
                  <>{loadWords(x)} at {place}, buying {market}: last twelve months <Missing why={noYear} />.</>
                )}
              </p>

              <HeadlineRow>
                <HeadlineNumber label="Last twelve months, market energy"
                  value={s12 && s12.per !== null ? <>USD {two(s12.per)}<span className="ml-1 font-sans text-sm text-muted">per MWh</span></> : <Missing why={noYear} />}
                  note={s12 ? <>USD {usdShort(s12.cost * x.mw)} for {whole(s12.energy * x.mw)} MWh, {l12Span}.</> : null} />
                <HeadlineNumber label="A bad month: the worst tenth of the last 36"
                  value={badPer !== null ? <>USD {two(badPer)}<span className="ml-1 font-sans text-sm text-muted">per MWh</span></> : <Missing why={noYear} />}
                  note={bad && w36 ? <>{monthName(bad.m)}. One month in ten of the {w36.months.length} held from {monthName(w36.months[0].m)} to {monthName(w36.to)} cost this or more.</> : null} />
                <HeadlineNumber label="Power per GPU-hour"
                  value={gh !== null ? <>USD {gh.toFixed(4)}</> : <Missing why={noYear} />}
                  note={<>At {x.gpu} kW per GPU and an overhead ratio of {x.pue}: {size} powers {whole(nGpu)} GPUs.</>} />
              </HeadlineRow>

              <ChartFrame title={`Cost by year, USD per MWh, ${x.region}, ${market}`}
                legend={flex ? [{ label: "Flat load", color: "#6B665E" }, { label: "This load", color: "#8C1515" }, { label: "Incomplete year", color: "#8C1515", hatch: true }] : [{ label: "Flat load", color: "#8C1515" }, { label: "Incomplete year", color: "#8C1515", hatch: true }]}>
                <YearCost rows={ys.map((r) => ({ y: r.y, flat: r.flat, per: r.per, complete: r.complete, months: r.months, down: r.down }))} flex={flex} off={off}
                  label={`Cost of power by year at ${place}, ${market}, USD per MWh${flex ? ": a flat load and this load" : ""}`} />
              </ChartFrame>

              <ToolSection title="What will it cost" id="cost">
                <ToolTable caption="What will it cost" minWidth={620} head={["", "USD per MWh", `USD, ${size}`, ""]}
                  rows={[
                    { key: "flat", cells: ["Market energy, a flat load, last twelve months", perMwh(s12?.flat ?? null, noYear), usd(s12 ? s12.flatCost * x.mw : null, noYear), <span key="n" className="text-xs text-muted">{l12Span ?? ""}</span>] },
                    ...(flex ? [
                      { key: "load", highlight: true, cells: ["Market energy, this load, last twelve months", perMwh(s12?.per ?? null, noYear), usd(s12 ? s12.cost * x.mw : null, noYear), <span key="n" className="text-xs text-muted">{s12 ? `${whole(s12.energy * x.mw)} MWh` : ""}</span>] },
                      { key: "saved", cells: ["What the flexibility saves", perMwh(saved, noYear), usd(s12 ? (s12.flatCost - s12.cost) * x.mw : null, noYear),
                        <span key="n" className="text-xs text-muted">{s12 ? (x.run === "shift" ? "the same energy, moved within each day" : `off in ${whole(s12.down)} hours; ${whole((s12.held - s12.energy) * x.mw)} MWh not bought`) : ""}</span>] },
                    ] : []),
                    { key: "bad", cells: ["A bad month", perMwh(badPer, noYear), usd(bad ? bad.cost * x.mw : null, noYear), <span key="n" className="text-xs text-muted">{bad ? monthName(bad.m) : ""}</span>] },
                    { key: "gpu", cells: ["Power per GPU-hour", gh !== null ? gh.toFixed(4) : <Missing key="m" why={noYear} />, "", <span key="n" className="text-xs text-muted">USD per GPU-hour, not per MWh</span>] },
                    ...(x.grid === "ercot"
                      ? (utilities.length || DELIVERY.withheld.length
                        ? [...utilities.map((u) => ({ key: `d-${u}`, cells: [<>Delivery and transmission, {u}</>], wide: <DeliveryCell rows={delivery.filter((r) => r.utility === u)} /> })),
                          ...DELIVERY.withheld.map((w) => ({ key: `d-${w.utility}`, cells: [<>Delivery and transmission, {w.utility}</>], wide: <Missing words={w.words} why={w.why} /> }))]
                        : [{ key: "delivery", cells: ["Delivery and transmission charges"], wide: <Missing why="The four large Texas wires utilities' tariff charges are not in this page's files yet." /> }])
                      : [{ key: "delivery", cells: ["Delivery charges"], wide: <Missing why={`The delivery and transmission tariffs of ${g.name}'s utilities are not in the warehouse. Texas's four large wires utilities are.`} /> }]),
                  ]} />
              </ToolSection>

              <ToolSection title="With your contract">
                <ContractResult l12={s12 ? { cost: s12.cost, energy: s12.energy } : null} mw={x.mw} bad={badPer} span={l12Span} />
              </ToolSection>
            </>
          )}

          <ToolSection title="Will the power be there" id="there">
            <ToolTable caption="Will the power be there" words minWidth={620} head={["", g?.name ?? x.grid, ""]}
              rows={[
                { key: "growth", cells: [`Demand growth, 2019 to ${DEMAND.last_year}`,
                  growth?.avg_demand_growth_since_2019_pct !== undefined ? <>average {growth.avg_demand_growth_since_2019_pct > 0 ? "+" : ""}{two(growth.avg_demand_growth_since_2019_pct)} percent; highest hour {growth.peak_demand_growth_since_2019_pct > 0 ? "+" : ""}{two(growth.peak_demand_growth_since_2019_pct)} percent</> : <Missing why={`No whole year of ${DEMAND.last_year} or of 2019 is held for this grid in the demand table.`} />,
                  <Link key="l" href={`/demand?area=${x.grid}`}>Demand growth</Link>] },
                { key: "peak", cells: [`Highest hour of demand${sy ? `, ${sy}` : ""}`,
                  peak !== null ? <>{whole(peak)} MW{peakAt ? `, ${stress.when(peakAt, sf.tz)}` : ""}</> : <Missing why="The year's highest hour is not in the grid stress table for this grid." />,
                  <Link key="l" href={`/mix?view=stress&grid=${x.grid}`}>How hard the grid works</Link>] },
                { key: "cap", cells: [`Installed capacity by fuel${sy ? `, ${sy}` : ""}`,
                  fuels.length ? <span className="block">{fuels.map((f, i) => <span key={f.fuel} className="mr-3 inline-block whitespace-nowrap" title={peak ? `${f.name}: ${whole(f.capacity!)} MW installed, ${two((100 * f.capacity!) / peak)} percent of the year's highest hour of demand` : undefined}>{f.name} {whole(f.capacity!)} MW{i < fuels.length - 1 ? ";" : ""}</span>)}</span> : <Missing why="No installed capacity is held for this grid and year." />,
                  ""] },
                { key: "tight", cells: [`Hours the grid was tight${lastTight ? `, ${lastTight.y}` : ""}`,
                  lastTight ? <>{whole(lastTight.d.tight_hours!)} hours{lastTight.when ? <>, in {monthsWords(lastTight.when.months)}, between {hh(lastTight.when.from)} and {hh(lastTight.when.to + 1)}</> : null}</>
                    : noDemand,
                  <span key="n" className="cursor-help border-b border-dotted border-muted text-xs text-muted" title={`An hour is counted tight when the grid's demand was at or above ${INDEX.tight * 100} percent of that year's highest hour. Hours are in ${g?.std_name ?? "standard time"}.`}>tight: within {Math.round((1 - INDEX.tight) * 100)} percent of the year&apos;s peak</span>] },
                { key: "down", cells: ["Of those hours, this load was off in",
                  !lastTight ? noDemand
                    : x.run === "flat" ? <>none: a flat load runs in every hour</>
                    : x.run === "shift" ? <Missing why="A load that shifts energy within the day is never off for a whole hour by rule, so its tight hours are not counted here." words="not counted for a shifting load" />
                    : lastTight.down === null ? <Missing why="No price is held for this region in that year." />
                    : <>{whole(lastTight.down)} of {whole(lastTight.d.tight_hours!)}</>,
                  ""] },
                { key: "zones", cells: ["Demand by region",
                  Object.keys(zones).length ? <ZoneCell zones={zones} own={x.region} /> : withheld ? noDemand : <Missing why={`Hourly demand by region is not held for ${g?.name ?? x.grid}.`} />,
                  ""] },
              ]} />
          </ToolSection>

          <ToolSection title="How clean" id="clean">
            <ToolTable caption="How clean" words minWidth={620} head={["", `${g?.name ?? x.grid}${cy ? `, ${cy}` : ""}`, ""]}
              rows={[
                { key: "annual", cells: ["Carbon-free share of the grid's generation, over the year", cv?.share != null ? <>{two(cv.share)} percent</> : <Missing why="The year's carbon-free share is not in the clean energy table for this grid." />, <Link key="l" href={`/mix?view=clean&grid=${x.grid}`}>How clean, and when</Link>] },
                { key: "flat", cells: ["What a flat load meets, hour by hour", cv?.flat != null ? <>{two(cv.flat)} percent</> : <Missing why="Not in the clean energy table for this grid and year." />, ""] },
                { key: "match", cells: ["Buying carbon-free energy equal to the load's whole year, shaped like the grid's own",
                  cv?.match.mix?.[100]?.energy != null ? <>{two(cv.match.mix[100].energy!)} percent of the energy matched hour by hour, against 100 percent on the annual count; {two(cv.match.mix[100].hours!)} percent of hours fully covered</> : <Missing why="Not in the clean energy table for this grid and year." />, ""] },
                { key: "carbon", cells: ["Carbon per MWh, a flat load", cv?.carbon.flat != null ? <>{two(cv.carbon.flat)} kg CO2 per MWh</> : <Missing why="Not in the clean energy table for this grid and year." />, ""] },
                { key: "own", cells: ["This load's own hours", <Missing key="m" why="The clean energy tables are by grid and for a flat load or a load moved toward the cleanest hours. This load's own hours are not matched against them yet." />, ""] },
              ]} />
          </ToolSection>

          <ToolSection title="How soon" id="soon">
            <ToolTable caption="How soon" words minWidth={620} head={["", g?.name ?? x.grid, ""]}
              rows={[
                { key: "q", cells: ["Generation waiting to connect", qv ? <>{whole(qv.total_active_mw)} MW in {whole(qv.total_active_requests)} active requests</> : <Missing why="The interconnection queue summary holds no row for this grid." />, <Link key="l" href={`/queues?grid=${x.grid}&tech=all`}>Interconnection queues</Link>] },
                { key: "wait", cells: ["From request to operation, the median", qv?.median_years_to_operation !== undefined ? <>{two(qv.median_years_to_operation)} years, over {whole(qv.years_to_operation_n)} projects</> : <Missing why="Too few dated projects to state a median for this grid." />, ""] },
                { key: "done", cells: [`Of the requests entered ${QUEUES.past[0]} to ${QUEUES.past[1]}`, qv?.past_operating_share_pct !== undefined ? <>{two(qv.past_operating_share_pct)} percent operating, {two(qv.past_withdrawn_share_pct!)} percent withdrawn</> : <Missing why="Not in the queue summary for this grid." />, ""] },
                { key: "ll", cells: ["Large load approved to energize",
                  ll ? <>{whole(ll.last.approved!)} MW, of which {whole(ll.last.nonsimultaneous!)} MW observed running (ERCOT, {dayWords(ll.last.day)})</>
                    : x.grid === "ercot" ? <Missing why="ERCOT's large load status table holds no report with these figures." /> : <Missing why={`${g?.name ?? x.grid} publishes no figure of large load approved or running that the warehouse holds.`} />,
                  <Link key="l" href="/datacenters">Datacenters</Link>] },
                { key: "line", cells: ["Large load in line, by region",
                  x.grid === "nyiso" ? <Missing key="m" why="NYISO publishes its load interconnection requests by zone in its interconnection queue workbook (the sheets Load Projects and Load Project Tracking). The warehouse reads the generator sheets of that workbook and not these yet." />
                    : x.grid === "ercot" ? <Missing key="m" words={NOWHERE} why="ERCOT publishes the large load seeking interconnection as system totals in slide decks, with no table by zone or county. A search on 7 October 2026 found no public list by place." />
                    : <Missing key="m" words={NOWHERE} why={`A search on 7 October 2026 found no public list of the large load waiting for power in ${g?.name ?? x.grid} by place. The pieces sit in utility planning filings, rate cases and operator reports.`} />, ""] },
                { key: "waitload", cells: ["How long a new large load waits", <Missing key="m" words={NOWHERE} why="A search on 7 October 2026 found no public dataset of the time from a large load's request to its energization, for any grid. The interconnection queue above is for generators, not loads." />, ""] },
              ]} />
          </ToolSection>

          {!failed && side ? (
            <div className="mb-8 border-t border-rule">
              <Fold title="Every year">
                <ToolTable caption="Every year" minWidth={620} head={["Year", "Flat load, USD/MWh", ...(flex ? ["This load, USD/MWh"] : []), ...(off ? ["Hours off"] : []), `USD, ${size}`, "Months held"]}
                  rows={[...ys].reverse().map((r) => ({ key: r.y, muted: !r.complete, cells: [r.y, r.flat === null ? "" : two(r.flat), ...(flex ? [r.per === null ? "" : two(r.per)] : []), ...(off ? [whole(r.down)] : []), usdShort(r.cost * x.mw), `${r.months} of 12`] }))} />
              </Fold>
              <Fold title="Every month">
                <ToolTable caption="Every month" minWidth={620} head={["Month", "Flat load, USD/MWh", ...(flex ? ["This load, USD/MWh"] : []), ...(off ? ["Hours off"] : []), `USD, ${size}`, "Hours held"]}
                  rows={[...ms].reverse().map((r) => ({ key: r.m, muted: !r.complete, cells: [r.m, two(r.flat / r.held), ...(flex ? [r.energy ? two(r.cost / r.energy) : ""] : []), ...(off ? [whole(r.down)] : []), usdShort(r.cost * x.mw), `${whole(r.held)} of ${whole(r.due)}`] }))} />
              </Fold>
              <Fold title={`Every region of ${g.name}, a flat load, ${market}`}>
                <ToolTable caption="Every region" words minWidth={560} head={["Region", "Last twelve months, USD/MWh", "Held from"]}
                  rows={regionRows.map((r) => ({ key: r.id, highlight: r.id === x.region, cells: [<Link key="l" href={hrefOf(x, { region: r.id })} scroll={false}>{r.id}</Link>,
                    r.per !== null ? <>{two(r.per)} <span className="text-xs text-muted">{r.sp}</span></> : <Missing key="m" why={r.from ? `Held from ${day(r.from)}: ${whole(r.hours)} hours, not yet twelve complete months.` : `No ${market} price is held for this region.`} />,
                    r.from ? day(r.from) : ""] }))} />
              </Fold>
            </div>
          ) : null}
        </div>
      </div>
      <SourceLine tables={[...INDEX.tables, "clean_energy_summary", "grid_stress_yearly", "eia930_demand_growth", "interconnection_queue_summary", ...(x.grid === "ercot" ? ["ercot_large_load_status"] : []), ...(g?.demand_source && !withheld ? [g.demand_source.split(" ")[0]] : []), ...(DELIVERY.table && x.grid === "ercot" ? [DELIVERY.table] : [])]}
        note={<>The price files were built {day(INDEX.built)}. Defaults: <span className="cursor-help border-b border-dotted border-muted" title={ASSUMED.gpu.source}>power per GPU</span>, <span className="cursor-help border-b border-dotted border-muted" title={ASSUMED.pue.source}>overhead ratio</span>. <Link href={METHOD}>Method note</Link>.</>} />
    </ContractProvider>
  );
}

/** One utility's delivery charges: each as the tariff prints it, with the line it was read from on hover; and, for the
 * transmission cost recovery factor alone, what it comes to per MWh for a flat load. Its own row: never added to the
 * market cost. */
function DeliveryCell({ rows }: { rows: typeof DELIVERY.rows }): ReactNode {
  const tcrf = rows.find((r) => /TCRF|Transmission Cost Recovery/i.test(r.charge) && /4CP/i.test(r.unit) && r.value > 0);
  return (
    <span className="block text-ink" data-delivery="1">
      {tcrf ? (
        <span className="mb-1 block">
          <span className="cursor-help border-b border-dotted border-muted" data-delivery-per-mwh="1"
            title={`${tcrf.value_as_written} ${tcrf.unit} is billed each month on the load's demand in the grid's four summer peak intervals. For a flat load that demand is its size, so a year costs ${tcrf.value} x 12 per kW, over 8,760 hours: USD ${two((tcrf.value * 12000) / 8760)} per MWh. Not added to the market cost above.`}>
            The transmission factor alone, a flat load: USD {two((tcrf.value * 12000) / 8760)} per MWh
          </span>
        </span>
      ) : null}
      {rows.map((r, i) => (
        <span key={i} className="mr-3 inline-block text-xs">
          <a href={r.url} title={`${r.document}${r.page ? `, page ${r.page}` : ""}${r.effective ? `, effective ${r.effective}` : ""}. Read from the line: "${r.sentence}"${r.column ? ` (its column ${r.column})` : ""}. ${r.terms}.`} className="cursor-help no-underline hover:underline">
            {r.charge}: {r.value_as_written.replace(/^\$\s*/, "").replace(/^\(\s*\$?\s*/, "(")} {r.unit.replace(/^\$\//, "USD per ").replace(/^per /, "USD per ")}
          </a>{i < rows.length - 1 ? ";" : ""}
        </span>
      ))}
    </span>
  );
}

/** Demand by region: each zone's average demand in the newest whole year against the first whole year held. */
function ZoneCell({ zones, own }: { zones: NonNullable<(typeof INDEX.grids)[string]["zones"]>; own: string }): ReactNode {
  const rows = Object.entries(zones).map(([z, ys]) => {
    const wholeYears = Object.keys(ys).filter((y) => ys[y].hours_held >= 0.95 * ys[y].hours_due && ys[y].hours_due >= 8760).sort();
    const a = wholeYears[0], b = wholeYears.at(-1);
    return { z, a, b, from: a ? ys[a].mean_mw : null, to: b ? ys[b].mean_mw : null, peak: b ? ys[b].peak_mw : null };
  }).filter((r) => r.a && r.b && r.a !== r.b);
  if (!rows.length) return <Missing why="No region holds two whole years of hourly demand." />;
  return (
    <span className="block" data-zones="1">
      {rows.map((r) => (
        <span key={r.z} className={`mr-3 inline-block cursor-help whitespace-nowrap ${r.z === own ? "font-semibold" : ""}`} data-zone={r.z} title={`${r.z}: average demand ${whole(r.from!)} MW in ${r.a}, ${whole(r.to!)} MW in ${r.b}; highest hour of ${r.b}: ${whole(r.peak!)} MW`}>
          {r.z} {r.to! >= r.from! ? "+" : ""}{two((100 * (r.to! - r.from!)) / r.from!)}%
        </span>
      ))}
      <span className="block text-xs text-muted">average demand, {rows[0].a} to {rows[0].b}</span>
    </span>
  );
}
