import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { count } from "@/lib/format";
import { LICENSE_FROM } from "@/lib/license";
import publicFile from "@/data/datacenters_public.json";

// Session 827: the datacenter tracker's rows sorted by who stands behind them, the same sort as the deal tracker's
// (warehouse/deals/public_rows.py --datacenters, site/data/datacenters_public.json; docs/reviews/
// datacenters-public-rows-2026-10-23.md). datacenter_projects is held whole; this line counts its rows a public source
// stands behind (shown), the rows every evidence row of which asks for permission (held, "license needed", the
// catalogue's words, in place) and the rows resting on a publisher not read (unsettled), each a check key
// (dcpub|counts|<sort>; scripts/check-values.mjs reads the live set's row count against the file). Today no row is
// shown: every evidence row is a news outlet's that asks for permission. The rows a public source names are the
// interconnection-queue positions, which the power side below draws from the queue tables themselves (session 467).
type File = { retrieved: string; counts: { shown: number; held: number; unsettled: number }; shown: unknown[] };
const FILE = publicFile as unknown as File;

export const DC_COUNT_KEY = (sort: "shown" | "held" | "unsettled") => `dcpub|counts|${sort}`;

export function DatacentersPublicLine() {
  const c = FILE.counts;
  if (c.shown !== FILE.shown.length) return null;   // a file that does not describe itself is not drawn
  return (
    <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-datacenters-public="1" data-datacenters-public-retrieved={FILE.retrieved}>
      <strong>
        <Num check={DC_COUNT_KEY("held")} raw={c.held}>{count(c.held)}</Num> news facilities of <code className="font-mono">datacenter_projects</code> rest on
        publishers whose terms ask for permission; license needed.
      </strong>{" "}
      {c.unsettled ? (
        <><Num check={DC_COUNT_KEY("unsettled")} raw={c.unsettled}>{count(c.unsettled)}</Num> rest on a publisher whose terms have not been read.{" "}</>
      ) : null}
      <Num check={DC_COUNT_KEY("shown")} raw={c.shown}>{count(c.shown)}</Num> {c.shown === 1 ? "rests" : "rest"} on a source whose terms the ERW reads as public
      {c.shown ? ", and would be drawn with their power-side fields only" : ""}. The sites a public source names are the interconnection-queue positions,
      drawn from the queues themselves under &quot;On the power side&quot; below. Held from {LICENSE_FROM}; how a row is sorted:{" "}
      <Link href="/data/methods/datacenter_facilities" className="underline">the method note</Link>.
    </p>
  );
}
