// Energy Research Warehouse (ERW) site, session 239 (the owner's instruction of 12 October 2026: the merges of
// docs/reviews/erw-review-2026-10-12.md, section B). Six pages hold what thirteen held, each as tabs of one address:
//
//   /storage    the fleet (what /storage showed), the build-out (/storage/buildout), the owners (/storage/owners)
//   /severance  the calculator (what /severance showed), the lease tool (/severance/lease)
//   /prices     every hub and zone (what /prices showed), ERCOT (/explorer/ercot-peak-premium)
//   /demand     as metered and with the weather taken out (session 152), consumption (/consumption)
//   /deals      the deals (what /deals showed), the tracker (/deals/v2), the companies (/companies)
//   /map        the projects (what /map showed), the resources (/resources)
//
// The tab in view is in the address, so a tab can be linked: the first tab is the page's own address, every other is
// ?tab=<key> (on /demand ?view=<key>, the parameter that page has used since session 152; /deals's tracker and the
// resource map keep "view" for their own choices, so the new pages take "tab"). Each old address redirects to its tab
// with its query carried over (next.config.ts). Pure, with no imports: the pages, components/tool/Tabs.tsx, the
// browser checks and tests/test_session239.py read this file as it is.

export type TabDef = readonly [key: string, label: string];
export type Tabbed = { param: "tab" | "view"; name: string; tabs: readonly TabDef[] };

export const TABBED = {
  "/storage": { param: "tab", name: "Storage", tabs: [["fleet", "The fleet"], ["buildout", "The build-out"], ["owners", "The owners"]] },
  "/severance": { param: "tab", name: "Severance tax", tabs: [["calculator", "Calculator"], ["lease", "Lease"]] },
  "/prices": { param: "tab", name: "Prices", tabs: [["now", "Every hub and zone"], ["ercot", "ERCOT"]] },
  "/demand": { param: "view", name: "Demand", tabs: [["metered", "As metered"], ["weather", "With the weather taken out"], ["consumption", "Consumption"]] },
  "/deals": { param: "tab", name: "Deals", tabs: [["deals", "Deals"], ["tracker", "Tracker"], ["companies", "Companies"]] },
  "/map": { param: "tab", name: "Project map", tabs: [["projects", "Projects"], ["resources", "Resources"]] },
} as const satisfies Record<string, Tabbed>;
export type TabbedPage = keyof typeof TABBED;

/** The old addresses, each with the tab it became (next.config.ts redirects them; scripts/check-routes.mjs asks each). */
export const MERGED: Record<string, string> = {
  "/storage/buildout": "/storage?tab=buildout",
  "/storage/owners": "/storage?tab=owners",
  "/severance/lease": "/severance?tab=lease",
  "/explorer/ercot-peak-premium": "/prices?tab=ercot",
  "/consumption": "/demand?view=consumption",
  "/deals/v2": "/deals?tab=tracker",
  "/companies": "/deals?tab=companies",
  "/resources": "/map?tab=resources",
};

/** The tab an address asks for: the first tab unless the parameter names another. */
export function tabOf(page: TabbedPage, value: string | undefined): string {
  const t: Tabbed = TABBED[page];
  return t.tabs.some(([k]) => k === value) ? (value as string) : t.tabs[0][0];
}
/** The address of a tab with nothing else chosen: the first tab is the page itself. `rest` is a query of the tab's own
 * choices ("grid=ercot"), written after the tab. */
export function tabHref(page: TabbedPage, key: string, rest = ""): string {
  const t: Tabbed = TABBED[page];
  const parts = [key === t.tabs[0][0] ? "" : `${t.param}=${key}`, rest.replace(/^[?&]+/, "")].filter(Boolean);
  return parts.length ? `${page}?${parts.join("&")}` : page;
}
/** One value of a page's search parameters each (a repeated parameter is not a choice). */
export function one(sp: Record<string, string | string[] | undefined>): Record<string, string | undefined> {
  return Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
}
