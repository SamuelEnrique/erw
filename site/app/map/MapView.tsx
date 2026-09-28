"use client";

// The project map (session 16; session 22: on ECharts, the site's one chart library). State shapes and
// tens of thousands of points on one canvas, with zoom and pan (drag, wheel, pinch), a hover card on each
// point, a click on a state that filters the page to it, and a legend that toggles kinds. A click on a
// point opens its card, read from Supabase through /api/entity. The filters in the row above stay.
import { useMemo, useState } from "react";
import { baseStyle, token, useEChart } from "@/components/echarts";
import { STATES } from "@/lib/regions";
import { COLOR_LEGEND, KINDS, TECH_GROUPS, type MapData } from "./groups";

type Card = { loading: true; id: string } | { loading: false; id: string; row?: Record<string, unknown>; error?: string };

const fmt = (n: number) => Math.round(n).toLocaleString("en-US");
const NAME_TO_CODE = Object.fromEntries(Object.entries(STATES).map(([code, name]) => [name, code]));

/** Point size in pixels: area grows with MW, clamped for legibility. */
function size(mw: number): number {
  return Math.min(18, Math.max(3, 2 + Math.sqrt(Math.max(mw, 0)) * 0.2));
}

export function MapView({ data, colors }: { data: MapData; colors: Record<string, string> }) {
  const n = data.x.length;
  const presentKinds = KINDS.map((k, i) => ({ ...k, i })).filter((k) => data.kind.includes(k.i));
  const presentTech = TECH_GROUPS.map((g, i) => ({ ...g, i })).filter((g) => data.tech.includes(g.i));
  const [kinds, setKinds] = useState<Set<number>>(() => new Set(presentKinds.map((k) => k.i)));
  const [tech, setTech] = useState<number>(-1);
  const [state, setState] = useState<number>(-1);
  const [status, setStatus] = useState<number>(-1);
  const [mwMin, setMwMin] = useState<string>("");
  const [mwMax, setMwMax] = useState<string>("");
  const [card, setCard] = useState<Card | null>(null);

  // everything but the kind filter: the legend toggles kinds inside the chart
  const matched = useMemo(() => {
    const lo = mwMin === "" ? -Infinity : Number(mwMin);
    const hi = mwMax === "" ? Infinity : Number(mwMax);
    const out: number[] = [];
    for (let i = 0; i < n; i++) {
      if (tech >= 0 && data.tech[i] !== tech) continue;
      if (state >= 0 && data.state[i] !== state) continue;
      if (status >= 0 && data.status[i] !== status) continue;
      if (data.mw[i] < lo || data.mw[i] > hi) continue;
      out.push(i);
    }
    return out;
  }, [n, data, tech, state, status, mwMin, mwMax]);
  const visible = useMemo(() => matched.filter((i) => kinds.has(data.kind[i])), [matched, kinds, data.kind]);
  const visibleMw = useMemo(() => visible.reduce((a, i) => a + data.mw[i], 0), [visible, data.mw]);

  async function open(i: number) {
    const id = data.id[i];
    const table = data.table[i] === 1 ? "datacenter_projects" : "energy_projects";
    setCard({ loading: true, id });
    try {
      const res = await fetch(`/api/entity?table=${table}&id=${encodeURIComponent(id)}`);
      const body = await res.json();
      setCard(res.ok ? { loading: false, id, row: body } : { loading: false, id, error: body.error ?? `HTTP ${res.status}` });
    } catch (e) {
      setCard({ loading: false, id, error: (e as Error).message });
    }
  }

  const box = useEChart(
    (chart, lib) => {
      lib.registerMap("erw-us", data.statesGeo as unknown);
      const st = baseStyle();
      const palette = TECH_GROUPS.map((g) => token(`var(${colors[g.color]})`));
      const panel = token("panel"), ink = token("ink"), paper = token("paper"), rule = token("rule"), accent = token("accent");
      const selName = state >= 0 ? STATES[data.stateCodes[state]] : null;
      const series = presentKinds.map((k) => ({
        name: k.label.replace(/ \(.*\)$/, ""),
        type: "scatter",
        coordinateSystem: "geo",
        progressive: 4000,
        // the legend icon: the kind's shape in a neutral color (a point's own color is its technology)
        symbol: k.i === 3 ? "diamond" : k.i === 2 ? "emptyCircle" : "circle",
        itemStyle: { color: k.i === 1 ? token("muted") : ink },
        emphasis: { scale: 1.6 },
        data: matched.filter((i) => data.kind[i] === k.i).map((i) => {
          const dc = data.kind[i] === 3, ring = !dc && data.county[i] === 1;
          return {
            value: [data.x[i], data.y[i], i],
            symbol: dc ? "diamond" : ring ? "emptyCircle" : "circle",
            symbolSize: dc ? 9 : size(data.mw[i]),
            itemStyle: dc
              ? { color: panel, borderColor: ink, borderWidth: 1.2, opacity: 0.95 }
              : ring
                ? { color: palette[data.tech[i]], borderColor: palette[data.tech[i]], borderWidth: 1, opacity: 0.85 }
                : { color: palette[data.tech[i]], borderColor: panel, borderWidth: 0.4, opacity: 0.78 },
          };
        }),
      }));
      chart.setOption(
        {
          animation: false,
          textStyle: st.textStyle,
          toolbox: { ...st.toolbox("erw-project-map"), feature: { restore: { title: "Reset zoom" }, saveAsImage: st.toolbox("erw-project-map").feature.saveAsImage } },
          legend: {
            top: 0,
            left: 0,
            right: 70,
            type: "scroll",
            textStyle: { color: ink, fontSize: 11 },
            selected: Object.fromEntries(presentKinds.map((k) => [k.label.replace(/ \(.*\)$/, ""), kinds.has(k.i)])),
          },
          tooltip: {
            ...st.tooltip,
            trigger: "item",
            formatter: (p: { componentType: string; name?: string; value?: number[] }) => {
              if (p.componentType === "geo") return `${p.name}: click to show this state only`;
              const i = (p.value as number[])[2];
              const dc = data.kind[i] === 3;
              return `<div style="max-width:16rem;white-space:normal"><div style="font-family:monospace">${data.id[i]}</div>`
                + `${dc ? "Datacenter" : TECH_GROUPS[data.tech[i]].label}, ${dc && !data.mw[i] ? "MW not stated" : `${fmt(data.mw[i])} MW`}<br/>`
                + `<span style="color:${token("muted")}">${KINDS[data.kind[i]].label.replace(/ \(.*\)$/, "")}, ${data.statuses[data.status[i]] || "status not stated"}`
                + `${data.county[i] ? (dc ? ", at a county or city point" : ", at a county point") : ""}. Click for details.</span></div>`;
            },
          },
          geo: {
            map: "erw-us",
            roam: true,
            scaleLimit: { min: 1, max: 20 },
            projection: { project: (p: number[]) => p, unproject: (p: number[]) => p },
            top: 36,
            bottom: 4,
            itemStyle: { areaColor: paper, borderColor: rule, borderWidth: 0.7 },
            emphasis: { itemStyle: { areaColor: panel }, label: { show: false } },
            select: { disabled: true },
            tooltip: { show: true },
            regions: selName ? [{ name: selName, itemStyle: { areaColor: panel, borderColor: accent, borderWidth: 1.5 } }] : [],
          },
          series,
        },
        true,
      );
      chart.off("click");
      chart.on("click", (p) => {
        if (p.componentType === "series") open((p.value as number[])[2]);
        else if (p.componentType === "geo") {
          const code = NAME_TO_CODE[p.name as string];
          const idx = code ? data.stateCodes.indexOf(code) : -1;
          setState((cur) => (idx < 0 || cur === idx ? -1 : idx));
        }
      });
      chart.off("legendselectchanged");
      chart.on("legendselectchanged", (p) => {
        const sel = p.selected as Record<string, boolean>;
        setKinds(new Set(presentKinds.filter((k) => sel[k.label.replace(/ \(.*\)$/, "")]).map((k) => k.i)));
      });
    },
    [matched, kinds, state, colors],
  );

  const toggleKind = (i: number) =>
    setKinds((s) => {
      const t = new Set(s);
      if (t.has(i)) t.delete(i);
      else t.add(i);
      return t;
    });
  const reset = () => {
    setKinds(new Set(presentKinds.map((k) => k.i)));
    setTech(-1);
    setState(-1);
    setStatus(-1);
    setMwMin("");
    setMwMax("");
  };

  const sel = "border border-rule bg-panel px-2 py-1 text-sm";
  return (
    <section aria-label="Map">
      <div className="mb-2 flex flex-wrap items-end gap-x-4 gap-y-2 text-sm">
        <fieldset className="flex flex-wrap gap-x-3">
          <legend className="text-xs text-muted">Kind</legend>
          {presentKinds.map((k) => (
            <label key={k.id} className="whitespace-nowrap">
              <input type="checkbox" className="mr-1" checked={kinds.has(k.i)} onChange={() => toggleKind(k.i)} />
              {k.label.replace(/ \(.*\)$/, "")}
            </label>
          ))}
        </fieldset>
        <label className="flex flex-col">
          <span className="text-xs text-muted">Technology</span>
          <select className={sel} value={tech} onChange={(e) => setTech(Number(e.target.value))}>
            <option value={-1}>All</option>
            {presentTech.map((g) => (
              <option key={g.id} value={g.i}>
                {g.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col">
          <span className="text-xs text-muted">State (or click one on the map)</span>
          <select className={sel} value={state} onChange={(e) => setState(Number(e.target.value))}>
            <option value={-1}>All</option>
            {data.stateCodes.map((s, i) => (
              <option key={s} value={i}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col">
          <span className="text-xs text-muted">Status</span>
          <select className={sel} value={status} onChange={(e) => setStatus(Number(e.target.value))}>
            <option value={-1}>All</option>
            {data.statuses.map((s, i) => (
              <option key={s || "none"} value={i}>
                {s ? s.replace("_", " ") : "not stated"}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col">
          <span className="text-xs text-muted">MW from</span>
          <input className={`${sel} w-24`} inputMode="decimal" value={mwMin} onChange={(e) => setMwMin(e.target.value.replace(/[^0-9.]/g, ""))} placeholder="0" />
        </label>
        <label className="flex flex-col">
          <span className="text-xs text-muted">MW to</span>
          <input className={`${sel} w-24`} inputMode="decimal" value={mwMax} onChange={(e) => setMwMax(e.target.value.replace(/[^0-9.]/g, ""))} placeholder="any" />
        </label>
        <button type="button" onClick={reset} className="border border-rule px-2 py-1 text-sm hover:text-accent">
          Reset
        </button>
      </div>
      <p className="mb-2 text-sm tabular-nums" aria-live="polite">
        Showing {fmt(visible.length)} of {fmt(n)} placed points, {fmt(visibleMw)} MW{state >= 0 ? ` in ${data.stateCodes[state]}` : ""}.{" "}
        <span className="text-muted">
          Not drawn: {fmt(data.unplaced)} without a location, {fmt(data.offMap)} outside the map&apos;s area (for example Puerto Rico). Drag to pan,
          scroll or pinch to zoom.
        </span>
      </p>

      <div className="grid gap-4 lg:grid-cols-[1fr_18rem]">
        <div>
          <div
            ref={box}
            className="w-full border border-rule bg-panel"
            style={{ aspectRatio: `${data.width} / ${data.height + 50}` }}
            role="img"
            aria-label={`Map of ${visible.length} energy projects in the United States; the table below lists them by technology`}
          />
          <Legend colors={colors} hasDatacenters={data.kind.includes(3)} />
        </div>
        <ProjectCard card={card} onClose={() => setCard(null)} />
      </div>
    </section>
  );
}

function Legend({ colors, hasDatacenters }: { colors: Record<string, string>; hasDatacenters: boolean }) {
  return (
    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs" aria-label="Colors">
      {COLOR_LEGEND.map((l) => (
        <span key={l.color} className="whitespace-nowrap">
          <span aria-hidden className="mr-1 inline-block h-2.5 w-2.5 rounded-full align-middle" style={{ background: `var(${colors[l.color]})` }} />
          {l.label}
        </span>
      ))}
      <span className="whitespace-nowrap text-muted">dot: exact coordinates (EIA); ring: county point (queue positions)</span>
      {hasDatacenters ? <span className="whitespace-nowrap text-muted">diamond: datacenter</span> : null}
      <span className="whitespace-nowrap text-muted">size: MW</span>
    </div>
  );
}

const LABELS: [string, string][] = [
  ["kind", "Kind"],
  ["technology_group", "Technology group"],
  ["mw", "MW"],
  ["status", "Status"],
  ["state", "State"],
  ["county", "County"],
  ["city", "City"],
  ["operator", "Operator or developer"],
  ["developer", "Developer"],
  ["date", "Date"],
  ["power", "Power"],
  ["geo_precision", "Location"],
  ["source_table", "Source table"],
];

function ProjectCard({ card, onClose }: { card: Card | null; onClose: () => void }) {
  if (!card) {
    return (
      <aside className="border border-dashed border-rule bg-panel p-3 text-sm text-muted">
        Click a point for its details: name, capacity, status, operator or developer, date and the table it comes from.
      </aside>
    );
  }
  if (card.loading) {
    return <aside className="border border-rule bg-panel p-3 text-sm text-muted">Reading {card.id} from Supabase...</aside>;
  }
  if (card.error || !card.row) {
    return (
      <aside className="border border-rule bg-panel p-3 text-sm" role="status">
        <span className="font-semibold">no data</span> for {card.id}: {card.error}
      </aside>
    );
  }
  const r = card.row as Record<string, unknown> & { extra?: Record<string, string> };
  const x = r.extra ?? {};
  const role = x.operator_role === "developer" ? "developer" : "operator";
  const dateKind: Record<string, string> = {
    operating_year: "operating year",
    planned_operation_date: "planned operation date",
    queue_date: "queue date",
  };
  const vals: Record<string, string> = {
    kind: x.kind ?? "",
    technology_group: (TECH_GROUPS.find((g) => g.id === x.technology_group)?.label ?? x.technology_group ?? "") + (x.technology ? ` (${x.technology})` : ""),
    mw: r.capacity_mw === null || r.capacity_mw === undefined ? "not stated" : `${Number(r.capacity_mw).toLocaleString("en-US")} MW`,
    status: x.project_status
      ? `${x.project_status.replace("_", " ")} (as stated)`
      : `${String(r.status ?? "not stated").replace("_", " ")}${r.status_date ? ` since ${r.status_date}` : ""}`,
    state: x.state ?? "",
    county: x.county ?? "",
    city: x.city ?? "",
    developer: x.developer && x.developer !== r.operator ? x.developer : "",
    power: [x.power_source, x.utility ? `utility ${x.utility}` : ""].filter(Boolean).join("; "),
    operator: r.operator ? `${r.operator} (${x.kind === "datacenter" ? "operator" : role})` : "not stated",
    date: x.date
      ? `${x.date} (${dateKind[x.date_kind] ?? x.date_kind ?? ""})`
      : x.planned_year
        ? `${x.planned_year} (planned year, as stated)`
        : "not stated",
    geo_precision:
      x.geo_precision === "point"
        ? `exact coordinates, ${r.lat}, ${r.lon}`
        : x.geo_precision === "county"
          ? `county point (Census gazetteer), ${r.lat}, ${r.lon}; not the site itself`
          : x.geo_precision === "place"
            ? `city point (Census gazetteer), ${r.lat}, ${r.lon}; not the site itself`
            : "not placed",
    source_table: x.source_table ?? String(r.table_name ?? ""),
  };
  return (
    <aside className="border border-rule bg-panel p-3 text-sm" aria-live="polite">
      <div className="mb-1 flex items-start justify-between gap-2">
        <h2 className="font-serif text-lg leading-tight">{String(r.name || "No name in the source")}</h2>
        <button type="button" onClick={onClose} className="text-muted hover:text-accent" aria-label="Close">
          x
        </button>
      </div>
      <div className="mb-2 font-mono text-xs text-muted">{String(r.entity_id)}</div>
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
        {LABELS.map(([k, label]) =>
          vals[k] ? (
            <div key={k} className="contents">
              <dt className="text-xs text-muted">{label}</dt>
              <dd>
                {k === "source_table" ? (
                  <a href={`/data#${vals[k]}`} className="font-mono">
                    {vals[k]}
                  </a>
                ) : (
                  vals[k]
                )}
              </dd>
            </div>
          ) : null,
        )}
      </dl>
      {typeof x.story_urls === "string" && x.story_urls ? (
        <div className="mt-2 text-xs">
          Stories:{" "}
          {x.story_urls
            .split(";")
            .filter(Boolean)
            .map((u, i) => (
              <a key={u} href={u} className="mr-2" rel="noreferrer" target="_blank">
                {i + 1}
              </a>
            ))}
        </div>
      ) : null}
      <p className="mt-2 text-xs text-muted">
        Read from the ERW table <code className="font-mono">{String(r.table_name)}</code> in Supabase{r.vintage ? `, vintage ${r.vintage}` : ""}.
      </p>
    </aside>
  );
}
