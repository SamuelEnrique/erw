// Energy Research Warehouse (ERW) site, session 237: the Exchange view of the Grid tool (/grid): the chosen grid's
// trade with its neighbours. Two reads, both the network page's own: the hourly snapshot of eia930_all_interchange
// (lib/network.ts: the newest hour every reporting pair holds, and the week before it) and ba_supply_monthly (the last
// twelve months, lib/basupply.ts). Every figure carries a check key that scripts/check-values.mjs recomputes from the
// snapshot or the table (net|..., bsup|...). A tie's flow is signed from the grid's side: positive, it sent power out.
// Session 1167 (chain 078): each neighbour's flow in the hour shown answers a hover with its tie, its hour and the week's
// mean, lowest and highest; beside it the same tie over the snapshot's week, keyed nettie|<stat>|... (lib/gridKeys.ts
// exchangeTies, recomputed by check-values with nettieValue); the direction in words ("sends to", "takes from"); the
// hour's age against the snapshot's refresh said once in each branch (net|lag), not in every row. No figure that stood moved.
import snapJson from "@/data/grid_network.json";
import type { Snapshot } from "@/app/network/Network";
import { ISO_BA, supplyRows } from "@/app/network/data";
import { LineChart } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, HeadlineNumber, HeadlineRow, SourceLine, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { HEADLINE, MEASURES, TABLE as SUPPLY_TABLE, supplyOf } from "@/lib/basupply";
import { shown } from "@/lib/format";
import { GRID_CHOICES, gridHref, type GridChoice } from "@/lib/gridtool";
import { directionWords, exchangeTies, type Fig } from "@/lib/gridKeys";  // session 1167
import { netExports, pickSnapshot, tiesAt, topExporter } from "@/lib/network";
import { freshSnapshot } from "@/lib/gridReads";  // session 1180
import { completeHour } from "@/lib/networkV3";
import { attempt } from "@/lib/supabase";
import { PanelFile, type FileOf } from "@/components/grid/PanelFile";  // session 1182: each table, to download

const committed = snapJson as unknown as Snapshot;
const hourName = (t: string) => `${t.slice(0, 10)} ${t.slice(11, 13)}:00 UTC`;
const refreshName = (t: string) => `${t.slice(0, 16).replace("T", " ")} UTC`;
/** Session 1182: the hour's age as the file's header writes it, the figure Age draws (net|lag). */
const lagFig = (hour: string, built: string) => ({ check: `net|lag|${hour}|${built}`, raw: Math.round((Date.parse(built) - Date.parse(hour)) / 3_600_000) });
const snapTable = (built: string) => `eia930_all_interchange (EIA-930, public domain), as the network snapshot holds it (read fresh; this snapshot built ${built})`;
/** Session 1167: a keyed figure with its one-line source on hover (the tool's dotted rule), or the words "none". */
const Tip = ({ f }: { f: Fig | null }) => (f ? <span title={f.tip} className="cursor-help border-b border-dotted border-muted"><Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num></span> : <span className="text-muted">none</span>);
/** Session 1167: the hour's age against the snapshot's refresh, said once (net|lag, lib/network.ts netValue). */
function Age({ hour, built }: { hour: string; built: string }) {
  const lag = Math.round((Date.parse(built) - Date.parse(hour)) / 3_600_000);
  return <>The hour starting {hourName(hour)} began <Num check={`net|lag|${hour}|${built}`} raw={lag}>{shown(lag)}</Num> hours before the snapshot&apos;s hourly refresh ({refreshName(built)}): EIA-930 publishes interchange about two days behind the clock.</>;
}

export async function ExchangeView({ grid }: { grid: GridChoice }) {
  // read on each request: the hourly refresh may revise an hour, and a number shown must be the object's own
  // session 1180: fresh once a render (lib/gridReads.ts freshSnapshot), the same object the network component above
  // draws on the Gravity tab
  const { snap } = pickSnapshot(await freshSnapshot(), committed);
  const complete = completeHour(snap.hours, snap.links);
  const hour = complete.hour ?? snap.hours[snap.hours.length - 1];
  const nameOf = (id: string) => snap.nodes.find((n) => n.id === id)?.name ?? id;
  const source = (
    <SourceLine tables={["eia930_all_interchange", SUPPLY_TABLE]}
      note={<>Public domain (EIA, Form EIA-930). The hour shown is the newest that every reporting pair of the week holds: {hourName(hour)}. <Link href="/data/methods/grid_network">Method</Link>.</>} />
  );

  if (grid.slug === "us48") {
    const net = netExports(snap, hour);
    const top = topExporter(snap, hour);
    const isos = GRID_CHOICES.filter((g) => g.slug !== "us48" && net.has(g.ba));
    // session 1182: the table's rows, drawn and offered as a file from the same cells
    const head48 = ["Grid", "Net export, MW", "Ties reporting"];
    const rows48 = isos.map((g) => ({ key: g.slug, cells: [
              <Link key="g" href={gridHref(g.slug, "gravity")}>{g.label}</Link>,
              <Num key="n" check={`net|export|${g.ba}|${hour}`} raw={net.get(g.ba)!}>{shown(net.get(g.ba)!)}</Num>,
              <Num key="t" check={`net|ties|${g.ba}|${hour}`} raw={tiesAt(snap, g.ba, hour).length}>{shown(tiesAt(snap, g.ba, hour).length)}</Num>,
            ] }));
    const file48: FileOf = { panel: "grid_exchange_us48", title: "the seven grids' net export in the hour", page: gridHref(grid.slug, "gravity"), tables: [snapTable(snap.built)],
      filter: "each of the seven ISO grids' reporting ties in the hour, summed and signed from the grid's side (negative: a net import)",
      window: `Hour: ${hourName(hour)} (hour start), the newest that every reporting pair of the week holds`,
      figures: [...(top ? [{ label: `the largest net exporter of the ${snap.nodes.length} balancing authorities, ${nameOf(top.id)} (${top.id}), MW`, value: { check: `net|topexport|${hour}`, raw: top.mw } }] : []),
        { label: "hours between the hour's start and the snapshot's hourly refresh", value: lagFig(hour, snap.built) }] };
    return (
      <div data-grid-view="exchange">
        <p className="mb-6 max-w-3xl text-base leading-relaxed">
          The Lower 48 is the sum of its grids, so its exchange is theirs: what each of the seven grids sent out or took in over its ties in the hour starting {hourName(hour)}.
          {top ? <> The largest net exporter among all {snap.nodes.length} balancing authorities was {nameOf(top.id)}, with <Num check={`net|topexport|${hour}`} raw={top.mw}>{shown(top.mw)}</Num> MW.</> : null}
        </p>
        <p className="-mt-3 mb-6 max-w-3xl text-sm text-muted" data-exchange-age="us48"><Age hour={hour} built={snap.built} /></p>
        <ToolSection title="The seven grids, that hour" note="Net export, MW: the sum of a grid's reporting ties, signed from its side. A negative number is a net import.">
          <ToolTable caption="Net export of the seven grids in the hour" minWidth={360} head={head48}
            rows={rows48} />
          <PanelFile of={file48} columns={head48} rows={rows48.map((r) => r.cells)} />
        </ToolSection>
        <p className="mb-6 text-sm"><Link href={gridHref(grid.slug, "network")}>See every tie on the network</Link>.</p>
        {source}
      </div>
    );
  }

  const ba = grid.ba;
  const ties = tiesAt(snap, ba, hour).map((t) => ({ ...t, mw: t.mw || 0 })).sort((a, b) => Math.abs(b.mw) - Math.abs(a.mw));
  const net = ties.reduce((a, t) => a + t.mw, 0) || 0;
  // a net import is written as one: the same sum from the other side, with its own key
  const out = net >= 0;
  const netNum = <Num check={`net|${out ? "export" : "import"}|${ba}|${hour}`} raw={out ? net : -net}>{shown(out ? net : -net)}</Num>;
  const maxFlow = ties.length ? Math.max(...ties.map((t) => Math.abs(t.mw))) : null;
  // the week: the grid's net export in each hour that holds a tie
  const mine = snap.links.filter((l) => l.a === ba || l.b === ba);
  const week = snap.hours.map((h, i) => {
    let sum = 0, n = 0;
    for (const l of mine) { const v = l.mw[i]; if (v === null || v === undefined) continue; sum += l.a === ba ? v : -v; n += 1; }
    return n ? { t: Date.parse(h) / 1000, v: sum } : null;
  }).filter((p): p is { t: number; v: number } => p !== null);
  const sup = Object.values(ISO_BA).includes(ba) ? await attempt(() => supplyRows(ba)) : null;
  const s = sup && sup.ok ? supplyOf(sup.data, ba) : null;
  // session 1167: the same ties over the snapshot's week, in the table's order, and each flow's hover line
  const wk = new Map(exchangeTies(snap, ba, hour, ties).map((w) => [w.other, w]));
  // session 1182: the ties' rows and the neighbours' rows, drawn and offered as files from the same cells; the headline's
  // figures in the ties file's header, the twelve months' in the neighbours'
  const tieHead = ["Neighbour", "Flow, MW", "Direction", "Week's mean, MW", "Week's lowest, MW", "Week's highest, MW", "Hours with a flow"];
  const tieRows = ties.map((t) => { const w = wk.get(t.other); return { key: t.other, cells: [
              <>{nameOf(t.other)} <span className="font-mono text-xs text-muted">{t.other}</span></>,
              <span key="v" title={w?.tip} className="cursor-help border-b border-dotted border-muted" data-exchange-tie={t.other}><Num check={`net|tie|${ba}|${t.other}|${hour}`} raw={t.mw}>{shown(t.mw)}</Num></span>,
              <span key="d" data-exchange-dir={directionWords(t.mw)}>{t.mw === 0 ? "none" : `${grid.label} ${directionWords(t.mw)} ${t.other}`}</span>,
              <Tip key="m" f={w?.mean ?? null} />, <Tip key="l" f={w?.min ?? null} />, <Tip key="h" f={w?.max ?? null} />, <Tip key="n" f={w?.hours ?? null} />,
            ] }; });
  const tieFile: FileOf = { panel: `grid_exchange_${grid.slug}`, part: "ties", title: `${grid.label}'s ties in the hour, and each tie over the snapshot's week`, page: gridHref(grid.slug, "gravity"),
    tables: [snapTable(snap.built)],
    filter: `the ties of ${ba} (${grid.label}) with a flow in the hour, signed from ${grid.label}'s side (positive: power left the grid); the week's columns are the same tie in the hours of the week that hold a flow`,
    window: `Hour: ${hourName(hour)} (hour start), the newest that every reporting pair of the week holds; the week: ${hourName(snap.hours[0])} to ${hourName(snap.hours[snap.hours.length - 1])}`,
    figures: [
      ...(ties.length ? [{ label: `net ${out ? "export" : "import"} over the reporting ties, MW`, value: { check: `net|${out ? "export" : "import"}|${ba}|${hour}`, raw: out ? net : -net } },
        { label: "ties reporting", value: { check: `net|ties|${ba}|${hour}`, raw: ties.length } }] : []),
      ...(maxFlow !== null ? [{ label: `the largest flow, either way, with ${nameOf(ties[0].other)}, MW`, value: { check: `net|maxflow|${ba}|${hour}`, raw: maxFlow } }] : []),
      { label: "hours between the hour's start and the snapshot's hourly refresh", value: lagFig(hour, snap.built) },
    ] };

  return (
    <div data-grid-view="exchange">
      <p className="mb-6 max-w-3xl text-base leading-relaxed">
        {ties.length ? (
          <>In the hour starting {hourName(hour)}, {grid.label} {net > 0 ? "sent out more power than it took in" : net < 0 ? "took in more power than it sent out" : "sent out as much power as it took in"} over
            its {ties.length} reporting ties: a net {out ? "export" : "import"} of {netNum} MW.</>
        ) : <>No tie of {grid.label} reported a flow in the hour starting {hourName(hour)}.</>}
      </p>
      {ties.length ? (
        <HeadlineRow>
          <HeadlineNumber label={out ? "Net export" : "Net import"} unit="MW" value={netNum} note="The sum of its reporting ties in the hour." />
          <HeadlineNumber label="Ties reporting" value={<Num check={`net|ties|${ba}|${hour}`} raw={ties.length}>{shown(ties.length)}</Num>} note={`Neighbours with a flow in the hour starting ${hourName(hour)}.`} />
          <HeadlineNumber label="Largest flow" unit="MW" value={maxFlow !== null ? <Num check={`net|maxflow|${ba}|${hour}`} raw={maxFlow}>{shown(maxFlow)}</Num> : null} note={`Either way, with ${nameOf(ties[0].other)}.`} />
        </HeadlineRow>
      ) : null}

      <ToolSection title="Each neighbour, that hour" note={`Flow over the tie, MW, signed from this grid's side: a positive number left the grid, a negative one came in. The week's columns are the same tie over the snapshot's week, ${hourName(snap.hours[0])} to ${hourName(snap.hours[snap.hours.length - 1])}, in the hours that hold a flow; hover a flow for its source and the week in words.`}>
        <p className="mb-3 max-w-3xl text-sm" data-exchange-age={ba}><Age hour={hour} built={snap.built} /></p>
        {ties.length ? (
          <><ToolTable caption={`${grid.label}'s ties in the hour`} minWidth={680} head={tieHead}
            rows={tieRows} />
          <PanelFile of={tieFile} columns={tieHead} rows={tieRows.map((r) => r.cells)} /></>
        ) : <NoData what={`${grid.label}'s ties`} reason={`the snapshot holds no flow for ${ba} in the hour starting ${hourName(hour)}`} />}
      </ToolSection>

      {week.length ? (
        <ChartFrame title="Net export, hour by hour over the week" note={`The sum of ${grid.label}'s reporting ties in each hour of the network's live week, ${hourName(snap.hours[0])} to ${hourName(snap.hours[snap.hours.length - 1])}. Above zero the grid sent power out; below, it took power in.`}>
          <LineChart lines={[{ label: "Net export", color: "accent", points: week }]} unit="MW" height={240} ariaLabel={`${grid.label} net export by hour over the latest week`} />
        </ChartFrame>
      ) : null}

      <ToolSection title="Over the last twelve months" note={s ? `${s.months[0]} to ${s.months.at(-1)}: ${s.daysHeld} days held, ${s.daysLeftOut} left out. Here a positive number is a net import: the neighbour supplied the grid. The share is of the grid's demand over the same months.` : undefined}>
        {!sup ? <NoData what="the twelve months" reason="a share needs the grid's demand, which the warehouse holds for the seven grids only" />
          : !sup.ok ? <NoData what="the twelve months" reason={sup.reason} />
          : !s ? <NoData what="the twelve months" reason={`${SUPPLY_TABLE} holds no whole month for ${ba}`} /> : (
            <>
              <p className="mb-3 max-w-3xl text-sm">
                {s.hasDemand
                  ? <>Net imports were <Num check={`bsup|${ba}|share:${HEADLINE}`} raw={s.share[HEADLINE]!}>{shown(s.share[HEADLINE]!)}</Num> percent of {grid.label}&apos;s demand ({MEASURES[HEADLINE]}): </>
                  : <>Net imports: </>}
                <Num check={`bsup|${ba}|mwh:${HEADLINE}`} raw={Math.round(s.mwh[HEADLINE] ?? 0)}>{shown(Math.round(s.mwh[HEADLINE] ?? 0))}</Num> MWh over{" "}
                <Num check={`bsup|${ba}|days_held`} raw={s.daysHeld}>{shown(s.daysHeld)}</Num> days.
              </p>
              {(() => {
                // session 1182: the neighbours' rows, drawn and offered as a file from the same cells
                const supHead = ["Neighbour", "Net import, MWh", "Percent of demand", "Direction"];
                const supRows = s.neighbours.map((n) => ({ key: n.id, cells: [
                  <>{nameOf(n.id)} <span className="font-mono text-xs text-muted">{n.id}</span></>,
                  <Num key="m" check={`bsup|${ba}|neighbour_mwh:${n.id}`} raw={Math.round(n.mwh)}>{shown(Math.round(n.mwh))}</Num>,
                  n.share !== null ? <Num key="s" check={`bsup|${ba}|neighbour:${n.id}`} raw={n.share}>{shown(n.share)}</Num> : <span className="text-muted">no share</span>,
                  // session 1167: the direction in words; here a positive number is a net import, so the grid takes from the neighbour
                  <span key="d" data-exchange-dir={directionWords(-Math.round(n.mwh))}>{Math.round(n.mwh) === 0 ? "none" : `${grid.label} ${directionWords(-Math.round(n.mwh))} ${n.id}, net`}</span>,
                ] }));
                const supFile: FileOf = { panel: `grid_exchange_${grid.slug}`, part: "twelve_months", title: `${grid.label}'s neighbours over the last twelve months`, page: gridHref(grid.slug, "gravity"),
                  tables: [`${SUPPLY_TABLE} (EIA-930's interchange by neighbour, with the grid's demand)`],
                  filter: `${ba} (${grid.label}): each neighbour's net import over the months, a positive number the neighbour supplied the grid; the share is of the grid's demand over the same months (${MEASURES[HEADLINE]})`,
                  window: `Window: ${s.months[0]} to ${s.months.at(-1)}, ${s.daysHeld} days held, ${s.daysLeftOut} left out`,
                  figures: [
                    ...(s.hasDemand ? [{ label: `net imports, percent of ${grid.label}'s demand`, value: { check: `bsup|${ba}|share:${HEADLINE}`, raw: s.share[HEADLINE]! } }] : []),
                    { label: "net imports, MWh", value: { check: `bsup|${ba}|mwh:${HEADLINE}`, raw: Math.round(s.mwh[HEADLINE] ?? 0) } },
                    { label: "days held", value: { check: `bsup|${ba}|days_held`, raw: s.daysHeld } },
                  ] };
                return <><ToolTable caption={`${grid.label}'s neighbours over twelve months`} minWidth={560} head={supHead}
                  rows={supRows} />
                  <PanelFile of={supFile} columns={supHead} rows={supRows.map((r) => r.cells)} /></>;
              })()}
            </>
          )}
      </ToolSection>
      <p className="mb-6 text-sm"><Link href={gridHref(grid.slug, "network")}>See these ties on the network, and trace the power two steps back</Link>.</p>
      {source}
    </div>
  );
}
