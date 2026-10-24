import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { shown } from "@/lib/format";
import { SourceLine } from "@/components/tool/ToolPage";
import snapJson from "@/data/grid_network.json";
import indexJson from "@/public/network/daily_index.json";
import { TABLE as SUPPLY_TABLE, supplyOf, type Supply } from "@/lib/basupply";
import { fetchHourly, pickSnapshot } from "@/lib/network";
import { freshSnapshot } from "@/lib/gridReads";  // session 1180
import { clampDay, completeHour, type DailyIndex } from "@/lib/networkV3";
import type { Shape } from "@/lib/networkMap";
import { HOURLY, attempt } from "@/lib/supabase";
import { Network, type Snapshot } from "@/app/network/Network";
import { ISO_BA, liveExtras, supplyRows } from "@/app/network/data";
import { GravityFigures, NetworkFigures } from "@/components/grid/NetworkFigures";
import type { GridChoice } from "@/lib/gridtool";
import { shownHour } from "@/lib/gridKeys";
import { readReplayYear } from "@/lib/gridReplayFile";
import type { ReplayAsk } from "@/components/grid/ReplayDay";
import { Preliminary } from "@/components/grid/Preliminary";

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
// Session 237: this file was app/network/page.tsx. /network redirects to the Network view of the Grid tool (/grid,
// next.config.ts), which draws this page whole: the component (app/network/Network.tsx), its two lines of freshness and
// its source line. The component keeps its view in the address under the tool's own words (lib/gridtool.ts: net, node).

const committed = snapJson as unknown as Snapshot;
const index = indexJson as unknown as DailyIndex;
const ET = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
const utc = (t: string) => `${t.slice(0, 16).replace("T", " ")} UTC`;
const both = (t: string) => `${utc(t)} (${ET.format(new Date(t))} Eastern)`;

// Session 1151 (chain 077): under the component, the figures it draws for the grid in view in the hour it opens on,
// drawn on the server with their check keys and a one-line source each (components/grid/NetworkFigures.tsx): the
// grid's ties, net and demand on the Network tab (the seven grids' net exchange for the Lower 48), what the gravity
// shape draws on the Gravity tab.
// Session 1170 (chain 078): when the address names a replayed day (net=day&t=<day>, `day`), the panels add that day's
// figures from the replay's committed daily file, held to the replay's first and last day as the component holds it.
export async function NetworkView({ keep, node, shape, grid, day }: { /** the page's own query, kept in the address: "?grid=ercot&view=network" */ keep: string; /** the balancing authority whose panel opens when the address names none */ node: string | null;
  /** session 299: the shape the page's tab is (the Gravity tab passes "gravity"); the address's, else the network, when absent */ shape?: Shape;
  /** session 1151: the grid in view, whose figures are drawn under the component; none given, none drawn */ grid?: GridChoice;
  /** session 1170: the replayed day the address names (net=day&t=<day>), else none */ day?: string | null }) {
  // session 1180: on the Gravity tab the Exchange blocks under the component read the snapshot fresh (session 237); the
  // render reads it once, fresh (lib/gridReads.ts freshSnapshot), and both draw that object. Every other tab: as before
  const { snap, from } = shape === "gravity" ? pickSnapshot(await freshSnapshot(), committed) : pickSnapshot(await fetchHourly(HOURLY), committed);
  const isos = Object.entries(ISO_BA);
  const [reads, extras] = await Promise.all([Promise.all(isos.map(([, ba]) => attempt(() => supplyRows(ba)))), liveExtras(snap)]);
  const bad = reads.find((r) => !r.ok);
  const supply: Record<string, Supply> = {};
  if (!bad) for (const [, ba] of isos) { const s = supplyOf(reads.flatMap((r) => (r.ok ? r.data : [])), ba); if (s) supply[ba] = s; }
  const complete = completeHour(snap.hours, snap.links);
  const shownDay = day ? clampDay(day, index) : null;
  const replay: ReplayAsk | null = day && shownDay ? { day: shownDay, asked: day, first: index.first, last: index.last, read: readReplayYear(shownDay) } : null;
  // carried over from the page that stood here until session 168: the newest hour of all, and of the seven ISOs' demand
  const newest = snap.hours[snap.hours.length - 1];
  const demandTs = snap.nodes.filter((n) => n.iso && n.demand_ts).map((n) => n.demand_ts as string).reduce((a, b) => (b > a ? b : a), "");
  const hourName = (t: string) => `${t.slice(0, 13).replace("T", " ")}:00 UTC`;
  // session 1171: the clock the page was drawn by, said in the lag line and in the source line's sentence on revisions
  const drawnAt = new Date();
  return (
    <div data-grid-network="1">
      <p className="mb-4 max-w-3xl text-base leading-relaxed">The {snap.nodes.length} balancing authorities that report to EIA-930 and the power they exchange. Watch a story, replay any day since {index.first.slice(0, 4)}, or
          click a grid to see who supplies it and trace the power two steps back. The address holds what you are looking at: copy it to share the view.</p>
      <Network snap={snap} supply={supply} live={extras} v3={{ index, complete }} page={{ keep, node, shape }} />
      {/* session 266: the two-day lag, under the chart, computed from the snapshot (net|lag in lib/network.ts) */}
      {(() => { const shownHour = complete.hour ?? newest; const lag = Math.round((Date.parse(snap.built) - Date.parse(shownHour)) / 3_600_000);
        // session 299 (the owner's ruling 3c of 18 October 2026): both ages: against the snapshot's refresh (checkable, the key) and against the clock when this page was drawn (not a key: the clock is not a table)
        const drawn = drawnAt; const clockLag = Math.round((drawn.getTime() - Date.parse(shownHour)) / 3_600_000); return (
        <p className="mt-3 max-w-3xl text-sm" data-network-lag={lag} data-network-clock-lag={clockLag}>The newest hour shown, {hourName(shownHour)}, began <Num check={`net|lag|${shownHour}|${snap.built}`} raw={lag}>{shown(lag)}</Num> hours before
          this week&apos;s latest hourly refresh ({utc(snap.built)}), and {shown(clockLag)} hours before this page was drawn ({utc(drawn.toISOString())}): EIA-930 publishes a balancing authority&apos;s interchange for a local day on the second morning after it, so the network runs about two days behind the clock.</p>
      ); })()}
      {grid ? (shape === "gravity"
        ? <GravityFigures snap={snap} hour={shownHour(snap, complete)} grid={grid} live={extras} replay={replay} />
        : <NetworkFigures snap={snap} hour={shownHour(snap, complete)} grid={grid} live={extras} replay={replay} node={node} />) : null}
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
      {/* session 1424: the reason can hold the database's answer, a long run without a space: it breaks at 390 px */}
      {bad && !bad.ok ? <p className="mt-2 text-sm text-muted break-words" role="status" data-reason-wraps="1">The last twelve months could not be read, so the panel shows none: {bad.reason}</p> : null}
      <SourceLine tables={["eia930_all_interchange", "eia930_daily_interchange", "eia930_daily_demand", "eia930_all_demand", "carbon_intensity_hourly", "carbon_intensity_daily", SUPPLY_TABLE,
        "eia930_event_hourly_interchange", "eia930_all_storage", "caiso_battery_storage"]}
        note={<>Public domain (EIA) and CAISO; hub prices as each ISO publishes them. <Preliminary drawn={drawnAt} say /> <Link href="/data/methods/grid_network">Method</Link>.</>} />
    </div>
  );
}
