"use client";
// Session 2201 (chain 086): the hover card of the brand's bar chart (components/tool/GroupedBars.tsx). The chart is
// drawn on the server as plain SVG and its only hover was a <title> a group, the browser's own tooltip: late, unstyled
// and nothing on a phone or from the keyboard. This wraps the SVG as it is (its figure, its patterns and its direct
// labels unchanged) and draws the brand's card (docs/brand.md, section 6: fog with a rule-colored edge, the period in
// sans, each series named in its own color with its figure in mono) for the group under the pointer, or the group a
// keyboard reader moves to (the chart takes focus; the left and right arrows move the card, Escape hides it). The words
// of each card come from the server, already written, so no number is computed here; the <title> stays for a reader
// with no script. Every color is a token (the series' colors are the chart's own CSS variables).
import { useState, type KeyboardEvent, type MouseEvent, type ReactNode } from "react";

export type BarCard = { label: string; sub?: string; lines: { name: string; color: string; text: string }[] };

export function BarsHover({ id, cards, left, right, width, children }: {
  id: string; cards: BarCard[];
  /** the plot's left and right edges and the drawing's width, in the SVG's own units (its viewBox) */
  left: number; right: number; width: number; children: ReactNode;
}) {
  const [at, setAt] = useState<number | null>(null);
  const n = cards.length;
  const groupAt = (e: MouseEvent<HTMLDivElement>) => {
    const svg = e.currentTarget.querySelector("svg");
    if (!svg || n === 0) return null;
    const r = svg.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * width;
    if (x < left || x > width - right) return null;
    const i = Math.floor(((x - left) / (width - right - left)) * n);
    return i >= 0 && i < n ? i : null;
  };
  const onKey = (e: KeyboardEvent<HTMLDivElement>) => {
    if (n === 0) return;
    if (e.key === "ArrowRight") { setAt((v) => (v === null ? 0 : Math.min(n - 1, v + 1))); e.preventDefault(); }
    else if (e.key === "ArrowLeft") { setAt((v) => (v === null ? n - 1 : Math.max(0, v - 1))); e.preventDefault(); }
    else if (e.key === "Home") { setAt(0); e.preventDefault(); }
    else if (e.key === "End") { setAt(n - 1); e.preventDefault(); }
    else if (e.key === "Escape") setAt(null);
  };
  const card = at !== null ? cards[at] : null;
  // the card's left edge in the chart's box: the group's middle in page pixels is not known here (the SVG scales with
  // its frame), so the card sits at the group's share of the width, kept inside the box
  const pct = at !== null && n > 0 ? ((left + ((at + 0.5) / n) * (width - right - left)) / width) * 100 : 0;
  return (
    <div className="relative" data-bars-hover={id} tabIndex={0} role="group" aria-roledescription="bar chart with a hover card"
      aria-label="Bar chart: the left and right arrows read each group's figures; Escape hides them"
      onMouseMove={(e) => setAt(groupAt(e))} onMouseLeave={() => setAt(null)} onKeyDown={onKey} onBlur={() => setAt(null)}>
      {children}
      {card ? (
        <div className="pointer-events-none absolute top-6 z-10 border border-rule bg-paper px-3 py-2 text-xs" style={{ left: `min(max(0%, calc(${pct}% + 10px)), calc(100% - 240px))` }} data-chart-card="1" aria-live="polite">
          <div className="text-ink">{card.label}{card.sub ? <span className="ml-1 text-muted">{card.sub}</span> : null}</div>
          {card.lines.map((l) => (
            <div key={l.name} className="flex justify-between gap-4"><span style={{ color: l.color }}>{l.name}</span><span className="font-mono text-ink">{l.text}</span></div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
