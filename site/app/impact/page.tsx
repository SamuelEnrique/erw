import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { SourceLine, Tip, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { NOT_MODELED, TABLE, TAX_TABLE } from "@/lib/impact";
import { pack, type Row } from "@/lib/forecast";
import { gasSeverance, groupPlanned, params } from "@/lib/forecastdata";
import { parse, withProjects } from "@/lib/forecastui";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import { Forecast } from "./Forecast";

// Session 4213 (chain 239, the owner's prompt of 13 November 2026): /impact becomes the forecast tool, "Local impact"
// (the name is a ruling for Samuel with that default). Session 347's page answered three questions for one project in
// one year from NLR's JEDI models; this page keeps its source (nlr_jedi_multipliers, read whole once) and its per-state
// view, and adds the years: construction and operating jobs and earnings, property tax by the state's statute where
// one is held, sales and use tax, state income tax, severance on a gas plant's in-state fuel, and present values, for
// two scenarios side by side (app/impact/Forecast.tsx; lib/forecast.ts; docs/methods/forecast.md, internal and never
// linked from here). The first draw is the address's scenarios, computed on the server, so every figure carries its
// check key in the HTML; every change after it is computed in the browser and sends no request.
export const metadata: Metadata = { title: "Local impact" };
export const dynamic = "force-dynamic";

export default async function Impact({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const start = parse(q);
  const read = await attempt(() => rest<Row>("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${TABLE}`, variable: "in.(jobs,earnings,output)", order: "entity,variable" }, HOURLY));
  const P = params();
  // session 4216: the planned projects of the left box's list (EIA-860M's planned generators in energy_projects); a failed
  // read leaves the list out and nothing else
  const planned = await attempt(() => rest<{ entity_id: string; name: string | null; capacity_mw: number | null; tech: string | null; state: string | null; county: string | null; date: string | null }>("entities", {
    select: "entity_id,name,capacity_mw,tech:extra->>technology_group,state:extra->>state,county:extra->>county,date:extra->>date",
    table_name: "eq.energy_projects", "extra->>kind": "eq.planned", "extra->>technology_group": "in.(wind,solar,natural_gas,geothermal)", order: "entity_id" }, HOURLY, 10_000));
  const list = planned.ok ? groupPlanned(planned.data) : [];
  return (
    <Brand noUsage>
      <ToolPage>
        <ToolHeader
          title="Local impact"
          crumb="Economics"
          lead={<>Jobs, earnings and state and local taxes of a wind, solar, gas or geothermal plant, year by year from its construction to the end of its operation, with their present value: two scenarios side by side.<Tip id="lead" label="the tool">Jobs, earnings and output are NLR&apos;s JEDI models read for every state. Property tax follows the state&apos;s statute where the ERW holds one (Minnesota, South Dakota, North Dakota, Nebraska, Iowa; Kansas exempts its first ten years; Oregon's solar fee in lieu by county agreement; Wyoming's wind generation excise, added to the property tax; Florida's 80 percent device exemption, Arizona's 20 percent valuation North Carolina's 80 percent solar exclusion and Maryland's 50 percent of generating equipment, on the reader's own rate; Michigan's solar specific tax by local option; Nevada's 55 percent abatement where approved, on the reader's own rate; Vermont's solar capacity tax, added to the property tax; Wisconsin's payments to the municipality and county in place of it); sales and income tax follow the 2026 rates; severance follows the rules of the severance calculator. Every dollar is a 2025 dollar. Gross effects of an input-output model: what the project adds, not net of what the land, money and workers would otherwise have done. {NOT_MODELED.why}</Tip></>}
        />
        {!read.ok ? (
          <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {read.reason}</p>
        ) : (
          <Forecast P={P} jedi={pack(read.data)} start={withProjects(start, q, list.map((p) => p.id))} rules={gasSeverance()} planned={list} />
        )}
        <div className="mt-10">
          <TableDownloads tables={[TABLE]} />
          <p className="mt-1 text-xs text-muted" data-tax-download="held"><code className="font-mono">{TAX_TABLE}</code> is held for review and not offered for download: its publishers&apos; terms are not read yet (<Link href="/data">Data and methods</Link>).</p>
          <SourceLine tables={[TABLE, TAX_TABLE, "lbnl_wind_capacity_factors", "lbnl_solar_projects", "eia860_plants_annual", "eia_steo_forecasts"]}
            note={<>Jobs, earnings and output from the National Laboratory of the Rockies (NLR, formerly NREL), <a href="https://www.nlr.gov/analysis/jedi/models" rel="noopener">JEDI models</a>, their own formulas evaluated by the ERW for each state; credit U.S. Department of Energy (DOE)/NLR/ALLIANCE. NLR&apos;s terms: &ldquo;The user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data&rdquo; (<a href="https://www.nlr.gov/disclaimer" rel="noopener">the notice</a>); the Data are provided as is. Capital cost, construction time, life and heat rate: <a href="https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2025.pdf" rel="noopener">EIA&apos;s capital cost study for AEO2025</a>. Price index: BEA&apos;s GDP implicit price deflator, as EIA&apos;s Short-Term Energy Outlook carries it. Sales and income tax rates: <a href="https://taxfoundation.org/data/all/state/2026-sales-tax-rates-midyear/" rel="noopener">Tax Foundation, 2026</a> (CC BY-NC 4.0). Property tax: the statutes of Minnesota, South Dakota, North Dakota, Nebraska, Iowa, Kansas, Oregon, Wyoming, Florida, Arizona, North Carolina, Michigan, Vermont, Wisconsin, Nevada and Maryland. Severance: the pages the <Link href="/severance">severance calculator</Link> cites. Discount rate: OMB Circular A-94.</>} />
        </div>
      </ToolPage>
    </Brand>
  );
}
