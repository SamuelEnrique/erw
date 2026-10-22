"use client";
// The /datacenters table (session 16; session 22: news, operator lists and queues): filters in one row, one row per facility, source links on each.
// Session 240: the list grouped by operator. One table, so every group shares its columns: a group is a head row (the
// operator, its facilities and the megawatts the page's sums count for it) and its rows, which open and close; the
// largest operator by megawatts comes first and is open as the page opens. A filter opens every group that has a row
// left. The rows inside a group are as they were, in the same order; every row stays in the page, open or closed.
import { useMemo, useState } from "react";
import { Num } from "@/components/Num";
import { FoldRows } from "@/components/tool/ToolPage";
import { cancelled } from "@/lib/largeload";

export type Facility = {
  id: string;
  operator: string;
  developer: string;
  site: string;
  state: string;
  county: string;
  city: string;
  country: string; // session 166: "US" when a US state is stated, else "" (no source records a country)
  mw: number | null;
  phase: string;
  status: string;
  plannedYear: string;
  power: string;
  utility: string;
  confidence: number | null;
  placed: boolean;
  firstStory: string;
  storyUrls: string[];
  kind: string; // session 22: news, operator or queue (the first source); kinds lists every source's kind
  kinds: string[];
  siteType: string;
  mwSpan: string;
  queueMw: number | null;
  sourceUrls: string[];
  /** session 719: the All grids tab's row for this facility (lib/siting.ts, facilitySite), and its address; none where
   *  neither its county nor its state places it in one grid */
  siting?: { grid: string; row: string; how: string; why: string; href: string } | null;
};

const KIND_LABEL: Record<string, string> = { news: "news", operator: "operator list", queue: "ISO queue" };
// session 166: a row whose story or operator page states no US state: no source the ERW reads records a country
const NO_COUNTRY = "country not stated";
const NO_COUNTRY_WHY = "No source the ERW reads states a country. This row may be outside the US, or a US site whose story or operator page names no state. It is left out of the totals and the bars.";

const uniq = (xs: string[]) => Array.from(new Set(xs.filter(Boolean))).sort();
const label = (s: string) => s.replace("_", " ");
const NO_OPERATOR = "Operator not stated";
const whole = (v: number) => Math.round(v).toLocaleString("en-US");

export type OperatorGroup = { operator: string; rows: Facility[]; mw: number; nMw: number };
/** The rows by operator, the largest first: by the megawatts the page's sums count (a named US state, not cancelled,
 *  MW stated), then by the number of facilities, then by name; the rows with no operator stated are the last group.
 *  The rows keep the order they come in. */
export function byOperator(rows: Facility[]): OperatorGroup[] {
  const m = new Map<string, OperatorGroup>();
  for (const f of rows) {
    const g = m.get(f.operator) ?? { operator: f.operator, rows: [], mw: 0, nMw: 0 };
    g.rows.push(f);
    if (f.country === "US" && !cancelled(f.status) && f.mw !== null) { g.mw += f.mw; g.nMw += 1; }
    m.set(f.operator, g);
  }
  // the rows no source names an operator for are not an operator: their group comes last, whatever its megawatts
  return [...m.values()].sort((a, b) => Number(!a.operator) - Number(!b.operator) || b.mw - a.mw || b.rows.length - a.rows.length || a.operator.localeCompare(b.operator));
}

function Select({ name, value, set, options }: { name: string; value: string; set: (v: string) => void; options: string[] }) {
  return (
    <label className="flex flex-col gap-1 text-xs text-muted">
      {name}
      <select value={value} onChange={(e) => set(e.target.value)} className="border border-rule bg-panel px-2 py-1 text-sm text-ink">
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {label(o)}
          </option>
        ))}
      </select>
    </label>
  );
}

export function DatacentersTable({ rows }: { rows: Facility[] }) {
  const [state, setState] = useState("");
  const [status, setStatus] = useState("");
  const [operator, setOperator] = useState("");
  const [minMw, setMinMw] = useState("");
  const [kind, setKind] = useState("");
  const [country, setCountry] = useState("");
  const countryKey = (f: Facility) => f.country || NO_COUNTRY;
  const shown = useMemo(
    () =>
      rows
        .filter((f) => (!state || f.state === state) && (!status || f.status === status) && (!operator || f.operator === operator))
        .filter((f) => !kind || f.kinds.includes(kind))
        .filter((f) => !country || countryKey(f) === country)
        .filter((f) => !minMw || (f.mw !== null && f.mw >= Number(minMw)))
        .sort((a, b) => b.firstStory.localeCompare(a.firstStory) || a.operator.localeCompare(b.operator) || a.site.localeCompare(b.site)),
    [rows, state, status, operator, minMw, kind, country],
  );
  const filtered = !!(state || status || operator || minMw || kind || country);
  const groups = useMemo(() => byOperator(shown), [shown]);
  // a group's own click wins; until then the first group is open, or every group while a filter is on
  const [toggled, setToggled] = useState<Record<string, boolean>>({});
  const isOpen = (g: OperatorGroup, i: number) => toggled[g.operator] ?? (filtered || i === 0);
  const allOpen = groups.every(isOpen);
  const blank = <span className="text-muted">not stated</span>;
  return (
    <section aria-label="Facilities" id="every-site">
      <div className="mb-2 flex flex-wrap items-end gap-3">
        <Select name="Country" value={country} set={setCountry} options={uniq(rows.map(countryKey))} />
        <Select name="State" value={state} set={setState} options={uniq(rows.map((f) => f.state))} />
        <Select name="Status" value={status} set={setStatus} options={uniq(rows.map((f) => f.status))} />
        <Select name="Operator" value={operator} set={setOperator} options={uniq(rows.map((f) => f.operator))} />
        <Select name="Source" value={kind} set={setKind} options={uniq(rows.flatMap((f) => f.kinds))} />
        <label className="flex flex-col gap-1 text-xs text-muted">
          MW at least
          <input
            value={minMw}
            onChange={(e) => setMinMw(e.target.value.replace(/[^0-9.]/g, ""))}
            inputMode="decimal"
            placeholder="any"
            className="w-24 border border-rule bg-panel px-2 py-1 text-sm text-ink"
          />
        </label>
        <span className="pb-1 text-sm text-muted">
          {shown.length} of {rows.length} facilities, {groups.length} {groups.length === 1 ? "operator" : "operators"}
        </span>
        {/* session 282: every filter back to its default, "any" */}
        <button type="button" data-reset="1" onClick={() => { setCountry(""); setState(""); setStatus(""); setOperator(""); setKind(""); setMinMw(""); }} className="border border-rule px-2 py-1 text-sm">Reset the filters</button>
        <button type="button" data-fold-all="1" aria-pressed={allOpen} onClick={() => setToggled(Object.fromEntries(groups.map((g) => [g.operator, !allOpen])))} className="border border-rule px-2 py-1 text-sm">
          {allOpen ? "Close every operator" : "Open every operator"}
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th className="py-1 pr-3 font-normal">First reported</th>
              <th className="py-1 pr-3 font-normal">Operator, site</th>
              <th className="py-1 pr-3 font-normal">Place</th>
              <th className="py-1 pr-3 text-right font-normal">MW</th>
              <th className="py-1 pr-3 font-normal">Status</th>
              <th className="py-1 pr-3 font-normal">Planned year</th>
              <th className="py-1 pr-3 font-normal">Power</th>
              <th className="py-1 font-normal">Sources</th>
            </tr>
          </thead>
          {groups.map((g, i) => (
            <FoldRows key={g.operator || "none"} id={g.operator || "none"} cols={8} open={isOpen(g, i)} onToggle={() => setToggled((t) => ({ ...t, [g.operator]: !isOpen(g, i) }))}
              title={g.operator || NO_OPERATOR}
              meta={filtered
                ? <>{g.rows.length} {g.rows.length === 1 ? "facility" : "facilities"} shown{g.nMw ? <>, {whole(g.mw)} MW stated</> : ", no MW stated"}</>
                : <><Num check={`datacenters|operator_count|${g.operator}`} raw={g.rows.length}>{g.rows.length}</Num> {g.rows.length === 1 ? "facility" : "facilities"}{g.nMw ? <>, <Num check={`datacenters|operator_mw|${g.operator}`} raw={g.mw}>{whole(g.mw)}</Num> MW stated (US rows not cancelled)</> : ", no MW stated"}</>}>
            {g.rows.map((f) => (
              <tr key={f.id} className="border-b border-rule align-top">
                <td className="py-1 pr-3 tabular-nums">
                  {f.firstStory ? f.firstStory.slice(0, 10) : <span className="text-muted">{f.kind === "news" ? "not stated" : "not in the news"}</span>}
                </td>
                <td className="py-1 pr-3">
                  <div>{f.operator || blank}</div>
                  {f.site ? <div className="text-xs">{f.site}</div> : null}
                  {f.developer && f.developer !== f.operator ? <div className="text-xs text-muted">developer {f.developer}</div> : null}
                  {f.phase ? <div className="text-xs text-muted">{f.phase}</div> : null}
                </td>
                <td className="py-1 pr-3">
                  {[f.city, f.county, f.state].filter(Boolean).join(", ") || blank}
                  {f.country ? null : <div className="text-xs text-muted" title={NO_COUNTRY_WHY} data-no-country="1">{NO_COUNTRY}</div>}
                  {f.placed ? <div className="text-xs text-muted">on the map</div> : null}
                  {f.siting ? <div className="text-xs" data-facility-siting={f.siting.how}><a href={f.siting.href} className="underline" aria-label={`${f.site || f.operator}: what a load of its size pays at ${f.siting.row}, on the All grids tab. ${f.siting.why}`}>on All grids</a>{" "}<span className="text-muted">({f.siting.how === "county" ? "its county" : f.siting.how === "utility" ? "its utility" : "its state"})</span></div> : null}
                </td>
                <td className="py-1 pr-3 text-right tabular-nums">
                  {f.mw === null ? blank : f.mw.toLocaleString("en-US")}
                  {f.mwSpan ? <div className="text-xs text-muted">&ldquo;{f.mwSpan}&rdquo;</div> : null}
                  {f.queueMw !== null ? <div className="text-xs text-muted">queue: {f.queueMw.toLocaleString("en-US")} MW generation or storage</div> : null}
                </td>
                <td className="py-1 pr-3">{f.status ? label(f.status) : blank}</td>
                <td className="py-1 pr-3 tabular-nums">{f.plannedYear || blank}</td>
                <td className="py-1 pr-3">
                  {f.power || f.utility ? [f.power, f.utility ? `utility ${f.utility}` : ""].filter(Boolean).join("; ") : blank}
                </td>
                <td className="py-1">
                  <div className="text-xs text-muted">{f.kinds.map((k) => KIND_LABEL[k] ?? k).join(", ")}</div>
                  {f.sourceUrls.map((u, i) => (
                    <a key={u} href={u} target="_blank" rel="noreferrer" className="mr-2">
                      {i + 1}
                    </a>
                  ))}
                  {f.confidence !== null ? <div className="text-xs text-muted">model confidence {f.confidence}</div> : null}
                </td>
              </tr>
            ))}
            </FoldRows>
          ))}
        </table>
      </div>
    </section>
  );
}
