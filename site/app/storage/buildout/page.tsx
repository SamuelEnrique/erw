import type { Metadata } from "next";
import { AskErcotLink } from "@/components/AskErcotLink";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection } from "@/components/tool/ToolPage";
import { attempt } from "@/lib/supabase";
import { BUCKETS, choices, direction, monthName, MEASURES, NOT_REPORTED, TABLE, view } from "@/lib/buildout";
import { DurationBars, GREY, GridTable, Panel, RAMP, SolarLine, V, YearTable } from "./parts";
import { buildoutRows } from "./read";

// Session 69: the storage build-out tracker, "How much storage has been built". How much battery storage operates on
// each grid, of what duration, how that grew year by year, how it compares with solar, and what is planned. Every
// number is a row of storage_buildout_monthly (warehouse/derived/storage_buildout.py; EIA-860M, derived), read from
// Supabase by ./read.ts and carried with its check key (series|storage_buildout_monthly|<entity>|<variable>|<month>),
// so the page does no arithmetic. Session 72 (session 69's finish): the page frame, header, input panel, headline
// numbers, chart frames, sections, folds and source line are session 67's shared pieces (components/tool/ToolPage.tsx);
// the two server-drawn charts and the two tables stay in ./parts.tsx, with their colors in app/tokens.css. The page is
// "review" in lib/release.ts.
export const metadata: Metadata = { title: "How much storage has been built" };
export const revalidate = 3600;

const METHOD = "/data/methods/storage_buildout";

export default async function Buildout({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const { grid, measure } = choices(Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined])));
  const rows = await attempt(buildoutRows);
  const v = rows.ok ? view(rows.data, grid, measure) : null;
  const outside = v?.table.find((g) => g.slug === "outside");
  const us = v?.table.find((g) => g.slug === "us");
  const notReported = !!v && measure === "mw" && v.years.some((y) => (y.notReported?.value ?? 0) > 0);
  return (
    <ToolPage>
      <ToolHeader
        title="How much storage has been built"
        lead={<>Battery storage operating on each US grid, how long it can run, and how it compares with solar, from the monthly generator inventory of the US
          Energy Information Administration. What the batteries do hour by hour is on <Link href="/storage">Storage</Link>.</>}
      />
      {grid.slug === "ercot" ? <AskErcotLink context={{ view: "/storage/buildout", title: "How much storage has been built", settings: { grid: "ERCOT", measure: MEASURES[measure].label, ...(v ? { inventory: v.newest } : {}) } }} /> : null}
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note="Power is how fast the batteries can discharge. Energy is how much they hold. Energy over power is duration, in hours.">
            <Panel grid={grid} measure={measure} />
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!v ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">
              <span className="font-semibold">no data</span> for the storage build-out: {rows.ok ? `${TABLE} returned no rows` : rows.reason}
            </p>
          ) : (
            <>
              <p className="mb-1 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                {v.mw && v.mwh && v.hours && v.mwBefore ? (
                  <>
                    {grid.name} has <V row={v.mw} /> MW of batteries holding <V row={v.mwh} /> MWh, an average of <V row={v.hours} /> hours,{" "}
                    {direction(v.mw.value, v.mwBefore.value)} <V row={v.mwBefore} /> MW a year ago.
                  </>
                ) : v.mw && v.mw.value === 0 ? (
                  <>{grid.name} has no operating battery storage in EIA&apos;s inventory of {monthName(v.newest)}.</>
                ) : (
                  <span className="text-muted">The summary is not held for {grid.name}: the table lacks a value it needs for {monthName(v.newest)}.</span>
                )}
              </p>
              <p className="mb-6 text-xs text-muted">As of {monthName(v.newest)}, the newest inventory held; a year ago is {monthName(v.before)}.</p>

              <HeadlineRow>
                <HeadlineNumber label="Operating power" value={<V row={v.mw} />} unit="MW" note={<><V row={v.units} /> battery units</>} />
                <HeadlineNumber label="Operating energy" value={<V row={v.mwh} />} unit="MWh" note={<>average duration <V row={v.hours} /> hours</>} />
                <HeadlineNumber label="Added over the last twelve months, net of retirements" value={<V row={v.addedMw} />} unit="MW" note={<><V row={v.addedMwh} /> MWh</>} />
              </HeadlineRow>

              <ToolSection title="Operating storage by year, by duration">
                <p className="mb-2 max-w-3xl text-sm">
                  Each bar is the fleet at a year&apos;s end, in {MEASURES[measure].unit}, split by how long each battery can discharge at full power. Darker is
                  longer. If duration were growing, the dark share of the bars would grow.
                </p>
                <ChartFrame title={`${grid.name}, ${MEASURES[measure].unit} at each year's end`}
                  legend={[...BUCKETS.map((b, i) => ({ label: b.label, color: RAMP[i] })), ...(notReported ? [{ label: NOT_REPORTED.label, color: GREY }] : [])]}
                  note={<>* {v.newest.slice(0, 4)} is the year so far, to {monthName(v.newest)}. Duration is a unit&apos;s energy (MWh) over its power (MW).
                    {measure === "mwh" && v.notReportedMw && v.notReportedMw.value > 0 ? <> Units with no energy value (<V row={v.notReportedMw} /> MW) cannot be drawn in MWh.</> : null}</>}>
                  <DurationBars v={v} />
                </ChartFrame>
              </ToolSection>

              <ToolSection title="Storage against solar">
                <ChartFrame title="MWh of batteries per MW of solar, at each year's end"
                  note="The ratio is the hours the grid's batteries could carry its whole solar fleet at nameplate output: at 1.0, they hold one hour of it.">
                  <SolarLine v={v} />
                </ChartFrame>
                <YearTable v={v} />
              </ToolSection>

              <ToolSection title="By grid" note={<>As of {monthName(v.newest)}. Added in twelve months is net of retirements. Planned is every battery unit developers have reported to EIA, by the
                year they expect it online; planned energy (MWh) is not held, because EIA&apos;s monthly inventory gives none for planned units. PJM is included:
                these are EIA&apos;s public generator data, not PJM&apos;s prices.</>}>
                <GridTable v={v} />
              </ToolSection>

              <div className="mb-8 border-t border-rule">
                <Fold title="How generators are assigned to a grid, and how many were not">
                  <div className="max-w-3xl space-y-2">
                    <p>
                      A generator belongs to the grid named by its balancing authority code in EIA&apos;s inventory: CISO is CAISO, ERCO is ERCOT, ISNE is ISO-NE, NYIS
                      is NYISO, SWPP is SPP, and MISO and PJM are themselves. Any other code, or none, is not assigned to one of the seven.
                    </p>
                    <p>
                      Not assigned: <V row={outside?.units} /> operating battery units, <V row={outside?.mw} /> MW, of the <V row={us?.units} /> units and{" "}
                      <V row={us?.mw} /> MW in the United States. Most sit in the West and Southeast outside any ISO. They are in the United States total and in the
                      table&apos;s row &quot;Outside the ISOs&quot;; the total is the seven grids plus that row.
                    </p>
                    <p>The <Link href={METHOD}>method</Link> counts how many of them carry no code at all, and gives the same counts for solar and planned units.</p>
                  </div>
                </Fold>
                <Fold title="What EIA-860M covers and misses">
                  <div className="max-w-3xl space-y-2">
                    <p>
                      Form EIA-860M is the monthly inventory of utility-scale generators: units at plants of 1 MW and above. Batteries behind a customer&apos;s meter
                      and rooftop solar are not in it.
                    </p>
                    <p>
                      Planned dates are the developers&apos; own estimates. They slip, and some planned units are never built: read the planned columns as intentions,
                      not a forecast.
                    </p>
                    <p>
                      The years are rebuilt from the one inventory held, by each unit&apos;s first operating month. A battery retired before {Number(v.newest.slice(0, 4)) - 1} is in
                      no year, and a unit shows its present MW and MWh in every year it operated, so early years are slightly understated.
                    </p>
                  </div>
                </Fold>
                <Fold title="The newest month held">
                  <p className="max-w-3xl">
                    {monthName(v.newest)}. EIA publishes each month&apos;s inventory near the end of the following month, and units that started late are added to
                    later inventories, so the newest months grow a little when the next one arrives.
                  </p>
                </Fold>
              </div>
            </>
          )}
        </div>
      </div>
      <SourceLine tables={[TABLE]}
        note={<>Derived by the ERW from the US Energy Information Administration&apos;s Form EIA-860M, Monthly Update to the Annual Electric Generator
          Report{v ? `, inventory of ${monthName(v.newest)}` : ""}. <Link href={METHOD}>Method</Link>.</>} />
    </ToolPage>
  );
}
