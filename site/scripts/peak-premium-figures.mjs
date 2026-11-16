// Energy Research Warehouse (ERW) site, session 7507 (chain 304): every figure of the ERCOT peak premium explorer
// (/explore/ercot-peak-premium), as the page itself draws it, for every hub, every period (the whole year and each of
// the twelve months) and every year the page offers.
//
//   node --import ./scripts/tsx-register.mjs scripts/peak-premium-figures.mjs <annual.csv> <monthly.csv> <out.json> [--coverage=<coverage.csv>] [--opening] [--html=<dir>]
//
// The page (app/explore/ercot-peak-premium/page.tsx) is drawn to HTML with the site's own code, once a view. Its reads
// of the live set (lib/supabase.ts: the rows of the two tables, their header lines, the catalogue) are answered here,
// in the process, from the two table files named and, when given, from warehouse/metadata/coverage.csv (the catalogue
// is that file, loaded). Nothing is asked of a server and nothing is written but <out.json>. From each view's HTML it
// keeps: every checked number (its key, the value read and the text shown, in the order drawn: the first six of a view
// of two years are the three headline numbers, each with the first year's under it), the filters as drawn (what is
// chosen, which years are marked partial or not held), the freshness line, the words that mark a partial period and
// the address of the rows' download. The charts draw the same rows (the server's HTML holds their axes, not their
// points: a browser read). replication/ercot_peak_premium/replicate.py sets these beside its own reading of
// the tables. --opening draws only the views a reader meets with no year named. It runs no effect and no click.
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

const [annualFile, monthlyFile, outFile, ...flags] = process.argv.slice(2);
if (!annualFile || !monthlyFile || !outFile) {
  console.error("usage: node --import ./scripts/tsx-register.mjs scripts/peak-premium-figures.mjs <annual.csv> <monthly.csv> <out.json> [--coverage=<coverage.csv>] [--opening] [--html=<dir>]");
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
  const T = { ercot_peak_premium_annual: readTable(annualFile), ercot_peak_premium_monthly: readTable(monthlyFile) };
  const coverageFile = flags.find((f) => f.startsWith("--coverage="))?.slice(11);
  let catalogue = [];
  if (coverageFile) {
    const lines = fs.readFileSync(coverageFile, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
    const cols = lines[0].split(",");
    catalogue = lines.slice(1).map((l) => Object.fromEntries(l.split(",").map((v, i) => [cols[i], v])))
      .filter((r) => r.table in T)
      .map((r) => ({ table_name: r.table, interval: r.interval, ts_min: r.ts_min, ts_max: r.ts_max, n_rows: Number(r.n_rows), last_run: r.last_run, license: r.license, in_live_set: "yes" }));
  }

  // the page's reads, answered from the files: GET <base>/rest/v1/<series|headers|catalogue>?...
  process.env.SUPABASE_URL = "http://peak-premium-figures.invalid";
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
    const t = T[eq(q.table_name) ?? ""];
    if (u.pathname === "/rest/v1/series" && t) {
      const ent = one(q.entity), vars = one(q.variable), when = one(q.ts_utc)?.map((x) => new Date(x).getTime());
      out = t.rows.filter((r) => (!ent || ent.includes(r.entity)) && (!vars || vars.includes(r.variable)) && (!when || when.includes(new Date(r.ts_utc).getTime())));
      const keys = (q.order ?? "").split(",").filter(Boolean);
      out = out.slice().sort((a, b) => { for (const k of keys) { if (a[k] < b[k]) return -1; if (a[k] > b[k]) return 1; } return 0; });
    } else if (u.pathname === "/rest/v1/headers" && t) {
      out = t.header.map((line) => ({ line }));
    } else if (u.pathname === "/rest/v1/catalogue") {
      out = catalogue;
    }
    const offset = Number(q.offset ?? 0), limit = Number(q.limit ?? 1000);
    out = out.slice(offset, offset + limit);
    return new Response(JSON.stringify(out), { status: 200, headers: { "Content-Type": "application/json" } });
  };

  const { prerenderToNodeStream } = await import("react-dom/static");
  const P = await import("../lib/explore/peakpremium.ts");
  const { default: Page } = await import("../app/explore/ercot-peak-premium/page.tsx");
  const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
  const text = (html) => decode(html.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
  // the page is an async server component and so is its freshness line: the static prerender waits for both
  const draw = async (q) => {
    const { prelude } = await prerenderToNodeStream(h(Page, { searchParams: Promise.resolve(q) }));
    const parts = [];
    for await (const c of prelude) parts.push(Buffer.from(c));
    return Buffer.concat(parts).toString("utf-8");
  };

  const annual = T[P.ANNUAL].rows;
  const hubs = [...new Set(annual.filter((r) => r.variable === "n_intervals").map((r) => r.entity))].sort();
  const views = [{ q: {}, why: "the page as it opens" }];
  for (const hub of hubs) {
    const years = [...new Set(annual.filter((r) => r.entity === hub && r.variable === "n_intervals").map((r) => new Date(r.ts_utc).getUTCFullYear()))].sort((a, b) => a - b);
    for (const month of ["", ...Array.from({ length: 12 }, (_, i) => String(i + 1))]) {
      views.push({ q: { hub, ...(month ? { month } : {}) }, why: "no year named" });
      if (flags.includes("--opening")) continue;
      for (let i = 0; i < years.length; i += 2) {
        const pair = years.slice(i, i + 2);
        views.push({ q: { hub, ...(month ? { month } : {}), from: String(pair[0]), to: String(pair[pair.length - 1]) }, why: "a pair of years" });
      }
    }
  }
  // a year against itself, and an address the tables do not hold
  views.push({ q: { hub: P.THESIS_HUB, from: "2021", to: "2021" }, why: "one year alone" });
  views.push({ q: { hub: "ercot:HB_NOWHERE", month: "13", from: "1999", to: "2031" }, why: "an address the tables do not hold" });

  const out = { annual_file: annualFile, monthly_file: monthlyFile, annual_rows: annual.length, monthly_rows: T[P.MONTHLY].rows.length, views: [], keyed: {}, conflicts: [] };
  const htmlDir = flags.find((f) => f.startsWith("--html="))?.slice(7);
  for (const v of views) {
    const html = await draw(v.q);
    if (htmlDir) fs.writeFileSync(`${htmlDir}/peak_${Object.entries(v.q).map(([k, x]) => `${k}-${x.replace(/[^A-Za-z0-9_]/g, "_")}`).join("_") || "opening"}.html`, html);
    const keys = [];
    for (const m of html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)) {
      const key = decode(m[1]), value = { raw: Number(m[2]), text: text(m[3]) };
      keys.push(key);
      if (key in out.keyed && JSON.stringify(out.keyed[key]) !== JSON.stringify(value)) out.conflicts.push({ key, first: out.keyed[key], second: value });
      out.keyed[key] = value;
    }
    // the filters as drawn: the option chosen of each select, and the years' marks
    const filters = {};
    for (const m of html.matchAll(/<select[^>]*name="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)) {
      const opts = [...m[2].matchAll(/<option([^>]*)>([\s\S]*?)<\/option>/g)].map((o) => ({ value: decode(o[1].match(/value="([^"]*)"/)?.[1] ?? ""), label: text(o[2]), selected: /\sselected(=""|\s|$)/.test(o[1]) }));
      filters[m[1]] = { chosen: opts.find((o) => o.selected)?.value ?? null, marked: opts.filter((o) => /\((partial|not held)\)/.test(o.label)).map((o) => o.label), options: opts.length };
    }
    const fresh = [...html.matchAll(/data-fresh-table="([^"]+)" data-last-run="([^"]*)" data-ts-max="([^"]*)"[^>]*>([\s\S]*?)<\/p>/g)].map((m) => ({ table: m[1], last_run: m[2], ts_max: m[3], words: text(m[4]) }));
    const page = text(html);
    out.views.push({
      q: v.q, why: v.why, keyed: keys.length, keys, filters, fresh,
      fresh_state: html.match(/data-fresh="([^"]+)"/)?.[1] ?? null,
      asked_unknown: /data-asked-unknown="1"/.test(html),
      thesis_chart: /data-thesis-chart="1"/.test(html),
      not_held: (html.match(/<span class="text-muted">not held<\/span>/g) ?? []).length,
      unit_beside_not_held: /not held<\/span>\s*(<!-- -->)?\s*(<span[^>]*>)?\s*USD\/MWh/.test(html),
      titles: [...html.matchAll(/<h[1-4][^>]*>([\s\S]*?)<\/h[1-4]>/g)].map((m) => text(m[1])),
      partial_words: [...page.matchAll(/([A-Z]?[a-z]* ?\d{4}(?: and [A-Z]?[a-z]* ?\d{4})?) is partial/g)].map((m) => m[0]),
      newest_interval: page.match(/The newest 15-minute interval the tables were computed from starts ([^(]+?) \(/)?.[1] ?? null,
      download: decode(html.match(/data-rows-download="[^"]+"[^>]*>[\s\S]*?<a href="([^"]+)"/)?.[1] ?? ""),
      length: html.length,
    });
  }
  out.asked = asked;
  fs.writeFileSync(outFile, JSON.stringify(out));
  console.log(`${views.length} views drawn, ${Object.keys(out.keyed).length} distinct checked figures, ${out.conflicts.length} drawn two ways, ${asked} reads answered from the files; written to ${outFile}`);
  if (out.conflicts.length) process.exitCode = 1;
}
