// Count-up, roll call and reorder: the other three motion types.
import React from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, MONO, SANS, SERIF } from "./brand";
import { fmt } from "./Frame";
import type { CountUp as CountSpec, Reorder as ReorderSpec, RollCall as RollSpec } from "./types";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Count-up: the headline number counts from zero to its value, then the finding's own sentence beneath it. */
export const CountUp: React.FC<{ spec: CountSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [18, 150], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const square = spec.height <= spec.width;
  return (
    <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%" }}>
      <div style={{ fontFamily: SERIF, fontWeight: 600, fontSize: square ? 190 : 220, color: C.cardinal, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>
        {fmt(spec.value * t, spec.decimals)}
      </div>
      <div style={{ fontSize: square ? 34 : 38, marginTop: 18, color: C.ink, opacity: interpolate(f, [60, 80], [0, 1], clamp) }}>{spec.unit}</div>
      <div style={{ fontSize: square ? 27 : 30, lineHeight: 1.4, marginTop: 40, color: C.ink, maxWidth: 900, opacity: interpolate(f, [160, 185], [0, 1], clamp) }}>
        {spec.sentence}
      </div>
    </div>
  );
};

/** Roll call: a list where each row takes the frame in turn while the list scrolls behind it. */
export const RollCall: React.FC<{ spec: RollSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const intro = 40;
  const per = Math.floor((spec.frames - intro - 70) / spec.rows.length);
  const at = Math.max(0, Math.min(spec.rows.length - 1, Math.floor((f - intro) / per)));
  // the list moves to the active row with a spring, from the row before it
  const s = spring({ frame: Math.max(0, f - intro - at * per), fps, config: { damping: 18, mass: 0.6 } });
  const pos = at === 0 ? s * 0 : at - 1 + s;
  const rowH = spec.height > spec.width ? 128 : 104;
  const center = spec.height > spec.width ? 300 : 210;
  return (
    <div style={{ position: "relative", height: "100%", overflow: "hidden" }}>
      <div style={{ fontSize: 24, color: C.captions, marginBottom: 6 }}>{spec.measure}</div>
      {spec.rows.map((r, i) => {
        const d = Math.abs(i - pos);
        const on = Math.max(0, 1 - d);
        const y = center + (i - pos) * rowH;
        return (
          <div key={r.label} style={{ position: "absolute", left: 0, right: 0, top: y, height: rowH, display: "flex", alignItems: "center", gap: 28,
            opacity: interpolate(d, [0, 2.5], [1, 0.28], clamp) * interpolate(f, [0, 20], [0, 1], clamp) }}>
            <div style={{ flex: 1, fontFamily: on > 0.5 ? SERIF : SANS, fontWeight: on > 0.5 ? 600 : 400, fontSize: 30 + 22 * on, color: C.ink }}>{r.label}</div>
            <div style={{ width: 300, height: 14, background: C.fog, position: "relative" }}>
              <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${(100 * Math.max(r.value, 0)) / (spec.max || 1)}%`, background: on > 0.5 ? C.cardinal : C.captions }} />
            </div>
            <div style={{ width: 210, textAlign: "right", fontFamily: MONO, fontWeight: 500, fontSize: 30 + 18 * on, color: on > 0.5 ? C.cardinal : C.ink }}>
              {fmt(r.value, spec.decimals)}{spec.unit}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/** Reorder: ranked bars that move from one ranking to another as their values change. */
export const Reorder: React.FC<{ spec: ReorderSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [150, 300], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const n = spec.labels.length;
  const value = (i: number) => spec.before.values[i] + (spec.after.values[i] - spec.before.values[i]) * t;
  const rank = (vs: number[]) => {
    const order = vs.map((v, i) => [v, i] as const).sort((a, b) => b[0] - a[0]).map(([, i]) => i);
    const r = new Array(n);
    order.forEach((i, k) => (r[i] = k));
    return r as number[];
  };
  const r0 = rank(spec.before.values);
  const r1 = rank(spec.after.values);
  const all = [...spec.before.values, ...spec.after.values];
  const lo = Math.min(0, ...all);
  const hi = Math.max(0, ...all);
  const rowH = (spec.height > spec.width ? 760 : 520) / n;
  const barW = spec.width - 2 * 72 - 300 - 176;   // the label column (300) and the value column (176) beside it
  const x = (v: number) => ((v - lo) / (hi - lo || 1)) * barW;
  return (
    <div style={{ position: "relative", height: "100%" }}>
      <div style={{ fontSize: 26, color: C.captions, marginBottom: 10 }}>
        <span style={{ color: t < 0.5 ? C.ink : C.captions, fontWeight: t < 0.5 ? 600 : 400 }}>{spec.before.name}</span>
        {"  to  "}
        <span style={{ color: t >= 0.5 ? C.cardinal : C.captions, fontWeight: t >= 0.5 ? 600 : 400 }}>{spec.after.name}</span>
      </div>
      <div style={{ position: "absolute", top: 74, left: 0, right: 0 }}>
        <div style={{ position: "absolute", left: 300 + x(0), top: 0, height: n * rowH, width: 2, background: C.ink }} />
        {spec.labels.map((label, i) => {
          const y = (r0[i] + (r1[i] - r0[i]) * t) * rowH;
          const v = value(i);
          const a = x(Math.min(0, v));
          const b = x(Math.max(0, v));
          return (
            <div key={label} style={{ position: "absolute", top: y, left: 0, right: 0, height: rowH, display: "flex", alignItems: "center",
              opacity: interpolate(f, [10 + i * 3, 30 + i * 3], [0, 1], clamp) }}>
              <div style={{ width: 286, flexShrink: 0, fontSize: 24, color: C.ink, textAlign: "right", paddingRight: 14, lineHeight: 1.1 }}>{label}</div>
              <div style={{ position: "relative", width: barW, flexShrink: 0, height: rowH * 0.62 }}>
                <div style={{ position: "absolute", left: a, width: Math.max(b - a, 2), top: 0, bottom: 0, background: t < 0.5 ? C.ink : C.cardinal }} />
              </div>
              <div style={{ width: 162, flexShrink: 0, fontFamily: MONO, fontSize: 24, paddingLeft: 14, color: C.ink }}>{fmt(v, spec.decimals)}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", right: 0, bottom: 0, fontSize: 22, color: C.captions }}>{spec.unit}</div>
    </div>
  );
};
