// Energy Research Warehouse (ERW) site, session 1406 (chain 100): the Lower 48 on the Network tab. Inside the Lower 48's
// Network panel (grid_network_us48, components/grid/NetworkFigures.tsx), under the seven grids' net exchange, which stands
// as it was: in the same hour, each of the seven grids' demand (chosen and keyed as the grid in view's demand is), the
// Lower 48's own (EIA-930's US48), the seven's sum and its share of the Lower 48; and, in words, the seven's exchange with
// the grids around them, with the rest of the Lower 48 and with Canada's and Mexico's operators. Every figure is a
// lib/gridKeys.ts figure (lower48Demand): a key check-values recomputes, a one-line source on hover. A failed read of
// eia930_all_demand says "could not be read" (session 1181's rule), never "not held"; a grid's demand the hourly snapshot
// holds still stands, as on the grid's own panel. Its file (session 1182), anchor (1183) and method (1184).
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { Missing } from "@/components/mix/Now";
import { ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { PanelFile, type FileOf } from "@/components/grid/PanelFile";
import type { LiveExtras, Snapshot } from "@/app/network/Network";
import { shown } from "@/lib/format";
import { gridHref, type GridChoice } from "@/lib/gridtool";
import { lower48Demand, type Fig, type Flow } from "@/lib/gridKeys";
import { LOWER48_DEMAND_ANCHOR, METHOD_NETWORK_US48 } from "@/lib/gridAnchors";

const hourName = (t: string) => `${t.slice(0, 10)} ${t.slice(11, 13)}:00 UTC`;
const DEMAND_TABLE = "eia930_all_demand";

/** A figure with its key and its one-line source as the hover tip. */
function F({ f }: { f: Fig }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>
    </span>
  );
}

/** A flow in words: its direction and its size, "sent out, on net, X MW" or "took in, on net, X MW". */
function Sent({ f, to, from }: { f: Flow; to: string; from: string }) {
  return f.kind === "export" ? <>sent <F f={f} /> MW {to}</> : <>took in <F f={f} /> MW {from}</>;
}

export function Lower48Demand({ snap, hour, live, grids }: { snap: Snapshot; hour: string; live: LiveExtras; grids: GridChoice[] }) {
  const d = lower48Demand(snap, grids.map((g) => g.ba), hour, live.demand);
  const failed = live.failed?.demand;
  const unread = (key: string) => <Missing key={key} words="could not be read" why={`${DEMAND_TABLE} could not be read just now: ${failed}`} />;
  const gone = (key: string) => (failed ? unread(key) : <span key={key} className="text-muted">not held</span>);
  const label = (ba: string) => grids.find((g) => g.ba === ba)!.label;
  const sourceOf = (f: Fig | null) => (!f ? "" : f.check.startsWith("netsnap|") ? "the hourly network snapshot (eia930_all_demand as the hourly refresh read it)" : DEMAND_TABLE);
  const notSum = failed ? "not computed: a grid's demand could not be read" : "not computed: a grid's demand is not held";
  const head = ["Grid", "Demand, MW", "Source"];
  const rows = [
    ...d.rows.map((r) => ({ key: r.ba, cells: [label(r.ba), r.demand ? <F key="v" f={r.demand} /> : gone("v"), sourceOf(r.demand)] })),
    { key: "seven", highlight: true, cells: ["The seven together", d.sum ? <F key="v" f={d.sum} /> : <span key="v" className="text-muted">{notSum}</span>, "the seven above, summed"] },
    { key: "us48", cells: ["The Lower 48 (EIA-930's US48)", d.us48 ? <F key="v" f={d.us48} /> : gone("v"), `${DEMAND_TABLE}, entity eia930:US48`] },
    { key: "share", highlight: true, cells: ["The seven's share of the Lower 48, percent", d.share ? <F key="v" f={d.share} />
      : <span key="v" className="text-muted">{!d.sum ? notSum : failed ? "not computed: the Lower 48's demand could not be read" : "not computed: the Lower 48's demand is not held"}</span>, "the two above"] },
  ];
  const few = d.reporting.length < grids.length;
  const file: FileOf = { panel: "grid_network_us48", part: "demand", title: "the seven grids' demand and the Lower 48's, and the seven's exchange, in the hour the network shows",
    page: gridHref("us48", "network"),
    tables: [`${DEMAND_TABLE} (EIA-930, demand_mw: each grid's and the Lower 48's (eia930:US48), the week's rows, else the hourly snapshot's for a grid)`,
      `eia930_all_interchange (EIA-930, public domain), as the network snapshot holds it (refreshed hourly; this snapshot built ${snap.built})`],
    filter: "the seven ISO grids and EIA-930's Lower 48 (US48): demand in the hour; the seven's reporting ties summed, signed from their side, and split by the operator at the other end (Canada's and Mexico's, or the rest of the Lower 48)",
    window: `Hour: ${hourName(hour)} (hour start), the hour the network opens on: the newest that every reporting pair of the snapshot's week holds`,
    figures: [
      { label: `the seven's net ${d.total ? d.total.kind : "exchange"} over their ties with every grid around them, MW`, value: d.total ? d.total : "no tie reported" },
      { label: `of it, with the rest of the Lower 48, MW (${d.rest ? (d.rest.kind === "export" ? "sent out" : "taken in") : "none"})`, value: d.rest ? d.rest : "no tie reported" },
      { label: `of it, with Canada's and Mexico's operators, MW (${d.abroad ? (d.abroad.kind === "export" ? "sent out" : "taken in") : "none"})`, value: d.abroad ? d.abroad : "no tie to Canada or Mexico reported" },
    ] };
  return (
    <div data-grid-lower48={hour} id={LOWER48_DEMAND_ANCHOR}>
      <ToolSection title={`The seven grids' demand and the Lower 48's, the same hour (${hourName(hour)})`}
        note={<>Demand is EIA-930&apos;s, as each grid&apos;s own panel reads it: the week&apos;s rows of {DEMAND_TABLE}, else the hourly snapshot&apos;s. The Lower 48 is EIA-930&apos;s US48, the sum EIA makes of the contiguous states&apos; balancing authorities, so the seven&apos;s share is of that total; the rest is the other balancing authorities of the Lower 48. The exchange is the seven&apos;s reporting ties summed, signed from their side: a tie between two of the seven counts once for each and cancels, so what is left is what crossed to the grids around them, split by the operator at the other end. Hover a figure for its table, filter and hour.</>}>
        <p className="mb-3 max-w-3xl text-sm" data-lower48-exchange={d.total ? d.total.kind : "none"}>
          {d.total && d.rest
            ? <>In the hour, the seven together {d.total.kind === "export" ? "sent out" : "took in"}, on net, <F f={d.total} /> MW over their ties with the grids around them: they <Sent f={d.rest} to="to the rest of the Lower 48" from="from the rest of the Lower 48" />{d.abroad ? <>, and <Sent f={d.abroad} to="to Canada's and Mexico's operators" from="from Canada's and Mexico's operators" /></> : <>; no tie to Canada or Mexico reported</>}.{few ? <> Only {d.reporting.length} of the seven report a tie in the hour; the sums are over them.</> : null}</>
            : <>No grid of the seven reports a tie in the hour, so their exchange is not said.</>}
        </p>
        <p className="mb-3 max-w-3xl text-sm" data-lower48-demand={d.share ? "share" : "none"}>
          {d.sum && d.share
            ? <>Their demand in the hour sums to <F f={d.sum} /> MW, <F f={d.share} /> percent of the Lower 48&apos;s <F f={d.us48!} /> MW.</>
            : d.sum ? <>Their demand in the hour sums to <F f={d.sum} /> MW; the Lower 48&apos;s demand {failed ? unread("u") : "is not held"} for the hour, so the share is not computed.</>
            : <>Their demand is not summed: {failed ? <>a grid&apos;s demand {unread("u")}</> : "a grid's demand is not held for the hour"}.</>}
        </p>
        <ToolTable caption="The seven grids' demand and the Lower 48's in the hour the network shows" minWidth={420} head={head} rows={rows} />
        <PanelFile of={file} columns={head} rows={rows.map((r) => r.cells)} />
        <p className="mt-1 text-xs text-muted" data-grid-method="lower48-demand"><Link href={METHOD_NETWORK_US48}>Method: the Lower 48 on the Network tab</Link>.</p>
      </ToolSection>
    </div>
  );
}
