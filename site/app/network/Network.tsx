"use client";
// Session 49 (session 42's B4): the 3D grid network. 3d-force-graph draws the balancing authorities at the fixed
// positions of the snapshot (data/grid_network.json, warehouse/derived/grid_network.py), never re-settled; each hour of
// the 168 is a frame: link width and particle speed follow the hour's MW, particles run in the direction of flow.
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { Num } from "@/components/Num";
import { shown } from "@/lib/format";

export type NetNode = { id: string; name: string; iso: string | null; demand_mw: number | null; demand_ts: string | null;
  intensity: number | null; intensity_ts: string | null; volume_mwh: number; x: number; y: number; z: number };
export type NetLink = { a: string; b: string; mw: (number | null)[] };
export type Snapshot = { built: string; window: [string, string]; hours: string[]; rule: string; nodes: NetNode[]; links: NetLink[] };

const ET = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
const fmt = (v: number) => Math.round(v).toLocaleString("en-US");
const GRID_SLUG: Record<string, string> = { CAISO: "caiso", ERCOT: "ercot", "ISO-NE": "isone", MISO: "miso", NYISO: "nyiso", PJM: "pjm", SPP: "spp" };

/** Green (low) to cardinal (high) for carbon intensity, kg CO2/MWh, over the held BAs' range; grey where not held. */
function colorOf(v: number | null, lo: number, hi: number): string {
  if (v === null) return "#9a958c";
  const t = Math.max(0, Math.min(1, (v - lo) / (hi - lo || 1)));
  const a = [0x17, 0x5e, 0x54], b = [0x8c, 0x15, 0x15];
  return `rgb(${a.map((c, i) => Math.round(c + (b[i] - c) * t)).join(",")})`;
}

export function Network({ snap }: { snap: Snapshot }) {
  const box = useRef<HTMLDivElement>(null);
  const graph = useRef<any>(null); // eslint-disable-line @typescript-eslint/no-explicit-any
  const [hour, setHour] = useState(snap.hours.length - 1);
  const [playing, setPlaying] = useState(false);
  const [pick, setPick] = useState<NetNode | null>(snap.nodes.find((n) => n.id === "ERCO") ?? null);
  const [noGl, setNoGl] = useState(false);
  const held = snap.nodes.filter((n) => n.intensity !== null).map((n) => n.intensity as number);
  const lo = Math.min(...held), hi = Math.max(...held);
  const maxDemand = Math.max(...snap.nodes.map((n) => n.demand_mw ?? 0)), maxVol = Math.max(...snap.nodes.map((n) => n.volume_mwh));
  const maxMw = Math.max(1, ...snap.links.flatMap((l) => l.mw.map((v) => Math.abs(v ?? 0))));
  const size = (n: NetNode) => (n.demand_mw !== null ? 4 + 30 * Math.sqrt(n.demand_mw / maxDemand) : 2 + 12 * Math.sqrt(n.volume_mwh / maxVol));

  const linksAt = (h: number) => snap.links.filter((l) => l.mw[h] !== null && l.mw[h] !== 0).map((l) => {
    const v = l.mw[h] as number;
    return { source: v > 0 ? l.a : l.b, target: v > 0 ? l.b : l.a, mw: Math.abs(v) };
  });

  useEffect(() => {
    let alive = true;
    const el = box.current;
    if (!el) return;
    const fail = () => { queueMicrotask(() => setNoGl(true)); };  // not synchronously inside the effect
    try {
      const c = document.createElement("canvas");
      if (!(c.getContext("webgl2") || c.getContext("webgl"))) { fail(); return; }
    } catch { fail(); return; }
    import("3d-force-graph").then(({ default: ForceGraph3D }) => {
      if (!alive || !el) return;
      const nodes = snap.nodes.map((n) => ({ ...n, fx: n.x, fy: n.y, fz: n.z }));
      const g = new ForceGraph3D(el, { controlType: "orbit" })
        .width(el.clientWidth).height(520).backgroundColor("#FBF8F2")
        .graphData({ nodes, links: linksAt(snap.hours.length - 1) })
        .nodeId("id").nodeLabel((n: object) => (n as NetNode).name)
        .nodeVal((n: object) => size(n as NetNode)).nodeColor((n: object) => colorOf((n as NetNode).intensity, lo, hi)).nodeOpacity(0.95)
        .linkColor(() => "#6B665E").linkOpacity(0.35)
        .linkWidth((l: object) => 0.3 + 4 * Math.sqrt((l as { mw: number }).mw / maxMw))
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
    }).catch(() => setNoGl(true));
    const onResize = () => graph.current?.width(el.clientWidth);
    window.addEventListener("resize", onResize);
    return () => { alive = false; window.removeEventListener("resize", onResize); graph.current?._destructor?.(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const g = graph.current;
    if (!g) return;
    const { nodes } = g.graphData();
    g.graphData({ nodes, links: linksAt(hour) });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hour]);

  useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => setHour((h) => (h + 1) % snap.hours.length), 700);
    return () => clearInterval(t);
  }, [playing, snap.hours.length]);

  const flows = useMemo(() => (pick ? snap.links.filter((l) => l.a === pick.id || l.b === pick.id).map((l) => {
    const v = l.mw[hour];
    if (v === null) return null;
    const out = l.a === pick.id ? v : -v; // positive: the picked BA exports
    return { other: l.a === pick.id ? l.b : l.a, mw: out };
  }).filter((x): x is { other: string; mw: number } => !!x).sort((x, y) => Math.abs(y.mw) - Math.abs(x.mw)).slice(0, 3) : []), [pick, hour, snap.links]);
  const nameOf = (id: string) => snap.nodes.find((n) => n.id === id)?.name ?? id;
  const ts = snap.hours[hour];

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-3 text-sm">
        <button onClick={() => setPlaying(!playing)} className="border border-accent px-3 py-1 text-accent">{playing ? "Pause" : "Play"}</button>
        <input type="range" min={0} max={snap.hours.length - 1} value={hour} onChange={(e) => { setPlaying(false); setHour(Number(e.target.value)); }}
          className="w-64" aria-label="Hour of the week shown" />
        <span className="tabular-nums">{ts.slice(0, 13).replace("T", " ")}:00 UTC, {ET.format(new Date(ts))} Eastern</span>
      </div>
      {noGl ? (
        <p className="border border-rule bg-panel p-4 text-sm">
          This browser cannot draw 3D (WebGL is not available), so the network is not shown. The table of balancing authorities below, and{" "}
          <Link href="/grid">grid conditions</Link>, hold the same numbers.
        </p>
      ) : (
        <div ref={box} className="w-full cursor-grab border border-rule" style={{ height: 520 }} aria-label="A 3D network of the US balancing authorities and their interchange; drag to rotate, scroll to zoom" role="img" />
      )}
      <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-muted">
        <span>Drag to rotate, scroll to zoom; it turns slowly until touched.</span>
        <span className="flex items-center gap-1">Carbon intensity of generation:
          <span className="inline-block h-2 w-24" style={{ background: "linear-gradient(90deg, #175E54, #8C1515)" }} /> {fmt(lo)} to {fmt(hi)} kg CO2/MWh; grey: not held</span>
        <span>Sphere: demand (the seven ISOs) or interchange volume (the others)</span>
      </div>
      {pick ? (
        <div className="mt-3 border border-rule bg-panel p-3 text-sm">
          <div className="mb-1 font-semibold">{pick.name} <span className="font-mono text-xs text-muted">{pick.id}</span>{pick.iso ? <> &middot; <Link href={`/grid/${GRID_SLUG[pick.iso]}`}>{pick.iso}&apos;s grid page</Link></> : null}</div>
          <div>
            {/* the ISO BAs' figures carry check keys: check-values reads them from Supabase (eia930_all_demand, carbon_intensity_hourly) */}
            {pick.demand_mw !== null ? <>Demand <Num check={`series|eia930_all_demand|eia930:${pick.id}|demand_mw|${pick.demand_ts}`} raw={pick.demand_mw}>{shown(pick.demand_mw)}</Num> MW at {pick.demand_ts?.slice(0, 13).replace("T", " ")}:00 UTC. </> : <>Demand: not held in the warehouse (sized by interchange). </>}
            {pick.intensity !== null ? <>Carbon intensity <Num check={`series|carbon_intensity_hourly|eia930:${pick.id}|intensity_generation|${pick.intensity_ts}`} raw={pick.intensity}>{shown(pick.intensity)}</Num> kg CO2/MWh. </> : null}
            Interchange over the week: {fmt(pick.volume_mwh)} MWh.
          </div>
          <div className="mt-1">Largest flows this hour: {flows.length ? flows.map((f, i) => <span key={f.other}>{i ? "; " : ""}{f.mw > 0 ? "to" : "from"} {nameOf(f.other)} {fmt(Math.abs(f.mw))} MW</span>) : "none reported"}.</div>
        </div>
      ) : null}
      <label className="mt-3 block text-sm">Show a balancing authority:{" "}
        <select className="border border-rule bg-panel px-2 py-1 text-sm" value={pick?.id ?? ""} onChange={(e) => setPick(snap.nodes.find((n) => n.id === e.target.value) ?? null)}>
          {[...snap.nodes].sort((a, b) => a.name.localeCompare(b.name)).map((n) => <option key={n.id} value={n.id}>{n.name} ({n.id})</option>)}
        </select>
      </label>
    </div>
  );
}
