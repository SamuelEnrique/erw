// Energy Research Warehouse (ERW) site, ruling alternatives of /events (session 7712, 17 November 2026; wip/alt-events-*
// branches, not a default on main). The page drawn with its own code on the replication's public rows (replication/events/
// window_rows.csv). On wip/alt-events-5: the Elliott page's SPP paragraph with FERC and NERC's winter peak beside EIA's
// highest hour. With EVENTS_DRAW_UNHELD=1 the hold of 21 October is stood aside and EIA's figure draws as a number.
//   node --import ./scripts/events-page-register.mjs scripts/alt-events-figures.mjs
import { csvRows, drawPage, pageText, PAGES } from "./events-pages.mjs";

const here = (p) => new URL(p, import.meta.url);
const tables = { event_window_daily: csvRows(here("../../replication/events/window_rows.csv")), caiso_grid_emergencies: csvRows(here("../../replication/events/notice_rows.csv")) };
const { html } = await drawPage(PAGES.find(([slug]) => slug === "elliott-2022")[1], (name) => tables[name] ?? null);
const text = pageText(html);
const para = (text.match(/A date that does not match\.[^\n]*/) ?? [""])[0];
const spp = [...html.matchAll(/data-check="series\|event_window_daily\|eia930:SWPP\|demand_max_mw\|([^"|]+)\|elliott_2022" data-raw="([^"]+)"/g)].map((m) => [m[1], Number(m[2])]);
process.stdout.write(JSON.stringify({ ferc: Number((html.match(/data-ferc-spp-peak="(\d+)"/) ?? [])[1] ?? NaN), eiaMax: spp.length ? Math.max(...spp.map((x) => x[1])) : null, para }));
