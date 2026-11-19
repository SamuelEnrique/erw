// Energy Research Warehouse (ERW) site, session 152: the one demand growth page (/demand), its two views and their
// addresses.
//
// One tool, one page, one address: /demand holds what /demand showed (session 97: growth as metered) and what the
// page built at /demand/weather showed (sessions 126 and 129: the same growth with the weather taken out), as two
// views of one page. The whole state is in the address: ?area and ?rank belong to the first view, ?view=weather with
// ?figure and ?year to the second. /demand/weather redirects to the second view (next.config.ts). Pure functions; the
// page, its checks (scripts/check-demand.mjs, scripts/check-demand-weather.mjs) and tests/test_session152.py share them.

// Session 239: a third view, consumption: what /consumption showed (electricity sold by state and sector, EIA-861M, and
// the energy the industrial and commercial sectors use), at ?view=consumption. /consumption redirects to it
// (next.config.ts). The three are the tabs of the page (lib/tabs.ts, components/tool/Tabs.tsx).
// Session 8420 (chain 503, part C): a fourth view, the whole country: each of EIA's thirteen regions of the lower 48 and
// every balancing authority, any two side by side, from the data machine's page files (site/data/regions/, read by
// lib/countrydemand.ts; drawn by components/demand/Country.tsx), at ?view=country with ?a, ?b, ?days, ?figure and ?year.
// The three views before it, their addresses and what they draw did not move (scripts/test-demand-pin.mjs).
export const VIEWS = [["metered", "As metered"], ["weather", "With the weather taken out"], ["consumption", "Consumption"], ["country", "The whole country"]] as const;
export type View = (typeof VIEWS)[number][0];

/** The view an address asks for: anything but "weather", "consumption" or "country" is the page as metered. */
export const viewOf = (q: Record<string, string | undefined>): View => (q.view === "weather" ? "weather" : q.view === "consumption" ? "consumption" : q.view === "country" ? "country" : "metered");
/** The address of a view with nothing else chosen. */
export const viewHref = (view: View) => (view === "metered" ? "/demand" : `/demand?view=${view}`);
/** The Method note of each view. */
// (the consumption view has no method note of its own: its two tables are EIA's, as published)
export const METHODS: Record<Exclude<View, "consumption">, { href: string; name: string }> = {
  metered: { href: "/data/methods/demand_growth", name: "demand growth" },
  weather: { href: "/data/methods/demand_weather", name: "demand growth with the weather taken out" },
  country: { href: "/data/methods/demand_growth", name: "demand growth, the whole country" },   // session 8420: the note's section "The whole country"
};

// Session 7543 (chain 304, part C, docs/reviews/demand-read-2026-11-16.md): words of two hovers of the page, here
// because a page file may export only what Next.js allows.
/** How the page names an hour (the explorer's "local-time" line says the same: an hour is named by its start). */
export const HOUR_WHY = "The grid's own clock time, daylight saving included: Central for ERCOT, MISO and SPP, Pacific for CAISO, Eastern for PJM, NYISO, ISO-NE and the Lower 48. An hour is named by its start: 17:00 is the hour from 17:00 to 18:00, which the operators' own files call hour ending 18.";
/** The register's entry (data/data_faults.json) on California's demand of early 2019, the base of every CAISO growth. */
export const CA_BASE_FAULT = "eia930_ciso_demand_low_early_2019";
export type Fault = { id: string; title: string; first: string; last: string; dates_note: string; status: string; evidence: string; erw_does: string };
export const caBaseWhy = (f: Fault, words: Record<string, string>) =>
  `${f.title}: ${f.first} to ${f.last} (${f.dates_note}). Status: ${words[f.status] ?? f.status}. What the ERW does: ${f.erw_does} ${f.evidence}`;
