// Energy Research Warehouse (ERW) site, session 1402 (chain 100): the hub's real-time price beside the Grid tool's
// hourly mix, `grid_hubprice_<grid>`, on the Mix tab under the 7-day chart of the energy mix panel (session 1152's
// grid_mix_<grid>). For the grids whose hub prices are public (site/lib/license.ts: ERCOT, CAISO, SPP) the hour's
// price (iso_rtm_hub_prices, the mean of its four 15-minute prices: lib/hubPriceHourly.ts) is drawn in a strip under
// the chart, on its time axis, and named on hover beside each fuel's MW (components/TimeChart.tsx, a `strip` series);
// this panel writes the strip's figures, each keyed: the hours held whole, their mean, the highest hour and the last
// hour held. CAISO's hourly mix is withheld (the session 118 ruling), and a grid whose generation could not be read has
// no chart: there the panel draws the price alone, over the 7 days to its newest day held whole. The other grids say in one
// line why no price is drawn (PJM no price held, MISO paused, NYISO and ISO-NE license needed, the Lower 48 no hub of
// its own). A failed read says "could not be read" (session 1181's rule); the mix chart above is drawn all the same.
// Its file (session 1182), its anchor (1183) and its method (1184), as every panel of the tool.
import { Num } from "@/components/Num";
import { Missing } from "@/components/mix/Now";
import { PanelFile } from "@/components/grid/PanelFile";
import { SiteLink } from "@/components/SiteLink";
import { TimeChart } from "@/components/TimeChart";
import { shown } from "@/lib/format";
import { gridHref } from "@/lib/gridtool";
import { hubPriceAnchor, METHOD_HUB_PRICE } from "@/lib/gridAnchors";
import { HUB_PRICE, RT_HUB_TABLE, hourName, type Fig, type HubPrice } from "@/lib/hubPriceHourly";
import { LICENSE_FROM, LICENSE_NEEDED, licenseHeldRow } from "@/lib/license";

type Read = { ok: true; data: unknown[] } | { ok: false; reason: string } | null;

/** Why a grid's hub price is not drawn on the day (one line in the tool's one look), or null when it is drawn. */
export function hubPriceWhy(grid: string, label: string, now: Date = new Date()): { words: string; why: string } | null {
  const hub = HUB_PRICE[grid];
  if (hub && !licenseHeldRow(RT_HUB_TABLE, hub.entity, now)) return null;
  if (grid === "us48") return { words: "no hub of its own", why: `The Lower 48 is many balancing authorities with no one hub, so no hub price is drawn beside its mix; ERCOT's, CAISO's and SPP's Mix tabs draw their hub's.` };
  if (grid === "pjm") return { words: LICENSE_NEEDED, why: `No PJM price is held (a licensed source is needed), so ${RT_HUB_TABLE} holds no PJM hub.` };
  if (grid === "miso") return { words: "paused", why: `MISO's own files are paused since 4 October 2026 (its terms forbid automated access: docs/methods/miso_pause.md), and ${RT_HUB_TABLE} is held for MISO.` };
  return { words: LICENSE_NEEDED, why: `${label}'s prices need a license from ${LICENSE_FROM} (warehouse/metadata/license_status.csv), so its hub's price is not drawn.` };
}

/** The strip's series for the hourly chart (TimeChart strip), or undefined when no hour of the window is held. */
export function hubStrip(hp: HubPrice | null) {
  return hp && hp.n.raw > 0 ? { name: `${hp.hub.hub} real-time`, color: "ink", unit: "USD/MWh", points: hp.points, strip: true } : undefined;
}

/** A figure with its key and its one-line source as the hover tip. */
function F({ f }: { f: Fig }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>
    </span>
  );
}

const endName = (t: number) => { const s = hourName(t); return s.endsWith(" 00:00 UTC") ? `${new Date(t - 3_600_000).toISOString().slice(0, 10)} 24:00 UTC` : s; };

export function HubPricePanel({ grid, label, i, read, hp, alone }: {
  grid: string;
  label: string;
  /** the grid's place among the grids of the page (its anchor) */
  i: number;
  /** the read of the hub's rows, or null when none was made */
  read: Read;
  /** the strip's hours and figures over the chart's window (or the price's own), or null */
  hp: HubPrice | null;
  /** true where no mix chart is drawn above (CAISO, or a failed generation read): the price is drawn here alone */
  alone: boolean;
}) {
  const id = hubPriceAnchor(i, grid);
  const why = hubPriceWhy(grid, label);
  const method = <p className="mt-1 text-xs text-muted" data-grid-method="hub-price"><SiteLink href={METHOD_HUB_PRICE}>Method: the hub&apos;s price beside the hourly mix</SiteLink>.</p>;
  if (why) {
    return (
      <div id={id} className="mb-2" data-grid-panel={`grid_hubprice_${grid}`}>
        <p className="max-w-3xl text-sm" data-hubprice-held={why.words}>The hub&apos;s real-time price beside the mix: <Missing why={why.why} words={why.words} /> <span className="text-xs text-muted">{why.why}</span></p>
      </div>
    );
  }
  const hub = HUB_PRICE[grid];
  if (!read || !read.ok) {
    return (
      <div id={id} className="mb-2" data-grid-panel={`grid_hubprice_${grid}`}>
        <p className="max-w-3xl text-sm" data-hubprice-unread={RT_HUB_TABLE}>{hub.label}, real-time price by hour: <Missing words="could not be read" why={`${RT_HUB_TABLE} could not be read just now: ${read ? read.reason : "no read"}`} /> ({RT_HUB_TABLE}).</p>
        {method}
      </div>
    );
  }
  if (!hp || hp.n.raw === 0) {
    return (
      <div id={id} className="mb-2" data-grid-panel={`grid_hubprice_${grid}`}>
        <p className="max-w-3xl text-sm" data-hubprice-none="1">{hub.label}, real-time price by hour: {hp ? <>no hour from {hourName(hp.t0)} to {endName(hp.t1)} holds its four 15-minute prices in {RT_HUB_TABLE}.</> : <>no day of the last 9 holds its 24 hours whole in {RT_HUB_TABLE}, so no 7 days are drawn.</>}</p>
        {method}
      </div>
    );
  }
  const strip = hubStrip(hp)!;
  const days = `${hourName(hp.t0)} to ${endName(hp.t1)}`;
  return (
    <div id={id} className="mb-2" data-grid-panel={`grid_hubprice_${grid}`}>
      {alone ? (
        <TimeChart series={[{ name: strip.name, color: strip.color, points: strip.points }]} unit="USD/MWh" height={200} x="minute"
          ariaLabel={`${hub.label}, real-time price by hour (the mean of its four 15-minute prices), ${days}`} />
      ) : null}
      <p className="mb-1 max-w-3xl text-sm" data-hubprice-figures="1">
        {alone ? <>{hub.label}, real-time price by hour, above: the 7 days to its newest day held whole, </> : <>Under the chart, {hub.label}&apos;s real-time price by hour, the same hours: </>}
        {days} (<F f={hp.n} /> of {hp.of} hours held whole). The mean of those hours <F f={hp.mean!} /> USD/MWh; the highest hour <F f={hp.max!.fig} /> USD/MWh, from {hourName(hp.max!.t)}; the last hour held, from {hourName(hp.latest!.t)}, <F f={hp.latest!.fig} /> USD/MWh.
      </p>
      <p className="mb-1 text-xs text-muted">An hour&apos;s price is the mean of its four 15-minute prices ({RT_HUB_TABLE}, {hub.entity}, {hub.variable}), drawn only when all four are held; hover the chart for the hour&apos;s price beside each fuel&apos;s MW.{alone && grid === "caiso" ? " California's hourly mix is withheld (session 118), so the price is drawn alone." : alone ? ` ${label}'s hourly mix is not drawn, so the price is drawn alone.` : ""}</p>
      <PanelFile of={{ panel: `grid_hubprice_${grid}`, title: `${label}: the real-time price at ${hub.label} by hour, over ${days}`, page: gridHref(grid, "mix"),
        tables: [`${RT_HUB_TABLE} (${hub.entity}, ${hub.variable}: the 15-minute real-time price, USD per MWh)`],
        filter: `${hub.entity}, ${hub.variable}: an hour's price is the mean of its four 15-minute prices, held only when all four are`,
        window: `Window: ${days}, ${alone ? "the 7 days to the hub's newest day held whole" : "the hours of the hourly mix chart"}`,
        notes: [`The window holds ${hp.of} hours; the hours' own prices are drawn in the chart, not written here`] }}
        columns={["Figure", "Value", "Unit"]}
        rows={[
          ["Hours held whole", <F key="n" f={hp.n} />, "hours"],
          ["Mean of the hours held", <F key="m" f={hp.mean!} />, "USD/MWh"],
          [`Highest hour, from ${hourName(hp.max!.t)}`, <F key="x" f={hp.max!.fig} />, "USD/MWh"],
          [`Last hour held, from ${hourName(hp.latest!.t)}`, <F key="l" f={hp.latest!.fig} />, "USD/MWh"],
        ]} />
      {method}
    </div>
  );
}
