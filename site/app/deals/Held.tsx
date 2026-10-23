import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { catalogue } from "@/lib/data";
import { count } from "@/lib/format";
import { countKey, heldLine, type PublicDealsFile, publicCounts } from "@/lib/dealspublic";
import { LICENSE_FROM } from "@/lib/license";
import { attempt } from "@/lib/supabase";

// Session 465: while energy_deals is held for a license (lib/license.ts; the owner's ruling of 12 October 2026, in
// force from the day in warehouse/metadata/license_status.csv), the deal pages show the catalogue's words where a deal
// would be. This says how many rows the hold covers, from the catalogue's row count (a count of the table, not a row of
// it: catalogue|energy_deals|n_rows, the key /data shows), and where the record of which rows rest on a public source
// alone is. Nothing of a held row is shown.
//
// Session 822: with the public rows' file (lib/dealspublic.ts, site/data/deals_public.json), the line counts the three
// sorts instead: the deals held (each rests only on publishers whose terms ask for permission: "license needed", the
// catalogue's words, in place), the deals unsettled (a publisher not read) and the deals shown below, each count a
// check key (dealpub|counts|<sort>; scripts/check-values.mjs reads the live set's row count against the file). The
// held rows are a count and nothing else: no held row's name comes from a public filing today, so none is drawn.
export async function DealsHeld({ file }: { file?: PublicDealsFile }) {
  if (file) {
    const c = publicCounts(file);
    const words = heldLine(c);
    return (
      <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-deals-held="rows" data-deals-public-retrieved={file.retrieved}>
        <strong>
          <Num check={countKey("held")} raw={c.held}>{count(c.held)}</Num> {words.held}
        </strong>{" "}
        {c.unsettled ? (
          <>
            <Num check={countKey("unsettled")} raw={c.unsettled}>{count(c.unsettled)}</Num> {words.unsettled}{" "}
          </>
        ) : null}
        <Num check={countKey("shown")} raw={c.shown}>{count(c.shown)}</Num> {words.shown} The held and unsettled rows are counted from the
        table&apos;s evidence rows, held from {LICENSE_FROM}: each deal was extracted from news stories, and most outlets&apos; own pages ask for
        permission, which is not yet recorded. How a row is sorted: <Link href="/data/methods/energy_deals" className="underline">the method note</Link>.
        The table on <Link href="/data#energy_deals" className="underline">the data page</Link>.
      </p>
    );
  }
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
