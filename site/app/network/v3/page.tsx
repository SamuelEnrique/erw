import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { Fold, SourceLine, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import snapJson from "@/data/grid_network.json";
import indexJson from "@/public/network/daily_index.json";
import { TABLE as SUPPLY_TABLE, supplyOf, type Supply } from "@/lib/basupply";
import { fetchHourly, pickSnapshot } from "@/lib/network";
import type { DailyIndex } from "@/lib/networkV3";
import { HOURLY, attempt } from "@/lib/supabase";
import { Network, type Snapshot } from "../Network";
import { ISO_BA, liveExtras, supplyRows } from "../data";

// Session 93: the network, version 3, in review (lib/release.ts). The same network, with the same look, read the same
// way as /network (app/network/data.ts), and four additions drawn by the same component behind its `v3` prop:
// a replay of any day since 2019 with a date picker and "Play the year"; an address that holds the grid, the moment and
// the switches; a Prices switch; and "Trace the power". The live page /network passes no `v3` and is as it was. To make
// version 3 the live page: pass `v3={{ index }}` on /network and remove this page (session 93's report).
export const metadata: Metadata = { title: "The grid network, version 3", robots: { index: false, follow: false } };
export const revalidate = 3600;

const committed = snapJson as unknown as Snapshot;
const index = indexJson as unknown as DailyIndex;
const utc = (t: string) => `${t.slice(0, 16).replace("T", " ")} UTC`;

export default async function NetworkV3Page() {
  const { snap, from } = pickSnapshot(await fetchHourly(HOURLY), committed);
  const isos = Object.entries(ISO_BA);
  const [reads, extras] = await Promise.all([Promise.all(isos.map(([, ba]) => attempt(() => supplyRows(ba)))), liveExtras(snap)]);
  const bad = reads.find((r) => !r.ok);
  const supply: Record<string, Supply> = {};
  if (!bad) for (const [, ba] of isos) { const s = supplyOf(reads.flatMap((r) => (r.ok ? r.data : [])), ba); if (s) supply[ba] = s; }
  const years = Object.keys(index.years);
  const priced = [...new Set(Object.values(index.years).flatMap((y) => y.priced))].sort();
  const screened = Object.values(index.years).reduce((a, y) => a + y.pair_days_screened, 0);
  return (
    <ToolPage>
      <ToolHeader title="The grid network"
        lead={<>The {snap.nodes.length} balancing authorities that report to EIA-930 and the power they exchange. Watch a story, replay any day since {index.first.slice(0, 4)}, or
          click a grid to see who supplies it and trace the power two steps back. The address holds what you are looking at: copy it to share the view.</>} />
      <Network snap={snap} supply={supply} live={extras} v3={{ index }} />
      <p className="mt-3 max-w-3xl text-xs text-muted" data-network-source={from}>
        The live week: refreshed {utc(snap.built)}. The replay: {index.first} to {index.last}, built {utc(index.built)}.
      </p>
      {bad && !bad.ok ? <p className="mt-2 text-sm text-muted" role="status">The last twelve months could not be read, so the panel shows none: {bad.reason}</p> : null}
      <div className="mt-8 border-t border-rule">
        <Fold title="The replay: what a day is">
          <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
            <li><strong>A day is EIA&apos;s Eastern day</strong>, from its daily interchange of every pair of balancing authorities, {years[0]} to {index.last}. A flow is the day&apos;s MWh over the day&apos;s hours: its average MW, so a day draws on the scale an hour draws on.</li>
            <li><strong>Each pair is counted once</strong>, by the network&apos;s own rule: read from the balancing authority whose code sorts first, as it reported it; on a day it did not report, from the other&apos;s report with the sign flipped. A day neither reported is left blank.</li>
            <li><strong>{screened.toLocaleString("en-US")} pair-days are left out as days no tie can carry</strong>: further than 10 median absolute deviations, and at least 500 MWh, from the pair&apos;s own median. It is the rule of the monthly supply table; one such day would set the scale of a whole year.</li>
            <li><strong>A share of demand, by day:</strong> each supplier&apos;s flow over the grid&apos;s demand that day, both as the day&apos;s average MW. Demand is EIA&apos;s daily figure, its own sum of the hours it holds; a day whose demand is not above zero, or outside half to twice the median of the six days around it, is not used and shows no share.</li>
            <li><strong>Not held by day:</strong> the batteries.</li>
            <li><strong>Not drawn:</strong> {index.left_out_bas.join(", ")}, which reported in those years and have no place in today&apos;s network.</li>
          </ul>
        </Fold>
        <Fold title="Prices, and what the ring does not say">
          <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
            <li><strong>The outer ring&apos;s weight follows the real-time price at the grid&apos;s main hub.</strong> It is drawn only where a public price is held for the moment shown: in the replay, for {priced.join(", ")}, and for most of them only from September 2024; ERCOT from {years[0]}.</li>
            <li><strong>PJM has no ring:</strong> its prices are licensed and not shown.</li>
            <li><strong>A hub is not a site:</strong> the price at one hub is not what power cost at every point of the grid.</li>
            <li><strong>The weight is relative to the highest price of the period shown</strong>, by its square root, so that one scarcity hour does not turn every other ring into a hair. The panel gives the number.</li>
          </ul>
        </Fold>
        <Fold title="Trace the power: what it is, and what it is not">
          <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
            <li><strong>Two steps.</strong> For the grid selected, over the period shown: the neighbours that supplied it on net, largest first, with each one&apos;s share of that inflow; and for each of those, the neighbours that supplied it over the same period.</li>
            <li><strong>Physical flows, not contracts.</strong> Who buys power from whom can differ from the path it takes.</li>
            <li><strong>Not where the power was generated.</strong> A supplier generates most of what it sends; its own inflows are listed beside it, and nothing says their power is the power passed on.</li>
            <li><strong>Net, over the period.</strong> A tie that carried power both ways counts by its balance; a neighbour that took power on net is not a supplier.</li>
          </ul>
        </Fold>
        <p className="mt-3 max-w-3xl text-sm">The three measures of each grid&apos;s imports, what the network is and is not, and how fresh each layer is: on <Link href="/network">the network page</Link>.</p>
      </div>
      <SourceLine tables={["eia930_all_interchange", "eia930_daily_interchange", "eia930_daily_demand", "eia930_all_demand", "carbon_intensity_hourly", "carbon_intensity_daily", SUPPLY_TABLE,
        "eia930_event_hourly_interchange", "eia930_all_storage", "caiso_battery_storage"]}
        note={<>Public domain (EIA) and CAISO; hub prices as each ISO publishes them. <Link href="/data/methods/grid_network">Method</Link>.</>} />
    </ToolPage>
  );
}
