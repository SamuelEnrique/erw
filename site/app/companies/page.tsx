// Energy Research Warehouse (ERW) site, session 3304 (chain 200): the company database (platform tool 10), its index.
// Every company the warehouse names in a public row (company_directory, warehouse/derived/companies.py), searched and
// filtered on the server from site/data/companies/index.json (warehouse/derived/companies_page.py), the largest
// footprint first. The query is the address (a GET form: it works without script). The choices on the left, the
// companies on the right; what a column means is a hover tip. A table held for a license (energy_deals, the datacenter
// tables, the NYISO queue) adds no row, no name and no figure here: its rows are counted. Until session 3304 this
// address redirected to the deals page's Companies tab (energy_companies), which stays at /deals?tab=companies.
import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";
import { InputPanel, SourceLine, Tip, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { KIND_ORDER, PAGE_SIZE, SORTS, filterRows, hrefOf, idTag, indexRows, mw, count, pageOf, plural, queryOf, sharedNames, stateLabel, statesCell, type CompanyIndex, type IndexRow, type Query, type Sort } from "@/lib/companydb";
import { companyIndex } from "@/lib/companydata";

export const metadata: Metadata = { title: "Companies", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const HAS_WORDS: Record<string, string> = {
  plants: "Operating plants", queue: "ERCOT queue positions", reactors: "Reactors", policy: "Policy actions",
  deals: "Deals", facilities: "Datacenter facilities",
};

function Key({ id, col, raw, children, source }: { id: string; col: string; raw: number | string; children: React.ReactNode; source: string }) {
  return <span data-n={`company_directory|company:${id}|${col}`} data-raw={String(raw)} title={source}>{children}</span>;
}

function figureCell(r: IndexRow, col: keyof IndexRow, source: string) {
  const v = Number(r[col] ?? 0);
  if (!v) return <span className="text-muted">0</span>;
  return <Key id={r.id} col={String(col)} raw={v} source={source}>{mw(v)}</Key>;
}

function Select({ name, label, value, options, tip }: { name: string; label: string; value: string; options: { value: string; label: string; disabled?: boolean }[]; tip?: React.ReactNode }) {
  return (
    <label className="mb-3 flex flex-col text-xs text-muted">
      <span>{label}{tip}</span>
      <select name={name} defaultValue={value} className="mt-1 border border-rule bg-white px-2 py-1 text-sm text-ink">
        {options.map((o) => <option key={o.value} value={o.value} disabled={o.disabled}>{o.label}</option>)}
      </select>
    </label>
  );
}

export default async function Companies({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  let ix: CompanyIndex;
  try {
    ix = companyIndex();
  } catch {
    return (
      <Brand>
        <ToolPage>
          <ToolHeader title="Companies" />
          <p className="text-sm" data-companies-unread="1">The company database&apos;s file could not be read; the tables are on <Link href="/data">Data and methods</Link>.</p>
        </ToolPage>
      </Brand>
    );
  }
  const sp = await searchParams;
  const q: Query = queryOf(sp, ix);
  const all = indexRows(ix);
  const kept = filterRows(all, q);
  const { rows, page, pages } = pageOf(kept, q.page);
  const held = ix.held_tables;
  const filtered = !!(q.q || q.kind || q.segment || q.state || q.grid || q.has);
  const dealsHeld = held.includes("energy_deals");
  const facHeld = held.includes("datacenter_facilities");
  const heldWords = held.length
    ? `Held for a license (the publishers ask for permission; warehouse/metadata/license_status.csv): ${held.map((t) => `${t} (${plural(ix.held_links[t] ?? 0, "row", "rows")})`).join(", ")}. Their rows add no company, no name and no figure here; ${plural(ix.held_only, "company", "companies")} named only in them ${ix.held_only === 1 ? "is" : "are"} not listed.`
    : "No input is held.";
  const sourceOf = (col: string) => `company_directory, ${col}: summed from the public rows of company_links (docs/methods/companies.md)`;
  const opt = (rec: Record<string, number>, order?: string[]) =>
    (order ? order.filter((k) => k in rec) : Object.keys(rec).sort()).map((k) => ({ value: k, label: `${k} (${count(rec[k])})` }));
  // session 1878 (companies faults row 5): a name more than one listed row carries; its cells add the id
  const shared = sharedNames(all);
  // session 1878 (row 11): each column head a link to its order, the filters kept, page 1
  const Head = ({ sort, label, right }: { sort: Sort; label: string; right?: boolean }) => (
    <th scope="col" className={`px-3 py-1.5 font-normal${right ? " text-right" : ""}`} aria-sort={q.sort === sort ? (sort === "name" ? "ascending" : "descending") : undefined} data-sort-col={sort}>
      <Link href={hrefOf("/companies", q, { sort, page: 1 })} title={`Order ${SORTS[sort].words}`} aria-current={q.sort === sort ? "true" : undefined}>{label}</Link>
    </th>
  );
  const csvHref = hrefOf("/companies/rows", { ...q, page: 1 });
  const readerHref = (as: string) => hrefOf(`/companies/rows/${as}`, { ...q, page: 1 });
  return (
    <Brand>
    <ToolPage>
      <ToolHeader
        title="Companies"
        lead={<>Every company the warehouse names in a public row: EIA&apos;s operators, owners and utilities, ERCOT&apos;s interconnection queue, the NRC&apos;s licensees and the policy actions&apos; agencies.<Tip id="companies-what" label="What the directory is">Built from the tables held and nothing else: no figure is typed in and no model is asked. A company is one EIA utility id where it has one, else one name as the rows write it (docs/methods/companies.md). {heldWords}</Tip></>}
      />
      <div className="grid gap-8 lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="min-w-0">
          <form method="get" action="/companies">
            <InputPanel title="Choose" reset={{ href: "/companies", defaults: "every listed company, the largest footprint first." }}>
              <label className="mb-3 flex flex-col text-xs text-muted">
                <span>Name<Tip id="companies-q" label="The search">Every word typed must be in the company&apos;s name or in another name its rows give it.</Tip></span>
                <input type="search" name="q" defaultValue={q.q} maxLength={80} className="mt-1 border border-rule bg-white px-2 py-1 text-sm text-ink" />
              </label>
              <Select name="kind" label="Kind" value={q.kind} options={[{ value: "", label: "Every kind" }, ...opt(ix.kinds, KIND_ORDER)]}
                tip={<Tip id="companies-kind" label="The kind">The first of regulator, lab or hyperscaler, OEM, utility, IPP, lender or investor, developer, operator, other that the company&apos;s rows show: EIA-861&apos;s ownership, EIA-860&apos;s sector, a queue&apos;s interconnection customer, an NRC licensee, a policy action&apos;s agency; lab or hyperscaler and OEM from the reviewed aliases only.</Tip>} />
              <Select name="segment" label="Segment" value={q.segment} options={[{ value: "", label: "Every segment" }, ...opt(ix.segments)]}
                tip={<Tip id="companies-segment" label="The segment">The fuel or line with the most MW across the company&apos;s plants, plans and queue positions; a utility or a government body with none is its kind&apos;s line.</Tip>} />
              <Select name="state" label="State" value={q.state} options={[{ value: "", label: "Every state" }, ...Object.keys(ix.states).sort().map((k) => ({ value: k, label: stateLabel(k, ix.states[k]) }))]} />
              <Select name="grid" label="Grid" value={q.grid} options={[{ value: "", label: "Every grid" }, ...opt(ix.grids)]}
                tip={<Tip id="companies-grid" label="The grid">The grids its plants&apos; balancing authorities, its queue positions and EIA-861&apos;s RTO flags name.</Tip>} />
              <Select name="has" label="Has" value={q.has} options={[
                { value: "", label: "Anything" },
                ...Object.entries(HAS_WORDS).map(([k, v]) => ({
                  value: k,
                  label: (k === "deals" && dealsHeld) || (k === "facilities" && facHeld) ? `${v} (license needed)` : v,
                  disabled: (k === "deals" && dealsHeld) || (k === "facilities" && facHeld),
                })),
              ]} tip={dealsHeld || facHeld ? <Tip id="companies-has" label="Held filters">Deals and datacenter facilities are held for a license: which company has them is not shown until a permission is recorded.</Tip> : undefined} />
              {q.sort !== "footprint" ? <input type="hidden" name="sort" value={q.sort} /> : null}
              <button type="submit" className="mt-1 border border-accent bg-accent px-3 py-1 text-sm text-white">Show</button>
            </InputPanel>
          </form>
          <p className="mt-3 text-xs leading-relaxed text-muted" data-downloads="companies">
            Download these companies: <a href={csvHref} download data-download="csv">CSV</a>, <a href={readerHref("python")} download data-download="python">Python</a>, <a href={readerHref("stata")} download data-download="stata">Stata</a>.
          </p>
        </aside>
        <div className="min-w-0">
          <p className="mb-3 text-sm" data-companies-count={kept.length}>
            <strong>{count(kept.length)}</strong> of {count(ix.n_listed)} companies{filtered ? " match" : ""}; page {page} of {pages}.
            <Tip id="companies-held" label="What is not listed">{heldWords}</Tip>
          </p>
          <div className="overflow-x-auto" role="region" aria-label="Companies" tabIndex={0}>
            <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 760 }}>
              <caption className="sr-only">{`Companies, ${SORTS[q.sort].words}`}</caption>
              <thead>
                <tr>
                  <Head sort="name" label="Company" />
                  <th scope="col" className="px-3 py-1.5 font-normal">Kind</th>
                  <th scope="col" className="px-3 py-1.5 font-normal">Segment</th>
                  <th scope="col" className="px-3 py-1.5 font-normal">States</th>
                  <Head sort="operating" label="Operating MW" right />
                  <Head sort="planned" label="Planned MW" right />
                  <Head sort="queue" label="Queue MW" right />
                  <Head sort="policy" label="Policy actions" right />
                  <Head sort="footprint" label="Footprint MW" right />
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className="border-b border-rule" data-company={r.id}>
                    <th scope="row" className="px-3 py-1.5 font-normal"><Link href={`/companies/${r.id}`}>{r.name}</Link>{shared.has(r.name) ? <span className="ml-1 font-mono text-xs" title={idTag(r.id).title} data-same-name={r.id}>{idTag(r.id).text}</span> : null}</th>
                    <td className="px-3 py-1.5">{r.kind}</td>
                    <td className="px-3 py-1.5">{r.segment}</td>
                    <td className="px-3 py-1.5" title={statesCell(r.states).title || undefined}>{statesCell(r.states).text}</td>
                    <td className="px-3 py-1.5 text-right">{figureCell(r, "plants_mw", sourceOf("plants_mw: EIA-860M operating generators' nameplate"))}</td>
                    <td className="px-3 py-1.5 text-right">{figureCell(r, "planned_mw", sourceOf("planned_mw: EIA-860M planned generators' nameplate"))}</td>
                    <td className="px-3 py-1.5 text-right">{figureCell(r, "queue_mw", sourceOf("queue_mw: ERCOT queue positions neither withdrawn nor completed"))}</td>
                    <td className="px-3 py-1.5 text-right">{r.n_policy_actions ? <Key id={r.id} col="n_policy_actions" raw={r.n_policy_actions} source={sourceOf("n_policy_actions: policy_actions rows")}>{count(r.n_policy_actions)}</Key> : <span className="text-muted">0</span>}</td>
                    <td className="px-3 py-1.5 text-right">{figureCell(r, "footprint_mw", sourceOf("footprint_mw: operating, owned, planned and queue MW summed, a sort key"))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!rows.length ? <p className="mt-3 text-sm" data-companies-none="1">No listed company matches. <Link href="/companies">Every company</Link>.</p> : null}
          {pages > 1 ? (
            <nav aria-label="Pages" className="mt-4 flex flex-wrap items-baseline gap-x-4 text-sm">
              {page > 1 ? <Link href={hrefOf("/companies", q, { page: page - 1 })} rel="prev">Previous {PAGE_SIZE}</Link> : null}
              <span className="text-muted">Page {page} of {pages}</span>
              {page < pages ? <Link href={hrefOf("/companies", q, { page: page + 1 })} rel="next">Next {PAGE_SIZE}</Link> : null}
            </nav>
          ) : null}
          <SourceLine tables={["company_directory", "company_aliases", "company_links"]} note={<>Built {ix.built.slice(0, 10)} from {ix.tables.length} tables held; the method is <Link href="/data/methods/companies">docs/methods/companies.md</Link>.</>} />
        </div>
      </div>
    </ToolPage>
    </Brand>
  );
}
