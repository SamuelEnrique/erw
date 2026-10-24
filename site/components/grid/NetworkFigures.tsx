// Energy Research Warehouse (ERW) site, session 1151 (chain 077): the figures the network component draws in the
// browser, drawn again on the server beside it, so a reader can trace each one and scripts/check-values.mjs can check
// it. The Network tab: the grid in view, in the hour the component opens on (its ties, their flow and direction, the
// net, the number of ties, the demand where held); for the Lower 48, the seven grids' net exchange. The Gravity tab:
// what the gravity shape draws (each grid's net generation, net import and the import as a share). Every figure is a
// lib/gridKeys.ts figure: a check key check-values already recomputes, and a one-line source in its hover tip.
// Session 1165 (chain 078): under the ties, the grid's balance (Balance below): the Grid pack's item 3, said where the
// figures are.
// Session 1170 (chain 078): when the address names a replayed day (net=day&t=<day>), the day's figures from the replay's
// committed daily file (components/grid/ReplayDay.tsx): on the Network tab the balancing authority in the address (node,
// any of the network's, BPAT as well as the seven), first in the panel; on the Gravity tab one line under the table, the
// grid in view's demand that day. Without a day in the address both panels draw as before.
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { NoData } from "@/components/NoData";
import { ToolSection, ToolTable } from "@/components/tool/ToolPage";
import type { LiveExtras, Snapshot } from "@/app/network/Network";
import { shown } from "@/lib/format";
import { GRID_CHOICES, type GridChoice } from "@/lib/gridtool";
import { balancePanel, gravityPanel, lower48Panel, networkPanel, type BalancePanel, type Fig } from "@/lib/gridKeys";
import { GRAVITY_CENTER, GRAVITY_GRIDS } from "@/lib/networkGravity";
import { ReplayDayDemand, ReplayDayFigures, type ReplayAsk } from "@/components/grid/ReplayDay";
import { Missing } from "@/components/mix/Now";
import { PanelFile, type FileOf } from "@/components/grid/PanelFile";  // session 1182: each panel's table, to download
import { gridHref } from "@/lib/gridtool";
import { GRID_ANCHOR, METHOD_BALANCE, METHOD_GRAVITY, METHOD_NETWORK } from "@/lib/gridAnchors";  // session 1183: each panel's anchor; session 1184: its method
import { PanelMethod } from "@/components/grid/PanelMethod";  // session 1184: the line that links the panel's method
import { BA_GRID } from "@/lib/gridHeld";
import { replayDay } from "@/lib/gridReplay";

const hourName = (t: string) => `${t.slice(0, 10)} ${t.slice(11, 13)}:00 UTC`;

/** A figure with its key and its one-line source as the hover tip. */
function F({ f }: { f: Fig }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>
    </span>
  );
}

const ISO_GRIDS = GRID_CHOICES.filter((g) => g.slug !== "us48");

/** Session 1182: what the file of a panel of the network snapshot says it is drawn from. */
const snapTable = (snap: Snapshot) => `eia930_all_interchange (EIA-930, public domain), as the network snapshot holds it (refreshed hourly; this snapshot built ${snap.built})`;
const hourLine = (hour: string) => `Hour: ${hourName(hour)} (hour start), the hour the network opens on: the newest that every reporting pair of the snapshot's week holds`;

// Session 1181 (chain 091): a read of the live week that failed (app/network/data.ts liveExtras keeps its reason) is said
// in the tool's one look for what is not there (Missing), as "could not be read", with the table and the reason on
// hover: never "not held", which would say the warehouse holds no such figure. Nothing of the failed read is drawn.
type Failed = LiveExtras["failed"];
const DEMAND_TABLE = "eia930_all_demand", GENERATION_TABLE = "eia930_all_generation";
function Unread({ table, reason }: { table: string; reason: string }) {
  return <Missing words="could not be read" why={`${table} could not be read just now: ${reason}`} />;
}

export function NetworkFigures({ snap, hour, grid, live, replay, node }: { snap: Snapshot; hour: string; grid: GridChoice; live: LiveExtras;
  /** session 1170: the replayed day the address names, and the balancing authority whose panel it opens */ replay?: ReplayAsk | null; node?: string | null }) {
  const nameOf = (id: string) => snap.nodes.find((n) => n.id === id)?.name ?? id;
  const panel = `grid_network_${grid.slug}`;
  const day = replay && node ? <ReplayDayFigures ask={replay} ba={node} name={nameOf(node)} /> : null;
  if (grid.slug === "us48") {
    const rows = lower48Panel(snap, ISO_GRIDS.map((g) => g.ba), hour);
    // session 1182: the table's rows, drawn and offered as a file from the same cells
    const head48 = ["Grid", "Net export, MW", "Ties reporting"];
    const rows48 = rows.map((r) => ({ key: r.ba, cells: [
      ISO_GRIDS.find((g) => g.ba === r.ba)!.label,
      r.net ? <F key="n" f={r.net} /> : <span key="n" className="text-muted">no tie reported</span>,
      <F key="c" f={r.count} />,
    ] }));
    const file48: FileOf = { panel, title: "the seven grids' net exchange in the hour the network shows", page: gridHref(grid.slug, "network"),
      tables: [snapTable(snap)], filter: "each of the seven ISO grids' reporting ties in the hour, summed and signed from the grid's side (negative: a net import)", window: hourLine(hour) };
    return (
      <div data-grid-panel={panel} id={GRID_ANCHOR.network} className="mt-10">
        {day}
        <ToolSection title={`The seven grids, the hour shown (${hourName(hour)})`}
          note="Net export, MW: the sum of a grid's reporting ties in the hour the network opens on, signed from its side; a negative number is a net import. Hover a figure for its table, filter, hour and the snapshot's refresh.">
          <ToolTable caption="Net exchange of the seven grids in the hour the network shows" minWidth={380} head={head48}
            rows={rows48} />
          <PanelFile of={file48} columns={head48} rows={rows48.map((r) => r.cells)} />
          <PanelMethod at="network"><Link href={METHOD_NETWORK}>Method: the Grid tool&apos;s panels, every figure keyed</Link></PanelMethod>
        </ToolSection>
      </div>
    );
  }
  const p = networkPanel(snap, grid.ba, hour, live.demand[grid.ba]);
  // session 1182: the ties' rows, drawn and offered as a file from the same cells; the sentence's figures in its header
  const tieHead = ["Neighbour", "Flow, MW", "Direction"];
  const tieRows = p.ties.map((t) => ({ key: t.other, cells: [
    <>{nameOf(t.other)} <span className="font-mono text-xs text-muted">{t.other}</span></>,
    <F key="v" f={t} />,
    t.dir,
  ] }));
  const tieFile: FileOf = { panel, title: `${grid.label}'s ties in the hour the network shows`, page: gridHref(grid.slug, "network"),
    tables: [snapTable(snap), "eia930_all_demand (EIA-930, the grid's demand in the hour: the week's rows, else the snapshot's)"],
    filter: `the ties of ${grid.ba} (${grid.label}) with a flow in the hour, signed from ${grid.label}'s side (positive: power left the grid)`, window: hourLine(hour),
    figures: p.net ? [
      { label: `net ${p.net.kind} over the reporting ties, MW`, value: p.net },
      { label: "ties reporting", value: p.count },
      { label: "demand in the hour, MW", value: p.demand ?? (live.failed?.demand ? "could not be read" : "not held") },
    ] : [] };
  return (
    <div data-grid-panel={panel} id={GRID_ANCHOR.network} className="mt-10">
      {day}
      <ToolSection title={`${grid.label}, the hour shown (${hourName(hour)})`}
        note={`The figures the network draws for ${grid.label} in the hour it opens on, from the same snapshot. A tie's flow is signed from ${grid.label}'s side: positive, power left the grid. Hover a figure for its table, filter, hour and the snapshot's refresh.`}>
        {p.ties.length ? (
          <>
            <p className="mb-3 max-w-3xl text-sm">
              {grid.label} {p.net!.kind === "export" ? "sent out, on net," : "took in, on net,"} <F f={p.net!} /> MW over its <F f={p.count} /> reporting ties
              {p.demand ? <>, with a demand of <F f={p.demand} /> MW in the hour</> : live.failed?.demand ? <>; its demand in the hour <Unread table={DEMAND_TABLE} reason={live.failed.demand} /></> : <>; its demand in the hour is not held</>}.
            </p>
            <ToolTable caption={`${grid.label}'s ties in the hour the network shows`} minWidth={420} head={tieHead}
              rows={tieRows} />
            <PanelFile of={tieFile} columns={tieHead} rows={tieRows.map((r) => r.cells)} />
          </>
        ) : <NoData what={`${grid.label}'s ties`} reason={`the snapshot holds no flow for ${grid.ba} in the hour starting ${hourName(hour)}`} />}
        <PanelMethod at="network"><Link href={METHOD_NETWORK}>Method: the Grid tool&apos;s panels, every figure keyed</Link></PanelMethod>
      </ToolSection>
      {/* session 1181: a read of the live week that failed is said in the balance (its parts, the gap and the week), never "not held" */}
      {live.failed?.generation || live.failed?.demand
        ? <Balance b={balancePanel(snap, grid.ba, hour, live.generation?.[grid.ba], live.demand[grid.ba], p.demand)} label={grid.label} failed={live.failed} />
        : <Balance b={balancePanel(snap, grid.ba, hour, live.generation?.[grid.ba], live.demand[grid.ba], p.demand)} label={grid.label} />}
    </div>
  );
}

/** Session 1165: whether the grid's balance closes, in the hour shown and over the week. Net generation less demand
 * less the net export over the ties: zero where EIA-930's figures close. CAISO's net generation is EIA-930's total, the
 * figure the gravity shape draws (the section "The gravity shape" of the method note, ruling 1a); the session 118
 * ruling withholds California's hourly mix by fuel, not this total. */
function Balance({ b, label, failed }: { b: BalancePanel; label: string; /** session 1181: the live week's reads that failed */ failed?: Failed }) {
  const hourName = (t: string) => `${t.slice(0, 10)} ${t.slice(11, 13)}:00 UTC`;
  const not = <span className="text-muted">not held</span>;
  // session 1181: a part whose read failed says so; the gap and the week are then not computed, and say why
  const genGone = !b.gen && failed?.generation ? <Unread table={GENERATION_TABLE} reason={failed.generation} /> : null;
  const demGone = !b.demand && failed?.demand ? <Unread table={DEMAND_TABLE} reason={failed.demand} /> : null;
  const weekGone = failed?.generation ? <Unread table={GENERATION_TABLE} reason={failed.generation} /> : failed?.demand ? <Unread table={DEMAND_TABLE} reason={failed.demand} /> : null;
  // session 1182: the table's rows, drawn and offered as a file from the same cells; the week's two figures in its header
  const balHead = ["In the hour shown", "MW", "Source"];
  const balRows = [
            { key: "gen", cells: ["Net generation", b.gen ? <F key="v" f={b.gen} /> : genGone ?? not, "eia930_all_generation"] },
            { key: "dem", cells: ["Demand", b.demand ? <F key="v" f={b.demand} /> : demGone ?? not, "eia930_all_demand"] },
            { key: "net", cells: ["Net export over the ties (negative: a net import)", b.net ? <F key="v" f={b.net} /> : <span key="v" className="text-muted">no tie reported</span>, "the network snapshot"] },
            { key: "gap", highlight: true, cells: ["The gap: net generation less demand less net export", b.gap ? <F key="v" f={b.gap} /> : genGone || demGone ? <span key="v" className="text-muted">not computed: a part could not be read</span> : <span key="v" className="text-muted">not computed: a part is not held</span>, "the three above"] },
          ];
  const weekWords = weekGone ? "not computed: its hours could not be read" : "not computed: no hour of the week holds all three";
  const balFile: FileOf = { panel: `grid_network_${BA_GRID[b.ba] ?? b.ba}`, part: "balance", title: `whether ${label}'s balance closes, the hour shown and the week`,
    page: gridHref(BA_GRID[b.ba] ?? b.ba, "network"),
    tables: ["eia930_all_generation (EIA-930, net_generation_mw)", "eia930_all_demand (EIA-930, demand_mw; the hour's figure is the network panel's, the week's rows, else the snapshot's)", "eia930_all_interchange (EIA-930, the network snapshot's ties)"],
    filter: `${b.ba} (${label}): net generation, demand, and the net export over its reporting ties; the gap is net generation less demand less net export`,
    window: `Hour: ${hourName(b.hour)} (hour start), the hour the network opens on; the week: ${hourName(b.from)} to ${hourName(b.to)}, the hours that hold every one of ${label}'s ties, its net generation and its demand`,
    figures: [
      { label: "hours of the week that hold all three", value: b.absmean && b.hours ? b.hours : weekWords },
      { label: "the gap's mean size over those hours, MW", value: b.absmean && b.hours ? b.absmean : weekWords },
    ] };
  return (
    <div data-grid-balance={b.ba} id={GRID_ANCHOR.balance}>
      <ToolSection title={`Does ${label}'s balance close? The hour shown, and the week`}
        note={<>A grid&apos;s net generation less its demand less its net export over its ties is zero when EIA-930&apos;s figures close. For {label}, session 360 found the gap {b.where} (<Link href="/data/methods/eia930_balance">the method note on EIA-930&apos;s balance</Link>; EIA&apos;s adjusted series do not close it). The week&apos;s figure is the mean size of the gap, its absolute value, over the hours from {hourName(b.from)} to {hourName(b.to)} that hold every one of {label}&apos;s ties, its net generation and its demand.
          {b.ba === "CISO" ? <> {label}&apos;s net generation here is EIA-930&apos;s total, the figure the gravity shape draws; since December 2025 it reads below CAISO&apos;s own, and California&apos;s hourly mix by fuel stays withheld.</> : null} Hover a figure for its table, filter and hour, and for where session 360 found each grid&apos;s gap.</>}>
        <ToolTable caption={`${label}'s balance in the hour the network shows`} minWidth={420} head={balHead}
          rows={balRows} />
        <PanelFile of={balFile} columns={balHead} rows={balRows.map((r) => r.cells)} />
        <p className="mt-3 max-w-3xl text-sm">
          {b.absmean && b.hours
            ? <>Over the <F f={b.hours} /> hours of the week that hold all three, the gap&apos;s mean size is <F f={b.absmean} /> MW.</>
            : weekGone ? <>The week&apos;s gap is not computed: its hours <span data-balance-unread="1">{weekGone}</span>.</>
            : <>No hour of the week holds all three, so the week&apos;s gap is not computed.</>}
        </p>
        <PanelMethod at="balance"><Link href={METHOD_BALANCE}>Method: the balance, said where the figures are</Link></PanelMethod>
      </ToolSection>
    </div>
  );
}

export function GravityFigures({ snap, hour, grid, live, replay }: { snap: Snapshot; hour: string; grid: GridChoice; live: LiveExtras;
  /** session 1170: the replayed day the address names; its demand of the grid in view is one line under the table */ replay?: ReplayAsk | null }) {
  const g = gravityPanel(snap, GRAVITY_GRIDS.map((x) => x.id), GRAVITY_CENTER, hour, live.generation);
  // session 1181: net generation's read failed: each circle's generation, and so its share, could not be read
  const genGone = live.failed?.generation;
  // session 1182: the table's rows, drawn and offered as a file from the same cells; the scale and the replayed day's
  // demand (the line under the table, components/grid/ReplayDay.tsx, the same figure) in its header
  const gHead = ["Grid", "Net generation, MW", "Net import, MW", "Import, percent of generation"];
  const gRows = g.rows.map((r) => ({ key: r.ba, highlight: r.ba === grid.ba, cells: [
            GRAVITY_GRIDS.find((x) => x.id === r.ba)!.label,
            r.gen ? <F key="g" f={r.gen} /> : genGone ? <Unread key="g" table={GENERATION_TABLE} reason={genGone} /> : <span key="g" className="text-muted">not held</span>,
            r.net ? <F key="n" f={r.net} /> : <span key="n" className="text-muted">no tie reported</span>,
            r.share ? <F key="s" f={r.share} /> : !r.gen && genGone ? <span key="s" className="text-muted">not computed</span> : <span key="s" className="text-muted">none</span>,
          ] }));
  const rd = replay && grid.ba !== "US48" && replay.read.ok ? replayDay(replay.read.y, grid.ba, replay.day) : null;
  const gFile: FileOf = { panel: `grid_gravity_${grid.slug}`, title: "the seven grids in the gravity shape, the hour shown", page: gridHref(grid.slug, "gravity", replay ? { net: "day", t: replay.day } : {}),
    tables: [snapTable(snap), "eia930_all_generation (EIA-930, net_generation_mw: the live week's rows, else the snapshot's)"],
    filter: "each of the seven ISO grids: its net generation, its net import over its reporting ties (negative: a net export), the import as a percent of the generation; the Lower 48's generation is the scale",
    window: hourLine(hour),
    figures: [
      { label: "the Lower 48's net generation (the shape's scale), MW", value: g.center ?? (genGone ? "could not be read" : "not held") },
      ...(replay ? [{ label: `${grid.label}'s demand on ${replay.day}, the day picked in the replay (EIA's Eastern day, the day's average MW, from the replay's committed daily file)`,
        value: rd?.demand ?? (grid.ba === "US48" || replay.read.ok ? "not held" : "could not be read") }] : []),
    ] };
  return (
    <div data-grid-panel={`grid_gravity_${grid.slug}`} id={GRID_ANCHOR.gravity} className="mt-10">
      <ToolSection title={`What the gravity shape draws, the hour shown (${hourName(hour)})`}
        note={<>Each circle&apos;s area follows the grid&apos;s net generation; its pull toward the center, its net import over its reporting ties as a percent of that generation (a negative number: a net export, pushed out). The Lower 48&apos;s generation sets the scale{g.center ? <>: <F f={g.center} /> MW</> : genGone ? <>; it <Unread table={GENERATION_TABLE} reason={genGone} /></> : <>; it is not held for the hour</>}. Hover a figure for its table, filter, hour and the snapshot&apos;s refresh.
          {" "}{replay
            ? <span data-gravity-window="day">These are the figures of the hour the shape opens on, in the live week. The day picked in the replay, {replay.day}, stays in the address, but neither the shape nor this table draws it: net generation is held by hour for the live week only, not by day, so no figure in this table is that day&apos;s; the line under the table gives that day&apos;s demand.</span>
            : <span data-gravity-window="live">These are the figures of the hour the shape opens on, in the live week. A day picked in the replay stays in the address, but neither the shape nor this table draws it: net generation is held by hour for the live week only, not by day, so no figure here is that day&apos;s.</span>}
          {" "}<span data-gravity-public="1">Every figure here, for every grid, is EIA-930&apos;s public interchange and net generation; no grid operator&apos;s own table is read, so no grid is held here.</span></>}>
        <ToolTable caption="The seven grids in the gravity shape, the hour shown" minWidth={460} head={gHead}
          rows={gRows} />
        {replay ? <ReplayDayDemand ask={replay} ba={grid.ba} label={grid.label} /> : null}
        <PanelFile of={gFile} columns={gHead} rows={gRows.map((r) => r.cells)} />
        <PanelMethod at="gravity"><Link href={METHOD_GRAVITY}>Method: the Grid tool&apos;s panels, every figure keyed</Link></PanelMethod>
      </ToolSection>
    </div>
  );
}
