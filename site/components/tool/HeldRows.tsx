// Energy Research Warehouse (ERW) site, session 500: the line a page draws beside the rows of a table held by row
// (session 499's reader, lib/license.ts licenseByRow; session 441's method). The page shows the rows whose own license
// is public, each with its source, and this line says how many rows of the table are held and why. Nothing of a held
// row is read: the count is PostgREST's count of the table's rows whose license is not public (check key
// held|<shape>|<table>|rows, recomputed by scripts/check-values.mjs). A table that is not held by row draws nothing,
// so until the data machine writes the column and the mark (warehouse/metadata/license_status.csv, `hold`) no page changes.
import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { heldRowCount } from "@/lib/data";
import { count } from "@/lib/format";
import { LICENSE_FROM, licenseByRow, licenseNeeded } from "@/lib/license";
import { attempt } from "@/lib/supabase";

export async function HeldRows({ shape, table, shown, method }: { shape: "events" | "entities"; table: string; shown: number; method: string }) {
  if (!licenseNeeded(table) || !licenseByRow(table)) return null;
  const n = await attempt(() => heldRowCount(shape, table));
  return (
    <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-held-rows={table}>
      <strong>Some rows are held for a license.</strong>{" "}
      {n.ok && n.data !== null ? (
        <><Num check={`held|${shape}|${table}|rows`} raw={n.data}>{count(n.data)}</Num> rows</>
      ) : (
        <>The other rows</>
      )}{" "}
      of <code className="font-mono">{table}</code> rest on a source whose own page asks for permission, which is not yet recorded, and are held
      from {LICENSE_FROM}. The {count(shown)} shown each rest on a source whose terms the ERW reads as public; each names its source. How a row is
      read: <Link href={method} className="underline">the method note</Link>.
    </p>
  );
}
