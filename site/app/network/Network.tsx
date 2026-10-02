"use client";
// Session 49 (session 42's B4): the 3D grid network. 3d-force-graph draws the balancing authorities at the fixed
// positions of the snapshot (data/grid_network.json, warehouse/derived/grid_network.py), never re-settled; each hour of
// the 168 is a frame: link width and particle speed follow the hour's MW, particles run in the direction of flow.
// Session 68: the network as a tool, its look unchanged (free-floating, light, names on hover, carbon intensity as the
// sphere color at all times). Four Watch buttons set the time range, move the camera to the grid a story is about and
// play: the live week, California's evening (the newest complete Pacific day, batteries on), Texas during Uri and the
// June 2025 heat (public/network/story_<event>.json, warehouse/derived/network_stories.py). Clicking a grid opens a panel
// beside the network (Escape or its button closes it): the hour's net imports and who supplies them, the hub price, carbon
// intensity, the last twelve months from ba_supply_monthly (lib/basupply.ts), and for ERCOT and CAISO a link to what a
// battery earns there. The selected grid and its ties stay as they are and the rest is dimmed; nobody's color changes. The
// Batteries switch (off by default) draws one thin ring around each grid whose batteries are reported for the hour shown,
// fuller as they discharge and emptier as they charge.
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Num } from "@/components/Num";
import { shown } from "@/lib/format";
import { HEADLINE, MEASURES, SPREAD, type Measure, type Supply } from "@/lib/basupply";

export type NetNode = { id: string; name: string; iso: string | null; demand_mw: number | null; demand_ts: string | null;
  intensity: number | null; intensity_ts: string | null; volume_mwh: number; x: number; y: number; z: number;
  // session 54: set by the hourly refresh (warehouse/derived/network_hourly.py) on the seven ISO BAs
  demand_src?: "hourly"; demand_recent?: Record<string, number> };
export type NetLink = { a: string; b: string; mw: (number | null)[] };
export type Snapshot = { built: string; window: [string, string]; hours: string[]; rule: string; nodes: NetNode[]; links: NetLink[];
  // session 54: the hourly snapshot's newest complete hour and the daily build it was merged onto
  newest_hour?: string; refresh?: "hourly"; base_built?: string };
/** Session 68: a historical story (warehouse/derived/network_stories.py). */
export type Story = { event: string; title: string; focus: string; tz: string; window: [string, string]; hours: string[]; built: string; rule: string;
  links: NetLink[]; demand: Record<string, (number | null)[]>; intensity: Record<string, Record<string, number>>; intensity_days: string[];
  batteries: Record<string, (number | null)[]>; hub_prices: Record<string, (number | null)[]>;
  missing: { link_hours: number; link_hours_from_other_side: number; demand_hours: number; left_out_bas: string[]; nodes_without_demand: string[]; batteries_reported: string[] } };
/** Session 68: the live week's extras, read by the page from Supabase and aligned to the snapshot's hours. */
export type LiveExtras = { batteries: Record<string, (number | null)[]>; batterySource: Record<string, string>; prices: Record<string, (number | null)[]>;
  priceKind: Record<string, string>; demand: Record<string, (number | null)[]> };

const ET = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
const fmt = (v: number) => (Math.round(v) === 0 ? 0 : Math.round(v)).toLocaleString("en-US");  // never "-0"
const GRID_SLUG: Record<string, string> = { CAISO: "caiso", ERCOT: "ercot", "ISO-NE": "isone", MISO: "miso", NYISO: "nyiso", PJM: "pjm", SPP: "spp" };
// the seven ISO balancing authorities' local time (the price board's operating days); the others' is not held
const LOCAL_TZ: Record<string, string> = { CISO: "America/Los_Angeles", ERCO: "America/Chicago", ISNE: "America/New_York", MISO: "Etc/GMT+5",
  NYIS: "America/New_York", PJM: "America/New_York", SWPP: "America/Chicago" };
// EIA's regional sums, which report interchange like balancing authorities but are not drawn
const EIA_REGIONS = new Set(["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX", "US48", "CAN", "MEX"]);
const BATTERY_PAGE: Record<string, string> = { ERCO: "ercot", CISO: "caiso" };
const STORIES: Record<string, { label: string; file: string }> = {
  uri_2021: { label: "Texas during Uri", file: "/network/story_uri_2021.json" },
  east_heat_2025: { label: "The June 2025 heat", file: "/network/story_east_heat_2025.json" },
};

/** Green (low) to cardinal (high) for carbon intensity, kg CO2/MWh, over the held BAs' range; grey where not held. */
function colorOf(v: number | null, lo: number, hi: number): string {
  if (v === null) return "#9a958c";
  const t = Math.max(0, Math.min(1, (v - lo) / (hi - lo || 1)));
  const a = [0x17, 0x5e, 0x54], b = [0x8c, 0x15, 0x15];
  return `rgb(${a.map((c, i) => Math.round(c + (b[i] - c) * t)).join(",")})`;
}
const localTime = (ts: string, tz: string) => new Intl.DateTimeFormat("en-US", { timeZone: tz, weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(ts));
const pct = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** What the network draws: the live week or a story, the same nodes either way. */
type View = {
  kind: "live" | "story"; key: string; title: string; hours: string[]; links: NetLink[];
  intensity: (id: string, h: number) => number | null; demand: (id: string, h: number) => number | null;
  battery: (id: string, h: number) => number | null; batteryReported: (id: string) => boolean; batterySource: (id: string) => string;
  price: (id: string, h: number) => number | null; priceKind: (id: string) => string; note?: string;
};

export function Network({ snap, supply, live }: { snap: Snapshot; supply: Record<string, Supply>; live: LiveExtras }) {
  const box = useRef<HTMLDivElement>(null);
  const graph = useRef<any>(null); // eslint-disable-line @typescript-eslint/no-explicit-any
  const three = useRef<any>(null); // eslint-disable-line @typescript-eslint/no-explicit-any
  const liveView: View = useMemo(() => ({
    kind: "live", key: "live", title: "The live week", hours: snap.hours, links: snap.links,
    intensity: (id) => snap.nodes.find((n) => n.id === id)?.intensity ?? null,
    demand: (id, h) => {
      const n = snap.nodes.find((x) => x.id === id);
      const ts = snap.hours[h];
      if (!n) return null;
      const d = live.demand[id]?.[h];
      if (d !== null && d !== undefined) return d;  // the seven ISOs' hourly demand of the week (eia930_all_demand)
      if (n.demand_recent && ts in n.demand_recent) return n.demand_recent[ts];
      return n.demand_ts === ts ? n.demand_mw : null;
    },
    battery: (id, h) => live.batteries[id]?.[h] ?? null, batteryReported: (id) => !!live.batteries[id], batterySource: (id) => live.batterySource[id] ?? "",
    price: (id, h) => live.prices[id]?.[h] ?? null, priceKind: (id) => live.priceKind[id] ?? "",
  }), [snap, live]);
  const [view, setView] = useState<View>(liveView);
  const [range, setRange] = useState<[number, number]>([0, snap.hours.length]);
  const [hour, setHour] = useState(snap.hours.length - 1);
  const [playing, setPlaying] = useState(false);
  const [pick, setPick] = useState<NetNode | null>(null);
  const [batteriesOn, setBatteriesOn] = useState(false);
  const [noGl, setNoGl] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const stories = useRef<Record<string, Story>>({});

  const held = useMemo(() => {
    const vals: number[] = [];
    for (const n of snap.nodes) for (let h = range[0]; h < range[1]; h += 24) { const v = view.intensity(n.id, h); if (v !== null) vals.push(v); }
    return vals.length ? vals : [0, 1];
  }, [view, range, snap.nodes]);
  const lo = Math.min(...held), hi = Math.max(...held);
  const ciTs = snap.nodes.map((n) => n.intensity_ts ?? "").reduce((a, b) => (b > a ? b : a), "");
  const maxDemand = Math.max(...snap.nodes.map((n) => n.demand_mw ?? 0)), maxVol = Math.max(...snap.nodes.map((n) => n.volume_mwh));
  const maxMw = Math.max(1, ...view.links.flatMap((l) => l.mw.map((v) => Math.abs(v ?? 0))));
  // session 68: a little smaller than before, so the ties between the spheres can be followed
  const size = (n: NetNode) => (n.demand_mw !== null ? 3 + 22 * Math.sqrt(n.demand_mw / maxDemand) : 2 + 10 * Math.sqrt(n.volume_mwh / maxVol));
  const batteryMax = useMemo(() => {
    const out: Record<string, number> = {};
    for (const n of snap.nodes) {
      let m = 0;
      for (let h = range[0]; h < range[1]; h++) { const v = view.battery(n.id, h); if (v !== null) m = Math.max(m, Math.abs(v)); }
      if (m > 0) out[n.id] = m;
    }
    return out;
  }, [view, range, snap.nodes]);

  const linksAt = useCallback((h: number) => view.links.filter((l) => l.mw[h] !== null && l.mw[h] !== undefined && l.mw[h] !== 0).map((l) => {
    const v = l.mw[h] as number;
    return { source: v > 0 ? l.a : l.b, target: v > 0 ? l.b : l.a, mw: Math.abs(v), a: l.a, b: l.b };
  }), [view]);

  // the node's own object: the same sphere 3d-force-graph draws (radius cube root of the value times 4), with its own
  // opacity so the rest can be dimmed without changing a color, and the battery ring when the switch is on
  const nodeObject = useCallback((n: NetNode) => {
    const THREE = three.current;
    const g = new THREE.Group();
    const r = Math.cbrt(size(n)) * 4;
    const dim = pick !== null && pick.id !== n.id && !view.links.some((l) => (l.a === pick.id && l.b === n.id) || (l.b === pick.id && l.a === n.id));
    const mat = new THREE.MeshLambertMaterial({ color: colorOf(view.intensity(n.id, hour), lo, hi), transparent: true, opacity: dim ? 0.22 : 0.95 });
    g.add(new THREE.Mesh(new THREE.SphereGeometry(r, 16, 12), mat));
    const mw = batteriesOn ? view.battery(n.id, hour) : null;
    if (batteriesOn && mw !== null && batteryMax[n.id]) {
      const f = Math.max(0.02, Math.min(1, 0.5 + 0.5 * (mw / batteryMax[n.id])));  // full: discharging at its most; empty: charging
      const pts = [];
      for (let k = 0; k <= 64 * f; k++) { const t = Math.PI / 2 - (2 * Math.PI * k) / 64; pts.push(new THREE.Vector3(Math.cos(t) * r * 1.45, Math.sin(t) * r * 1.45, 0)); }
      const ring = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: "#2E2D29", transparent: true, opacity: dim ? 0.25 : 0.85 }));
      ring.onBeforeRender = (_r: unknown, _s: unknown, camera: { quaternion: unknown }) => { ring.quaternion.copy(camera.quaternion); };
      g.add(ring);
    }
    return g;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, hour, lo, hi, pick, batteriesOn, batteryMax]);

  useEffect(() => {
    let alive = true;
    const el = box.current;
    if (!el) return;
    const fail = () => { queueMicrotask(() => setNoGl(true)); };  // not synchronously inside the effect
    try {
      const c = document.createElement("canvas");
      if (!(c.getContext("webgl2") || c.getContext("webgl"))) { fail(); return; }
    } catch { fail(); return; }
    Promise.all([import("3d-force-graph"), import("three")]).then(([{ default: ForceGraph3D }, THREE]) => {
      if (!alive || !el) return;
      three.current = THREE;
      const nodes = snap.nodes.map((n) => ({ ...n, fx: n.x, fy: n.y, fz: n.z }));
      const g = new ForceGraph3D(el, { controlType: "orbit" })
        .width(el.clientWidth).height(el.clientHeight).backgroundColor("#FBF8F2")
        .graphData({ nodes, links: linksAt(snap.hours.length - 1) })
        .nodeId("id").nodeLabel((n: object) => (n as NetNode).name)
        .nodeVal((n: object) => size(n as NetNode)).nodeThreeObject((n: object) => nodeObject(n as NetNode))
        .linkColor(() => "#6B665E").linkOpacity(0.45)
        .linkWidth((l: object) => 0.4 + 3 * Math.sqrt((l as { mw: number }).mw / maxMw))
        .linkDirectionalParticles((l: object) => ((l as { mw: number }).mw > 0 ? 2 : 0))
        .linkDirectionalParticleSpeed((l: object) => 0.002 + 0.02 * ((l as { mw: number }).mw / maxMw))
        .linkDirectionalParticleWidth(1.6).linkDirectionalParticleColor(() => "#8C1515")
        .cooldownTicks(0).enableNodeDrag(false)
        .onNodeClick((n: object) => setPick(snap.nodes.find((x) => x.id === (n as NetNode).id) ?? null));
      const ctl = g.controls() as { autoRotate: boolean; autoRotateSpeed: number; addEventListener: (e: string, f: () => void) => void };
      ctl.autoRotate = true;
      ctl.autoRotateSpeed = 0.6;
      ctl.addEventListener("start", () => { ctl.autoRotate = false; }); // stops when touched
      g.cameraPosition({ x: 0, y: 0, z: 700 });
      graph.current = g;
      // session 68: the network fills its frame when the page opens
      setTimeout(() => { if (alive) g.zoomToFit(0, 10); }, 300);
      setTimeout(() => { if (alive) g.zoomToFit(400, 10); }, 1200);
    }).catch(() => setNoGl(true));
    const onResize = () => { if (graph.current && el) graph.current.width(el.clientWidth).height(el.clientHeight); };
    window.addEventListener("resize", onResize);
    return () => { alive = false; window.removeEventListener("resize", onResize); graph.current?._destructor?.(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // each hour, view, selection or switch: the links and the nodes' objects again
  useEffect(() => {
    const g = graph.current;
    if (!g) return;
    const { nodes } = g.graphData();
    g.graphData({ nodes, links: linksAt(hour) });
    g.nodeThreeObject((n: object) => nodeObject(n as NetNode));
    g.linkOpacity(pick ? 0.6 : 0.45)
      .linkColor((l: object) => { const x = l as { a: string; b: string }; return pick && x.a !== pick.id && x.b !== pick.id ? "#D9D2C3" : "#6B665E"; })
      .linkDirectionalParticles((l: object) => { const x = l as { a: string; b: string; mw: number }; return pick && x.a !== pick.id && x.b !== pick.id ? 0 : (x.mw > 0 ? 2 : 0); });
  }, [hour, view, pick, batteriesOn, linksAt, nodeObject]);

  // the panel opening or closing changes the frame's width: the canvas follows it
  useEffect(() => {
    const t = setTimeout(() => { const el = box.current; if (graph.current && el) graph.current.width(el.clientWidth).height(el.clientHeight); }, 0);
    return () => clearTimeout(t);
  }, [pick]);

  useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => setHour((h) => (h + 1 >= range[1] || h < range[0] ? range[0] : h + 1)), 700);
    return () => clearInterval(t);
  }, [playing, range]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setPick(null); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const focusOn = (id: string | null) => {
    const g = graph.current;
    if (!g) return;
    if (!id) { g.zoomToFit(1200, 20); return; }
    const n = snap.nodes.find((x) => x.id === id);
    if (!n) return;
    const d = Math.hypot(n.x, n.y, n.z) || 1, k = 1 + 260 / d;
    (g.controls() as { autoRotate: boolean }).autoRotate = false;
    g.cameraPosition({ x: n.x * k, y: n.y * k, z: n.z * k + 60 }, { x: n.x, y: n.y, z: n.z }, 1500);
  };

  const watchLive = () => {
    setFailed(null); setView(liveView); setRange([0, snap.hours.length]); setHour(snap.hours.length - 1); setPick(null); focusOn(null); setPlaying(true);
  };
  const watchEvening = () => {
    // the newest Pacific day whose every hour is in the live week
    const day = (ts: string) => new Intl.DateTimeFormat("en-CA", { timeZone: "America/Los_Angeles" }).format(new Date(ts));
    const days = [...new Set(snap.hours.map(day))];
    for (const d of days.reverse()) {
      const idx = snap.hours.map((t, i) => (day(t) === d ? i : -1)).filter((i) => i >= 0);
      const want = Math.round((new Date(`${d}T00:00:00Z`).getTime() + 86_400_000 - new Date(`${d}T00:00:00Z`).getTime()) / 3_600_000);
      const contiguous = idx.length >= 23 && idx.at(-1)! - idx[0] + 1 === idx.length;
      if (contiguous && idx.length >= want - 1 && idx[0] > 0 && idx.at(-1)! < snap.hours.length - 1) {
        setFailed(null); setView({ ...liveView, key: "evening", title: `California's evening, ${d} (Pacific)` }); setRange([idx[0], idx.at(-1)! + 1]); setHour(idx[0]);
        setBatteriesOn(true); setPick(snap.nodes.find((n) => n.id === "CISO") ?? null); focusOn("CISO"); setPlaying(true);
        return;
      }
    }
    setFailed("The live week holds no complete Pacific day.");
  };
  const watchStory = async (event: string) => {
    setPlaying(false); setFailed(null);
    let s = stories.current[event];
    if (!s) {
      setLoading(event);
      try {
        const r = await fetch(STORIES[event].file);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        s = (await r.json()) as Story;
        stories.current[event] = s;
      } catch (e) {
        setLoading(null); setFailed(`${STORIES[event].label} could not be loaded (${(e as Error).message}).`);
        return;
      }
      setLoading(null);
    }
    const dayOf = (ts: string) => new Intl.DateTimeFormat("en-CA", { timeZone: s.tz }).format(new Date(ts));
    const v: View = {
      kind: "story", key: event, title: `${s.title}, ${s.window[0]} to ${s.window[1]}`, hours: s.hours, links: s.links,
      intensity: (id, h) => s.intensity[id]?.[dayOf(s.hours[h])] ?? null,
      demand: (id, h) => s.demand[id]?.[h] ?? null,
      battery: (id, h) => s.batteries[id]?.[h] ?? null, batteryReported: (id) => !!s.batteries[id], batterySource: () => "EIA-930",
      price: (id, h) => s.hub_prices[id]?.[h] ?? null, priceKind: () => "real time",
      note: `${s.missing.link_hours.toLocaleString("en-US")} pair-hours not reported by either side (left blank); ${s.missing.link_hours_from_other_side.toLocaleString("en-US")} read from the other side's report; ${s.missing.demand_hours.toLocaleString("en-US")} hours of demand not reported. Batteries reported for this period: ${s.missing.batteries_reported.length ? s.missing.batteries_reported.join(", ") : "none"}. Not drawn (no place in today's network): ${s.missing.left_out_bas.filter((b) => !EIA_REGIONS.has(b)).join(", ") || "none"}.`,
    };
    setView(v); setRange([0, s.hours.length]); setHour(0); setPick(snap.nodes.find((n) => n.id === s.focus) ?? null); focusOn(s.focus); setPlaying(true);
  };

  const ts = view.hours[Math.min(hour, view.hours.length - 1)];
  const nameOf = (id: string) => snap.nodes.find((n) => n.id === id)?.name ?? id;
  const ties = useMemo(() => (pick ? view.links.filter((l) => l.a === pick.id || l.b === pick.id).map((l) => {
    const v = l.mw[hour];
    if (v === null || v === undefined) return null;
    return { other: l.a === pick.id ? l.b : l.a, imp: l.a === pick.id ? -v : v };  // positive: the neighbour supplies this grid
  }).filter((x): x is { other: string; imp: number } => !!x).sort((x, y) => y.imp - x.imp) : []), [pick, hour, view]);
  const netImport = ties.reduce((a, t) => a + t.imp, 0);
  const demandNow = pick ? view.demand(pick.id, hour) : null;
  const buttons = "border border-accent px-3 py-1 text-sm text-accent hover:bg-paper";
  // the live week's demand carries its check key: from the hourly refresh's snapshot in Storage, else eia930_all_demand
  const demandKey = (n: NetNode, t: string, v: number) => {
    if (view.kind !== "live") return fmt(v);
    const check = n.demand_src === "hourly" && n.demand_recent && t in n.demand_recent && n.demand_recent[t] === v
      ? `netsnap|${n.id}|demand_mw|${t}` : `series|eia930_all_demand|eia930:${n.id}|demand_mw|${t}`;
    return <Num check={check} raw={v}>{shown(v)}</Num>;
  };

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-2 text-sm" role="group" aria-label="Watch">
        <span className="mr-1 text-muted">Watch:</span>
        <button type="button" onClick={watchLive} className={buttons} aria-pressed={view.key === "live"}>Live now</button>
        <button type="button" onClick={watchEvening} className={buttons} aria-pressed={view.key === "evening"}>California&apos;s evening</button>
        <button type="button" onClick={() => watchStory("uri_2021")} className={buttons} aria-pressed={view.key === "uri_2021"}>{loading === "uri_2021" ? "Loading..." : "Texas during Uri"}</button>
        <button type="button" onClick={() => watchStory("east_heat_2025")} className={buttons} aria-pressed={view.key === "east_heat_2025"}>{loading === "east_heat_2025" ? "Loading..." : "The June 2025 heat"}</button>
      </div>
      <div className="mb-2 flex flex-wrap items-center gap-3 text-sm">
        <button type="button" onClick={() => setPlaying(!playing)} className="border border-accent px-3 py-1 text-accent">{playing ? "Pause" : "Play"}</button>
        <input type="range" min={range[0]} max={range[1] - 1} value={Math.min(Math.max(hour, range[0]), range[1] - 1)} onChange={(e) => { setPlaying(false); setHour(Number(e.target.value)); }}
          className="w-64" aria-label="Hour shown" />
        <span className="tabular-nums">{ts.slice(0, 13).replace("T", " ")}:00 UTC, {ET.format(new Date(ts))} Eastern</span>
        <button type="button" role="switch" aria-checked={batteriesOn} onClick={() => setBatteriesOn(!batteriesOn)}
          className={`ml-auto border px-3 py-1 ${batteriesOn ? "border-ink bg-ink text-white" : "border-rule text-ink"}`}>Batteries: {batteriesOn ? "on" : "off"}</button>
      </div>
      <div className="mb-1 text-xs text-muted" data-network-view={view.key}>
        Showing: {view.title}.{failed ? <span className="text-accent"> {failed}</span> : null}{view.note ? <> {view.note}</> : null}
      </div>
      <div className={`grid grid-cols-[minmax(0,1fr)] gap-3 ${pick ? "lg:grid-cols-[minmax(0,1fr)_340px]" : ""}`}>
        {noGl ? (
          <p className="border border-rule bg-panel p-4 text-sm">
            This browser cannot draw 3D (WebGL is not available), so the network is not shown. The table of balancing authorities below, and{" "}
            <Link href="/grid">grid conditions</Link>, hold the same numbers.
          </p>
        ) : (
          <div ref={box} className="w-full min-w-0 cursor-grab overflow-hidden border border-rule" style={{ height: "min(72vh, 620px)", minHeight: 420 }}
            aria-label="A 3D network of the US balancing authorities and their interchange; drag to rotate, scroll to zoom, click a grid for its panel" role="img" />
        )}
        {pick ? (
          <aside className="border border-rule bg-panel p-3 text-sm" aria-label={`${pick.name}, the hour shown`} data-panel={pick.id}>
            <div className="mb-2 flex items-start justify-between gap-2">
              <div>
                <div className="font-serif text-lg text-accent">{pick.name}</div>
                <div className="font-mono text-xs text-muted">{pick.id}{pick.iso ? <> &middot; <Link href={`/grid/${GRID_SLUG[pick.iso]}`}>{pick.iso}&apos;s grid page</Link></> : null}</div>
              </div>
              <button type="button" onClick={() => setPick(null)} className="border border-rule px-2 py-0.5 text-xs" aria-label="Close the panel">Close</button>
            </div>
            <p className="mb-2 text-xs">{LOCAL_TZ[pick.id] ? <>{localTime(ts, LOCAL_TZ[pick.id])} local time</> : <>{ts.slice(0, 13).replace("T", " ")}:00 UTC (its local time is not held)</>}</p>
            <dl className="space-y-1.5">
              <div>
                <dt className="text-xs text-muted">Net {netImport >= 0 ? "imports" : "exports"} this hour</dt>
                <dd>{ties.length ? <>{fmt(Math.abs(netImport))} MW{demandNow ? <>, {pct((Math.abs(netImport) / demandNow) * 100)} percent of its {demandKey(pick, ts, demandNow)} MW demand</> : <> (its demand for this hour is not held)</>}</> : "no tie reported this hour"}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted">Who is supplying it, largest first</dt>
                <dd>{ties.length ? (
                  <ul className="mt-0.5 space-y-0.5 tabular-nums">
                    {ties.map((t) => <li key={t.other} className="flex justify-between gap-2"><span>{nameOf(t.other)} <span className="font-mono text-[10px] text-muted">{t.other}</span></span><span className="whitespace-nowrap">{Math.round(t.imp) === 0 ? "0 MW" : t.imp > 0 ? `${fmt(t.imp)} MW in` : `${fmt(-t.imp)} MW out`}</span></li>)}
                  </ul>
                ) : "none reported"}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted">Hub price this hour</dt>
                <dd>{pick.id === "PJM" ? "Not shown: PJM's prices are licensed" : (() => { const p = view.price(pick.id, hour); return p !== null ? <>{p.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD/MWh <span className="text-xs text-muted">({view.priceKind(pick.id)})</span></> : (pick.iso ? "Not held for this hour" : "No public hub price in the warehouse"); })()}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted">Carbon intensity of generation</dt>
                <dd>{(() => { const c = view.intensity(pick.id, hour); return c !== null ? <>{view.kind === "live" && pick.intensity_ts ? <Num check={`series|carbon_intensity_hourly|eia930:${pick.id}|intensity_generation|${pick.intensity_ts}`} raw={c}>{shown(c)}</Num> : fmt(c)} kg CO2/MWh <span className="text-xs text-muted">({view.kind === "live" ? "the latest hour held" : "that day"})</span></> : "Not held"; })()}</dd>
              </div>
              {batteriesOn ? (
                <div>
                  <dt className="text-xs text-muted">Its batteries</dt>
                  <dd>{view.batteryReported(pick.id) ? (() => { const b = view.battery(pick.id, hour); return b === null ? "Not reported for this hour" : <>{b >= 0 ? `discharging ${fmt(b)} MW` : `charging ${fmt(-b)} MW`} <span className="text-xs text-muted">({view.batterySource(pick.id)})</span></>; })() : "Not reported for this period"}</dd>
                </div>
              ) : null}
              <div className="border-t border-rule pt-1.5">
                <dt className="text-xs text-muted">Over the last twelve months</dt>
                <dd>{(() => {
                  const s = supply[pick.id];
                  if (!s) return pick.iso ? "Not held" : "Not held: a share needs the grid's demand, which the warehouse holds for the seven ISO grids only";
                  const top = s.neighbours[0];
                  const range3 = s.spread !== null && s.spread > SPREAD ? (Object.keys(MEASURES) as Measure[]).map((k) => s.share[k]).filter((v): v is number => v !== undefined) : null;
                  return (
                    <>
                      {s.hasDemand ? <>Net imports {pct(s.share[HEADLINE]!)} percent of demand ({MEASURES[HEADLINE]})</> : <>Net imports {fmt(s.mwh[HEADLINE] ?? 0)} MWh ({MEASURES[HEADLINE]}; its demand is not held, so no share)</>}.
                      {range3 ? <> The three measures disagree: {pct(Math.min(...range3))} to {pct(Math.max(...range3))} percent (see below).</> : null}
                      {top ? <> Largest supplier: {nameOf(top.id)}{top.share !== null ? <>, {pct(top.share)} percent of demand</> : <>, {fmt(top.mwh)} MWh</>}.</> : null}
                      <span className="block text-xs text-muted">{s.months[0]} to {s.months.at(-1)}; {s.daysHeld} days held, {s.daysLeftOut} left out{s.thin ? `, ${s.thin} thin month${s.thin > 1 ? "s" : ""}` : ""}.</span>
                    </>
                  );
                })()}</dd>
              </div>
            </dl>
            {BATTERY_PAGE[pick.id] ? <p className="mt-2 text-sm"><Link href={`/cost-of-power/battery?grid=${BATTERY_PAGE[pick.id]}`}>What a battery earns here</Link></p> : null}
          </aside>
        ) : null}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-muted">
        <span>Drag to rotate, scroll to zoom, click a grid; it turns slowly until touched.</span>
        <span className="flex items-center gap-1">Carbon intensity of generation:
          <span className="inline-block h-2 w-24" style={{ background: "linear-gradient(90deg, #175E54, #8C1515)" }} /> {fmt(lo)} to {fmt(hi)} kg CO2/MWh; grey: not held.
          {view.kind === "live" ? <> The color updates daily (latest hour {ciTs.slice(0, 13).replace("T", " ")}:00 UTC); the links and demand, hourly.</> : <> In a story, each day&apos;s own.</>}</span>
        <span>Sphere: demand (the seven ISOs) or interchange volume (the others)</span>
        {batteriesOn ? <span>Ring: batteries reported for the hour, fuller as they discharge, emptier as they charge.</span> : null}
      </div>
      <label className="mt-3 block text-sm">Show a balancing authority:{" "}
        <select className="w-full max-w-md border border-rule bg-panel px-2 py-1 text-sm sm:w-auto" value={pick?.id ?? ""} onChange={(e) => setPick(snap.nodes.find((n) => n.id === e.target.value) ?? null)}>
          <option value="">none</option>
          {[...snap.nodes].sort((a, b) => a.name.localeCompare(b.name)).map((n) => <option key={n.id} value={n.id}>{n.name} ({n.id})</option>)}
        </select>
      </label>
      <details className="mt-4 border-t border-rule pt-2 text-sm">
        <summary className="cursor-pointer font-serif text-lg text-accent">{pick ? `${pick.name}'s neighbours, last twelve months` : "A grid's neighbours, last twelve months"}</summary>
        {pick && supply[pick.id] ? (
          <div className="mt-2 overflow-x-auto">
            <table className="w-full min-w-[420px] text-sm tabular-nums">
              <thead><tr className="bg-accent text-left text-white"><th className="px-2 py-1 font-normal">Neighbour</th><th className="px-2 py-1 text-right font-normal">Net imports, MWh</th><th className="px-2 py-1 text-right font-normal">Share of demand</th></tr></thead>
              <tbody>
                {supply[pick.id].neighbours.map((n) => (
                  <tr key={n.id} className="border-b border-rule"><td className="px-2 py-1">{nameOf(n.id)} <span className="font-mono text-[10px] text-muted">{n.id}</span></td><td className="px-2 py-1 text-right">{fmt(n.mwh)}</td><td className="px-2 py-1 text-right">{n.share === null ? "" : `${pct(n.share)} percent`}</td></tr>
                ))}
              </tbody>
            </table>
            <p className="mt-1 text-xs text-muted">Positive: the neighbour supplied {pick.name}; negative: {pick.name} supplied it. Over the held days of {supply[pick.id].months[0]} to {supply[pick.id].months.at(-1)}, as {pick.name} reported each tie.</p>
          </div>
        ) : <p className="mt-2 text-muted">Click a grid, or choose one above.</p>}
      </details>
    </div>
  );
}
