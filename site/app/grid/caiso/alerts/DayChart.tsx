"use client";
// Energy Research Warehouse (ERW) site, session 1412 (chain 107): one small chart of the Flex Alert scorecard ("Each alert
// day through the evening"), now answering a hover. The drawing is session 60's, unchanged (lib/alertDayChart.ts holds
// its arithmetic word for word: the same viewBox, scale, points and colors, demand served in cardinal, the model's
// prediction dashed, its 90 percent band shaded, the alert hours boxed). What is added is drawn only while a card is open:
// a dashed guide at the hour and a dot on each line, and the shared charts' card (components/svgchart.tsx `Card`: fog,
// a rule-colored edge, the hour in sans, each figure in mono) with the hour on the Pacific clock as the axis writes it,
// demand served, the model's estimate and its band in MW, and the estimate less demand (the page's sign: a positive
// number is a cut). The card's figures are the chart's own points (rows of flex_alert_effects the page hands), not
// written figures: they carry no key, as no shared chart's card does.
//
// A mouse: the card follows the pointer to the nearest hour and goes when it leaves. A finger (session 1158's rules for
// cards): a tap opens the card at the nearest hour, the finger lifting leaves it open, a tap on the same hour or anywhere
// off the chart closes it.
import { useEffect, useRef, useState, type PointerEvent } from "react";
import { Card, num } from "@/components/svgchart";
import { B, Hh, W, dayGeometry, hourCard, nearestHour, type HourPoint } from "@/lib/alertDayChart";

type Hover = { h: number; left: number; width: number };

export function DayChart({ points, ariaLabel }: { points: HourPoint[]; ariaLabel: string }) {
  const g = dayGeometry(points);
  const wrap = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState<Hover | null>(null);
  useEffect(() => {
    if (!hover) return;
    const off = (e: globalThis.PointerEvent) => { if (wrap.current && !wrap.current.contains(e.target as Node)) setHover(null); };
    document.addEventListener("pointerdown", off);
    return () => document.removeEventListener("pointerdown", off);
  }, [hover]);
  if (!g) return null;
  const { hs, by, x, y, step, lo, hi, band, alertHs, actual, predicted, ticks } = g;
  const at = (e: PointerEvent<SVGSVGElement>): Hover => {
    const r = e.currentTarget.getBoundingClientRect();
    const h = nearestHour(hs, x, ((e.clientX - r.left) / (r.width || 1)) * W);
    return { h, left: (x(h) / W) * r.width, width: r.width };
  };
  const touch = (e: PointerEvent<SVGSVGElement>) => e.pointerType === "touch" || e.pointerType === "pen";
  const c = hover ? hourCard(by.get(hover.h) ?? {}, hover.h) : null;
  const mw0 = (v: number) => num(Math.round(v) || 0, 0);   // a whole MW, never "-0"
  const mw = (v: number | undefined) => (v === undefined ? <span className="font-sans text-muted">not held</span> : <>{mw0(v)} MW</>);
  return (
    <div ref={wrap} className="relative" data-alert-day-chart="1">
      <svg viewBox={`0 0 ${W} ${Hh}`} className="h-auto w-full" role="img" aria-label={ariaLabel}
        onPointerMove={(e) => { if (!touch(e)) setHover(at(e)); }}
        onPointerDown={(e) => { if (!touch(e)) return; const n = at(e); setHover((o) => (o && o.h === n.h ? null : n)); }}
        onPointerLeave={(e) => { if (!touch(e)) setHover(null); }}>
        {alertHs.map((h) => <rect key={h} x={x(h) - step / 2} y={2} width={step} height={Hh - B - 2} fill="var(--color-panel)" stroke="var(--color-rule)" strokeWidth={0.4} />)}
        <polygon points={band} fill="var(--color-rule)" opacity={0.7} />
        <path d={predicted} fill="none" stroke="var(--color-muted)" strokeWidth={1.2} strokeDasharray="3 2" />
        <path d={actual} fill="none" stroke="var(--color-accent)" strokeWidth={1.6} />
        <text x={2} y={10} fontSize={8} fill="var(--color-muted)">{Math.round(hi / 1000)} GW</text>
        <text x={2} y={Hh - B} fontSize={8} fill="var(--color-muted)">{Math.round(lo / 1000)} GW</text>
        {ticks.map((h) => <text key={h} x={x(h)} y={Hh - 4} fontSize={8} textAnchor="middle" fill="var(--color-muted)">{h}:00</text>)}
        {hover && c ? (
          <g data-alert-day-hover={hover.h} pointerEvents="none">
            <line x1={x(hover.h)} x2={x(hover.h)} y1={2} y2={Hh - B} stroke="var(--color-muted)" strokeWidth={0.6} strokeDasharray="2 2" />
            {c.predicted !== undefined ? <circle cx={x(hover.h)} cy={y(c.predicted)} r={1.8} fill="var(--color-muted)" /> : null}
            {c.actual !== undefined ? <circle cx={x(hover.h)} cy={y(c.actual)} r={2} fill="var(--color-accent)" /> : null}
          </g>
        ) : null}
      </svg>
      {hover && c ? (
        <Card left={hover.left + 8} width={hover.width}>
          <div className="text-ink">{c.hour} Pacific{c.alert ? ", an alert hour" : ""}</div>
          <div className="flex justify-between gap-4"><span style={{ color: "var(--color-accent)" }}>Demand served</span><span className="font-mono text-ink">{mw(c.actual)}</span></div>
          <div className="flex justify-between gap-4"><span className="text-muted">Model&apos;s estimate</span><span className="font-mono text-ink">{mw(c.predicted)}</span></div>
          {c.lo !== undefined && c.hi !== undefined ? (
            <div className="flex justify-between gap-4"><span className="text-muted">90 percent band</span><span className="font-mono text-ink">{mw0(c.lo)} to {mw0(c.hi)}</span></div>
          ) : null}
          {c.diff !== undefined ? (
            <div className="flex justify-between gap-4"><span className="text-muted">Estimate less demand</span><span className="font-mono text-ink">{mw0(c.diff)} MW</span></div>
          ) : null}
        </Card>
      ) : null}
    </div>
  );
}
