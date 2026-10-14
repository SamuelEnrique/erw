// The /datacenters body (session 16; session 22: the combined table): the summary strip, the table and the citation.
// Session 166 (accuracy): the Status column and filter show the cleaned status (the entities vocabulary: planned,
// under_construction, operating, withdrawn), never a source's raw field; the totals and the two bars count only rows
// in a named US state whose status is not withdrawn (cancelled); a row without a US state stays in the table and
// reads "country not stated" (no source records a country).
// Session 240: on the brand. The strip is a top block of three numbers (the facilities held, the megawatts stated with
// what the sum counts by status, and the facilities first reported this week), then what changed this week with what
// the table does not hold said in words, the two bars, and the list grouped by operator (DatacentersTable).
import Link from "next/link";
import type { ReactNode } from "react";
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import type { EntityRow } from "@/lib/data";
import { count } from "@/lib/format";
import { cancelled, countryOf } from "@/lib/largeload";
import { HeadlineNumber, HeadlineRow, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { DatacentersTable, type Facility } from "./DatacentersTable";

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
  };
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
  const sumBy = (key: (f: Facility) => string, blank = false) => {
    const m = new Map<string, number>();
    for (const f of withMw) {
      const k = key(f);
      if (k || blank) m.set(k, (m.get(k) ?? 0) + (f.mw ?? 0));
    }
    return Array.from(m.entries()).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  };
  const byState = sumBy((f) => f.state);
  const byOperator = sumBy((f) => f.operator).slice(0, 5);
  const byStatus = sumBy((f) => f.status, true);            // the megawatts by status, as the table has them (a blank status is "status not stated")
  const noMw = inTotals.length - withMw.length;
  const start = weekStart(today);
  const fresh = firstReportedSince(rows, start);
  const dated = rows.filter((f) => f.firstStory).length;
  const bars = (list: [string, number][], key: string, max: number) =>
    list.length === 0 ? (
      <div className="text-sm text-muted">no data: no facility with a stated {key === "state" ? "state" : "operator"} states its MW</div>
    ) : (
      <ul className="space-y-1">
        {list.map(([k, v]) => (
          <li key={k} className="grid grid-cols-[7rem_1fr_auto] items-center gap-2 text-sm">
            <span className="truncate">{k}</span>
            <span aria-hidden className="h-2 bg-muted" style={{ width: `${Math.max(2, (100 * v) / max)}%` }} />
            <span className="font-mono tabular-nums">
              <Num check={`datacenters|${key}_mw|${k}`} raw={v}>{count(v)}</Num> MW
            </span>
          </li>
        ))}
      </ul>
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
        <div className="mb-3 grid gap-6 md:grid-cols-2">
          <div>
            <div className="mb-1 text-xs text-muted">Stated MW by state (MW a story or the operator states; US rows not cancelled)</div>
            {bars(byState, "state", maxMw)}
          </div>
          <div>
            <div className="mb-1 text-xs text-muted">Top operators by MW (US rows not cancelled)</div>
            {bars(byOperator, "operator", maxMw)}
          </div>
        </div>
        <p className="mb-8 text-xs text-muted">
          Sums count only facilities in a named US state whose status is not withdrawn (cancelled), and whose story or operator page states MW, and a
          state or operator. A queue position&apos;s MW is the generation or storage it asks to connect, not the datacenter&apos;s load, so it is never summed.
        </p>
      </section>
      {children}
      <DatacentersTable rows={rows} />
      <Cite
        tables={["datacenter_facilities"]}
        note={<>Built by warehouse/derived/datacenter_facilities.py from datacenter_projects (the news, extracted by warehouse/datacenters/extract.py; the evidence sentences stay in the internal table datacenter_projects_evidence), datacenter_operator_sites (nine operators&apos; public site lists) and the six ISO queues, deduplicated by operator plus location (method: <Link href="/data/methods/datacenter_facilities">datacenter_facilities</Link>)</>}
      />
    </>
  );
}
