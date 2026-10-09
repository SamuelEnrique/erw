import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Num } from "@/components/Num";
import { Fold, SourceLine, ToolHeader, ToolPage, ToolTable } from "@/components/tool/ToolPage";
import snapJson from "@/data/grid_network.json";
import { HEADLINE, MEASURES, SPREAD, TABLE as SUPPLY_TABLE, supplyOf, supplyStat, type Supply } from "@/lib/basupply";
import { fetchHourly, pickSnapshot } from "@/lib/network";
import { HOURLY, attempt } from "@/lib/supabase";
import { Network, type Snapshot } from "@/app/network/Network";
import { ISO_BA, liveExtras, supplyRows } from "@/app/network/data";  // session 93: the page's reads, shared with version 3
import { CaisoBreakNote } from "@/components/CaisoBreakNote";  // session 78 (session 73's "To finish", step 2)

// Session 168: retired and kept unrouted, as it stood. Version 3 is the network page now (app/network/page.tsx); what this
// page's folded sections and its note on California's data break said is in docs/methods/grid_network.md, and its
// "Newest hour" line is carried over to the page.
// Session 49 (session 42's Part B4): the 3D grid network. The page reads only the static snapshot
// data/grid_network.json, written by warehouse/derived/grid_network.py from eia930_all_interchange (EIA-930 hourly
// interchange), eia930_all_demand and carbon_intensity_hourly; no hourly history is in Supabase. Method:
// docs/methods/grid_network.md.
// Session 54: the page reads the hourly snapshot in the public Supabase Storage bucket erw-public (object storage, not the
// database; warehouse/derived/network_hourly.py, every hour) with a one-hour revalidation, and falls back to the committed
// data/grid_network.json (the daily build) when Storage is unreachable, the object is not whole, or it is older
// (lib/network.ts).
// Session 68: the network and its controls first, the explanation below in folded sections. The page also reads, for the
// panel: ba_supply_monthly (the last twelve months, lib/basupply.ts), the batteries of the live week (eia930_all_storage;
// CAISO's own caiso_battery_storage) and the hub prices of the live week (the price tables of data/markets.json), each
// aligned to the snapshot's hours. The two stories are static files (public/network/, warehouse/derived/network_stories.py).
export const metadata: Metadata = { title: "The grid network" };
export const revalidate = 3600;

const committed = snapJson as unknown as Snapshot;
const EIA_BA = "https://www.eia.gov/todayinenergy/detail.php?id=27152";
const ET = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
const utc = (t: string) => `${t.slice(0, 16).replace("T", " ")} UTC`;
const both = (t: string) => `${utc(t)} (${ET.format(new Date(t))} Eastern)`;
export default async function NetworkPage() {
  const { snap, from } = pickSnapshot(await fetchHourly(HOURLY), committed);
  const newest = snap.hours[snap.hours.length - 1];
  const demandTs = snap.nodes.filter((n) => n.iso && n.demand_ts).map((n) => n.demand_ts as string).reduce((a, b) => (b > a ? b : a), "");
  const heldDemand = snap.nodes.filter((n) => n.demand_mw !== null).length;
  const erco = snap.links.filter((l) => l.a === "ERCO" || l.b === "ERCO");
  const isos = Object.entries(ISO_BA);
  const [reads, extras] = await Promise.all([Promise.all(isos.map(([, ba]) => attempt(() => supplyRows(ba)))), liveExtras(snap)]);
  const bad = reads.find((r) => !r.ok);
  const rows = bad && !bad.ok ? { ok: false as const, reason: bad.reason } : { ok: true as const, data: reads.flatMap((r) => (r.ok ? r.data : [])) };
  const supply: Record<string, Supply> = {};
  if (rows.ok) for (const [, ba] of isos) { const s = supplyOf(rows.data, ba); if (s) supply[ba] = s; }
  const S = (ba: string, what: string, d = 2) => {
    const v = rows.ok ? supplyStat(rows.data, ba, what) : null;
    return v === null ? <span className="text-muted">not held</span> : <Num check={`bsup|${ba}|${what}`} raw={v}>{Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d })}</Num>;
  };
  const caiso = supply.CISO;

  return (
    <ToolPage>
      <ToolHeader title="The grid network"
        lead={<>The {snap.nodes.length} balancing authorities that report to EIA-930 and the power they exchange, hour by hour. Watch a story, or click a grid to see who supplies it.</>} />
      <Network snap={snap} supply={supply} live={extras} />
      <p className="mt-3 max-w-3xl text-xs text-muted" data-network-source={from}>
        Newest hour: {both(newest)}, refreshed {utc(snap.built)}{from === "storage" ? " (the hourly refresh)" : " (the daily snapshot: the hourly copy was not reachable)"}.
        {demandTs ? <> Demand of the seven ISOs: newest hour {both(demandTs)}.</> : null}
      </p>
      {!rows.ok ? <p className="mt-2 text-sm text-muted" role="status">The last twelve months could not be read, so the panel shows none: {rows.reason}</p> : null}

      <div className="mt-8 border-t border-rule">
        <Fold title="Who supplies each ISO grid: three measures">
          <p className="mb-3 max-w-3xl">
            A grid&apos;s net imports can be measured three ways from EIA-930: the sum of the ties it reports with each neighbour; EIA&apos;s own total
            interchange for it; and its demand less its net generation. They should agree. Over the last twelve months, as a share of demand, on each
            measure&apos;s own months:
          </p>
          <ToolTable caption="Three measures of net imports" minWidth={680}
            head={["Grid", "Sum of its ties", "EIA's total interchange", "Demand less net generation", "Largest supplier", "Days held / left out"]}
            rows={isos.map(([iso, ba]) => ({ key: ba, highlight: ba === "CISO", cells: [iso,
              <>{S(ba, `share:pairs`)} percent</>, <>{S(ba, `share:total_interchange`)} percent</>, <>{S(ba, `share:balance`)} percent</>,
              supply[ba]?.neighbours[0] ? <>{supply[ba].neighbours[0].id}, {S(ba, "top_share")} percent</> : <span className="text-muted">not held</span>,
              <>{S(ba, "days_held")} / {S(ba, "days_left_out")}</>] }))} />
          <ul className="mt-3 max-w-3xl list-disc space-y-1.5 pl-5">
            <li><strong>The headline is the sum of the ties</strong> ({MEASURES[HEADLINE]}). It is complete on every day it counts, it equals EIA&apos;s total interchange on the same days for CAISO, ERCOT, ISO-NE, MISO and NYISO, and the neighbours&apos; shares add up to it. Where the three measures differ by more than {SPREAD} point of demand, the panel shows the range.</li>
            <li><strong>CAISO.</strong> {caiso ? <>Its ties and EIA&apos;s total interchange agree to the MWh on every day; demand less net generation reads about ten points higher.</> : null} The gap opens in December 2025: through 2024 and most of 2025, CAISO&apos;s demand less net generation less its interchange was within about 2 percent of demand; from January 2026 it runs at 70 to 93 GWh a day, 10 to 15 percent of demand. The interchange did not change: CAISO&apos;s published net generation fell. Why EIA&apos;s figure fell is not in the data the warehouse holds. Until it is explained, the balance overstates California&apos;s imports.</li>
            <li><strong>PJM</strong>: the three disagree by about two points. <strong>SPP</strong>: its ties read about half a point below the other two. Both leave out many days (a regular neighbour missing or a pair-day screened).</li>
            <li><strong>MISO</strong>: demand less net generation reads one to three points below its interchange on the same days, in every year since 2019.</li>
          </ul>
          <p className="mt-2 text-xs text-muted">
            Held days: every regular neighbour reported and no pair-day screened out (further than 10 median absolute deviations, at least 500 MWh, from the
            pair&apos;s own median: EIA&apos;s daily interchange holds days no tie can carry). Demand and net generation are held for the seven ISO grids only. EIA&apos;s
            Eastern day. Method: <Link href="/data/methods/grid_network">grid network</Link>.
          </p>
        </Fold>
        <Fold title="What this is, and what it is not">
          <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
            <li><strong>Physical flows between balancing authorities</strong>, as each reports them to EIA. Not contracts: who buys power from whom can differ from the path it takes.</li>
            <li><strong>EIA revises its data.</strong> A day reported late or corrected changes these figures when the warehouse next pulls it.</li>
            <li><strong>A neighbour&apos;s power may itself be imported.</strong> A grid&apos;s supplier is the tie it arrives over, not where it was generated.</li>
            <li><strong>Each pair is counted once</strong> on the network: {snap.rule.replace(/^Each pair is counted once: /, "")}</li>
            <li>A balancing authority keeps supply and demand matched in its own area and trades across the ties with its neighbours. EIA: the power system of the Lower 48 &quot;is made up of three main interconnections, which operate largely independently from each other with limited transfers of power between them&quot;, and ERCOT is the one where &quot;the balancing authority, interconnection, and the regional transmission organization are all the same entity and physical system&quot; (<a href={EIA_BA}>EIA, Today in Energy</a>). That is why ERCOT hangs on {erco.length} thin {erco.length === 1 ? "tie" : "ties"} while the eastern grids form one dense mesh.</li>
            <li>Sphere size: demand for the {heldDemand} ISO balancing authorities the warehouse holds demand for, interchange volume over the week for the others. Color: carbon intensity of generation, green to cardinal, grey where not held. Positions are computed once, with a fixed seed, and never re-settle.</li>
          </ul>
        </Fold>
        <Fold title="How fresh each layer is">
          <ul className="max-w-3xl list-disc space-y-1 pl-5">
            <li>The flows of the live week: refreshed every hour; newest hour {both(newest)}. EIA&apos;s interchange between pairs has run more than a day behind its demand.</li>
            <li>Demand of the seven ISOs: {demandTs ? <>newest hour {both(demandTs)}</> : "not held"}; EIA publishes it one to two hours after the hour.</li>
            <li>Carbon intensity, the sphere color: daily.</li>
            <li>Batteries of the live week: EIA-930 for ERCOT, ISO-NE, MISO and SPP; CAISO&apos;s own data for CAISO; refreshed daily. NYISO and PJM report no battery series.</li>
            <li>Who supplies a grid, the last twelve months: EIA-930&apos;s daily interchange, refreshed with the warehouse; {caiso ? <>{caiso.months[0]} to {caiso.months.at(-1)}</> : "not held"}.</li>
            <li>The two stories: fixed windows, pulled once (Uri: 2021-02-07 to 2021-02-24; the June 2025 heat: 2025-06-20 to 2025-06-28).</li>
          </ul>
        </Fold>
      </div>
      <CaisoBreakNote className="mt-6 mb-0" />
      <SourceLine tables={["eia930_all_interchange", "eia930_all_demand", "carbon_intensity_hourly", "carbon_intensity_daily", SUPPLY_TABLE, "eia930_daily_interchange",
        "eia930_daily_total_interchange", "eia930_event_hourly_interchange", "eia930_all_storage", "caiso_battery_storage"]}
        note={<>Built {utc(snap.built)}{snap.base_built ? <>, onto the daily build of {utc(snap.base_built)}</> : null}. Public domain (EIA) and CAISO. <Link href="/data/methods/grid_network">Method</Link>.</>} />
    </ToolPage>
  );
}
