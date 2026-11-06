"use client";
// The /deals table (session 2238, chain 156): the inputs on the left, the deals on the right; every column sorts; each
// row opens to the whole deal; the sources, the flags and how a field was read are hover tips; the filtered rows
// download as CSV with a Python and a Stata reader. The logic is lib/dealsview.ts (pure, tested by Node).
import { Fragment, useEffect, useMemo, useState } from "react";
import { Num } from "@/components/Num";
import { companyAnchor, companyKey } from "@/lib/companies";
import {
  KINDS, KIND_LABEL, NO_INPUTS, STAGES, STAGE_LABEL, filterRows, filterWords, partiesOf, priceDisclosed, pythonReader,
  sortRows, stageOf, stataReader, toCsv, type Inputs, type Row, type SortKey,
} from "@/lib/dealsview";

export type Deal = Row;

/** US dollars, short: 6000000000 gives "6 billion". scripts/check-values.mjs formats the same way (data-format usd). */
export function usd(v: number): string {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}

const n = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const day = (d: string) => d.slice(0, 10);
const uniq = (xs: string[]) => Array.from(new Set(xs.filter(Boolean))).sort();
const FILE = "erw_energy_deals.csv";

function Select({ label, tip, value, set, options, render }: { label: string; tip: string; value: string; set: (v: string) => void; options: string[]; render?: (v: string) => string }) {
  return (
    <label className="flex min-w-0 max-w-full flex-col gap-1 text-xs text-muted">
      <span title={tip}>{label}</span>
      <select title={tip} value={value} onChange={(e) => set(e.target.value)} className="max-w-full border border-rule bg-panel px-2 py-1 text-sm text-ink">
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {render ? render(o) : o}
          </option>
        ))}
      </select>
    </label>
  );
}

function Field({ label, tip, value, set, type = "text", list, placeholder }: { label: string; tip: string; value: string; set: (v: string) => void; type?: string; list?: string; placeholder?: string }) {
  return (
    <label className="flex min-w-0 flex-col gap-1 text-xs text-muted" title={tip}>
      {label}
      <input type={type} value={value} list={list} placeholder={placeholder} onChange={(e) => set(e.target.value)} className="w-full min-w-0 border border-rule bg-panel px-2 py-1 text-sm text-ink" />
    </label>
  );
}

// Session 26: a party name that matches a company of energy_companies links to its row on the companies tab
function Party({ name: n, known }: { name: string; known: Set<string> }) {
  return known.has(companyKey(n)) ? (
    <a href={`/deals?tab=companies#${companyAnchor(n)}`} onClick={(e) => e.stopPropagation()}>{n}</a>
  ) : (
    <>{n}</>
  );
}

function save(name: string, text: string, type: string) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

const COLS: [SortKey, string, string, boolean][] = [
  ["date", "Date", "The announced date where a story states it, else the first story's publish date (UTC)", false],
  ["kind", "Kind", "Master plan tool 6's kinds: the power kind first (a PPA for a restarted reactor is a restart), else the deal's form", false],
  ["parties", "Parties", "Buyer / seller, one name a company: the spellings of one company joined (warehouse/deals/counterparties.py)", false],
  ["asset", "Asset", "The project, plant, company or asset traded, as the story names it", false],
  ["where", "Where", "The US state and the country the story names; never read from a city, a basin or a company", false],
  ["grid", "Grid", "A grid operator a story names, else the grid that serves most of the state (each cell's tip says which)", false],
  ["mw", "MW", "As stated; empty where no story states it. A sum is never estimated", true],
  ["usd", "US dollars", "As stated in US dollars; a sum in another currency, a valuation or a company-wide investment is not the deal's", true],
  ["price", "Price", "A price per MWh as stated; almost no story the ERW reads states one", true],
  ["stage", "Stage", "Where the deal stands, as its words say; each cell's tip shows how it moved", false],
  ["ai", "AI", "A named AI lab, hyperscaler, datacenter operator or AI-load buyer is a party, or the load is a datacenter", false],
  ["sources", "Sources", "The stories the deal was read from; hover for the outlets and the flags", true],
];

export function DealsTable({ rows, companies = [] }: { rows: Row[]; companies?: string[] }) {
  const known = useMemo(() => new Set(companies.map(companyKey)), [companies]);
  const [f, setF] = useState<Inputs>(NO_INPUTS);
  const [sort, setSort] = useState<{ key: SortKey; dir: "asc" | "desc" }>({ key: "date", dir: "desc" });
  const [open, setOpen] = useState<string | null>(null);
  const set = (k: keyof Inputs) => (v: string) => setF((x) => ({ ...x, [k]: v }));
  // a kind in the address (/deals?kind=gas_buildout, and the older ?type=capital) sets the filter once, after the page loads
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const k = q.get("kind") ?? (q.get("type") === "capital" ? "capital" : null);
    if (k && KIND_LABEL[k]) setF((x) => ({ ...x, kind: k })); // eslint-disable-line react-hooks/set-state-in-effect
  }, []);

  const shown = useMemo(() => sortRows(filterRows(rows, f), sort.key, sort.dir), [rows, f, sort]);
  const parties = useMemo(() => uniq(rows.flatMap(partiesOf)), [rows]);
  const years = useMemo(() => uniq(rows.map((d) => d.date.slice(0, 4))).reverse(), [rows]);
  const kinds = useMemo(() => KINDS.map(([k]) => k).filter((k) => rows.some((d) => d.kind === k)), [rows]);
  const grids = useMemo(() => [...uniq(rows.map((d) => d.grid)), "none"], [rows]);
  const stages = useMemo(() => [...STAGES.filter((s) => rows.some((d) => stageOf(d) === s)), "none"], [rows]);
  const sortBy = (key: SortKey, numeric: boolean) =>
    setSort((s) => (s.key === key ? { key, dir: s.dir === "asc" ? "desc" : "asc" } : { key, dir: numeric || key === "date" ? "desc" : "asc" }));
  const download = (what: "csv" | "py" | "do") => {
    const when = new Date().toISOString().slice(0, 16).replace("T", " ") + " UTC";
    if (what === "csv") save(FILE, toCsv(shown, { url: window.location.href, when, filters: filterWords(f) }), "text/csv");
    else if (what === "py") save("erw_energy_deals.py", pythonReader(FILE), "text/x-python");
    else save("erw_energy_deals.do", stataReader(FILE), "text/plain");
  };

  return (
    <section aria-label="Deals" className="grid gap-4 lg:grid-cols-[15rem_minmax(0,1fr)]" data-deals-table="2238">
      <aside aria-label="Choose the deals" className="flex flex-col gap-3">
        <Select label="Kind" tip="Master plan tool 6's kinds; the power kind first, else the form" value={f.kind} set={set("kind")} options={kinds} render={(v) => KIND_LABEL[v] ?? v} />
        <Select label="Grid" tip="Named in a story, else the state's main grid; none: neither" value={f.grid} set={set("grid")} options={grids} render={(v) => (v === "none" ? "No grid stated or read" : v)} />
        <Select label="State" tip="The US state the story names" value={f.state} set={set("state")} options={uniq(rows.map((d) => d.state))} />
        <Field label="Counterparty" tip="Any party whose name holds these letters, one name a company" value={f.party} set={set("party")} list="deal-parties" placeholder="any" />
        <datalist id="deal-parties">{parties.map((p) => <option key={p} value={p} />)}</datalist>
        <div className="grid grid-cols-2 gap-2">
          <Field label="MW from" tip="Deals that state MW of at least this; a deal that states none is left out" value={f.mwMin} set={set("mwMin")} type="number" />
          <Field label="MW to" tip="Deals that state MW of at most this" value={f.mwMax} set={set("mwMax")} type="number" />
        </div>
        <Select label="Year" tip="The year of the deal's date" value={f.year} set={set("year")} options={years} />
        <Select label="AI or datacenter power" tip="The AI-power rule: a named AI party or a datacenter load" value={f.ai} set={set("ai")} options={["yes", "no"]} />
        <Select label="Stage" tip="As the words state it; none: the stories state no stage" value={f.stage} set={set("stage")} options={stages} render={(v) => (v === "none" ? "Not stated" : STAGE_LABEL[v] ?? v)} />
        <Select label="Price disclosed" tip="A price per MWh (or another energy unit) the stories state" value={f.price} set={set("price")} options={["yes", "no"]} />
        <button type="button" data-reset="1" title="Every input back to All" onClick={() => setF(NO_INPUTS)} className="border border-rule px-2 py-1 text-xs">Reset the filters</button>
        <div className="flex flex-col gap-1 text-xs" aria-label="Download the deals shown">
          <span className="text-muted">The {shown.length} deals shown, as</span>
          <div className="flex flex-wrap gap-2">
            <button type="button" data-download="csv" onClick={() => download("csv")} className="border border-rule px-2 py-1" title="The rows shown, their fields and links; no outlet text">CSV</button>
            <button type="button" data-download="py" onClick={() => download("py")} className="border border-rule px-2 py-1" title="A Python reader of that CSV (pandas)">Python</button>
            <button type="button" data-download="do" onClick={() => download("do")} className="border border-rule px-2 py-1" title="A Stata reader of that CSV">Stata</button>
          </div>
        </div>
      </aside>
      <div className="min-w-0">
        <p className="mb-2 text-xs text-muted" data-count={`${shown.length}/${rows.length}`}>
          {shown.length} of the {rows.length} deals shown
        </p>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                {COLS.map(([key, label, tip, numeric]) => (
                  <th key={key} className={`py-1 pr-3 font-normal ${numeric ? "text-right" : ""}`} aria-sort={sort.key === key ? (sort.dir === "asc" ? "ascending" : "descending") : "none"} title={tip}>
                    <button type="button" onClick={() => sortBy(key, numeric)} className="text-muted" data-sort={key}>
                      {label}
                      {sort.key === key ? (sort.dir === "asc" ? " ▲" : " ▼") : ""}
                    </button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {shown.map((d) => {
                const isOpen = open === d.id;
                const names = [d.buyerName, d.sellerName].filter(Boolean);
                const outlets = `${d.source}${d.storyUrls.length > 1 ? ` and ${d.storyUrls.length - 1} more` : ""}`;
                return (
                  <Fragment key={d.id}>
                    <tr className="cursor-pointer border-b border-rule/60 align-top hover:bg-panel" onClick={() => setOpen(isOpen ? null : d.id)}>
                      <td className="py-1 pr-3 whitespace-nowrap">
                        <button type="button" aria-expanded={isOpen} className="mr-1 text-accent" aria-label={isOpen ? "Hide details" : "Show details"}>
                          {isOpen ? "▾" : "▸"}
                        </button>
                        {day(d.date)}
                      </td>
                      <td className="py-1 pr-3 whitespace-nowrap" title={d.kindBasis}>{KIND_LABEL[d.kind] ?? d.kind}</td>
                      <td className="py-1 pr-3">
                        {names.length ? names.map((x, i) => (
                          <Fragment key={`${x}-${i}`}>
                            {i ? " / " : ""}
                            {x.split("; ").map((p, j) => <Fragment key={`${p}-${j}`}>{j ? ", " : ""}<Party name={p} known={known} /></Fragment>)}
                          </Fragment>
                        )) : d.others.split(";").filter(Boolean).join(", ")}
                      </td>
                      <td className="py-1 pr-3">{d.asset}</td>
                      <td className="py-1 pr-3 whitespace-nowrap">{[d.state, d.country].filter(Boolean).join(", ")}</td>
                      <td className="py-1 pr-3 whitespace-nowrap" title={d.gridBasis}>{d.grid}</td>
                      <td className="py-1 pr-3 text-right tabular-nums">
                        {d.mw !== null ? <Num check={`event|energy_deals|${d.id}|mw`} raw={d.mw}>{n(d.mw)}</Num> : ""}
                      </td>
                      <td className="py-1 pr-3 text-right tabular-nums whitespace-nowrap">
                        {d.dollars !== null ? (
                          <span data-format="usd">
                            <Num check={`event|energy_deals|${d.id}|dollars`} raw={d.dollars}>{usd(d.dollars)}</Num>
                          </span>
                        ) : (
                          ""
                        )}
                      </td>
                      <td className="py-1 pr-3 text-right tabular-nums whitespace-nowrap">
                        {d.usdPerMwh !== null ? `${n(d.usdPerMwh)}/MWh` : d.priceValue !== null && priceDisclosed(d) ? `${n(d.priceValue)} ${d.priceUnit}` : ""}
                      </td>
                      <td className="py-1 pr-3 whitespace-nowrap" title={d.statusHistory || (d.stage ? "" : "the status as extracted before session 2232")}>
                        {STAGE_LABEL[stageOf(d)] ?? stageOf(d)}
                      </td>
                      <td className="py-1 pr-3" title={d.aiBasis}>{d.aiPower ? "yes" : ""}</td>
                      <td className="py-1 pr-3 text-right whitespace-nowrap" title={`${outlets}${d.flags.length ? `. Flags: ${d.flags.join("; ")}` : ""}`}>
                        {d.storyUrls.length}
                        {d.flags.length ? <span className="ml-1 text-accent" aria-label={`${d.flags.length} flags`} data-flags={d.flags.length}>!</span> : null}
                      </td>
                    </tr>
                    <tr hidden={!isOpen} className="border-b border-rule/60 bg-panel">
                      <td colSpan={COLS.length} className="px-3 py-2 text-sm">
                        <dl className="grid grid-cols-1 gap-x-6 gap-y-1 sm:grid-cols-[10rem_1fr]">
                          <dt className="text-muted">Buyer</dt>
                          <dd>{d.buyer ? <>{d.buyer}{d.buyerName && d.buyerName !== d.buyer ? <span className="text-muted"> (one name: {d.buyerName})</span> : null}</> : "not stated"}</dd>
                          <dt className="text-muted">Seller</dt>
                          <dd>{d.seller ? <>{d.seller}{d.sellerName && d.sellerName !== d.seller ? <span className="text-muted"> (one name: {d.sellerName})</span> : null}</> : "not stated"}</dd>
                          <dt className="text-muted">Other parties</dt>
                          <dd>{d.others ? d.others.split(";").join(", ") : "none named"}</dd>
                          <dt className="text-muted">Form</dt>
                          <dd>{d.type || "not stated"}{d.technology ? `; ${d.technology}` : ""}</dd>
                          <dt className="text-muted">Capacity</dt>
                          <dd>{d.mw !== null ? `${n(d.mw)} MW` : "MW not stated"}{d.mwh !== null ? `; ${n(d.mwh)} MWh` : ""}</dd>
                          <dt className="text-muted">Value</dt>
                          <dd>{d.dollars !== null ? `USD ${usd(d.dollars)}` : "not stated in US dollars"}</dd>
                          <dt className="text-muted">Price</dt>
                          <dd>{d.usdPerMwh !== null ? `USD ${n(d.usdPerMwh)} per MWh` : d.priceValue !== null && priceDisclosed(d) ? `${n(d.priceValue)} ${d.priceUnit}` : "not stated"}</dd>
                          <dt className="text-muted">Term</dt>
                          <dd>{d.termYears !== null ? `${n(d.termYears)} years` : "not stated"}</dd>
                          <dt className="text-muted">Stage</dt>
                          <dd>{STAGE_LABEL[stageOf(d)] ?? (stageOf(d) || "not stated")}{d.statusHistory ? <span className="text-muted"> ({d.statusHistory})</span> : null}</dd>
                          <dt className="text-muted">Model confidence</dt>
                          <dd>{d.confidence !== null ? n(d.confidence) : ""}</dd>
                          <dt className="text-muted">Flags</dt>
                          <dd>{d.flags.length ? d.flags.join("; ") : "none"}</dd>
                          <dt className="text-muted">Sources</dt>
                          <dd>
                            {d.storyUrls.map((u, i) => (
                              <span key={u}>
                                {i ? ", " : ""}
                                <a href={u} rel="noopener noreferrer" target="_blank">{i === 0 ? d.source : `story ${i + 1}`}</a>
                              </span>
                            ))}
                          </dd>
                          <dt className="text-muted">Evidence</dt>
                          <dd className="text-muted">
                            The sentence each field was read from is the outlet&apos;s text, which the ERW does not republish (the internal table
                            energy_deals_evidence keeps it); the stories above hold it.
                          </dd>
                        </dl>
                      </td>
                    </tr>
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
        {shown.length === 0 ? <p className="mt-2 text-sm text-muted">No deal matches these inputs.</p> : null}
      </div>
    </section>
  );
}
