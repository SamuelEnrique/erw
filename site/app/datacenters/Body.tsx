// The /datacenters body (session 16; session 22: the combined table): the summary strip, the table and the citation.
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
            <div className="mb-1 text-xs text-muted">Stated MW by state (MW a story or the operator states, any status)</div>
            {bars(byState, "state", maxMw)}
          </div>
          <div className="bg-panel px-3 py-2">
            <div className="mb-1 text-xs text-muted">Top operators by MW</div>
            {bars(byOperator, "operator", maxMw)}
          </div>
        </div>
        <p className="mt-1 text-xs text-muted">
          Sums count only the facilities whose story or operator page states MW, and a state or operator. A queue position&apos;s MW is the generation
          or storage it asks to connect, not the datacenter&apos;s load, so it is never summed.
        </p>
      </section>
      <DatacentersTable rows={rows} />
      <Cite
        tables={["datacenter_facilities"]}
        note="Built by warehouse/derived/datacenter_facilities.py from datacenter_projects (the news, extracted by warehouse/datacenters/extract.py; the evidence sentences stay in the internal table datacenter_projects_evidence), datacenter_operator_sites (nine operators' public site lists) and the six ISO queues, deduplicated by operator plus location (method: docs/methods/datacenter_facilities.md)"
      />
    </>
  );
}
