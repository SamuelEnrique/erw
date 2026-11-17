// Energy Research Warehouse (ERW) site, ruling alternatives of /events (session 7712, 17 November 2026; wip/alt-events-*
// branches, not a default on main). The page drawn with its own code on the replication's public rows (replication/events/
// window_rows.csv). On wip/alt-events-6: the September 2022 California page's sentence on each airport's hottest day.
// With EVENTS_DRAW_UNHELD=1 the hold of 21 October is stood aside and the figures draw as numbers.
//   node --import ./scripts/events-page-register.mjs scripts/alt-events-figures.mjs
import { csvRows, drawPage, pageText, PAGES } from "./events-pages.mjs";

const here = (p) => new URL(p, import.meta.url);
const tables = { event_window_daily: csvRows(here("../../replication/events/window_rows.csv")), caiso_grid_emergencies: csvRows(here("../../replication/events/notice_rows.csv")) };
const { html } = await drawPage(PAGES.find(([slug]) => slug === "caiso-heat-2022")[1], (name) => tables[name] ?? null);
const text = pageText(html);
const cell = (k) => (html.match(new RegExp(`data-check="series\\|event_window_daily\\|noaa:${k}\\|temp_max_f\\|([^"|]+)\\|caiso_heat_2022" data-raw="([^"]+)"`)) ?? []).slice(1);
process.stdout.write(JSON.stringify({
  sentence: (text.match(/The heat\.[^\n]*/) ?? [""])[0],
  sac: cell("SAC"), lax: cell("LAX"),
  held: (html.match(/data-airport-hottest="1"[\s\S]*?<\/p>/)?.[0].match(/data-license-held=/g) ?? []).length,
}));
