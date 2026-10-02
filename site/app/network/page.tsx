import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Section } from "@/components/Section";
import snapJson from "@/data/grid_network.json";
import { fetchHourly, pickSnapshot } from "@/lib/network";
import { HOURLY } from "@/lib/supabase";
import { Network, type Snapshot } from "./Network";

// Session 49 (session 42's Part B4): the 3D grid network. The page reads only the static snapshot
// data/grid_network.json, written by warehouse/derived/grid_network.py from eia930_all_interchange (EIA-930 hourly
// interchange), eia930_all_demand and carbon_intensity_hourly; no hourly history is in Supabase. Method:
// docs/methods/grid_network.md.
// Session 54: the page reads the hourly snapshot in the public Supabase Storage bucket erw-public (object storage, not the
// database; warehouse/derived/network_hourly.py, every hour) with a one-hour revalidation, and falls back to the committed
// data/grid_network.json (the daily build) when Storage is unreachable, the object is not whole, or it is older
// (lib/network.ts).
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
  const held = snap.nodes.filter((n) => n.demand_mw !== null).length;
  const erco = snap.links.filter((l) => l.a === "ERCO" || l.b === "ERCO");
  return (
    <>
      <h1 className="mb-1 text-3xl">The grid network</h1>
      <p className="mb-4 max-w-3xl text-sm">
        The {snap.nodes.length} balancing authorities that report to EIA-930, and the power they exchange, hour by hour over the week from{" "}
        {snap.window[0].slice(0, 10)} to {snap.window[1].slice(0, 10)} (UTC). Each sphere is a balancing authority; each line, the interchange between
        two of them, its width the hour&apos;s megawatts and its particles running the way the power flows.
      </p>
      <p className="mb-4 max-w-3xl text-sm" data-network-source={from}>
        <strong>Newest hour: {both(newest)}</strong>, refreshed {utc(snap.built)}
        {from === "storage" ? " (the hourly refresh)" : " (the daily snapshot: the hourly copy was not reachable)"}.
        {demandTs ? <> Demand of the seven ISOs: newest hour {both(demandTs)}.</> : null}{" "}
        <span className="text-muted">
          EIA publishes demand one to two hours after the hour, and the interchange between pairs of balancing authorities, in its API, has run more than a day
          behind it; carbon intensity, the sphere color, updates daily.
        </span>
      </p>
      <Section title="The network">
        <Network snap={snap} />
      </Section>
      <Section title="What you are looking at">
        <p className="mb-2 max-w-3xl text-sm">
          A balancing authority keeps supply and demand matched, minute by minute, in its own area, and trades power across the ties with its
          neighbors. EIA&apos;s description: the power system of the Lower 48 &quot;is made up of three main interconnections, which operate largely
          independently from each other with limited transfers of power between them&quot;, and ERCOT is the one where &quot;the balancing authority,
          interconnection, and the regional transmission organization are all the same entity and physical system&quot; (
          <a href={EIA_BA}>EIA, Today in Energy</a>). That is why ERCOT&apos;s node hangs on {erco.length} thin {erco.length === 1 ? "tie" : "ties"} here,
          while the eastern balancing authorities form one dense mesh.
        </p>
        <p className="max-w-3xl text-xs text-muted">
          Sphere size: demand for the {held} ISO balancing authorities the warehouse holds demand for (the latest hour), interchange volume over the
          week for the others. Color: carbon intensity of generation, green to cardinal, grey where not held. Positions are computed once, with a fixed
          seed, and never re-settle. Each pair is counted once: {snap.rule.replace(/^Each pair is counted once: /, "")} Snapshot built{" "}
          {utc(snap.built)}{snap.base_built ? <>, onto the daily build of {utc(snap.base_built)}</> : null}. Sources: <code className="font-mono">eia930_all_interchange</code>,{" "}
          <code className="font-mono">eia930_all_demand</code>, <code className="font-mono">carbon_intensity_hourly</code> (<Link href="/data">data</Link>);{" "}
          <Link href="/data/methods/grid_network">method</Link>.
        </p>
      </Section>
    </>
  );
}
