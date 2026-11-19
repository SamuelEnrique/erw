"use client";
// Session 180: the network as a map. The same grids, the same hour and the same ties as the network beside it
// (Network.tsx owns every one of them: the view, the hour the replay is on, the selection, the colors and the panel);
// this file only draws them on the ground. Each balancing authority is its published boundary
// (public/network/ba_boundaries.json, warehouse/connectors/eia_ba_boundaries.py), filled with the color its sphere
// has; each tie is a line between the two regions, as wide as the network draws it, with a dash that runs from the
// exporter to the importer and an arrowhead at the importer. Hovering a region names it, as hovering a sphere does;
// clicking it opens the same panel.
// Real data only: the file is read when the map is first shown, and when it is not held the frame says so and draws
// nothing. No shape is drawn from anything but the file. A grid of the network with no shape in the file (Canada's and
// Mexico's operators, and any the publisher's file does not name) is not on the map, and the line under it says which.
// Session 193: the file held is a DERIVED one (each county given to one balancing authority from EIA-861; no public
// file of the boundaries was reached in three pulls). A derived file is never drawn without its label: the words stand
// inside the frame, under the map, wherever the regions are.
// Session 8601 (chain 504, 19 November 2026): the map made whole, with nothing it drew taken away.
// - The file: the whole country's boundary file (data/regions/ba_boundaries.json, read through /grid/boundaries) when
//   the server holds it; until then the derived file above, with its label, exactly as before.
// - A grid with no shape in the file is listed by name in the map's frame, right under the map, with the same hover
//   and the same click as a region: it is not dropped.
// - Hovering a region gives its name and its figures for the frame shown; hovering a tie gives both names, the
//   megawatts, the frame and which side reported it.
// - The Batteries switch draws the network's ring on the map, at the point inside each region its ties meet at.
// - The map is moved and zoomed: the wheel, two fingers, a drag once it is zoomed, and three buttons.
// - A tie answers along its own line: the hover takes the nearest line to the pointer (lib/networkMap.ts nearestLine),
//   so a short tie is not hidden under a long one; under a finger, which has no hover, a tap on a tie shows it.
import { geoAlbersUsa } from "d3-geo";
import { useEffect, useMemo, useRef, useState, type MouseEvent as ReactMouseEvent, type PointerEvent as ReactPointerEvent } from "react";
import { MAP_HOME, MAP_ZOOM, arcPath, batteryFill, clampMapView, derivedLabel, flowTip, flowWidth, nearestLine, onTheLine, readBoundaries, readGeoBoundaries, ringPath, whole, zoomMapAt, type Held, type MapView } from "@/lib/networkMap";

export const BOUNDARY_FILE = "/network/ba_boundaries.json";
/** session 8601: the whole country's boundary file, behind the release gate; it answers { held: false } until the server holds the file */
export const PUBLISHED_FILE = "/grid/boundaries";
const W = 975, H = 610;
// the plane of the site's other map (app/map/ProjectMap.tsx): Albers for the lower 48, Alaska and Hawaii inset
const projection = geoAlbersUsa().scale(1300).translate([W / 2, H / 2]);
const project = (p: [number, number]) => projection(p) as [number, number] | null;

export type MapNode = { id: string; name: string };
export type MapFlow = { source: string; target: string; mw: number; a: string; b: string };
/** Session 8601: a grid's figures for the frame shown, from the network's own view (the panel's numbers). */
export type MapFigures = { intensity: number | null; /** the intensity as the panel writes it for this view (two decimals in the live week, whole in a story or a day) */ intensityShown?: string; demand: number | null; /** the sum of its ties, positive when it imports; null when no tie reported */ net: number | null; ties: number };
/** Session 8601: the frame shown, in the words of the slider's own line, and the tables its figures come from. */
export type MapFrame = { when: string; unit: "hour" | "day"; tables: string };

type Hover = { kind: "region" | "listed" | "flow"; id: string; x: number; y: number; right: boolean; low: boolean };

export function NetworkMap({ nodes, flows, maxMw, colorOf, pick, neighbours, onPick, frame, figures, battery, sideOf }: {
  nodes: MapNode[]; flows: MapFlow[]; maxMw: number;
  /** the color the grid's sphere has for the hour shown (Network.tsx colorOf: the same measure, the same scale) */
  colorOf: (id: string) => string;
  pick: string | null;
  /** the selected grid's neighbours, which stay as they are while the rest is dimmed, as in the network */
  neighbours: Set<string>;
  onPick: (id: string) => void;
  /** session 8601: the frame shown; without it a hover names the grid and no more, as before */
  frame?: MapFrame;
  figures?: (id: string) => MapFigures;
  /** session 8601: given while the Batteries switch is on: a grid's batteries in the frame shown and the period's most, or null when none is reported for the period */
  battery?: (id: string) => { mw: number | null; max: number } | null;
  /** session 8601: which side's report a pair's flow is in the frame shown (lib/networkMap.ts reportedBy) */
  sideOf?: (a: string, b: string) => "first" | "second" | null;
}) {
  const [held, setHeld] = useState<Held>({ state: "loading" });
  const [hover, setHover] = useState<Hover | null>(null);
  const [t, setT] = useState<MapView>(MAP_HOME);
  const svg = useRef<SVGSVGElement>(null);
  const ptrs = useRef(new Map<number, { x: number; y: number }>());
  const pinch = useRef<{ d: number; from: MapView; px: number; py: number } | null>(null);
  const dragged = useRef(false);
  const finger = useRef(false);   // the last press was a finger's: a tap on a tie shows the tie
  const [px, setPx] = useState(W / 748);   // the drawing's units to a screen pixel; the frame's own once it is measured
  useEffect(() => {
    const el = svg.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const read = () => { const w = el.getBoundingClientRect().width; if (w > 0) setPx(Math.max(W / w, H / (el.getBoundingClientRect().height || 1))); };
    read();
    const seen = new ResizeObserver(read);
    seen.observe(el);
    return () => seen.disconnect();
  }, [held.state]);
  useEffect(() => {
    let alive = true;
    const derivedFile = () => fetch(BOUNDARY_FILE)
      .then(async (r) => (r.status === 404 ? ({ state: "absent" } as Held) : r.ok ? readBoundaries(await r.json()) : ({ state: "error", why: `HTTP ${r.status}` } as Held)));
    // session 8601: the whole country's file first; an answer that is not that file (not held yet, or the address not reachable) leaves the map on the file it has drawn since session 193
    fetch(PUBLISHED_FILE).then(async (r) => { if (!r.ok) return null; const v = await r.json(); return v && v.type === "FeatureCollection" ? readGeoBoundaries(v) : null; }).catch(() => null)
      .then((published) => published ?? derivedFile())
      .catch((e: Error) => ({ state: "error", why: e.message }) as Held)
      .then((h) => { if (alive) setHeld(h); });
    return () => { alive = false; };
  }, []);

  const names = useMemo(() => new Map(nodes.map((n) => [n.id, n.name])), [nodes]);
  // only the grids the network draws, each once, in the file's order (largest first, so a smaller one is on top)
  const regions = useMemo(() => {
    if (held.state !== "held") return [];
    const seen = new Set<string>();
    return held.file.regions.filter((r) => names.has(r.id) && !seen.has(r.id) && !!seen.add(r.id))
      .map((r) => ({ id: r.id, d: r.rings.map((ring) => ringPath(ring, project)).join(""), at: project(r.point) })).filter((r) => r.d);
  }, [held, names]);
  const at = useMemo(() => new Map(regions.filter((r) => r.at).map((r) => [r.id, r.at as [number, number]])), [regions]);
  const drawnFlows = flows.filter((f) => at.has(f.source) && at.has(f.target));
  const noShape = useMemo(() => nodes.filter((n) => !regions.some((r) => r.id === n.id)).sort((a, b) => a.name.localeCompare(b.name)), [nodes, regions]);

  // session 8601: a point of the screen in the drawing's own units, whatever the frame's size
  const toBox = (cx: number, cy: number): [number, number] => {
    const m = svg.current?.getScreenCTM();
    if (!m) return [0, 0];
    const p = new DOMPoint(cx, cy).matrixTransform(m.inverse());
    return [p.x, p.y];
  };
  // the wheel zooms about the pointer; at rest a wheel that would zoom out scrolls the page, as anywhere else
  useEffect(() => {
    const el = svg.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      const zoomIn = e.deltaY < 0;
      if (!zoomIn && t.k <= MAP_ZOOM[0]) return;
      e.preventDefault();
      const m = el.getScreenCTM();
      if (!m) return;
      const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(m.inverse());
      setT((v) => zoomMapAt(v, zoomIn ? 1.25 : 0.8, p.x, p.y, W, H));
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, [held.state, t.k]);

  const derived = held.state === "held" ? derivedLabel(held.file) : null;
  const frameBox = "w-full min-w-0 overflow-hidden border border-rule";
  // the frame has the map's own proportions, so a phone shows the whole country with no empty band above and below it
  const style = { aspectRatio: `${W} / ${H}`, maxHeight: "min(72vh, 620px)", minHeight: 200 };
  if (held.state !== "held") {
    return (
      <div className={`${frameBox} flex items-center justify-center bg-panel p-6`} style={style} data-map-state={held.state} data-map-regions="0" data-map-matched="0">
        <p className="max-w-md text-sm" role="status">
          {held.state === "loading" ? <>Reading the boundaries.</>
            : held.state === "absent" ? <>The boundary file is not yet held: the warehouse does not yet hold a published file of the balancing authorities&apos; boundaries, so no region is drawn here and none is
              sketched in its place. The Network view shows the same grids, flows and numbers.</>
              : <>The boundary file could not be read ({held.why}), so no region is drawn. The Network view shows the same grids, flows and numbers.</>}
        </p>
      </div>
    );
  }
  const unit = frame?.unit ?? "hour";
  const place = (e: { clientX: number; clientY: number }, kind: Hover["kind"], id: string): Hover => {
    const b = (svg.current as SVGSVGElement).getBoundingClientRect();
    return { kind, id, x: e.clientX - b.left, y: e.clientY - b.top, right: e.clientX - b.left > b.width / 2, low: e.clientY - b.top > b.height / 2 };
  };
  const moving = () => ptrs.current.size > 0 && dragged.current;
  // the tie under the pointer: the nearest line within reach (half its width, and four screen pixels for a mouse, twelve for a finger)
  const flowAt = (e: { clientX: number; clientY: number }, reach: number): MapFlow | null => {
    const m = svg.current?.getScreenCTM();
    if (!m || !drawnFlows.length) return null;
    const [bx, by] = toBox(e.clientX, e.clientY);
    const near = nearestLine([(bx - t.x) / t.k, (by - t.y) / t.k], drawnFlows.map((f) => ({ from: at.get(f.source) as [number, number], to: at.get(f.target) as [number, number] })));
    // not at a tie's ends (eight screen pixels): there the pointer is on a grid's own point, and the grid answers
    if (!near || !onTheLine(near, 8 / (t.k * m.a))) return null;
    const f = drawnFlows[near.index];
    return near.distance * t.k * m.a <= reach + flowWidth(f.mw, maxMw) / 2 ? f : null;
  };
  // two fingers zoom about the point between them; one finger, or the mouse held down, moves a map that is zoomed
  const down = (e: ReactPointerEvent<SVGSVGElement>) => {
    ptrs.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    dragged.current = false; finger.current = e.pointerType === "touch";
    if (ptrs.current.size === 2) {
      const [p, q] = [...ptrs.current.values()];
      const [px, py] = toBox((p.x + q.x) / 2, (p.y + q.y) / 2);
      pinch.current = { d: Math.hypot(p.x - q.x, p.y - q.y) || 1, from: t, px, py };
    }
  };
  const move = (e: ReactPointerEvent<SVGSVGElement>) => {
    const was = ptrs.current.get(e.pointerId);
    if (!was) {
      // no button held: a tie near the pointer takes the hover from the region under it (the region's own handler ran first)
      if (e.pointerType === "touch") return;
      const f = flowAt(e, 4);
      const here = f ? place(e, "flow", `${f.a}-${f.b}`) : null;
      setHover((h) => here ?? (h?.kind === "flow" ? null : h));
      return;
    }
    ptrs.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.current.size === 2 && pinch.current) {
      const [p, q] = [...ptrs.current.values()], g = pinch.current;
      dragged.current = true; setHover(null);
      setT(zoomMapAt(g.from, Math.hypot(p.x - q.x, p.y - q.y) / g.d, g.px, g.py, W, H));
      return;
    }
    if (ptrs.current.size !== 1 || t.k <= MAP_ZOOM[0]) return;
    if (!dragged.current && Math.hypot(e.clientX - was.x, e.clientY - was.y) < 3) { ptrs.current.set(e.pointerId, was); return; }
    if (!dragged.current) { dragged.current = true; setHover(null); try { e.currentTarget.setPointerCapture(e.pointerId); } catch { /* a pointer already gone */ } }
    const [x0, y0] = toBox(was.x, was.y), [x1, y1] = toBox(e.clientX, e.clientY);
    setT((v) => clampMapView({ k: v.k, x: v.x + (x1 - x0), y: v.y + (y1 - y0) }, W, H));
  };
  const up = (e: ReactPointerEvent<SVGSVGElement>) => { ptrs.current.delete(e.pointerId); if (ptrs.current.size < 2) pinch.current = null; };
  const zoomBy = (factor: number) => setT((v) => zoomMapAt(v, factor, W / 2, H / 2, W, H));
  // a click or a tap on the map: a finger on a tie shows the tie's figures (a finger has no hover); anything else on a region opens its panel
  const choose = (e: ReactMouseEvent<SVGSVGElement>) => {
    if (dragged.current) return;
    const f = finger.current ? flowAt(e, 12) : null;
    if (f) { setHover(place(e, "flow", `${f.a}-${f.b}`)); return; }
    const id = (e.target as Element).getAttribute?.("data-region");
    if (id) onPick(id);
    else if (finger.current) setHover(null);
  };

  // session 8601: the words of the hover, from the network's own figures for the frame shown
  const card = (() => {
    if (!hover) return null;
    if (hover.kind === "flow") {
      const f = drawnFlows.find((x) => `${x.a}-${x.b}` === hover.id);
      if (!f) return null;
      const tip = flowTip({ from: f.source, to: f.target, fromName: names.get(f.source) ?? f.source, toName: names.get(f.target) ?? f.target, mw: f.mw, when: frame?.when ?? "", unit,
        a: f.a, b: f.b, aName: names.get(f.a) ?? f.a, bName: names.get(f.b) ?? f.b, side: sideOf ? sideOf(f.a, f.b) : null });
      return { attr: { "data-map-flow-hover": `${f.source}>${f.target}`, "data-mw": String(f.mw) }, head: tip.head, lines: tip.lines.filter(Boolean), source: frame?.tables ?? "" };
    }
    const fig = figures?.(hover.id);
    const lines: string[] = [];
    if (fig) {
      lines.push(`Carbon intensity of generation: ${fig.intensity !== null ? `${fig.intensityShown ?? whole(fig.intensity)} kg CO2/MWh` : "not held"}`);
      lines.push(`Demand: ${fig.demand !== null ? `${whole(fig.demand)} MW${unit === "day" ? " on average" : ""}` : `not held for this ${unit}`}`);
      lines.push(fig.net !== null && fig.ties ? `Net ${fig.net >= 0 ? "imports" : "exports"}: ${whole(Math.abs(fig.net))} MW over ${fig.ties} tie${fig.ties === 1 ? "" : "s"}` : `No tie reported this ${unit}`);
      if (battery) { const b = battery(hover.id); lines.push(`Batteries: ${!b ? "not reported for this period" : b.mw === null ? `not reported for this ${unit}` : b.mw >= 0 ? `discharging ${whole(b.mw)} MW` : `charging ${whole(-b.mw)} MW`}`); }
      if (hover.kind === "listed") lines.push("No boundary in the file: its ties are drawn in the Network view.");
      if (frame) lines.push(frame.when);
    }
    return { attr: { "data-map-hover": hover.id }, head: names.get(hover.id) ?? hover.id, lines, source: fig && frame ? frame.tables : "" };
  })();
  // session 8601: one screen pixel in the drawing's own units, at the zoom shown: a line's width, the dash and the ring
  // are sizes on the screen (a tie's width is the rule's own pixels on a phone as on a desk, zoomed or not)
  const u = px / t.k;
  const ring = 10 * u;
  return (
    <div className={`${frameBox} self-start bg-paper`} data-map-state="held" data-map-regions={regions.length} data-map-matched={held.file.matched}
      data-map-flows={drawnFlows.length} data-map-flows-all={flows.length} data-map-no-shape={noShape.map((n) => n.id).join(",")} data-map-sha={held.file.provenance.raw_sha256}
      data-map-derived={derived ? "1" : "0"} data-map-zoom={t.k} data-map-source={held.file.provenance.source}>
      <div>
      {/* the map keeps its own proportions; a derived file's label stands under it, inside the frame, and covers no region */}
      <div className="relative" style={style}>
      <svg ref={svg} viewBox={`0 0 ${W} ${H}`} className="h-full w-full" role="img" preserveAspectRatio="xMidYMid meet" style={{ touchAction: t.k > MAP_ZOOM[0] ? "none" : "pan-y", cursor: t.k > MAP_ZOOM[0] ? "grab" : undefined }}
        onPointerDown={down} onPointerMove={move} onPointerUp={up} onPointerCancel={up} onPointerLeave={(e) => { if (!e.currentTarget.hasPointerCapture(e.pointerId)) up(e); setHover((h) => (h?.kind === "flow" ? null : h)); }}
        onClick={choose}
        aria-label="A map of the US balancing authorities, each region colored by the carbon intensity of its generation, with the power they exchange; hover a region for its name and figures, click it for its panel">
        <defs>
          <marker id="erw-flow-head" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L8,4L0,8Z" fill="var(--color-accent)" /></marker>
          <marker id="erw-flow-head-dim" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L8,4L0,8Z" fill="var(--color-rule)" /></marker>
        </defs>
        <g transform={`translate(${t.x},${t.y}) scale(${t.k})`} data-map-moved="1">
        <g>
          {regions.map((r) => {
            const dim = pick !== null && pick !== r.id && !neighbours.has(r.id);
            const fill = colorOf(r.id);
            return (
              <path key={r.id} d={r.d} fillRule="evenodd" fill={fill} fillOpacity={dim ? 0.22 : 0.9} stroke={pick === r.id ? "var(--color-ink)" : "var(--color-panel)"} strokeWidth={(pick === r.id ? 1.6 : 0.6) * u}
                data-region={r.id} data-fill={fill} data-dim={dim ? "1" : "0"} className="erw-region cursor-pointer" tabIndex={0} role="button" aria-label={names.get(r.id)}
                onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onPick(r.id); } }}
                onPointerMove={(e) => { if (!moving()) setHover(place(e, "region", r.id)); }}
                onPointerLeave={() => setHover(null)} onFocus={() => setHover({ kind: "region", id: r.id, x: -1, y: -1, right: false, low: false })} onBlur={() => setHover(null)} />
            );
          })}
        </g>
        <g pointerEvents="none" fill="none">
          {drawnFlows.map((f) => {
            const s = at.get(f.source) as [number, number], e = at.get(f.target) as [number, number];
            const dim = pick !== null && f.a !== pick && f.b !== pick;
            const w = flowWidth(f.mw, maxMw) * u;
            return (
              <g key={`${f.a}-${f.b}`} data-flow={`${f.source}>${f.target}`} data-mw={f.mw}>
                <line x1={s[0]} y1={s[1]} x2={e[0]} y2={e[1]} stroke={dim ? "var(--color-rule)" : "var(--color-muted)"} strokeOpacity={pick ? 0.6 : 0.45} strokeWidth={w} markerEnd={`url(#${dim ? "erw-flow-head-dim" : "erw-flow-head"})`} />
                {dim ? null : <line x1={s[0]} y1={s[1]} x2={e[0]} y2={e[1]} stroke="var(--color-accent)" strokeWidth={Math.max(u, w * 0.5)} strokeDasharray={`${2 * u} ${10 * u}`} strokeLinecap="round"
                  className="erw-flow-dash" style={{ animationDuration: `${Math.max(0.6, 2.4 - 1.8 * (f.mw / (maxMw || 1)))}s`, ["--erw-dash" as string]: -12 * u }} />}
              </g>
            );
          })}
        </g>
        {/* session 8601: the Batteries switch on the map: the network's ring (fuller as they discharge, emptier as they charge), over a faint whole circle */}
        {battery ? (
          <g pointerEvents="none" fill="none" data-map-batteries="1">
            {regions.map((r) => {
              const b = battery(r.id), p = at.get(r.id);
              if (!b || b.mw === null || !b.max || !p) return null;
              const dim = pick !== null && pick !== r.id && !neighbours.has(r.id);
              return (
                <g key={r.id} data-battery-ring={r.id} data-battery-mw={b.mw} data-battery-fill={batteryFill(b.mw, b.max)} opacity={dim ? 0.25 : 1}>
                  <circle cx={p[0]} cy={p[1]} r={ring} stroke="var(--color-panel)" strokeWidth={4.5 * u} />
                  <circle cx={p[0]} cy={p[1]} r={ring} stroke="var(--color-rule)" strokeWidth={1.5 * u} />
                  <path d={arcPath(p[0], p[1], ring, batteryFill(b.mw, b.max))} stroke="var(--color-ink)" strokeWidth={2.5 * u} />
                </g>
              );
            })}
          </g>
        ) : null}
        </g>
      </svg>
      <div className="absolute right-2 top-2 flex gap-1 text-sm" role="group" aria-label="Zoom the map" data-map-zoom-buttons="1">
        <button type="button" onClick={() => zoomBy(1.6)} disabled={t.k >= MAP_ZOOM[1]} className="h-8 w-8 border border-rule bg-panel text-ink disabled:text-muted" aria-label="Zoom in" title="Zoom in" data-zoom="in">+</button>
        <button type="button" onClick={() => zoomBy(1 / 1.6)} disabled={t.k <= MAP_ZOOM[0]} className="h-8 w-8 border border-rule bg-panel text-ink disabled:text-muted" aria-label="Zoom out" title="Zoom out" data-zoom="out">&minus;</button>
        <button type="button" onClick={() => setT(MAP_HOME)} disabled={t.k === 1 && t.x === 0 && t.y === 0} className="h-8 border border-rule bg-panel px-2 text-ink disabled:text-muted" title="Show the whole map" data-zoom="reset">Reset</button>
      </div>
      {card ? (
        <div className="pointer-events-none absolute z-10 max-w-[18rem] border border-rule bg-panel px-2 py-1 text-xs leading-snug text-ink" {...card.attr}
          style={hover!.x < 0 ? { left: 8, top: 8 } : { ...(hover!.right ? { right: `calc(100% - ${hover!.x - 12}px)` } : { left: hover!.x + 12 }), ...(hover!.low ? { bottom: `calc(100% - ${hover!.y - 12}px)` } : { top: hover!.y + 12 }) }}>
          <div className="text-sm" data-map-hover-name="1">{card.head}</div>
          {card.lines.map((l) => <div key={l} className="tabular-nums">{l}</div>)}
          {card.source ? <div className="text-muted" data-map-hover-source="1">Tables: {card.source}</div> : null}
        </div>
      ) : null}
      {/* the dash runs from the exporter to the importer, faster as the flow is larger; still where the reader asks for less motion */}
      <style>{`@keyframes erw-flow { to { stroke-dashoffset: var(--erw-dash, -12); } } .erw-flow-dash { animation: erw-flow 1.2s linear infinite; } .erw-region:focus { outline: none; } .erw-region:focus-visible { stroke: var(--color-ink); } @media (prefers-reduced-motion: reduce) { .erw-flow-dash { animation: none; } }`}</style>
      </div>
      {/* session 8601: the grids with no shape in the file, by name, in the map's own frame, right under it: at 1280 px a
          column beside the map took a quarter of the map's width (seen in the browser), so the names run in lines */}
      {noShape.length ? (
        <div className="border-t border-rule bg-panel px-2 py-1 text-xs" data-map-listed={noShape.length}>
          <div className="mb-1 cursor-help text-ink" title={`These ${noShape.length} balancing authorities of the network have no boundary in the file the map draws, so they have no region here. Each keeps its hover and its panel; its ties are drawn in the Network view. ${drawnFlows.length} of the ${flows.length} ties moving power in the ${unit} shown have both ends on the map.`}>
            Not on the map: no boundary in the file ({noShape.length})
          </div>
          <ul className="flex flex-wrap gap-x-3 gap-y-0.5">
            {noShape.map((n) => (
              <li key={n.id}>
                <button type="button" className={`text-left underline decoration-dotted underline-offset-2 ${pick === n.id ? "text-accent" : "text-ink"}`} data-listed={n.id} onClick={() => onPick(n.id)}
                  onPointerEnter={() => setHover({ kind: "listed", id: n.id, x: -1, y: -1, right: false, low: false })} onPointerLeave={() => setHover(null)}
                  onFocus={() => setHover({ kind: "listed", id: n.id, x: -1, y: -1, right: false, low: false })} onBlur={() => setHover(null)}>{n.name}</button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      </div>
      {/* session 8601: what a line's width is, in megawatts: the rule's own widths for the largest flow of the period shown, a quarter and a sixteenth of it */}
      <p className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-rule bg-panel px-2 py-1 text-xs text-ink" data-map-width-key={maxMw}>
        <span>Line width, megawatts:</span>
        {[1, 1 / 4, 1 / 16].map((share) => (
          <span key={share} className="flex items-center gap-1 tabular-nums">
            <svg width="28" height="10" aria-hidden="true"><line x1="0" y1="5" x2="28" y2="5" stroke="var(--color-muted)" strokeWidth={flowWidth(maxMw * share, maxMw)} /></svg>
            {whole(maxMw * share)}{share === 1 ? " (the largest of the period shown)" : ""}
          </span>
        ))}
        <span>The dash runs from the exporter to the importer.</span>
      </p>
      {derived ? (
        <p className="border-t border-rule bg-panel px-2 py-1 text-xs leading-snug text-ink" data-map-derived-label="1">
          {derived} {held.file.provenance.vintage ? <>Data year: {held.file.provenance.vintage}.</> : null}
        </p>
      ) : (
        <p className="border-t border-rule bg-panel px-2 py-1 text-xs leading-snug text-ink" data-map-source-label="1">
          Boundaries: {held.file.provenance.source}, retrieved {(held.file.provenance.retrieved_utc ?? "").slice(0, 10)}{held.file.provenance.simplification.tolerance_degrees ? <>, simplified to {held.file.provenance.simplification.tolerance_degrees} degrees for the web</> : null}.
        </p>
      )}
    </div>
  );
}
