"use client";

// Session 152: a chart that answers the mouse. Any mark inside that carries data-tip shows its words in a small box
// beside the pointer (or under a finger, or on keyboard focus), at once. The charts of /demand are drawn on the
// server as SVG; this wraps one and adds nothing to its numbers: the words are the mark's own.
import { useRef, useState, type FocusEvent, type MouseEvent, type ReactNode, type TouchEvent } from "react";

type Tip = { x: number; y: number; width: number; text: string };
const BOX = 230;  // the widest the box is drawn, px

export function Hover({ children }: { children: ReactNode }) {
  const box = useRef<HTMLDivElement>(null);
  const [tip, setTip] = useState<Tip | null>(null);
  const show = (target: EventTarget | null, clientX: number, clientY: number) => {
    const mark = target instanceof Element ? target.closest("[data-tip]") : null;
    const frame = box.current?.getBoundingClientRect();
    if (!mark || !frame) { setTip(null); return; }
    setTip({ x: clientX - frame.left, y: clientY - frame.top, width: frame.width, text: mark.getAttribute("data-tip") ?? "" });
  };
  const onMove = (e: MouseEvent) => show(e.target, e.clientX, e.clientY);
  const onTouch = (e: TouchEvent) => { const t = e.touches[0]; if (t) show(e.target, t.clientX, t.clientY); };
  const onFocus = (e: FocusEvent) => { const r = (e.target as Element).getBoundingClientRect(); show(e.target, r.left + r.width / 2, r.top + r.height / 2); };
  return (
    <div ref={box} className="relative" data-hover="1" onMouseMove={onMove} onMouseLeave={() => setTip(null)} onTouchStart={onTouch} onFocus={onFocus} onBlur={() => setTip(null)}>
      {children}
      {tip ? (
        <div role="tooltip" data-tooltip="1" className="pointer-events-none absolute z-10 border border-rule bg-white px-2 py-1 text-xs leading-snug text-ink shadow"
          style={{ left: Math.max(0, Math.min(tip.x + 12, tip.width - BOX)), top: tip.y + 14, maxWidth: BOX }}>{tip.text}</div>
      ) : null}
    </div>
  );
}
