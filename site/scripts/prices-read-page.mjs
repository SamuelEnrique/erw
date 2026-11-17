// Energy Research Warehouse (ERW) site, session 7539 (chain 304, part C): /prices (its first tab, "Every hub and zone")
// and /prices/<hub> drawn to HTML by the pages' own functions (app/prices/page.tsx, app/prices/[entity]/page.tsx),
// without building the site. The pages read the live set at render time; here their reads are answered by a stand-in
// for fetch from rows the caller gives (`rowsOf(table)`: an array of { entity, variable, ts_utc, value }, or null for a
// table that cannot be read), and the render time is the caller's. No network, no table written, no click, no chart
// seen. Used by scripts/test-prices-read.mjs, and on its own over the warehouse's own tables:
//   node --import ./scripts/prices-read-register.mjs scripts/prices-read-page.mjs <tables dir> <render time ISO> <out dir> [entity ...]
// It writes <out dir>/prices.txt and one <out dir>/<entity>.txt a hub, the page as a reader meets it (a table row's cells
// joined by " | ", a hover as "[title: ...]"; scripts/battery-awards-page.mjs, pageText). Only the public grids' rows
// are given: a held table's rows (license_status.json; lib/license.ts licenseHeldRow) are dropped before the page reads
// them, and nothing this script writes is committed.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createElement } from "react";
import { prerenderToNodeStream } from "react-dom/static";
import { pageText, tableRows } from "./battery-awards-page.mjs";

/** Answers the pages' reads (lib/supabase.ts: /rest/v1/series and /rest/v1/latest_prices) from `rowsOf`, with the
 * filters PostgREST applies (table_name, entity eq or in, variable, ts_utc gte), ordered, a page at a time. */
function standIn(rowsOf, asked) {
  return async (url) => {
    const u = new URL(String(url));
    const q = u.searchParams;
    const name = u.pathname.endsWith("/latest_prices") ? "latest_prices" : (q.get("table_name") ?? "").replace(/^eq\./, "");
    const all = rowsOf(name);
    if (all === null || all === undefined) { asked.push(`${name || u.pathname}: not answered`); return new Response("stand-in: the table is not held", { status: 404 }); }
    const ent = q.get("entity") ?? "";
    const ents = ent.startsWith("eq.") ? new Set([ent.slice(3)]) : ent.startsWith("in.(") ? new Set(ent.slice(4, -1).split(",").map((s) => s.replace(/^"|"$/g, ""))) : null;
    const v = (q.get("variable") ?? "").replace(/^eq\./, "");
    const fromAt = Date.parse((q.get("ts_utc") ?? "").replace(/^gte\./, ""));
    const from = Number.isNaN(fromAt) ? "" : fromAt;   // compared as times, as PostgREST compares them
    // the partition of a consolidated table (iso_dam_hub_prices: ercot_dam, caiso_dam, ...): the row's own market, or
    // its grid and the table's market (day-ahead or real time) when the rows carry none
    const market = (q.get("market") ?? "").replace(/^eq\./, "");
    const marketOf = (r) => r.market ?? `${r.entity.split(":")[0]}_${/_dam_/.test(name) ? "dam" : "rtm"}`;
    const rows = all.filter((r) => (!ents || ents.has(r.entity)) && (!v || r.variable === v) && (!from || Date.parse(r.ts_utc) >= from) && (!market || marketOf(r) === market));
    rows.sort((a, b) => (a.entity < b.entity ? -1 : a.entity > b.entity ? 1 : a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : a.ts_utc < b.ts_utc ? -1 : a.ts_utc > b.ts_utc ? 1 : 0));
    const limit = Number(q.get("limit") ?? 1000), offset = Number(q.get("offset") ?? 0);
    asked.push(`${name} ${ent || "all"}: ${rows.length} rows`);
    const page = rows.slice(offset, offset + limit).map((r) => ({ entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value), unit: r.unit ?? "USD/MWh", freq: r.freq ?? null }));
    return new Response(JSON.stringify(page), { status: 200, headers: { "content-type": "application/json", "content-range": `${offset}-${offset + page.length - 1}/${rows.length}` } });
  };
}

/** The HTML of a tree that holds async server components (React's static prerender waits for every one). */
async function html(tree) {
  const { prelude } = await prerenderToNodeStream(tree);
  const parts = [];
  for await (const c of prelude) parts.push(Buffer.from(c));
  return Buffer.concat(parts).toString("utf-8").replace(/<!-- -->/g, "");
}

/** Draws `/prices` (no entity) or `/prices/<entity>` at the render time `now` (ms), on the rows `rowsOf` gives. */
export async function draw(rowsOf, now, entity) {
  process.env.SUPABASE_URL = "http://localhost:9/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  const asked = [];
  const realFetch = globalThis.fetch, realNow = Date.now, log = console.error;
  globalThis.fetch = standIn(rowsOf, asked);
  Date.now = () => now;
  console.error = () => {};
  try {
    if (!entity) {
      const { default: Prices } = await import("../app/prices/page.tsx");
      return { html: await html(createElement(Prices, { searchParams: Promise.resolve({}) })), asked };
    }
    const { default: EntityPrices } = await import("../app/prices/[entity]/page.tsx");
    return { html: await html(createElement(EntityPrices, { params: Promise.resolve({ entity: encodeURIComponent(entity) }) })), asked };
  } finally {
    globalThis.fetch = realFetch;
    Date.now = realNow;
    console.error = log;
  }
}

/** The grids whose rows may be given (the public ones): a held grid's rows never reach a drawing or a file. */
export const PUBLIC_PREFIXES = ["ercot:", "caiso:", "spp:"];

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [dir, at, out, ...ents] = process.argv.slice(2);
  if (!dir || !at || !out) { console.error("usage: prices-read-page.mjs <tables dir> <render time ISO> <out dir> [entity ...]"); process.exitCode = 2; }
  else {
    const cache = new Map();
    const rowsOf = (t) => {
      if (cache.has(t)) return cache.get(t);
      const f = path.join(dir, `${t}.csv`);
      const rows = fs.existsSync(f) ? tableRows(f).filter((r) => PUBLIC_PREFIXES.some((p) => r.entity.startsWith(p))) : null;
      cache.set(t, rows);
      return rows;
    };
    fs.mkdirSync(out, { recursive: true });
    for (const e of [null, ...ents]) {
      const { html, asked } = await draw(rowsOf, Date.parse(at), e);
      const name = e ? e.replace(/[^\w.-]+/g, "_") : "prices";
      fs.writeFileSync(path.join(out, `${name}.html`), html);
      fs.writeFileSync(path.join(out, `${name}.txt`), pageText(html) + "\n\n[reads]\n" + asked.join("\n") + "\n");
      console.log(`${name}: ${html.length} bytes, ${asked.length} reads`);
    }
  }
}
