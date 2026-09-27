// The /datacenters body (session 16): the summary strip, the table and the citation.
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import type { EntityRow } from "@/lib/data";
import { count } from "@/lib/format";
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
    mw: r.capacity_mw === null ? null : Number(r.capacity_mw),
    phase: x.phase ?? "",
    status: x.project_status ?? "",
    plannedYear: x.planned_year ?? "",
    power: x.power_source ?? "",
    utility: x.utility ?? "",
    confidence: x.confidence ? Number(x.confidence) : null,
    placed: x.geo_precision === "county" || x.geo_precision === "place",
    firstStory: x.first_story_at ?? "",
    storyUrls: (x.story_urls ?? r.source_url ?? "").split(";").filter(Boolean),
  };
}

export function Body({ rows }: { rows: Facility[] }) {
  const withMw = rows.filter((f) => f.mw !== null);
  const totalMw = withMw.reduce((a, f) => a + (f.mw ?? 0), 0);
  const sumBy = (key: (f: Facility) => string) => {
    const m = new Map<string, number>();
    for (const f of withMw) {
      const k = key(f);
      if (k) m.set(k, (m.get(k) ?? 0) + (f.mw ?? 0));
    }
    return Array.from(m.entries()).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  };
  const byState = sumBy((f) => f.state);
  const byOperator = sumBy((f) => f.operator).slice(0, 5);
  const noMw = rows.length - withMw.length;
  const bars = (list: [string, number][], key: string, max: number) =>
    list.length === 0 ? (
      <div className="text-sm text-muted">no data: no facility with a stated {key === "state" ? "state" : "operator"} states its MW</div>
    ) : (
      <ul className="space-y-1">
        {list.map(([k, v]) => (
          <li key={k} className="grid grid-cols-[7rem_1fr_auto] items-center gap-2 text-sm">
            <span className="truncate">{k}</span>
            <span aria-hidden className="h-2 rounded-r-sm bg-muted/60" style={{ width: `${Math.max(2, (100 * v) / max)}%` }} />
            <span className="tabular-nums">
              <Num check={`datacenters|${key}_mw|${k}`} raw={v}>{count(v)}</Num> MW
            </span>
          </li>
        ))}
      </ul>
    );
  const maxMw = Math.max(1, ...byState.map((x) => x[1]), ...byOperator.map((x) => x[1]));
  return (
    <>
      <section aria-label="Summary" className="mb-6">
        <div className="grid gap-px border border-rule bg-rule md:grid-cols-3">
          <div className="bg-panel px-3 py-2">
            <div className="text-xs text-muted">Facilities</div>
            <div className="text-lg tabular-nums">
              <Num check="datacenters|count" raw={rows.length}>{count(rows.length)}</Num>
            </div>
            <div className="text-xs text-muted">
              <Num check="datacenters|mw_total" raw={totalMw}>{count(totalMw)}</Num> MW stated, by{" "}
              <Num check="datacenters|n_with_mw" raw={withMw.length}>{count(withMw.length)}</Num> of them; {noMw} state no MW
            </div>
          </div>
          <div className="bg-panel px-3 py-2">
            <div className="mb-1 text-xs text-muted">Announced MW by state (MW the stories state, any status)</div>
            {bars(byState, "state", maxMw)}
          </div>
          <div className="bg-panel px-3 py-2">
            <div className="mb-1 text-xs text-muted">Top operators by MW</div>
            {bars(byOperator, "operator", maxMw)}
          </div>
        </div>
        <p className="mt-1 text-xs text-muted">
          The ERW has scored news since 2026-09-23, so the tracker starts there. Sums count only the facilities whose stories state MW and a state or
          operator.
        </p>
      </section>
      <DatacentersTable rows={rows} />
      <Cite
        tables={["datacenter_projects"]}
        note="Extracted by warehouse/datacenters/extract.py from the scored datacenter_power stories of news_stories; the evidence sentences are outlet text and stay in the internal table datacenter_projects_evidence"
      />
    </>
  );
}
