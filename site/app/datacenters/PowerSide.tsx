// Session 467 (chain 019): the datacenter tracker on the power side. For every site that rests on a public source, its
// grid, its county and the queue's own fields, and what a flat load paid at that grid's load zones under the cost-of-power
// calculator's defaults. Since 21 October 2026 datacenter_facilities is held whole (license needed): most of its rows
// rest on news stories and on operators' pages whose publishers ask for permission. The rows that rest on a public
// source are the interconnection-queue positions that name a datacenter or a large load (the third machine's session
// 441, docs/reviews/sources-by-row-2026-10-21.md, on wip/441-450-third: 2 of 420 facilities, both from ERCOT's queue),
// so this section reads them from each ISO's own queue table (lib/data.ts, queueSites), never from the held table, and a
// queue held itself is named, not read. The cost figures are /cost-of-power's own (lib/datacenter.ts, regionCosts, the
// same months and rule as the calculator's headline for that region): no figure the calculator shows moves.
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { Tip, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import type { EntityRow } from "@/lib/data";
import { BUYS, regionCosts, shortMonth, two, type RegionCost } from "@/lib/datacenter";
import { INDEX, yearFiles } from "@/lib/datacenterdata";
import { licenseHeldGrid } from "@/lib/license";

/** The grids' names as the calculator writes them (data/datacenter/index.json), or the prefix in capitals. */
const gridName = (g: string) => INDEX.grids[g]?.name ?? g.toUpperCase();
/** A queue table's grid, by its name: ercot_interconnection_queue is ERCOT's. */
const gridOf = (r: EntityRow) => r.table_name.replace(/_interconnection_queue$/, "");
/** The point of interconnection's first line: the queue's field often runs on with the transformer's ratings. */
const firstLine = (s: string | undefined) => (s ?? "").split(/\r?\n/).map((x) => x.trim()).find(Boolean) ?? "";
const day = (d: string | undefined) => (d ? d.slice(0, 10) : "not stated");
/** The calculator's address for a region, under its defaults. */
const calcHref = (grid: string, region: string) => `/cost-of-power?grid=${encodeURIComponent(grid)}&region=${encodeURIComponent(region)}`;

/** Session 467: the load zones of a grid where a load settles (ERCOT names its regions zone or hub; the other grids'
 *  regions carry no kind, and every one is shown). Empty when the calculator holds no prices for the grid. */
export function zoneCosts(grid: string): RegionCost[] {
  const g = INDEX.grids[grid];
  if (!g) return [];
  return regionCosts(yearFiles(grid), g, ["zone"]);
}

type Read = { ok: true; data: { rows: EntityRow[]; held: string[] } } | { ok: false; reason: string };

export function PowerSide({ read }: { read: Read }) {
  const rows = read.ok ? read.data.rows : [];
  // a grid whose prices are held (lib/license.ts) shows no price; today the held grids' queues are held too, so none is drawn
  const grids = [...new Set(rows.map(gridOf))].filter((g) => INDEX.grids[g] && !licenseHeldGrid(g));
  const costs = new Map(grids.map((g) => [g, zoneCosts(g)]));
  const zoneOf = (r: EntityRow): RegionCost | null => {
    const z = (r.extra?.zone ?? "").trim();
    return z ? costs.get(gridOf(r))?.find((c) => c.id === z || c.name === z) ?? null : null;
  };
  return (
    <section aria-label="On the power side" data-power-side="1">
      <ToolSection title="On the power side: the sites a public source names" id="power-side"
        note={<>Source: each grid operator&apos;s own interconnection queue as the ERW holds it (its table and the day it was read are in the row), and the
          ERW&apos;s hourly prices at each load zone as the <Link href="/cost-of-power">cost of power</Link> calculator reads them. <Link href="/data/methods/datacenter_facilities">Method</Link>.</>}>
        <p className="mb-3 max-w-3xl text-sm" data-power-lead="1">
          Of the facilities above, those that rest on a public source are the interconnection-queue positions that name a datacenter or a large load; the
          others rest on news stories or on operators&apos; own pages, whose publishers ask for permission, and stay held. For each such site: its grid, its
          county, what the queue says of its connection, and what a flat load paid at that grid&apos;s load zones over the calculator&apos;s last twelve
          months. A queue position&apos;s megawatts are the generation or storage it asks to connect, not the site&apos;s load.
        </p>
        {!read.ok ? (
          <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The queues could not be read, so no number is shown: {read.reason}</p>
        ) : rows.length === 0 ? (
          <p className="text-sm text-muted">No position in the queues read names a datacenter or a large load.</p>
        ) : (
          <ToolTable caption="Sites from the interconnection queues" minWidth={760} words
            head={["Site", "Grid", "County, state", "Queue position",
              <span key="mw">MW asked to connect<Tip id="power-mw" label="the MW asked to connect">The generation or storage the position asks to connect, as the grid operator&apos;s queue states it (the column capacity_mw of the queue&apos;s table, read from the live set with its check key). It is not the site&apos;s load: no queue states that. Hover a figure for its row&apos;s table and the day it was read.</Tip></span>,
              "Point of interconnection", "Load zone", "Queue date, in service"]}
            rows={rows.map((r) => {
              const z = zoneOf(r);
              return {
                key: r.entity_id,
                cells: [
                  <span key="n" data-power-site={r.entity_id}>{r.name ?? "not named"}{r.operator ? <span className="text-muted">, {r.operator}</span> : null}</span>,
                  gridName(gridOf(r)),
                  [r.extra?.county, r.extra?.state].filter(Boolean).join(", ") || "not stated",
                  <span key="q">{r.extra?.queue_id ?? r.entity_id}: {r.extra?.iso_status ?? r.status ?? "status not stated"}{r.source_url ? <> (<a href={r.source_url} className="underline" rel="noopener">report</a>, read {day(r.vintage ?? undefined)})</> : null}</span>,
                  r.capacity_mw === null ? "not stated" : (
                    <span key="mw" title={`${Number(r.capacity_mw).toLocaleString("en-US")} MW the position asks to connect, not the site's load. Read from ${r.table_name} (${r.extra?.queue_id ?? r.entity_id}), the queue report read ${day(r.vintage ?? undefined)}.`} data-power-mw={r.entity_id}>
                      <Num check={`entity|${r.table_name}|${r.entity_id}|capacity_mw`} raw={Number(r.capacity_mw)}>{Number(r.capacity_mw).toLocaleString("en-US")}</Num>
                    </span>),
                  firstLine(r.extra?.poi) || "not stated",
                  z ? <Link key="z" href={calcHref(gridOf(r), z.id)}>{z.name}</Link> : <span key="z" className="text-muted">not stated by the queue</span>,
                  `${day(r.extra?.queue_date)}; ${r.extra?.actual_in_service_date ? `in service ${day(r.extra.actual_in_service_date)}` : `proposed ${day(r.extra?.proposed_in_service_date)}`}`,
                ],
              };
            })} />
        )}
        {read.ok && read.data.held.length ? (
          <p className="mt-2 max-w-3xl text-sm text-muted" data-power-held="1">
            Not read: the queues of {read.data.held.map(gridName).join(", ")}, held while their operators&apos; terms ask for a license.
          </p>
        ) : null}
        {grids.map((g) => {
          const cs = costs.get(g) ?? [];
          if (!cs.length) return null;
          return (
            <div key={g} className="mt-6" data-power-zones={g}>
              <ToolTable caption={`What a flat load paid in ${gridName(g)}, by load zone`} minWidth={560}
                head={["Load zone", "Bought in", "Twelve months", "USD per MWh"]}
                rows={cs.map((c) => ({
                  key: c.id,
                  cells: [
                    <Link key="z" href={calcHref(g, c.id)}>{c.name}{c.main ? " (the calculator's default)" : ""}</Link>,
                    BUYS[c.buy].toLowerCase(),
                    `${shortMonth(c.from)} to ${shortMonth(c.to)}`,
                    <Num key="v" check={`dcpow|${g}|${c.id}|per`} raw={c.per}>{two(c.per)}</Num>,
                  ],
                }))} />
              <p className="mt-2 max-w-3xl text-xs text-muted">
                A flat load, the same in every hour, at the calculator&apos;s defaults: bought in real time where twelve complete months of real-time prices are held,
                else day-ahead. Energy only: no delivery charge, no capacity charge, no tax. {g === "ercot" ? <>The queue states a county, not a load zone, and ERCOT publishes
                its load zones only as a picture of a map, with no list of counties, so the ERW does not place a site in one; each zone is shown.</> : <>Where the queue names
                no zone, each is shown.</>}
              </p>
            </div>
          );
        })}
        <p className="mt-6 max-w-3xl text-sm" data-power-epoch="1">
          How large the frontier AI facilities are being built, their power, compute and cost from satellite images and permits: Epoch AI&apos;s{" "}
          <a href="https://epoch.ai/data/data-centers" className="underline" rel="noopener">data on AI data centers</a> (their figures, not the ERW&apos;s; the ERW
          does not compute them).
        </p>
      </ToolSection>
    </section>
  );
}
