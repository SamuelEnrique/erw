// Session 67: the release gate. One list: every page of the site and its status. A tool is open to visitors only once
// Samuel has approved it. To open or lock a tool, change its one line here.
//
//   live    open to every visitor
//   review  listed in the menu, greyed and not clickable; its address answers the short "in review" page
//
// A path takes the status of the longest entry that is the path itself or a parent of it ("/grid/ercot" reads
// "/grid/ercot", else "/grid"); "/" matches only itself. A path with no entry is in review. This is a curtain for
// visitors, not security: the API routes and the data are as they were (docs/release-gate.md). The internal view
// (/internal/unlock?token=<INTERNAL_COSTS_TOKEN>) opens everything. No imports: the proxy, the pages, the menu and
// scripts/check-routes.mjs all read this file as it is.

export type Status = "live" | "review";

export const RELEASE: Record<string, Status> = {
  "/": "live",
  "/cost-of-power/battery": "live",
  "/cost-of-power/seller": "live",
  "/network": "live",
  "/storage": "live",
  "/storage/buildout": "review",
  "/shoulder": "review",  // session 75  // session 72: without its own line it would take /storage's status
  "/about": "live",
  "/terms": "live",
  // the methods pages the live tools link to
  "/data/methods/battery_stack": "live",
  "/data/methods/cost_of_power": "live",
  "/data/methods/grid_network": "live",
  "/data/methods/storage": "live",

  "/board": "review",
  "/markets": "review",
  "/cost-of-power": "review",
  "/prices": "review",
  "/explorer/ercot-peak-premium": "review",
  "/grid": "review",
  "/mix": "review",
  "/curtailment": "review",
  "/emissions": "review",
  "/consumption": "review",
  "/grid/ercot": "review",
  "/grid/caiso": "review",
  "/grid/pjm": "review",
  "/grid/nyiso": "review",
  "/grid/isone": "review",
  "/grid/miso": "review",
  "/grid/spp": "review",
  "/map": "review",
  "/datacenters": "review",
  "/companies": "review",
  "/policy": "review",
  "/deals": "review",
  "/events": "review",
  "/tour": "review",
  "/learn/problems": "review",
  "/learn/bill": "review",
  "/play/battery": "review",
  "/severance": "review",
  "/severance/lease": "review",
  "/digest": "review",
  "/roundup": "review",
  "/subscribe": "review",
  "/data": "review",
  "/data/standard": "review",
  "/data/methods": "review",
  "/analysis": "review",
  "/ask": "review",
  "/reports": "review",
};

/** Never behind the curtain: the API and route handlers (the scheduled jobs and the game read them), the internal
 * routes (each has its own token), the in-review page itself, Next's own files and anything with a file extension. */
export function exempt(path: string): boolean {
  return path.startsWith("/api/") || path.startsWith("/internal/") || path.startsWith("/_next/") || path === "/in-review"
    || path === "/severance/finder/download" || /\.[a-z0-9]+$/i.test(path);
}

/** The status of a path (no query, no hash). */
export function statusOf(path: string): Status {
  let p = path.split(/[?#]/)[0].replace(/\/+$/, "") || "/";
  try { p = decodeURIComponent(p); } catch { /* a malformed escape stays as it is */ }
  if (exempt(p)) return "live";
  for (;;) {
    if (p in RELEASE) return RELEASE[p];
    const i = p.lastIndexOf("/");
    if (i <= 0) return "review";  // "/" is not a parent: only the home page itself is "/"
    p = p.slice(0, i);
  }
}
export const isLive = (path: string) => statusOf(path) === "live";
/** An href as the site writes it: a site path is gated, anything else (another site, mailto, a bare hash) is not. */
export const gated = (href: string) => href.startsWith("/") && !href.startsWith("//") && statusOf(href) === "review";

// The internal view: two cookies set by /internal/unlock, both for 90 days. COOKIE is httpOnly and holds a digest of
// the token (never the token); the proxy opens the review pages only when it matches. VIEW is readable by the page's
// own script and only tells the menu to draw itself as the internal view; it opens nothing.
export const COOKIE = "erw_internal";
export const VIEW = "erw_view";
export const MAX_AGE = 90 * 24 * 3600;
export async function digest(token: string): Promise<string> {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`erw-internal-view:${token}`));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
