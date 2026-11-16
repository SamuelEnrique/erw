"use client";
// Chain 302 (session 7201): the states' laws and bills on large electric loads, in the monitor view of /policy
// (?view=monitor), under the records. One row a law or a bill of state_large_load_laws (the 2025 and 2026 sessions,
// each read in the legislature's own text): its status with the text's cite on hover, its effective date, the smallest
// load it names and what it requires, topic by topic, each with its words and its cite on hover. The block follows the
// monitor's State filter, so the All grids tab's link from a rule's state (/policy?view=monitor&state=TX#large-load-laws)
// opens on that state's laws. A law held for a license is drawn with its state and bill and every other cell blank,
// "license needed" on hover. The rows come from the page (data/siting/large_load_rules.json, read on the server); what is
// shown is lib/largeloadrules.ts, tested by scripts/test-large-load-rules.mjs.
import { useMemo } from "react";
import { Blank, Tip } from "@/components/largeload/parts";
import { TipPlace } from "@/components/largeload/TipPlace";
import { Download } from "@/components/largeload/Download";
import { SiteLink } from "@/components/SiteLink";
import { LAWS_ANCHOR, LAWS_CSV_NAME, LAWS_TABLE, LAW_CSV_COLS, LAW_STATUSES, LAW_STATUS_TIP, LICENSE_NEEDED, NOT_SHOWN, cut, dateWords, lawSearchOf, lawStatusTip, lawsCsv, pythonReader, requirementsOf, rulesHref, stataReader, statusDateWords,
  type HeldLaw, type Law, type LawSearch } from "@/lib/largeloadrules";

// session 7204: `searches` is what the research records for a state with no law in the table; `rules` and `changes`
// count the utilities' rules and their changes by state (the All grids tab's table), for the line that links them
export type LawsProp = { laws: Law[]; held: HeldLaw[]; built: string; retrieved: Record<string, string>; searches?: LawSearch[]; rules?: Record<string, number>; changes?: Record<string, number> };
const HELD_TIP = (bill: string) => `${LICENSE_NEEDED}: the ERW read ${bill} on a site whose terms ask permission before it is shown. The bill is counted and its values are not printed.`;
const WHAT = "the states' large-load laws as filtered on /policy?view=monitor";

export function StateLaws({ file, states, clearStates }: { file: LawsProp; states: string[]; clearStates: () => void }) {
  const keep = (s: string) => !states.length || states.includes(s);
  const laws = useMemo(() => file.laws.filter((l) => keep(l.state)), [file, states]);   // eslint-disable-line react-hooks/exhaustive-deps
  const held = useMemo(() => file.held.filter((l) => keep(l.state)), [file, states]);   // eslint-disable-line react-hooks/exhaustive-deps
  const total = file.laws.length + file.held.length, shown = laws.length + held.length;
  // session 7204 (the read of /policy, rows 1 and 2): a chosen state with no row in the table is never "no law": the
  // research found none where it searched, could not read the site, read a bill it does not show, or did not search
  const haveLaw = new Set([...file.laws, ...file.held].map((l) => l.state));
  const without = states.filter((s) => !haveLaw.has(s)).map((s) => ({ state: s, ...lawSearchOf(file.searches, s) }));
  const notShown = without.filter((w) => w.kind === "withheld");
  const others = (file.searches ?? []).filter((x) => !haveLaw.has(x.state));
  // session 7600 (the browser read, row 9): the bills read and not shown that the table draws as rows, counted in the
  // line above it: with every state, 29 rows stood under "28 of 28 shown"
  const withheldRows = states.length ? notShown : others.filter((x) => x.kind === "withheld").map((x) => ({ state: x.state, ...lawSearchOf(file.searches, x.state) }));
  const ruleStates = (states.length ? states : []).filter((s) => (file.rules?.[s] ?? 0) > 0);
  const byStatus = LAW_STATUSES.map((s) => [s, file.laws.filter((l) => l.status === s).length] as const).filter(([, n]) => n);
  return (
    <section className="mt-8" id={LAWS_ANCHOR} aria-label="State laws on large loads" data-llr="laws" data-laws-shown={shown}>
      <h3 className="mb-1 font-serif text-lg">State laws on large loads</h3>
      <p className="mb-2 text-xs" data-laws-counts="1">
        <span data-check="largeload|laws|public" data-raw={file.laws.length}>{file.laws.length}</span>{" "}
        <Tip tip={`Laws and bills of the 2025 and 2026 sessions that set terms for large electric loads, each read in the legislature's own text or the state code (${LAWS_TABLE}, written ${file.retrieved[LAWS_TABLE]?.slice(0, 8).replace(/^(\d{4})(\d{2})(\d{2})$/, "$1-$2-$3") ?? ""}). Each value is the text's own words with its page or section on hover.`}>laws and bills</Tip>:{" "}
        {byStatus.map(([s, n], i) => <span key={s}>{i ? ", " : ""}<span data-check={`largeload|laws|status|${s}`} data-raw={n}>{n}</span> <Tip tip={LAW_STATUS_TIP[s]}>{s}</Tip></span>)}
        {file.held.length ? <>, and <span data-check="largeload|laws|held" data-raw={file.held.length}>{file.held.length}</span> <Tip tip={`${LICENSE_NEEDED}: read on a site whose terms ask permission before it is shown.`}>held</Tip></> : null}.
        {" "}{shown} of {total} shown{withheldRows.length ? <>, and <span data-laws-not-shown={withheldRows.length}>{withheldRows.length}</span> <Tip tip={`A bill the ERW read and does not show (${withheldRows.map((w) => `${w.state} ${w.bill}`).join(", ")}): its row names the bill and its cells are blank, with the reason on hover. It is not a row of ${LAWS_TABLE}, so it is not among the ${total}.`}>read and not shown</Tip></> : null}{states.length ? <> (the State filter: {states.join(", ")}; <button type="button" className="underline" onClick={clearStates} data-laws-all="1">every state</button>)</> : null}
        {" · "}<Download make={() => lawsCsv(laws, held, file, "/policy?view=monitor")} name={LAWS_CSV_NAME} mark={{ "data-laws-csv": "1" }}>CSV of these</Download>,{" "}
        <Download make={() => pythonReader(LAWS_CSV_NAME, LAW_CSV_COLS, WHAT)} name="erw-state-large-load-laws.py" type="text/x-python" mark={{ "data-download": "python" }}>Python</Download>,{" "}
        <Download make={() => stataReader(LAWS_CSV_NAME, LAW_CSV_COLS, WHAT)} name="erw-state-large-load-laws.do" type="text/plain" mark={{ "data-download": "stata" }}>Stata</Download>
      </p>
      {without.length ? (
        <p className="mb-2 text-sm" data-laws-without={without.map((w) => w.state).join(",")}>
          {without.map((w, i) => <span key={w.state} data-law-search={w.kind} data-law-search-state={w.state}>{i ? "; " : ""}{w.state}: <Tip tip={w.tip}>{w.kind === "withheld" ? `${w.bill}, ${w.words}` : w.words}</Tip></span>)}.
          {" "}<Tip tip={`${LAWS_TABLE} has rows for ${haveLaw.size} states. A state with none is not a state with no law: the hover on each says what the ERW's read found, or did not reach.`}>The table has {total} rows for other states</Tip>.
        </p>
      ) : null}
      {ruleStates.length ? (
        <p className="mb-2 text-sm" data-laws-rules="1">
          The utilities&apos; own large-load rules: {ruleStates.map((s, i) => <span key={s}>{i ? ", " : ""}<SiteLink href={rulesHref(s)} gate="plain" data-laws-rules-state={s}>{file.rules![s]} in {s}</SiteLink>{file.changes?.[s] ? ` (${file.changes[s]} ${file.changes[s] === 1 ? "change" : "changes"} in the last 90 days)` : ""}</span>)}, on What a datacenter pays.
        </p>
      ) : null}
      {!states.length && file.rules ? (
        <p className="mb-2 text-sm" data-laws-rules="all">
          <SiteLink href={rulesHref()} gate="plain">The utilities&apos; own large-load rules</SiteLink>, by state, are on What a datacenter pays.
        </p>
      ) : null}
      {shown === 0 && !notShown.length ? null : (
        <div className="overflow-x-auto" role="region" aria-label="State laws on large loads, the table" tabIndex={0}>
          <table className="w-full text-sm" style={{ minWidth: 860 }} data-laws-table="1">
            <caption className="sr-only">State laws and bills on large electric loads, one row each: the state, the bill, its status and date, its effective date, the smallest load it names, and what it requires</caption>
            <thead><tr className="border-b border-rule text-left text-xs text-muted">{["State", "Bill", "Status", "Effective", "Smallest load", "Requires"].map((h) => <th key={h} scope="col" className="py-1 pr-3 font-normal">{h}</th>)}</tr></thead>
            <tbody>
              {laws.map((l) => (
                <tr key={l.id} className="border-b border-rule/60 align-top" data-law={l.id} data-law-state={l.state}>
                  <td className="py-1 pr-3">{l.state}</td>
                  <td className="py-1 pr-3" style={{ minWidth: "14rem" }}>
                    <a href={l.url} title={`${l.doc}, read ${l.read}`} data-law-doc={l.id}>{l.bill}</a>
                    <span className="block text-xs">{l.title.length > 120 ? <Tip tip={l.title} plain>{cut(l.title, 118)}</Tip> : l.title}{l.notes ? <> <Tip tip={l.notes} data={{ "llr-notes": "1" }}>notes</Tip></> : null}</span>
                  </td>
                  <td className="py-1 pr-3"><Tip tip={lawStatusTip(l)} data={{ "law-status": l.status }}>{l.status}</Tip><span className="block whitespace-nowrap text-xs tabular-nums">{statusDateWords(l.status_date)}</span></td>
                  <td className="whitespace-nowrap py-1 pr-3 tabular-nums">{dateWords(l.effective)}</td>
                  <td className="py-1 pr-3" style={{ minWidth: "11rem" }}>{l.threshold && l.threshold !== "not published"
                    ? <Tip tip={`${l.threshold} As the text prints it: ${l.threshold_cite}`} data={{ "law-threshold": "1" }}>{cut(l.threshold, 90)}</Tip>
                    : <Tip tip={`The text read names no smallest load. ${l.threshold_cite.replace(/^searched:\s*/i, "Searched: ")}`.trim()}>not published</Tip>}</td>
                  <td className="py-1 pr-3" data-law-requires={l.id}>
                    {/* session 7204 (the read of /policy, row 9): a topic a law names twice is numbered, so two requirements
                        under one topic do not read as one word drawn twice */}
                    {requirementsOf(l).map((p, i, all) => { const same = all.filter((x) => x.topic === p.topic).length, nth = all.slice(0, i + 1).filter((x) => x.topic === p.topic).length;
                      return <span key={i} className="mr-2 inline-block"><Tip tip={`${p.words} As the text prints it: ${p.cite}`} data={{ "law-topic": p.topic }}>{same > 1 ? `${p.topic} (${nth} of ${same})` : p.topic}</Tip></span>; })}
                  </td>
                </tr>
              ))}
              {held.map((l) => (
                <tr key={l.id} className="border-b border-rule/60 align-top" data-law={l.id} data-law-state={l.state} data-law-held="1">
                  <td className="py-1 pr-3">{l.state}</td>
                  <td className="py-1 pr-3">{l.bill}</td>
                  {["Status", "Effective", "Smallest load", "Requires"].map((h) => <td key={h} className="py-1 pr-3"><Blank tip={HELD_TIP(l.bill)} table={LAWS_TABLE} what={h} /></td>)}
                </tr>
              ))}
              {/* session 7204: a bill the research read and withholds (Texas S.B. 6: its copy sits on a path the legislature's
                  robots file disallows) is a row of its state: the bill named, its cells blank, the reason on hover */}
              {withheldRows.map((w) => (
                <tr key={`${w.state}-${w.bill}`} className="border-b border-rule/60 align-top" data-law-withheld={w.state} data-law-state={w.state}>
                  <td className="py-1 pr-3">{w.state}</td>
                  <td className="py-1 pr-3">{w.bill}</td>
                  {["Status", "Effective", "Smallest load", "Requires"].map((h) => <td key={h} className="py-1 pr-3"><Blank tip={w.tip} table={LAWS_TABLE} what={h} label={NOT_SHOWN} /></td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {/* session 7204: with no state chosen, the states the table has no row for, each with what the read found */}
      {!states.length && others.length ? (
        <p className="mt-2 text-xs" data-laws-searched={others.length}>
          No row for {others.length} states the ERW searched:{" "}
          {others.map((x, i) => { const w = lawSearchOf(file.searches, x.state); return <span key={x.state} data-law-search={w.kind} data-law-search-state={x.state}>{i ? ", " : ""}<Tip tip={w.tip}>{x.state}{w.kind === "none found" ? "" : ` (${w.kind === "withheld" ? `${w.bill}, ${w.words}` : w.words})`}</Tip></span>; })}.
          {" "}A state named with nothing after it: <Tip tip="No law or bill on large loads was found where the ERW searched. It is not proof that none exists: each state's hover says what was searched.">none found where searched</Tip>.
        </p>
      ) : null}
      {/* session 7600: this block's hovers, placed against the window (the table scrolls sideways in its frame) */}
      <TipPlace />
    </section>
  );
}
