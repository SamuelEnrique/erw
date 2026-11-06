// Energy Research Warehouse (ERW) site, session 3305 (chain 200): one company of the company database (platform tool 10).
// What the warehouse holds about it, from site/data/companies/c/<xx>.json (warehouse/derived/companies_page.py): its
// figures, its MW by fuel and by year, its names and every public row that names it, each figure keyed to its table,
// row and column (data-n; scripts/check-companies.mjs reads them back) with its source as the hover. The company's
// facts on the left, what it holds on the right; what a figure means is a hover tip. A table held for a license
// (energy_deals, the datacenter tables, the NYISO queue) shows the count of its rows, never a row or a figure.
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, HeadlineNumber, InputPanel, SourceLine, Tip, ToolHeader, ToolPage, ToolSection } from "@/components/tool/ToolPage";
import { GroupedBars } from "@/components/tool/GroupedBars";
import { ROLE_WORDS, TABLE_WORDS, count, linksOf, mw, yearGroups, type Company, type CompanyIndex, type Link as Row } from "@/lib/companydb";
import { company, companyIndex } from "@/lib/companydata";

export const dynamic = "force-dynamic";
const SHOWN = 100;   // rows a table shows on the page; every public row is in the download
const FUEL_ORDER = ["solar", "wind", "gas", "coal", "nuclear", "hydro", "storage", "oil", "geothermal", "other"];

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  let name = "Company";
  try { name = company(id)?.name ?? name; } catch { /* the page says so */ }
  return { title: name, robots: { index: false, follow: false } };
}

function K({ c, col, raw, source, children }: { c: Company; col: string; raw: number | string; source: string; children: React.ReactNode }) {
  return <span data-n={`company_directory|${c.entity_id}|${col}`} data-raw={String(raw)} title={source}>{children}</span>;
}

function Fact({ label, children, tip }: { label: string; children: React.ReactNode; tip?: React.ReactNode }) {
  return (
    <div className="mb-2">
      <dt className="text-xs uppercase tracking-wide text-muted">{label}{tip ? <span className="normal-case tracking-normal">{tip}</span> : null}</dt>
      <dd className="text-sm">{children}</dd>
    </div>
  );
}

function rowsTable(c: Company, table: string, rows: Row[], ix: CompanyIndex) {
  const src = ix.sources[table] ?? "";
  const shown = [...rows].sort((x, y) => y.date.localeCompare(x.date) || x.row.localeCompare(y.row)).slice(0, SHOWN);
  const hasMw = rows.some((r) => r.mw !== "");
  const hasUsd = rows.some((r) => r.usd !== "");
  return (
    <section key={table} id={`rows-${table}`} className="mb-8" data-rows-table={table} data-rows={rows.length}>
      <h3 className="mb-2 font-serif text-lg text-accent">{TABLE_WORDS[table] ?? table} <span className="font-sans text-xs text-muted">{count(rows.length)} rows</span>
        <Tip id={`src-${table}`} label={`Source of ${table}`}>{`${table}. Source: ${src}`}</Tip></h3>
      <div className="overflow-x-auto" role="region" aria-label={`${TABLE_WORDS[table] ?? table} rows`} tabIndex={0}>
        <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 640 }}>
          <caption className="sr-only">{`Rows of ${table} that name ${c.name}`}</caption>
          <thead>
            <tr className="bg-accent text-white">
              <th scope="col" className="px-3 py-1.5 font-normal">Row</th>
              <th scope="col" className="px-3 py-1.5 font-normal">Role</th>
              <th scope="col" className="px-3 py-1.5 font-normal">Name as written</th>
              <th scope="col" className="px-3 py-1.5 font-normal">Date</th>
              <th scope="col" className="px-3 py-1.5 font-normal">Detail</th>
              {hasMw ? <th scope="col" className="px-3 py-1.5 text-right font-normal">MW</th> : null}
              {hasUsd ? <th scope="col" className="px-3 py-1.5 text-right font-normal">USD</th> : null}
              <th scope="col" className="px-3 py-1.5 text-right font-normal">Match</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((r) => (
              <tr key={r.link} className="border-b border-rule" data-link={r.link}>
                <th scope="row" className="px-3 py-1.5 font-mono text-xs font-normal" title={`${table} ${r.row}. Source: ${src}`}>{r.row}</th>
                <td className="px-3 py-1.5">{ROLE_WORDS[r.role] ?? r.role}</td>
                <td className="px-3 py-1.5">{r.name}</td>
                <td className="px-3 py-1.5">{r.date}</td>
                <td className="px-3 py-1.5">{[r.fuel, r.state, r.grid, r.detail].filter(Boolean).join(", ")}</td>
                {hasMw ? <td className="px-3 py-1.5 text-right">{r.mw !== "" ? <span data-n={`company_links|${r.link}|mw`} data-raw={r.mw} title={`${table} ${r.row}. Source: ${src}`}>{Number(r.mw).toLocaleString("en-US", { maximumFractionDigits: 1 })}</span> : ""}</td> : null}
                {hasUsd ? <td className="px-3 py-1.5 text-right">{r.usd !== "" ? <span data-n={`company_links|${r.link}|usd`} data-raw={r.usd} title={`${table} ${r.row}. Source: ${src}`}>{Number(r.usd).toLocaleString("en-US")}</span> : ""}</td> : null}
                <td className="px-3 py-1.5 text-right text-xs" title={`Matched by the rule ${r.rule} (confidence ${r.confidence}); docs/methods/companies.md`}>{r.confidence.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length > SHOWN ? <p className="mt-1 text-xs text-muted" data-rows-more={rows.length - SHOWN}>The newest {SHOWN} of {count(rows.length)} by date; every row is in the download.</p> : null}
    </section>
  );
}

export default async function CompanyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let ix: CompanyIndex;
  let c: Company | null;
  try {
    ix = companyIndex();
    c = company(id);
  } catch {
    return (
      <ToolPage>
        <ToolHeader title="Company" crumb={<Link href="/companies">Companies</Link>} />
        <p className="text-sm" data-companies-unread="1">The company database&apos;s file could not be read; the tables are on <Link href="/data">Data and methods</Link>.</p>
      </ToolPage>
    );
  }
  if (!c) notFound();
  const links = linksOf(c, ix);
  const byTable = new Map<string, Row[]>();
  for (const l of links) byTable.set(l.table, [...(byTable.get(l.table) ?? []), l]);
  const f = c.figures;
  const fromRows = (col: string, t: string) => `company_directory, ${col}: the sum of ${count(byTable.get(t)?.length ?? 0)} rows of company_links from ${t}. Source: ${ix.sources[t] ?? ""}`;
  const held = Object.entries(c.held);
  const groups = yearGroups(c.years);
  const fuels = FUEL_ORDER.filter((k) => (c.fuel[k] ?? 0) > 0);
  const dealsHeld = ix.held_tables.includes("energy_deals");
  const heads: { label: string; col: string; v: number; unit?: string; t: string; tip: string }[] = [
    { label: "Operating", col: "plants_mw", v: f.plants_mw, unit: "MW", t: "eia860m_operating_generators", tip: `Nameplate MW of the ${count(f.n_generators)} operating generators at ${count(f.n_plants)} plants it operates (EIA-860M).` },
    { label: "Planned", col: "planned_mw", v: f.planned_mw, unit: "MW", t: "eia860m_planned_generators", tip: `Nameplate MW of planned generators at ${count(f.n_planned_plants)} plants it would operate (EIA-860M).` },
    { label: "Owned share", col: "owned_mw", v: f.owned_mw, unit: "MW", t: "eia860_generator_owners", tip: `Nameplate MW times the percent owned, of ${count(f.n_owned_generators)} jointly owned generators (EIA-860 schedule 4 lists only those).` },
    { label: "ERCOT queue", col: "queue_mw", v: f.queue_mw, unit: "MW", t: "ercot_interconnection_queue", tip: `MW of ${count(f.n_queue)} ERCOT queue positions neither withdrawn nor completed, as the queue states them.` },
    { label: "Reactors", col: "n_reactors", v: f.n_reactors, t: "nrc_power_reactors", tip: `NRC power reactors it is the licensee or operator of: ${mw(f.reactors_mw)} MW as the NRC states them.` },
    { label: "Policy actions", col: "n_policy_actions", v: f.n_policy_actions, t: "policy_actions", tip: "Policy actions (Federal Register and agency news) that name it as an agency." },
  ].filter((h) => h.v > 0);
  return (
    <ToolPage>
      <ToolHeader
        title={c.name}
        crumb={<><Link href="/companies">Companies</Link> <span aria-hidden="true">/</span> {c.kind}</>}
        lead={<>{c.kind}{c.segment ? `, ${c.segment}` : ""}{c.states.length ? `, in ${c.states.slice(0, 6).join(", ")}${c.states.length > 6 ? ` and ${c.states.length - 6} more states` : ""}` : ""}. {count(links.length)} public rows of {byTable.size} tables name it{held.length ? `; ${count(held.reduce((s, [, n]) => s + n, 0))} held rows do too` : ""}.</>}
      />
      <div className="grid gap-8 lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="This company">
            <dl>
              <Fact label="Kind" tip={<Tip id="c-kind" label="How the kind was set">{`Set by: ${c.kind_basis}. The first of regulator, lab or hyperscaler, OEM, utility, IPP, lender or investor, developer, operator, other that its rows show.`}</Tip>}>{c.kind}</Fact>
              {c.segment ? <Fact label="Segment" tip={<Tip id="c-seg" label="How the segment was set">{`By ${c.segment_basis || "kind"}: the fuel or line with the most MW across its plants, plans and queue positions.`}</Tip>}>{c.segment}</Fact> : null}
              {c.parent ? <Fact label="Parent" tip={<Tip id="c-parent" label="Where the parent is stated">{`Stated by ${c.parent_basis}. A parent is a second field, never in place of the name.`}</Tip>}>{c.parent_id ? <Link href={`/companies/${c.parent_id}`}>{c.parent}</Link> : c.parent}</Fact> : null}
              {c.eia_utility_id ? <Fact label="EIA utility id" tip={<Tip id="c-eia" label="The EIA id">Every row carrying this id in EIA-860, EIA-860M and EIA-861 is this company, whatever name the row gives it.</Tip>}><span className="font-mono">{c.eia_utility_id}</span></Fact> : null}
              {c.hq_state ? <Fact label="Headquarters state" tip={<Tip id="c-hq" label="Where the state is stated">{c.hq_basis}: the state of the owner&apos;s address in EIA-860&apos;s owner schedule.</Tip>}>{c.hq_state}</Fact> : null}
              {c.grids.length ? <Fact label="Grids">{c.grids.join(", ")}</Fact> : null}
              {c.first_seen ? <Fact label="Seen" tip={<Tip id="c-seen" label="First and last seen">The earliest and latest date its public rows state: a generator&apos;s first month, a queue date, a policy action&apos;s date, an EIA-861 year.</Tip>}>{c.first_seen} to {c.last_seen}</Fact> : null}
              <Fact label="Match" tip={<Tip id="c-match" label="The weakest match">The lowest confidence of the rules that matched its rows: 1.0 an EIA id, 0.95 a reviewed alias, 0.9 an anchored name, 0.85 a name, 0.7 a company word added.</Tip>}>{c.min_confidence.toFixed(2)}</Fact>
            </dl>
            <nav aria-label="Its rows" className="mt-3 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Its rows</div>
              {Array.from(byTable.entries()).map(([t, r]) => <div key={t}><a href={`#rows-${t}`}>{TABLE_WORDS[t] ?? t}</a> <span className="text-xs text-muted">{count(r.length)}</span></div>)}
              {held.map(([t, n]) => <div key={t} className="text-muted" data-held-table={t}>{TABLE_WORDS[t] ?? t} <span className="text-xs">{count(n)}, held<Tip id={`held-${t}`} label={`${t} is held`}>License needed: the publishers ask for permission, not yet recorded (warehouse/metadata/license_status.csv). The rows are counted, never shown.</Tip></span></div>)}
            </nav>
          </InputPanel>
          <p className="mt-3 text-xs leading-relaxed text-muted" data-downloads="company">
            Download its public rows: <a href={`/companies/${c.id}/rows`} download data-download="csv">CSV</a>, <a href={`/companies/${c.id}/rows/python`} download data-download="python">Python</a>, <a href={`/companies/${c.id}/rows/stata`} download data-download="stata">Stata</a>.
          </p>
        </aside>
        <div>
          {heads.length ? (
            <div className="mb-10 grid gap-6 sm:grid-cols-3">
              {heads.map((h) => (
                <HeadlineNumber key={h.col} label={h.label} unit={h.unit}
                  tip={<Tip id={`h-${h.col}`} label={h.label}>{h.tip}</Tip>}
                  value={<K c={c} col={h.col} raw={h.v} source={fromRows(h.col, h.t)}>{h.unit ? mw(h.v) : count(h.v)}</K>} />
              ))}
            </div>
          ) : null}
          {fuels.length ? (
            <ToolSection title="Operating MW by fuel">
              <div className="overflow-x-auto" role="region" aria-label="Operating MW by fuel" tabIndex={0}>
                <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 320 }}>
                  <caption className="sr-only">Operating nameplate MW by fuel</caption>
                  <thead><tr className="bg-accent text-white"><th scope="col" className="px-3 py-1.5 font-normal">Fuel</th><th scope="col" className="px-3 py-1.5 text-right font-normal">MW</th><th scope="col" className="px-3 py-1.5 text-right font-normal">Share</th></tr></thead>
                  <tbody>
                    {fuels.map((k) => (
                      <tr key={k} className="border-b border-rule">
                        <th scope="row" className="px-3 py-1.5 font-normal">{k}</th>
                        <td className="px-3 py-1.5 text-right"><K c={c} col={`mw_${k}`} raw={c.fuel[k]} source={fromRows(`mw_${k}`, "eia860m_operating_generators")}>{mw(c.fuel[k])}</K></td>
                        <td className="px-3 py-1.5 text-right">{f.plants_mw ? `${((c.fuel[k] / f.plants_mw) * 100).toFixed(1)}%` : ""}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </ToolSection>
          ) : null}
          {groups.length ? (
            <ChartFrame title="MW by year" legend={[{ label: "Operating, by first month", color: "var(--color-accent)" }, { label: "Planned, by planned month", color: "var(--color-ink)" }, { label: "ERCOT queue, by queue date", color: "var(--color-muted)" }]}
              tip={<Tip id="c-years" label="The years">{`Nameplate MW of its operating generators by the year each began, of its planned generators by the year planned, and of its live ERCOT queue positions by the year each entered the queue.${groups[0].label.includes(" to ") ? " Its years are many, so each bar is five years." : ""}`}</Tip>}>
              <GroupedBars id={`years-${c.id}`} unit="MW" label={`${c.name}: MW by year`} series={[{ name: "Operating", tone: "accent" }, { name: "Planned", tone: "ink" }, { name: "ERCOT queue", tone: "muted" }]}
                groups={groups.map((g) => ({ label: g.label, values: [g.operating, g.planned, g.queue], title: `${g.label}: ${mw(g.operating)} MW operating, ${mw(g.planned)} MW planned, ${mw(g.queue)} MW in the ERCOT queue` }))} />
            </ChartFrame>
          ) : null}
          <ChartFrame title="Deals by quarter" tip={<Tip id="c-deals" label="The deals">Deals from the deal tracker (energy_deals) that name it, by the quarter of the deal&apos;s date: the count, the MW and the USD the stories state.</Tip>}>
            {dealsHeld ? (
              <p className="border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-deals-held="company">
                {c.held.energy_deals ? <>{count(c.held.energy_deals)} rows of <code className="font-mono">energy_deals</code> name this company; </> : <>No row of <code className="font-mono">energy_deals</code> names this company; </>}
                the table is held for a license, so no deal is drawn.
              </p>
            ) : c.quarters.length ? (
              <GroupedBars id={`deals-${c.id}`} unit="deals" label={`${c.name}: deals by quarter`} series={[{ name: "Deals", tone: "accent" }]}
                groups={c.quarters.map(([q, n, m, u]) => ({ label: q, values: [n], title: `${q}: ${n} deals, ${mw(m)} MW and USD ${mw(u)} stated` }))} />
            ) : <p className="text-sm text-muted" data-deals-none="1">No deal names this company.</p>}
          </ChartFrame>
          <ToolSection title="Its rows">
            {Array.from(byTable.entries()).map(([t, r]) => rowsTable(c, t, r, ix))}
          </ToolSection>
          {c.names.length > 1 ? (
            <ToolSection title="Its names">
              <ul className="text-sm" data-names={c.names.length}>
                {c.names.map(([n, t, role, k, rule]) => <li key={`${n}|${t}|${role}`}>{n} <span className="text-xs text-muted">{TABLE_WORDS[t] ?? t}, {ROLE_WORDS[role] ?? role}, {count(k)} rows, {rule}</span></li>)}
              </ul>
            </ToolSection>
          ) : null}
          <SourceLine tables={["company_directory", "company_aliases", "company_links", ...Array.from(byTable.keys())]} note={<>Built {ix.built.slice(0, 10)}; the method is <Link href="/data/methods/companies">docs/methods/companies.md</Link>.</>} />
        </div>
      </div>
    </ToolPage>
  );
}
