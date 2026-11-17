// Energy Research Warehouse (ERW) site, ruling alternatives of /explore/demand-growth (session 7709, 17 November 2026;
// wip/alt-demand-growth-* branches, not a default on main). The page's own library and component run on public rows, so
// that the figures under the other choice are pinned with the site's code. On wip/alt-demand-growth-3: a site's MW as a
// share of each grid's growth since 2019, on replication/demand_growth/table_rows.csv (the rows the page reads, 16
// November 2026), for 300 and 1,000 MW, and the section drawn for 300 MW and for a size it cannot use.
//   node --import ./scripts/tsx-register.mjs scripts/alt-demand-growth-figures.mjs
import fs from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const D = await import("../lib/explore/demandgrowth.ts");
const { SiteShareSection } = await import("../app/explore/demand-growth/SiteShare.tsx");
const text = fs.readFileSync(new URL("../../replication/demand_growth/table_rows.csv", import.meta.url), "utf8").replace(/\r\n/g, "\n").split("\n").filter((l) => l && !l.startsWith("#"));
const head = text[0].split(",");
const rows = text.slice(1).map((l) => Object.fromEntries(l.split(",").map((v, i) => [head[i], v]))).map((r) => ({ entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value) }));
const out = {};
for (const g of D.GRIDS) {
  const a = D.siteShare(rows, D.entityOf(g.ba), 300), b = D.siteShare(rows, D.entityOf(g.ba), 1000);
  out[g.slug] = a && { year: a.year, growth: a.growthMw, s300: a.sharePct, s1000: b.sharePct };
}
const html = renderToStaticMarkup(createElement(SiteShareSection, { rows, grid: "ercot", win: "avg", mw: 300, typed: "300" }));
const bad = renderToStaticMarkup(createElement(SiteShareSection, { rows, grid: "ercot", win: "avg", mw: D.siteMw("lots"), typed: "lots" }));
process.stdout.write(JSON.stringify({
  grids: out, read: [D.siteMw("300"), D.siteMw("1,000"), D.siteMw("0"), D.siteMw("-5"), D.siteMw("200000"), D.siteMw("abc")],
  drawn: { ercot: (html.match(/data-site-share="ercot">([^<]*)</) ?? [])[1], nyiso: (html.match(/data-site-share="nyiso">([^<]*)</) ?? [])[1], tip: /data-site-tip="1"/.test(html), bad: /is not a size this page can use/.test(bad) },
}));
