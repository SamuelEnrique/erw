import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { catalogue } from "@/lib/data";
import { count, day, utc } from "@/lib/format";
import { DOCS, render } from "@/lib/markdown";
import { attempt } from "@/lib/supabase";
import site from "@/data/site.json";
import { PAGES } from "@/lib/pages";
import { TIER_LABEL, TIER_TITLE, isModelExtracted } from "@/lib/tiers";
import { LICENSE_NEEDED, licenseNeeded, licensePublishers } from "@/lib/license";  // session 207: "license needed" from 20 October 2026

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
    <Brand>
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
                  <th className="py-1 pr-3 font-normal">Refreshed (UTC)</th>
                  <th className="py-1 pr-3 text-right font-normal">Rows</th>
                  <th className="py-1 pr-3 font-normal">Source report</th>
                  <th className="py-1 pr-3 font-normal">License</th>
                  <th className="py-1 pr-3 font-normal">Tier</th>
                  <th className="py-1 pr-3 font-normal">Download</th>
                </tr>
              </thead>
              <tbody>
                {cat.data.map((r) => (
                  <tr key={r.table_name} id={r.table_name} className="border-b border-rule/60 align-top target:bg-panel">
                    {/* session 416: the table's name is the row's header, a th, so that it stays in place beside its column's
                        head when the figures scroll sideways on a phone (tokens.css keeps a first th in place, not a td) */}
                    <th scope="row" className="py-1 pr-3 text-left align-top font-mono text-xs font-normal">
                      {r.table_name}
                      {r.derived === "yes" ? <span className="ml-1 font-sans text-muted">(derived)</span> : null}
                    </th>
                    <td className="py-1 pr-3 text-xs">{(r.sector ?? "").split(";").join(", ")}</td>
                    <td className="py-1 pr-3 text-xs">{r.interval}</td>
                    <td className="py-1 pr-3 text-xs whitespace-nowrap">{day(r.ts_min)}</td>
                    <td className="py-1 pr-3 text-xs whitespace-nowrap">{day(r.ts_max)}</td>
                    {/* session 410: the table's last run, coverage.csv's last_run as the loader put it in the catalogue */}
                    <td className="py-1 pr-3 text-xs whitespace-nowrap" title={r.last_run ? utc(r.last_run) : undefined}>
                      {r.last_run ? day(r.last_run) : <span className="text-muted" title="coverage.csv records no run for this table">not recorded</span>}
                    </td>
                    <td className="py-1 pr-3 text-right tabular-nums">
                      <Num check={`catalogue|${r.table_name}|n_rows`} raw={r.n_rows ?? ""}>
                        {count(r.n_rows)}
                      </Num>
                    </td>
                    <td className="py-1 pr-3 font-mono text-xs break-all">{r.source_report}</td>
                    <td className="py-1 pr-3 text-xs">
                      {licenseNeeded(r.table_name) ? (
                        <span title={`${licensePublishers(r.table_name).join("; ")}: the publisher's own page asks for permission; none is recorded yet`}>{LICENSE_NEEDED}</span>
                      ) : (
                        r.license
                      )}
                    </td>
                    <td className="py-1 pr-3 text-xs whitespace-nowrap" title={r.tier ? TIER_TITLE[r.tier] : undefined}>
                      {r.tier ? (isModelExtracted(r.tier) ? <strong className="font-normal text-accent">{TIER_LABEL[r.tier]}</strong> : TIER_LABEL[r.tier] ?? r.tier) : ""}
                    </td>
                    <td className="py-1 pr-3 text-xs whitespace-nowrap">
                      {licenseNeeded(r.table_name) ? (
                        <span className="text-muted">Held: license needed</span>
                      ) : r.in_live_set === "yes" ? (
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
        <Cite tables={["catalogue"]} note="Freq is the interval between rows (ISO 8601 duration); snapshot means an entities table. First and Last are the first and last row; Refreshed is the day of the table's last run" />
        <p className="mt-2 max-w-3xl text-xs text-muted">
          Tier (session 28) is where a table&apos;s numbers come from: <strong className="font-normal">source</strong>, as the publisher published them;{" "}
          <strong className="font-normal">derived</strong>, computed by the ERW from other tables, with a method in the methods pages; or{" "}
          <strong className="font-normal text-accent">model-extracted</strong>, where at least one field was written by a model reading news, filings or the
          web, not published by a source. Cite a model-extracted number with its linked source. The rules are in the{" "}
          <Link href="/data/standard">data standard</Link>.
        </p>
        <p className="mt-2 max-w-3xl text-xs text-muted">
          Download CSV gives the rows the site&apos;s live set holds, with the table&apos;s provenance header lines at the top, up to 500,000 rows; for a table
          the live set keeps a window of (such as the last 35 days of prices), that window. The full history of every table, and the tables not in the
          live set, are on <a href={site.redivis.url}>Redivis</a>, where version 1 is pending release.
        </p>
        {/* session 312: the citation line of release v1 (docs/redivis/release-v1.md, "How to cite v1"); the date is added at the click */}
        <p className="mt-2 max-w-3xl text-xs text-muted">
          How to cite a table: the publisher, the report, then &ldquo;via the Energy Research Warehouse (ERW), table{" "}
          <code className="font-mono">&lt;table&gt;</code>, Redivis dataset <code className="font-mono">energy_research_warehouse</code>, version v1&rdquo;,
          with the date of the release. Version: v1, pending release; each table&apos;s own line is in the release&apos;s{" "}
          <a href="https://github.com/SamuelEnrique/erw/blob/main/docs/redivis/release-v1/tables.csv">table list</a>.
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
              the last 35 days of power prices, demand, generation and emissions, other windows of the daily curtailment, trader and retail sales tables, and the derived,
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
    </Brand>
  );
}
