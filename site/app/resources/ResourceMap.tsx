"use client";

// Session 146: the map of "Where the resources are" (/resources, in review). One canvas; one renderer a kind of layer
// (a grid, shapes, points), each driven by the layer's entry in the manifest, so a layer that arrives later needs no
// code here. A layer's file is asked for only when its toggle is switched on, a grid's finer levels only when the zoom
// calls for them, and a part of a grid kept in files of its own (Alaska, Hawaii) only when the map shows that part.
// The overlays (plants, the queue by county, datacenters) are read the same way, on their toggle. The map is drawn on
// a plane where a grid cell is a rectangle (lib/resources.ts), so a grid is drawn cell for cell with no smoothing, and
// the hover reads the stored value of the cell under the pointer. Nothing leaves the site.
import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { feature, mesh } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import statesTopo from "us-atlas/states-10m.json";
import { COLOR } from "@/lib/map2";
import * as R from "@/lib/resources";

type GridImg = { grid: R.Grid; canvas: HTMLCanvasElement; cell: number; decimals: number };
type Feat = { path: Path2D; box: [number, number, number, number]; geometry: R.Geometry; props: Record<string, unknown>; fill: string; stroke: string; line: boolean };
type Dot = { lon: number; lat: number; props: Record<string, unknown> };
/** A still picture of a heavy layer: `image` is what is drawn (the canvas it was painted on, then the browser's own
 *  bitmap of it once that is made, which it keeps ready to draw). */
type Still = { image: CanvasImageSource; width: number; height: number; west: number; north: number; perDeg: number };
type ShapeSet = { feats: Feat[]; dots: Dot[]; kinds: { kind: string; fill: string; stroke: string }[]; fill: string; stroke: string; vertices: number; still: Still | null };
type PointSet = { columns: string[]; rows: unknown[][]; iName: number; iValue: number; bins: number[][]; colors: string[]; stroke: string; sideDeg: number; still: Still | null; box: [number, number, number, number] };
type Plants = {
  vintage: string; techs: { slug: string; name: string }[]; statuses: { slug: string; name: string }[]; states: string[]; names: string[];
  n: number[]; s: number[]; t: number[]; st: number[]; mw: number[]; y: number[]; lo: (number | null)[]; la: (number | null)[];
};
type Queue = { rows: number; drawn: number; counties: number; not_placed: number; no_shape: number; vintage_first: string; vintage_last: string; shapes: { features: { properties: Record<string, unknown>; geometry: R.Geometry }[] }; points: { lon: number; lat: number; id: string; mw: number | null; status: string; tech: string; state: string }[] };
type Centers = { rows: number; drawn: number; not_placed: number; vintage: string; points: { lon: number; lat: number; id: string; operator: string; site: string; mw: number | null; status: string; state: string; city: string; county: string; prec: string; src: string }[] };
type HoverRow = { id: string; title: string; text: string; sub: string; value: number | null; feature?: string; empty?: boolean };
type Hover = { x: number; y: number; w: number; h: number; lon: number; lat: number; rows: HoverRow[] };
/** The longest of each kind of work so far, in ms: what the frame-time script reads to say where a slow frame came from. */
type Slow = { moving: number; rest: number; decode: number };
type Chosen = { on: string[]; fuel: string[] | null };

const NO_VALUE = "no value in the source here";
const ASPECT = (R.HOME.spanLon * R.KX) / R.HOME.spanLat;
const BINS = 12;              // steps of color for points drawn by value
const HEAVY_VERTICES = 30000; // a set of shapes with more corners than this is drawn from a still picture while the map moves
const HEAVY_POINTS = 6000;    // and so is a set of points with more rows than this
const X = (lon: number) => lon * R.KX, Y = (lat: number) => -lat;
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const one = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
/** Point size in pixels: area grows with MW, clamped for legibility (the project map's rule). */
const sizeOf = (mw: number) => Math.min(18, Math.max(3, 2 + Math.sqrt(Math.max(mw, 0)) * 0.2));
const cssVar = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim() || "#888888";
const never = () => () => {};

function trace(p: Path2D, g: R.Geometry | null | undefined): number {
  if (!g) return 0;
  let n = 0;
  const ring = (r: number[][], close: boolean) => {
    r.forEach((c, i) => { if (i) p.lineTo(X(c[0]), Y(c[1])); else p.moveTo(X(c[0]), Y(c[1])); });
    if (close) p.closePath();
    n += r.length;
  };
  if (g.type === "Polygon") (g.coordinates as number[][][]).forEach((r) => ring(r, true));
  else if (g.type === "MultiPolygon") (g.coordinates as number[][][][]).forEach((poly) => poly.forEach((r) => ring(r, true)));
  else if (g.type === "LineString") ring(g.coordinates as number[][], false);
  else if (g.type === "MultiLineString") (g.coordinates as number[][][]).forEach((r) => ring(r, false));
  else if (g.type === "GeometryCollection") (g.geometries ?? []).forEach((x) => { n += trace(p, x); });
  return n;
}
const isLine = (g: R.Geometry | null | undefined) => !!g && (g.type === "LineString" || g.type === "MultiLineString");
function pointsOf(g: R.Geometry | null | undefined): number[][] {
  if (!g) return [];
  if (g.type === "Point") return [g.coordinates as number[]];
  if (g.type === "MultiPoint") return g.coordinates as number[][];
  return [];
}
/** Whether a place is within `tol` (in the plane's units) of a line. */
function nearLine(g: R.Geometry, lon: number, lat: number, tol: number): boolean {
  const px = X(lon), py = Y(lat);
  const lines = g.type === "LineString" ? [g.coordinates as number[][]] : g.type === "MultiLineString" ? (g.coordinates as number[][][]) : [];
  for (const l of lines) for (let i = 1; i < l.length; i++) {
    const ax = X(l[i - 1][0]), ay = Y(l[i - 1][1]), bx = X(l[i][0]), by = Y(l[i][1]);
    const dx = bx - ax, dy = by - ay, len = dx * dx + dy * dy;
    const t = len ? Math.min(1, Math.max(0, ((px - ax) * dx + (py - ay) * dy) / len)) : 0;
    if (Math.hypot(px - ax - t * dx, py - ay - t * dy) <= tol) return true;
  }
  return false;
}

/** A grid as a picture, one pixel a cell, colored along the layer's ramp; an empty cell is clear. */
function gridImage(grid: R.Grid, layer: R.Layer, ramp: R.Rgb[]): GridImg {
  let legend = R.legendOf(layer);
  if (!legend) {   // the manifest gives no range: the file's own lowest and highest stored values
    let lo = 65536, hi = -1;
    for (let i = 0; i < grid.data.length; i++) { const s = grid.data[i]; if (s !== grid.nodata) { if (s < lo) lo = s; if (s > hi) hi = s; } }
    legend = { min: lo * grid.scale + grid.offset, max: hi * grid.scale + grid.offset };
  }
  const classes = layer.classes ?? null, tones = classes ? R.classTones(classes) : [], knots = R.knotsOf(legend);
  const lut = new Uint32Array(65536);
  for (let s = 0; s < 65536; s++) {
    const v = s * grid.scale + grid.offset;
    const ci = classes ? classes.findIndex((c) => Math.abs(c.value - v) < 1e-9) : -1;
    if (classes && ci < 0) continue;
    const tone = classes ? tones[ci] : R.positionOn(knots, v);
    const c = tone === null ? ([184, 178, 167] as R.Rgb) : R.along(ramp, tone);
    lut[s] = ((235 << 24) | (c[2] << 16) | (c[1] << 8) | c[0]) >>> 0;
  }
  lut[grid.nodata] = 0;
  const canvas = document.createElement("canvas");
  canvas.width = grid.ncols; canvas.height = grid.nrows;
  const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;
  const img = ctx.createImageData(grid.ncols, grid.nrows);
  const px = new Uint32Array(img.data.buffer);
  for (let i = 0; i < px.length; i++) px[i] = lut[grid.data[i]];
  ctx.putImageData(img, 0, 0);
  return { grid, canvas, cell: grid.dlon, decimals: R.decimalsOf(grid.scale) };
}

/** A still picture of a heavy layer over its own box, drawn once: what the map shows of it while it moves. */
function stillOf(box: [number, number, number, number], paint: (ctx: CanvasRenderingContext2D, k: number) => void): Still | null {
  const spanX = (box[2] - box[0]) * R.KX, spanY = box[3] - box[1];
  if (!(spanX > 0) || !(spanY > 0)) return null;
  const perDeg = Math.min(40, 2000 / spanX, 1250 / spanY);
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.ceil(spanX * perDeg)); canvas.height = Math.max(1, Math.ceil(spanY * perDeg));
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;
  ctx.setTransform(perDeg, 0, 0, perDeg, -X(box[0]) * perDeg, -Y(box[3]) * perDeg);
  paint(ctx, perDeg);
  const still: Still = { image: canvas, width: canvas.width, height: canvas.height, west: box[0], north: box[3], perDeg };
  if (typeof createImageBitmap === "function") createImageBitmap(canvas).then((bitmap) => { still.image = bitmap; }).catch(() => { /* the canvas stays the picture */ });
  return still;
}
function paintShapes(ctx: CanvasRenderingContext2D, k: number, set: ShapeSet, view?: [number, number, number, number]): number {
  let n = 0;
  for (const f of set.feats) {
    if (view && (f.box[2] < view[0] || f.box[0] > view[2] || f.box[3] < view[1] || f.box[1] > view[3])) continue;
    n += 1;
    if (!f.line) { ctx.fillStyle = f.fill; ctx.fill(f.path, "evenodd"); }
    ctx.strokeStyle = f.stroke; ctx.lineWidth = (f.line ? 1.6 : 0.8) / k; ctx.stroke(f.path);
  }
  return n;
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: "same-origin" });
  if (!res.ok) throw new Error(`the server answered ${res.status}`);
  if (!(res.headers.get("content-type") ?? "").includes("json")) throw new Error("this layer is in review");
  return (await res.json()) as T;
}

export function ResourceMap({ layers, groups, manifestReason }: { layers: R.Layer[]; groups: R.ToggleGroup[]; manifestReason: string | null }) {
  // What is switched on: what the address says, until the reader changes it. The server draws the bare address.
  const search = useSyncExternalStore(never, () => window.location.search, () => "");
  const fromAddress = useMemo(() => R.parseShown(search, layers), [search, layers]);
  const [chosen, setChosen] = useState<Chosen | null>(null);
  const on = chosen ? chosen.on : fromAddress.on, fuel = chosen ? chosen.fuel : fromAddress.fuel;
  const [status, setStatus] = useState<Record<string, string>>({});
  const [levels, setLevels] = useState<Record<string, number>>({});
  const [kinds, setKinds] = useState<Record<string, { kind: string; fill: string; stroke: string }[]>>({});
  const [plants, setPlants] = useState<Plants | null>(null);
  const [queue, setQueue] = useState<Queue | null>(null);
  const [centers, setCenters] = useState<Centers | null>(null);
  const [hover, setHover] = useState<Hover | null>(null);

  const box = useRef<HTMLDivElement>(null), canvas = useRef<HTMLCanvasElement>(null);
  const view = useRef<R.View>({ z: 1, lon: R.HOME.lon, lat: R.HOME.lat });
  const size = useRef({ w: 900, h: 520, dpr: 1 });
  const store = useRef({
    grids: new Map<string, GridImg>(), shapes: new Map<string, ShapeSet>(), points: new Map<string, PointSet>(), asked: new Set<string>(),
    plants: null as Plants | null, plantIdx: null as Record<string, number[][]> | null, queue: null as (Queue & { set: ShapeSet }) | null, centers: null as Centers | null,
    drawnGrid: {} as Record<string, GridImg | undefined>, drawn: {} as Record<string, number>, frames: 0, slow: { moving: 0, rest: 0, decode: 0 } as Slow,
  });
  const live = useRef({ on, fuel, touched: false, ready: false, dragging: false, moving: false });
  const pal = useRef<{ ink: R.Rgb; land: string; sea: string; panel: string; ramp: Record<string, R.Rgb[]>; fuel: Record<string, string> } | null>(null);
  const base = useRef<{ nation: Path2D; states: Path2D } | null>(null);
  const settleRef = useRef<() => void>(() => {}), readRef = useRef<((x: number, y: number) => Hover) | null>(null);
  // the reader of grid files, off this thread (grid.worker.ts); null where the browser gives none, and the page reads them itself
  const reader = useRef<{ worker: Worker; next: number; waiting: Map<number, { file: string; ok: (g: R.Grid) => void; no: (e: Error) => void }> } | null>(null);
  const raf = useRef(0), settleTimer = useRef<ReturnType<typeof setTimeout> | null>(null), hoverRaf = useRef(0), lastPointer = useRef<{ x: number; y: number } | null>(null);

  const byId = useMemo(() => new Map(layers.map((l) => [l.id, l])), [layers]);
  const pyramids = useMemo(() => new Map(layers.filter((l) => l.kind === "grid").map((l) => [l.id, R.pyramidsOf(l)])), [layers]);
  const groupIndex = useMemo(() => new Map(layers.map((l) => [l.id, layers.filter((x) => R.groupId(x.group) === R.groupId(l.group)).findIndex((x) => x.id === l.id)])), [layers]);
  const mark = useCallback((key: string, value: string) => setStatus((s) => (s[key] === value ? s : { ...s, [key]: value })), []);

  // -------------------------------------------------------------------------------------------------------------------
  // Drawing. Everything is drawn again on each frame the view changes: grids as stored pictures, cell for cell; shapes
  // and state lines as paths; points as marks. While the map moves, a heavy set of shapes or points is drawn from a
  // still picture of itself, and as it is when the map comes to rest.
  const draw = useCallback(() => {
    raf.current = 0;
    const cv = canvas.current, p = pal.current, b = base.current;
    if (!cv || !p || !b) return;
    const ctx = cv.getContext("2d");
    if (!ctx) return;
    const { w, h, dpr } = size.current, v = view.current, S = store.current, shown = live.current.on, moving = live.current.moving;
    const k = R.fitK(w, h) * v.z, began = performance.now();
    const screen = () => ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const world = () => ctx.setTransform(dpr * k, 0, 0, dpr * k, dpr * (w / 2 - X(v.lon) * k), dpr * (h / 2 - Y(v.lat) * k));
    const [west, north] = R.toPlace(v, w, h, 0, 0), [east, south] = R.toPlace(v, w, h, w, h);
    const place = (lon: number, lat: number): [number, number] => [(lon - v.lon) * R.KX * k + w / 2, (v.lat - lat) * k + h / 2];
    // a still picture is drawn as a grid is: only the part of it the map shows, so that far zoomed in the browser is
    // not asked to stretch the whole picture over a surface many screens wide (the first such frame took half a second)
    const stillDraw = (s: Still) => {
      const sx0 = Math.max(0, (west - s.west) * R.KX * s.perDeg), sx1 = Math.min(s.width, (east - s.west) * R.KX * s.perDeg);
      const sy0 = Math.max(0, (s.north - north) * s.perDeg), sy1 = Math.min(s.height, (s.north - south) * s.perDeg);
      if (sx1 <= sx0 || sy1 <= sy0) return;
      const [x0, y0] = place(s.west + sx0 / (R.KX * s.perDeg), s.north - sy0 / s.perDeg);
      ctx.imageSmoothingEnabled = true;
      ctx.drawImage(s.image, sx0, sy0, sx1 - sx0, sy1 - sy0, x0, y0, ((sx1 - sx0) / s.perDeg) * k, ((sy1 - sy0) / s.perDeg) * k);
    };
    const drawn: Record<string, number> = {};
    screen();
    ctx.fillStyle = p.sea; ctx.fillRect(0, 0, w, h);
    world();
    ctx.fillStyle = p.land; ctx.fill(b.nation, "evenodd");

    // grids: for each pyramid of a layer, the level the zoom calls for when it is loaded, else the nearest that is
    screen();
    for (const id of shown) {
      const l = byId.get(id);
      if (!l || l.kind !== "grid") continue;
      let cells = 0;
      for (const py of pyramids.get(id) ?? []) {
        const want = R.levelFor(py.levels, R.KX * k), wc = want?.cell_deg ?? 1;
        const have = py.levels.filter((x) => S.grids.has(x.file)).sort((a, c) => Math.abs(Math.log(a.cell_deg / wc)) - Math.abs(Math.log(c.cell_deg / wc)));
        const img = have.length ? S.grids.get(have[0].file) : undefined;
        S.drawnGrid[py.key] = img;
        if (!img) continue;
        const g = img.grid;
        const c0 = Math.max(0, Math.floor((west - g.lon0) / g.dlon)), c1 = Math.min(g.ncols, Math.ceil((east - g.lon0) / g.dlon));
        const r0 = Math.max(0, Math.floor((g.lat0 - north) / g.dlat)), r1 = Math.min(g.nrows, Math.ceil((g.lat0 - south) / g.dlat));
        if (c1 <= c0 || r1 <= r0) continue;
        const [x0, y0] = place(g.lon0 + c0 * g.dlon, g.lat0 - r0 * g.dlat);
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img.canvas, c0, r0, c1 - c0, r1 - r0, x0, y0, (c1 - c0) * g.dlon * R.KX * k, (r1 - r0) * g.dlat * k);
        cells += (c1 - c0) * (r1 - r0);
      }
      drawn[id] = cells;
    }

    // shapes: the manifest's, then the queue's counties
    const shapeSets: [string, ShapeSet][] = [];
    for (const id of shown) { const s = S.shapes.get(id); if (s) shapeSets.push([id, s]); }
    if (shown.includes("queue") && S.queue) shapeSets.push(["queue", S.queue.set]);
    for (const [id, set] of shapeSets) {
      if (moving && set.still) { screen(); stillDraw(set.still); drawn[id] = set.feats.length + set.dots.length; continue; }
      world();
      drawn[id] = paintShapes(ctx, k, set, [west, south, east, north]) + set.dots.length;
    }
    // points drawn by value: a square the size of the source's own spacing where the manifest gives it
    for (const id of shown) {
      const set = S.points.get(id);
      if (!set) continue;
      if (moving && set.still) { screen(); stillDraw(set.still); drawn[id] = set.rows.length; continue; }
      screen();
      const side = Math.max(set.sideDeg > 0 ? 2.5 : 7, set.sideDeg * k), half = side / 2, round = set.sideDeg === 0;
      let n = 0;
      for (let bi = 0; bi < set.bins.length; bi++) {
        if (!set.bins[bi].length) continue;
        ctx.beginPath();
        for (const i of set.bins[bi]) {
          const r = set.rows[i], lon = r[0] as number, lat = r[1] as number;
          if (lon < west - 0.2 || lon > east + 0.2 || lat < south - 0.2 || lat > north + 0.2) continue;
          const [x, y] = place(lon, lat);
          if (round) { ctx.moveTo(x + half, y); ctx.arc(x, y, half, 0, 6.2832); } else ctx.rect(x - half * R.KX, y - half, side * R.KX, side);
          n += 1;
        }
        ctx.fillStyle = set.colors[bi]; ctx.fill();
        if (round) { ctx.strokeStyle = set.stroke; ctx.lineWidth = 0.8; ctx.stroke(); }
      }
      drawn[id] = n;
    }
    // the states, over the layers, so a place can be read
    world();
    ctx.strokeStyle = R.css(p.ink, 0.38); ctx.lineWidth = 0.7 / k; ctx.stroke(b.states);
    ctx.strokeStyle = R.css(p.ink, 0.55); ctx.lineWidth = 0.8 / k; ctx.stroke(b.nation);

    screen();
    for (const [, set] of shapeSets) {
      if (!set.dots.length) continue;
      ctx.fillStyle = set.fill; ctx.strokeStyle = set.stroke; ctx.lineWidth = 1;
      ctx.beginPath();
      for (const d of set.dots) { const [x, y] = place(d.lon, d.lat); if (x < -6 || y < -6 || x > w + 6 || y > h + 6) continue; ctx.moveTo(x + 3.5, y); ctx.arc(x, y, 3.5, 0, 6.2832); }
      ctx.fill(); ctx.stroke();
    }

    // plants: a dot for an operating unit, a ring for one planned or under construction; the color is the fuel
    const P = S.plants;
    if (P && S.plantIdx && (shown.includes("plants_operating") || shown.includes("plants_planned"))) {
      const fuels = live.current.fuel;
      for (const which of ["plants_operating", "plants_planned"] as const) {
        if (!shown.includes(which)) continue;
        let n = 0;
        for (let t = 0; t < P.techs.length; t++) {
          if (fuels && !fuels.includes(P.techs[t].slug)) continue;
          const color = p.fuel[P.techs[t].slug] ?? p.fuel.other;
          ctx.beginPath();
          for (const i of S.plantIdx[which][t]) {
            const lon = P.lo[i], lat = P.la[i];
            if (lon === null || lat === null || lon < west || lon > east || lat < south || lat > north) continue;
            const [x, y] = place(lon, lat), r = sizeOf(P.mw[i]) / 2;
            if (r < 2.2 && which === "plants_operating") ctx.rect(x - r, y - r, 2 * r, 2 * r); else { ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, 6.2832); }
            n += 1;
          }
          if (which === "plants_operating") { ctx.globalAlpha = 0.78; ctx.fillStyle = color; ctx.fill(); ctx.globalAlpha = 1; }
          else { ctx.strokeStyle = color; ctx.lineWidth = 1.4; ctx.stroke(); }
        }
        drawn[which] = n;
      }
    }
    // the queue's rows with coordinates of their own, and the datacenters: a diamond
    if (shown.includes("queue") && S.queue?.points.length) {
      ctx.strokeStyle = R.css(p.ink); ctx.lineWidth = 1.2;
      ctx.beginPath();
      for (const d of S.queue.points) { const [x, y] = place(d.lon, d.lat); ctx.moveTo(x + 3, y); ctx.arc(x, y, 3, 0, 6.2832); }
      ctx.stroke();
    }
    if (shown.includes("datacenters") && S.centers) {
      let n = 0;
      ctx.fillStyle = p.panel; ctx.strokeStyle = R.css(p.ink); ctx.lineWidth = 1.3;
      ctx.beginPath();
      for (const d of S.centers.points) {
        const [x, y] = place(d.lon, d.lat);
        if (x < -8 || y < -8 || x > w + 8 || y > h + 8) continue;
        n += 1;
        ctx.moveTo(x, y - 5); ctx.lineTo(x + 5, y); ctx.lineTo(x, y + 5); ctx.lineTo(x - 5, y); ctx.closePath();
      }
      ctx.fill(); ctx.stroke();
      drawn.datacenters = n;
    }
    S.drawn = drawn;
    S.frames += 1;
    const took = performance.now() - began;
    if (moving) S.slow.moving = Math.max(S.slow.moving, took); else S.slow.rest = Math.max(S.slow.rest, took);
  }, [byId, pyramids]);
  const redraw = useCallback(() => { if (!raf.current) raf.current = requestAnimationFrame(draw); }, [draw]);

  // -------------------------------------------------------------------------------------------------------------------
  // Loading: a file is asked for once, when a toggle or the zoom or the place first needs it.
  const load = useCallback((ids: string[]) => {
    const S = store.current, p = pal.current;
    if (!p) return;
    const { w, h } = size.current, v = view.current, k = R.fitK(w, h) * v.z;
    const [west, north] = R.toPlace(v, w, h, 0, 0), [east, south] = R.toPlace(v, w, h, w, h);
    const done = (id: string) => { mark(id, "ready"); redraw(); settleRef.current(); };
    const readGrid = (file: string): Promise<R.Grid> => {
      const rd = reader.current;
      if (!rd) return getJson<R.GridFile>(R.layerHref(file)).then((f) => R.decodeGrid(f));
      return new Promise((ok, no) => { rd.next += 1; rd.waiting.set(rd.next, { file, ok, no }); rd.worker.postMessage({ id: rd.next, url: new URL(R.layerHref(file), window.location.origin).href }); });
    };
    const timed = <T,>(work: () => T): T => { const t = performance.now(); const out = work(); S.slow.decode = Math.max(S.slow.decode, performance.now() - t); return out; };
    // a still picture is drawn once, one pixel of it, when it is made: the browser readies it then, not in the first frame of a drag
    const warm = (s: Still | null) => { const ctx = canvas.current?.getContext("2d"); if (s && ctx) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.01; ctx.drawImage(s.image, 0, 0, s.width, s.height, 0, 0, 1, 1); ctx.restore(); } };
    for (const id of ids) {
      const l = byId.get(id);
      if (l && l.kind === "grid") {
        const ramp = p.ramp[R.groupId(l.group)] ?? p.ramp.other;
        for (const py of pyramids.get(id) ?? []) {
          if (py.box && (py.box[2] < west || py.box[0] > east || py.box[3] < south || py.box[1] > north)) continue;   // a part the map does not show
          const want = R.levelFor(py.levels, R.KX * k), main = py.key === id;
          if (!want || S.asked.has(want.file)) continue;
          S.asked.add(want.file);
          const none = () => !py.levels.some((x) => S.grids.has(x.file));
          if (main && none()) mark(id, "loading");
          readGrid(want.file).then((grid) => { S.grids.set(want.file, timed(() => gridImage(grid, l, ramp))); if (main) done(id); else { redraw(); settleRef.current(); } })
            .catch((e: Error) => { S.asked.delete(want.file); if (main && none()) mark(id, `not read: ${e.message}`); });
        }
      } else if (l) {
        const file = R.filesOf(l)[0];
        if (!file || S.asked.has(file)) continue;
        S.asked.add(file);
        mark(id, "loading");
        const ramp = p.ramp[R.groupId(l.group)] ?? p.ramp.other, li = groupIndex.get(id) ?? 0, lg = R.legendOf(l), knots = lg ? R.knotsOf(lg) : [];
        getJson<unknown>(R.layerHref(file)).then((body) => timed(() => {
          if (l.kind === "points") {
            const f = body as { columns?: string[]; rows?: unknown[][] };
            const columns = f.columns ?? [], find = (re: RegExp, d: number) => { const i = columns.findIndex((c) => re.test(c)); return i < 0 ? d : i; };
            const rows = (f.rows ?? []).filter((r) => Number.isFinite(r[0] as number) && Number.isFinite(r[1] as number));
            const iValue = find(/^value$/i, 3);
            const bins: number[][] = Array.from({ length: lg ? BINS : 1 }, () => []);
            let bw = Infinity, bs = Infinity, be = -Infinity, bn = -Infinity;
            rows.forEach((r, i) => {
              const val = r[iValue], lon = r[0] as number, lat = r[1] as number;
              bins[lg && typeof val === "number" ? Math.min(BINS - 1, Math.floor(R.positionOn(knots, val) * BINS)) : 0].push(i);
              bw = Math.min(bw, lon); be = Math.max(be, lon); bs = Math.min(bs, lat); bn = Math.max(bn, lat);
            });
            const sideDeg = typeof l.point_spacing_km === "number" && l.point_spacing_km > 0 ? l.point_spacing_km / 111.2 : 0;
            const set: PointSet = {
              columns, rows, iName: find(/^name$/i, 2), iValue, bins, sideDeg, still: null, box: [bw - sideDeg, bs - sideDeg, be + sideDeg, bn + sideDeg],
              colors: bins.map((_, bi) => (lg ? R.css(R.along(ramp, (bi + 0.5) / BINS), 0.92) : R.css(R.along(ramp, 0.55), 0.85))), stroke: R.css(R.along(ramp, 0.95)),
            };
            if (rows.length > HEAVY_POINTS && sideDeg > 0) {
              set.still = stillOf(set.box, (ctx) => {
                for (let bi = 0; bi < bins.length; bi++) {
                  ctx.beginPath();
                  for (const i of bins[bi]) { const r = rows[i]; ctx.rect(X(r[0] as number) - (sideDeg * R.KX) / 2, Y(r[1] as number) - sideDeg / 2, sideDeg * R.KX, sideDeg); }
                  ctx.fillStyle = set.colors[bi]; ctx.fill();
                }
              });
              warm(set.still);
            }
            S.points.set(id, set);
          } else {
            const fc = body as { features?: { geometry: R.Geometry; properties?: Record<string, unknown> }[] };
            const seen: string[] = [];
            for (const f of fc.features ?? []) { const kd = String(f.properties?.kind ?? ""); if (!seen.includes(kd)) seen.push(kd); }
            const shade = [0.5, 0.95, 0.25, 0.75];
            const classes = l.classes ?? null, tones = classes ? R.classTones(classes) : [];
            const kindColors = seen.map((kd, j) => { const t = shade[(li * 2 + (seen.length > 4 ? 0 : j)) % shade.length]; return { kind: kd, fill: R.css(R.along(ramp, t), 0.5), stroke: R.css(R.along(ramp, Math.min(1, t + 0.3))) }; });
            const set: ShapeSet = { feats: [], dots: [], kinds: lg || classes ? [] : kindColors, fill: R.css(R.along(ramp, 0.55), 0.85), stroke: R.css(R.along(ramp, 0.95)), vertices: 0, still: null };
            let bw = Infinity, bs = Infinity, be = -Infinity, bn = -Infinity;
            for (const f of fc.features ?? []) {
              const props = f.properties ?? {};
              for (const c of pointsOf(f.geometry)) set.dots.push({ lon: c[0], lat: c[1], props });
              const bx = R.boxOf(f.geometry);
              if (!bx || pointsOf(f.geometry).length) continue;
              const path = new Path2D();
              set.vertices += trace(path, f.geometry);
              const kc = kindColors[seen.indexOf(String(props.kind ?? ""))];
              const val = typeof props.value === "number" ? props.value : null;
              const ci = classes && val !== null ? classes.findIndex((c) => c.value === val) : -1;
              const tone = ci >= 0 ? tones[ci] : lg && val !== null ? R.positionOn(knots, val) : undefined;
              const fill = tone === undefined ? kc.fill : tone === null ? "rgba(184,178,167,0.6)" : R.css(R.along(ramp, tone), 0.82);
              const stroke = tone === undefined ? kc.stroke : lg && !classes ? R.css(p.ink, 0.22) : fill;
              set.feats.push({ path, box: bx, geometry: f.geometry, props, line: isLine(f.geometry), fill, stroke });
              bw = Math.min(bw, bx[0]); bs = Math.min(bs, bx[1]); be = Math.max(be, bx[2]); bn = Math.max(bn, bx[3]);
            }
            if (set.vertices > HEAVY_VERTICES) { set.still = stillOf([bw, bs, be, bn], (ctx, kk) => { paintShapes(ctx, kk, set); }); warm(set.still); }
            S.shapes.set(id, set);
            setKinds((s) => ({ ...s, [id]: set.kinds }));
          }
          done(id);
        })).catch((e: Error) => { S.asked.delete(file); mark(id, `not read: ${e.message}`); });
      } else if (id === "plants_operating" || id === "plants_planned") {
        if (S.asked.has("plants")) continue;
        S.asked.add("plants"); mark("plants", "loading");
        getJson<Plants & { ok: boolean; reason?: string }>("/resources/overlay/plants").then((d) => {
          if (!d.ok) throw new Error(d.reason ?? "no rows");
          const op: number[][] = d.techs.map(() => []), pl: number[][] = d.techs.map(() => []);
          for (let i = 0; i < d.mw.length; i++) (d.st[i] === 0 ? op : pl)[d.t[i]].push(i);
          S.plants = d; S.plantIdx = { plants_operating: op, plants_planned: pl }; setPlants(d); done("plants");
        }).catch((e: Error) => { S.asked.delete("plants"); mark("plants", `not read: ${e.message}`); });
      } else if (id === "queue") {
        if (S.asked.has("queue")) continue;
        S.asked.add("queue"); mark("queue", "loading");
        getJson<Queue & { ok: boolean; reason?: string }>("/resources/overlay/queue").then((d) => {
          if (!d.ok) throw new Error(d.reason ?? "no rows");
          const max = d.shapes.features.reduce((m, f) => Math.max(m, Number(f.properties.mw) || 0), 0);
          const set: ShapeSet = { feats: [], dots: [], kinds: [], fill: R.css(p.ink, 0.5), stroke: R.css(p.ink, 0.5), vertices: 0, still: null };
          for (const f of d.shapes.features) {
            const bx = R.boxOf(f.geometry);
            if (!bx) continue;
            const path = new Path2D();
            set.vertices += trace(path, f.geometry);
            const share = max > 0 ? Math.sqrt((Number(f.properties.mw) || 0) / max) : 0;
            set.feats.push({ path, box: bx, geometry: f.geometry, props: f.properties, line: false, fill: R.css(p.ink, 0.1 + 0.55 * share), stroke: R.css(p.ink, 0.45) });
          }
          if (set.vertices > HEAVY_VERTICES && set.feats.length) {
            const bb = set.feats.reduce((a, f) => [Math.min(a[0], f.box[0]), Math.min(a[1], f.box[1]), Math.max(a[2], f.box[2]), Math.max(a[3], f.box[3])] as [number, number, number, number], [Infinity, Infinity, -Infinity, -Infinity] as [number, number, number, number]);
            set.still = stillOf(bb, (ctx, kk) => { paintShapes(ctx, kk, set); });
            warm(set.still);
          }
          S.queue = { ...d, set }; setQueue(d); done("queue");
        }).catch((e: Error) => { S.asked.delete("queue"); mark("queue", `not read: ${e.message}`); });
      } else if (id === "datacenters") {
        if (S.asked.has("datacenters")) continue;
        S.asked.add("datacenters"); mark("datacenters", "loading");
        getJson<Centers & { ok: boolean; reason?: string }>("/resources/overlay/datacenters").then((d) => { if (!d.ok) throw new Error(d.reason ?? "no rows"); S.centers = d; setCenters(d); done("datacenters"); })
          .catch((e: Error) => { S.asked.delete("datacenters"); mark("datacenters", `not read: ${e.message}`); });
      }
    }
  }, [byId, pyramids, groupIndex, mark, redraw]);

  // When the view comes to rest: the map as it is (no still pictures), the address, the box's own record of the view
  // (the check reads it), the levels drawn, any finer level the zoom now calls for, and the hover again.
  const settle = useCallback(() => {
    if (settleTimer.current) clearTimeout(settleTimer.current);
    settleTimer.current = setTimeout(() => {
      const L = live.current, v = view.current, S = store.current, el = box.current;
      if (L.moving) { L.moving = false; draw(); }
      load(L.on);
      const lv: Record<string, number> = {};
      for (const id of L.on) for (const py of pyramids.get(id) ?? []) { const g = S.drawnGrid[py.key]; if (g) lv[py.key] = g.cell; }
      setLevels((s) => (JSON.stringify(s) === JSON.stringify(lv) ? s : lv));
      if (el) {
        el.dataset.z = String(v.z); el.dataset.lon = String(v.lon); el.dataset.lat = String(v.lat);
        el.dataset.w = String(size.current.w); el.dataset.h = String(size.current.h); el.dataset.levels = JSON.stringify(lv);
        el.dataset.drawn = JSON.stringify(S.drawn); el.dataset.frames = String(S.frames); el.dataset.slow = JSON.stringify(S.slow); el.dataset.settled = String(Date.now());
      }
      const lp = lastPointer.current;
      if (lp && !L.dragging && readRef.current) setHover(readRef.current(lp.x, lp.y));
      if (L.ready && L.touched) window.history.replaceState(null, "", `${window.location.pathname}${R.shownQuery({ on: L.on, view: v, fuel: L.fuel })}`);
    }, 160);
  }, [draw, load, pyramids]);

  const moved = useCallback((v: R.View) => {
    view.current = R.clampView(v);
    live.current.touched = true; live.current.moving = true;
    setHover(null);
    redraw(); settle();
  }, [redraw, settle]);

  // -------------------------------------------------------------------------------------------------------------------
  // Start: the tokens, the states, the box's size, the view the address holds.
  useEffect(() => { live.current.on = on; live.current.fuel = fuel; });
  useEffect(() => {
    const ink = R.rgbOf(cssVar("--color-ink"));
    const ramp: Record<string, R.Rgb[]> = { other: R.rampOf(R.rgbOf(cssVar(R.groupColor("other"))), ink) };
    for (const g of R.GROUPS) ramp[g.id] = R.rampOf(R.rgbOf(cssVar(g.color)), ink);
    const fuelColors: Record<string, string> = {};
    for (const [slug, name] of Object.entries(COLOR)) fuelColors[slug] = cssVar(name);
    pal.current = { ink, land: cssVar("--color-paper"), sea: cssVar("--color-surface"), panel: cssVar("--color-panel"), ramp, fuel: fuelColors };
    const topo = statesTopo as unknown as Topology<{ states: GeometryCollection; nation: GeometryCollection }>;
    const nation = new Path2D(), states = new Path2D();
    for (const f of feature(topo, topo.objects.nation).features) trace(nation, f.geometry as R.Geometry);
    trace(states, mesh(topo, topo.objects.states, (a, b) => a !== b) as R.Geometry);
    base.current = { nation, states };

    try {
      const worker = new Worker(new URL("./grid.worker.ts", import.meta.url));
      const waiting = new Map<number, { file: string; ok: (g: R.Grid) => void; no: (e: Error) => void }>();
      worker.onmessage = (e: MessageEvent<{ id: number; ok: boolean; grid?: R.Grid; error?: string }>) => {
        const ask = waiting.get(e.data.id);
        if (!ask) return;
        waiting.delete(e.data.id);
        if (e.data.ok && e.data.grid) ask.ok(e.data.grid); else ask.no(new Error(e.data.error ?? "the file was not read"));
      };
      worker.onerror = () => {   // the reader did not start: this thread reads what was asked of it, and everything after
        reader.current = null;
        for (const ask of waiting.values()) getJson<R.GridFile>(R.layerHref(ask.file)).then((f) => ask.ok(R.decodeGrid(f)), ask.no);
        waiting.clear();
      };
      reader.current = { worker, next: 0, waiting };
    } catch { reader.current = null; }

    const shown = R.parseShown(window.location.search, layers);
    view.current = shown.view;
    live.current.on = shown.on; live.current.fuel = shown.fuel; live.current.ready = true;
    live.current.touched = window.location.search.length > 1;

    const el = box.current, cv = canvas.current;
    if (!el || !cv) return;
    const fit = () => {
      const w = Math.max(280, Math.floor(el.clientWidth)), h = Math.round(Math.min(640, Math.max(300, w / ASPECT))), dpr = Math.min(2, window.devicePixelRatio || 1);
      size.current = { w, h, dpr };
      cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
      cv.style.height = `${h}px`;
      redraw(); settle();
    };
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(el);
    const wheel = (e: WheelEvent) => {
      e.preventDefault();
      const r = cv.getBoundingClientRect();
      moved(R.zoomAbout(view.current, size.current.w, size.current.h, e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * 0.0015)));
    };
    cv.addEventListener("wheel", wheel, { passive: false });
    return () => { ro.disconnect(); cv.removeEventListener("wheel", wheel); reader.current?.worker.terminate(); reader.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { if (live.current.ready) { load(live.current.on); redraw(); settle(); } }, [on, fuel, load, redraw, settle]);

  // -------------------------------------------------------------------------------------------------------------------
  // The hover: for each layer that is on, what is under the pointer.
  const readAt = useCallback((x: number, y: number): Hover => {
    const { w, h } = size.current, v = view.current, S = store.current, shown = live.current.on;
    const [lon, lat] = R.toPlace(v, w, h, x, y), k = R.fitK(w, h) * v.z;
    const rows: HoverRow[] = [];
    const tail = (l: R.Layer) => `Vintage: ${l.vintage ?? "not stated"}. ${l.publisher ?? ""}`.trim();
    const near = (plon: number, plat: number, reach: number) => Math.hypot((plon - lon) * R.KX * k, (plat - lat) * k) <= reach;
    for (const id of shown) {
      const l = byId.get(id);
      if (!l) continue;
      if (l.kind === "grid") {
        // the pyramid whose grid holds this place: the layer's own, or a part kept in files of its own
        const imgs = (pyramids.get(id) ?? []).map((py) => S.drawnGrid[py.key]).filter((g): g is GridImg => !!g);
        if (!imgs.length) continue;
        const img = imgs.find((g) => R.cellOf(g.grid, lon, lat)) ?? imgs[0];
        const val = R.valueAt(img.grid, lon, lat);
        const cls = val !== null && l.classes ? l.classes.find((c) => Math.abs(c.value - val) < 1e-9)?.label : undefined;
        rows.push({ id, title: l.title, value: val, empty: val === null, text: val === null ? NO_VALUE : cls ?? `${R.show(val, img.decimals)} ${l.unit ?? ""}`.trim(), sub: `Cell of ${img.cell} degrees. ${tail(l)}` });
      } else if (l.kind === "shapes") {
        const set = S.shapes.get(id);
        if (!set) continue;
        const hits: Record<string, unknown>[] = [];
        for (const f of set.feats) {
          if (lon < f.box[0] - 0.1 || lon > f.box[2] + 0.1 || lat < f.box[1] - 0.1 || lat > f.box[3] + 0.1) continue;
          if (f.line ? nearLine(f.geometry, lon, lat, 4 / k) : R.inGeometry(f.geometry, lon, lat)) hits.push(f.props);
        }
        for (const d of set.dots) if (near(d.lon, d.lat, 6)) hits.push(d.props);
        for (const props of hits.slice(0, 4)) {
          const val = typeof props.value === "number" ? props.value : null, name = String(props.name ?? "not named in the source");
          const amount = l.classes || props.value === undefined || props.value === null || props.value === "" ? "" : `: ${typeof props.value === "number" ? R.plainNumber(props.value) : props.value} ${props.value_unit ?? l.unit ?? ""}`.trimEnd();
          rows.push({ id, title: l.title, value: val, feature: name, text: `${name}${props.kind && !l.classes ? ` (${props.kind})` : ""}${amount}`, sub: `${l.classes && props.kind ? `${String(props.kind).replace(/^./, (c) => c.toUpperCase())}. ` : ""}${tail(l)}` });
        }
      } else {
        const set = S.points.get(id);
        if (!set) continue;
        const reach = Math.max(6, (set.sideDeg * k) / 2 + 1);
        let best: unknown[] | null = null, bestD = Infinity;
        if (lon >= set.box[0] - 1 && lon <= set.box[2] + 1 && lat >= set.box[1] - 1 && lat <= set.box[3] + 1) {
          for (const r of set.rows) { const d = Math.hypot(((r[0] as number) - lon) * R.KX * k, ((r[1] as number) - lat) * k); if (d <= reach && d < bestD) { best = r; bestD = d; } }
        }
        if (!best) continue;
        const r = best, val = typeof r[set.iValue] === "number" ? (r[set.iValue] as number) : null, name = String(r[set.iName] ?? "not named in the source");
        const rest = set.columns.map((c, i) => (i > 1 && i !== set.iName && i !== set.iValue && r[i] !== null && r[i] !== "" && r[i] !== undefined ? `${c.replace(/_/g, " ")}: ${r[i]}` : "")).filter(Boolean).slice(0, 5);
        rows.push({ id, title: l.title, value: val, feature: name, text: `${name}${val !== null ? `: ${R.plainNumber(val)} ${l.unit ?? ""}`.trimEnd() : ""}`, sub: `${rest.length ? `${rest.join("; ")}. ` : ""}${tail(l)}` });
      }
    }
    if (shown.includes("queue") && S.queue) {
      const q = S.queue;
      for (const f of q.set.feats) {
        if (lon < f.box[0] || lon > f.box[2] || lat < f.box[1] || lat > f.box[3] || !R.inGeometry(f.geometry, lon, lat)) continue;
        const pr = f.props as { name: string; requests: number; mw: number; without_mw: number };
        rows.push({ id: "queue", title: "Interconnection queue", value: pr.mw, feature: pr.name, text: `${pr.name}: ${whole(pr.requests)} ${pr.requests === 1 ? "request" : "requests"}, ${whole(pr.mw)} MW asked for${pr.without_mw ? ` (${pr.without_mw} state no MW)` : ""}`, sub: `A county, not a site. Queue reports held, ${q.vintage_first === q.vintage_last ? q.vintage_last : `${q.vintage_first} to ${q.vintage_last}`}.` });
        break;
      }
      const d = q.points.find((x) => near(x.lon, x.lat, 6));
      if (d) rows.push({ id: "queue", title: "Interconnection queue", value: d.mw, feature: d.id, text: `${d.id}: ${d.mw === null ? "MW not stated" : `${whole(d.mw)} MW asked for`}`, sub: `The request's own coordinates. ${d.status}` });
    }
    const P = S.plants;
    if (P && (shown.includes("plants_operating") || shown.includes("plants_planned"))) {
      const fuels = live.current.fuel;
      let best = -1, bestD = Infinity;
      for (let i = 0; i < P.mw.length; i++) {
        const plon = P.lo[i], plat = P.la[i];
        if (plon === null || plat === null) continue;
        if (!shown.includes(P.st[i] === 0 ? "plants_operating" : "plants_planned") || (fuels && !fuels.includes(P.techs[P.t[i]].slug))) continue;
        const d = Math.hypot((plon - lon) * R.KX * k, (plat - lat) * k);
        if (d <= Math.max(4, sizeOf(P.mw[i]) / 2 + 1.5) && d < bestD) { best = i; bestD = d; }
      }
      if (best >= 0) {
        const i = best;
        rows.push({ id: P.st[i] === 0 ? "plants_operating" : "plants_planned", title: "Plant", value: P.mw[i], feature: P.names[P.n[i]], text: `${P.names[P.n[i]]}: ${P.techs[P.t[i]].name}, ${one(P.mw[i])} MW`, sub: `${P.statuses[P.st[i]].name}, ${P.states[P.s[i]]}${P.y[i] ? `, ${P.y[i]}` : ""}. EIA-860M, ${P.vintage}.` });
      }
    }
    if (shown.includes("datacenters") && S.centers) {
      const d = S.centers.points.find((x) => near(x.lon, x.lat, 7));
      if (d) rows.push({ id: "datacenters", title: "Datacenter", value: d.mw, feature: d.operator || d.site, text: `${d.operator || "Operator not stated"}${d.site ? `, ${d.site}` : ""}: ${d.mw === null ? "MW not stated" : `${whole(d.mw)} MW`}`, sub: `${[d.city, d.county, d.state].filter(Boolean).join(", ")}. ${d.prec === "operator" || d.prec === "point" ? "At the operator's coordinates" : "At a county or city point, not the site"}. Table of ${S.centers.vintage}.` });
    }
    return { x, y, w, h, lon, lat, rows };
  }, [byId, pyramids]);
  useEffect(() => { settleRef.current = settle; readRef.current = readAt; });

  const pointer = useRef<{ id: number; x: number; y: number; lon: number; lat: number } | null>(null);
  const onDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    pointer.current = { id: e.pointerId, x: e.clientX - r.left, y: e.clientY - r.top, lon: view.current.lon, lat: view.current.lat };
    try { e.currentTarget.setPointerCapture(e.pointerId); } catch { /* a synthetic pointer has nothing to capture */ }
  };
  const onMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const r = e.currentTarget.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
    const d = pointer.current;
    if (d && ((e.buttons & 1) === 1 || e.pointerType === "touch")) {
      if (!live.current.dragging && Math.hypot(x - d.x, y - d.y) < 3) return;
      live.current.dragging = true;
      const k = R.fitK(size.current.w, size.current.h) * view.current.z;
      moved({ z: view.current.z, lon: d.lon - (x - d.x) / (R.KX * k), lat: d.lat + (y - d.y) / k });
      return;
    }
    lastPointer.current = { x, y };
    if (!hoverRaf.current) hoverRaf.current = requestAnimationFrame(() => { hoverRaf.current = 0; const p = lastPointer.current; if (p && !live.current.dragging) setHover(readAt(p.x, p.y)); });
  };
  const onUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    if (pointer.current && !live.current.dragging && e.pointerType === "touch") setHover(readAt(e.clientX - r.left, e.clientY - r.top));
    pointer.current = null; live.current.dragging = false;
  };
  const step = (dx: number, dy: number) => { const { w, h } = size.current, k = R.fitK(w, h) * view.current.z; moved({ z: view.current.z, lon: view.current.lon + (dx * w * 0.2) / (R.KX * k), lat: view.current.lat - (dy * h * 0.2) / k }); };
  const zoom = (f: number) => moved(R.zoomAbout(view.current, size.current.w, size.current.h, size.current.w / 2, size.current.h / 2, f));
  const onKey = (e: React.KeyboardEvent) => {
    const keys: Record<string, () => void> = { ArrowLeft: () => step(-1, 0), ArrowRight: () => step(1, 0), ArrowUp: () => step(0, -1), ArrowDown: () => step(0, 1), "+": () => zoom(1.5), "=": () => zoom(1.5), "-": () => zoom(1 / 1.5) };
    if (keys[e.key]) { e.preventDefault(); keys[e.key](); }
  };

  const toggle = (id: string) => { live.current.touched = true; setChosen({ on: on.includes(id) ? on.filter((x) => x !== id) : [...on, id], fuel }); };
  const toggleFuel = (slug: string, all: string[]) => {
    live.current.touched = true;
    const cur = fuel ?? all, next = cur.includes(slug) ? cur.filter((x) => x !== slug) : [...cur, slug];
    setChosen({ on, fuel: next.length === all.length ? null : next });
  };
  const gradient = (group: string) => `linear-gradient(to right, ${R.rampCss(R.groupColor(group)).join(", ")})`;
  const queueMax = useMemo(() => (queue ? queue.shapes.features.reduce((m, f) => Math.max(m, Number(f.properties.mw) || 0), 0) : 0), [queue]);

  const stateOf = (key: string) => status[key] ?? "";
  const note = (key: string) => {
    const s = stateOf(key);
    if (s === "loading") return <span className="ml-1 text-xs text-muted">reading</span>;
    if (s.startsWith("not read")) return <span className="ml-1 cursor-help border-b border-dotted border-muted text-xs text-muted" title={s}>not read</span>;
    return null;
  };
  const plantsOn = on.includes("plants_operating") || on.includes("plants_planned");
  const fuelsHeld = plants ? plants.techs.filter((t, i) => plants.t.includes(i)).map((t) => t.slug) : [];
  const plantCount = (operating: boolean) => (plants ? plants.st.reduce((a, s, i) => a + ((s === 0) === operating && (!fuel || fuel.includes(plants.techs[plants.t[i]].slug)) ? 1 : 0), 0) : 0);
  const check = "mr-2 align-middle accent-[var(--color-accent)]";
  const btn = "border border-rule bg-white px-2 py-0.5 text-sm leading-tight hover:text-accent";
  const hint = "cursor-help border-b border-dotted border-muted";

  return (
    <div className="grid gap-8 lg:grid-cols-[250px_minmax(0,1fr)]">
      <aside data-toggles="1">
        <section className="mb-4 bg-paper px-4 py-4" aria-label="The resource">
          <h2 className="mb-3 font-serif text-lg text-accent">The resource</h2>
          {manifestReason ? <p className="mb-2 text-xs text-muted" data-manifest-missing="1"><span className={hint} title={manifestReason}>layers not read</span></p> : null}
          {groups.map((g) => (
            <fieldset key={g.id} className="mb-3" data-group={g.id}>
              <legend className="mb-1 text-xs uppercase tracking-wide text-muted">{g.label}</legend>
              {g.items.map((it) => it.held ? (
                <label key={it.layer.id} className="block py-0.5 text-sm" data-layer={it.layer.id} data-kind={it.layer.kind} data-state={stateOf(it.layer.id)} data-level={levels[it.layer.id] ?? ""}>
                  <input type="checkbox" className={check} checked={on.includes(it.layer.id)} onChange={() => toggle(it.layer.id)} data-toggle={it.layer.id} />
                  {it.layer.title}{on.includes(it.layer.id) ? note(it.layer.id) : null}
                </label>
              ) : (
                <label key={it.key} className="block cursor-help py-0.5 text-sm text-muted" title={it.reason} data-missing={it.key}>
                  <input type="checkbox" className={check} disabled aria-disabled="true" />
                  {it.label} <span className="border-b border-dotted border-muted text-xs">{R.NOT_HELD}</span>
                </label>
              ))}
            </fieldset>
          ))}
        </section>
        <section className="mb-4 bg-paper px-4 py-4" aria-label="What is built or planned">
          <h2 className="mb-3 font-serif text-lg text-accent">What is built or planned</h2>
          {R.OVERLAYS.map((o) => (
            <label key={o.id} className="block py-0.5 text-sm" data-layer={o.id} data-kind="overlay" data-state={stateOf(o.source)}>
              <input type="checkbox" className={check} checked={on.includes(o.id)} onChange={() => toggle(o.id)} data-toggle={o.id} />
              {o.label}{on.includes(o.id) ? note(o.source) : null}
            </label>
          ))}
          {plantsOn && plants ? (
            <p className="mt-2 text-xs text-muted" data-count="plants">
              {on.includes("plants_operating") ? <><span data-count-value="plants_operating">{whole(plantCount(true))}</span> operating units</> : null}
              {on.includes("plants_operating") && on.includes("plants_planned") ? ", " : null}
              {on.includes("plants_planned") ? <><span data-count-value="plants_planned">{whole(plantCount(false))}</span> planned or under construction</> : null}
            </p>
          ) : null}
          {on.includes("queue") && queue ? (
            <p className="mt-2 text-xs text-muted" data-count="queue">
              <span data-count-value="queue_drawn">{whole(queue.drawn)}</span> queue rows in <span data-count-value="queue_counties">{whole(queue.counties)}</span> counties;{" "}
              <span className={hint} title="These rows name neither a county the Census Bureau's county outlines hold nor coordinates, so they have no place on the map."><span data-count-value="queue_not_drawn">{whole(queue.not_placed + queue.no_shape)}</span> not drawn</span>
            </p>
          ) : null}
          {on.includes("datacenters") && centers ? (
            <p className="mt-2 text-xs text-muted" data-count="datacenters">
              <span data-count-value="datacenters_drawn">{whole(centers.drawn)}</span> facilities;{" "}
              <span className={hint} title="The table states no place for these facilities, so they have no place on the map."><span data-count-value="datacenters_not_drawn">{whole(centers.not_placed)}</span> not drawn</span>
            </p>
          ) : null}
        </section>
      </aside>

      <div className="min-w-0">
        <div className="mb-2 flex flex-wrap items-center gap-1.5" data-map-buttons="1">
          <button type="button" className={btn} onClick={() => zoom(1.6)} aria-label="Zoom in" data-map-button="in">+</button>
          <button type="button" className={btn} onClick={() => zoom(1 / 1.6)} aria-label="Zoom out" data-map-button="out">-</button>
          <button type="button" className={btn} onClick={() => step(-1, 0)} aria-label="Move west" data-map-button="west">&larr;</button>
          <button type="button" className={btn} onClick={() => step(0, -1)} aria-label="Move north" data-map-button="north">&uarr;</button>
          <button type="button" className={btn} onClick={() => step(0, 1)} aria-label="Move south" data-map-button="south">&darr;</button>
          <button type="button" className={btn} onClick={() => step(1, 0)} aria-label="Move east" data-map-button="east">&rarr;</button>
          {R.PLACES.map((pl) => <button key={pl.id} type="button" className={btn} onClick={() => moved({ z: pl.z, lon: pl.lon, lat: pl.lat })} data-map-button={pl.id}>{pl.label}</button>)}
        </div>
        <div ref={box} className="relative w-full border border-rule" data-map="1" onPointerLeave={() => { lastPointer.current = null; setHover(null); }}>
          <canvas ref={canvas} className="block w-full cursor-crosshair touch-none" role="img" tabIndex={0} aria-label="Map of the United States with the resource layers that are switched on; the legend below names each"
            onPointerDown={onDown} onPointerMove={onMove} onPointerUp={onUp} onPointerCancel={onUp} onKeyDown={onKey} onDoubleClick={(e) => { const r = e.currentTarget.getBoundingClientRect(); moved(R.zoomAbout(view.current, size.current.w, size.current.h, e.clientX - r.left, e.clientY - r.top, 2)); }} />
          {hover ? (
            <div className="pointer-events-none absolute z-10 max-w-xs border border-rule bg-white px-3 py-2 text-sm shadow-sm" data-hover="1" data-hover-lon={hover.lon} data-hover-lat={hover.lat}
              style={{ left: hover.x > hover.w * 0.6 ? undefined : hover.x + 14, right: hover.x > hover.w * 0.6 ? hover.w - hover.x + 14 : undefined, top: hover.y > hover.h * 0.6 ? undefined : hover.y + 14, bottom: hover.y > hover.h * 0.6 ? hover.h - hover.y + 14 : undefined }}>
              <div className="text-xs tabular-nums text-muted">{Math.abs(hover.lat).toFixed(2)} {hover.lat >= 0 ? "N" : "S"}, {Math.abs(hover.lon).toFixed(2)} {hover.lon >= 0 ? "E" : "W"}</div>
              {hover.rows.length === 0 ? <div className="text-muted">No layer has anything here.</div> : hover.rows.map((r, i) => (
                <div key={`${r.id}-${i}`} className="mt-1" data-hover-layer={r.id} data-hover-value={r.value ?? ""} data-hover-feature={r.feature ?? ""} data-hover-empty={r.empty ? "1" : "0"}>
                  <div><span className="text-xs uppercase tracking-wide text-muted">{r.title}</span><br /><span className={r.empty ? "text-muted" : "font-semibold"} data-hover-text="1">{r.text}</span></div>
                  <div className="text-xs leading-snug text-muted" data-hover-sub="1">{r.sub}</div>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        <div className="mt-3 grid gap-x-8 gap-y-3 sm:grid-cols-2" data-legends="1">
          {on.map((id) => {
            const l = byId.get(id);
            if (l) {
              const lg = R.legendOf(l), group = R.groupId(l.group), ks = kinds[id] ?? [];
              const ticks = lg ? [...new Set([lg.min, ...(lg.stops ?? []), lg.max])].filter((t) => t >= lg.min && t <= lg.max).sort((a, c) => a - c) : [];
              const tones = l.classes ? R.classTones(l.classes) : [];
              return (
                <div key={id} data-legend={id} data-unit={l.unit ?? ""} className={`text-xs ${ticks.length > 6 || (l.classes?.length ?? 0) > 4 ? "sm:col-span-2" : ""}`}>
                  <div className="mb-1 text-sm">{l.title}{l.unit ? <span className="text-muted">, {l.unit}</span> : null}</div>
                  {l.classes ? (
                    <ul className="flex flex-wrap gap-x-3 gap-y-1">{l.classes.map((c, j) => <li key={c.value} className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-4" style={{ background: tones[j] === null ? "var(--color-not-reported)" : R.alongCss(R.groupColor(group), tones[j] as number) }} />{c.label}</li>)}</ul>
                  ) : lg ? (
                    <>
                      <div aria-hidden="true" className="h-2.5 w-full border border-rule" style={{ background: gradient(group) }} />
                      <div className="relative mt-0.5 h-4 tabular-nums text-muted">
                        {ticks.map((t, j) => <span key={t} className="absolute" style={j === 0 ? { left: 0 } : j === ticks.length - 1 ? { right: 0 } : { left: `${100 * R.position(t, lg)}%`, transform: "translateX(-50%)" }} data-legend-tick={t}>{R.tickLabel(t, lg)}</span>)}
                      </div>
                    </>
                  ) : ks.length > 4 ? (
                    <div className="inline-flex items-center gap-1.5 text-muted"><span aria-hidden="true" className="inline-block h-2.5 w-4" style={{ background: ks[0].fill, border: `1px solid ${ks[0].stroke}` }} />{ks.length} classes of the source, each named on hover</div>
                  ) : ks.length ? (
                    <ul className="flex flex-wrap gap-x-3 gap-y-1">{ks.map((kd) => <li key={kd.kind} className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-4" style={{ background: kd.fill, border: `1px solid ${kd.stroke}` }} />{kd.kind || "shape"}</li>)}</ul>
                  ) : <div className="text-muted">{l.kind === "grid" || stateOf(id) !== "ready" ? "reading" : "one mark a row of the source"}</div>}
                </div>
              );
            }
            if (id === "plants_planned" && on.includes("plants_operating")) return null;
            if (id === "plants_operating" || id === "plants_planned") {
              return (
                <div key={id} data-legend="plants" data-unit="MW" className="text-xs sm:col-span-2">
                  <div className="mb-1 text-sm">Plants<span className="text-muted">, MW{plants ? `, EIA-860M of ${plants.vintage}` : ""}</span></div>
                  <ul className="flex flex-wrap gap-x-1.5 gap-y-1">
                    {(plants?.techs ?? []).filter((t) => fuelsHeld.includes(t.slug)).map((t) => {
                      const shown = !fuel || fuel.includes(t.slug);
                      return <li key={t.slug}><button type="button" aria-pressed={shown} onClick={() => toggleFuel(t.slug, fuelsHeld)} data-fuel={t.slug} className={`inline-flex items-center gap-1.5 border px-1.5 py-0.5 ${shown ? "border-rule" : "border-transparent text-muted line-through"}`}>
                        <span aria-hidden="true" className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: `var(${COLOR[t.slug] ?? COLOR.other})`, opacity: shown ? 1 : 0.3 }} />{t.name}</button></li>;
                    })}
                  </ul>
                  <div className="mt-1 text-muted">A dot: operating. A ring: planned or under construction. Larger: more MW.</div>
                </div>
              );
            }
            if (id === "queue") {
              return (
                <div key={id} data-legend="queue" data-unit="MW" className="text-xs">
                  <div className="mb-1 text-sm">Interconnection queue by county<span className="text-muted">, MW asked for</span></div>
                  <div aria-hidden="true" className="h-2.5 w-full border border-rule" style={{ background: "linear-gradient(to right, color-mix(in srgb, var(--color-ink) 10%, transparent), color-mix(in srgb, var(--color-ink) 65%, transparent))" }} />
                  <div className="mt-0.5 flex justify-between tabular-nums text-muted"><span>0</span><span>{queue ? whole(queueMax) : ""}</span></div>
                </div>
              );
            }
            if (id === "datacenters") {
              return (
                <div key={id} data-legend="datacenters" data-unit="" className="text-xs">
                  <div className="mb-1 text-sm">Datacenters</div>
                  <div className="inline-flex items-center gap-1.5 text-muted"><span aria-hidden="true" className="inline-block h-2.5 w-2.5 rotate-45 border border-ink bg-panel" />a facility the table places</div>
                </div>
              );
            }
            return null;
          })}
        </div>
      </div>
    </div>
  );
}
