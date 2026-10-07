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
  // Session 126 (the owner's instruction, 5 October 2026): the home page, About, Terms, the seller's tab and the four
  // methods notes are in review. Three pages are open: /cost-of-power/battery, /network and /storage.
  "/": "review",
  "/cost-of-power/battery": "live",
  "/cost-of-power/battery/awards": "review",  // session 115: what Texas's storage resources were awarded day-ahead; without its own line it would take the live battery page's status
  "/cost-of-power/seller": "review",
  // session 145: /cost-of-power/seller/v2 is retired and redirects to /cost-of-power/seller (next.config.ts); its line stays so that an address typed by hand never reads as a page with no status
  "/cost-of-power/seller/v2": "review",  // session 107: version 2 of the seller's tab; without its own line it would take the live tab's status
  "/network": "live",
  "/network/v3": "review",  // session 93: version 3 (replay, a shareable address, prices, trace); without its own line it would take /network's status
  "/storage": "live",
  "/storage/buildout": "review",
  "/battery/customer": "review",  // session 88: what a battery saves a customer; the reader's own numbers, in the browser
  "/storage/owners": "review",  // session 87: without its own line it would take /storage's status
  "/contracts": "review",  // session 83: an internal table; it stays behind the internal view
  "/shoulder": "review",  // session 75  // session 72: without its own line it would take /storage's status
  "/about": "review",
  "/terms": "review",
  // the methods pages the live tools link to
  "/data/methods/battery_stack": "review",
  "/data/methods/cost_of_power": "review",
  "/data/methods/grid_network": "review",
  "/data/methods/storage": "review",

  "/board": "review",
  // session 132: /board/v4, /board/v3 and /markets are retired and redirect to /board (next.config.ts); their lines stay so that an address typed by hand never reads as a page with no status
  "/board/v4": "review",  // session 127: the price board, version 4 (every price held: latest, moves over a day, week, month and year, its one-year range; the spreads; what is not held)
  "/board/v3": "review",  // session 104: the price board, version 3 (power by grid, gas, oil; last value, day, week, thirty days)
  "/markets": "review",
  "/cost-of-power": "review",
  "/supply": "review",  // session 134: supply and trade (storage, stocks, production, refining, trade and positioning against last week, last year and the five-year average)
  "/prices": "review",
  "/explorer/ercot-peak-premium": "review",
  "/grid": "review",
  "/mix": "review",
  "/prices/compare": "review",  // session 96: where power is cheap (hub and zone prices compared)
  "/demand": "review",  // session 97: the demand growth explorer
  // session 144: /curtailment/v2 is retired and redirects to /curtailment (next.config.ts); its line stays so that an address typed by hand never reads as a page with no status
  "/curtailment/v2": "review",  // session 98: curtailment, version 2 (California by hour, month and reason, against battery charging)
  "/queues": "review",  // session 95: the interconnection queue explorer
  // session 133: /mix/v2, /mix/clean and /mix/stress are retired and redirect to /mix (next.config.ts); their lines stay so that an address typed by hand never reads as a page with no status
  "/mix/clean": "review",  // session 122: how clean each grid's generation is, and when (hourly against annual matching, the cleanest hours, load moved into them)
  "/mix/stress": "review",  // session 123: how hard each grid works (evening ramp, lowest net load, fuels in the tightest hours, dark and calm stretches)
  "/mix/v2": "review",  // session 94: the energy mix, version 2 (any grid, any month or year, two grids side by side, the records)
  "/curtailment": "review",  // session 144: the one curtailment page (every grid by day and month, California by the hour, where free energy is, what it is worth)
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
  "/map/v2": "review",  // session 105: the project map, version 2 (EIA-860M's operating and planned units, with the queue beside it)
  "/datacenters": "review",
  "/datacenters/v2": "review",  // session 106: the tracker, version 2 (ERCOT's large-load status beside the facilities held)
  "/companies": "review",
  "/thesis": "review",  // session 135: Thesis Builder (a niche typed, a run queued, the report in tabs, the PitchBook stage); internal, and the page checks the internal cookie itself
  "/policy": "review",
  "/deals": "review",
  "/deals/v2": "review",  // session 113: the deals tracker, version 2 (the battery page's layout; the deals already extracted, duplicates shown once)
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
  "/data/faults": "review",  // session 103: known faults in source data
  "/analysis": "review",
  "/ask": "review",
  "/ask/ercot": "review",  // session 92: Ask ERCOT, the reference version
  "/reports": "review",
  "/home/v2": "review",  // session 110: the home page and menu by audience, a draft
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
