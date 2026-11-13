// Energy Research Warehouse (ERW) site, session 177: what a usage count may hold of a page (docs/methods/usage_counts.md).
// The server reads these; the browser sends only a path and an event.
//
//   cleanPath   the path alone: no query, no hash, at most 120 characters of the characters an address of this site
//               uses, and only a page the release list knows (lib/release.ts) or a page under one. Anything else is
//               not counted.
//   toolOf      the tool's name, from the menu's own list (lib/pages.ts): the page whose address is the path or its
//               nearest parent. No second list of names exists.
import { GROUPS } from "@/lib/pages";
import { RELEASE } from "@/lib/release";

export const EVENTS = ["tool opened", "input changed", "scenario compared", "download"] as const;
export type UsageEvent = (typeof EVENTS)[number];
export const isEvent = (v: unknown): v is UsageEvent => typeof v === "string" && (EVENTS as readonly string[]).includes(v);

/** The tool shown to a visitor who asked for a page in review: the in-review page, not the tool. */
export const IN_REVIEW = "In review (not opened)";

const SAFE = /^\/[A-Za-z0-9/_.~:%-]{0,119}$/;

/** The nearest entry of the release list that is the path or a parent of it, or null. */
function entryOf(path: string): string | null {
  let p = path;
  for (;;) {
    if (p in RELEASE) return p;
    const i = p.lastIndexOf("/");
    if (i <= 0) return null;
    p = p.slice(0, i);
  }
}

export function cleanPath(raw: unknown): string | null {
  if (typeof raw !== "string" || raw.length > 400) return null;
  const p = raw.split(/[?#]/)[0].replace(/\/+$/, "") || "/";
  if (!SAFE.test(p) || p.includes("//") || p.includes("..")) return null;
  if (p.startsWith("/api/") || p.startsWith("/internal/") || p.startsWith("/_next/")) return null;
  return entryOf(p) === null ? null : p;
}

const NAMES: [string, string][] = [
  // session 5102: a group's sub-group too (the menu's "Infrastructure Economics", the ruling of 12 October 2026); its
  // five pages were named "" from the day the menu gained it
  ...GROUPS.flatMap((g) => [...g.pages, ...(g.sub?.pages ?? [])].map((pg) => [pg.href, pg.label] as [string, string])),
].sort((a, b) => b[0].length - a[0].length);

export function toolOf(path: string): string {
  for (const [href, label] of NAMES) {
    if (path === href || path.startsWith(href + "/")) return label.slice(0, 80);
  }
  return "";
}

// Session 5155 (docs/reviews/security-faults-2026-11-13.md, row 24): the pages of the menu that carry the mark
// data-no-usage on the whole page (<Brand noUsage>: the owner's ruling "no usage count on tool pages"). On them the
// browser sends the page view and nothing after it. This list is the server's copy of that mark, for the setting
// USAGE_TOOL_PAGES=off (lib/guard.ts), under which not even the page view of such a page is recorded. The match is exact: a
// sub-page is in the list only if its own file carries the mark. tests/test_session5155.py holds the list to the page
// files: a page that gains or loses the mark fails the suite until the list says so.
export const NO_COUNT = ["/battery/customer", "/cost-of-power", "/cost-of-power/battery", "/cost-of-power/seller", "/impact", "/play/ev", "/severance"];
export const noCount = (path: string) => NO_COUNT.includes(path);
