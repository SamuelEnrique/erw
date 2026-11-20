// Energy Research Warehouse (ERW): the LinkedIn post template, approved by Samuel on 17 November 2026.
// A ranked list where all rows stay on screen. The highlight walks down the rows; the active row grows
// (serif label, thick cardinal bar, large cardinal number) while the others make room. After the last row
// it holds, then the chart settles into equal rows with nothing highlighted and the source fades in.
// Header "ERW Research": ERW in cardinal serif, Research in ink sans, optically centered. No character.
// Works at 1080 x 1080 (approved) and 1080 x 1350; render at scale 2 for a sharp 2160 px master.
import React from "react";
import "@fontsource/source-serif-4/600.css";
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import { AbsoluteFill, continueRender, delayRender, Easing, interpolate, interpolateColors, useCurrentFrame } from "remotion";

const SERIF = '"Source Serif 4"';
const SANS = '"IBM Plex Sans"';
const MONO = '"IBM Plex Mono"';
const P = { fog: "#F7F3EA", rule: "#E3DED1", captions: "#6B675F", ink: "#2E2D29", cardinal: "#8C1515", bar: "#9A958B" };
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

if (typeof document !== "undefined") {
  const h = delayRender("post fonts");
  Promise.all(['600 64px "Source Serif 4"', '400 24px "IBM Plex Sans"', '500 24px "IBM Plex Mono"'].map((f) => document.fonts.load(f))).then(() => continueRender(h));
}

export type PostSpec = {
  id: string; type: "post"; width: number; height: number; frames: number;
  title: string; source: string; rows: { label: string; value: number }[]; decimals?: number;
};

export const Post: React.FC<{ spec: PostSpec }> = ({ spec }) => {
  const f = useCurrentFrame();
  const rows = spec.rows;
  const n = rows.length;
  const dec = spec.decimals ?? 1;
  const fade = (from: number) => interpolate(f, [from, from + 12], [0, 1], cl);
  const ease = Easing.inOut(Easing.cubic);
  // timing (30 fps): rows in 0.5 to 1.5 s; highlight walk from 2.1 s, 1.33 s a row; hold 1.2 s on the last row
  const start = 64, per = 40;
  const k = (f - start) / per;
  let pos = -1;
  if (f >= start) { const i = Math.min(n - 1, Math.floor(k)); const t = Math.min(1, (k - i) / 0.4); pos = i - 1 + ease(t); }
  const landed = start + (n - 1) * per + 16;
  const compAt = landed + 36;
  const c = interpolate(f, [compAt, compAt + 20], [0, 1], { ...cl, easing: ease });          // settle into equal rows
  const src = interpolate(f, [compAt + 12, compAt + 26], [0, 1], { ...cl, easing: Easing.out(Easing.cubic) });
  // layout: the chart fills the frame while it plays; after settling, the rule and source take the bottom
  const H = spec.height, tall = H > 1080, K = tall ? 1.15 : 1;
  const top = tall ? 320 : 290, big = 168 * K, base = (H - 70 - top - big) / 6;
  const labelW = 390 * (tall ? 1.08 : 1), numW = 180 * (tall ? 1.06 : 1), barMax = 1080 - 144 - labelW - numW - 24;
  const ruleY = H - 196, hf = (ruleY - 34 - top) / n;
  let y = top;
  return (
    <AbsoluteFill style={{ backgroundColor: P.fog, fontFamily: SANS, color: P.ink }}>
      <div style={{ position: "absolute", left: 72, top: 64, opacity: fade(0), display: "flex", alignItems: "baseline", gap: 10, lineHeight: 1 }}>
        <span style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 34, color: P.cardinal }}>ERW</span>
        {/* lifted 2.5 px: the lowercase pulls the word's visual center below the capitals of ERW */}
        <span style={{ fontFamily: SANS, fontWeight: 400, fontSize: 32.5, color: P.ink, position: "relative", top: -2.5 }}>Research</span>
      </div>
      <div style={{ position: "absolute", left: 72, right: 72, top: 126, opacity: fade(4), fontFamily: SERIF, fontWeight: 600, fontSize: 62, lineHeight: 1.1 }}>{spec.title}</div>
      {rows.map((r, i) => {
        const on0 = Math.max(0, 1 - Math.abs(pos - i));
        const on = on0 * (1 - c);
        const h = (base + (big - base) * on0) * (1 - c) + hf * c;
        const ry = y; y += h;
        const g = interpolate(f, [16 + i * 5, 40 + i * 5], [0, 1], { ...cl, easing: Easing.out(Easing.cubic) });
        const barH = ((14 + 22 * on0) * (1 - c) + 24 * c) * K;
        return (
          <div key={r.label} style={{ position: "absolute", left: 72, right: 72, top: ry, height: h, display: "flex", alignItems: "center", opacity: interpolate(f, [12 + i * 4, 26 + i * 4], [0, 1], cl) }}>
            <div style={{ width: labelW, fontFamily: on > 0.5 ? SERIF : SANS, fontWeight: on > 0.5 ? 600 : 400, fontSize: ((28 + 16 * on0) * (1 - c) + 33 * c) * K, whiteSpace: "nowrap" }}>{r.label}</div>
            <div style={{ width: barMax, height: barH, background: P.rule, position: "relative", marginLeft: 12 }}>
              <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${r.value * g}%`, background: interpolateColors(on, [0, 1], [P.bar, P.cardinal]) }} />
            </div>
            <div style={{ width: numW, textAlign: "right", fontFamily: MONO, fontWeight: 500, fontSize: ((28 + 26 * on0) * (1 - c) + 35 * c) * K, color: interpolateColors(on, [0, 1], [P.ink, P.cardinal]), fontVariantNumeric: "tabular-nums", opacity: g }}>
              {r.value.toFixed(dec)}%
            </div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 72, right: 72, top: ruleY, height: 2, background: P.rule, opacity: src }} />
      <div style={{ position: "absolute", left: 72, right: 72, top: ruleY + 30, fontSize: 21, lineHeight: 1.42, color: P.captions, opacity: src, transform: `translateY(${(1 - src) * 12}px)` }}>{spec.source}</div>
    </AbsoluteFill>
  );
};
