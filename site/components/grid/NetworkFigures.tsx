// Energy Research Warehouse (ERW) site, session 1151 (chain 077): the figures the network component draws in the
// browser, drawn again on the server beside it, so a reader can trace each one and scripts/check-values.mjs can check
// it. The Network tab: the grid in view, in the hour the component opens on (its ties, their flow and direction, the
// net, the number of ties, the demand where held); for the Lower 48, the seven grids' net exchange. The Gravity tab:
// what the gravity shape draws (each grid's net generation, net import and the import as a share). Every figure is a
// lib/gridKeys.ts figure: a check key check-values already recomputes, and a one-line source in its hover tip.
import { Num } from "@/components/Num";
import { NoData } from "@/components/NoData";
import { ToolSection, ToolTable } from "@/components/tool/ToolPage";
import type { LiveExtras, Snapshot } from "@/app/network/Network";
import { shown } from "@/lib/format";
import { GRID_CHOICES, type GridChoice } from "@/lib/gridtool";
import { gravityPanel, lower48Panel, networkPanel, type Fig } from "@/lib/gridKeys";
import { GRAVITY_CENTER, GRAVITY_GRIDS } from "@/lib/networkGravity";

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

export function NetworkFigures({ snap, hour, grid, live }: { snap: Snapshot; hour: string; grid: GridChoice; live: LiveExtras }) {
  const nameOf = (id: string) => snap.nodes.find((n) => n.id === id)?.name ?? id;
  const panel = `grid_network_${grid.slug}`;
  if (grid.slug === "us48") {
    const rows = lower48Panel(snap, ISO_GRIDS.map((g) => g.ba), hour);
    return (
      <div data-grid-panel={panel} className="mt-8">
        <ToolSection title={`The seven grids, the hour shown (${hourName(hour)})`}
          note="Net export, MW: the sum of a grid's reporting ties in the hour the network opens on, signed from its side; a negative number is a net import. Hover a figure for its table, filter, hour and the snapshot's refresh.">
          <ToolTable caption="Net exchange of the seven grids in the hour the network shows" minWidth={380} head={["Grid", "Net export, MW", "Ties reporting"]}
            rows={rows.map((r) => ({ key: r.ba, cells: [
              ISO_GRIDS.find((g) => g.ba === r.ba)!.label,
              r.net ? <F key="n" f={r.net} /> : <span key="n" className="text-muted">no tie reported</span>,
              <F key="c" f={r.count} />,
            ] }))} />
        </ToolSection>
      </div>
    );
  }
  const p = networkPanel(snap, grid.ba, hour, live.demand[grid.ba]);
  return (
    <div data-grid-panel={panel} className="mt-8">
      <ToolSection title={`${grid.label}, the hour shown (${hourName(hour)})`}
        note={`The figures the network draws for ${grid.label} in the hour it opens on, from the same snapshot. A tie's flow is signed from ${grid.label}'s side: positive, power left the grid. Hover a figure for its table, filter, hour and the snapshot's refresh.`}>
        {p.ties.length ? (
          <>
            <p className="mb-3 max-w-3xl text-sm">
              {grid.label} {p.net!.kind === "export" ? "sent out, on net," : "took in, on net,"} <F f={p.net!} /> MW over its <F f={p.count} /> reporting ties
              {p.demand ? <>, with a demand of <F f={p.demand} /> MW in the hour</> : <>; its demand in the hour is not held</>}.
            </p>
            <ToolTable caption={`${grid.label}'s ties in the hour the network shows`} minWidth={420} head={["Neighbour", "Flow, MW", "Direction"]}
              rows={p.ties.map((t) => ({ key: t.other, cells: [
                <>{nameOf(t.other)} <span className="font-mono text-xs text-muted">{t.other}</span></>,
                <F key="v" f={t} />,
                t.dir,
              ] }))} />
          </>
        ) : <NoData what={`${grid.label}'s ties`} reason={`the snapshot holds no flow for ${grid.ba} in the hour starting ${hourName(hour)}`} />}
      </ToolSection>
    </div>
  );
}

export function GravityFigures({ snap, hour, grid, live }: { snap: Snapshot; hour: string; grid: GridChoice; live: LiveExtras }) {
  const g = gravityPanel(snap, GRAVITY_GRIDS.map((x) => x.id), GRAVITY_CENTER, hour, live.generation);
  return (
    <div data-grid-panel={`grid_gravity_${grid.slug}`} className="mt-8">
      <ToolSection title={`What the gravity shape draws, the hour shown (${hourName(hour)})`}
        note={<>Each circle&apos;s area follows the grid&apos;s net generation; its pull toward the center, its net import over its reporting ties as a percent of that generation (a negative number: a net export, pushed out). The Lower 48&apos;s generation sets the scale{g.center ? <>: <F f={g.center} /> MW</> : <>; it is not held for the hour</>}. Hover a figure for its table, filter, hour and the snapshot&apos;s refresh.
          {" "}<span data-gravity-window="live">These are the figures of the hour the shape opens on, in the live week. A day picked in the replay stays in the address, but neither the shape nor this table draws it: net generation is held by hour for the live week only, not by day, so no figure here is that day&apos;s.</span>
          {" "}<span data-gravity-public="1">Every figure here, for every grid, is EIA-930&apos;s public interchange and net generation; no grid operator&apos;s own table is read, so no grid is held here.</span></>}>
        <ToolTable caption="The seven grids in the gravity shape, the hour shown" minWidth={460} head={["Grid", "Net generation, MW", "Net import, MW", "Import, percent of generation"]}
          rows={g.rows.map((r) => ({ key: r.ba, highlight: r.ba === grid.ba, cells: [
            GRAVITY_GRIDS.find((x) => x.id === r.ba)!.label,
            r.gen ? <F key="g" f={r.gen} /> : <span key="g" className="text-muted">not held</span>,
            r.net ? <F key="n" f={r.net} /> : <span key="n" className="text-muted">no tie reported</span>,
            r.share ? <F key="s" f={r.share} /> : <span key="s" className="text-muted">none</span>,
          ] }))} />
      </ToolSection>
    </div>
  );
}
