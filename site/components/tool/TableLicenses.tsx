// Energy Research Warehouse (ERW) site, session 502 (roadmap v4 draft, item 6: each live view states what it holds and
// under which license): one line under a page's title naming the ERW tables the page reads and each one's license, in
// the downloads line's form (components/tool/TableDownloads.tsx). The verdict is the record's: a table of
// warehouse/metadata/license_status.csv that is "license needed" on the day is named as held (whole, or for the grids that
// decide it, as lib/license.ts holds it); every other table a page reads is public in coverage.csv (tests/test_session502.py
// checks each list against it). No read of the live set: the line is the same when the database is slow. No link to
// /data/licenses (session 471 put that link to Samuel).
import { licenseTitle, licenseWords } from "@/lib/license";

export function TableLicenses({ tables, now }: { tables: readonly string[]; now?: Date }) {
  const list = Array.from(new Set(tables));
  return (
    <p className="mt-2 text-xs leading-relaxed text-muted" data-licenses={list.length}>
      Tables read, with their licenses:{" "}
      {list.map((t, i) => {
        const words = licenseWords(t, now);
        return (
          <span key={t} data-license-table={t} data-license={words === "public" ? "public" : "held"} title={words === "public" ? undefined : licenseTitle(t)}>
            {i ? "; " : ""}
            <code className="font-mono">{t}</code> {words}
          </span>
        );
      })}
      .
    </p>
  );
}
