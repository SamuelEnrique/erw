// The /datacenters body (session 16; session 22: the combined table): the summary strip, the table and the citation.
// Session 166 (accuracy): the Status column and filter show the cleaned status (the entities vocabulary: planned,
// under_construction, operating, withdrawn), never a source's raw field; the totals and the two bars count only rows
// in a named US state whose status is not withdrawn (cancelled); a row without a US state stays in the table and
// reads "country not stated" (no source records a country).
// Session 240: on the brand. The strip is a top block of three numbers (the facilities held, the megawatts stated with
// what the sum counts by status, and the facilities first reported this week), then what changed this week with what
// the table does not hold said in words, the two bars, and the list grouped by operator (DatacentersTable).
import type { ReactNode } from "react";
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import type { EntityRow } from "@/lib/data";
import { count } from "@/lib/format";
import { cancelled, countryOf } from "@/lib/largeload";
import { Fold, HeadlineNumber, HeadlineRow, Tip, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { DatacentersTable, type Facility } from "./DatacentersTable";
import { facilityHref, facilitySite } from "@/lib/siting";
import { FACILITY_GRID, SITING_FILES } from "@/lib/sitingdata";

export function toFacility(r: EntityRow): Facility {
  const x = r.extra ?? {};
  return {
    id: r.entity_id,
    operator: r.operator ?? "",
    developer: x.developer ?? "",
    site: x.site_name ?? r.name ?? "",
    state: x.state ?? "",
    county: x.county ?? "",
    city: x.city ?? "",
    country: countryOf(x.country, x.state),
    mw: r.capacity_mw === null ? null : Number(r.capacity_mw),
    phase: x.phase ?? "",
    status: r.status ?? "",
    plannedYear: x.planned_year ?? "",
    power: x.power_source ?? "",
    utility: x.utility ?? "",
    confidence: x.confidence ? Number(x.confidence) : null,
    placed: ["county", "place", "operator", "point"].includes(x.geo_precision ?? ""),
    firstStory: x.first_story_at ?? "",
    storyUrls: (x.story_urls ?? r.source_url ?? "").split(";").filter(Boolean),
    kind: x.kind ?? "",
    kinds: (x.kinds ?? x.kind ?? "").split(";").filter(Boolean),
    siteType: x.site_type ?? "",
    mwSpan: x.mw_span ?? "",
    queueMw: x.queue_mw ? Number(x.queue_mw) : null,
    sourceUrls: (x.source_urls ?? r.source_url ?? "").split(";").filter(Boolean),
    siting: sitingOf(x.state ?? "", x.county ?? "", r.capacity_mw === null ? null : Number(r.capacity_mw)),
  };
}
/** Session 719: the facility's row on the All grids tab of /cost-of-power, by its county, else its state; none where
 *  neither places it in one grid. The tracker names no node, so an ERCOT facility is never placed at a node. */
function sitingOf(state: string, county: string, mw: number | null): Facility["siting"] {
  const s = facilitySite(FACILITY_GRID, SITING_FILES.index, state, county);
  return s ? { ...s, href: facilityHref(s, mw) } : null;
}

/** Session 166: the rows the totals and bars count: in a named US state, and not cancelled. */
export const counted = (rows: Facility[]): Facility[] => rows.filter((f) => f.country === "US" && !cancelled(f.status));

const DAY = 86_400_000;
const STATUS_WORDS = (s: string) => (s ? s.replace("_", " ") : "status not stated");
const dayWords = (d: string) => new Date(`${d}T00:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });

/** Session 240: the first day of "this week": the seven UTC days that end on `today` (both included). */
export const weekStart = (today: string): string => new Date(Date.parse(`${today}T00:00:00Z`) - 6 * DAY).toISOString().slice(0, 10);
/** The facilities whose first story is dated in the week, newest first. The only date the table holds a facility by. */
export const firstReportedSince = (rows: Facility[], start: string): Facility[] =>
  rows.filter((f) => f.firstStory && f.firstStory.slice(0, 10) >= start).sort((a, b) => b.firstStory.localeCompare(a.firstStory) || a.operator.localeCompare(b.operator) || a.site.localeCompare(b.site));

export function Body({ rows, today, children }: { rows: Facility[]; today: string; children?: ReactNode }) {
  const inTotals = counted(rows);
  const noCountry = rows.filter((f) => f.country !== "US").length;
  const dropped = rows.filter((f) => f.country === "US" && cancelled(f.status)).length;
  const withMw = inTotals.filter((f) => f.mw !== null);
  const totalMw = withMw.reduce((a, f) => a + (f.mw ?? 0), 0);
  // session 2301 (chain 087): each sum keeps the facilities it counts, for the bar's hover card and the table under the bars
  const sumBy = (key: (f: Facility) => string, blank = false) => {
    const m = new Map<string, number>(), c = new Map<string, number>();
    for (const f of withMw) {
      const k = key(f);
      if (k || blank) { m.set(k, (m.get(k) ?? 0) + (f.mw ?? 0)); c.set(k, (c.get(k) ?? 0) + 1); }
    }
    return Array.from(m.entries()).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([k, v]) => [k, v, c.get(k) ?? 0] as [string, number, number]);
  };
  const byState = sumBy((f) => f.state);
  const byOperator = sumBy((f) => f.operator).slice(0, 5);
  const byStatus = sumBy((f) => f.status, true);            // the megawatts by status, as the table has them (a blank status is "status not stated")
  const noMw = inTotals.length - withMw.length;
  const start = weekStart(today);
  const fresh = firstReportedSince(rows, start);
  const dated = rows.filter((f) => f.firstStory).length;
  // session 2301: a bar's hover card (docs/brand.md, section 6: fog with a rule-colored edge, the name in sans, the figure in
  // mono, the source line), shown when the figure is pointed at or focused (the figure is a button, so a keyboard reaches
  // it; app/tokens.css, "tip"); the same figures stand in the fold under the bars as a table
  const barWords = (key: string, k: string, v: number, c: number) =>
    `${key === "state" ? "State" : "Operator"} ${k}: ${count(v)} MW stated by ${count(c)} ${c === 1 ? "facility" : "facilities"} in a named US state and not cancelled, whose story or operator page states MW. Read from datacenter_facilities, the live set, summed on the page; the check key datacenters|${key}_mw|${k}.`;
  const bars = (list: [string, number, number][], key: string, max: number) =>
    list.length === 0 ? (
      <div className="text-sm text-muted">no data: no facility with a stated {key === "state" ? "state" : "operator"} states its MW</div>
    ) : (
      <ul className="space-y-1" data-bars-list={key}>
        {list.map(([k, v, c]) => (
          <li key={k} className="grid grid-cols-[7rem_1fr_auto] items-center gap-2 text-sm">
            <span className="truncate">{k}</span>
            <span aria-hidden className="h-2 bg-muted" style={{ width: `${Math.max(2, (100 * v) / max)}%` }} />
            <span className="tip relative inline-block font-mono tabular-nums" data-bar-tip={`${key}|${k}`}>
              <button type="button" data-tip-trigger="1" className="cursor-help border-b border-dotted border-muted" style={{ font: "inherit", verticalAlign: "baseline" }} aria-describedby={`bar-${key}-${k.replace(/[^A-Za-z0-9]+/g, "-")}`}>
                <Num check={`datacenters|${key}_mw|${k}`} raw={v}>{count(v)}</Num> MW
              </button>
              <span role="tooltip" id={`bar-${key}-${k.replace(/[^A-Za-z0-9]+/g, "-")}`} className="absolute right-0 top-5 z-10 hidden w-72 max-w-[80vw] border border-rule bg-paper px-2 py-1.5 text-left font-sans text-xs font-normal leading-snug text-ink">
                <span className="block">{key === "state" ? "State" : "Operator"} {k}</span>
                <span className="block font-mono">{count(v)} MW, {count(c)} {c === 1 ? "facility" : "facilities"}</span>
                <span className="block text-muted">{barWords(key, k, v, c).split(". ").slice(1).join(". ")}</span>
              </span>
            </span>
          </li>
        ))}
      </ul>
    );
  const barsTable = (list: [string, number, number][], key: string) => (
    <ToolTable caption={key === "state" ? "Stated MW by state, the bars' figures" : "Top operators by MW, the bars' figures"} minWidth={360}
      head={[key === "state" ? "State" : "Operator", "Facilities counted", "MW stated"]}
      rows={list.map(([k, v, c]) => ({ key: k, cells: [k, count(c), <span key="mw" data-bar-row={`${key}|${k}`}>{count(v)}</span>] }))} />
  );
  const maxMw = Math.max(1, ...byState.map((x) => x[1]), ...byOperator.map((x) => x[1]));
  return (
    <>
      <section aria-label="Summary" data-top-block="1">
        <HeadlineRow>
          <HeadlineNumber
            label="Facilities held"
            value={<Num check="datacenters|count" raw={rows.length}>{count(rows.length)}</Num>}
            note={<span data-counted="1">
              <Num check="datacenters|counted" raw={inTotals.length}>{count(inTotals.length)}</Num> in a named US state and not cancelled. Left out of the sums:{" "}
              <span title="No source the ERW reads states a country. A row with no US state stated may be outside the US (Firmus's Tasmanian rows are among these) or a US site whose story or operator page names no state. Such rows stay in the table and read &quot;country not stated&quot;.">
                <Num check="datacenters|no_us_state" raw={noCountry}>{count(noCountry)}</Num> with no US state stated
              </span>
              , <Num check="datacenters|cancelled" raw={dropped}>{count(dropped)}</Num> cancelled
            </span>}
          />
          <HeadlineNumber
            label="Megawatts stated"
            value={<Num check="datacenters|mw_total" raw={totalMw}>{count(totalMw)}</Num>}
            unit="MW"
            note={<span data-mw-by-status="1">
              Stated by <Num check="datacenters|n_with_mw" raw={withMw.length}>{count(withMw.length)}</Num> of the facilities counted; {noMw} state no MW. By status, as the table has it:{" "}
              {byStatus.map(([k, v], i) => (
                <span key={k || "blank"}>{i ? ", " : ""}{STATUS_WORDS(k)} <Num check={`datacenters|status_mw|${k}`} raw={v}>{count(v)}</Num> MW</span>
              ))}
            </span>}
          />
          <HeadlineNumber
            label="First reported this week"
            value={<Num check={`datacenters|first_week|${start}`} raw={fresh.length}>{count(fresh.length)}</Num>}
            note={<span data-week={start}>
              Facilities whose first story is dated {dayWords(start)} to {dayWords(today)}. A change of status or of megawatts: not held
            </span>}
          />
        </HeadlineRow>
        <ToolSection
          title="What changed this week"
          note={<span data-not-held="1">
            Not held: a facility whose status or megawatts changed this week. The table is rebuilt whole each day and keeps one row a facility as it stands
            now: no earlier value, and no date of a change (its status date is empty on every row). The one date a facility carries is its first story&apos;s,
            which <Num check="datacenters|n_first_story" raw={dated}>{count(dated)}</Num> of the {count(rows.length)} facilities have (those found in the news); a facility from an operator&apos;s list or a queue
            carries no date, so one added there this week cannot be told from one held for months.
          </span>}
        >
          {fresh.length === 0 ? (
            <p className="text-sm text-muted">No facility&apos;s first story is dated {dayWords(start)} to {dayWords(today)}.</p>
          ) : (
            <ToolTable
              words
              caption="Facilities first reported this week"
              head={["First reported", "Operator, site", "Place", "MW stated", "Status"]}
              rows={fresh.map((f) => ({
                key: f.id,
                cells: [
                  f.firstStory.slice(0, 10),
                  [f.operator || "operator not stated", f.site].filter(Boolean).join(", "),
                  [f.city, f.county, f.state].filter(Boolean).join(", ") || "not stated",
                  f.mw === null ? "not stated" : f.mw.toLocaleString("en-US"),
                  f.status ? STATUS_WORDS(f.status) : "not stated",
                ],
              }))}
            />
          )}
        </ToolSection>
        <div className="mb-3 grid gap-6 md:grid-cols-2" data-bars="1">
          <div>
            <div className="mb-1 text-xs text-muted">Stated MW by state (MW a story or the operator states; US rows not cancelled)
              <Tip id="bars-state" label="the bars by state">Each bar is the MW stated for the facilities counted in that state, read from datacenter_facilities (the live set) and summed on the page; hover or focus a figure for the facilities behind it. The same figures are in the fold under the bars, as a table.</Tip></div>
            {bars(byState, "state", maxMw)}
          </div>
          <div>
            <div className="mb-1 text-xs text-muted">Top operators by MW (US rows not cancelled)
              <Tip id="bars-operator" label="the bars by operator">The five operators with the most MW stated for their facilities counted, read from datacenter_facilities (the live set) and summed on the page; hover or focus a figure for the facilities behind it. The same figures are in the fold under the bars.</Tip></div>
            {bars(byOperator, "operator", maxMw)}
          </div>
        </div>
        {byState.length || byOperator.length ? (
          <Fold title="The bars' figures">
            <div className="grid gap-6 md:grid-cols-2" data-bars-table="1">
              {byState.length ? barsTable(byState, "state") : null}
              {byOperator.length ? barsTable(byOperator, "operator") : null}
            </div>
          </Fold>
        ) : null}
        <p className="mb-8 text-xs text-muted">
          Sums count only facilities in a named US state whose status is not withdrawn (cancelled), and whose story or operator page states MW, and a
          state or operator. A queue position&apos;s MW is the generation or storage it asks to connect, not the datacenter&apos;s load, so it is never summed.
        </p>
      </section>
      {children}
      <DatacentersTable rows={rows} />
      <Cite
        tables={["datacenter_facilities"]}
        note="Built by warehouse/derived/datacenter_facilities.py from datacenter_projects (the news, extracted by warehouse/datacenters/extract.py; the evidence sentences stay in the internal table datacenter_projects_evidence), datacenter_operator_sites (nine operators' public site lists) and the six ISO queues, deduplicated by operator plus location (method: docs/methods/datacenter_facilities.md)"
      />
    </>
  );
}
