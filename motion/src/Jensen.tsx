// ERW video posts in the approved look (header, title, fog page, rule and source), with two other chart types:
// "blocks" (areas sized by value, one grid) and "ladder" (one rising column against labelled levels). Same 15 seconds.
import React from "react";
import "@fontsource/source-serif-4/600.css";
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import { AbsoluteFill, continueRender, delayRender, Easing, interpolate, useCurrentFrame } from "remotion";

const SERIF = '"Source Serif 4"';
const SANS = '"IBM Plex Sans"';
const MONO = '"IBM Plex Mono"';
const P = { fog: "#F7F3EA", rule: "#E3DED1", captions: "#6B675F", ink: "#2E2D29", cardinal: "#8C1515", bar: "#9A958B" };
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

if (typeof document !== "undefined") {
  const h = delayRender("jensen fonts");
  Promise.all(['600 64px "Source Serif 4"', '400 24px "IBM Plex Sans"', '500 24px "IBM Plex Mono"'].map((f) => document.fonts.load(f))).then(() => continueRender(h));
}

export type ValueSpec = {
  id: string; type: "blocks" | "ladder"; width: number; height: number; frames: number; title: string; source: string;
  lead: { label: string; sub: string; value: number; width?: number };          // the cardinal figure (USD billion)
  rows: { label: string; value: number; count?: number; countText?: string }[];
  showPct?: boolean;                                            // default true: each box shows its value against the lead                    // USD billion, largest first
  max?: number;
};

const usd = (v: number) => (v >= 1000 ? `$${(Math.round(v / 10) / 100).toFixed(2)}T` : `$${Math.round(v)}B`);
const pct = (v: number, lead: number) => `${Math.round((100 * v) / lead)}%`;

const Shell: React.FC<{ spec: ValueSpec; children: React.ReactNode }> = ({ spec, children }) => {
  const f = useCurrentFrame();
  const fade = (from: number) => interpolate(f, [from, from + 12], [0, 1], cl);
  const H = spec.height, ruleY = H - 196;
  const src = interpolate(f, [368, 382], [0, 1], { ...cl, easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ backgroundColor: P.fog, fontFamily: SANS, color: P.ink }}>
      <div style={{ position: "absolute", left: 72, top: 64, opacity: fade(0), display: "flex", alignItems: "baseline", gap: 10, lineHeight: 1 }}>
        <span style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 34, color: P.cardinal }}>ERW</span>
        <span style={{ fontFamily: SANS, fontWeight: 400, fontSize: 32.5, color: P.ink, position: "relative", top: -2.5 }}>Research</span>
      </div>
      <div style={{ position: "absolute", left: 72, right: 72, top: 126, opacity: fade(4), fontFamily: SERIF, fontWeight: 600, fontSize: 62, lineHeight: 1.1 }}>{spec.title}</div>
      {children}
      <div style={{ position: "absolute", left: 72, right: 72, top: ruleY, height: 2, background: P.rule, opacity: src }} />
      <div style={{ position: "absolute", left: 72, right: 72, top: ruleY + 30, fontSize: 21, lineHeight: 1.42, color: P.captions, opacity: src, transform: `translateY(${(1 - src) * 12}px)` }}>{spec.source}</div>
    </AbsoluteFill>
  );
};

// ---- squarified treemap -------------------------------------------------------------------------------------------
type Cell = { i: number; x: number; y: number; w: number; h: number };
function squarify(vals: number[], x: number, y: number, w: number, h: number): Cell[] {
  const total = vals.reduce((a, b) => a + b, 0);
  const areas = vals.map((v) => (v / total) * w * h);
  const out: Cell[] = [];
  let i = 0, rx = x, ry = y, rw = w, rh = h;
  const worst = (row: number[], side: number) => {
    const s = row.reduce((a, b) => a + b, 0), mx = Math.max(...row), mn = Math.min(...row);
    return Math.max((side * side * mx) / (s * s), (s * s) / (side * side * mn));
  };
  while (i < areas.length) {
    const side = Math.min(rw, rh);
    let row = [areas[i]]; let j = i + 1;
    while (j < areas.length && worst([...row, areas[j]], side) <= worst(row, side)) { row.push(areas[j]); j++; }
    const s = row.reduce((a, b) => a + b, 0);
    if (rw >= rh) { // lay the row as a column on the left
      const cw = s / rh; let cy = ry;
      row.forEach((a, k) => { const ch = a / cw; out.push({ i: i + k, x: rx, y: cy, w: cw, h: ch }); cy += ch; });
      rx += cw; rw -= cw;
    } else {
      const ch = s / rw; let cx = rx;
      row.forEach((a, k) => { const cw = a / ch; out.push({ i: i + k, x: cx, y: ry, w: cw, h: ch }); cx += cw; });
      ry += ch; rh -= ch;
    }
    i = j;
  }
  return out;
}

// One grid: the lead figure is a block among the others, on the same scale, so the areas compare directly.
// The three smallest blocks are stacked in one column, so the smallest is wide enough to hold its text on one line.
export const Blocks: React.FC<{ spec: ValueSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const H = spec.height, top = H > 1080 ? 330 : 296, bottom = H - 196 - 40, availH = bottom - top, availW = 1080 - 144;
  type Item = { label: string; value: number; lead: boolean; count?: number; countText?: string };
  const items: Item[] = [...spec.rows.map((r) => ({ ...r, lead: false }))].sort((a, b) => b.value - a.value);
  const gap = 26, all = items.reduce((a, r) => a + r.value, 0);
  // The lead block is on the same area scale as the grid. Default: same height as the grid, so widths are in proportion.
  // With lead.width set, the block is that wide and its height follows from the same pixels-per-dollar as the grid.
  const leadW = spec.lead.width ?? ((availW - gap) * spec.lead.value) / (spec.lead.value + all);
  const leadH = spec.lead.width ? ((availW - gap - leadW) * availH * spec.lead.value) / all / leadW : availH;
  const tail = items.slice(-3), head = items.slice(0, -3);
  const tailSum = tail.reduce((a, r) => a + r.value, 0);
  const cellsH = squarify([...head.map((r) => r.value), tailSum], 72 + leadW + gap, top, availW - leadW - gap, availH);
  const boxes: { r: Item; x: number; y: number; w: number; h: number }[] = [{ r: { label: spec.lead.label, value: spec.lead.value, lead: true }, x: 72, y: top + availH - leadH, w: leadW, h: leadH }];
  cellsH.forEach((c) => {
    if (c.i < head.length) boxes.push({ r: head[c.i], x: c.x, y: c.y, w: c.w, h: c.h });
    else { let yy = c.y; tail.forEach((r) => { const hh = (r.value / tailSum) * c.h; boxes.push({ r, x: c.x, y: yy, w: c.w, h: hh }); yy += hh; }); }
  });
  // order of appearance: the lead first, then the rest from the largest
  const order = [...boxes].sort((a, b) => (a.r.lead ? -1 : b.r.lead ? 1 : b.r.value - a.r.value));
  const ease = Easing.out(Easing.cubic);
  return (
    <Shell spec={spec}>
      {order.map((b, k) => {
        const r = b.r;
        const start = r.lead ? 26 : 84 + (k - 1) * 26;
        const g = interpolate(f, [start, start + 22], [0, 1], { ...cl, easing: ease });
        const count = r.lead ? interpolate(f, [26, 70], [0, 1], { ...cl, easing: Easing.inOut(Easing.cubic) }) : 1;
        const rise = r.lead ? count : 1;
        const w = Math.max(0, b.w - 4), h = Math.max(0, b.h - 4);
        const longest = Math.max(...r.label.split(" ").map((x) => x.length), usd(r.value).length * 1.2);
        const base0 = w * h > 60000 ? 30 : 25;
        const fs = Math.max(13, Math.min(base0, (w - 30) / (0.56 * longest)));
        const oneLine = h < 44;                             // a flat strip: label, value and percent on one line
        const twoLine = !oneLine && h < fs * 4.4;           // a low box: the label, then value and percent side by side
        const fs1 = Math.min(17, Math.max(11.5, h - 1));
        const fs2 = Math.min(19, (w - 26) / (0.54 * Math.max(r.label.length, 12)));
        const ink = r.lead ? P.fog : P.ink, soft = r.lead ? "#E9CFCB" : P.captions;
        // number of companies in the box: beside the percent where it fits, else on its own line; the flat strip takes the bare number
        const showPct = spec.showPct !== false;
        const cTxt = r.countText ?? (r.count ? `${r.count} ${r.count === 1 ? "company" : "companies"}` : "");
        const pTxt = pct(r.value, spec.lead.value);
        const padL = fs < 22 ? 10 : 14, inner = w - padL - 6;
        const cfs = Math.max(13.5, fs * 0.6);
        const beside = 0.6 * pTxt.length * fs * 0.72 + 12 + 0.53 * cTxt.length * cfs <= inner;
        const rest2 = 0.6 * usd(r.value).length * fs2 * 1.08 + 0.6 * pTxt.length * fs2 * 0.78 + 20;
        const cfs2 = Math.max(12, Math.min(fs2 * 0.74, (w - 20 - rest2) / (0.56 * Math.max(1, cTxt.length))));
        return (
          <div key={r.label} style={{ position: "absolute", left: b.x + 2, top: b.y + 2 + h * (1 - rise), width: w, height: h * rise, background: r.lead ? P.cardinal : P.rule, opacity: r.lead ? 1 : g, transform: r.lead ? undefined : `scale(${0.96 + 0.04 * g})`, transformOrigin: "top left", overflow: "hidden", color: ink }}>
            {oneLine ? (
              <div style={{ position: "absolute", left: 12, right: 8, top: 0, bottom: 0, display: "flex", alignItems: "center", gap: 8, fontSize: fs1, lineHeight: 1, whiteSpace: "nowrap" }}>
                <span>{r.label}</span>
                <span style={{ fontFamily: MONO, fontWeight: 500 }}>{usd(r.value)}</span>
                {showPct && <span style={{ fontFamily: MONO, fontWeight: 500, color: soft, fontSize: fs1 * 0.85 }}>{pTxt}</span>}
                {cTxt ? <span style={{ color: soft, fontSize: fs1 * 0.9 }}>{r.countText ?? r.count}</span> : null}
              </div>
            ) : twoLine ? (
              <div style={{ position: "absolute", left: 12, right: 8, top: 0, bottom: 0, display: "flex", flexDirection: "column", justifyContent: "center", whiteSpace: "nowrap" }}>
                <div style={{ fontSize: fs2, lineHeight: 1.15 }}>{r.label}</div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 3 }}>
                  <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: fs2 * 1.08 }}>{usd(r.value)}</span>
                  {showPct && <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: fs2 * 0.78, color: soft }}>{pTxt}</span>}
                  {cTxt ? <span style={{ fontSize: showPct ? cfs2 : fs2 * 0.86, color: soft }}>{!showPct || rest2 + 0.53 * cTxt.length * 12 <= w - 20 ? cTxt : r.count}</span> : null}
                </div>
              </div>
            ) : (
              <div style={{ position: "absolute", left: fs < 22 ? 10 : 14, top: r.lead ? undefined : fs < 22 ? 8 : 11, bottom: r.lead ? h - (h * rise) + 0 : undefined, right: 6, ...(r.lead ? { top: 14 - h * (1 - rise) * 0 } : {}) }}>
                <div style={{ fontFamily: r.lead ? SERIF : SANS, fontWeight: r.lead ? 600 : 400, fontSize: r.lead ? Math.min(fs * 1.25, (w - 30) / (0.74 * r.label.length)) : fs, lineHeight: 1.12 }}>{r.label}</div>
                {r.lead && <div style={{ fontSize: Math.max(15, fs * 0.66), lineHeight: 1.25, marginTop: 6, color: soft }}>{spec.lead.sub}</div>}
                <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: fs * (fs < 22 ? 1 : 1.12) * (r.lead ? 1.25 : 1), marginTop: fs < 22 ? 3 : 6, fontVariantNumeric: "tabular-nums" }}>{usd(Math.round(r.value * count))}</div>
                {!r.lead && (
                  <div style={{ display: "flex", flexDirection: beside ? "row" : "column", alignItems: beside ? "baseline" : "flex-start", gap: beside ? 12 : 3, marginTop: 2, color: soft, whiteSpace: "nowrap" }}>
                    {showPct && <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: fs * 0.72 }}>{pTxt}</span>}
                    {cTxt ? <span style={{ fontSize: showPct ? cfs : fs * 0.72 }}>{cTxt}</span> : null}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </Shell>
  );
};

export const Ladder: React.FC<{ spec: ValueSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const H = spec.height, top = H > 1080 ? 340 : 304, base = H - 196 - 36, span = base - top;
  const max = spec.max ?? Math.max(spec.lead.value, ...spec.rows.map((r) => r.value)) * 1.04;
  const y = (v: number) => base - (v / max) * span;
  const colX = 72, colW = 236, lineX0 = colX + colW + 26, labelX = 600;
  const rise = interpolate(f, [120, 330], [0, 1], { ...cl, easing: Easing.inOut(Easing.cubic) });
  const now = spec.lead.value * rise;
  const order = [...spec.rows].sort((p, q) => p.value - q.value);
  const minGap = H > 1080 ? 46 : 40;
  const ly: number[] = [];
  order.forEach((r, k) => { const want = y(r.value); ly.push(k === 0 ? Math.min(want, base - 26) : Math.min(want, ly[k - 1] - minGap)); });
  return (
    <Shell spec={spec}>
      <div style={{ position: "absolute", left: colX, top: base, width: 1080 - 144, height: 2, background: P.ink, opacity: interpolate(f, [12, 26], [0, 1], cl) }} />
      {order.map((r, k) => {
        const g = interpolate(f, [20 + k * 9, 40 + k * 9], [0, 1], cl);
        const passed = now >= r.value ? 1 : 0;
        const yy = y(r.value);
        return (
          <React.Fragment key={r.label}>
            <div style={{ position: "absolute", left: lineX0, top: yy - 1, width: labelX - lineX0 - 70, height: 2, background: passed ? P.bar : P.rule, opacity: g }} />
            <svg style={{ position: "absolute", left: 0, top: 0, opacity: g }} width={1080} height={H}>
              <polyline points={`${labelX - 70},${yy} ${labelX - 22},${ly[k]} ${labelX - 8},${ly[k]}`} fill="none" stroke={passed ? P.bar : P.rule} strokeWidth={2} />
            </svg>
            <div style={{ position: "absolute", left: labelX, top: ly[k] - 19, right: 72, display: "flex", alignItems: "baseline", opacity: g, whiteSpace: "nowrap" }}>
              <div style={{ fontSize: 27, width: 232 }}>{r.label}</div>
              <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 27, width: 112, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{usd(r.value)}</div>
              <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 19, width: 64, textAlign: "right", color: P.captions }}>{pct(r.value, spec.lead.value)}</div>
            </div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: colX, top: y(now), width: colW, height: base - y(now), background: P.cardinal }} />
      <div style={{ position: "absolute", left: colX, width: colW + 60, top: y(now) - 172, opacity: interpolate(f, [100, 118], [0, 1], cl) }}>
        <div style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 36, lineHeight: 1.08, color: P.cardinal }}>{spec.lead.label}</div>
        <div style={{ fontSize: 22, lineHeight: 1.2, marginTop: 4 }}>{spec.lead.sub}</div>
        <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 46, marginTop: 4, color: P.cardinal, fontVariantNumeric: "tabular-nums" }}>{usd(Math.round(now))}</div>
      </div>
    </Shell>
  );
};
