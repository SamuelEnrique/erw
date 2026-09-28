import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { catalogue } from "@/lib/data";
import { count, day } from "@/lib/format";
import { DOCS, render } from "@/lib/markdown";
import { attempt } from "@/lib/supabase";
import site from "@/data/site.json";
import { PAGES } from "@/lib/pages";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Data" };

function title(md: string): string {
  const m = md.match(/^#\s+(.+)$/m);
  return m ? m[1].trim() : "";
}

/** The data standard's three shape sections (series, entities, events), for the data dictionary. */
function dictionary(md: string): string {
  const a = md.indexOf("## Shape (a)");
  const b = md.indexOf("## Decisions", a);
  return a < 0 ? "" : md.slice(a, b < 0 ? undefined : b).replace(/^## /gm, "### ");
}

export default async function Data() {
  const cat = await attempt(catalogue);
  return (
    <>
      <h1 className="mb-1 text-3xl">Data</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        Every public table in the ERW. Each table is one of three shapes (series, entities, events), in UTC, with the source report
        and retrieval time of every row. Internal tables, licensed for internal use only, are not listed.
      </p>

      <Section title="Coverage" id="coverage" aside={cat.ok ? <>{count(cat.data.length)} public tables</> : null}>
        {!cat.ok ? (
          <NoData what="the coverage table" reason={cat.reason} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-rule text-left text-xs text-muted">
                  <th className="py-1 pr-3 font-normal">Table</th>
                  <th className="py-1 pr-3 font-normal">Sector</th>
                  <th className="py-1 pr-3 font-normal">Freq</th>
                  <th className="py-1 pr-3 font-normal">First (UTC)</th>
                  <th className="py-1 pr-3 font-normal">Last (UTC)</th>
                  <th className="py-1 pr-3 text-right font-normal">Rows</th>
                  <th className="py-1 pr-3 font-normal">Source report</th>
                  <th className="py-1 pr-3 font-normal">License</th>
                  <th className="py-1 pr-3 font-normal">Download</th>
                </tr>
              </thead>
              <tbody>
                {cat.data.map((r) => (
                  <tr key={r.table_name} id={r.table_name} className="border-b border-rule/60 align-top target:bg-panel">
                    <td className="py-1 pr-3 font-mono text-xs">
                      {r.table_name}
                      {r.derived === "yes" ? <span className="ml-1 font-sans text-muted">(derived)</span> : null}
                    </td>
                    <td className="py-1 pr-3 text-xs">{(r.sector ?? "").split(";").join(", ")}</td>
                    <td className="py-1 pr-3 text-xs">{r.interval}</td>
                    <td className="py-1 pr-3 text-xs whitespace-nowrap">{day(r.ts_min)}</td>
                    <td className="py-1 pr-3 text-xs whitespace-nowrap">{day(r.ts_max)}</td>
                    <td className="py-1 pr-3 text-right tabular-nums">
                      <Num check={`catalogue|${r.table_name}|n_rows`} raw={r.n_rows ?? ""}>
                        {count(r.n_rows)}
                      </Num>
                    </td>
                    <td className="py-1 pr-3 font-mono text-xs break-all">{r.source_report}</td>
                    <td className="py-1 pr-3 text-xs">{r.license}</td>
                    <td className="py-1 pr-3 text-xs whitespace-nowrap">
                      {r.in_live_set === "yes" ? (
                        <a href={`/api/download?table=${r.table_name}`}>Download CSV</a>
                      ) : (
                        <a href={site.redivis.url} title="On Redivis; version 1 is pending release">
                          Redivis
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <Cite tables={["catalogue"]} note="Freq is the interval between rows (ISO 8601 duration); snapshot means an entities table. Dates are the first and last row" />
        <p className="mt-2 max-w-3xl text-xs text-muted">
          Download CSV gives the rows the site&apos;s live set holds, with the table&apos;s provenance header lines at the top, up to 200,000 rows; for a table
          the live set keeps a window of (such as the last 90 days of prices), that window. The full history of every table, and the tables not in the
          live set, are on <a href={site.redivis.url}>Redivis</a>, where version 1 is pending release.
        </p>
      </Section>

      <Section title="Pages" id="pages">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-3 font-normal">Page</th>
                <th className="py-1 pr-3 font-normal">What it shows</th>
                <th className="py-1 pr-3 font-normal">Tables it reads</th>
              </tr>
            </thead>
            <tbody>
              {PAGES.map((p) => (
                <tr key={p.href} className="border-b border-rule/60 align-top">
                  <td className="py-1 pr-3 whitespace-nowrap">
                    <Link href={p.href}>{p.label}</Link>
                  </td>
                  <td className="py-1 pr-3">{p.line}</td>
                  <td className="py-1 pr-3 font-mono text-xs">{p.tables}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section title="Access" id="access">
        <div className="grid gap-6 md:grid-cols-2 [&>*]:min-w-0">
          <div>
            <h3 className="mb-1 text-lg">Redivis, the store of record</h3>
            <p className="mb-2 text-sm">
              Every ERW table, full history, versioned:{" "}
              <a href={site.redivis.url}>
                <code className="font-mono">{site.redivis.dataset}</code> on Redivis
              </a>
              .
            </p>
            <p className="text-xs text-muted">
              {site.redivis.status} (Checked {site.redivis.checked}.) This site reads a live subset of the public tables (<code className="font-mono">warehouse/supabase/live_set.yaml</code>):
              the last 90 days of power prices and demand, shorter windows of the daily curtailment, trader and retail sales tables, and the derived,
              fuel, project, queue, deal and news tables whole. The ERCOT yearly history and the EIA-860M operating and planned generator tables are on
              Redivis only; the project map carries every operating and planned generator.
            </p>
          </div>
          <div>
            <h3 className="mb-1 text-lg">The erw Python package</h3>
            <pre className="overflow-x-auto border border-rule bg-panel p-2 font-mono text-xs">{site.package.install.join("\n")}</pre>
            <p className="mt-2 text-xs text-muted">
              {site.package.note} <a href={site.package.readme}>Package README</a>.
            </p>
            <p className="mt-2 text-xs text-muted">From a clone, which reads the clone&apos;s own tables:</p>
            <pre className="mt-1 overflow-x-auto border border-rule bg-panel p-2 font-mono text-xs">{site.package.clone_install.join("\n")}</pre>
          </div>
        </div>
      </Section>

      <Section title="Data dictionary" id="dictionary">
        <p className="mb-3 max-w-3xl text-sm text-muted">
          Every ERW table is one of three shapes. Their columns, from the <Link href="/data/standard">data standard</Link>:
        </p>
        <div className="prose-erw max-w-none overflow-x-auto text-sm" dangerouslySetInnerHTML={{ __html: render(dictionary(DOCS.datastandard), "docs/datastandard.md") }} />
      </Section>

      <Section title="Methodology" id="methods">
        <ul className="list-disc pl-5 text-sm">
          <li>
            <Link href="/data/standard">{title(DOCS.datastandard) || "The ERW data standard"}</Link>: table shapes, column names, units, timestamps, licenses and
            file naming.
          </li>
          {Object.entries(DOCS.methods).map(([slug, md]) => (
            <li key={slug}>
              <Link href={`/data/methods/${slug}`}>{title(md) || slug}</Link>
            </li>
          ))}
        </ul>
      </Section>
    </>
  );
}
