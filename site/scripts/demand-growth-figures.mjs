// Energy Research Warehouse (ERW) site, session 7508 (chain 304): every figure of the demand growth explorer
// (/explore/demand-growth), as the page itself draws it, for every grid (8) and every window (39): 312 views, the
// page as it opens, and an address the table does not hold.
//
//   node --import ./scripts/tsx-register.mjs scripts/demand-growth-figures.mjs <eia930_demand_growth.csv> <out.json> [--coverage=<coverage.csv>] [--opening] [--html=<dir>]
//
// The page (app/explore/demand-growth/page.tsx) is drawn to HTML with the site's own code, once a view. Its reads of
// the live set (lib/supabase.ts: the rows of the table, its header lines, the catalogue) are answered here, in the
// process, from the table file named and, when given, from warehouse/metadata/coverage.csv (the catalogue is that
// file, loaded; the table is held for review there, warehouse/supabase/live_set.yaml). Nothing is asked of a server
// and nothing is written but <out.json>. From each view's HTML it keeps, slot by slot, the text a reader sees:
//
//   h1.label h1.value h1.unit h1.base h1.latest   the first headline: growth since 2019, with the two MW under it
//   h2.label h2.value h2.unit h2.base             the second: the demand in the window, with 2019's under it
//   h3.label h3.value h3.unit                     the third: the change in MW, or the other window's growth
//   bar1.<grid name>                              the headline chart's hover line, one a grid
//   grid.<slug>.base .latest .growth .change      the table "Every grid", one row a grid (.year: a year marked beside a figure)
//   bar2.<year>                                   the second chart's hover line, one a year
//   bar3.<year>                                   the third chart's hover line, one a year
//   year.<year>.label .mw .growth .yoy .used .hours   the grid's table year by year
//
// and, beside them, every checked number (its key, the value read, the text shown). A figure's sign is drawn outside
// its checked span; a slot keeps it. replication/demand_growth/replicate.py sets these beside its own reading of the
// table. The bars' heights are not in the server's words (a browser read). It runs no effect and no click.
import fs from "node:fs";
import { register } from "node:module";
import { createElement as h } from "react";

// The page's frame (components/Brand.tsx) names the brand's fonts through next/font/google, which exists only inside a
// build. Here a font is its class names and nothing more: no figure of the page depends on one.
register(`data:text/javascript,${encodeURIComponent(`
export async function resolve(specifier, context, next) {
  if (specifier === "next/font/google") return { url: "erw-font-stub:google", shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url === "erw-font-stub:google") return { format: "module", shortCircuit: true, source:
    "const f = () => ({ className: '', variable: '', style: { fontFamily: 'stand-in' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;" };
  return next(url, context);
}`)}`);

const [tableFile, outFile, ...flags] = process.argv.slice(2);
if (!tableFile || !outFile) {
  console.error("usage: node --import ./scripts/tsx-register.mjs scripts/demand-growth-figures.mjs <eia930_demand_growth.csv> <out.json> [--coverage=<coverage.csv>] [--opening] [--html=<dir>]");
  process.exitCode = 2;
} else {
  await main();
}

function readTable(file) {
  const all = fs.readFileSync(file, "utf-8").split(/\r?\n/);
  const header = all.filter((l) => l.startsWith("#")).map((l) => l.replace(/^#\s?/, ""));
  const lines = all.filter((l) => l && !l.startsWith("#"));
  const cols = lines[0].split(",");
  const ix = Object.fromEntries(cols.map((k, i) => [k, i]));
  const rows = lines.slice(1).map((l) => {
    const c = l.split(",");
    return { entity: c[ix.entity], variable: c[ix.variable], ts_utc: c[ix.ts_utc], value: Number(c[ix.value]) };
  });
  return { header, rows };
}

async function main() {
  const TABLE = "eia930_demand_growth";
  const T = readTable(tableFile);
  const coverageFile = flags.find((f) => f.startsWith("--coverage="))?.slice(11);
  let catalogue = [];
  if (coverageFile) {
    const lines = fs.readFileSync(coverageFile, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
    const cols = lines[0].split(",");
    catalogue = lines.slice(1).map((l) => Object.fromEntries(l.split(",").map((v, i) => [cols[i], v])))
      .filter((r) => r.table === TABLE)
      .map((r) => ({ table_name: r.table, interval: r.interval, ts_min: r.ts_min, ts_max: r.ts_max, n_rows: Number(r.n_rows), last_run: r.last_run, license: r.license, in_live_set: "review" }));
  }

  // the page's reads, answered from the file: GET <base>/rest/v1/<series|headers|catalogue>?...
  process.env.SUPABASE_URL = "http://demand-growth-figures.invalid";
  process.env.SUPABASE_ANON_KEY = "local";
  const eq = (f) => (f?.startsWith("eq.") ? f.slice(3) : null);
  const among = (f) => (f?.startsWith("in.(") ? f.slice(4, -1).split(",").map((x) => x.replace(/^"|"$/g, "")) : null);
  const one = (f) => (f === undefined ? null : eq(f) !== null ? [eq(f)] : among(f));
  let asked = 0;
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    const q = Object.fromEntries(u.searchParams);
    asked++;
    let out = [];
    if (u.pathname === "/rest/v1/series" && eq(q.table_name) === TABLE) {
      const ent = one(q.entity), vars = one(q.variable);
      out = T.rows.filter((r) => (!ent || ent.includes(r.entity)) && (!vars || vars.includes(r.variable)));
      const keys = (q.order ?? "").split(",").filter(Boolean);
      out = out.slice().sort((a, b) => { for (const k of keys) { if (a[k] < b[k]) return -1; if (a[k] > b[k]) return 1; } return 0; });
    } else if (u.pathname === "/rest/v1/headers" && eq(q.table_name) === TABLE) {
      out = T.header.map((line, i) => ({ table_name: TABLE, line_no: i + 1, line }));
    } else if (u.pathname === "/rest/v1/catalogue") {
      out = catalogue;
    }
    const offset = Number(q.offset ?? 0), limit = Number(q.limit ?? 1000);
    out = out.slice(offset, offset + limit);
    return new Response(JSON.stringify(out), { status: 200, headers: { "Content-Type": "application/json" } });
  };

  const { prerenderToNodeStream } = await import("react-dom/static");
  const D = await import("../lib/explore/demandgrowth.ts");
  const { default: Page } = await import("../app/explore/demand-growth/page.tsx");
  const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
  // a tip's words (role="tooltip") are a hover, not the face: they are taken out before a slot's text is read
  const noTips = (html) => html.replace(/<span class="tip [\s\S]*?<span role="tooltip"[^>]*>[\s\S]*?<\/span><\/span>/g, "");
  const text = (html) => decode(noTips(html).replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim().replace(/^\+ (?=[0-9])/, "+");   // the sign is drawn against its number
  // the page is an async server component and so is its freshness line: the static prerender waits for both
  const draw = async (q) => {
    const { prelude } = await prerenderToNodeStream(h(Page, { searchParams: Promise.resolve(q) }));
    const parts = [];
    for await (const c of prelude) parts.push(Buffer.from(c));
    return Buffer.concat(parts).toString("utf-8");
  };

  const views = [{ q: {}, why: "the page as it opens" }];
  const grids = flags.includes("--opening") ? D.GRIDS.slice(0, 1) : D.GRIDS;
  for (const g of grids) for (const w of D.WINDOWS) views.push({ q: { grid: g.slug, window: w.slug }, why: "a grid and a window" });
  views.push({ q: { grid: "ercot", window: "avg", extra: "1" }, why: "the default named" });
  views.push({ q: { grid: "tva", window: "m13" }, why: "an address the table does not hold" });

  const out = { table_file: tableFile, table_rows: T.rows.length, header: T.header, views: [], keyed: {}, conflicts: [] };
  const htmlDir = flags.find((f) => f.startsWith("--html="))?.slice(7);
  const cellsOf = (tr) => [...tr.matchAll(/<t[dh][^>]*>([\s\S]*?)<\/t[dh]>/g)].map((m) => m[1]);
  for (const v of views) {
    const html = await draw(v.q);
    if (htmlDir) fs.writeFileSync(`${htmlDir}/demand_growth_${v.q.grid ?? "opening"}_${v.q.window ?? ""}.html`, html);
    const slots = {};
    const keys = [];
    for (const m of html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)) {
      const key = decode(m[1]), value = { raw: Number(m[2]), text: text(m[3]) };
      keys.push(key);
      if (key in out.keyed && JSON.stringify(out.keyed[key]) !== JSON.stringify(value)) out.conflicts.push({ key, first: out.keyed[key], second: value });
      out.keyed[key] = value;
    }
    // the three headline numbers: the label, the number with its sign and its unit, the line under it
    const heads = [...html.matchAll(/<div class="border-t-2 border-accent pt-2"><div class="text-xs uppercase tracking-wide text-muted">([\s\S]*?)<\/div><div class="mt-1 font-serif text-3xl tabular-nums text-ink">([\s\S]*?)<\/div>(?:<div class="mt-1 text-xs leading-snug text-muted">([\s\S]*?)<\/div>)?<\/div>/g)];
    heads.forEach((m, i) => {
      const k = `h${i + 1}`;
      slots[`${k}.label`] = text(m[1]);
      const unit = m[2].match(/<span class="ml-1 font-sans text-sm text-muted">([\s\S]*?)<\/span>$/);
      slots[`${k}.value`] = text(unit ? m[2].slice(0, unit.index) : m[2]);
      slots[`${k}.unit`] = unit ? text(unit[1]) : "";
      if (m[3] !== undefined) slots[`${k}.note`] = text(m[3]);
    });
    // the three bar charts' hover lines, one a group
    const charts = {};
    for (const m of html.matchAll(/<svg[^>]*data-bars="([^"]+)"[^>]*>([\s\S]*?)<\/svg>/g)) {
      const n = { "growth-by-grid": "bar1", "growth-by-window": "bar2", "demand-by-year": "bar3" }[m[1]];
      charts[m[1]] = 0;
      for (const g of m[2].matchAll(/<g data-group="([^"]*)">([\s\S]*?)<\/g>/g)) {
        const title = g[2].match(/<title>([\s\S]*?)<\/title>/);
        const sub = [...g[2].matchAll(/<text[^>]*>([\s\S]*?)<\/text>/g)].map((t) => text(t[1]));
        slots[`${n}.${decode(g[1])}`] = title ? text(title[1]) : "";
        slots[`${n}.${decode(g[1])}.drawn`] = sub.join(" | ");
        charts[m[1]]++;
      }
    }
    // the two tables: "Every grid" (its caption begins "Growth since") and the grid's years
    const tables = [...html.matchAll(/<table[^>]*>([\s\S]*?)<\/table>/g)].map((m) => {
      const caption = text(m[1].match(/<caption[^>]*>([\s\S]*?)<\/caption>/)?.[1] ?? "");
      const rows = [...m[1].matchAll(/<tr[^>]*>([\s\S]*?)<\/tr>/g)].map((r) => cellsOf(r[1]));
      return { caption, head: rows[0].map(text), body: rows.slice(1) };
    });
    const every = tables.find((t) => t.caption.startsWith("Growth since"));
    if (every) {
      slots["grid.head"] = every.head.join(" | ");
      for (const r of every.body) {
        const slug = decode(r[0].match(/grid=([a-z0-9]+)/)?.[1] ?? text(r[0]));
        const names = ["name", "base", "latest", "growth", "change"];
        r.forEach((c, i) => { slots[`grid.${slug}.${names[i]}`] = text(c); });
      }
    }
    const yearly = tables.find((t) => !t.caption.startsWith("Growth since"));
    if (yearly) {
      slots["year.head"] = yearly.head.join(" | ");
      for (const r of yearly.body) {
        const y = text(r[0]).slice(0, 4);
        r.forEach((c, i) => { slots[`year.${y}.${i}`] = text(c); });
      }
    }
    const page = text(html);
    const fresh = [...html.matchAll(/data-fresh-table="([^"]+)" data-last-run="([^"]*)" data-ts-max="([^"]*)" data-held="([^"]*)"[^>]*>([\s\S]*?)<\/p>/g)].map((m) => ({ table: m[1], last_run: m[2], ts_max: m[3], held: m[4], words: text(m[5]) }));
    out.views.push({
      q: v.q, why: v.why, keyed: keys.length, keys, slots, charts, fresh,
      fresh_detail: text(html.match(/<div[^>]*data-fresh="[^"]*"[^>]*>[\s\S]*?<p class="mt-1 text-xs text-muted">([\s\S]*?)<\/p><\/div>/)?.[1] ?? ""),
      filters: Object.fromEntries([...html.matchAll(/<select[^>]*name="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)].map((m) => {
        const opts = [...m[2].matchAll(/<option([^>]*)>([\s\S]*?)<\/option>/g)];
        return [m[1], { chosen: decode(opts.find((o) => /\sselected(=""|\s|$)/.test(o[1]))?.[1].match(/value="([^"]*)"/)?.[1] ?? ""), options: opts.length }];
      })),
      asked_unknown: /data-asked-unknown="1"/.test(html),
      no_window: (html.match(/data-no-window="1"/g) ?? []).length,
      not_held: (html.match(/>not held<\/span>/g) ?? []).length,
      decisions: (html.match(/data-decision="/g) ?? []).length,
      titles: [...html.matchAll(/<h[1-4][^>]*>([\s\S]*?)<\/h[1-4]>/g)].map((m) => text(m[1])),
      chart_titles: [...html.matchAll(/<figcaption[^>]*><span class="font-serif text-xl text-accent">([\s\S]*?)<\/span>/g)].map((m) => text(m[1])),
      download: decode(html.match(/data-rows-download="[^"]+"[^>]*>[\s\S]*?<a href="([^"]+)"/)?.[1] ?? ""),
      grey: (html.match(/class="[^"]*\btext-muted\b[^"]*"/g) ?? []).length,
      em_dash: html.includes(String.fromCharCode(0x2014)) || html.includes(String.fromCharCode(0x2013)),
      undefined_or_nan: /\bundefined\b|\bNaN\b/.test(page),
      no_data: /data-no-data|role="status"/.test(html) && /could not be read|returned no rows/.test(page),
      length: html.length,
    });
  }
  out.asked = asked;
  fs.writeFileSync(outFile, JSON.stringify(out));
  const slots = out.views.reduce((n, v) => n + Object.keys(v.slots).length, 0);
  console.log(`${views.length} views drawn, ${slots} slots of text, ${Object.keys(out.keyed).length} distinct checked figures, ${out.conflicts.length} drawn two ways, ${asked} reads answered from the file; written to ${outFile}`);
  if (out.conflicts.length || out.views.some((v) => v.undefined_or_nan || v.em_dash)) process.exitCode = 1;
}
