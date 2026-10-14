// Draw-on: a line (or bar) chart drawn over its x axis, left to right; the lead series' newest value rides the head, and
// every series is named at its end when the drawing is done (direct labels, no legend).
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { C, MONO, SANS, SERIES } from "./brand";
import { fmt, PAD, ticks } from "./Frame";
import type { DrawOn as Spec } from "./types";

const bodySize = (s: Spec) => ({ w: s.width - 2 * PAD, h: s.height - 2 * PAD - (s.height > s.width ? 300 : 280) - 100 });

export const DrawOn: React.FC<{ spec: Spec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { w, h } = bodySize(spec);
  const m = { l: 112, r: spec.series.some((x) => x.axis !== "left" && !x.bar) ? 300 : 250, t: 50, b: 76 };
  const pw = w - m.l - m.r;
  const ph = h - m.t - m.b;
  const n = spec.x.length;
  const xAt = (i: number) => m.l + (n <= 1 ? 0 : (i / (n - 1)) * pw);
  const left = spec.series.filter((s) => s.axis === "left");
  const vals = left.flatMap((s) => s.values.filter((v): v is number => v !== null));
  let lo = Math.min(...vals);
  let hi = Math.max(...vals);
  if (lo >= 0 && lo < 0.4 * hi) lo = 0;
  const tk = ticks(lo, hi, 4);
  lo = Math.min(lo, tk[0]);
  hi = Math.max(hi, tk[tk.length - 1]);
  const yLeft = (v: number) => m.t + ph - ((v - lo) / (hi - lo || 1)) * ph;
  // the first series off the left axis has a right axis of its own, with its own round ticks
  const right = spec.series.find((s) => s.axis !== "left" && !s.bar);
  const rv = right ? right.values.filter((v): v is number => v !== null) : [];
  const rt = right ? ticks(Math.min(0, ...rv), Math.max(...rv), 4) : [];
  const rlo = rt.length ? rt[0] : 0;
  const rhi = rt.length ? rt[rt.length - 1] : 1;
  const yRight = (v: number) => m.t + ph - ((v - rlo) / (rhi - rlo || 1)) * ph;
  const scaleOf = (s: Spec["series"][number]) => {
    if (s.axis === "left") return yLeft;
    if (s === right) return yRight;
    const vs = s.values.filter((v): v is number => v !== null);
    const a = Math.min(0, ...vs);
    const b = Math.max(...vs);
    return (v: number) => m.t + ph - ((v - a) / (b - a || 1)) * ph * (s.bar ? 0.35 : 1);
  };

  const p = interpolate(f, [24, spec.frames - 80], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const k = p * (n - 1);
  const done = interpolate(f, [spec.frames - 75, spec.frames - 55], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const pathOf = (s: Spec["series"][number]) => {
    const y = scaleOf(s);
    let d = "";
    let pen = false;
    for (let i = 0; i <= Math.min(Math.floor(k) + 1, n - 1); i++) {
      const v = s.values[i];
      if (v === null || v === undefined) { pen = false; continue; }
      let x = xAt(i);
      let yy = y(v);
      if (i > k) {   // the last segment, drawn to the head
        const prev = s.values[i - 1];
        if (prev === null || prev === undefined) break;
        const t = k - (i - 1);
        x = xAt(i - 1) + (xAt(i) - xAt(i - 1)) * t;
        yy = y(prev) + (y(v) - y(prev)) * t;
      }
      d += `${pen ? "L" : "M"}${x.toFixed(1)},${yy.toFixed(1)} `;
      pen = true;
    }
    return d;
  };

  const xTicks = (() => {
    const longest = Math.max(...spec.x.map((v) => v.length));
    const want = Math.max(2, Math.min(n, Math.floor(pw / (longest * 13 + 40))));
    const idx = new Set<number>();
    for (let j = 0; j < want; j++) idx.add(Math.round((j / Math.max(want - 1, 1)) * (n - 1)));
    return [...idx];
  })();

  const lead = spec.series[0];
  const headI = Math.min(Math.round(k), n - 1);
  const headV = lead.values[headI];

  // end labels, nudged apart
  const ends = spec.series.map((s, i) => {
    let j = n - 1;
    while (j > 0 && (s.values[j] === null || s.values[j] === undefined)) j--;
    const v = s.values[j] as number;
    return { i, y: scaleOf(s)(v), v, s };
  }).sort((a, b) => a.y - b.y);
  const lines = (name: string) => {   // a series' name in at most two lines of about 19 characters, cut at a word
    const words = name.split(" ");
    const out = [""];
    for (const w of words) {
      if ((out[out.length - 1] + " " + w).trim().length > 19 && out[out.length - 1]) out.push(w);
      else out[out.length - 1] = (out[out.length - 1] + " " + w).trim();
    }
    return out.length > 2 ? [out[0], out[1] + "..."] : out;
  };
  const one = spec.series.length === 1;   // one series: the title names it; the label is its value and unit
  const gap = one ? 40 : 82;
  for (let j = 1; j < ends.length; j++) if (ends[j].y - ends[j - 1].y < gap) ends[j].y = ends[j - 1].y + gap;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="100%" preserveAspectRatio="xMidYMid meet" style={{ fontFamily: SANS }}>
      {spec.band && (
        <g opacity={k >= spec.band.from ? interpolate(k, [spec.band.from, spec.band.from + 0.6], [0, 1], { extrapolateRight: "clamp" }) : 0}>
          <rect x={xAt(spec.band.from)} y={m.t} width={Math.max(xAt(spec.band.to) - xAt(spec.band.from), 4)} height={ph} fill={C.fog} />
          <text x={xAt(spec.band.from) + 8} y={m.t + 26} fontSize={22} fill={C.captions}>{spec.band.label}</text>
        </g>
      )}
      {tk.map((t) => (
        <g key={t}>
          <line x1={m.l} x2={m.l + pw} y1={yLeft(t)} y2={yLeft(t)} stroke={t === 0 ? C.ink : C.rule} strokeWidth={t === 0 ? 1.5 : 1} />
          <text x={m.l - 14} y={yLeft(t) + 8} fontSize={22} fill={C.captions} textAnchor="end">{fmt(t, Math.abs(hi - lo) < 10 ? 1 : 0)}</text>
        </g>
      ))}
      <text x={0} y={16} fontSize={20} fill={C.captions}>{spec.yLabel}</text>
      {right && rt.map((t) => (
        <text key={"r" + t} x={m.l + pw + 8} y={yRight(t) + 7} fontSize={19} fill={SERIES[spec.series.indexOf(right)]}>{fmt(t, 0)}</text>
      ))}
      {xTicks.map((i) => (
        <text key={i} x={xAt(i)} y={m.t + ph + 34} fontSize={22} fill={C.captions} textAnchor={i === 0 ? "start" : i === n - 1 ? "end" : "middle"}>{spec.x[i]}</text>
      ))}
      <text x={m.l + pw / 2} y={m.t + ph + 66} fontSize={20} fill={C.captions} textAnchor="middle">{spec.xLabel}</text>
      {spec.series.map((s, i) => s.bar ? (
        <g key={s.name}>
          {s.values.map((v, j) => (v === null || j > k) ? null : (
            <rect key={j} x={xAt(j) - Math.max(pw / n / 2 - 1, 1)} width={Math.max(pw / n - 2, 2)} y={scaleOf(s)(v)} height={m.t + ph - scaleOf(s)(v)} fill={SERIES[Math.min(i, SERIES.length - 1)]} opacity={0.35} />
          ))}
        </g>
      ) : (
        <path key={s.name} d={pathOf(s)} fill="none" stroke={SERIES[Math.min(i, SERIES.length - 1)]} strokeWidth={i === 0 ? 5 : 3} strokeLinejoin="round" strokeLinecap="round" />
      ))}
      {headV !== null && headV !== undefined && done < 1 && (
        <g opacity={1 - done}>
          <circle cx={xAt(k)} cy={scaleOf(lead)(headV)} r={8} fill={C.cardinal} />
          <text x={Math.min(xAt(k) + 14, m.l + pw + 10)} y={scaleOf(lead)(headV) - 14} fontSize={28} fontFamily={MONO} fontWeight={500} fill={C.cardinal}>{fmt(headV, spec.decimals)}</text>
          <text x={Math.min(xAt(k) + 14, m.l + pw + 10)} y={scaleOf(lead)(headV) + 18} fontSize={20} fill={C.captions}>{spec.x[headI]}</text>
        </g>
      )}
      <g opacity={done}>
        {ends.map(({ i, y, v, s }) => (
          <g key={s.name}>
            {one ? null : lines(s.name).map((ln, j) => (
              <text key={j} x={m.l + pw + (right ? 74 : 14)} y={y + j * 24} fontSize={21} fill={SERIES[Math.min(i, SERIES.length - 1)]} fontWeight={600}>{ln}</text>
            ))}
            <text x={m.l + pw + (right ? 74 : 14)} y={y + (one ? 0 : lines(s.name).length * 24 + 4)} fontSize={one ? 30 : 22} fontFamily={MONO} fontWeight={500} fill={one ? C.cardinal : C.ink}>
              {fmt(v, spec.decimals)}{s.unit ? ` ${s.unit}` : ""}
            </text>
            {one ? <text x={m.l + pw + (right ? 74 : 14)} y={y + 28} fontSize={21} fill={C.captions}>{spec.yLabel}</text> : null}
          </g>
        ))}
      </g>
    </svg>
  );
};
