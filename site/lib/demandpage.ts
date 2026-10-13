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
export const VIEWS = [["metered", "As metered"], ["weather", "With the weather taken out"], ["consumption", "Consumption"]] as const;
export type View = (typeof VIEWS)[number][0];

/** The view an address asks for: anything but "weather" or "consumption" is the page as metered. */
export const viewOf = (q: Record<string, string | undefined>): View => (q.view === "weather" ? "weather" : q.view === "consumption" ? "consumption" : "metered");
/** The address of a view with nothing else chosen. */
export const viewHref = (view: View) => (view === "metered" ? "/demand" : `/demand?view=${view}`);
/** The Method note of each view. */
// (the consumption view has no method note of its own: its two tables are EIA's, as published)
export const METHODS: Record<Exclude<View, "consumption">, { href: string; name: string }> = {
  metered: { href: "/data/methods/demand_growth", name: "demand growth" },
  weather: { href: "/data/methods/demand_weather", name: "demand growth with the weather taken out" },
};
