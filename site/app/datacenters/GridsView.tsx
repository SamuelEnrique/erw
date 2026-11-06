// Session 468 (chain 019): the datacenter tracker by grid, /datacenters?view=grids (in review, as the page is). For each
// grid and zone that holds a site a public source names (the interconnection-queue positions that name a datacenter or
// a large load: lib/data.ts, queueSites), how many sites, the MW their positions ask to connect, the grid's or zone's own
// queue still active beside them, and what a flat load paid at the grid's load zones: over the cost-of-power calculator's
// last twelve months (the table) and by calendar year (the chart, with its figures in the fold under it). Every figure
// carries its key: dcq| (lib/datacenter/bygrid.ts, recomputed by scripts/check-values.mjs from the queue tables) and
// dcpow| (lib/datacenter.ts, regionCosts, recomputed with the calculator's own steps).
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { GroupedBars } from "@/components/tool/GroupedBars";
import { ChartFrame, Fold, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import type { EntityRow } from "@/lib/data";
import { BUYS, shortMonth, two, type RegionCost } from "@/lib/datacenter";
import { NO_ZONE, groups, type Group, type QueueRow } from "@/lib/datacenter/bygrid";
import { INDEX } from "@/lib/datacenterdata";
import { licenseHeldGrid } from "@/lib/license";
import { zoneCosts } from "./PowerSide";

const gridName = (g: string) => INDEX.grids[g]?.name ?? g.toUpperCase();
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const mw = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
/** The cheapest and dearest of some zones' figures, first by value, then by name. */
function ends<T extends { per: number; id: string }>(xs: T[]): [T, T] | null {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a.per - b.per || a.id.localeCompare(b.id));
  return [s[0], s[s.length - 1]];
}

type Read<T> = { ok: true; data: T } | { ok: false; reason: string };
export type SitesRead = Read<{ rows: EntityRow[]; held: string[] }>;

export function GridsView({ sites, active }: { sites: SitesRead; active: Read<QueueRow[]> }) {
  if (!sites.ok) return <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The queues could not be read, so no number is shown: {sites.reason}</p>;
  const rows: QueueRow[] = sites.data.rows.map((r) => ({ table_name: r.table_name, capacity_mw: r.capacity_mw, status: r.status, zone: r.extra?.zone ?? null }));
  const gs: Group[] = groups(rows, active.ok ? active.data : []);
  const grids = [...new Set(gs.map((g) => g.grid))];
  const costs = new Map<string, RegionCost[]>(grids.filter((g) => INDEX.grids[g] && !licenseHeldGrid(g)).map((g) => [g, zoneCosts(g)]));
  const priceCell = (g: Group) => {
    const cs = costs.get(g.grid) ?? [];
    const z = g.zone === NO_ZONE ? cs : cs.filter((c) => c.id === g.zone || c.name === g.zone);
    const e = ends(z);
    if (!e) return <span className="text-muted">not held</span>;
    const [lo, hi] = e;
    return lo.id === hi.id
      ? <>USD <Num check={`dcpow|${g.grid}|${lo.id}|per`} raw={lo.per}>{two(lo.per)}</Num> ({lo.name})</>
      : <>USD <Num check={`dcpow|${g.grid}|${lo.id}|per`} raw={lo.per}>{two(lo.per)}</Num> ({lo.name}) to <Num check={`dcpow|${g.grid}|${hi.id}|per`} raw={hi.per}>{two(hi.per)}</Num> ({hi.name})</>;
  };
  return (
    <section aria-label="By grid" data-view-grids="1">
      <p className="mb-4 max-w-3xl text-sm" data-grids-lead="1">
        The sites a public source names, the interconnection-queue positions that name a datacenter or a large load, counted by grid and by the zone their
        queue states, beside that grid&apos;s own queue still waiting to connect and what a flat load paid at its load zones. The facilities that rest on news
        stories or on operators&apos; own pages are held (license needed) and are not counted here. None of these positions states the site&apos;s own load:
        their megawatts are the generation or storage each asks to connect.
      </p>
      {gs.length === 0 ? (
        <p className="text-sm text-muted">No position in the queues read names a datacenter or a large load.</p>
      ) : (
        <ToolSection title="By grid and zone" id="by-grid"
          note={<>Source: each grid operator&apos;s own interconnection queue as the ERW holds it, and the ERW&apos;s hourly prices as the{" "}
            <Link href="/cost-of-power">cost of power</Link> calculator reads them. <Link href="/data/methods/datacenter_facilities">Method</Link>.</>}>
          <ToolTable caption="Sites from public sources, by grid and zone, against the queue and the price" minWidth={820}
            head={["Grid", "Zone", "Sites", "Sites stating MW", "MW the sites ask to connect", "Active positions in the queue", "Active MW in the queue", "Flat load, last twelve months, per MWh"]}
            rows={gs.map((g) => ({
              key: `${g.grid}|${g.zone}`,
              cells: [
                gridName(g.grid),
                g.zone === NO_ZONE ? <span key="z" className="text-muted">not stated by the queue (the whole grid&apos;s queue beside it)</span> : g.zone,
                <Num key="s" check={`dcq|${g.grid}|${g.zone}|sites`} raw={g.sites}>{whole(g.sites)}</Num>,
                <Num key="w" check={`dcq|${g.grid}|${g.zone}|sites_with_mw`} raw={g.sitesWithMw}>{whole(g.sitesWithMw)}</Num>,
                <Num key="m" check={`dcq|${g.grid}|${g.zone}|mw_asked`} raw={g.mwAsked}>{mw(g.mwAsked)}</Num>,
                active.ok ? <Num key="p" check={`dcq|${g.grid}|${g.zone}|active_positions`} raw={g.activePositions}>{whole(g.activePositions)}</Num> : <span key="p" className="text-muted">not read</span>,
                active.ok ? <Num key="a" check={`dcq|${g.grid}|${g.zone}|active_mw`} raw={g.activeMw}>{whole(g.activeMw)}</Num> : <span key="a" className="text-muted">not read</span>,
                <span key="c">{priceCell(g)}</span>,
              ],
            }))} />
          <ul className="mt-3 max-w-3xl list-disc space-y-1 pl-5 text-sm">
            <li><strong>Sites</strong> counts the positions; <strong>sites stating MW</strong>, those whose position states the MW it asks for, the count behind the sum beside it.</li>
            <li><strong>Active positions</strong> are the grid&apos;s whole queue (or the zone&apos;s, where the queue names one) whose status is active: requests to connect generation or storage, not plants and not load.</li>
            <li><strong>The price</strong> is the cheapest and the dearest load zone of the grid (or the zone the queue names) for a flat load, at the calculator&apos;s defaults, over its last twelve complete months. Energy only.</li>
            {!active.ok ? <li>The queue totals could not be read: {active.reason}</li> : null}
            {sites.data.held.length ? <li data-grids-held="1">Not read: the queues of {sites.data.held.map(gridName).join(", ")}, held while their operators&apos; terms ask for a license.</li> : null}
          </ul>
        </ToolSection>
      )}
      {[...costs.entries()].map(([g, cs]) => {
        const main = cs.find((c) => c.main) ?? cs[0];
        if (!main) return null;
        const ys = [...new Set(cs.flatMap((c) => c.years.map((y) => y.y)))].sort().slice(-8);
        const per = (c: RegionCost, y: string) => c.years.find((x) => x.y === y)?.per ?? null;
        const yearRows = ys.map((y) => {
          const held = cs.filter((c) => per(c, y) !== null).map((c) => ({ id: c.id, name: c.name, per: per(c, y) as number }));
          return { y, main: per(main, y), e: ends(held) };
        });
        const l12 = ends(cs);
        return (
          <ToolSection key={g} title={`${gridName(g)}: what a flat load paid, by year`} id={`years-${g}`}
            note={<>A flat load at the calculator&apos;s defaults, each complete calendar year in the market its last twelve months are bought in ({cs.some((c) => c.buy === "da") ? "real time where held, else day-ahead" : BUYS[main.buy].toLowerCase()}). The cheapest and the dearest load zone of each year are the year&apos;s own.</>}>
            <ChartFrame title={`${gridName(g)}, USD per MWh`} note={<>The last group is the calculator&apos;s last twelve months, {shortMonth(main.from)} to {shortMonth(main.to)}.</>}>
              <GroupedBars id={`dc-years-${g}`} unit="USD per MWh" label={`${gridName(g)}: a flat load's price by year at the cheapest load zone, ${main.name} and the dearest load zone, USD per MWh`}
                series={[{ name: "Cheapest load zone", tone: "muted" }, { name: `${main.name} (the calculator's default)`, tone: "accent" }, { name: "Dearest load zone", tone: "ink" }]}
                fmt={(v) => two(v)}
                groups={[...yearRows.map((r) => ({ label: r.y, values: [r.e ? r.e[0].per : null, r.main, r.e ? r.e[1].per : null] })),
                  { label: "Last 12 months", sub: `${shortMonth(main.from)} to ${shortMonth(main.to)}`, values: [l12 ? l12[0].per : null, main.per, l12 ? l12[1].per : null] }]} />
            </ChartFrame>
            <Fold title="The chart's figures">
              <ToolTable caption={`${gridName(g)}: the chart's figures, USD per MWh`} minWidth={620} head={["Year", "Cheapest load zone", `${main.name}`, "Dearest load zone"]}
                rows={[...yearRows.map((r) => ({
                  key: r.y,
                  cells: [
                    r.y,
                    r.e ? <span key="lo">{r.e[0].name}: <Num check={`dcpow|${g}|${r.e[0].id}|year|${r.y}`} raw={r.e[0].per}>{two(r.e[0].per)}</Num></span> : "not held",
                    r.main === null ? "not held" : <Num key="m" check={`dcpow|${g}|${main.id}|year|${r.y}`} raw={r.main}>{two(r.main)}</Num>,
                    r.e ? <span key="hi">{r.e[1].name}: <Num check={`dcpow|${g}|${r.e[1].id}|year|${r.y}`} raw={r.e[1].per}>{two(r.e[1].per)}</Num></span> : "not held",
                  ],
                })), {
                  key: "l12",
                  cells: [
                    `Last 12 months (${shortMonth(main.from)} to ${shortMonth(main.to)})`,
                    l12 ? <span key="lo">{l12[0].name}: <Num check={`dcpow|${g}|${l12[0].id}|per`} raw={l12[0].per}>{two(l12[0].per)}</Num></span> : "not held",
                    <Num key="m" check={`dcpow|${g}|${main.id}|per`} raw={main.per}>{two(main.per)}</Num>,
                    l12 ? <span key="hi">{l12[1].name}: <Num check={`dcpow|${g}|${l12[1].id}|per`} raw={l12[1].per}>{two(l12[1].per)}</Num></span> : "not held",
                  ],
                }]} />
            </Fold>
          </ToolSection>
        );
      })}
    </section>
  );
}
