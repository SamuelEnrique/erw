"use client";
// Energy Research Warehouse (ERW) site, session 177: the one place the usage counts are sent from, mounted once in the
// root layout (lib/usage.ts, docs/methods/usage_counts.md). No cookie, no storage, no value of any input.
//
//   tool opened     once a page view (the path changed)
//   input changed   a form control inside the page's <main> changed; at most once a control a page view. Only the fact
//                   is sent: never the control's name or its value.
//   download        a click on a link that carries `download`, goes to /api/download or a download route, or names a
//                   .csv, .do or .py file
//
// "scenario compared" is sent by the tool that compares (it calls track itself).
//
// A page that tells the reader nothing typed is sent (lib/usage.ts, QUIET and PROMISE) gets its page view counted and
// nothing after it: no request follows what the reader does there. An element inside `data-no-usage` is never counted.
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import { PROMISE, isDownload, quiet, track } from "@/lib/usage";

export function Usage() {
  const path = usePathname();
  useEffect(() => {
    track("tool opened");
    if (quiet(path)) return;
    const seen = new WeakSet<Element>();
    let promised: boolean | null = null;
    // read when the reader first acts, so the page's own text has been drawn
    const silent = (t: Element) => {
      if (t.closest("[data-no-usage]")) return true;
      if (promised === null) promised = PROMISE.test(document.querySelector("main")?.textContent ?? "");
      return promised;
    };
    const onChange = (e: Event) => {
      const t = e.target;
      if (!(t instanceof Element) || !t.matches("input, select, textarea") || !t.closest("main") || seen.has(t) || silent(t)) return;
      seen.add(t);
      track("input changed");
    };
    const onClick = (e: MouseEvent) => {
      const a = e.target instanceof Element ? e.target.closest("a") : null;
      if (!a || silent(a)) return;
      if (isDownload({ hasDownload: a.hasAttribute("download"), href: a.getAttribute("href") ?? "" }, window.location.origin)) track("download");
    };
    document.addEventListener("change", onChange, true);
    document.addEventListener("click", onClick, true);
    return () => {
      document.removeEventListener("change", onChange, true);
      document.removeEventListener("click", onClick, true);
    };
  }, [path]);
  return null;
}
