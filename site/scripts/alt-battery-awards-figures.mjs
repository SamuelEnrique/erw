// Energy Research Warehouse (ERW) site, ruling alternatives of /cost-of-power/battery/awards (session 7705, 17 November
// 2026; wip/alt-battery-awards-* branches, not a default on main). The page's own library run on the public tables as the
// warehouse writes them, so that the figures under the other choice are pinned with the site's code. On
// wip/alt-battery-awards-4: every storage settlement point's own spread (ercot_storage_node_basis, spread_node), and the
// real-time section drawn with two points by name side by side.
//   node --import ./scripts/tsx-register.mjs scripts/alt-battery-awards-figures.mjs <tables dir> <point A> <point B>
import fs from "node:fs";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const R = await import("../lib/storagerealtime.ts");
const { RealTimeSection } = await import("../app/cost-of-power/battery/awards/RealTime.tsx");
const [dir, a, b] = process.argv.slice(2);
const rows = [], basisRows = [];
let head = null;
for (const line of fs.readFileSync(path.join(dir, `${R.BASIS_TABLE}.csv`), "utf-8").split(/\r?\n/)) {
  if (!line || line.startsWith("#")) continue;
  if (!head) { head = line; continue; }
  const c = line.split(",");
  if (c[1] === R.POINT_VARIABLE) rows.push({ entity: c[0], ts_utc: c[2], value: c[3] });
  if (c[0] === R.BASIS_ENTITY && R.BASIS_VARIABLES.includes(c[1])) basisRows.push({ variable: c[1], ts_utc: c[2], value: c[3] });
}
const A = await import("../lib/storageawards.ts");
function read(table, entity, variables) {
  const want = new Set(variables), out = [];
  let h = null;
  for (const line of fs.readFileSync(path.join(dir, `${table}.csv`), "utf-8").split(/\r?\n/)) {
    if (!line || line.startsWith("#")) continue;
    if (!h) { h = line; continue; }
    const c = line.split(",");
    if (c[0] === entity && want.has(c[1])) out.push({ variable: c[1], ts_utc: c[2], value: c[3] });
  }
  return out;
}
const months = R.rtMonthsOf(read(R.RT_TABLE, R.RT_ENTITY, R.RT_VARIABLES), read(A.MODEL_TABLE, A.MODEL_ENTITY, A.MODEL_VARIABLES), A.MODEL_PREFIX);
const points = R.pointsOf(rows), basis = R.basisOf(basisRows);
const pA = R.pointNamed(points, a), pB = R.pointNamed(points, b);
const html = renderToStaticMarkup(createElement(RealTimeSection, { months, basis, unread: null, basisUnread: null, points, a, b, pointA: pA, pointB: pB, pointsUnread: null }));
const spread = (k) => (html.match(new RegExp(`data-rt-ab-spread="${k}"[^>]*>([^<]*)<`)) ?? [])[1] ?? null;
const sorted = points.map((p) => p.spread).sort((x, y) => x - y);
process.stdout.write(JSON.stringify({
  points: points.length, widest: points[0], narrowest: points.at(-1), median: (sorted[(sorted.length - 1) >> 1] + sorted[sorted.length >> 1]) / 2,
  a: pA, b: pB, drawn: { a: spread("A"), b: spread("B"), options: (html.match(/<option /g) ?? []).length, notFound: /is not one of the/.test(html) },
}));
