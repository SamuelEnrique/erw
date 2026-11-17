// Energy Research Warehouse (ERW) site, ruling alternatives of /explore/demand-growth (session 7709, 17 November 2026;
// wip/alt-demand-growth-* branches, not a default on main). The page's own library and component run on public rows, so
// that the figures under the other choice are pinned with the site's code. On wip/alt-demand-growth-1: California's
// growth with and without the batteries' charging, on replication/demand_growth/california_rows.csv (rows copied
// unchanged from eia930_demand_growth and shoulder_hours_monthly), for the impact file's two windows and for the windows
// the page chooses; and the section drawn.
//   node --import ./scripts/tsx-register.mjs scripts/alt-demand-growth-figures.mjs
import fs from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const D = await import("../lib/explore/demandgrowth.ts");
const { CaliforniaCharging } = await import("../app/explore/demand-growth/Charging.tsx");
const text = fs.readFileSync(new URL("../../replication/demand_growth/california_rows.csv", import.meta.url), "utf8").replace(/\r\n/g, "\n").split("\n").filter((l) => l && !l.startsWith("#"));
const head = text[0].split(",");
const rows = text.slice(1).map((l) => Object.fromEntries(l.split(",").map((v, i) => [head[i], v])));
const pick = (t) => rows.filter((r) => r.table === t).map((r) => ({ entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value) }));
const eia = pick("eia930_demand_growth"), own = pick("shoulder_hours_monthly");
const fig = (w) => w && { year: w.year, months: w.months, base: w.base, eia: w.eia, charging: w.charging, growth: w.growthPct, less: w.lessChargingPct };
const windows = D.chargingWindows(eia, own);
const html = renderToStaticMarkup(createElement(CaliforniaCharging, { windows, unread: null }));
process.stdout.write(JSON.stringify({
  june_december_2025: fig(D.chargingWindow(eia, own, 2025, [6, 7, 8, 9, 10, 11, 12])),
  january_august_2026: fig(D.chargingWindow(eia, own, 2026, [1, 2, 3, 4, 5, 6, 7, 8])),
  may_2025: D.chargingWindow(eia, own, 2025, [5]),
  page: windows.map(fig),
  drawn: { windows: [...html.matchAll(/data-charging-window="(\d+)">([^<]*)</g)].map((m) => m[2]), less: [...html.matchAll(/data-charging-less="\d+">([^<]*)</g)].map((m) => m[1]), tip: /data-charging-tip="1"/.test(html) },
}));
