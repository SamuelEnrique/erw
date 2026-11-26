import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Brand } from "@/components/Brand";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { LineChart, type Line } from "@/components/LineChart";
import { ChartFrame, HeadlineNumber, HeadlineRow, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { STATES } from "@/lib/regions";
import {
  MECS_FUELS, MECS_REGIONS, MONTHLY_KEYS, OUTLOOK_INDUSTRIES, SEDS_SOURCES, changePct, industryChoices, lastMonth, lastStateYear, lastWholeYear,
  monthValue, monthlyPoints, outlookPoints, outlookSeries, outlookValue, pct1, rankedIndustries, rankedStates, readIndustry, salesPoints, salesYear,
  shareOfSum, stateValue, statePoints, statePrice, tbtu, yearSum, type IndustryFile,
} from "@/lib/industry";
import raw from "@/data/industry.json";
import { IndustryDecisions } from "./Decisions";

// Session 8012 (chain 505, part B1): "Energy use by industry", Samuel's idea of September: energy consumption by
// industry, kept current. The page reads data/industry.json (the data machine's file: warehouse/derived/industry_page.py,
// contract section 9 of docs/state/page_files_regions.md, method docs/methods/industry_page.md) and draws its figures
// as they stand: the industrial sector by source month by month (Monthly Energy Review), the manufacturing industries
// ranked by fuel and region (2022 MECS), the states by year (State Energy Data System) with electricity sold to industry
// by month (Form EIA-861M), and EIA's own projections by industry (Annual Energy Outlook). Two industries and two states
// stand side by side. Every figure says its source on hover. Facts and no view: no figure of the ERW's own, nothing
// filled; a cell EIA withholds is drawn as "not held" with EIA's reason on hover. In review (a path with no line in
// lib/release.ts is in review); in no menu (chain 505).
export const metadata: Metadata = { title: "Energy use by industry", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const F = readIndustry(raw) as IndustryFile;
const TABLES = F.tables;
const COLORS = ["accent", "series-1", "series-3", "series-5", "series-6", "series-8", "series-2", "series-4"];
const SRC = {
  monthly: `${F.sources.monthly}, as the ERW's table eia_sector_energy_consumption_monthly holds it.`,
  mecs: `${F.sources.industries}, as the ERW's table eia_mecs_manufacturing holds it. Figures are for ${F.industries.survey_year}.`,
  seds: `${F.sources.states}, as the ERW's tables eia_seds_industrial_annual and eia_seds_state_energy hold it.`,
  sales: `${F.sources.electricity_sales}, as the ERW's table eia_retail_sales_monthly holds it.`,
  aeo: `${F.sources.outlook}, AEO${F.outlook.release}, as the ERW's table eia_aeo_industrial holds it: EIA's own projections, not the ERW's.`,
};
const WITHHELD = `EIA withholds or does not estimate this cell (its codes *, D, NA or Q), so it has no figure here. ${F.industries.note}`;

type Query = Record<string, string | string[] | undefined>;
const one = (q: Query, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
const pick = <T extends string>(v: string | undefined, ok: readonly T[] | T[], dflt: T): T => (v && (ok as string[]).includes(v) ? (v as T) : dflt);

/** A figure with its source on hover; "not held" with the reason where the file has none. */
function Fig({ v, src, k, digits }: { v: number | null; src: string; k: string; digits?: (v: number) => string }) {
  if (v === null) return <span className="cursor-help text-muted" title={src.startsWith("EIA withholds") ? src : `Not held in the file. ${src}`} data-not-held={k}>not held</span>;
  return <span className="cursor-help" title={src} data-fig={k}>{digits ? digits(v) : tbtu(v)}</span>;
}
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const usd = (v: number) => `$${v.toFixed(2)}`;
const billions = (v: number) => `$${(v / 1e9).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} bn`;
/** The chart's short names of the Monthly Energy Review's sources; the table and the hover keep EIA's own words. */
const SHORT: Record<string, string> = { total: "Total", end_use_total: "End use", natural_gas: "Natural gas", petroleum: "Petroleum", electricity_retail_sales: "Electricity sold", electrical_system_losses: "Electrical losses", renewables: "Renewables", coal: "Coal" };
const twh = (v: number) => (v / 1e6).toLocaleString("en-US", { maximumFractionDigits: 1 });
const stateName = (st: string) => (st === "US" ? "United States" : STATES[st] ?? st);
const monthWords = (m: string) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1, 1)).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });

function Form({ children, anchor, keep }: { children: ReactNode; anchor: string; keep: Record<string, string> }) {
  return (
    <form method="get" action={`/industry#${anchor}`} className="mb-3 flex flex-wrap items-end gap-3 text-sm [&_label]:max-w-full [&_select]:max-w-full" data-industry-form={anchor}>
      {Object.entries(keep).map(([k, v]) => <input key={k} type="hidden" name={k} value={v} />)}
      {children}
      <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
    </form>
  );
}

export default async function IndustryPage({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const last = lastMonth(F);
  const lastYear = lastWholeYear(F);
  const fromYears = ["1973", "1990", "2005", "2015", "2020"];
  const from = pick(one(q, "from"), fromYears, "2015");
  // the industries: region, A and B (default: the two largest three-digit industries in the nation)
  const region = pick(one(q, "region"), MECS_REGIONS.map((r) => r.key), "us");
  const ranked = rankedIndustries(F, region);
  const usRanked = rankedIndustries(F, "us");
  const codes = Object.keys(F.industries.industries);
  const ia = pick(one(q, "a"), codes, usRanked[0].naics);
  const ib = pick(one(q, "b"), codes, usRanked[1].naics);
  // the states: year and source, A and B (default: the two largest in the newest year's total)
  const sYear = lastStateYear(F) ?? F.states_annual.years[F.states_annual.years.length - 1];
  const years = F.states_annual.years.map(String);
  const year = Number(pick(one(q, "year"), years, String(sYear)));
  const src = pick(one(q, "src"), SEDS_SOURCES.map((s) => s.key), "total");
  const byState = rankedStates(F, year, src);
  const sts = Object.keys(F.states_annual.states);
  const firstTwo = rankedStates(F, sYear, "total");
  const sa = pick(one(q, "sa"), sts, firstTwo[0].st);
  const sb = pick(one(q, "sb"), sts, firstTwo[1].st);
  // the outlook: industry, series, cases A and B (default: the Counterfactual Baseline case and the High Electricity Demand case)
  const oInds = Object.keys(F.outlook.industries).filter((k) => OUTLOOK_INDUSTRIES[k]);
  const oi = pick(one(q, "oi"), oInds, oInds.includes("iron_and_steel") ? "iron_and_steel" : oInds[0]);
  const series = outlookSeries(F, oi);
  const os = pick(one(q, "os"), series, series[0]);
  const caseKeys = Object.keys(F.outlook.cases);
  const ca = pick(one(q, "ca"), caseKeys, caseKeys.includes("cb2026") ? "cb2026" : caseKeys[0]);
  const cb = pick(one(q, "cb"), caseKeys, caseKeys.includes("higheldmd") ? "higheldmd" : caseKeys[1]);
  const keep = (omit: string[]) => Object.fromEntries(Object.entries({ from, region, a: ia, b: ib, year: String(year), src, sa, sb, oi, os, ca, cb }).filter(([k]) => !omit.includes(k)));

  const monthlyLines: Line[] = MONTHLY_KEYS.map((k, i) => ({ label: SHORT[k] ?? F.monthly.labels[k] ?? k, color: COLORS[i % COLORS.length], points: monthlyPoints(F, k, Number(from)) })).filter((l) => l.points.length);
  const yearAgo = last ? `${Number(last.slice(0, 4)) - 1}${last.slice(4)}` : null;
  const top = usRanked[0];
  const choices = industryChoices(F);
  const name = (n: string) => F.industries.industries[n]?.name ?? n;
  const fuelCell = (n: string, fuel: string) => F.industries.industries[n]?.by_region?.[region]?.[fuel] ?? null;
  const elec = (n: string, k: string) => F.industries.industries[n]?.electricity_mwh?.[region]?.[k] ?? null;
  const ELEC: { key: string; label: string }[] = [
    { key: "elec_net_demand", label: "Net demand for electricity" }, { key: "elec_purchases", label: "Purchases" },
    { key: "elec_transfers_in", label: "Transfers in" }, { key: "elec_onsite_generation", label: "Total onsite generation" },
    { key: "gen_cogeneration", label: "Onsite generation: cogeneration" }, { key: "gen_renewable", label: "Onsite generation: renewables (excluding wood and other biomass)" },
    { key: "gen_other", label: "Onsite generation: other" }, { key: "elec_sales_transfers_offsite", label: "Sales and transfers offsite" },
  ];
  const srcLabel = SEDS_SOURCES.find((s) => s.key === src)?.label ?? src;
  const stateLines: Line[] = [sa, sb].map((st, i) => ({ label: stateName(st), color: i ? "series-3" : "accent", points: statePoints(F, st, src) }));
  const salesFrom = 2015;
  const salesLines: Line[] = [sa, sb].map((st, i) => ({ label: stateName(st), color: i ? "series-3" : "accent", points: salesPoints(F, st, salesFrom) }));
  const outLines: Line[] = [ca, cb].map((c, i) => ({ label: F.outlook.cases[c] ?? c, color: i ? "series-3" : "accent", points: outlookPoints(F, oi, os, c) }));
  const outYears = F.outlook.years.filter((y) => Number(y) % 5 === 0 || y === F.outlook.years[0]);
  const stateOptions = sts.map((st) => ({ value: st, label: stateName(st) })).sort((a, b) => (a.value === "US" ? -1 : b.value === "US" ? 1 : a.label.localeCompare(b.label)));

  return (
    <Brand>
    <ToolPage>
      <div data-industry="1">
      <ToolHeader
        title="Energy use by industry"
        lead={<>How much energy American industry uses, of which fuels, in which industries and states, and what EIA projects: the industrial sector month by month, the manufacturing industries of the{" "}
          <Hint words={`${F.industries.survey_year} survey`} why={SRC.mecs} />, every state year by year, and EIA&apos;s outlook to {F.outlook.years[F.outlook.years.length - 1]}.{" "}
          <Hint words="Two of each side by side" why="Choose two industries, two states or two of EIA's cases; each pair is drawn in the same table or chart." />.{" "}
          <Hint words="The industrial sector and the survey count different things" why="The industrial sector of the Monthly Energy Review and the State Energy Data System is manufacturing, agriculture, mining and construction together, and its total counts energy used as a raw material (feedstocks) and the sector's share of the energy lost making and moving electricity. The 2022 survey counts manufacturing alone, and only the energy it uses as fuel, with its electricity at 3,412 Btu a kWh and no losses. An industry's figure is not a part of the sector's total." />.</>}
        under={<p className="mt-2 text-xs text-muted" data-license-line="1">License: public (<Hint words="EIA" why="U.S. Energy Information Administration: its data are in the public domain, and EIA asks to be credited as the source. Every table this page reads is public in the ERW's license register." />). File built {F.built.slice(0, 10)}.</p>}
      />

      <HeadlineRow>
        <HeadlineNumber label="Industrial sector, latest month" value={last ? <Fig v={monthValue(F, "total", last)} src={SRC.monthly} k="h-month" /> : <Fig v={null} src={SRC.monthly} k="h-month" />} unit={F.monthly.unit} note={last ? `${monthWords(last)}: ${F.monthly.labels.total}` : undefined} />
        <HeadlineNumber label={`Industrial sector, ${lastYear ?? "latest whole year"}`} value={<Fig v={lastYear ? yearSum(F, "total", lastYear) : null} src={`The sum of the year's twelve months. ${SRC.monthly}`} k="h-year" />} unit={F.monthly.unit} note="the twelve months summed" />
        <HeadlineNumber label={`Largest manufacturing industry by fuel, ${F.industries.survey_year}`} value={<Fig v={top.total} src={SRC.mecs} k="h-top" />} unit={F.industries.unit.split(" ")[0]} note={`${top.name} (NAICS ${top.naics}), United States: fuel consumption, feedstocks not counted`} />
      </HeadlineRow>

      <ToolSection title="The industrial sector, month by month" id="monthly">
        <Form anchor="monthly" keep={keep(["from"])}>
          <AutoSubmitSelect name="from" value={from} options={fromYears.map((y) => ({ value: y, label: `From ${y}` }))} label="Months drawn" />
        </Form>
        <ChartFrame title={`Energy consumed by the industrial sector, ${F.monthly.unit} a month`} tip={<Hint words=" (source)" why={`${SRC.monthly} Electricity sold to industrial customers counts the electricity delivered; the losses are the industrial sector's share of the energy lost making and moving it, as EIA allocates them; the total counts both.`} />}>
          <LineChart lines={monthlyLines} unit={F.monthly.unit} x="month" ariaLabel="Energy consumed by the industrial sector by source, by month" />
        </ChartFrame>
        {last && yearAgo ? (
          <ToolTable
            caption="The latest month beside the same month a year before"
            head={["Source", monthWords(last), monthWords(yearAgo), "Change"]}
            rows={MONTHLY_KEYS.map((k) => {
              const a = monthValue(F, k, last), b = monthValue(F, k, yearAgo);
              return { key: k, highlight: k === "total", cells: [F.monthly.labels[k] ?? k, <Fig key="a" v={a} src={SRC.monthly} k={`m-${k}`} />, <Fig key="b" v={b} src={SRC.monthly} k={`m1-${k}`} />,
                <Fig key="c" v={a !== null && b !== null && b ? (100 * (a - b)) / b : null} src={`The change from the same month a year before, percent of the earlier month. ${SRC.monthly}`} k={`mc-${k}`} digits={(v) => pct1(v) as string} />] };
            })}
          />
        ) : null}
      </ToolSection>

      <ToolSection title={`Manufacturing industries ranked, ${F.industries.survey_year}`} id="industries">
        <Form anchor="industries" keep={keep(["region"])}>
          <AutoSubmitSelect name="region" value={region} options={MECS_REGIONS.map((r) => ({ value: r.key, label: r.label }))} label="Census region" />
          <Hint words="How the ranking is formed" why={`The three-digit manufacturing industries of the survey, by their total fuel consumption in the region, largest first; an industry whose total EIA withholds stands last. ${SRC.mecs}`} />
        </Form>
        <ToolTable
          minWidth={980}
          caption={`Manufacturing industries by fuel consumption, ${F.industries.survey_year}, ${MECS_REGIONS.find((r) => r.key === region)?.label}`}
          head={["Industry", "Share", ...MECS_FUELS.map((f) => f.label)]}
          rows={ranked.map((r, i) => ({ key: r.naics, cells: [
            <span key="n" title={`NAICS ${r.naics}`} data-industry-rank={i + 1}>{i + 1}. {r.name}</span>,
            <Fig key="s" v={shareOfSum(F, r.naics, region)} src={`The industry's total as a percent of the sum of the three-digit industries' totals in the region; not held where EIA withholds a total there. ${SRC.mecs}`} k={`sh-${r.naics}`} digits={(v) => `${v.toFixed(1)}%`} />,
            ...MECS_FUELS.map((f) => <Fig key={f.key} v={r.fuels[f.key] ?? null} src={(r.fuels[f.key] ?? null) === null ? WITHHELD : `${f.label}, ${F.industries.unit.split(" ")[0]}. ${SRC.mecs}`} k={`f-${r.naics}-${f.key}`} />),
          ] }))}
        />
      </ToolSection>

      <ToolSection title="Two industries side by side" id="two-industries">
        <Form anchor="two-industries" keep={keep(["a", "b"])}>
          <AutoSubmitSelect name="a" value={ia} options={choices} label="Industry A" />
          <AutoSubmitSelect name="b" value={ib} options={choices} label="Industry B" />
          <Hint words="The industries drawn first" why={`Industry A is ${name(usRanked[0].naics)} and Industry B is ${name(usRanked[1].naics)}: the two largest three-digit industries in the nation in ${F.industries.survey_year}. The page's own choice.`} />
        </Form>
        <ToolTable
          caption={`Fuel consumption of ${name(ia)} and ${name(ib)}, ${F.industries.survey_year}, ${MECS_REGIONS.find((r) => r.key === region)?.label}`}
          head={[`Fuel (${MECS_REGIONS.find((r) => r.key === region)?.label}, ${F.industries.unit.split(" ")[0]})`, `A: ${name(ia)}`, `B: ${name(ib)}`]}
          rows={MECS_FUELS.map((f) => ({ key: f.key, highlight: f.key === "total", cells: [f.label,
            <Fig key="a" v={fuelCell(ia, f.key)} src={fuelCell(ia, f.key) === null ? WITHHELD : SRC.mecs} k={`a-${f.key}`} />,
            <Fig key="b" v={fuelCell(ib, f.key)} src={fuelCell(ib, f.key) === null ? WITHHELD : SRC.mecs} k={`b-${f.key}`} />] }))}
        />
        <h3 className="mb-1 mt-5 font-serif text-base text-accent">Electricity, MWh</h3>
        <ToolTable
          caption={`Electricity of ${name(ia)} and ${name(ib)}, ${F.industries.survey_year}`}
          head={["Component (MWh)", `A: ${name(ia)}`, `B: ${name(ib)}`]}
          rows={ELEC.map((e) => ({ key: e.key, highlight: e.key === "elec_net_demand", cells: [e.label,
            <Fig key="a" v={elec(ia, e.key)} src={elec(ia, e.key) === null ? WITHHELD : `MWh. ${SRC.mecs} (Table 11.1 and 11.3)`} k={`ea-${e.key}`} digits={whole} />,
            <Fig key="b" v={elec(ib, e.key)} src={elec(ib, e.key) === null ? WITHHELD : `MWh. ${SRC.mecs} (Table 11.1 and 11.3)`} k={`eb-${e.key}`} digits={whole} />] }))}
        />
      </ToolSection>

      <ToolSection title="States, year by year" id="states">
        <Form anchor="states" keep={keep(["year", "src"])}>
          <AutoSubmitSelect name="year" value={String(year)} options={[...years].reverse().map((y) => ({ value: y, label: y }))} label="Year" />
          <AutoSubmitSelect name="src" value={src} options={SEDS_SOURCES.map((s) => ({ value: s.key, label: s.label }))} label="Source" />
        </Form>
        <ToolTable
          minWidth={640}
          caption={`States by industrial ${srcLabel.toLowerCase()} consumption, ${year}`}
          head={["State", `${srcLabel} (TBtu)`, ...(src === "total" ? [] : ["Total (TBtu)"]), "Average price (USD per MMBtu)", "Expenditures"]}
          rows={byState.map((r, i) => ({ key: r.st, cells: [
            <span key="n" data-state-rank={i + 1}>{i + 1}. {stateName(r.st)}</span>,
            <Fig key="v" v={r.value} src={SRC.seds} k={`s-${r.st}`} />,
            ...(src === "total" ? [] : [<Fig key="t" v={r.total} src={SRC.seds} k={`st-${r.st}`} />]),
            <Fig key="p" v={r.price} src={`The industrial sector's total average price, nominal dollars. ${SRC.seds}`} k={`sp-${r.st}`} digits={usd} />,
            <Fig key="e" v={r.expenditures} src={`The industrial sector's total expenditures, nominal dollars. ${SRC.seds}`} k={`se-${r.st}`} digits={billions} />,
          ] }))}
        />
      </ToolSection>

      <ToolSection title="Two states side by side" id="two-states">
        <Form anchor="two-states" keep={keep(["sa", "sb"])}>
          <AutoSubmitSelect name="sa" value={sa} options={stateOptions} label="State A" />
          <AutoSubmitSelect name="sb" value={sb} options={stateOptions} label="State B" />
          <Hint words="The states drawn first" why={`State A is ${stateName(firstTwo[0].st)} and State B is ${stateName(firstTwo[1].st)}: the two largest by the industrial sector's total consumption in ${sYear}. The page's own choice.`} />
        </Form>
        <ChartFrame title={`Industrial ${srcLabel.toLowerCase()} consumption, TBtu a year`} tip={<Hint words=" (source)" why={SRC.seds} />}>
          <LineChart lines={stateLines} unit="TBtu" x="year" ariaLabel={`Industrial ${srcLabel} consumption by year, ${stateName(sa)} and ${stateName(sb)}`} />
        </ChartFrame>
        <ToolTable
          caption={`${stateName(sa)} and ${stateName(sb)}, ${year}`}
          head={[`${year}`, `A: ${stateName(sa)}`, `B: ${stateName(sb)}`]}
          rows={[
            ...SEDS_SOURCES.map((s) => ({ key: s.key, highlight: s.key === "total", cells: [`${s.label} (TBtu)`, <Fig key="a" v={stateValue(F, sa, s.key, year)} src={SRC.seds} k={`sa-${s.key}`} />, <Fig key="b" v={stateValue(F, sb, s.key, year)} src={SRC.seds} k={`sb-${s.key}`} />] })),
            { key: "chg", cells: [`Total, change since 2019`, <Fig key="a" v={changePct(F, sa, "total", 2019, year)} src={`Percent change of the total from 2019 to ${year}. ${SRC.seds}`} k="sa-chg" digits={(v) => pct1(v) as string} />, <Fig key="b" v={changePct(F, sb, "total", 2019, year)} src={`Percent change of the total from 2019 to ${year}. ${SRC.seds}`} k="sb-chg" digits={(v) => pct1(v) as string} />] },
            { key: "price", cells: ["Average price (USD per MMBtu)", <Fig key="a" v={statePrice(F, sa, year)} src={SRC.seds} k="sa-price" digits={usd} />, <Fig key="b" v={statePrice(F, sb, year)} src={SRC.seds} k="sb-price" digits={usd} />] },
            { key: "exp", cells: ["Expenditures, total", <Fig key="a" v={stateValue(F, sa, "total", year, "expenditures_usd")} src={`Nominal dollars. ${SRC.seds}`} k="sa-exp" digits={billions} />, <Fig key="b" v={stateValue(F, sb, "total", year, "expenditures_usd")} src={`Nominal dollars. ${SRC.seds}`} k="sb-exp" digits={billions} />] },
            { key: "sales", cells: [`Electricity sold to industry, ${year} (TWh)`, <Fig key="a" v={salesYear(F, sa, year)} src={`The year's twelve months summed. ${SRC.sales}`} k="sa-sales" digits={twh} />, <Fig key="b" v={salesYear(F, sb, year)} src={`The year's twelve months summed. ${SRC.sales}`} k="sb-sales" digits={twh} />] },
          ]}
        />
        <ChartFrame title="Electricity sold to industrial customers, MWh a month" tip={<Hint words=" (source)" why={SRC.sales} />}>
          <LineChart lines={salesLines} unit="MWh" x="month" ariaLabel={`Electricity sold to industrial customers by month, ${stateName(sa)} and ${stateName(sb)}`} />
        </ChartFrame>
      </ToolSection>

      <ToolSection title={`EIA's outlook by industry, AEO${F.outlook.release}`} id="outlook">
        <Form anchor="outlook" keep={keep(["oi", "os", "ca", "cb"])}>
          <AutoSubmitSelect name="oi" value={oi} options={oInds.map((k) => ({ value: k, label: OUTLOOK_INDUSTRIES[k] }))} label="Industry" />
          <AutoSubmitSelect name="os" value={os} options={series.map((s) => ({ value: s, label: s.split(" : ").slice(1).join(": ") || s }))} label="Series" />
          <AutoSubmitSelect name="ca" value={ca} options={caseKeys.map((k) => ({ value: k, label: F.outlook.cases[k] }))} label="Case A" />
          <AutoSubmitSelect name="cb" value={cb} options={caseKeys.map((k) => ({ value: k, label: F.outlook.cases[k] }))} label="Case B" />
          <Hint words="The cases drawn first" why="Case A is the Counterfactual Baseline case and Case B is the High Electricity Demand case: the page's own choice. AEO2026 names no Reference case." />
        </Form>
        <ChartFrame title={`${os.split(" : ").join(": ")}, ${F.outlook.unit} a year`} tip={<Hint words=" (source)" why={SRC.aeo} />}>
          <LineChart lines={outLines} unit={F.outlook.unit} x="year" ariaLabel={`EIA's projection of ${os} in two cases`} />
        </ChartFrame>
        <ToolTable
          minWidth={640}
          caption={`${os}, every case of AEO${F.outlook.release}`}
          head={["Case", ...outYears]}
          rows={caseKeys.map((c) => ({ key: c, highlight: c === ca || c === cb, cells: [F.outlook.cases[c], ...outYears.map((y) => <Fig key={y} v={outlookValue(F, oi, os, c, y)} src={SRC.aeo} k={`o-${c}-${y}`} />)] }))}
        />
      </ToolSection>

      <IndustryDecisions />
      <TableDownloads tables={TABLES} />
      <SourceLine tables={TABLES} note={<>Method: <a href="/data/methods/industry_page">the page&apos;s method note</a>. EIA&apos;s figures as published; the page sums only a year&apos;s twelve months and computes the shares and changes it names.</>} />
      </div>
    </ToolPage>
    </Brand>
  );
}
