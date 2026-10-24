// Energy Research Warehouse (ERW) site, session 237: the Now view of the Grid tool (/grid). One sentence of what the
// chosen grid is doing in the latest hours held, computed from the tables, then the numbers: demand, the mix, the
// exchange and carbon, each with its hour and its check key (scripts/check-values.mjs recomputes every one).
// All eight choices read the public EIA-930 tables (eia930_all_demand, eia930_all_generation), the carbon table built
// from them (carbon_intensity_hourly) and the network's snapshot of eia930_all_interchange (lib/network.ts); none of
// the four numbers depends on a grid operator's own table. Under them, what the grid's own page showed
// (components/grid/YourGrid.tsx) and its block of "Grid conditions" (components/grid/Conditions.tsx), as they were.
import snapJson from "@/data/grid_network.json";
import type { Snapshot } from "@/app/network/Network";
import { CaisoMixWithheld } from "@/components/CaisoMixWithheld";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { ShareBar } from "@/components/ShareBar";
import { SiteLink as Link } from "@/components/SiteLink";
import { HeadlineNumber, HeadlineRow, SourceLine, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { daysAgo, renderTime, series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";
import { FUELS, fuelName, fuelOf, type GridData } from "@/lib/grid";
import { latestHour } from "@/lib/gridReads";
import { gridHref, type GridChoice } from "@/lib/gridtool";
import type { GridConfig } from "@/lib/markdown";
import { fetchHourly, pickSnapshot, tiesAt } from "@/lib/network";
import { completeHour } from "@/lib/networkV3";
import { attempt } from "@/lib/supabase";
import { GridYesterday } from "./Conditions";
import { GridNowParts } from "./YourGrid";
import { Preliminary } from "./Preliminary";
import { PanelFile } from "@/components/grid/PanelFile";  // session 1420: the mix in that hour, to download
import { METHOD_NOW_MIX, OLDER_ANCHOR } from "@/lib/gridAnchors";  // session 1421: its anchor and its method (as session 1184)

const DEMAND = "eia930_all_demand", GEN = "eia930_all_generation", CARBON = "carbon_intensity_hourly";
const H = 3_600_000;
/** The snapshot is read on each request: the hourly refresh may revise an hour, and a number shown must be the object's own. */
const FRESH = 0;
const committed = snapJson as unknown as Snapshot;
/** The EIA-930 code of each choice as "Grid conditions" names it (components/grid/Conditions.tsx BAS). */
const CONDITIONS_CODE: Record<string, string> = { ercot: "erco", caiso: "ciso", pjm: "pjm", miso: "miso", spp: "swpp", nyiso: "nyis", isone: "isne", us48: "us48" };

const hourOf = (ts: string, tz: string | null) => (tz
  ? new Intl.DateTimeFormat("en-US", { timeZone: tz, month: "short", day: "numeric", hour: "numeric", minute: "2-digit", timeZoneName: "short" }).format(new Date(ts))
  : `${ts.slice(0, 10)} ${ts.slice(11, 16)} UTC`);
const key = (t: string, r: SeriesRow) => `series|${t}|${r.entity}|${r.variable}|${r.ts_utc}`;
const N = ({ t, r }: { t: string; r: SeriesRow }) => <Num check={key(t, r)} raw={r.value}>{shown(r.value)}</Num>;
const byTime = (a: SeriesRow, b: SeriesRow) => a.ts_utc.localeCompare(b.ts_utc);

export async function NowView({ grid, cfg, data }: { grid: GridChoice; /** the grid's page config and reads (lib/grid.ts), null for the Lower 48 */ cfg: GridConfig | null; data: GridData | null }) {
  const entity = `eia930:${grid.ba}`;
  const tz = cfg?.tz ?? null;
  const withheld = grid.slug === "caiso";  // session 118: EIA-930's generation for California is not drawn
  // session 1160: the mix's read is the newest hour of the total in the last 34 days and that hour's rows
  // (lib/gridReads.ts latestHour: the rows drawn are the ones the 34-day read gave), and none for California, whose
  // EIA-930 generation is not drawn
  const [dem, gen, ci, fetched] = await Promise.all([
    attempt(() => series(DEMAND, { entity, variable: "demand_mw", since: daysAgo(9) })),
    withheld ? Promise.resolve({ ok: true as const, data: [] as SeriesRow[] }) : attempt(() => latestHour(GEN, entity, "net_generation_mw", daysAgo(34))),
    attempt(() => series(CARBON, { entity, since: daysAgo(7) })),
    fetchHourly(FRESH),
  ]);
  // demand: the latest hour held, and the same hour a week earlier
  const demand = dem.ok ? [...dem.data].sort(byTime) : [];
  const d = demand.at(-1);
  const dWeek = d ? demand.find((r) => Date.parse(r.ts_utc) === Date.parse(d.ts_utc) - 7 * 24 * H) : undefined;
  // the mix: the latest hour that holds the total, its fuels largest first
  const rows = gen.ok && !withheld ? gen.data : [];
  const total = rows.filter((r) => r.variable === "net_generation_mw").sort(byTime).at(-1);
  const fuels = total ? rows.filter((r) => r.ts_utc === total.ts_utc && r.variable !== "net_generation_mw" && r.variable.startsWith("net_generation_")).sort((a, b) => b.value - a.value) : [];
  const top = fuels[0];
  // the exchange: the network's snapshot, the newest hour every reporting pair holds
  const { snap } = pickSnapshot(fetched, committed);
  const complete = completeHour(snap.hours, snap.links);
  const xHour = complete.hour ?? snap.hours[snap.hours.length - 1];
  const ties = grid.slug === "us48" ? [] : tiesAt(snap, grid.ba, xHour);
  const net = ties.reduce((a, t) => a + t.mw, 0) || 0;
  // a net import is written as one: the same sum from the other side, with its own key
  const out = net >= 0;
  const netNum = <Num check={`net|${out ? "export" : "import"}|${grid.ba}|${xHour}`} raw={out ? net : -net}>{shown(out ? net : -net)}</Num>;
  // session 266: how old the exchange's hour is, in hours before the snapshot's hourly refresh (net|lag in lib/network.ts)
  const lag = Math.round((Date.parse(snap.built) - Date.parse(xHour)) / H);
  const lagNum = <Num check={`net|lag|${xHour}|${snap.built}`} raw={lag}>{shown(lag)}</Num>;
  // carbon: the latest hour EIA has estimated
  const cg = ci.ok ? ci.data.filter((r) => r.variable === "intensity_generation").sort(byTime).at(-1) : undefined;
  const cd = cg && ci.ok ? ci.data.find((r) => r.variable === "intensity_demand" && r.ts_utc === cg.ts_utc) : undefined;
  // session 1420: the mix's rows, drawn in its table and written in its file
  const mixRows = fuels.map((r) => ({ key: r.variable, cells: [fuelName(r.variable), <N key="v" t={GEN} r={r} />] }));

  return (
    <div data-grid-view="now">
      <p className="mb-8 max-w-3xl text-base leading-relaxed" data-now-sentence={grid.slug}>
        {d ? (
          <>
            In the hour starting {hourOf(d.ts_utc, tz)}, the latest EIA has published, {grid.slug === "us48" ? "the Lower 48 states" : grid.label} used <N t={DEMAND} r={d} /> MW
            {dWeek ? <>, {d.value > dWeek.value ? "more than" : d.value < dWeek.value ? "less than" : "the same as"} the <N t={DEMAND} r={dWeek} /> MW of the same hour a week earlier</> : null}.
          </>
        ) : <>The latest hour of demand could not be read just now. </>}
        {top && total ? (
          <> {fuelName(top.variable).replace(/^./, (c) => c.toUpperCase())} was its largest source: <N t={GEN} r={top} /> MW of the <N t={GEN} r={total} /> MW generated in the hour starting {hourOf(total.ts_utc, tz)}.</>
        ) : null}
        {ties.length ? (
          <> Over its {ties.length} reporting ties it {net > 0 ? "sent out more than it took in" : net < 0 ? "took in more than it sent out" : "sent out as much as it took in"}: a net {out ? "export" : "import"} of{" "}
            {netNum} MW in the hour starting {hourOf(xHour, tz)}, {lagNum} hours before the latest hourly refresh of EIA-930&apos;s interchange ({`${snap.built.slice(0, 16).replace("T", " ")} UTC`}), which EIA publishes about two days late.</>
        ) : null}
        {cg ? <> Each MWh it generated carried <N t={CARBON} r={cg} /> kg of CO2 in the hour starting {hourOf(cg.ts_utc, tz)}, the latest EIA has estimated.</> : null}
      </p>

      <HeadlineRow>
        <HeadlineNumber label="Demand" unit="MW" value={d ? <N t={DEMAND} r={d} /> : <span className="text-muted">not read</span>}
          note={d ? <>Hour starting {hourOf(d.ts_utc, tz)}.{dWeek ? <> A week earlier: <N t={DEMAND} r={dWeek} /> MW.</> : null}</> : dem.ok ? "No hour of demand in the last nine days." : dem.reason} />
        <HeadlineNumber label={ties.length && !out ? "Net import" : "Net export"} unit="MW" value={ties.length ? netNum : <span className="text-muted">{grid.slug === "us48" ? "by grid" : "not reported"}</span>}
          note={ties.length
            ? <>Hour starting {hourOf(xHour, tz)}, over <Num check={`net|ties|${grid.ba}|${xHour}`} raw={ties.length}>{shown(ties.length)}</Num> ties. <Link href={gridHref(grid.slug, "gravity")}>Each neighbour</Link>.</>
            : grid.slug === "us48" ? <>The Lower 48 is the sum of its grids: <Link href={gridHref(grid.slug, "gravity")}>the exchange of each</Link>.</>
              : <>No tie of {grid.label} reported in the hour starting {hourOf(xHour, tz)}, the newest hour every reporting pair holds (session 266: nothing stands in for it).</>} />
        <HeadlineNumber label="Carbon intensity" unit="kg CO2/MWh" value={cg ? <N t={CARBON} r={cg} /> : <span className="text-muted">not read</span>}
          note={cg ? <>Of generation, hour starting {hourOf(cg.ts_utc, tz)}.{cd ? <> Of the power used here, imports counted: <N t={CARBON} r={cd} />.</> : null}</> : ci.ok ? "No hour in the last seven days." : ci.reason} />
      </HeadlineRow>

      {/* session 1420: a named panel, its table to download */}
      <div data-grid-panel={`grid_nowmix_${grid.slug}`}>
      <ToolSection title="The mix in that hour" id={OLDER_ANCHOR.nowMix}>
        {withheld ? <CaisoMixWithheld what="California's generation by fuel" /> : !gen.ok ? <NoData what="generation by fuel" reason={gen.reason} /> : !total || !fuels.length ? <NoData what="generation by fuel" reason={`${GEN} holds no hour for ${grid.label} in the last 34 days`} /> : (
          <>
            <p className="mb-2 max-w-3xl text-sm">
              Hour starting {hourOf(total.ts_utc, tz)}: <N t={GEN} r={total} /> MW of net generation. <Link href={gridHref(grid.slug, "mix")}>The mix over days, months and years</Link>.
            </p>
            <ShareBar parts={FUELS.map((f) => ({ name: f.label, value: fuels.filter((r) => fuelOf(r.variable) === f.key).reduce((a, r) => a + r.value, 0), color: `var(--color-fuel-${f.key})` }))}
              unit="MW" ariaLabel={`${grid.label} generation by fuel, the latest hour`} file={`erw-${grid.slug}-mix-now`} />
            <div className="mt-3 max-w-xl">
              <ToolTable caption={`${grid.label} net generation by fuel, the latest hour`} minWidth={280} head={["Fuel, as EIA names it", "MW"]}
                rows={mixRows} />
            </div>
            <PanelFile of={{ panel: `grid_nowmix_${grid.slug}`, title: `${grid.label}'s net generation by fuel in the latest hour that holds the total, MW`, page: gridHref(grid.slug, "mix"),
              tables: [`${GEN} (EIA-930's hourly net generation by fuel, MW; hour starts)`], filter: `${entity}: net_generation_mw and each fuel's net_generation_<fuel>_mw`,
              window: `Hour: ${total.ts_utc.slice(0, 16).replace("T", " ")} UTC (hour start), the newest that holds the total in the last 34 days`,
              notes: ["The bar's shares are drawn from these rows, the fuels grouped as the bar's colours; they are not written here"],
              figures: [{ label: "Net generation in the hour", value: <N t={GEN} r={total} /> }] }}
              columns={["Fuel, as EIA names it", "MW"]} rows={mixRows.map((r) => r.cells)} />
          </>
        )}
        {/* session 1421: the section that defines the block, drawn in each of its states */}
        <p className="mt-1 text-xs text-muted" data-grid-method="now-mix"><Link href={METHOD_NOW_MIX}>Method: &quot;Right now&quot; and the mix in that hour</Link>.</p>
      </ToolSection>
      </div>

      {cfg && data ? <GridNowParts g={cfg} d={data} /> : null}
      <GridYesterday code={CONDITIONS_CODE[grid.slug]} />
      <SourceLine tables={[DEMAND, GEN, CARBON, "eia930_all_interchange"]}
        note={<>Public domain (EIA, Form EIA-930). The exchange is read from the network&apos;s hourly snapshot of the interchange table. Hours are hour starts. <Preliminary drawn={new Date(renderTime())} /></>} />
    </div>
  );
}
