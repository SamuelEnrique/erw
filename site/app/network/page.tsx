import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { SourceLine, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import snapJson from "@/data/grid_network.json";
import indexJson from "@/public/network/daily_index.json";
import { TABLE as SUPPLY_TABLE, supplyOf, type Supply } from "@/lib/basupply";
import { fetchHourly, pickSnapshot } from "@/lib/network";
import { completeHour, type DailyIndex } from "@/lib/networkV3";
import { HOURLY, attempt } from "@/lib/supabase";
import { Network, type Snapshot } from "./Network";
import { ISO_BA, liveExtras, supplyRows } from "./data";

// Session 168 (the owner's instruction of 8 October 2026): version 3 is the network page. This file is version 3's page
// (app/network/v3/page.tsx, sessions 93, 109 and 124), moved to the tool's own address; /network/v3 redirects here
// (next.config.ts) and the page that stood here is kept, unrouted, in app/_retired/network-original. Carried over from
// that page: the "Newest hour ... Demand of the seven ISOs" line. Moved off the page face into the Method note
// (docs/methods/grid_network.md, "What stood on the page face until session 168"): the old page's three measures of
// net imports, "What this is, and what it is not", "How fresh each layer is" and the note on California's data break;
// version 3's "The replay: what a day is", "Prices, and what the ring does not say", "Trace the power: what it is, and
// what it is not" and its line pointing back to the old page. The page keeps one source line at the bottom.
// Session 93: the same network, with the same look and the same reads (app/network/data.ts), and four additions drawn
// by the component behind its `v3` prop: a replay of any day since 2019 with a date picker and "Play the year"; an
// address that holds the grid, the moment and the switches; a Prices switch; and "Trace the power".
// Session 124: the live week opens on the newest hour that every reporting pair holds, and the page says which hour and
// which pairs have stopped reporting (lib/networkV3.ts completeHour); the replay says when a day holds few pairs or none;
// the trace covers a day, its month or the year, says how many of its days hold a flow, and traces nothing through
// Mexico; MISO's hub price is not shown: its panel reads "paused while terms are reviewed".
export const metadata: Metadata = { title: "The grid network" };
export const revalidate = 3600;

const committed = snapJson as unknown as Snapshot;
const index = indexJson as unknown as DailyIndex;
const ET = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
const utc = (t: string) => `${t.slice(0, 16).replace("T", " ")} UTC`;
const both = (t: string) => `${utc(t)} (${ET.format(new Date(t))} Eastern)`;

export default async function NetworkPage() {
  const { snap, from } = pickSnapshot(await fetchHourly(HOURLY), committed);
  const isos = Object.entries(ISO_BA);
  const [reads, extras] = await Promise.all([Promise.all(isos.map(([, ba]) => attempt(() => supplyRows(ba)))), liveExtras(snap)]);
  const bad = reads.find((r) => !r.ok);
  const supply: Record<string, Supply> = {};
  if (!bad) for (const [, ba] of isos) { const s = supplyOf(reads.flatMap((r) => (r.ok ? r.data : [])), ba); if (s) supply[ba] = s; }
  const complete = completeHour(snap.hours, snap.links);
  // carried over from the page that stood here until session 168: the newest hour of all, and of the seven ISOs' demand
  const newest = snap.hours[snap.hours.length - 1];
  const demandTs = snap.nodes.filter((n) => n.iso && n.demand_ts).map((n) => n.demand_ts as string).reduce((a, b) => (b > a ? b : a), "");
  const hourName = (t: string) => `${t.slice(0, 13).replace("T", " ")}:00 UTC`;
  return (
    <ToolPage>
      <ToolHeader title="The grid network"
        lead={<>The {snap.nodes.length} balancing authorities that report to EIA-930 and the power they exchange. Watch a story, replay any day since {index.first.slice(0, 4)}, or
          click a grid to see who supplies it and trace the power two steps back. The address holds what you are looking at: copy it to share the view.</>} />
      <Network snap={snap} supply={supply} live={extras} v3={{ index, complete }} />
      <p className="mt-3 max-w-3xl text-xs text-muted" data-network-source={from}>
        The live week: refreshed {utc(snap.built)}. <span data-newest-complete={complete.hour ?? "none"}>{complete.hour
          ? <>Newest hour complete for every reporting pair: {hourName(complete.hour)} ({complete.reporting} of the week&apos;s {complete.pairs} pairs report; the newest hour of all, {hourName(complete.newest)}, holds {complete.newestPairs} of them).</>
          : <>No hour of the week holds every reporting pair.</>}</span>
        {complete.silent.length ? <> <span data-silent-pairs={complete.silent.length}>Not reporting for two days or more, and not waited for: {complete.silent.map((x) => `${x.a} with ${x.b}${x.last ? `, last ${hourName(x.last)}` : ", nothing this week"}`).join("; ")}.</span></> : null}
        {" "}The replay: {index.first} to {index.last}, built {utc(index.built)}{index.last_complete && index.last_complete !== index.last ? <>; its newest day that holds nine tenths of the usual pairs is {index.last_complete}</> : null}.
      </p>
      <p className="mt-1 max-w-3xl text-xs text-muted" data-newest-hour={newest}>
        Newest hour: {both(newest)}, refreshed {utc(snap.built)}{from === "storage" ? " (the hourly refresh)" : " (the daily snapshot: the hourly copy was not reachable)"}.
        {demandTs ? <> Demand of the seven ISOs: newest hour {both(demandTs)}.</> : null}
      </p>
      {bad && !bad.ok ? <p className="mt-2 text-sm text-muted" role="status">The last twelve months could not be read, so the panel shows none: {bad.reason}</p> : null}
      <SourceLine tables={["eia930_all_interchange", "eia930_daily_interchange", "eia930_daily_demand", "eia930_all_demand", "carbon_intensity_hourly", "carbon_intensity_daily", SUPPLY_TABLE,
        "eia930_event_hourly_interchange", "eia930_all_storage", "caiso_battery_storage"]}
        note={<>Public domain (EIA) and CAISO; hub prices as each ISO publishes them. <Link href="/data/methods/grid_network">Method</Link>.</>} />
    </ToolPage>
  );
}
