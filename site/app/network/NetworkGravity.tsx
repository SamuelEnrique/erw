"use client";
// Session 266 (the owner's task of 14 October 2026): the network's third shape, "Gravity", beside "Map" and "Network".
// The Lower 48 at the center; each of the seven ISO grids a circle whose area follows its net generation in the hour
// shown, pulled toward the center by its net imports over its reporting ties and pushed out by its net exports, as a
// share of its generation (lib/networkGravity.ts holds the rule; docs/methods/grid_network.md writes it down).
// Network.tsx owns everything this file draws from: the view, the hour, the selection, the colors and the panel. As on
// the map, hovering a circle names it and clicking it opens the same panel; no number is drawn here that the panel and
// the other two shapes do not show. Colors are the brand's tokens (app/tokens.css), never a literal.
// Session 1153 (chain 077): every edge (the line from the Lower 48 to a grid) carries the grid's net exchange in the
// window and answers a hover with it, its share of the grid's generation and its window (the hour shown, the snapshot's
// refresh); a grid with no tie reported in the window has no edge. A circle's hover card adds its generation. The note
// under the frame says the shape is drawn from EIA-930's public interchange and generation only, for every grid.
import { useMemo, useState, type PointerEvent } from "react";
import { GRAVITY, gravityEdges, gravityLayout, gravityTip, type GravityLayout, type GravityWindow } from "@/lib/networkGravity";

export function NetworkGravity({ gen, net, names, colorOf, at, pick, neighbours, onPick, held }: {
  /** the hour's net generation, MW, by EIA-930 code (the seven ISO grids and US48) */
  gen: Record<string, number | null>;
  /** the hour's net imports over the reporting ties, MW, by code (null: no tie reported) */
  net: Record<string, number | null>;
  names: Map<string, string>;
  /** the color the grid's sphere has for the hour shown (Network.tsx colorOf) */
  colorOf: (id: string) => string;
  /** session 1153: the window every figure of the shape belongs to: the hour shown and the snapshot's refresh */
  at: GravityWindow;
  pick: string | null;
  neighbours: Set<string>;
  onPick: (id: string) => void;
  /** false outside the live week: generation by hour is held for the live week only, so nothing is drawn */
  held: boolean;
}) {
  const [hover, setHover] = useState<{ id: string; kind: "edge" | "circle"; x: number; y: number; right: boolean } | null>(null);
  const lay: GravityLayout = useMemo(() => gravityLayout(gen, net), [gen, net]);
  const { SIZE, D_MID } = GRAVITY;
  const frame = "w-full min-w-0 overflow-hidden border border-rule";
  const style = { aspectRatio: "1 / 1", maxHeight: "min(72vh, 620px)", minHeight: 200 };
  if (!held) {
    return (
      <div className={`${frame} flex items-center justify-center bg-panel p-6`} style={style} data-gravity-state="not-held">
        <p className="max-w-md text-sm" role="status">The gravity shape is drawn for the live week only: net generation by hour is held for the live week, not for a story or a replayed day, and no circle is sized from a stand-in. Choose &quot;Live now&quot;, or the Network or Map shape.
          {" "}A replayed day stays in the address, and the Network and Map shapes draw its interchange from EIA&apos;s daily file; its generation is not held, so this shape places no grid for it.</p>
      </div>
    );
  }
  const c = SIZE / 2;
  const nameOf = (id: string) => names.get(id) ?? (id === "US48" ? "The Lower 48 states" : id);
  const hoverAt = (id: string, kind: "edge" | "circle" = "circle") => (e: PointerEvent<SVGElement>) => {
    const b = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
    setHover({ id, kind, x: e.clientX - b.left, y: e.clientY - b.top, right: e.clientX - b.left > b.width / 2 });
  };
  const hovered = hover ? lay.places.find((p) => p.id === hover.id) ?? null : null;
  return (
    <div className={`${frame} self-start bg-paper`} data-gravity-state="held" data-gravity-center={lay.center.gen ?? ""}>
      <div className="relative mx-auto" style={style}>
        <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="h-full w-full" role="group" preserveAspectRatio="xMidYMid meet"
          aria-label="The seven ISO grids around the Lower 48: each circle's area is its net generation in the hour shown; a net importer sits nearer the center, a net exporter farther out; hover a circle or its line for its figures and their hour, click a circle for its panel">
          {/* the middle ring: no net exchange */}
          <circle cx={c} cy={c} r={D_MID} fill="none" stroke="var(--color-rule)" strokeDasharray="4 6" data-gravity-ring="1" />
          {/* session 1153: an edge only where the grid has a net figure in the window; a wide clear stroke takes the hover */}
          {gravityEdges(lay).map((p) => (
            <g key={`s-${p.id}`} data-gravity-edge={p.id} data-mw={p.net ?? ""} onPointerMove={hoverAt(p.id, "edge")} onPointerLeave={() => setHover(null)}>
              <line x1={c} y1={c} x2={p.x} y2={p.y} stroke="var(--color-rule)" strokeWidth={1.2}
                strokeOpacity={pick !== null && pick !== p.id && !neighbours.has(p.id) ? 0.3 : 0.9} />
              <line x1={c} y1={c} x2={p.x} y2={p.y} stroke="var(--color-ink)" strokeOpacity={0} strokeWidth={16} pointerEvents="stroke" />
            </g>
          ))}
          <g data-gravity-grid="US48" onPointerMove={hoverAt("US48")} onPointerLeave={() => setHover(null)}>
            <circle cx={c} cy={c} r={lay.center.r} fill="var(--color-panel)" stroke="var(--color-ink)" strokeWidth={1.2} strokeDasharray={lay.center.gen === null ? "3 4" : undefined} />
            <text x={c} y={c + 9} textAnchor="middle" fontSize={26} fontFamily="var(--font-sans)" fill="var(--color-ink)">Lower 48</text>
          </g>
          {lay.places.map((p) => {
            const dim = pick !== null && pick !== p.id && !neighbours.has(p.id);
            const hollow = p.state === "no-generation" || p.state === "zero-generation";
            const fill = hollow ? "none" : colorOf(p.id);
            // session 583: a circle's name begins with the label drawn under it ("CAISO, California Independent System
            // Operator"), so a voice command that says what is seen reaches it (AccessLint, label-content-mismatch, WCAG 2.5.3)
            return (
              <g key={p.id} data-gravity-grid={p.id} data-gravity-state={p.state} data-gen={p.gen ?? ""} data-net={p.net ?? ""} data-share={p.share ?? ""}
                data-d={Math.round(p.d * 10) / 10} data-r={Math.round(p.r * 10) / 10} data-dim={dim ? "1" : "0"} className="cursor-pointer" tabIndex={0} role="button" aria-label={nameOf(p.id).includes(p.label) ? nameOf(p.id) : `${p.label}, ${nameOf(p.id)}`}
                onClick={() => onPick(p.id)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onPick(p.id); } }}
                onPointerMove={hoverAt(p.id)} onPointerLeave={() => setHover(null)} onFocus={() => setHover({ id: p.id, kind: "circle", x: -1, y: -1, right: false })} onBlur={() => setHover(null)}>
                <circle cx={p.x} cy={p.y} r={p.r} fill={fill} fillOpacity={dim ? 0.22 : 0.9} stroke={pick === p.id ? "var(--color-ink)" : hollow ? "var(--color-muted)" : "var(--color-panel)"}
                  strokeWidth={pick === p.id ? 2.4 : 1.2} strokeDasharray={hollow ? "3 3" : undefined} />
                <text x={p.x} y={p.y + p.r + 26} textAnchor="middle" fontSize={26} fontFamily="var(--font-sans)" fill="var(--color-ink)" fillOpacity={dim ? 0.4 : 1}>{p.label}</text>
              </g>
            );
          })}
        </svg>
        {hover ? (
          <div className="pointer-events-none absolute z-10 max-w-xs border border-rule bg-panel px-2 py-0.5 text-xs" data-gravity-hover={hover.id} data-gravity-hover-kind={hover.kind}
            style={hover.x < 0 ? { left: 8, top: 8 } : hover.right ? { right: `calc(100% - ${hover.x - 12}px)`, top: hover.y + 12 } : { left: hover.x + 12, top: hover.y + 12 }}>
            <div className="text-ink">{nameOf(hover.id)}</div>
            {hovered ? gravityTip(hovered, at, hover.kind).map((line) => <div key={line} className="text-muted">{line}</div>) : null}
          </div>
        ) : null}
      </div>
      {/* session 299 (the owner's rulings 1a and 2c of 18 October 2026): the one source, with its break named; the pull's scale */}
      <p className="border-t border-rule px-3 py-2 text-xs text-muted" data-gravity-note="1">
        Every circle is EIA-930&apos;s net generation, one source for all eight; CAISO&apos;s reads smaller and more pulled in since December 2025, when its EIA-930 generation by fuel broke (the Mix and Clean views draw California from CAISO&apos;s own supply by fuel from mid-December 2025; this shape does not).
        A circle&apos;s pull follows the square root of its net imports over its generation, full at {Math.round(GRAVITY.S_FULL * 100)} percent (session 299; a straight line until then), so a small importer moves visibly. The 63 other balancing authorities are not drawn.
        {" "}<span data-gravity-public="1">Every place and size is drawn from EIA-930&apos;s public interchange and net generation only, for every grid, PJM, MISO, ISO-NE and NYISO included, whose own tables are held or paused here: no grid operator&apos;s own table places or sizes a circle. The color is carbon intensity (carbon_intensity_hourly): EIA-930&apos;s emissions over its net generation, and for California since 16 December 2025 over CAISO&apos;s own generation.</span>
      </p>
    </div>
  );
}
