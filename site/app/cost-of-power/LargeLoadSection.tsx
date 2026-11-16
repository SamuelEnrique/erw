// Chain 302 (session 7201): the large-load rules of US utilities under the All grids tab of /cost-of-power, and the
// lines the tab's Utility and Time to connect cells draw to open a row's rule. Drawn on the server from the page file
// (lib/sitingdata.ts, LARGE_LOAD): the counts, each a check key (largeload|..., lib/largeloadrules.ts, largeLoadStat);
// the panel a row of the tab opens (its utilities' rules in full, the rules that bind every utility of its state, and
// what was read and not found); then the table and the changes (LargeLoadRules.tsx, on the client). The tool prints
// what each document prints and takes no view. No database is read: the tab reads files only.
import { Num } from "@/components/Num";
import { SiteLink } from "@/components/SiteLink";
import { HeldCard, RuleCard, Tip } from "@/components/largeload/parts";
import { LICENSE_NEEDED, CHANGES_ANCHOR, RULES_ANCHOR, RULES_TABLE, CHANGES_TABLE, LAWS_TABLE, RULE_STATUSES, STATUS_TIP, lawStates, lawsHref, lineOf, rowRules, statesOf, type RowRules } from "@/lib/largeloadrules";
import { GRID_NAMES, rowOf, rowUtilities, sitingHref, type Row, type SitingInputs } from "@/lib/siting";
import { LARGE_LOAD, SITING_FILES } from "@/lib/sitingdata";
import { LargeLoadRules, type Opened } from "./LargeLoadRules";

export const ROW_ANCHOR = "large-load-rule";
const READ_WORDS = "the 166 utilities whose large-load rules the ERW read on 13 and 14 November 2026 (docs/methods/large_load_research.md)";
const stamp = (s: string) => (/^\d{8}T/.test(s) ? `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}` : s);

export function rulesOfRow(r: Row): RowRules & { state: string | null; names: string[] } {
  const { state, utilities } = rowUtilities(SITING_FILES, r);
  return { ...rowRules(LARGE_LOAD, utilities, state, r.grid), state, names: utilities.map((u) => u.name) };
}
/** The address that opens a row's rule under the table. */
export const rowRuleHref = (x: SitingInputs, r: Row) => `${sitingHref(x)}&llrow=${encodeURIComponent(r.id)}#${ROW_ANCHOR}`;
const stateHref = (x: SitingInputs, state: string) => `${sitingHref(x)}&rstate=${encodeURIComponent(state)}#${RULES_ANCHOR}`;
const noneWhy = (rr: ReturnType<typeof rulesOfRow>) => [
  ...rr.none.map((n) => `${n.name}: ${n.words} (${n.note})`),
  rr.unread.length ? `${rr.unread.map((u) => u.name).join(", ")}: not among ${READ_WORDS}.` : "",
  !rr.none.length && !rr.unread.length ? "No utility is named for this row." : "",
].filter(Boolean).join(" ");

/** The line a cell of the hub table draws: a link that opens the rule of the row's utility, or, in the same place,
 * that none was found or none was read, with why on hover. `cell` is the column it stands in. */
export function RuleLine({ r, x, cell }: { r: Row; x: SitingInputs; cell: "utility" | "connect" }) {
  const rr = rulesOfRow(r), ids = [...rr.own, ...rr.statewide];
  const rules = ids.map((id) => lineOf(LARGE_LOAD, id)).filter((l) => !!l);
  const first = rules[0];
  if (!ids.length || !first) {
    const words = rr.none.length ? "no large-load rule found" : "no large-load rule read";
    return (
      <span className="block text-xs" data-llr="cell" {...{ [`data-${cell}-rule`]: "0" }}>
        {cell === "connect" ? "utility: " : ""}<Tip tip={noneWhy(rr)} data={{ "cell-words": "1" }}>{words}</Tip>
        {cell === "utility" && rr.state && rr.inState ? <>, <SiteLink href={stateHref(x, rr.state)} gate="plain" data-llr-state-link={rr.state}>{rr.inState} in {rr.state}</SiteLink></> : null}
      </span>
    );
  }
  const what = `${first.utility}${first.rule ? `: ${first.rule.status}, ${first.rule.status_date}` : `: ${LICENSE_NEEDED}`}${ids.length > 1 ? `, and ${ids.length - 1} more` : ""}. Opens under the table.`;
  if (cell === "utility") {
    const label = rr.own.length ? (ids.length === 1 ? "large-load rule" : `${ids.length} large-load rules`) : ids.length === 1 ? "state's large-load rule" : `${ids.length} state large-load rules`;
    return <span className="block text-xs" data-llr="cell" data-utility-rule={ids.length}><SiteLink href={rowRuleHref(x, r)} gate="plain" title={what} data-llr-open-row={r.id}>{label}</SiteLink></span>;
  }
  const timed = rules.some((l) => l.rule && (l.rule.fields.study_timeline?.kind === "value" || l.rule.fields.connection_timeline?.kind === "value"));
  return (
    <span className="block text-xs" data-llr="cell" data-connect-rule={ids.length}>
      utility: <SiteLink href={rowRuleHref(x, r)} gate="plain" title={what} data-llr-open-row={r.id}>{timed ? "its rule's timed steps" : "its rule"}</SiteLink>
      {timed ? null : <>, <Tip tip="The rule read prints no study time and no time to energize, or the row is held for a license." data={{ "cell-words": "1" }}>no timed step printed</Tip></>}
    </span>
  );
}

/** The panel a row of the tab opens: its utilities' rules in full, then the rules binding every utility of its state. */
function RowPanel({ r, x }: { r: Row; x: SitingInputs }) {
  const rr = rulesOfRow(r), laws = lawStates(LARGE_LOAD);
  const card = (id: string) => {
    const l = lineOf(LARGE_LOAD, id);
    if (!l) return null;
    const st = statesOf(l.state).filter((s) => laws.includes(s));
    return <div key={id} className="mt-2">{l.rule
      ? <RuleCard rule={l.rule} lawsHref={st.length ? <span data-llr-laws={st.join(",")}>State law: {st.map((s, i) => <span key={s}>{i ? ", " : ""}<SiteLink href={lawsHref(s)} gate="plain">{s}</SiteLink></span>)}</span> : undefined} />
      : <HeldCard rule={l} />}</div>;
  };
  return (
    <section id={ROW_ANCHOR} className="mb-6 max-w-4xl border border-rule bg-paper px-4 py-3 text-sm" aria-label={`The large-load rule at ${GRID_NAMES[r.grid]} ${r.label}`} data-llr-row-panel={r.id}>
      <h3 className="font-serif text-lg">The large-load rule at {GRID_NAMES[r.grid]} {r.label} <SiteLink href={`${sitingHref(x)}#${RULES_ANCHOR}`} gate="plain" className="ml-2 text-xs underline">Close</SiteLink></h3>
      {rr.own.length ? <><p className="mt-1">The rule of a utility this row names ({rr.names.join(", ")}):</p>{rr.own.map(card)}</> : null}
      {rr.statewide.length ? <><p className="mt-3">Binding every utility of {rr.state}{LARGE_LOAD.statewide[rr.statewide[0]]?.grid ? ` in ${GRID_NAMES[r.grid]}` : ""}:</p>{rr.statewide.map(card)}</> : null}
      {rr.none.map((n) => <p key={n.number} className="mt-2" data-llr-none={n.number}>{n.name}: <Tip tip={`${n.words} (${n.note})`}>no large-load rule found</Tip>.</p>)}
      {rr.unread.length ? <p className="mt-2" data-llr-unread={rr.unread.length}>{rr.unread.map((u) => u.name).join(", ")}: <Tip tip={`Not among ${READ_WORDS}.`}>no large-load rule read</Tip>.</p> : null}
      {!rr.names.length ? <p className="mt-2">No utility is named for this row.</p> : null}
      {rr.state && rr.inState ? <p className="mt-2" data-llr-in-state={rr.state}><SiteLink href={stateHref(x, rr.state)} gate="plain">Every rule read in {rr.state}</SiteLink>: <Num check={`largeload|rules|state|${rr.state}`} raw={rr.inState}>{rr.inState}</Num>, in the table below.</p> : null}
    </section>
  );
}

export function LargeLoadSection({ q, x }: { q: Record<string, string | undefined>; x: SitingInputs }) {
  const f = LARGE_LOAD, n = f.rules.length + f.held_rules.length;
  const row = q.llrow ? rowOf(SITING_FILES, q.llrow) : undefined;
  const opened: Opened = { state: q.rstate ?? "", grid: q.rgrid ?? "", status: q.rstatus ?? "", find: q.rq ?? "", sort: q.rsort ?? "", dir: q.rdir ?? "", a: q.ra ?? "", b: q.rb ?? "", rule: q.rule ?? "", region: q.rregion ?? "" };
  const statuses = RULE_STATUSES.filter((s) => f.rules.some((r) => r.status === s));
  return (
    <section className="mt-4 min-w-0 lg:col-span-2" id={RULES_ANCHOR} aria-label="Large-load rules by utility" data-llr="1">
      <h2 className="mb-2 border-b border-rule pb-1 font-serif text-xl text-accent">Large-load rules by utility</h2>
      <p className="mb-3 max-w-4xl text-sm" data-llr-counts="1">
        <Num check="largeload|rules|all" raw={n}>{n}</Num>{" "}
        <Tip tip={`The connection rules a large load meets at a utility: tariffs, special contracts, commission orders and statewide rules, each read in its own document and audited by five independent readers (${RULES_TABLE}, written ${stamp(f.retrieved[RULES_TABLE] ?? "")}). Each value is the document's own words with its page or section on hover. The tool states what each document prints and takes no view.`}>rules of US utilities and state commissions for a large load</Tip>:{" "}
        {statuses.map((s, i) => <span key={s}>{i ? ", " : ""}<Num check={`largeload|rules|status|${s}`} raw={f.counts.rules[s]}>{f.counts.rules[s]}</Num> <Tip tip={STATUS_TIP[s]}>{s}</Tip></span>)}
        {f.held_rules.length ? <>, and <Num check="largeload|rules|held" raw={f.held_rules.length}>{f.held_rules.length}</Num> <Tip tip={`${LICENSE_NEEDED}: read in a document whose publisher's terms ask permission before it is shown. The utility is named and every other cell is blank.`}>held</Tip></> : null}.
        {" "}<a href={`#${CHANGES_ANCHOR}`}><Num check="largeload|changes|public" raw={f.changes.length}>{f.changes.length}</Num> changes in the last 90 days</a> below ({CHANGES_TABLE});{" "}
        <SiteLink href={lawsHref()} gate="plain"><Num check="largeload|laws|public" raw={f.laws.length}>{f.laws.length}</Num> state laws and bills</SiteLink> on Policy ({LAWS_TABLE}).
      </p>
      {row ? <RowPanel r={row} x={x} /> : null}
      <LargeLoadRules opened={opened} address={sitingHref(x)} />
    </section>
  );
}
