"use client";
// Chain 302 (session 7201): "Large-load rules by utility" and "What changed in the last 90 days", under the All grids
// tab of /cost-of-power. One row a rule of utility_large_load_rules, the reader's questions as columns (docs/reviews/
// large-load-on-site/questions.md), each cell the document's own words cut at a word, whole with its cite on hover. The
// table sorts by any column, filters by state, grid and status, opens a row to the rule in full, and sets two rules
// side by side as A and B. A row held for a license is drawn with its utility and place and every other cell blank,
// "license needed" on hover; the same for a withheld field. Everything is read from data/siting/large_load_rules.json
// (warehouse/derived/large_load_rules_page.py), which holds no held value; what is shown and in what order is
// lib/largeloadrules.ts, tested by scripts/test-large-load-rules.mjs. The filters, the sort, A and B and the open row
// are kept in the address, so a reader can send the screen. No request is made: the downloads are made here.
import { Fragment, useEffect, useMemo, useState, type ReactNode } from "react";
import fileJson from "@/data/siting/large_load_rules.json";
import { Blank, FieldView, HELD_ROW_TIP, HeldCard, RuleCard, Tip } from "@/components/largeload/parts";
import { Download } from "@/components/largeload/Download";
import { SiteLink } from "@/components/SiteLink";
import {
  CHANGES_ANCHOR, CHANGES_CSV_NAME, CHANGE_CSV_COLS, CHANGE_GROUPS, CHANGE_KIND_WORDS, FIELDS, FIELD_HEAD, FIELD_TIP, GRID_WORDS, HELD_STATUS, LICENSE_NEEDED,
  RULES_CSV_NAME, RULE_CSV_COLS, RULE_SORTS, STATUS_TIP, CHANGES_TABLE, affectsOf, changesCsv, dateWords, filterChanges, filterLines, groupWords,
  lawStates, lawsHref, lineOf, lines, pythonReader, ruleOptions, rulesCsv, sortLines, stataReader, statesOf, statusTip,
  type Change, type Line, type RuleSort, type RulesFile,
} from "@/lib/largeloadrules";

const FILE = fileJson as unknown as RulesFile;
const ALL = lines(FILE);
const LAW_STATES = lawStates(FILE);
const PAGE = 12, CHANGE_PAGE = 12;
const HEADS: Record<string, [string, string]> = {
  utility: ["Utility and rule", "The utility, or the commission whose rule binds a state's utilities, and the rule's name. Press a name to open the rule in full."],
  state: ["State", "The state or states the rule applies in."],
  grid: ["Grid", "The grid operator the utility is in, or no ISO: the ERW's classification, not a cited value."],
  status: ["Status", "In effect, approved, proposed, ordered or denied, as the document read says, with its date on hover."],
  date: ["Date", "The date of the status as the document prints it: a day or a month."],
  ...Object.fromEntries(FIELDS.map((f) => [f, [FIELD_HEAD[f], FIELD_TIP[f]]])),
};
const COLS: RuleSort[] = ["utility", "state", "grid", "status", "date", ...FIELDS];

export type Opened = { state: string; grid: string; status: string; find: string; sort: string; dir: string; a: string; b: string; rule: string; region: string };

export function LargeLoadRules({ opened, address }: { opened: Opened; address: string }) {
  const opts = useMemo(() => ruleOptions(ALL), []);
  const has = (list: { key: string }[], k: string) => (list.some((o) => o.key === k) ? k : "");
  const known = (id: string) => (ALL.some((r) => r.id === id) ? id : "");
  const [st, setSt] = useState(has(opts.states, opened.state));
  const [gr, setGr] = useState(has(opts.grids, opened.grid));
  const [su, setSu] = useState(has(opts.statuses, opened.status));
  const [nq, setNq] = useState(opened.find);
  const [by, setBy] = useState<RuleSort>((RULE_SORTS as string[]).includes(opened.sort) ? (opened.sort as RuleSort) : "utility");
  const [dir, setDir] = useState<"asc" | "desc">(opened.dir === "desc" ? "desc" : "asc");
  const [a, setA] = useState(known(opened.a));
  const [b, setB] = useState(known(opened.b));
  const [open, setOpen] = useState(known(opened.rule));
  const [limit, setLimit] = useState(PAGE);
  const [region, setRegion] = useState(CHANGE_GROUPS.some(([k]) => k === opened.region) ? opened.region : "");
  const [changeLimit, setChangeLimit] = useState(CHANGE_PAGE);
  // the row the page moves to: a new object each time, so the same rule can be asked for twice
  const [jump, setJump] = useState<{ id: string }>({ id: known(opened.rule) });

  const shown = useMemo(() => sortLines(filterLines(ALL, { states: st ? [st] : [], grids: gr ? [gr] : [], statuses: su ? [su] : [], find: nq }), by, dir), [st, gr, su, nq, by, dir]);
  // the open row is always drawn, whatever the page of the list it is on
  const drawnRows = useMemo(() => { const i = shown.findIndex((r) => r.id === open); return shown.slice(0, Math.max(limit, i + 1)); }, [shown, limit, open]);
  const changes = useMemo(() => filterChanges(FILE.changes, region ? [region] : []), [region]);

  // a link of the page that names a state, a grid, a status, a rule or A and B (the tab's cells, the row's panel) sets it
  // here; a navigation that names none (the hub table's sort, the load's form) leaves the table as the reader set it
  const openedKey = JSON.stringify(opened);
  const [seen, setSeen] = useState(openedKey);
  if (seen !== openedKey) {
    setSeen(openedKey);
    if (opened.state) setSt(has(opts.states, opened.state));
    if (opened.grid) setGr(has(opts.grids, opened.grid));
    if (opened.status) setSu(has(opts.statuses, opened.status));
    if (opened.find) setNq(opened.find);
    if (opened.a) setA(known(opened.a));
    if (opened.b) setB(known(opened.b));
    if (opened.rule) { setOpen(known(opened.rule)); setJump({ id: known(opened.rule) }); }
    if (opened.state || opened.grid || opened.status || opened.find) setLimit(PAGE);
  }
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const put = (k: string, v: string, none = "") => { if (v && v !== none) q.set(k, v); else q.delete(k); };
    put("rstate", st); put("rgrid", gr); put("rstatus", su); put("rq", nq.trim()); put("rsort", by, "utility"); put("rdir", dir, "asc");
    put("ra", a); put("rb", b); put("rule", open); put("rregion", region);
    const s = q.toString();
    window.history.replaceState(null, "", `${window.location.pathname}${s ? `?${s}` : ""}${window.location.hash}`);
  }, [st, gr, su, nq, by, dir, a, b, open, region, openedKey]);
  useEffect(() => {
    // the address's own anchor (a row's panel, the section's head) wins on arrival; a rule asked for with no anchor is moved to
    if (jump.id && (!window.location.hash || window.location.hash === "#llr")) document.getElementById(`llr-row-${jump.id}`)?.scrollIntoView({ block: "center" });
  }, [jump]);

  /** Open a rule from elsewhere in the section (a change, a pointer to the utility's other row): the filters that
   * would hide it are lifted, and the page moves to its row. */
  const openRule = (id: string) => {
    if (!filterLines(ALL, { states: st ? [st] : [], grids: gr ? [gr] : [], statuses: su ? [su] : [], find: nq }).some((r) => r.id === id)) { setSt(""); setGr(""); setSu(""); setNq(""); }
    setOpen(id); setJump({ id });
    if (window.location.hash) window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}#llr`);
  };
  const seeRow = (id: string): ReactNode => <button type="button" className="underline decoration-dotted" onClick={() => openRule(id)} data-llr-see={id}>see its other row</button>;
  const click = (k: RuleSort) => { if (k === by) setDir(dir === "asc" ? "desc" : "asc"); else { setBy(k); setDir("asc"); } };
  const reset = () => { setSt(""); setGr(""); setSu(""); setNq(""); setLimit(PAGE); };
  const pick = (which: "a" | "b", id: string) => (which === "a" ? setA(a === id ? "" : id) : setB(b === id ? "" : id));
  const lawLink = (state: string) => {
    const s = statesOf(state).filter((x) => LAW_STATES.includes(x));
    return s.length ? <span data-llr-laws={s.join(",")}>State law: {s.map((x, i) => <Fragment key={x}>{i ? ", " : ""}<SiteLink href={lawsHref(x)} gate="plain">{x}</SiteLink></Fragment>)}</span> : null;
  };
  const sel = "border border-rule bg-panel px-2 py-1 text-sm text-ink";
  const la = a ? lineOf(FILE, a) : undefined, lb = b ? lineOf(FILE, b) : undefined;

  return (
    <div data-llr-table="1">
      {la || lb ? <AbRules a={la} b={lb} clearA={() => setA("")} clearB={() => setB("")} /> : null}
      <div className="mb-2 flex flex-wrap items-end gap-3 text-sm" data-llr-filters="1">
        <label className="flex flex-col gap-1">State
          <select value={st} onChange={(e) => { setSt(e.target.value); setLimit(PAGE); }} className={sel} data-llr-filter="state">
            <option value="">every state</option>
            {opts.states.map((o) => <option key={o.key} value={o.key}>{o.label} ({o.n})</option>)}
          </select>
        </label>
        <label className="flex flex-col gap-1">Grid
          <select value={gr} onChange={(e) => { setGr(e.target.value); setLimit(PAGE); }} className={sel} data-llr-filter="grid">
            <option value="">every grid</option>
            {opts.grids.map((o) => <option key={o.key} value={o.key}>{o.label} ({o.n})</option>)}
          </select>
        </label>
        <label className="flex flex-col gap-1">Status
          <select value={su} onChange={(e) => { setSu(e.target.value); setLimit(PAGE); }} className={sel} data-llr-filter="status">
            <option value="">every status</option>
            {opts.statuses.map((o) => <option key={o.key} value={o.key}>{o.label} ({o.n})</option>)}
          </select>
        </label>
        <label className="flex flex-col gap-1">Utility or rule
          <input type="search" value={nq} onChange={(e) => { setNq(e.target.value); setLimit(PAGE); }} placeholder="for example Dominion" className={`w-56 max-w-full ${sel}`} data-llr-filter="find" />
        </label>
        <button type="button" onClick={reset} className="border border-rule px-2 py-1 text-sm" data-llr-reset="1">Every rule</button>
      </div>
      <p className="mb-2 text-sm" role="status" data-llr-shown={shown.length} data-llr-sort={`${by}|${dir}`}>
        {shown.length} of {ALL.length} rules shown{st || gr || su || nq.trim() ? ` (${[st, gr ? GRID_WORDS[gr] : "", su === HELD_STATUS ? LICENSE_NEEDED : su, nq.trim() ? `names holding "${nq.trim()}"` : ""].filter(Boolean).join(", ")})` : ""},
        sorted by {HEADS[by][0].toLowerCase()}, {by === "date" ? (dir === "asc" ? "earliest first" : "latest first") : dir === "asc" ? "A to Z" : "Z to A"}; a row with nothing printed in that column last.
        {" "}<Download make={() => rulesCsv(shown, FILE, address)} name={RULES_CSV_NAME} mark={{ "data-llr-csv": "rules" }}>CSV of these</Download>,{" "}
        <Download make={() => pythonReader(RULES_CSV_NAME, RULE_CSV_COLS, "the large-load rules as filtered on /cost-of-power?view=allgrids")} name="erw-large-load-rules.py" type="text/x-python" mark={{ "data-download": "python" }}>Python</Download>,{" "}
        <Download make={() => stataReader(RULES_CSV_NAME, RULE_CSV_COLS, "the large-load rules as filtered on /cost-of-power?view=allgrids")} name="erw-large-load-rules.do" type="text/plain" mark={{ "data-download": "stata" }}>Stata</Download>
      </p>
      <div className="overflow-x-auto" role="region" aria-label="Large-load rules by utility" tabIndex={0}>
        <table className="w-full border-collapse text-left text-sm" style={{ minWidth: 1500 }} data-llr-rules="1">
          <caption className="sr-only">US utilities&apos; large-load connection rules, one row a rule: the smallest load covered, the contract&apos;s length, the minimum bill, the collateral, the exit fee, the study time, the time to energize and the queue, each as the document prints it</caption>
          <thead>
            <tr className="border-b border-ink text-xs">
              {COLS.map((k) => (
                <th key={k} scope="col" className="px-2 py-1.5 align-bottom font-normal" aria-sort={by === k ? (dir === "asc" ? "ascending" : "descending") : "none"} style={k === "utility" ? { minWidth: "15rem" } : FIELDS.includes(k as never) ? { minWidth: "9.5rem" } : undefined}>
                  <HeadTip tip={`${HEADS[k][1]} Press to sort by it; again to turn it round.`} onClick={() => click(k)} k={k}>{HEADS[k][0]}{by === k ? (dir === "asc" ? " (up)" : " (down)") : ""}</HeadTip>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {drawnRows.map((l) => (
              <Fragment key={l.id}>
                <tr id={`llr-row-${l.id}`} className={`border-b border-rule align-top ${open === l.id ? "bg-paper" : ""}`} data-llr-row={l.id} data-llr-held={l.held ? "1" : "0"}>
                  <th scope="row" className="px-2 py-1.5 text-left font-normal">
                    <button type="button" onClick={() => setOpen(open === l.id ? "" : l.id)} aria-expanded={open === l.id} className="text-left underline decoration-dotted" data-llr-open={l.id}>{l.utility}</button>
                    {l.rule ? <span className="block text-xs" data-llr-name="1">{l.rule.name.length > 90 ? <Tip tip={l.rule.name} plain>{`${l.rule.name.slice(0, 88).replace(/\s+\S*$/, "")}...`}</Tip> : l.rule.name}</span> : null}
                    <span className="mt-0.5 block text-xs">
                      <button type="button" onClick={() => pick("a", l.id)} aria-pressed={a === l.id} className={`mr-1 border px-1 ${a === l.id ? "border-ink font-semibold" : "border-rule"}`} data-llr-set="a" aria-label={`Set ${l.utility} as A`}>A</button>
                      <button type="button" onClick={() => pick("b", l.id)} aria-pressed={b === l.id} className={`border px-1 ${b === l.id ? "border-ink font-semibold" : "border-rule"}`} data-llr-set="b" aria-label={`Set ${l.utility} as B`}>B</button>
                    </span>
                  </th>
                  <td className="px-2 py-1.5">{l.state}</td>
                  <td className="px-2 py-1.5">{l.rule ? <Tip tip={`The ERW's classification: ${l.region}.`} plain>{GRID_WORDS[l.grid] ?? l.grid}</Tip> : GRID_WORDS[l.grid] ?? l.grid}</td>
                  {l.held || !l.rule ? (
                    <>{["Status", "Date", ...FIELDS.map((f) => FIELD_HEAD[f])].map((h) => <td key={h} className="px-2 py-1.5"><Blank tip={HELD_ROW_TIP(l.utility)} what={h} /></td>)}</>
                  ) : (
                    <>
                      <td className="px-2 py-1.5"><Tip tip={statusTip(l.rule)} data={{ "llr-status": l.rule.status }}>{l.rule.status}</Tip></td>
                      <td className="whitespace-nowrap px-2 py-1.5 tabular-nums">{dateWords(l.rule.status_date)}</td>
                      {FIELDS.map((f) => <td key={f} className="px-2 py-1.5"><FieldView rule={l.rule!} f={f} onSee={seeRow} /></td>)}
                    </>
                  )}
                </tr>
                {open === l.id ? (
                  <tr className="border-b border-rule bg-paper" data-llr-opened={l.id}>
                    <td colSpan={COLS.length} className="px-2 py-2">
                      <div className="max-w-4xl">{l.rule ? <RuleCard rule={l.rule} onSee={seeRow} lawsHref={lawLink(l.state)} /> : <HeldCard rule={l} />}</div>
                    </td>
                  </tr>
                ) : null}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
      {shown.length > drawnRows.length ? (
        <button type="button" className="mt-2 border border-rule px-2 py-1 text-sm" onClick={() => setLimit(drawnRows.length + PAGE)} data-llr-more="1">
          Next {Math.min(PAGE, shown.length - drawnRows.length)} ({drawnRows.length} of {shown.length} drawn; the CSV holds every rule shown)
        </button>
      ) : null}

      <h3 className="mb-2 mt-8 font-serif text-lg" id={CHANGES_ANCHOR}>What changed in the last 90 days</h3>
      <div className="mb-2 flex flex-wrap items-center gap-1 text-xs" role="group" aria-label="Region" data-llr-regions="1">
        {[["", "Every region"] as [string, string], ...CHANGE_GROUPS].map(([k, label]) => {
          const n = k ? FILE.changes.filter((c) => c.group === k).length : FILE.changes.length;
          return <button key={k || "all"} type="button" aria-pressed={region === k} onClick={() => { setRegion(k); setChangeLimit(CHANGE_PAGE); }} className={`border px-2 py-1 ${region === k ? "border-ink font-semibold" : "border-rule"}`} data-llr-region={k || "all"}>{label} ({n})</button>;
        })}
      </div>
      <p className="mb-2 text-sm" role="status" data-llr-changes-shown={changes.length}>
        {changes.length} of {FILE.changes.length} changes{region ? `, ${groupWords(region)}` : ""}, newest first: <Tip tip={`Filings, orders, effective dates, amendments, denials, suspensions and hearings from 15 August to 13 November 2026, each read in its own document (${CHANGES_TABLE}). A change dated to a month is drawn as that month.`}>15 August to 13 November 2026</Tip>.
        {" "}<Download make={() => changesCsv(changes, FILE, address)} name={CHANGES_CSV_NAME} mark={{ "data-llr-csv": "changes" }}>CSV of these</Download>,{" "}
        <Download make={() => pythonReader(CHANGES_CSV_NAME, CHANGE_CSV_COLS, "the changes to large-load rules as filtered on /cost-of-power?view=allgrids")} name="erw-large-load-rule-changes.py" type="text/x-python" mark={{ "data-download": "python" }}>Python</Download>,{" "}
        <Download make={() => stataReader(CHANGES_CSV_NAME, CHANGE_CSV_COLS, "the changes to large-load rules as filtered on /cost-of-power?view=allgrids")} name="erw-large-load-rule-changes.do" type="text/plain" mark={{ "data-download": "stata" }}>Stata</Download>
      </p>
      <div className="overflow-x-auto" role="region" aria-label="Changes to large-load rules" tabIndex={0}>
        <table className="w-full border-collapse text-left text-sm" style={{ minWidth: 760 }} data-llr-changes="1">
          <caption className="sr-only">Changes to US utilities&apos; large-load rules in the 90 days to 13 November 2026, newest first: the date, the region, the utility, what happened, and the rule it changed</caption>
          <thead><tr className="border-b border-ink text-xs">{["Date", "Region", "Utility", "What happened", "Rule it changed"].map((h) => <th key={h} scope="col" className="px-2 py-1.5 font-normal">{h}</th>)}</tr></thead>
          <tbody>
            {changes.slice(0, changeLimit).map((c) => <ChangeRow key={c.id} c={c} openRule={openRule} />)}
            {FILE.held_changes.filter((h) => !region || h.id.startsWith(`${region}-`)).map((h) => (
              <tr key={h.id} className="border-b border-rule align-top" data-llr-change={h.id} data-llr-held="1">
                <td className="px-2 py-1.5"><Blank tip={HELD_ROW_TIP(h.utility)} table={CHANGES_TABLE} what="Date" /></td>
                <td className="px-2 py-1.5"><Blank tip={HELD_ROW_TIP(h.utility)} table={CHANGES_TABLE} what="Region" /></td>
                <td className="px-2 py-1.5">{h.utility}</td>
                <td className="px-2 py-1.5"><Blank tip={HELD_ROW_TIP(h.utility)} table={CHANGES_TABLE} what="What happened" /></td>
                <td className="px-2 py-1.5"><Blank tip={HELD_ROW_TIP(h.utility)} table={CHANGES_TABLE} what="Rule it changed" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {changes.length > changeLimit ? (
        <button type="button" className="mt-2 border border-rule px-2 py-1 text-sm" onClick={() => setChangeLimit(changeLimit + CHANGE_PAGE)} data-llr-more="changes">
          Next {Math.min(CHANGE_PAGE, changes.length - changeLimit)} ({Math.min(changeLimit, changes.length)} of {changes.length} drawn)
        </button>
      ) : null}
    </div>
  );
}

function HeadTip({ tip, onClick, k, children }: { tip: string; onClick: () => void; k: string; children: ReactNode }) {
  return (
    <span className="tip relative inline-block">
      <button type="button" aria-describedby={`llr-head-${k}`} onClick={onClick} className="cursor-pointer border-b border-dotted border-muted text-left text-inherit" data-llr-head={k}>{children}</button>
      <span role="tooltip" id={`llr-head-${k}`} data-tp="">{tip}</span>
    </span>
  );
}

function ChangeRow({ c, openRule }: { c: Change; openRule: (id: string) => void }) {
  const af = affectsOf(FILE, c);
  return (
    <tr className="border-b border-rule align-top" data-llr-change={c.id}>
      <td className="whitespace-nowrap px-2 py-1.5 tabular-nums">
        {c.date_kind === "date read" || c.date_printed !== c.date
          ? <Tip tip={c.date_kind === "date read" ? `The document prints ${c.date_printed || "no date"}; ${c.date} is the day it was read.` : `As the document prints it: ${c.date_printed}.`}>{c.date_printed || c.date}</Tip>
          : c.date}
      </td>
      <td className="px-2 py-1.5">{groupWords(c.group)}</td>
      <td className="px-2 py-1.5">{c.utility}{c.state ? ` (${c.state})` : ""}</td>
      <td className="px-2 py-1.5">
        <span className="font-semibold">{CHANGE_KIND_WORDS[c.kind] ?? c.kind}</span>: {c.what}{" "}
        <Tip tip={`As the document prints it: ${c.cite}${c.docket && c.docket !== "not published" ? ` Docket: ${c.docket}.` : ""}`} data={{ "llr-cite": "change" }}>source</Tip>{" "}
        <a href={c.url} title={`${c.title}, read ${c.read}`} data-llr-doc={c.id}>document</a>
      </td>
      <td className="px-2 py-1.5">
        {af.kind === "rule" ? (af.held
          ? <Blank tip={HELD_ROW_TIP(af.utility)} what="Rule it changed" />
          : <button type="button" className="text-left underline decoration-dotted" onClick={() => openRule(af.id)} data-llr-affects={af.id}>{c.rule}</button>)
          : af.kind === "registry" ? <Tip tip={`A document of the ERW's registry of the grid operators' and commissions' connection rules, not a row of the table above: warehouse/sources/${af.file}.`}>{c.rule}</Tip>
            : af.kind === "new" ? <Tip tip="A rule that is not yet a row of the table above: the change is its first filing or its first mention.">{c.rule}</Tip> : c.rule}
      </td>
    </tr>
  );
}

/** A and B, side by side: two rules, each field as the document prints it, whole. No difference is computed: the
 * fields are words. */
function AbRules({ a, b, clearA, clearB }: { a?: Line; b?: Line; clearA: () => void; clearB: () => void }) {
  const head = (l: Line | undefined, which: string, clear: () => void) => (
    <th scope="col" className="w-[42%] px-2 py-1.5 text-left font-normal" data-llr-ab-head={which}>
      {which}: {l ? <>{l.utility} ({l.state}) <button type="button" onClick={clear} className="ml-1 text-xs underline" aria-label={`Clear ${which}`}>clear</button></> : "none chosen"}
    </th>
  );
  const cell = (l: Line | undefined, draw: (l: Line) => ReactNode, what: string) => (
    <td className="px-2 py-1.5 align-top">{!l ? "" : l.held || !l.rule ? <Blank tip={HELD_ROW_TIP(l.utility)} what={what} /> : draw(l)}</td>
  );
  const rows: [string, (l: Line) => ReactNode][] = [
    ["Rule", (l) => <a href={l.rule!.url} title={`${l.rule!.title}, read ${l.rule!.read}`}>{l.rule!.name}</a>],
    ["Status", (l) => <Tip tip={statusTip(l.rule!)}>{l.rule!.status}, {dateWords(l.rule!.status_date)}</Tip>],
    ...FIELDS.map((f): [string, (l: Line) => ReactNode] => [FIELD_HEAD[f], (l) => <FieldView rule={l.rule!} f={f} whole />]),
  ];
  return (
    <section className="mb-4" aria-label="Two rules, A and B" data-llr-ab="1">
      <h3 className="mb-2 font-serif text-lg">Two rules, side by side</h3>
      <div className="overflow-x-auto" role="region" aria-label="Two rules, A and B, the table" tabIndex={0}>
        <table className="w-full border-collapse text-sm" style={{ minWidth: 640 }}>
          <thead><tr className="border-b border-ink text-xs"><th scope="col" className="px-2 py-1.5 text-left font-normal">As each document prints it</th>{head(a, "A", clearA)}{head(b, "B", clearB)}</tr></thead>
          <tbody>
            {rows.map(([h, draw]) => (
              <tr key={h} className="border-b border-rule">
                <th scope="row" className="px-2 py-1.5 text-left align-top font-normal">{FIELDS.some((f) => FIELD_HEAD[f] === h) ? <Tip tip={FIELD_TIP[FIELDS.find((f) => FIELD_HEAD[f] === h)!]}>{h}</Tip> : h === "Status" ? <Tip tip={Object.entries(STATUS_TIP).map(([k, v]) => `${k}: ${v}`).join(" ")}>{h}</Tip> : h}</th>
                {cell(a, draw, h)}{cell(b, draw, h)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
