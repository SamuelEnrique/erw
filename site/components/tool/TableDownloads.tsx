// Energy Research Warehouse (ERW) site, session 328 (roadmap v3 of 13 October 2026: every other page finished to the
// five tools' standard, lighter): the downloads of a page's public tables. Each ERW table the page reads, as the live
// set's CSV (/api/download, session 21) with a Python and a Stata reader of that same CSV (?as=py, ?as=do): a reader
// fetches the file, keeps its "#" provenance lines and loads the rows as they are, so every number the page shows from
// that table is in what it loads. A table held for a license, or not in the live set, says so, as /data says it; a
// name that is not a public ERW table is left out. A failed catalogue read sends the reader to /data.
import { SiteLink as Link } from "@/components/SiteLink";
import { catalogue } from "@/lib/data";
import { licenseNeeded } from "@/lib/license";
import { attempt } from "@/lib/supabase";
import site from "@/data/site.json";

export async function TableDownloads({ tables }: { tables: string[] }) {
  const cat = await attempt(catalogue);
  const live = new Map(cat.ok ? cat.data.map((r) => [r.table_name, r.in_live_set]) : []);
  const shown = Array.from(new Set(tables)).filter((t) => live.has(t));
  return (
    <p className="mt-3 text-xs leading-relaxed text-muted" data-downloads={cat.ok ? shown.length : "unread"}>
      Download the tables:{" "}
      {!cat.ok || !shown.length ? (
        <>every public table is on <Link href="/data">Data and methods</Link></>
      ) : (
        shown.map((t, i) => (
          <span key={t} data-download-table={t}>
            {i ? "; " : ""}
            <code className="font-mono">{t}</code>{" "}
            {licenseNeeded(t) ? (
              <span data-not-held="license">held: license needed</span>
            ) : live.get(t) === "yes" ? (
              <>
                <a href={`/api/download?table=${t}`} download data-download="csv">CSV</a>,{" "}
                <a href={`/api/download?table=${t}&as=py`} download data-download="python">Python</a>,{" "}
                <a href={`/api/download?table=${t}&as=do`} download data-download="stata">Stata</a>
              </>
            ) : (
              <a href={site.redivis.url} data-not-held="live-set" title="Not in the site's live set: on Redivis, version 1 pending release">on Redivis</a>
            )}
          </span>
        ))
      )}
      .
    </p>
  );
}
