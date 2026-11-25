// Energy Research Warehouse (ERW), session 9901 (25 November 2026): the batch-2 video posts. The approved look of
// Jensen.tsx (header, title, fog page, rule and source line, 15 seconds) with the header and title shown from frame 0,
// and ten chart types, so that no two options of a post share one. Every printed figure is a display string written
// by docs/research/motion/posts/batch_2026-11-25/scripts/build_9901.py from the source digits (rounded half up);
// marks are drawn from the unrounded values, on scales that start at zero.
import React from "react";
import "@fontsource/source-serif-4/600.css";
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import { AbsoluteFill, continueRender, delayRender, Easing, interpolate, useCurrentFrame } from "remotion";

const SERIF = '"Source Serif 4"';
const SANS = '"IBM Plex Sans"';
const MONO = '"IBM Plex Mono"';
const P = { fog: "#F7F3EA", rule: "#E3DED1", captions: "#6B675F", ink: "#2E2D29", cardinal: "#8C1515", mark: "#9A958B", fill: "#E3DED1" };
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const E = Easing.out(Easing.cubic);
const EIO = Easing.inOut(Easing.cubic);
const ramp = (f: number, a: number, b: number, easing = E) => interpolate(f, [a, b], [0, 1], { ...cl, easing });
const HALO = `0 0 3px ${P.fog}, 0 0 3px ${P.fog}, 0 0 6px ${P.fog}, 0 0 6px ${P.fog}`;
const L = 72, R = 1008, W = 936;

if (typeof document !== "undefined") {
  const h = delayRender("batch2 fonts");
  Promise.all(['600 64px "Source Serif 4"', '400 24px "IBM Plex Sans"', '500 24px "IBM Plex Mono"'].map((x) => document.fonts.load(x))).then(() => continueRender(h));
}

type Base = { id: string; type: string; width: number; height: number; frames: number; title: string; source: string };
const zone = (H: number) => ({ top: H > 1080 ? 330 : 296, bottom: H - 196 - 40 });

// a trailing period ("2019-2025") never breaks at its hyphen
const titleParts = (t: string) => { const m = t.match(/^(.*?)(\d{4}-\d{4})$/); return m ? <>{m[1]}<span style={{ whiteSpace: "nowrap" }}>{m[2]}</span></> : t; };

// The frame: header and title fully visible from frame 0 (the cover X and Instagram may show), the rule and source line
// fading in at 368 to 382 as in Jensen.tsx.
export const Shell2: React.FC<{ spec: Base; children: React.ReactNode }> = ({ spec, children }) => {
  const f = useCurrentFrame();
  const H = spec.height, ruleY = H - 196;
  const src = interpolate(f, [368, 382], [0, 1], { ...cl, easing: E });
  return (
    <AbsoluteFill style={{ backgroundColor: P.fog, fontFamily: SANS, color: P.ink }}>
      <div style={{ position: "absolute", left: L, top: 64, display: "flex", alignItems: "baseline", gap: 10, lineHeight: 1 }}>
        <span style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 34, color: P.cardinal }}>ERW</span>
        <span style={{ fontFamily: SANS, fontWeight: 400, fontSize: 32.5, color: P.ink, position: "relative", top: -2.5 }}>Research</span>
      </div>
      <div data-check="title" style={{ position: "absolute", left: L, right: L, top: 126, fontFamily: SERIF, fontWeight: 600, fontSize: 62, lineHeight: 1.1 }}>{titleParts(spec.title)}</div>
      {children}
      <div style={{ position: "absolute", left: L, right: L, top: ruleY, height: 2, background: P.rule, opacity: src }} />
      <div data-check="source" style={{ position: "absolute", left: L, right: L, top: ruleY + 30, fontSize: 21, lineHeight: 1.42, color: P.captions, opacity: src, transform: `translateY(${(1 - src) * 12}px)` }}>{spec.source}</div>
    </AbsoluteFill>
  );
};

const Txt: React.FC<{ x: number; y: number; anchor?: "left" | "right" | "center"; v?: "top" | "middle" | "bottom"; style?: React.CSSProperties; children: React.ReactNode; o?: number }> = ({ x, y, anchor = "left", v = "top", style, children, o = 1 }) => {
  const tx = anchor === "left" ? "0" : anchor === "right" ? "-100%" : "-50%";
  const ty = v === "top" ? "0" : v === "bottom" ? "-100%" : "-50%";
  return <div style={{ position: "absolute", left: x, top: y, transform: `translate(${tx}, ${ty})`, whiteSpace: "nowrap", opacity: o, ...style }}>{children}</div>;
};

// ---- columns: one column a year, from zero, the highlighted one cardinal --------------------------------------------------
type ColSpec = Base & { rows: { label: string; value: number; display: string }[]; highlight: number; max: number };
export const Columns: React.FC<{ spec: ColSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const base = bottom - 46, span = base - top;
  const n = spec.rows.length, slot = W / n, cw = Math.min(104, slot * 0.7);
  const split = (d: string) => { const m = d.match(/^(.*) (MW)$/); return m ? [m[1], m[2]] : [d, ""]; };
  const longest = Math.max(...spec.rows.map((r) => split(r.display)[0].length));
  const fs = Math.min(30, (slot - 10) / (0.6 * longest));
  return (
    <Shell2 spec={spec}>
      <div style={{ position: "absolute", left: L, top: base, width: W, height: 2, background: P.ink, opacity: ramp(f, 6, 20) }} />
      {spec.rows.map((r, i) => {
        const st = 30 + i * 26, g = ramp(f, st, st + 36), hl = i === spec.highlight;
        const h = (r.value / spec.max) * span * g, cx = L + slot * (i + 0.5);
        return (
          <React.Fragment key={r.label}>
            <div style={{ position: "absolute", left: cx - cw / 2, top: base - h, width: cw, height: h, background: hl ? P.cardinal : P.mark }} />
            <Txt x={cx} y={base - (r.value / spec.max) * span - 10} anchor="center" v="bottom" o={ramp(f, st + 26, st + 40)}
              style={{ textAlign: "center", lineHeight: 1.1, color: hl ? P.cardinal : P.ink }}>
              <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: fs }}>{split(r.display)[0]}</div>
              {split(r.display)[1] && <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 19, color: hl ? P.cardinal : P.captions }}>{split(r.display)[1]}</div>}
            </Txt>
            <Txt x={cx} y={base + 12} anchor="center" o={ramp(f, st, st + 14)} style={{ fontSize: 26, color: hl ? P.cardinal : P.ink }}>{r.label}</Txt>
          </React.Fragment>
        );
      })}
    </Shell2>
  );
};

// ---- a line or area by year, from zero, first and last values labelled ---------------------------------------------------
type YLSpec = Base & { mode: "line" | "area"; points: { year: number; value: number | null; display: string | null }[]; yMax: number; yTicks: { v: number; label: string }[]; yUnit?: string; xTicks: number[] };
export const YearLine: React.FC<{ spec: YLSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const pt = top + (spec.yUnit ? 46 : 26), base = bottom - 46;
  const tickW = Math.max(...spec.yTicks.map((t) => t.label.length)) * 11 + 16;
  const lastDisp = [...spec.points].reverse().find((p) => p.value !== null)!.display || "";
  const x0 = L + tickW + 14, x1 = R - (18 + 0.6 * 32 * lastDisp.length + 6);
  const ys = spec.points.map((p) => p.year), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const X = (yr: number) => x0 + ((yr - y0) / (y1 - y0)) * (x1 - x0);
  const Y = (v: number) => base - (v / spec.yMax) * (base - pt);
  const segs: { year: number; value: number }[][] = [];
  let cur: { year: number; value: number }[] = [];
  spec.points.forEach((p) => { if (p.value === null) { if (cur.length) segs.push(cur); cur = []; } else cur.push({ year: p.year, value: p.value }); });
  if (cur.length) segs.push(cur);
  const prog = ramp(f, 30, 270, EIO);
  const clipW = (x1 - x0 + 24) * prog;
  const first = spec.points.find((p) => p.value !== null)!, last = [...spec.points].reverse().find((p) => p.value !== null)!;
  const head = x0 - 12 + clipW;
  // the first label sits above the line wherever the line runs under it
  const fw = 0.6 * 32 * (first.display || "").length + 8, fx0 = X(first.year) - 4, fx1 = fx0 + fw;
  let firstY = Y(first.value!) - 6;
  segs.forEach((s) => s.forEach((p, i) => {
    const xa = X(p.year);
    if (xa >= fx0 && xa <= fx1) firstY = Math.min(firstY, Y(p.value) - 6);
    const q = s[i + 1];
    if (q && xa < fx1 && X(q.year) > fx1) { const t = (fx1 - xa) / (X(q.year) - xa); firstY = Math.min(firstY, Y(p.value + (q.value - p.value) * t) - 6); }
  }));
  const isArea = spec.mode === "area";
  const lineCol = P.cardinal;
  return (
    <Shell2 spec={spec}>
      <svg style={{ position: "absolute", left: 0, top: 0 }} width={1080} height={spec.height}>
        <defs><clipPath id={`clip-${spec.id}`}><rect x={x0 - 12} y={0} width={clipW} height={spec.height} /></clipPath></defs>
        {spec.yTicks.map((t) => (
          <line key={t.v} x1={x0 - 8} x2={x1 + 8} y1={Y(t.v)} y2={Y(t.v)} stroke={t.v === 0 ? P.ink : P.rule} strokeWidth={2} opacity={ramp(f, 6, 22)} />
        ))}
        <g clipPath={`url(#clip-${spec.id})`}>
          {segs.map((s, k) => {
            const d = s.map((p, i) => `${i ? "L" : "M"}${X(p.year)},${Y(p.value)}`).join(" ");
            return (
              <React.Fragment key={k}>
                {isArea && <path d={`${d} L${X(s[s.length - 1].year)},${Y(0)} L${X(s[0].year)},${Y(0)} Z`} fill={P.cardinal} />}
                <path d={d} fill="none" stroke={lineCol} strokeWidth={isArea ? 3 : 5} strokeLinejoin="round" strokeLinecap="round" />
                {!isArea && s.map((p) => <circle key={p.year} cx={X(p.year)} cy={Y(p.value)} r={6} fill={lineCol} />)}
              </React.Fragment>
            );
          })}
        </g>
        {[first, last].map((p) => (
          <circle key={p.year} cx={X(p.year)} cy={Y(p.value!)} r={isArea ? 8 : 10} fill={P.cardinal} stroke={P.fog} strokeWidth={3} opacity={head >= X(p.year) - 1 ? 1 : 0} />
        ))}
      </svg>
      {spec.yTicks.map((t) => (
        <Txt key={t.v} x={x0 - 18} y={Y(t.v)} anchor="right" v="middle" o={ramp(f, 6, 22)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 18, color: P.captions }}>{t.label}</Txt>
      ))}
      {spec.yUnit && <Txt x={x0 - 18} y={pt - 30} anchor="right" v="middle" o={ramp(f, 6, 22)} style={{ fontSize: 18, color: P.captions }}>{spec.yUnit}</Txt>}
      {spec.xTicks.map((yr) => (
        <Txt key={yr} x={X(yr)} y={base + 12} anchor="center" o={ramp(f, 6, 22)} style={{ fontSize: 24 }}>{String(yr)}</Txt>
      ))}
      <Txt x={X(first.year) - 4} y={firstY - 12} anchor="left" v="bottom" o={ramp(f, 40, 54)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 32, textShadow: HALO }}>{first.display}</Txt>
      <Txt x={X(last.year) + 18} y={Y(last.value!)} anchor="left" v="middle" o={ramp(f, 266, 282)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 32, color: P.cardinal }}>{last.display}</Txt>
    </Shell2>
  );
};

// ---- the weekly price line, Thanksgiving weeks marked --------------------------------------------------------------------
type WLSpec = Base & { values: number[]; dots: { i: number; label: string }[]; yMax: number; yTicks: { v: number; label: string }[]; xTicks: { i: number; label: string }[] };
export const WeekLine: React.FC<{ spec: WLSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const pt = top + 60, base = bottom - 46;
  const x0 = L + 58, x1 = R - 40, n = spec.values.length;
  const X = (i: number) => x0 + (i / (n - 1)) * (x1 - x0);
  const Y = (v: number) => base - (v / spec.yMax) * (base - pt);
  const prog = ramp(f, 24, 300, EIO);
  const head = x0 + (x1 - x0) * prog;
  const d = spec.values.map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(2)},${Y(v).toFixed(2)}`).join(" ");
  return (
    <Shell2 spec={spec}>
      <svg style={{ position: "absolute", left: 0, top: 0 }} width={1080} height={spec.height}>
        <defs><clipPath id={`clip-${spec.id}`}><rect x={x0 - 4} y={0} width={head - x0 + 4} height={spec.height} /></clipPath></defs>
        {spec.yTicks.map((t) => <line key={t.v} x1={x0 - 6} x2={x1 + 6} y1={Y(t.v)} y2={Y(t.v)} stroke={t.v === 0 ? P.ink : P.rule} strokeWidth={2} opacity={ramp(f, 4, 18)} />)}
        <path d={d} fill="none" stroke={P.mark} strokeWidth={3} strokeLinejoin="round" clipPath={`url(#clip-${spec.id})`} />
        {spec.dots.map((p) => <circle key={p.i} cx={X(p.i)} cy={Y(spec.values[p.i])} r={9} fill={P.cardinal} stroke={P.fog} strokeWidth={3} opacity={head >= X(p.i) ? 1 : 0} />)}
      </svg>
      {spec.yTicks.map((t) => <Txt key={t.v} x={x0 - 14} y={Y(t.v)} anchor="right" v="middle" o={ramp(f, 4, 18)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 18, color: P.captions }}>{t.label}</Txt>)}
      <div style={{ position: "absolute", left: x0, top: top - 10, display: "flex", gap: 30, alignItems: "center", fontSize: 22, opacity: ramp(f, 4, 18) }}>
        <span style={{ display: "flex", alignItems: "center", gap: 9 }}><span style={{ width: 18, height: 18, borderRadius: 9, background: P.cardinal, display: "inline-block" }} />Thanksgiving week</span>
        <span style={{ display: "flex", alignItems: "center", gap: 9 }}><span style={{ width: 28, height: 3, background: P.mark, display: "inline-block" }} />Every week</span>
      </div>
      {spec.xTicks.map((t) => <Txt key={t.i} x={X(t.i)} y={base + 12} anchor="left" o={ramp(f, 4, 18)} style={{ fontSize: 22, color: P.ink }}>{t.label}</Txt>)}
      {spec.xTicks.map((t) => <div key={`t${t.i}`} style={{ position: "absolute", left: X(t.i) - 1, top: base, width: 2, height: 10, background: P.ink, opacity: ramp(f, 4, 18) }} />)}
      {spec.dots.map((p) => {
        const at = X(p.i), o = Math.max(interpolate(head - at, [0, 30], [0, 1], cl), ramp(f, 300, 314));
        return <Txt key={p.i} x={at} y={Y(spec.values[p.i]) - 18} anchor="center" v="bottom" o={o} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 24, color: P.cardinal, textShadow: HALO }}>{p.label}</Txt>;
      })}
    </Shell2>
  );
};

// ---- the clock: each grid's normal peak hour and its Thanksgiving peak hour --------------------------------------------
type CSSpec = Base & { rows: { label: string; normal: number; tg: number; normalText: string; tgText: string; shiftText: string }[]; legend: { normal: string; tg: string } };
export const ClockShift: React.FC<{ spec: CSSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const n = spec.rows.length;
  const axisY = top + 62, rowTop = axisY + 30, rowH = (bottom - rowTop) / n;
  const labW = 214, shiftW = 156;
  const t0 = L + labW + 14, t1 = R - shiftW - 18;
  const X = (he: number) => t0 + ((he - 0) / 24) * (t1 - t0);
  const ticks = [{ he: 6, t: "6 am" }, { he: 12, t: "noon" }, { he: 18, t: "6 pm" }, { he: 24, t: "midnight" }];
  return (
    <Shell2 spec={spec}>
      <div style={{ position: "absolute", left: t0, top: top - 4, display: "flex", gap: 30, alignItems: "center", fontSize: 22, opacity: ramp(f, 4, 18) }}>
        <span style={{ display: "flex", alignItems: "center", gap: 9 }}><span style={{ width: 18, height: 18, borderRadius: 9, background: P.mark, display: "inline-block" }} />{spec.legend.normal}</span>
        <span style={{ display: "flex", alignItems: "center", gap: 9 }}><span style={{ width: 18, height: 18, borderRadius: 9, background: P.cardinal, display: "inline-block" }} />{spec.legend.tg}</span>
      </div>
      <div style={{ position: "absolute", left: t0, top: axisY + 12, width: t1 - t0, height: 2, background: P.ink, opacity: ramp(f, 4, 18) }} />
      {ticks.map((t) => (
        <React.Fragment key={t.he}>
          <div style={{ position: "absolute", left: X(t.he) - 1, top: axisY + 4, width: 2, height: bottom - axisY - 4, background: P.rule, opacity: ramp(f, 4, 18) }} />
          <Txt x={X(t.he)} y={axisY - 2} anchor="center" v="bottom" o={ramp(f, 4, 18)} style={{ fontSize: 20, color: P.captions }}>{t.t}</Txt>
        </React.Fragment>
      ))}
      {spec.rows.map((r, i) => {
        const cy = rowTop + rowH * (i + 0.5);
        const appear = ramp(f, 16 + i * 10, 32 + i * 10);
        const st = 132 + i * 14, mv = ramp(f, st, st + 64, EIO);
        const xn = X(r.normal), xt = X(r.normal + (r.tg - r.normal) * mv);
        const done = ramp(f, st + 60, st + 74);
        const same = r.normal === r.tg;
        return (
          <React.Fragment key={r.label}>
            <Txt x={L} y={cy} v="middle" o={appear} style={{ fontSize: 27 }}>{r.label}</Txt>
            <div style={{ position: "absolute", left: t0, top: cy - 1, width: t1 - t0, height: 2, background: P.rule, opacity: appear }} />
            <div style={{ position: "absolute", left: Math.min(xn, xt), top: cy - 2, width: Math.abs(xn - xt), height: 4, background: P.cardinal, opacity: ramp(f, st, st + 6) }} />
            <div style={{ position: "absolute", left: xn - 11, top: cy - 11, width: 22, height: 22, borderRadius: 11, background: P.mark, opacity: appear }} />
            <div style={{ position: "absolute", left: xt - 12, top: cy - 12, width: 24, height: 24, borderRadius: 12, background: P.cardinal, border: `2px solid ${P.fog}`, boxSizing: "border-box", opacity: ramp(f, st - 12, st) }} />
            {!same && <Txt x={xn} y={cy + 15} anchor="center" o={done} style={{ fontSize: 18, color: P.captions }}>{r.normalText}</Txt>}
            <Txt x={X(r.tg)} y={cy + 15} anchor="center" o={done} style={{ fontSize: 18, color: P.cardinal }}>{r.tgText}</Txt>
            <Txt x={R} y={cy} anchor="right" v="middle" o={done} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 22, color: same ? P.captions : P.cardinal }}>{r.shiftText}</Txt>
          </React.Fragment>
        );
      })}
    </Shell2>
  );
};

// ---- two demand curves over the day ---------------------------------------------------------------------------------------
type CVSpec = Base & { caption: string; normal: number[]; tg: number[]; peaks: { normal: { he: number; label: string; text: string }; tg: { he: number; label: string; text: string } }; yMax: number; yTicks: { v: number; label: string }[]; yUnit: string; xTicks: { he: number; label: string }[] };
export const Curves: React.FC<{ spec: CVSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const pt = top + 52, base = bottom - 46;
  const x0 = L + 100, x1 = R - 50;
  const X = (he: number) => x0 + ((he - 1) / 23) * (x1 - x0);
  const Y = (v: number) => base - (v / spec.yMax) * (base - pt);
  const path = (vals: number[]) => vals.map((v, i) => `${i ? "L" : "M"}${X(i + 1).toFixed(2)},${Y(v).toFixed(2)}`).join(" ");
  const pn = ramp(f, 30, 140, EIO), ptg = ramp(f, 160, 280, EIO);
  const pk = (k: "normal" | "tg") => { const vals = spec[k], he = spec.peaks[k].he; return { x: X(he), y: Y(vals[he - 1]) }; };
  const a = pk("normal"), b = pk("tg");
  return (
    <Shell2 spec={spec}>
      <Txt x={L} y={top - 4} o={ramp(f, 4, 18)} style={{ fontSize: 23, color: P.ink }}>{spec.caption}</Txt>
      <svg style={{ position: "absolute", left: 0, top: 0 }} width={1080} height={spec.height}>
        <defs>
          <clipPath id={`cn-${spec.id}`}><rect x={x0 - 6} y={0} width={(x1 - x0 + 12) * pn} height={spec.height} /></clipPath>
          <clipPath id={`ct-${spec.id}`}><rect x={x0 - 6} y={0} width={(x1 - x0 + 12) * ptg} height={spec.height} /></clipPath>
        </defs>
        {spec.yTicks.map((t) => <line key={t.v} x1={x0 - 8} x2={x1 + 8} y1={Y(t.v)} y2={Y(t.v)} stroke={t.v === 0 ? P.ink : P.rule} strokeWidth={2} opacity={ramp(f, 4, 18)} />)}
        <path d={path(spec.normal)} fill="none" stroke={P.mark} strokeWidth={5} strokeLinejoin="round" clipPath={`url(#cn-${spec.id})`} />
        <path d={path(spec.tg)} fill="none" stroke={P.cardinal} strokeWidth={5} strokeLinejoin="round" clipPath={`url(#ct-${spec.id})`} />
        <circle cx={a.x} cy={a.y} r={10} fill={P.mark} stroke={P.fog} strokeWidth={3} opacity={ramp(f, 130, 140)} />
        <circle cx={b.x} cy={b.y} r={10} fill={P.cardinal} stroke={P.fog} strokeWidth={3} opacity={ramp(f, 270, 280)} />
      </svg>
      {spec.yTicks.map((t) => <Txt key={t.v} x={x0 - 16} y={Y(t.v)} anchor="right" v="middle" o={ramp(f, 4, 18)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 18, color: P.captions }}>{t.label}</Txt>)}
      {spec.xTicks.map((t) => <Txt key={t.he} x={X(t.he)} y={base + 12} anchor="center" o={ramp(f, 4, 18)} style={{ fontSize: 22 }}>{t.label}</Txt>)}
      <Txt x={a.x} y={a.y - 20} anchor="center" v="bottom" o={ramp(f, 136, 150)} style={{ textAlign: "center", textShadow: HALO }}>
        <div style={{ fontSize: 21, color: P.captions }}>{spec.peaks.normal.label}</div>
        <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 24, color: P.ink }}>{spec.peaks.normal.text}</div>
      </Txt>
      <Txt x={b.x} y={b.y + 20} anchor="center" v="top" o={ramp(f, 276, 290)} style={{ textAlign: "center", textShadow: HALO }}>
        <div style={{ fontSize: 21, color: P.cardinal }}>{spec.peaks.tg.label}</div>
        <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 24, color: P.cardinal }}>{spec.peaks.tg.text}</div>
      </Txt>
    </Shell2>
  );
};

// ---- one block standing for 100%, filled to the share year by year ----------------------------------------------------
type Step = { year: number; value: number; display: string };
const stepValue = (f: number, steps: Step[], t0: number, gap: number, dur: number, first: number) => {
  // value at frame f: 0 to the first step over [t0, t0+first], then each next step over its own window
  let v = steps[0].value * ramp(f, t0, t0 + first, EIO), k = 0;
  for (let i = 1; i < steps.length; i++) {
    const s = t0 + first + 10 + (i - 1) * gap;
    if (f >= s) k = i;
    v += (steps[i].value - steps[i - 1].value) * ramp(f, s, s + dur, EIO);
  }
  return { v, k };
};
type FBSpec = Base & { steps: Step[]; blockLabel: string; fillLabel: string };
export const FillBlock: React.FC<{ spec: FBSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const bw = 520, bh = bottom - top, bx = L, by = top;
  const { v, k } = stepValue(f, spec.steps, 40, 38, 24, 30);
  const fillH = (v / 100) * bh;
  const cur = spec.steps[k];
  const lx = bx + bw + 26;
  const showFirst = k >= 2;
  return (
    <Shell2 spec={spec}>
      <div style={{ position: "absolute", left: bx, top: by, width: bw, height: bh, background: P.fill, opacity: ramp(f, 4, 20) }} />
      <Txt x={bx + 18} y={by + 16} o={ramp(f, 8, 22)} style={{ fontSize: 28, color: P.ink }}>{spec.blockLabel}</Txt>
      <div style={{ position: "absolute", left: bx, top: by + bh - fillH, width: bw, height: fillH, background: P.cardinal }} />
      <Txt x={bx + 18} y={by + bh - fillH + 14} o={interpolate(fillH, [70, 90], [0, 1], cl)} style={{ fontSize: 26, color: P.fog }}>{spec.fillLabel}</Txt>
      <div style={{ position: "absolute", left: bx + bw, top: by + bh - fillH - 1, width: 18, height: 2, background: P.cardinal, opacity: ramp(f, 40, 50) }} />
      <Txt x={lx} y={by + bh - fillH} v="middle" o={ramp(f, 40, 52)} style={{ display: "flex", alignItems: "baseline", gap: 16 }}>
        <span style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 40 }}>{cur.year}</span>
        <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: 58, color: P.cardinal }}>{cur.display}</span>
      </Txt>
      <Txt x={lx} y={by + bh - 4} v="bottom" o={showFirst ? 1 : 0} style={{ display: "flex", alignItems: "baseline", gap: 12, color: P.captions }}>
        <span style={{ fontSize: 26 }}>{spec.steps[0].year}</span>
        <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: 28 }}>{spec.steps[0].display}</span>
      </Txt>
    </Shell2>
  );
};

// ---- a flow band whose thickness is the megawatts, narrowing year by year ------------------------------------------------
type FLSpec = Base & { steps: Step[]; fromLabel: string; toLabel: string };
export const FlowBand: React.FC<{ spec: FLSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const mx = Math.max(...spec.steps.map((s) => s.value));
  const tMax = (bottom - top) * 0.62, k = tMax / mx;
  const axis = top + 70 + tMax / 2 + ((bottom - top) - 70 - tMax) / 2;
  const bx0 = L + 150, bx1 = R - 190;
  const grow = ramp(f, 30, 70);
  const { v, k: idx } = stepValue(f, spec.steps, 40, 34, 22, 1);
  const T = v * k;
  const cur = spec.steps[idx];
  const ghost = idx >= 1 ? 1 : 0;
  const T0 = spec.steps[0].value * k;
  return (
    <Shell2 spec={spec}>
      <div style={{ position: "absolute", left: bx0, top: axis - T0 / 2, width: bx1 - bx0, height: T0, border: `2px dashed ${P.mark}`, boxSizing: "border-box", opacity: ghost }} />
      <div style={{ position: "absolute", left: bx0, top: axis - T / 2, width: (bx1 - bx0) * grow, height: T, background: P.cardinal }} />
      <Txt x={bx0 - 18} y={axis} anchor="right" v="middle" o={ramp(f, 6, 20)} style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 36 }}>{spec.fromLabel}</Txt>
      <Txt x={bx1 + 18} y={axis} anchor="left" v="middle" o={ramp(f, 6, 20)} style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 36 }}>{spec.toLabel}</Txt>
      <Txt x={bx0} y={axis - T / 2 - 12} v="bottom" o={ramp(f, 60, 72)} style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
        <span style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 36 }}>{cur.year}</span>
        <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: 44, color: P.cardinal }}>{cur.display}</span>
      </Txt>
      <Txt x={bx1} y={axis - T0 / 2 - 12} anchor="right" v="bottom" o={ghost} style={{ display: "flex", alignItems: "baseline", gap: 12, color: P.captions }}>
        <span style={{ fontSize: 26 }}>{spec.steps[0].year}</span>
        <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: 30 }}>{spec.steps[0].display}</span>
      </Txt>
    </Shell2>
  );
};

// ---- a staircase: the first year's level, each year's change, and the change since the first year in cardinal ----------
type SCSpec = Base & { base: { label: string; value: number; display: string }; steps: { label: string; from: number; to: number; delta: number; display: string }[]; total: { label: string; value: number; display: string }; max: number };
export const Staircase: React.FC<{ spec: SCSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const base = bottom - 62, span = base - top - 10;
  const n = spec.steps.length + 2, slot = W / n, cw = Math.min(82, slot * 0.68);
  const Y = (v: number) => base - (v / spec.max) * span;
  const cx = (i: number) => L + slot * (i + 0.5);
  const gb = ramp(f, 20, 60);
  const lastLevel = spec.steps[spec.steps.length - 1].to;
  return (
    <Shell2 spec={spec}>
      <div style={{ position: "absolute", left: L, top: base, width: W, height: 2, background: P.ink, opacity: ramp(f, 4, 18) }} />
      <div style={{ position: "absolute", left: cx(0) - cw / 2, top: base - (base - Y(spec.base.value)) * gb, width: cw, height: (base - Y(spec.base.value)) * gb, background: P.mark }} />
      <Txt x={cx(0)} y={Y(spec.base.value) - 10} anchor="center" v="bottom" o={ramp(f, 52, 66)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 20 }}>{spec.base.display}</Txt>
      <Txt x={cx(0)} y={base + 12} anchor="center" o={ramp(f, 20, 34)} style={{ fontSize: 24 }}>{spec.base.label}</Txt>
      <div style={{ position: "absolute", left: cx(0) + cw / 2, top: Y(spec.base.value) - 1, width: cx(n - 1) - cx(0) - cw, height: 0, borderTop: `2px dashed ${P.mark}`, opacity: ramp(f, 240, 256) }} />
      {spec.steps.map((s, i) => {
        const st = 70 + i * 26, g = ramp(f, st, st + 22);
        const yTop = Y(Math.max(s.from, s.to)), yBot = Y(Math.min(s.from, s.to));
        const x = cx(i + 1);
        return (
          <React.Fragment key={s.label}>
            <div style={{ position: "absolute", left: cx(i) + cw / 2, top: Y(s.from) - 1, width: slot - cw, height: 2, background: P.mark, opacity: g }} />
            <div style={{ position: "absolute", left: x - cw / 2, top: yTop, width: cw, height: Math.max(2, yBot - yTop), background: s.delta >= 0 ? P.mark : "transparent", border: s.delta >= 0 ? undefined : `2px solid ${P.mark}`, boxSizing: "border-box", opacity: g }} />
            <Txt x={x} y={yTop - 10} anchor="center" v="bottom" o={ramp(f, st + 12, st + 26)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 21 }}>{s.display}</Txt>
            <Txt x={x} y={base + 12} anchor="center" o={g} style={{ fontSize: 24 }}>{s.label}</Txt>
          </React.Fragment>
        );
      })}
      {(() => {
        const g = ramp(f, 240, 276), x = cx(n - 1);
        const y0 = Y(spec.base.value), y1 = Y(lastLevel);
        return (
          <>
            <div style={{ position: "absolute", left: x - cw / 2, top: y0 - (y0 - y1) * g, width: cw, height: (y0 - y1) * g, background: P.cardinal }} />
            <Txt x={x} y={y1 + 10} anchor="center" o={ramp(f, 266, 280)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 21, color: P.fog, textAlign: "center", lineHeight: 1.15 }}>
              <div>{spec.total.display.replace(/ MW$/, "")}</div><div>MW</div>
            </Txt>
            <Txt x={x} y={base + 12} anchor="center" o={ramp(f, 240, 254)} style={{ fontSize: 21, color: P.cardinal, textAlign: "center", lineHeight: 1.1 }}>{spec.total.label}</Txt>
          </>
        );
      })()}
    </Shell2>
  );
};

// ---- a grid of 100 squares, the share in cardinal (the last square filled by its fraction) ------------------------------
type WFSpec = Base & { steps: Step[]; unitText: string; squareNote: string; extra?: string };
export const Waffle: React.FC<{ spec: WFSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const avail = bottom - top, G = Math.min(avail, 548), gap = 6, cell = (G - 9 * gap) / 10;
  const gx = L, gy = top + (avail - G) / 2;
  const multi = spec.steps.length > 1;
  const { v, k } = multi ? stepValue(f, spec.steps, 30, 38, 24, 60) : { v: spec.steps[0].value * ramp(f, 40, 150, EIO), k: 0 };
  const cur = spec.steps[k];
  const rx = gx + G + 46;
  return (
    <Shell2 spec={spec}>
      {Array.from({ length: 100 }, (_, i) => {
        const r = Math.floor(i / 10), c = i % 10, fr = Math.max(0, Math.min(1, v - i));
        const x = gx + c * (cell + gap), y = gy + r * (cell + gap);
        return (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: x, top: y, width: cell, height: cell, background: P.fill, opacity: ramp(f, 4 + r * 2, 16 + r * 2) }} />
            {fr > 0 && <div style={{ position: "absolute", left: x, top: y, width: cell * fr, height: cell, background: P.cardinal }} />}
          </React.Fragment>
        );
      })}
      <Txt x={rx} y={gy - 6} o={ramp(f, 30, 44)} style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 48 }}>{String(cur.year)}</Txt>
      <Txt x={rx} y={gy + 58} o={ramp(f, 30, 44)} style={{ fontFamily: MONO, fontWeight: 500, fontSize: 76, color: P.cardinal }}>{cur.display}</Txt>
      <Txt x={rx} y={gy + 158} o={ramp(f, 30, 44)} style={{ fontSize: 27 }}>{spec.unitText}</Txt>
      {spec.extra && <Txt x={rx} y={gy + 204} o={ramp(f, 150, 166)} style={{ fontSize: 22, color: P.captions, whiteSpace: "normal", width: R - rx }}>{spec.extra}</Txt>}
      {multi && (
        <Txt x={rx} y={gy + 232} o={k >= 2 ? 1 : 0} style={{ display: "flex", alignItems: "baseline", gap: 12, color: P.captions }}>
          <span style={{ fontSize: 26 }}>{spec.steps[0].year}</span>
          <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: 30 }}>{spec.steps[0].display}</span>
        </Txt>
      )}
      <Txt x={rx} y={gy + G} v="bottom" o={ramp(f, 10, 24)} style={{ fontSize: 20, color: P.captions, whiteSpace: "normal", width: R - rx }}>{spec.squareNote}</Txt>
    </Shell2>
  );
};

// ---- the ladder: one cardinal column rising past each earlier year's level -------------------------------------------------
type LDSpec = Base & { lead: { label: string; sub: string; value: number; display: string }; rows: { label: string; value: number; display: string }[]; max: number };
export const Ladder2: React.FC<{ spec: LDSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const H = spec.height, { top, bottom } = zone(H);
  const base = bottom - 4, span = base - top - 20;
  const Y = (v: number) => base - (v / spec.max) * span;
  const colX = L, colW = 236, lineX0 = colX + colW + 26, labelX = 690;
  const rise = ramp(f, 120, 320, EIO);
  const now = spec.lead.value * rise;
  const order = [...spec.rows].sort((p, q) => p.value - q.value);
  const minGap = H > 1080 ? 46 : 40;
  const ly: number[] = [];
  order.forEach((r, k) => { const want = Y(r.value); ly.push(k === 0 ? Math.min(want, base - 26) : Math.min(want, ly[k - 1] - minGap)); });
  const shown = rise >= 1 ? spec.lead.display : `${Math.round(now).toLocaleString("en-US")} MW`;
  return (
    <Shell2 spec={spec}>
      <div style={{ position: "absolute", left: colX, top: base, width: W, height: 2, background: P.ink, opacity: ramp(f, 6, 20) }} />
      {order.map((r, k) => {
        const g = ramp(f, 20 + k * 12, 40 + k * 12);
        const passed = now >= r.value;
        const yy = Y(r.value);
        return (
          <React.Fragment key={r.label}>
            <div style={{ position: "absolute", left: lineX0, top: yy - 1, width: labelX - lineX0 - 70, height: 2, background: passed ? P.mark : P.rule, opacity: g }} />
            <svg style={{ position: "absolute", left: 0, top: 0, opacity: g }} width={1080} height={H}>
              <polyline points={`${labelX - 70},${yy} ${labelX - 22},${ly[k]} ${labelX - 8},${ly[k]}`} fill="none" stroke={passed ? P.mark : P.rule} strokeWidth={2} />
            </svg>
            <Txt x={labelX} y={ly[k]} v="middle" o={g} style={{ display: "flex", alignItems: "baseline" }}>
              <span style={{ fontSize: 28, width: 110 }}>{r.label}</span>
              <span style={{ fontFamily: MONO, fontWeight: 500, fontSize: 28, width: R - labelX - 110, textAlign: "right" }}>{r.display}</span>
            </Txt>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: colX, top: Y(now), width: colW, height: base - Y(now), background: P.cardinal }} />
      <div style={{ position: "absolute", left: colX + 16, width: colW - 24, top: Y(now) + 14, opacity: interpolate(base - Y(now), [150, 190], [0, 1], cl), color: P.fog }}>
        <div style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 40, lineHeight: 1.05 }}>{spec.lead.label}</div>
        <div style={{ fontSize: 22, lineHeight: 1.2, marginTop: 4, color: "#E9CFCB" }}>{spec.lead.sub}</div>
        <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 34, marginTop: 6, whiteSpace: "nowrap" }}>{shown}</div>
      </div>
    </Shell2>
  );
};

// ---- proportional blocks of a whole, the lead block in cardinal at the left --------------------------------------------
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
    const row = [areas[i]]; let j = i + 1;
    while (j < areas.length && worst([...row, areas[j]], side) <= worst(row, side)) { row.push(areas[j]); j++; }
    const s = row.reduce((a, b) => a + b, 0);
    if (rw >= rh) { const cw = s / rh; let cy = ry; row.forEach((a, k) => { const ch = a / cw; out.push({ i: i + k, x: rx, y: cy, w: cw, h: ch }); cy += ch; }); rx += cw; rw -= cw; }
    else { const ch = s / rw; let cx = rx; row.forEach((a, k) => { const cw = a / ch; out.push({ i: i + k, x: cx, y: ry, w: cw, h: ch }); cx += cw; }); ry += ch; rh -= ch; }
    i = j;
  }
  return out;
}
type TMSpec = Base & { items: { label: string; value: number; display: string; lead?: boolean; countText?: string }[]; leadSub: string };
export const Treemap: React.FC<{ spec: TMSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { top, bottom } = zone(spec.height);
  const h = bottom - top, total = spec.items.reduce((a, b) => a + b.value, 0);
  const lead = spec.items.find((x) => x.lead)!, rest = spec.items.filter((x) => !x.lead);
  const leadW = (W * lead.value) / total;           // the same area scale as the rest: a full-height column
  const cells = squarify(rest.map((x) => x.value), L + leadW, top, W - leadW, h);
  const boxes = [{ it: lead, x: L, y: top, w: leadW, h }, ...cells.map((c) => ({ it: rest[c.i], x: c.x, y: c.y, w: c.w, h: c.h }))];
  return (
    <Shell2 spec={spec}>
      {boxes.map((b, k) => {
        const isLead = !!b.it.lead;
        const st = isLead ? 24 : 80 + (k - 1) * 20;
        const g = ramp(f, st, st + 24);
        const w = b.w - 4, hh = b.h - 4;
        const longest = Math.max(...b.it.label.split(" ").map((s) => s.length), 6);
        const fs = Math.max(16, Math.min(isLead ? 34 : 30, (w - 28) / (0.56 * longest)));
        const rise = isLead ? ramp(f, 24, 70, EIO) : 1;
        const ink = isLead ? P.fog : P.ink;
        return (
          <div key={b.it.label} style={{ position: "absolute", left: b.x + 2, top: b.y + 2 + hh * (1 - rise), width: w, height: hh * rise, background: isLead ? P.cardinal : P.fill, opacity: isLead ? 1 : g, transform: isLead ? undefined : `scale(${0.96 + 0.04 * g})`, transformOrigin: "top left", overflow: "hidden", color: ink }}>
            <div style={{ position: "absolute", left: 14, top: 12, right: 8 }}>
              <div style={{ fontFamily: isLead ? SERIF : SANS, fontWeight: isLead ? 600 : 400, fontSize: fs, lineHeight: 1.12 }}>{b.it.label}</div>
              {isLead && <div style={{ fontSize: 21, lineHeight: 1.25, marginTop: 6, color: "#E9CFCB" }}>{spec.leadSub}</div>}
              <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: isLead ? 46 : fs * 1.1, marginTop: 6 }}>{b.it.display}</div>
              {b.it.countText && <div style={{ fontSize: Math.max(18, fs * 0.72), marginTop: 2, color: P.captions }}>{b.it.countText}</div>}
            </div>
          </div>
        );
      })}
    </Shell2>
  );
};

export const Batch2: React.FC<{ spec: any }> = ({ spec }) => {
  switch (spec.type) {
    case "columns": return <Columns spec={spec} />;
    case "yearline": return <YearLine spec={spec} />;
    case "weekline": return <WeekLine spec={spec} />;
    case "clockshift": return <ClockShift spec={spec} />;
    case "curves": return <Curves spec={spec} />;
    case "fillblock": return <FillBlock spec={spec} />;
    case "flowband": return <FlowBand spec={spec} />;
    case "staircase": return <Staircase spec={spec} />;
    case "waffle": return <Waffle spec={spec} />;
    case "ladder2": return <Ladder2 spec={spec} />;
    case "treemap": return <Treemap spec={spec} />;
    default: return null;
  }
};
export const BATCH2_TYPES = ["columns", "yearline", "weekline", "clockshift", "curves", "fillblock", "flowband", "staircase", "waffle", "ladder2", "treemap"];
