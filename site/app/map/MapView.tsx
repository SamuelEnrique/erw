"use client";

// The project map (session 16): state outlines in SVG, projects on a canvas (tens of thousands of
// points), filters in one row above, a tooltip on hover and a card on click. The card's fields are
// read from Supabase through /api/entity when a point is clicked.
import { useEffect, useMemo, useRef, useState } from "react";
import { COLOR_LEGEND, KINDS, TECH_GROUPS, type MapData } from "./groups";

type Card = { loading: true; id: string } | { loading: false; id: string; row?: Record<string, unknown>; error?: string };

const fmt = (n: number) => Math.round(n).toLocaleString("en-US");

/** Point radius in map units (the map is 975 wide): area grows with MW, clamped for legibility. */
function radius(mw: number): number {
  return Math.min(9, Math.max(1.1, 0.9 + Math.sqrt(Math.max(mw, 0)) * 0.11));
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
  const [hover, setHover] = useState<{ i: number; left: number; top: number } | null>(null);
  const [card, setCard] = useState<Card | null>(null);
  const wrap = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [width, setWidth] = useState(0);

  const visible = useMemo(() => {
    const lo = mwMin === "" ? -Infinity : Number(mwMin);
    const hi = mwMax === "" ? Infinity : Number(mwMax);
    const out: number[] = [];
    for (let i = 0; i < n; i++) {
      if (!kinds.has(data.kind[i])) continue;
      if (tech >= 0 && data.tech[i] !== tech) continue;
      if (state >= 0 && data.state[i] !== state) continue;
      if (status >= 0 && data.status[i] !== status) continue;
      if (data.mw[i] < lo || data.mw[i] > hi) continue;
      out.push(i);
    }
    return out;
  }, [n, data, kinds, tech, state, status, mwMin, mwMax]);
  const visibleMw = useMemo(() => visible.reduce((a, i) => a + data.mw[i], 0), [visible, data.mw]);

  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setWidth(el.clientWidth));
    ro.observe(el);
    setWidth(el.clientWidth);
    return () => ro.disconnect();
  }, []);

  // draw
  useEffect(() => {
    const c = canvas.current;
    if (!c || !width) return;
    const dpr = window.devicePixelRatio || 1;
    const k = width / data.width;
    const h = data.height * k;
    c.width = Math.round(width * dpr);
    c.height = Math.round(h * dpr);
    c.style.height = `${h}px`;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    const css = getComputedStyle(document.documentElement);
    const col = (name: string) => css.getPropertyValue(colors[name]).trim() || "#888";
    const palette = TECH_GROUPS.map((g) => col(g.color));
    const surface = css.getPropertyValue("--color-panel").trim() || "#fff";
    const ink = css.getPropertyValue("--color-ink").trim() || "#000";
    ctx.setTransform(dpr * k, 0, 0, dpr * k, 0, 0);
    ctx.clearRect(0, 0, data.width, data.height);
    for (const i of visible) {
      const r = radius(data.mw[i]);
      const x = data.x[i];
      const y = data.y[i];
      if (data.kind[i] === 3) {
        // a datacenter: an ink diamond (a load, not a technology)
        ctx.beginPath();
        ctx.moveTo(x, y - r - 1);
        ctx.lineTo(x + r + 1, y);
        ctx.lineTo(x, y + r + 1);
        ctx.lineTo(x - r - 1, y);
        ctx.closePath();
        ctx.globalAlpha = 0.9;
        ctx.fillStyle = surface;
        ctx.fill();
        ctx.lineWidth = 1.2;
        ctx.strokeStyle = ink;
        ctx.stroke();
        continue;
      }
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      if (data.county[i]) {
        // a county point: a ring, so an approximate place never reads as an exact one
        ctx.globalAlpha = 0.85;
        ctx.lineWidth = 0.9;
        ctx.strokeStyle = palette[data.tech[i]];
        ctx.stroke();
      } else {
        ctx.globalAlpha = 0.75;
        ctx.fillStyle = palette[data.tech[i]];
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.lineWidth = 0.35;
        ctx.strokeStyle = surface;
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;
  }, [visible, width, data, colors]);

  function pick(ev: React.MouseEvent): number | null {
    const c = canvas.current;
    if (!c || !width) return null;
    const rect = c.getBoundingClientRect();
    const k = width / data.width;
    const mx = (ev.clientX - rect.left) / k;
    const my = (ev.clientY - rect.top) / k;
    let best: number | null = null;
    let bestD = Infinity;
    for (let j = visible.length - 1; j >= 0; j--) {
      const i = visible[j];
      const d = Math.hypot(data.x[i] - mx, data.y[i] - my);
      const reach = radius(data.mw[i]) + 4 / k; // a hit target larger than the mark
      if (d <= reach && d < bestD) {
        best = i;
        bestD = d;
      }
    }
    return best;
  }

  function onMove(ev: React.MouseEvent) {
    const i = pick(ev);
    if (i === null) return setHover(null);
    const rect = wrap.current!.getBoundingClientRect();
    setHover({ i, left: ev.clientX - rect.left, top: ev.clientY - rect.top });
  }

  async function onClick(ev: React.MouseEvent) {
    const i = pick(ev);
    if (i === null) return;
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
          <span className="text-xs text-muted">State</span>
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
        Showing {fmt(visible.length)} of {fmt(n)} placed points, {fmt(visibleMw)} MW.{" "}
        <span className="text-muted">
          Not drawn: {fmt(data.unplaced)} without a location, {fmt(data.offMap)} outside the map&apos;s area (for example Puerto Rico).
        </span>
      </p>

      <div className="grid gap-4 lg:grid-cols-[1fr_18rem]">
        <div>
          <div ref={wrap} className="relative w-full border border-rule bg-panel">
            <svg viewBox={`0 0 ${data.width} ${data.height}`} className="block w-full" aria-hidden>
              <path d={data.nation} fill="var(--color-paper)" stroke="var(--color-muted)" strokeWidth={0.8} />
              <path d={data.statesPath} fill="none" stroke="var(--color-rule)" strokeWidth={0.7} />
            </svg>
            <canvas
              ref={canvas}
              className="absolute left-0 top-0 w-full cursor-pointer"
              role="img"
              aria-label={`Map of ${visible.length} energy projects in the United States; the table below lists them by technology`}
              onMouseMove={onMove}
              onMouseLeave={() => setHover(null)}
              onClick={onClick}
            />
            {hover ? (
              <div
                className="pointer-events-none absolute z-10 max-w-64 border border-rule bg-panel px-2 py-1 text-xs shadow-sm"
                style={{ left: Math.min(hover.left + 12, width - 200), top: hover.top + 12 }}
              >
                <div className="font-mono">{data.id[hover.i]}</div>
                <div>
                  {data.kind[hover.i] === 3 ? "Datacenter" : TECH_GROUPS[data.tech[hover.i]].label},{" "}
                  {data.kind[hover.i] === 3 && !data.mw[hover.i] ? "MW not stated" : `${fmt(data.mw[hover.i])} MW`}
                </div>
                <div className="text-muted">
                  {KINDS[data.kind[hover.i]].label.replace(/ \(.*\)$/, "")}, {data.statuses[data.status[hover.i]] || "status not stated"}
                  {data.county[hover.i] ? (data.kind[hover.i] === 3 ? ", at a county or city point" : ", at a county point") : ""}. Click for details.
                </div>
              </div>
            ) : null}
          </div>
          <Legend colors={colors} hasDatacenters={data.kind.includes(3)} />
        </div>
        <ProjectCard card={card} onClose={() => setCard(null)} />
      </div>
    </section>
  );
}

function Legend({ colors, hasDatacenters }: { colors: Record<string, string>; hasDatacenters: boolean }) {
  return (
    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs" aria-label="Legend">
      {COLOR_LEGEND.map((l) => (
        <span key={l.color} className="whitespace-nowrap">
          <span aria-hidden className="mr-1 inline-block h-2.5 w-2.5 rounded-full align-middle" style={{ background: `var(${colors[l.color]})` }} />
          {l.label}
        </span>
      ))}
      <span className="whitespace-nowrap text-muted">
        <svg width="12" height="12" className="mr-1 inline align-middle" aria-hidden>
          <circle cx="6" cy="6" r="4.5" fill="var(--color-muted)" />
        </svg>
        exact coordinates (EIA)
      </span>
      <span className="whitespace-nowrap text-muted">
        <svg width="12" height="12" className="mr-1 inline align-middle" aria-hidden>
          <circle cx="6" cy="6" r="4.5" fill="none" stroke="var(--color-muted)" strokeWidth="1.3" />
        </svg>
        county point (queue positions)
      </span>
      {hasDatacenters ? (
        <span className="whitespace-nowrap text-muted">
          <svg width="12" height="12" className="mr-1 inline align-middle" aria-hidden>
            <path d="M6 1 L11 6 L6 11 L1 6 Z" fill="var(--color-panel)" stroke="var(--color-ink)" strokeWidth="1.2" />
          </svg>
          datacenter
        </span>
      ) : null}
      <span className="whitespace-nowrap text-muted">
        size: MW (
        {[10, 500, 2000].map((mw, i) => (
          <span key={mw}>
            {i ? ", " : ""}
            <svg width="20" height="20" className="inline align-middle" aria-hidden>
              <circle cx="10" cy="10" r={radius(mw) * 1.1} fill="var(--color-muted)" opacity="0.6" />
            </svg>
            {fmt(mw)}
          </span>
        ))}
        )
      </span>
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
