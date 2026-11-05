import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { catalogue } from "@/lib/data";
import { count } from "@/lib/format";
import { LICENSE_FROM } from "@/lib/license";
import { attempt } from "@/lib/supabase";

// Session 465: while energy_deals is held for a license (lib/license.ts; the owner's ruling of 12 October 2026, in
// force from the day in warehouse/metadata/license_status.csv), the deal pages show the catalogue's words where a deal
// would be. This says how many rows the hold covers, from the catalogue's row count (a count of the table, not a row of
// it: catalogue|energy_deals|n_rows, the key /data shows), and where the record of which rows rest on a public source
// alone is. Nothing of a held row is shown.
export async function DealsHeld() {
  const cat = await attempt(catalogue);
  const row = cat.ok ? cat.data.find((r) => r.table_name === "energy_deals") : undefined;
  return (
    <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-deals-held="1">
      <strong>The hold covers every row of the table.</strong>{" "}
      {row && row.n_rows !== null ? (
        <>
          All <Num check="catalogue|energy_deals|n_rows" raw={row.n_rows}>{count(row.n_rows)}</Num> rows of <code className="font-mono">energy_deals</code> are
        </>
      ) : (
        <>Every row of <code className="font-mono">energy_deals</code> is</>
      )}{" "}
      held from {LICENSE_FROM}: each deal was extracted from news stories, and the outlets&apos; own pages ask for permission, which is not yet
      recorded. Which rows rest on a source whose terms the ERW reads as public is counted in{" "}
      <Link href="/data/methods/energy_deals" className="underline">the method note</Link>; showing those rows alone waits for a license column a
      row and a ruling. The table on <Link href="/data#energy_deals" className="underline">the data page</Link>.
    </p>
  );
}
