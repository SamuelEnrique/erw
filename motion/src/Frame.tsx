// The frame every motion video shares: the kicker, the title and subtitle, the body, the source line and the mark.
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, SANS, SERIF } from "./brand";
import type { Base } from "./types";

export const PAD = 72;

// The E in the cardinal square (docs/brand.md: a white stem and three bars of 14, 11 and 17 units).
const Mark: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden>
    <rect width="24" height="24" fill={C.cardinal} />
    <rect x="4" y="3" width="3" height="18" fill="#FFFFFF" />
    <rect x="4" y="3" width="14" height="3" fill="#FFFFFF" />
    <rect x="4" y="10.5" width="11" height="3" fill="#FFFFFF" />
    <rect x="4" y="18" width="17" height="3" fill="#FFFFFF" />
  </svg>
);

export const Frame: React.FC<{ spec: Base; children: React.ReactNode }> = ({ spec, children }) => {
  const f = useCurrentFrame();
  const fade = (from: number) => interpolate(f, [from, from + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const square = spec.height <= spec.width;
  return (
    <AbsoluteFill style={{ backgroundColor: C.page, padding: PAD, display: "flex", flexDirection: "column", fontFamily: SANS, color: C.ink }}>
      <div style={{ opacity: fade(0), fontSize: 24, letterSpacing: 1.5, textTransform: "uppercase", color: C.captions, fontWeight: 500 }}>{spec.kicker}</div>
      <div style={{ opacity: fade(4), fontFamily: SERIF, fontWeight: 600, fontSize: square ? 56 : 64, lineHeight: 1.1, marginTop: 18 }}>{spec.title}</div>
      <div style={{ opacity: fade(10), fontSize: square ? 27 : 30, lineHeight: 1.3, color: C.captions, marginTop: 14 }}>{spec.subtitle}</div>
      <div style={{ flex: 1, position: "relative", marginTop: 28 }}>{children}</div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 24, marginTop: 20, borderTop: `1px solid ${C.rule}`, paddingTop: 16 }}>
        <div style={{ flex: 1, fontSize: 19, lineHeight: 1.35, color: C.captions }}>{spec.source}</div>
        <Mark size={44} />
      </div>
    </AbsoluteFill>
  );
};

/** A number in the house style: thousands separated, the decimals the chart gives. */
export const fmt = (v: number, decimals: number) =>
  v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

/** Round tick values covering [lo, hi]. */
export function ticks(lo: number, hi: number, n = 4): number[] {
  if (hi === lo) return [lo];
  const raw = (hi - lo) / n;
  const p = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * p).find((s) => s >= raw) ?? 10 * p;
  const out: number[] = [];
  // from the tick at or below lo to the tick at or above hi, so the top value always has a gridline above it
  for (let t = Math.floor(lo / step) * step; t < hi + step - 1e-9; t += step) out.push(Math.round(t / step) * step);
  return out;
}
