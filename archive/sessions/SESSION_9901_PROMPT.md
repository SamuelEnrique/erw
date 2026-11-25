# SESSION 9901: ERW video posts, batch 2 (nine posts, two chart options each, three shapes)

Run on the desktop (`C:\Users\Shared\Documents\erw`). Unattended. Samuel reviews the results afterward and picks one option per post.

## 0. Why this session exists (read first)

Session 9900 rendered nine posts and Samuel rejected all of them. Two reasons, in his words:

1. Every video reused the chart type of the first post (ranked rows). "The graphic type itself CANNOT BE THE SAME EVERY TIME."
2. Titles were cheesy. Titles are plain and descriptive, like the first post's "Grid connection requests withdrawn, filed 2000-2020". The joke belongs in the post copy, which Samuel writes himself.

On Nov 24 the NVIDIA post was rebuilt in chat with a new chart type (proportional blocks), iterated with Samuel, approved and posted on LinkedIn, X and Instagram. That post is the reference for what he wants. Its code is in section 2 of this file. This session builds the other nine posts to that standard, with two different chart options per post so Samuel can choose and not iterate.

## 1. Hard rules

- **Accuracy is the whole game.** Every number comes from an ERW table with a named original source. Re-derive each post's numbers before drawing them. If a number cannot be verified, do not render that post; say why in the report. Never invent, estimate or pad.
- **Proportions are exact.** Areas, lengths and heights are in exact proportion to the values. Bars, columns and areas start at zero. If a line chart does not start at zero, say so in the report.
- **Nothing is posted, published or merged.** Work on a branch (section 7). Do not touch `main`, the site, Supabase or Redivis.
- **USD 0.** No paid API calls, no Claude API calls. Free public data sources only, within their terms.
- **No em dashes** in any text you write: titles, labels, source lines, the review page, the report.
- **Do not change** `motion/src/Post.tsx` (the first post's template) or anything about the first post or the NVIDIA post beyond what section 2 says.
- **You cannot ask questions in this run.** Where something is unclear, take the conservative reading, keep going, and list it under "Open questions for Samuel" in the report. Samuel's standing rule is to ask before doing a task you do not understand, so anything that would change what a chart claims goes on that list and the affected option is marked "needs ruling" on the review page.
- **Commit and push after every post** (the chain worker closes a session that goes 30 minutes without a commit).

## 2. Starting code: the approved NVIDIA post

Start from branch `wip/linkedin-posts-2026-11-24`. The files below exist only in the chat sandbox, so create them exactly as given.

### 2a. `motion/src/Jensen.tsx` (create verbatim)

````tsx
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
````

### 2b. `motion/src/Root.tsx` (edit)

Add `import { Blocks, Ladder } from "./Jensen";` and route by spec type before the existing cases:

```tsx
(spec as any).type === "blocks" ? <Blocks spec={spec as any} /> : (spec as any).type === "ladder" ? <Ladder spec={spec as any} /> : /* existing routing for "post" and the rest */
```

### 2c. `motion/specs/posts/nvidia_energy_blocks.json` (create verbatim)

````json
{
 "id": "nvidia_energy_blocks",
 "type": "blocks",
 "width": 1080,
 "height": 1080,
 "frames": 450,
 "title": "NVIDIA’s one-day gain exceeds several U.S. energy sectors",
 "source": "Source: SEC filings (shares outstanding, latest report) and closing prices of 23 November 2026 (StockAnalysis.com). Market value of U.S.-headquartered listed companies above $5 billion ($1 billion for renewables). The number in each box is its count of companies.",
 "lead": {
  "label": "NVIDIA",
  "sub": "market value gained on Nov\u00a023",
  "value": 952.4320000000002
 },
 "rows": [
  {
   "label": "Utilities",
   "value": 1314.0749175026401,
   "count": 40,
   "countText": "40 companies"
  },
  {
   "label": "Integrated Majors",
   "value": 1045.24099046622,
   "count": 2,
   "countText": "2"
  },
  {
   "label": "Midstream",
   "value": 555.48383034596,
   "count": 13,
   "countText": "13"
  },
  {
   "label": "Upstream",
   "value": 541.61867751147,
   "count": 17,
   "countText": "17"
  },
  {
   "label": "Power Equipment",
   "value": 460.64873617148004,
   "count": 8,
   "countText": "8"
  },
  {
   "label": "Downstream",
   "value": 312.36621267705,
   "count": 6,
   "countText": "6"
  },
  {
   "label": "Power Producers",
   "value": 166.94303446865,
   "count": 4,
   "countText": "4"
  },
  {
   "label": "Oilfield Services",
   "value": 156.41666686035998,
   "count": 6,
   "countText": "6"
  },
  {
   "label": "Renewables",
   "value": 51.666281051895005,
   "count": 9,
   "countText": "9"
  }
 ],
 "_numbers_from": "/home/claude/jensen/data/caps_included_floor1.csv (SEC cover pages; StockAnalysis.com closes of 2026-11-23)",
 "showPct": false
}
````

### 2d. Regression check before anything else

Render the last frame of `nvidia_energy_blocks.json` at 1080x1080 and at 1080x1350 (scale 2) and open the images. They must show:

- "ERW Research" at top left (ERW in cardinal serif, Research in sans).
- Title on two lines: "NVIDIA’s one-day gain exceeds / several U.S. energy sectors".
- A full-height cardinal block at the left reading "NVIDIA", "market value gained on Nov 23", "$952B".
- Nine grey blocks: Utilities $1.31T "40 companies", Integrated Majors $1.05T "2", Midstream $555B "13", Upstream $542B "17", Power Equipment $461B "8", Downstream $312B "6", Power Producers $167B "4", Oilfield Services $156B "6", Renewables $52B "9".
- No percentages anywhere. A three-line source line under a thin rule.

If it does not match, fix the transcription before continuing. Do not re-render or re-publish the NVIDIA post itself; it is already posted.

## 3. The format (fixed across every video)

Samuel's definition: a 15-second video, the right amount of motion, "ERW Research" at the top left the same across videos, the dimensions, the source at the end, and the general style of the graphics. The chart type is NOT part of the format and must vary.

- **Length:** 450 frames at 30 fps.
- **Look:** fog page `#F7F3EA`, rule `#E3DED1`, captions `#6B675F`, ink `#2E2D29`, cardinal `#8C1515`, neutral marks `#9A958B`, neutral fills `#E3DED1`. Source Serif 4 600 for the header word "ERW" and the title, IBM Plex Sans 400 for text, IBM Plex Mono 500 for every number.
- **Header:** "ERW Research" at left 72, top 64, as in `Shell`.
- **Title:** 62px serif at top 126, at most two lines. Plain and descriptive. Include the period covered when the chart is a time series.
- **Source line:** 21px, captions grey, at most three lines, under the rule at `H - 196`. It fades in at frames 368 to 382 and holds to the end. It names the original source, the ERW table, and any definition the reader needs.
- **One cardinal element per chart:** the thing the title is about. Everything else is neutral.
- **Motion:** calm. Marks appear in a sensible order (chronological, or largest first), with `Easing.out(Easing.cubic)`. No bounce, no camera moves, no spinning. All chart motion ends by about frame 330. The last 2 seconds are still.
- **NEW, approved today: the header and title are fully visible from frame 0.** Remove their fade-in in `Shell` for all new posts. The first frame is what X and Instagram can show as a cover, so it must never be an empty page.

### Lessons from the NVIDIA iterations (apply to every chart)

- Text sits inside its mark or directly attached to it. If it does not fit, change the layout or the type size; never let text spill outside or get clipped. Open every still and look.
- Category names are in Title Case ("Power Equipment"). Write "U.S." with periods. Use the curved apostrophe (’), not the straight one.
- Do not print a second number that the picture already shows. Samuel removed the percentages from the NVIDIA chart because the box sizes already said it.
- Numbers carry their unit ($952B, 1,992 MW, 46.6%).
- If a count or a definition helps the reader judge a number, show it small and grey, and explain it in the source line.
- No text under 15px at 1080 scale unless a mark is too small for anything else. List every exception in the report.
- A thing that is a different kind of quantity from the others gets its own separate mark (NVIDIA's gain was a gain, not a market cap, so it stood apart from the grid).

## 4. Three shapes for every video

| Platform | Canvas at scale 1 | Rendered at scale 2 | Notes |
|---|---|---|---|
| LinkedIn | 1080 x 1350 | 2160 x 2700 | Lay out for this shape. |
| X | 1080 x 1080 | 2160 x 2160 | Lay out for this shape. |
| Instagram | 1080 x 1920 | 2160 x 3840 | Full vertical for Reels. |

For Instagram, place the 1080 x 1350 layout on a 1080 x 1920 fog canvas, shifted down 200px from the top, so all content sits between y = 200 and y = 1550. Instagram covers the top and bottom of the screen with its own buttons and caption, and the feed crops a vertical video toward its center. This safe area is a design assumption, not a measured fact; record it in the report.

Each shape is checked on its own still. A layout that works at 1080 x 1350 can clip at 1080 x 1080.

Every video ships with a thumbnail: its final frame as a PNG at the same size.

## 5. The nine posts

For each post build **option A and option B: two different chart types, the same title, the same numbers, the same source line.** Neither option is the ranked-rows chart of the first post. The types below are the plan Samuel saw. If the data makes a planned type impossible or misleading, build the closest honest alternative and say so on the review page.

Build in this order, so the time-sensitive ones exist first.

| # | Post id | Proposed plain title | Option A | Option B |
|---|---|---|---|---|
| 1 | `thanksgiving_peak_hour` | Hour of peak power demand, Thanksgiving vs normal days | A 24-hour axis per region with two dots: the normal peak hour (grey) and the Thanksgiving peak hour (cardinal). The cardinal dot slides from evening to late morning. | Two demand curves over 24 hours for one large region: a normal late-November Thursday (grey) and Thanksgiving (cardinal), with each peak marked. |
| 2 | `thanksgiving_gasoline` (Black Friday) | U.S. gasoline price on Thanksgiving week, 2020-2026 | One line of the weekly U.S. regular gasoline price from 2020 to now, drawn left to right, with a dot and price label on each Thanksgiving week. | Seven columns, one per Thanksgiving week 2020 to 2026, with the price on each and 2026 in cardinal. |
| 3 | `caiso_battery_peak` | California batteries as a share of peak demand, 2019-2025 | One large block standing for peak-day demand, with a cardinal area filling it year by year while the year and share count up. | An area chart of the share by year, 2019 to 2025, with the first and last values labelled. |
| 4 | `canada_new_york_flow` | Power flow from Canada to New York, 2019-2025 | A flow band running from "Canada" to "New York" whose thickness is in proportion to the megawatts, narrowing year by year. | Seven columns by year, shrinking, with megawatts on each and 2025 in cardinal. |
| 5 | `dominion_mean_hour` | Electricity demand in Dominion's Virginia zone, 2019-2025 | A staircase: the 2019 level as a grey base, with each year's change added as a step and the total added since 2019 in cardinal. | One line by year with the first and last values labelled. |
| 6 | `ercot_solar_tight_hours` | Solar output in Texas's tightest grid hours, 2019-2025 | A grid of 100 squares where the cardinal squares are the share, stepping through the years from 71 squares to 5. | One line by year, falling, with the first and last values labelled. |
| 7 | `texas_cold_peak` | Texas peak power demand in late January, 2020-2026 | One cardinal column rising past labelled year levels (the `Ladder` idea in `Jensen.tsx`), ending at the 2026 level. | Seven columns by year with megawatts on each and 2026 in cardinal. |
| 8 | `uranium_us_origin` | U.S.-origin uranium bought for U.S. reactors, 2003-2025 | Proportional blocks (the `Blocks` idea) of the latest year's purchases by country of origin, with the U.S. block in cardinal. Only if the ERW table holds origin by country; otherwise a grid of 100 squares for the latest year. | One line of the U.S.-origin share by year across the whole period, with the first and last values labelled. |
| 9 | `us_share_world_oil` | U.S. share of world oil and liquids production, 1995-2025 | Proportional blocks of world production in the latest year by country, with the U.S. block in cardinal. Only if the ERW table holds production by country; otherwise a grid of 100 squares. | One area chart of the U.S. share by year across the whole period, with the first and last values labelled. |

Titles are proposals. Keep them plain, fix any that run past two lines, and make sure each one says exactly what the data is (for example, if post 3 measures installed battery power against peak demand, say that).

### Numbers already verified in chat on Nov 24 (use these as a check on your own re-derivation)

**Post 1, Thanksgiving peak hour (EIA-930, 2019 to 2025, median):** Plains 7 pm to 10 am (9 hours earlier). Midwest 6 pm to 11 am Central (7). Mid-Atlantic 7 pm to noon (7). New York 6 pm to 1 pm (5). Texas 4 pm to noon (4). New England 6 pm to 3 pm (3). California 0 hours: its midday peaks in 2024 and 2025 are battery charging counted as demand, so if California is shown, the source line must say so. The baseline definition is in `docs/research/motion/posts/data/thanksgiving_peak_hour_*.csv` and the Nov 24 note; restate it in the source line.

**Post 2, gasoline (EIA weekly U.S. regular retail price, the Monday of Thanksgiving week):** 2020 $2.10, 2021 $3.40, 2022 $3.65, 2023 $3.29, 2024 $3.04, 2025 $3.06, 2026 $3.64 (EIA's Nov 23, 2026 value is $3.642). 2026 is NOT a record: 2022 was $3.648. Do not write "record" or "highest" anywhere. The spec on the branch may still hold an older 2026 value; fix it.

If your re-derived numbers differ from these, do not pick one silently. Report both and mark the post "needs ruling".

## 6. How to work each post

1. **Verify the numbers.** Re-run the reproduce notes under `docs/research/motion/posts/data/` against the ERW tables. Write the final values to a small data file for the post, with the ERW table and original source for each.
2. **Build option A and option B** as Remotion components in the approved look. Reuse `Shell`. Put shared pieces in one file so the nine posts stay consistent.
3. **Render the final frame of both options in all three shapes** and open every PNG. Check: title at most two lines; source at most three lines; no clipped, overlapping or spilling text; one cardinal element; numbers match the data file digit for digit; proportions exact.
4. **Render four evenly spaced frames** of each option (square is enough) and open them, to check that the motion reads and that frame 0 already shows the header and title.
5. Fix and repeat until every still is clean. Then render the six videos (two options, three shapes) and their six thumbnails.
6. Commit and push.

Be honest with yourself at step 3. Session 9900 failed because nobody looked at the result with Samuel's eyes. Ask of each still: is this interesting to look at, would a partner at a fund stop scrolling for it, and is every number right?

## 7. Deliverables

Branch: create `wip/linkedin-posts-2026-11-25` from `wip/linkedin-posts-2026-11-24`. Commit as you go. Push after every post. Do not merge.

- **Videos and thumbnails:** `docs/research/motion/posts/batch_2026-11-25/<post_id>/<post_id>_<a|b>_<linkedin|x|ig>.mp4` and the matching `..._thumb.png`.
- **One comparison image per post:** `docs/reviews/linkedin/img/batch_2026-11-25/<post_id>_options.png`, showing the square final frames of A and B side by side, labelled A and B.
- **Review page:** `docs/reviews/linkedin/posts-2026-11-25.md`. For each post: the title, the finding in one plain sentence, every number with its ERW table and original source, the two chart types, any caveat, and "ready" or "needs ruling".
- **Report:** `archive/sessions/SESSION_9901_REPORT.md`. What was built, what was skipped and why, every text-size exception, the Instagram safe-area assumption, numbers that differed from section 5, and "Open questions for Samuel".
- Also save this prompt as `archive/sessions/SESSION_9901_PROMPT.md`.

Stop when all nine posts are done or blocked. A post with one clean option and one blocked option still ships, marked as such.
