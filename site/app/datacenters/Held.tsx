import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { catalogue } from "@/lib/data";
import { count } from "@/lib/format";
import { LICENSE_FROM } from "@/lib/license";
import { attempt } from "@/lib/supabase";

// Session 1855 (chain 213, datacenter faults row 2): while datacenter_facilities is held for a license (lib/license.ts;
// the owner's ruling of 12 October 2026, from the day in warehouse/metadata/license_status.csv), the tracker says the
// hold once, as one sentence, where the facilities would be: how many rows, since when, why, and where the record of
// which rows rest on a public source is. The row count is the catalogue's (catalogue|datacenter_facilities|n_rows, a
// count of the table, not a row of it), as deals/Held.tsx does for energy_deals. Nothing of a held row is shown.
export async function FacilitiesHeld() {
  const cat = await attempt(catalogue);
  const row = cat.ok ? cat.data.find((r) => r.table_name === "datacenter_facilities") : undefined;
  return (
    <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-facilities-held="1">
      <strong>The hold covers every row of the table.</strong>{" "}
      {row && row.n_rows !== null ? (
        <>
          All <Num check="catalogue|datacenter_facilities|n_rows" raw={row.n_rows}>{count(row.n_rows)}</Num> rows of <code className="font-mono">datacenter_facilities</code> are
        </>
      ) : (
        <>Every row of <code className="font-mono">datacenter_facilities</code> is</>
      )}{" "}
      held from {LICENSE_FROM}: the facilities rest on news stories and the operators&apos; own pages, whose terms ask for permission, which is not yet
      recorded. So the list, the rollups by grid and operator, the timeline and the charts are not drawn; ERCOT&apos;s own large-load report and the
      sites the public queues name are below. Which rows rest on a source whose terms the ERW reads as public is counted in{" "}
      <Link href="/data/methods/datacenter_facilities" className="underline">the method note</Link>. The table on{" "}
      <Link href="/data#datacenter_facilities" className="underline">the data page</Link>.
    </p>
  );
}
