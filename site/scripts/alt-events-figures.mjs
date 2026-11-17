// Energy Research Warehouse (ERW) site, ruling alternatives of /events (session 7712, 17 November 2026; wip/alt-events-*
// branches, not a default on main). The site's own code run on the replication's public rows (replication/events/
// window_rows.csv) and, on wip/alt-events-3, on noaa_grid_weather_daily as the warehouse wrote it (its path the first
// argument): the three newest events' estimate with and without temperature, and the January 2025 page drawn with its
// own component (with EVENTS_DRAW_UNHELD=1 its EIA-930 figures draw as numbers).
//   node --import ./scripts/events-page-register.mjs scripts/alt-events-figures.mjs <noaa_grid_weather_daily.csv>
import { csvRows, drawPage, PAGES } from "./events-pages.mjs";

const S = await import("../lib/eventstudy.ts");
const here = (p) => new URL(p, import.meta.url);
const all = csvRows(here("../../replication/events/window_rows.csv"));
const noaa = csvRows(process.argv[2]);
const out = { studies: {} };
for (const ev of ["cold_2025", "east_heat_2025", "cold_2026"]) {
  for (const ent of ["eia930:PJM", "eia930:ERCO", "eia930:SWPP"]) {
    const rows = all.filter((r) => r.event === ev && r.entity === ent && r.variable === "demand_mwh").map((r) => ({ ts_utc: r.ts_utc, value: Number(r.value), freq: r.freq }));
    if (!rows.length) continue;
    const wx = S.noaaGridWeather(noaa.filter((r) => r.entity === S.NOAA_GRID_ENTITY[ent]));
    const s = S.studyOf(ev, rows), t = S.studyOf(ev, rows, wx);
    out.studies[`${ev}|${ent}`] = { without: s.pooled.estimate, with: t.pooled.estimate, lo: t.pooled.lo, hi: t.pooled.hi, share: (1 - t.pooled.estimate / s.pooled.estimate) * 100, days: t.n };
  }
}
const tables = { event_window_daily: all, caiso_grid_emergencies: csvRows(here("../../replication/events/notice_rows.csv")), [S.NOAA_GRID_TABLE]: noaa };
const html = (await drawPage(PAGES.find(([slug]) => slug === "cold-2025")[1], (name) => tables[name] ?? null)).html;
const elliott = (await drawPage(PAGES.find(([slug]) => slug === "elliott-2022")[1], (name) => tables[name] ?? null)).html;
out.drawn = { noaaTip: /data-es-noaa-tip="1"/.test(html), pooledTemp: (html.match(/data-check="es\|cold_2025\|eia930:PJM\|demand_mwh\|pooled_temp\|est"/g) ?? []).length,
  noStation: /No weather station is held for PJM/.test(html), elliottNoaa: /data-es-noaa-tip/.test(elliott) };
process.stdout.write(JSON.stringify(out));
