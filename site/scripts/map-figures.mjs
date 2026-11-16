// Energy Research Warehouse (ERW) site, session 7601 (chain 305): every figure the Projects tab of /map draws, for a
// list of views, computed by the page's own functions (lib/projectmap.ts: parseChoice, select, totals) on the page's own
// file (data/map.json), with the drawing's own projection. The page computes these in the reader's browser; this runs
// the same functions in Node, so replication/map/replicate.py has the page's side of each figure to stand against.
// No server, no network, no browser.
//
//   node scripts/map-figures.mjs                 # JSON on standard output
//   node scripts/map-figures.mjs <out.json>      # written to a file
//
// A view is an address of the page (the part after /map). The list: no choice; every option of the five lists alone
// (4 kinds, 9 grids, 17 technologies, 19 statuses, 53 states); and 20 combinations a reader makes (two lists at once,
// a size from and to, a state with a kind). A figure's key is "<view>|<what>"; its value is the number the page writes
// (a whole number: the page rounds a sum of megawatts once, with Math.round).
import fs from "node:fs";
import { geoAlbersUsa } from "d3-geo";

const L = await import("../lib/projectmap.ts");
const f = JSON.parse(fs.readFileSync(new URL("../data/map.json", import.meta.url), "utf-8"));
const projection = geoAlbersUsa().scale(1300).translate([487.5, 305]);   // app/map/ProjectMap.tsx
const placed = f.k.map((_, i) => f.la[i] !== null && f.lo[i] !== null && projection([f.lo[i], f.la[i]]) !== null);

const views = [""];
for (const which of L.FILTERS) for (const slug of L.optionsOf(f, which)) views.push(`?${which}=${encodeURIComponent(slug)}`);
views.push("?grid=ercot&tech=solar,battery", "?kind=operating,planned&state=TX,CA&min=100&max=500", "?kind=queue&grid=ercot", "?status=u,v,ts", "?min=1000",
  "?max=1", "?kind=planned&tech=battery", "?kind=operating&grid=caiso&tech=battery", "?kind=queue&state=TX&tech=queue_storage,hybrid", "?kind=datacenter&state=VA",
  "?kind=operating&tech=nuclear", "?kind=operating,planned&grid=outside", "?kind=none", "?kind=queue&min=500", "?kind=datacenter&min=100",
  "?grid=pjm&status=operating&tech=natural_gas,coal", "?kind=planned&status=p,l,t", "?state=TX&min=200&max=400", "?grid=ercot&tech=battery", "?grid=ercot&tech=battery&min=100");

const round = (v) => Math.round(v);
const figures = [];
const put = (view, what, value) => figures.push({ key: `${view || "(no choice)"}|${what}`, page: value, tolerance: 0.5 });
for (const view of views) {
  const choice = L.parseChoice(view, f);
  const picked = L.select(f, choice);
  const sum = L.totals(f, picked);
  const [op, pl, q, dc] = sum.byKind;
  put(view, "rows", sum.rows);
  // the sentence
  put(view, "units", op.rows + pl.rows);
  put(view, "units_mw", round(op.mw + pl.mw));
  put(view, "queue", q.rows);
  put(view, "queue_mw", round(q.mw));
  put(view, "datacenters", dc.rows);
  put(view, "datacenters_mw", round(dc.mw));
  put(view, "datacenters_with_mw", dc.withMw);
  // the tiles: a status with a row
  f.statuses.forEach((s, i) => {
    const t = sum.byStatus[i];
    if (!t.rows) return;
    put(view, `status|${s.slug}|rows`, t.rows);
    put(view, `status|${s.slug}|with_mw`, t.withMw);
    if (t.withMw) put(view, `status|${s.slug}|mw`, round(t.mw));
  });
  // the table by technology: the kinds chosen among operating, planned and queue; a technology with a row
  const kindOn = (k) => choice.kind === null || choice.kind.includes(k);
  f.techs.forEach((t, ti) => {
    if (t.slug === "datacenter") return;
    for (const k of [L.KIND.operating, L.KIND.planned, L.KIND.queue]) {
      const c = sum.byTech[ti][k];
      if (!kindOn(k) || !c.rows) continue;
      put(view, `tech|${t.slug}|${f.kinds[k].slug}|rows`, c.rows);
      put(view, `tech|${t.slug}|${f.kinds[k].slug}|mw`, round(c.mw));
    }
  });
  // the drawing
  const drawn = picked.filter((i) => placed[i]).length;
  put(view, "drawn", drawn);
  put(view, "not_drawn", picked.length - drawn);
}
// the file's own counts, which the page's first lines and the note quote
for (const [k, v] of Object.entries(f.counts)) figures.push({ key: `file|counts|${k}`, page: v, tolerance: /_mw$/.test(k) ? 0.05 : 0.5 });

const out = {
  tool: "/map", tab: "projects", file: "site/data/map.json", built: f.built, vintage: f.vintage, vintages: f.vintages, tables: f.tables,
  views: views.length, figures,
};
const text = JSON.stringify(out, null, 1) + "\n";
if (process.argv[2]) fs.writeFileSync(process.argv[2], text);
else process.stdout.write(text);
