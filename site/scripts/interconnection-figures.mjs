// Energy Research Warehouse (ERW) site, session 7509 (chain 304): every figure of the interconnection queue explorer
// (/explore/interconnection), as the page itself draws it, for every queue, both counts (positions and MW) and every
// first and last entry year the page offers.
//
//   node --import ./scripts/tsx-register.mjs scripts/interconnection-figures.mjs <iso_queue_statistics.csv> <out.json> [--coverage=<coverage.csv>] [--grid] [--html=<dir>]
//
// The page (app/explore/interconnection/page.tsx) is drawn to HTML with the site's own code, once a view. Its reads of
// the live set (lib/supabase.ts: the rows of the table, its header lines, the catalogue) are answered here, in the
// process, from the table file named and, when given, from warehouse/metadata/coverage.csv (the catalogue is that
// file, loaded). Nothing is asked of a server and nothing is written but <out.json>. From each view's HTML it keeps:
// every checked number (its key, the value read and the text shown, in the order drawn), the three headline numbers
// with their labels and the first year's figure under each, the filters as drawn (what is chosen, which years are
// marked partial), the rows of the two tables, the lines the page says (the first build's fault, what a queue does not
// hold, a held queue, an address the table does not hold) and the count of cells that say "not held".
// A held queue (license needed) is drawn as the page draws it: its rows are never read and no figure of it is kept.
// The views: each queue in each count as it opens; for a queue that is shown, every first entry year with the default
// last one and every last entry year with the default first one; --grid adds every pair of years (several minutes).
// replication/interconnection/replicate.py sets these beside its own reading of the table. No effect, no click.
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
  console.error("usage: node --import ./scripts/tsx-register.mjs scripts/interconnection-figures.mjs <iso_queue_statistics.csv> <out.json> [--coverage=<coverage.csv>] [--grid] [--html=<dir>]");
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
  // the four columns the page reads are the first four and hold no comma; a later column may (x_rule), and is not read
  const rows = lines.slice(1).map((l) => {
    const c = l.split(",");
    return { entity: c[ix.entity], variable: c[ix.variable], ts_utc: c[ix.ts_utc], value: Number(c[ix.value]) };
  });
  return { header, rows };
}

async function main() {
  const TABLE = "iso_queue_statistics";
  const T = { [TABLE]: readTable(tableFile) };
  const coverageFile = flags.find((f) => f.startsWith("--coverage="))?.slice(11);
  let catalogue = [];
  if (coverageFile) {
    const lines = fs.readFileSync(coverageFile, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
    const cols = lines[0].split(",");
    catalogue = lines.slice(1).map((l) => Object.fromEntries(l.split(",").map((v, i) => [cols[i], v])))
      .filter((r) => r.table === TABLE || /_interconnection_queue$/.test(r.table))
      .map((r) => ({ table_name: r.table, interval: r.interval, ts_min: r.ts_min, ts_max: r.ts_max, n_rows: Number(r.n_rows), last_run: r.last_run, license: r.license, in_live_set: "yes" }));
  }

  // the page's reads, answered from the file: GET <base>/rest/v1/<series|headers|catalogue>?...
  process.env.SUPABASE_URL = "http://interconnection-figures.invalid";
  process.env.SUPABASE_ANON_KEY = "local";
  const eq = (f) => (f?.startsWith("eq.") ? f.slice(3) : null);
  const among = (f) => (f?.startsWith("in.(") ? f.slice(4, -1).split(",").map((x) => x.replace(/^"|"$/g, "")) : null);
  const like = (f) => (f?.startsWith("like.") ? new RegExp(`^${f.slice(5).replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*")}$`) : null);
  let asked = 0;
  const askedOf = [];
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    const q = Object.fromEntries(u.searchParams);
    asked++;
    let out = [];
    const t = T[eq(q.table_name) ?? ""];
    if (u.pathname === "/rest/v1/series" && t) {
      const one = eq(q.entity), set = among(q.entity), re = like(q.entity);
      if (q.entity !== undefined) askedOf.push(q.entity);
      out = t.rows.filter((r) => (q.entity === undefined) || (one !== null && r.entity === one) || (set !== null && set.includes(r.entity)) || (re !== null && re.test(r.entity)));
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
  const Q = await import("../lib/explore/interconnection.ts");
  const { licenseHeldGrid } = await import("../lib/license.ts");
  const { default: Page } = await import("../app/explore/interconnection/page.tsx");
  const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
  const text = (html) => decode(html.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
  // the page is an async server component and so is its freshness line: the static prerender waits for both
  const draw = async (q) => {
    const { prelude } = await prerenderToNodeStream(h(Page, { searchParams: Promise.resolve(q) }));
    const parts = [];
    for await (const c of prelude) parts.push(Buffer.from(c));
    return Buffer.concat(parts).toString("utf-8");
  };

  const held = Q.QUEUES.map(([k]) => k).filter((k) => licenseHeldGrid(k));
  const views = [{ q: {}, why: "the page as it opens" }];
  for (const [queue] of Q.QUEUES) {
    for (const measure of Q.MEASURES.map((m) => m.key)) {
      views.push({ q: { queue, measure }, why: "no year named" });
      if (held.includes(queue)) continue;
      const years = [...new Set(T[TABLE].rows.filter((r) => r.entity.startsWith(`${queue}:queue_`)).map((r) => Q.yearOf(r.entity)))].sort((a, b) => a - b);
      for (const y of years) {
        views.push({ q: { queue, measure, from: String(y) }, why: "a first entry year" });
        views.push({ q: { queue, measure, to: String(y) }, why: "a last entry year" });
      }
      if (flags.includes("--grid")) for (const a of years) for (const b of years) views.push({ q: { queue, measure, from: String(a), to: String(b) }, why: "a pair of years" });
    }
  }
  views.push({ q: { queue: "caiso", from: "2020", to: "2010" }, why: "the years the other way round" });
  views.push({ q: { queue: "spp", measure: "mw", from: "2019", to: "2019" }, why: "one year alone" });
  views.push({ q: { queue: "pjm", measure: "gw", from: "1066", to: "2999" }, why: "an address the table does not hold" });
  // session 7518 (chain 304, part B): --only=<query>;<query> draws the named addresses and no other ("queue=spp&from=2018&to=2018;queue=pjm"),
  // for a reader's case read start to finish and for a test that needs a few views, not the 284
  const only = flags.find((f) => f.startsWith("--only="))?.slice(7);
  if (only !== undefined) {
    views.length = 0;
    for (const one of only.split(";")) views.push({ q: Object.fromEntries(new URLSearchParams(one)), why: "named by --only" });
  }

  const out = { table_file: tableFile, table_rows: T[TABLE].rows.length, held, views: [], keyed: {}, conflicts: [] };
  const htmlDir = flags.find((f) => f.startsWith("--html="))?.slice(7);
  const tableOf = (html, captionStart) => {
    const m = html.match(new RegExp(`<table[^>]*><caption[^>]*>${captionStart}[\\s\\S]*?</table>`));
    if (!m) return null;
    const head = [...m[0].matchAll(/<th scope="col"[^>]*>([\s\S]*?)<\/th>/g)].map((x) => text(x[1]));
    const body = m[0].slice(m[0].indexOf("<tbody>"));
    const rows = [...body.matchAll(/<tr class="([^"]*)">([\s\S]*?)<\/tr>/g)].map((r) => ({
      // session 7518: a row's label may carry a tip (ERCOT's status words in the six queues' table); the label is the words before it
      label: text((r[2].match(/<th scope="row"[^>]*>([\s\S]*?)<\/th>/)?.[1] ?? "").replace(/<span class="tip[\s\S]*$/, "")),
      label_tip: text(r[2].match(/<th scope="row"[^>]*>[\s\S]*?<span role="tooltip"[^>]*>([\s\S]*?)<\/span>/)?.[1] ?? "") || null,
      muted: /\btext-muted\b/.test(r[1]), highlight: /\bfont-semibold\b/.test(r[1]),
      cells: [...r[2].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((c) => {
        const k = c[1].match(/data-check="([^"]+)"/);
        return k ? decode(k[1]) : text(c[1]);
      }),
    }));
    return { head, rows };
  };
  for (const v of views) {
    asked = 0; askedOf.length = 0;
    const html = await draw(v.q);
    if (htmlDir) fs.writeFileSync(`${htmlDir}/interconnection_${Object.entries(v.q).map(([k, x]) => `${k}-${x.replace(/[^A-Za-z0-9_]/g, "_")}`).join("_") || "opening"}.html`, html);
    const keys = [];
    for (const m of html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"([^>]*)>([\s\S]*?)<\/span>/g)) {
      const key = decode(m[1]), value = { raw: Number(m[2]), text: text(m[4]), source: decode(m[3].match(/title="([^"]*)"/)?.[1] ?? "") };
      keys.push(key);
      if (key in out.keyed && JSON.stringify(out.keyed[key]) !== JSON.stringify(value)) out.conflicts.push({ key, first: out.keyed[key], second: value });
      out.keyed[key] = value;
    }
    const filters = {};
    for (const m of html.matchAll(/<select[^>]*name="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)) {
      const opts = [...m[2].matchAll(/<option([^>]*)>([\s\S]*?)<\/option>/g)].map((o) => ({ value: decode(o[1].match(/value="([^"]*)"/)?.[1] ?? ""), label: text(o[2]), selected: /\sselected(=""|\s|$)/.test(o[1]) }));
      filters[m[1]] = { chosen: opts.find((o) => o.selected)?.value ?? null, marked: opts.filter((o) => /\((partial|license needed)\)/.test(o.label)).map((o) => o.label), options: opts.length };
    }
    // the three headline numbers: the label, the figure's key (or the words in its place) and the first year's under it
    const headlines = [...html.matchAll(/<div class="border-t-2 border-accent pt-2"><div class="text-xs uppercase tracking-wide text-muted">([\s\S]*?)<\/div><div class="mt-1 font-serif text-3xl tabular-nums text-ink">([\s\S]*?)<\/div>(?:<div class="mt-1 text-xs leading-snug text-muted">([\s\S]*?)<\/div>)?<\/div>/g)].map((m) => ({
      label: text(m[1].replace(/<span class="normal-case[\s\S]*$/, "")),
      key: decode(m[2].match(/data-check="([^"]+)"/)?.[1] ?? "") || text(m[2]),
      note: m[3] ? text(m[3]) : null,
      note_key: m[3] ? decode(m[3].match(/data-check="([^"]+)"/)?.[1] ?? "") : null,
    }));
    const page = text(html);
    out.views.push({
      q: v.q, why: v.why, keyed: keys.length, keys, filters, headlines,
      years_table: tableOf(html, "[^<]*queue by entry year and status"),
      queues_table: tableOf(html, "The six queues"),
      fault: html.match(/data-queue-fault="([^"]*)"/)?.[1] ?? null,
      not_held_line: html.match(/data-queue-not-held="([^"]*)"/)?.[1] ?? null,
      held_line: text(html.match(/<p[^>]*role="status" data-license-held="[^"]*"[^>]*>([\s\S]*?)<\/p>/)?.[1] ?? "") || null,
      license_cells: (html.match(/data-license-held="/g) ?? []).length,
      asked_unknown: text(html.match(/<span data-asked-unknown="1">([\s\S]*?)<\/span>/)?.[1] ?? "") || null,
      not_held: (html.match(/<span class="text-muted">not held<\/span>/g) ?? []).length,
      fresh_state: html.match(/data-fresh="([^"]+)"/)?.[1] ?? null,
      built_line: page.match(/The table's header says it was built at ([^.]*)\./)?.[1] ?? null,
      undated_line: page.match(/The table's header counts ([\d,]+) of ([A-Z-]+)'s positions with no queue date/)?.slice(1, 3) ?? null,
      // session 7518: a chart's title may carry a tip (the wait's); the title is the words before it
      charts: [...html.matchAll(/<figcaption[^>]*>\s*<span[^>]*>([\s\S]*?)<\/span>/g)].map((m) => text(m[1].replace(/<span class="tip[\s\S]*$/, ""))),
      wait_tip: text(html.match(/<span role="tooltip" id="tip-wait-counts"[^>]*>([\s\S]*?)<\/span>/)?.[1] ?? "") || null,
      load_side: text(html.match(/<p[^>]*data-load-side="1"[^>]*>([\s\S]*?)<\/p>/)?.[1] ?? "") || null,
      related: text(html.match(/<p[^>]*data-related-view="1"[^>]*>([\s\S]*?)<\/p>/)?.[1] ?? "") || null,
      asked_pjm: text(html.match(/<span data-asked-pjm="1">([\s\S]*?)<\/span>/)?.[1] ?? "") || null,
      held_elsewhere: html.match(/data-held-elsewhere="([^"]*)"/)?.[1] ?? null,
      links: [...new Set([...html.matchAll(/href="(\/(?:queues|datacenters|cost-of-power|map)[^"]*)"/g)].map((m) => decode(m[1])))],
      status_chart: /data-queue-status-chart="/.test(html),
      decisions: (html.match(/data-decision="/g) ?? []).length,
      titles: [...html.matchAll(/<h[1-4][^>]*>([\s\S]*?)<\/h[1-4]>/g)].map((m) => text(m[1])),
      reads: asked, read_entities: [...askedOf],
      length: html.length,
    });
  }
  fs.writeFileSync(outFile, JSON.stringify(out));
  console.log(`${views.length} views drawn, ${Object.keys(out.keyed).length} distinct checked figures, ${out.conflicts.length} drawn two ways; held and not read: ${held.join(", ") || "none"}; written to ${outFile}`);
  if (out.conflicts.length) process.exitCode = 1;
}
