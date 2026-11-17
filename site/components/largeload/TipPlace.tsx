"use client";
// Chain 305 (session 7600, the browser read of 16 November 2026, rows 1 and 2): where the hovers of the large-load
// rules are drawn. A hover's box here holds a document's words and its cite, so it is wide, and its trigger stands
// inside a table that scrolls sideways. Placed by the style sheet alone (under its trigger, inside the table's frame),
// a box near the frame's bottom or right edge was cut by the frame, which grew scroll bars; one whose trigger stood in
// the right third of the window ran past the window's edge; and at 390 px nearly every box of the tables did (144 of
// 147 measured). This places the open box against the window, where no frame cuts it: under its trigger where it fits,
// above where there is more room, never past an edge (lib/largeloadrules.ts, placeTip). It listens once for the whole
// page and draws nothing. Without it (before the page's script has loaded) the style sheet's placing stands.
import { useEffect } from "react";
import { placeTip } from "@/lib/largeloadrules";

// Which hovers it places. The large-load rules' (any tip inside [data-llr]), for which it was written; and, since the
// same session read the old laptop's four pages at 390 px (docs/state/browser_reads_wanted.md, rows 1, 7, 9, 10 and 12),
// the site's shared "i" mark (components/tool/ToolPage.tsx, Tip: span.tip[data-tip]). That mark's box is 288 px wide and
// opened from the mark's left edge, so on a phone a mark right of the first 100 px had its box run past the screen and
// the page grew a sideways scroll while it was open: every "Decisions on this page" fold did it, and at 1280 px so did a
// mark in a page's right column. It is mounted once, in the site's layout. The All grids hub table's own tips (Tp,
// placed by the tab's style sheet since session 714) and the charts' hovers are not its.
const TIP = "[data-llr] span.tip, span.tip[data-tip]";
const BOX = ':scope > [role="tooltip"]';

export function TipPlace() {
  useEffect(() => {
    let open: HTMLElement | null = null;
    const box = (tip: HTMLElement) => tip.querySelector<HTMLElement>(BOX);
    const place = (tip: HTMLElement) => {
      const b = box(tip), trigger = tip.querySelector<HTMLElement>(":scope > button") ?? tip;
      if (!b) return;
      // measured as the style sheet sizes it, with no limit of ours left on it from the last time
      b.style.position = "fixed"; b.style.right = "auto"; b.style.bottom = "auto"; b.style.left = "0px"; b.style.top = "0px"; b.style.maxHeight = "";
      b.style.width = ""; b.style.maxWidth = "";
      let size = b.getBoundingClientRect();
      if (!size.width || !size.height) return;                // not shown: nothing to place
      // Session 7602 (browser reads rows 52 and 62): a box too tall for the room above or below its mark at its own
      // width (a decision's source of over 1,000 characters) is made wider where the window allows, up to 576 px, so
      // it is read whole and not in a scrolled box; on a phone there is no width to give, and it scrolls as before
      const tb = trigger.getBoundingClientRect(), vw = document.documentElement.clientWidth;
      const room = Math.max(window.innerHeight - 8 - (tb.bottom + 2), tb.top - 2 - 8);
      const wide = Math.min(576, vw - 16);
      if (size.height > room && wide > size.width + 24) {
        b.style.width = `${wide}px`; b.style.maxWidth = "none";
        size = b.getBoundingClientRect();
      }
      // a headline's mark (components/tool/ToolPage.tsx, HeadlineNumber) opens above it: under it stands the figure
      const prefer = tip.closest('[data-tip-open="above"]') ? "above" : "below";
      const p = placeTip(trigger.getBoundingClientRect(), { width: size.width, height: size.height }, { width: document.documentElement.clientWidth, height: window.innerHeight }, 8, 2, prefer);
      b.style.left = `${p.left}px`; b.style.top = `${p.top}px`; b.style.maxHeight = `${p.maxHeight}px`; b.style.overflowY = "auto";
      b.setAttribute("data-tp-placed", p.above ? "above" : "below");
      open = tip;
    };
    const inBox = (t: EventTarget | null) => !!(t instanceof Element && t.closest('[role="tooltip"]'));
    const over = (e: Event) => {
      const tip = e.target instanceof Element ? e.target.closest<HTMLElement>(TIP) : null;
      // the mouse moving on into the open box itself (to scroll a long one) leaves it where it is
      if (tip && !(tip === open && inBox(e.target))) place(tip);
    };
    // the page or a table's frame scrolled under an open box: it follows its trigger, or closes with the hover. The
    // box's own scroll (a long cite) moves nothing
    const moved = (e: Event) => {
      if (inBox(e.target)) return;
      if (open && open.isConnected && open.matches(":hover, :focus-within")) place(open); else open = null;
    };
    document.addEventListener("pointerover", over, true);
    document.addEventListener("focusin", over, true);
    document.addEventListener("scroll", moved, { capture: true, passive: true });
    window.addEventListener("resize", moved);
    return () => {
      document.removeEventListener("pointerover", over, true);
      document.removeEventListener("focusin", over, true);
      document.removeEventListener("scroll", moved, true);
      window.removeEventListener("resize", moved);
    };
  }, []);
  return null;
}
