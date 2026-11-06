"use client";
// Session 3060 (chain 166): the monitor view of /policy (?view=monitor). The owner's page rules: inputs left, results
// right; explanations and sources as hover tips only; dense; no point of view. Every row is a record of
// data/policy/monitor.json (warehouse/policy/monitor_site.py): the documents that name one proceeding. The filters and
// the sort are lib/policymonitor.ts's, tested by scripts/test-policy-monitor.mjs; this component only shows them.
import { Fragment, useMemo, useState } from "react";
import {
  INSTRUMENT_WORDS, OPEN_FILTERS, SORT_KEYS, STATUS_WORDS, GRID_WORDS, figureText, filterRows, hrefOf, options, sortRows, toCsv,
  type Filters, type MonitorRow, type Option, type SortKey,
  figureKey, pythonReader, stataReader,
} from "@/lib/policymonitor";
import { MonitorCalendar } from "./MonitorCalendar";
import { MonitorCharts } from "./MonitorCharts";

const tip = "cursor-help border-b border-dotted border-muted";
const HEAD: Record<SortKey, [string, string]> = {
  date: ["Date", "The date of the record's newest document, as the Register or the agency dates it."],
  body: ["Body", "The issuing body at the level a reader filters by: a bureau, not its department."],
  instrument: ["Instrument", "What the newest document is, read from its title and the Register's action line by a written rule."],
  title: ["Action", "The newest document's title; the impact sentence below it where one was read."],
  status: ["Status", "The record's status as of its newest document."],
  sector: ["Sector", "The scorer's sector of the record's most significant document."],
  significance: ["Sig.", "The highest significance of the record's documents, 0 to 10, scored with the news rubric (a model's)."],
  next: ["Next step", "The first dated step any document states on or after the newest document's date."],
  figure: ["Figure", "The action's own figure, from a title or a document's opening paragraph only, in its unit."],
  n: ["Docs", "How many documents the record holds."],
};

function Multi({ label, opts, chosen, set, why }: { label: string; opts: Option[]; chosen: string[]; set: (v: string[]) => void; why: string }) {
  return (
    <fieldset className="mb-3" data-monitor-filter={label}>
      <legend className={`text-xs text-muted ${tip}`} title={why}>{label}{chosen.length ? ` (${chosen.length})` : ""}</legend>
      <div className="mt-1 max-h-40 overflow-y-auto border border-rule bg-panel px-2 py-1 text-xs">
        {opts.map((o) => (
          <label key={o.key} className="flex items-center gap-1 py-px">
            <input type="checkbox" checked={chosen.includes(o.key)} onChange={(e) => set(e.target.checked ? [...chosen, o.key] : chosen.filter((x) => x !== o.key))} />
            <span>{o.label}</span><span className="ml-auto tabular-nums text-muted">{o.n}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}

export function MonitorView({ rows, built, held, opened, today }: { rows: MonitorRow[]; built: string; held: number; opened: Filters; today: string }) {
  const [f, setF] = useState<Filters>(opened);
  const [sort, setSort] = useState<[SortKey, "asc" | "desc"]>(["date", "desc"]);
  const [open, setOpen] = useState<string | null>(null);
  // session 3124: below the lg width the filters fold behind one button, so the records are the first thing at 390;
  // at 1280 they stand at the left, open, as before
  const [showFilters, setShowFilters] = useState(false);
  const chosen = f.bodies.length + f.instruments.length + f.statuses.length + f.sectors.length + f.grids.length + f.states.length
    + (f.from ? 1 : 0) + (f.to ? 1 : 0) + (f.minSig !== OPEN_FILTERS.minSig ? 1 : 0);
  const opts = useMemo(() => options(rows), [rows]);
  const shown = useMemo(() => sortRows(filterRows(rows, f), sort[0], sort[1]), [rows, f, sort]);
  const put = (next: Filters) => { setF(next); window.history.replaceState(null, "", hrefOf(next)); };
  const csvHref = useMemo(() => `data:text/csv;charset=utf-8,${encodeURIComponent(toCsv(shown, built))}`, [shown, built]);
  // session 3062: a Python and a Stata reader of that CSV, as the site's TableDownloads gives for a whole table
  const pyHref = `data:text/x-python;charset=utf-8,${encodeURIComponent(pythonReader("erw-policy-monitor.csv"))}`;
  const doHref = `data:text/plain;charset=utf-8,${encodeURIComponent(stataReader("erw-policy-monitor.csv"))}`;
  const head = (k: SortKey) => (
    <th key={k} className="py-1 pr-3" aria-sort={sort[0] === k ? (sort[1] === "asc" ? "ascending" : "descending") : "none"}>
      <button type="button" className={tip} title={HEAD[k][1]} data-sort={k}
        onClick={() => setSort(sort[0] === k ? [k, sort[1] === "asc" ? "desc" : "asc"] : [k, k === "title" || k === "body" ? "asc" : "desc"])}>
        {HEAD[k][0]}{sort[0] === k ? (sort[1] === "asc" ? " ↑" : " ↓") : ""}
      </button>
    </th>
  );
  return (
    <div className="grid gap-4 lg:grid-cols-[14rem_1fr]" data-policy-monitor="1">
      <button type="button" className="border border-rule px-2 py-1 text-left text-xs lg:hidden" aria-expanded={showFilters} aria-controls="monitor-filters"
        onClick={() => setShowFilters(!showFilters)} data-monitor-filters-toggle="1">{showFilters ? "Hide the filters" : "Filters"}{chosen ? ` (${chosen} chosen)` : ""}</button>
      <aside aria-label="Filters" id="monitor-filters" data-monitor-filters="1" className={`${showFilters ? "" : "hidden"} lg:block`}>
        <Multi label="Body" opts={opts.bodies} chosen={f.bodies} set={(v) => put({ ...f, bodies: v })} why="The issuing body (a bureau, not its department)." />
        <Multi label="Instrument" opts={opts.instruments} chosen={f.instruments} set={(v) => put({ ...f, instruments: v })} why="What the newest document is." />
        <Multi label="Status" opts={opts.statuses} chosen={f.statuses} set={(v) => put({ ...f, statuses: v })} why="As of the newest document." />
        <Multi label="Sector" opts={opts.sectors} chosen={f.sectors} set={(v) => put({ ...f, sectors: v })} why="The scorer's sector of the most significant document." />
        <Multi label="Grid" opts={opts.grids} chosen={f.grids} set={(v) => put({ ...f, grids: v })} why="A grid operator the record's reads or titles name." />
        <Multi label="State" opts={opts.states} chosen={f.states} set={(v) => put({ ...f, states: v })} why="A state the record's documents apply to." />
        <label className="mb-2 flex flex-col text-xs text-muted">From
          <input type="date" value={f.from} onChange={(e) => put({ ...f, from: e.target.value })} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink" />
        </label>
        <label className="mb-2 flex flex-col text-xs text-muted">To
          <input type="date" value={f.to} onChange={(e) => put({ ...f, to: e.target.value })} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink" />
        </label>
        <label className="mb-3 flex flex-col text-xs text-muted">Significance
          <select value={f.minSig === null ? "" : String(f.minSig)} onChange={(e) => put({ ...f, minSig: e.target.value === "" ? null : Number(e.target.value) })}
            className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink">
            {[["", "All"], ["3", "3 or more"], ["5", "5 or more"], ["7", "7 or more"]].map(([k, l]) => <option key={k} value={k}>{l}</option>)}
          </select>
        </label>
        <button type="button" data-reset="1" onClick={() => put(OPEN_FILTERS)} className="border border-rule px-2 py-1 text-xs"
          title="Every body, instrument, status, sector, grid and state, any date, significance 5 or more">Reset the filters</button>
      </aside>
      <section aria-label="Records">
        {/* session 3061: the calendar of the records the filters leave */}
        <MonitorCalendar rows={filterRows(rows, { ...f, from: "", to: "" })} today={today} />
        <p className="mb-2 text-xs text-muted" data-monitor-shown={shown.length} data-monitor-held={held}>
          <span className={tip} title="The records the filters leave, counted on this page.">{shown.length}</span> shown of{" "}
          <span className={tip} title={`Every record of data/policy/monitor.json, built ${built} from policy_actions: the documents that name one proceeding, grouped.`}>{held}</span> records held
          {" · "}<a href={csvHref} download="erw-policy-monitor.csv" data-monitor-csv="1" className={tip} title="The records shown, with every source, as CSV.">CSV of these</a>,{" "}
          <a href={pyHref} download="erw-policy-monitor.py" data-download="python" className={tip} title="A Python reader of that CSV (pandas).">Python</a>,{" "}
          <a href={doHref} download="erw-policy-monitor.do" data-download="stata" className={tip} title="A Stata reader of that CSV.">Stata</a>
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <caption className="sr-only">The policy actions the filters leave, one row a proceeding: date, body, instrument, action, status, sector, significance, next step, figure and documents; a row opens to its history and sources</caption>
            <thead><tr className="border-b border-rule text-left text-xs text-muted">{SORT_KEYS.map(head)}</tr></thead>
            <tbody>
              {shown.slice(0, 300).map((r) => (
                <Fragment key={r.id}>
                  <tr className="cursor-pointer border-b border-rule/60 align-top hover:bg-panel" onClick={() => setOpen(open === r.id ? null : r.id)} data-record={r.id}>
                    <td className="py-1 pr-3 tabular-nums">{r.date}</td>
                    <td className="py-1 pr-3">{r.body}</td>
                    <td className="py-1 pr-3">{INSTRUMENT_WORDS[r.instrument] ?? r.instrument}</td>
                    <td className="py-1 pr-3">
                      <a href={r.sources?.[0]} onClick={(e) => e.stopPropagation()} title={`The newest document's own page; ${r.sources?.length ?? 0} source${r.sources?.length === 1 ? "" : "s"} in all`}>{r.title}</a>
                      {r.impact ? <div className="mt-0.5 text-xs text-muted"><span className={tip} title={`Its words in the document: "${r.impact.quote}" (the clause is ${r.impact.model}'s, kept only because these words stand in the text; where it bears is a written rule's)`}>{r.impact.text}</span></div>
                        : r.plain ? <div className="mt-0.5 text-xs text-muted"><span className={tip} title="The impact read of policy_reads, a model's, each field kept only when its words stand in the action's text.">{r.plain}</span></div> : null}
                    </td>
                    <td className="py-1 pr-3">{STATUS_WORDS[r.status] ?? r.status}{r.scope ? <div className={`text-xs italic text-muted ${tip}`} title="A document the connector keeps that is no energy action, by a written list (warehouse/policy/fields.py, OUT_OF_SCOPE): marked, never dropped." data-scope="1">{r.scope}</div> : null}</td>
                    <td className="py-1 pr-3">{r.sector?.replace(/_/g, " ") ?? ""}</td>
                    <td className="py-1 pr-3 text-right tabular-nums">{r.significance ?? ""}</td>
                    <td className="py-1 pr-3 tabular-nums">{r.next ? <span className={tip} title={`"${r.next.words}"`}>{r.next.date} {r.next.step}</span> : ""}</td>
                    <td className="py-1 pr-3 tabular-nums">{r.figure ? <span className={tip} title={`"${r.figure.words}" (${r.figure.event_id})`} data-check={figureKey(r)}>{figureText(r.figure)}</span> : ""}</td>
                    <td className="py-1 text-right tabular-nums">{r.n}</td>
                  </tr>
                  {open === r.id ? (
                    <tr className="border-b border-rule/60 bg-panel text-xs" data-record-open={r.id}>
                      <td colSpan={SORT_KEYS.length} className="px-2 py-2">
                        <div>Proceeding: {r.docket || "none named"}{r.grids?.length ? ` · grids: ${r.grids.map((g) => GRID_WORDS[g] ?? g).join(", ")}` : ""}{r.states?.length ? ` · states: ${r.states.join(", ")}` : ""}
                          {" · "}bears on <a href={r.bears_on.page}>{r.bears_on.table}</a></div>
                        <ol className="mt-1 list-decimal pl-5">{(r.history ?? []).map((h) => <li key={h}>{h}</li>)}</ol>
                        <div className="mt-1">Sources: {(r.sources ?? []).map((u, i) => <a key={u} href={u} className="mr-2">{i + 1}</a>)}{r.news?.length ? ` · news: ${r.news.length}` : ""}</div>
                      </td>
                    </tr>
                  ) : null}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
        {shown.length > 300 ? <p className="mt-2 text-xs text-muted">The first 300 are listed; narrow the filters, or take the CSV, for the rest.</p> : null}
        <MonitorCharts rows={rows} />
      </section>
    </div>
  );
}
