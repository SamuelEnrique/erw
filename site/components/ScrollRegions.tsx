"use client";
// Session 412 (the accessibility pass, docs/reviews/accessibility-2026-10-20.md): a table or a block of code wider than
// its frame scrolls inside it (docs/brand.md, section 5), and AccessLint found seven on the pages, at 1280 px, that a
// keyboard could not scroll (WCAG 2.1.1: the battery's and the generator's tables, the cost of power's chart table, the
// contracts, demand by year, the shoulder hours' worst days, the package's install line on /data); at 390 px every wide
// table is one. One component for the site, mounted once in the layout, so a fix lands on every page: each
// scrolling box under <main> that holds nothing the keyboard can reach is made one stop of the keyboard (tabindex 0),
// a region named for what it holds (its table's caption, else its figure's or section's title), and is put back as it
// was when it no longer scrolls. The arrow keys then scroll it. Nothing is drawn; the brand's focus ring shows on it
// (app/tokens.css, data-scroll-focus). A box that already holds a link or a control is left alone: Tab reaches it.
import { usePathname } from "next/navigation";
import { useEffect } from "react";

// Session 583 (docs/reviews/accessibility-2026-10-22.md): two more kinds of box scroll by the stylesheet, not by a class,
// and AccessLint found them at 390 px that the keyboard could not reach: a chart's figure on a phone (app/tokens.css,
// section "charts": the year chart keeps its width and scrolls inside its frame; /shoulder, /storage, demand growth,
// the datacenters' grids) and a table of rendered markdown (app/globals.css, .prose-erw table: the digest, the roundup,
// /data/licenses, the resources map's file list). Each is marked only while it scrolls, as every other box is.
export const SCROLLERS = "main .overflow-x-auto, main .overflow-auto, main .overflow-x-scroll, main pre, main figure, main .prose-erw table";
export const FOCUSABLE = 'a[href], button:not([disabled]), input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';

/** What a scrolling box is called: its table's caption, else the title of its figure or section, else plain words. */
export function regionName(el: HTMLElement): string {
  const pick = (n: Element | null | undefined) => (n?.textContent ?? "").replace(/\s+/g, " ").trim();
  const caption = pick(el.querySelector("caption"));
  if (caption) return caption;
  const fig = pick(el.closest("figure")?.querySelector("figcaption"));
  if (fig) return fig;
  const heading = pick(el.closest("section, details")?.querySelector("h2, h3, summary"));
  if (heading) return heading;
  return el.tagName === "PRE" ? "Code" : "Table";
}

export function markScrollers(root: ParentNode = document) {
  // session 428: every box's sizes are read first and the attributes written after, so the browser lays the page out
  // once, not once a box (a write between two reads forced a new layout: Lighthouse's forced reflow)
  const boxes = [...root.querySelectorAll<HTMLElement>(SCROLLERS)].map((el) => ({
    el, scrolls: el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1,
  }));
  boxes.forEach(({ el, scrolls }) => {
    const ours = el.dataset.scrollFocus === "1";
    const reachable = !!el.querySelector(FOCUSABLE);
    if (scrolls && !reachable && !ours && !el.hasAttribute("tabindex")) {
      el.tabIndex = 0;
      el.dataset.scrollFocus = "1";
      // session 583: a figure is a stop of the keyboard and nothing more: it is already a figure named by its caption,
      // and the role of a region is not allowed on it (AccessLint, aria-allowed-role, after the first pass of the fix)
      if (el.tagName === "FIGURE") return;
      if (!el.hasAttribute("role")) { el.setAttribute("role", "region"); el.dataset.scrollRole = "1"; }
      if (!el.hasAttribute("aria-label") && !el.hasAttribute("aria-labelledby")) { el.setAttribute("aria-label", regionName(el)); el.dataset.scrollLabel = "1"; }
    } else if (ours && (!scrolls || reachable)) {
      el.removeAttribute("tabindex");
      delete el.dataset.scrollFocus;
      if (el.dataset.scrollRole) { el.removeAttribute("role"); delete el.dataset.scrollRole; }
      if (el.dataset.scrollLabel) { el.removeAttribute("aria-label"); delete el.dataset.scrollLabel; delete el.dataset.scrollName; }
    }
  });
  uniqueNames(root);
}

/** Session 583: two regions of one page never share a name (AccessLint, landmark-unique: at 390 px two tables under one
 *  heading, "Reliability" on the grid pages, or the research cards' "Method, the table of estimates", were two regions
 *  of one name, which a screen reader's list of regions cannot tell apart). A name this script or the server's
 *  scrollRegion() gave (data-scroll-label) takes its place among those that share it, "Reliability, 2 of 2"; the first
 *  words stay the table's own. A name a page wrote itself is never changed. */
export function uniqueNames(root: ParentNode = document) {
  const groups = new Map<string, HTMLElement[]>();
  root.querySelectorAll<HTMLElement>('[role="region"][aria-label], section[aria-label]').forEach((el) => {
    const key = (el.dataset.scrollName ?? el.getAttribute("aria-label") ?? "").trim().toLowerCase();
    groups.set(key, [...(groups.get(key) ?? []), el]);
  });
  groups.forEach((els) => els.forEach((el, i) => {
    if (el.dataset.scrollLabel !== "1") return;
    const base = el.dataset.scrollName ?? el.getAttribute("aria-label") ?? "";
    el.dataset.scrollName = base;
    const name = els.length > 1 ? `${base}, ${i + 1} of ${els.length}` : base;
    if (el.getAttribute("aria-label") !== name) el.setAttribute("aria-label", name);
  }));
}

export function ScrollRegions() {
  const path = usePathname();
  useEffect(() => {
    let t: ReturnType<typeof setTimeout> | undefined;
    const soon = () => { if (t) clearTimeout(t); t = setTimeout(() => markScrollers(), 150); };
    // session 428: once the fonts and the charts have settled, not at once: a pass inside this effect read the boxes'
    // sizes while the page was still being laid out after it loaded, and so forced the browser to lay it out early
    soon();
    window.addEventListener("resize", soon);
    document.addEventListener("toggle", soon, true);   // a details opened: its table is laid out only now
    const main = document.querySelector("main");
    const watch = main ? new MutationObserver(soon) : null;
    if (main && watch) watch.observe(main, { childList: true, subtree: true });
    return () => { if (t) clearTimeout(t); window.removeEventListener("resize", soon); document.removeEventListener("toggle", soon, true); watch?.disconnect(); };
  }, [path]);
  return null;
}
