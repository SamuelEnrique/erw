import type { Metadata } from "next";
import Link from "next/link";
import { attempt } from "@/lib/supabase";
import { choices, direction, monthName, MEASURES, TABLE, view } from "@/lib/buildout";
import { DurationBars, Fold, GridTable, H2, Headlines, Panel, SolarLine, SURFACE, V, YearTable } from "./parts";
import { buildoutRows } from "./read";

// Session 69: the storage build-out tracker, "How much storage has been built". How much battery storage operates on
// each grid, of what duration, how that grew year by year, how it compares with solar, and what is planned. Every
// number is a row of storage_buildout_monthly (warehouse/derived/storage_buildout.py; EIA-860M, derived), read from
// Supabase by ./read.ts and carried with its check key (series|storage_buildout_monthly|<entity>|<variable>|<month>),
// so the page does no arithmetic. Its pieces are its own (./parts.tsx): see the note there.
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
  return (
    <div className="border border-rule text-ink" style={{ background: SURFACE }}>
      <div className="grid md:grid-cols-[220px_minmax(0,1fr)]">
        <Panel grid={grid} measure={measure} />
        <div className="min-w-0 p-4 md:p-6">
          <h1 className="mb-1 font-serif text-3xl text-accent">How much storage has been built</h1>
          <p className="max-w-3xl text-sm text-muted">
            Battery storage operating on each US grid, how long it can run, and how it compares with solar, from the monthly generator inventory of the US
            Energy Information Administration. What the batteries do hour by hour is on <Link href="/storage">Storage</Link>.
          </p>

          {!v ? (
            <div className="mt-4 border border-dashed border-rule px-3 py-2 text-sm text-muted" role="status">
              <span className="font-semibold text-ink">no data</span> for the storage build-out: {rows.ok ? `${TABLE} returned no rows` : rows.reason}
            </div>
          ) : (
            <>
              <p className="mt-4 max-w-3xl text-lg leading-snug">
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
              <p className="text-xs text-muted">As of {monthName(v.newest)}, the newest inventory held; a year ago is {monthName(v.before)}.</p>

              <Headlines v={v} />

              <H2>Operating storage by year, by duration</H2>
              <p className="mb-2 max-w-3xl text-sm">
                Each bar is the fleet at a year&apos;s end, in {MEASURES[measure].unit}, split by how long each battery can discharge at full power. Darker is
                longer. If duration were growing, the dark share of the bars would grow.
              </p>
              <DurationBars v={v} />
              <p className="text-xs text-muted">
                * {v.newest.slice(0, 4)} is the year so far, to {monthName(v.newest)}. Duration is a unit&apos;s energy (MWh) over its power (MW).
                {measure === "mwh" && v.notReportedMw && v.notReportedMw.value > 0 ? <> Units with no energy value (<V row={v.notReportedMw} /> MW) cannot be drawn in MWh.</> : null}
              </p>

              <H2>Storage against solar</H2>
              <SolarLine v={v} />
              <p className="max-w-3xl text-sm">
                The ratio is the hours the grid&apos;s batteries could carry its whole solar fleet at nameplate output: at 1.0, they hold one hour of it.
              </p>
              <YearTable v={v} />

              <H2>By grid</H2>
              <GridTable v={v} />
              <p className="mt-1 max-w-3xl text-xs text-muted">
                As of {monthName(v.newest)}. Added in twelve months is net of retirements. Planned is every battery unit developers have reported to EIA, by the
                year they expect it online; planned energy (MWh) is not held, because EIA&apos;s monthly inventory gives none for planned units. PJM is included:
                these are EIA&apos;s public generator data, not PJM&apos;s prices.
              </p>

              <div className="mt-8 border-t border-rule">
                <Fold title="How generators are assigned to a grid, and how many were not">
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
                </Fold>
                <Fold title="What EIA-860M covers and misses">
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
                </Fold>
                <Fold title="The newest month held">
                  <p>
                    {monthName(v.newest)}. EIA publishes each month&apos;s inventory near the end of the following month, and units that started late are added to
                    later inventories, so the newest months grow a little when the next one arrives.
                  </p>
                </Fold>
              </div>
            </>
          )}

          <p className="mt-6 text-xs text-muted">
            Source: ERW table <Link href={`/data#${TABLE}`} className="font-mono">{TABLE}</Link> (derived), computed from the US Energy Information Administration&apos;s Form
            EIA-860M, Monthly Update to the Annual Electric Generator Report{v ? `, inventory of ${monthName(v.newest)}` : ""}. <Link href={METHOD}>Method</Link>.
          </p>
        </div>
      </div>
    </div>
  );
}
