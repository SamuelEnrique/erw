// Energy Research Warehouse (ERW) site, ruling alternatives of /events (session 7712, 17 November 2026; wip/alt-events-*
// branches, not a default on main). The site's own code run on the replication's public rows (replication/events/
// window_rows.csv), so that the figures under the other choice are pinned with the site's code. On wip/alt-events-2: the
// Elliott page's PJM estimate for each day with and without temperature (lib/eventstudy.ts), and the page drawn with its
// own component: how many cells the new column has, as numbers (with EVENTS_DRAW_UNHELD=1) or "license needed".
//   node --import ./scripts/events-page-register.mjs scripts/alt-events-figures.mjs
import { csvRows, drawPage, PAGES } from "./events-pages.mjs";

const S = await import("../lib/eventstudy.ts");
const here = (p) => new URL(p, import.meta.url);
const all = csvRows(here("../../replication/events/window_rows.csv"));
const rows = all.filter((r) => r.event === "elliott_2022");
const pjm = rows.filter((r) => r.entity === "eia930:PJM" && r.variable === "demand_mwh").map((r) => ({ ts_utc: r.ts_utc, value: Number(r.value), freq: r.freq }));
const wx = S.gridWeather(rows.filter((r) => r.entity.startsWith("noaa:") && (r.variable === "hdd_65f" || r.variable === "cdd_65f") && S.STATION_BA[r.entity] === "pjm")
  .map((r) => ({ ...r, value: Number(r.value) })));
const s = S.studyOf("elliott_2022", pjm), t = S.studyOf("elliott_2022", pjm, wx);
const tables = { event_window_daily: all, caiso_grid_emergencies: csvRows(here("../../replication/events/notice_rows.csv")) };
const file = PAGES.find(([slug]) => slug === "elliott-2022")[1];
const { html } = await drawPage(file, (name) => tables[name] ?? null);
const other = PAGES.find(([slug]) => slug === "uri-2021")[1];
const uri = (await drawPage(other, (name) => tables[name] ?? null)).html;
process.stdout.write(JSON.stringify({
  pooled: [s.pooled.estimate, t.pooled.estimate],
  days: Object.fromEntries(t.days.map((d) => [d.day, [s.days.find((x) => x.day === d.day)?.estimate ?? null, d.estimate]])),
  drawn: { numbers: (html.match(/data-check="es\|elliott_2022\|eia930:PJM\|demand_mwh\|day_temp\|/g) ?? []).length,
    tip: /data-es-day-temp-tip="1"/.test(html), held: (html.match(/data-license-held="event_window_daily"/g) ?? []).length },
  uriHasColumn: /data-es-day-temp-tip/.test(uri),
}));
