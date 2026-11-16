// Energy Research Warehouse (ERW) site, session 7501 (chain 304): every figure of /contracts ("Where power contracts
// are being struck") and its four views, as the page draws it.
//
//   node --import ./scripts/tsx-register.mjs scripts/contracts-figures.mjs <rows dir> [--html <dir>]
//
// <rows dir> holds summary.json (the stored summary the page reads through internal_eqr_summary) and quarters/<q>.json
// (the rows internal_eqr_contracts answers for a quarter of execution), written by replication/contracts/copy_rows.py
// from the tables on the machine. The page's own default export (app/contracts/page.tsx) is called and drawn to HTML
// for every view, quarter, product and listed balancing authority; the two database functions are answered from those
// files by a stand-in for fetch, so no request leaves the machine. The figures are read off the HTML: what a reader of
// the internal view sees. Prints one JSON object: { figures: {key: number}, words: {key: text}, pages }. A key that
// names a party's own figure (a row of a ranking) and every party's name are internal: replication/contracts/
// replicate.py compares them and writes neither to a file. Nothing is written here unless --html names a folder.
import fs from "node:fs";
import { register } from "node:module";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";

// The page wraps what it draws in <Brand> (components/Brand.tsx), which loads the brand's three families through
// next/font/google: that exists only inside a build. Here the three are stand-ins with no file behind them; the
// scripts' shared loaders (tsx-loader, alias-loader) are left as they are.
register(`data:text/javascript,${encodeURIComponent(`
const SRC = "const f = (o) => ({ variable: o?.variable ?? '', className: '', style: { fontFamily: 'stand-in' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
export async function resolve(s, c, next) { return s === "next/font/google" ? { url: "erw-font-stub:google", shortCircuit: true } : next(s, c); }
export async function load(u, c, next) { return u === "erw-font-stub:google" ? { format: "module", source: SRC, shortCircuit: true } : next(u, c); }
`)}`);

const dir = process.argv[2];
const htmlAt = process.argv.indexOf("--html");
const htmlDir = htmlAt > 0 ? process.argv[htmlAt + 1] : null;
if (!dir || !fs.existsSync(path.join(dir, "summary.json"))) {
  console.error("usage: node --import ./scripts/tsx-register.mjs scripts/contracts-figures.mjs <rows dir with summary.json and quarters/>");
  process.exitCode = 2;
} else {
  await main();
}

async function main() {
  const summary = JSON.parse(fs.readFileSync(path.join(dir, "summary.json"), "utf-8"));
  // the page's read (app/contracts/read.ts) needs a database named and an internal token held; both are stand-ins here
  process.env.SUPABASE_URL = "https://rows.invalid";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  process.env.INTERNAL_COSTS_TOKEN = "stand-in-token-of-the-figures-script";
  let asked = 0;
  globalThis.fetch = async (url, init) => {
    asked++;
    const fn = String(url).split("/rpc/")[1] ?? "";
    const args = JSON.parse(init?.body ?? "{}");
    const answer = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
    if (fn === "internal_eqr_summary") return answer(summary);
    if (fn === "internal_eqr_contracts") {
      const q = `${args.p_from.slice(0, 4)}-Q${Math.floor((Number(args.p_from.slice(5, 7)) - 1) / 3) + 1}`;
      const file = path.join(dir, "quarters", `${q}.json`);
      return answer(fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf-8")) : []);
    }
    return answer({ message: `the stand-in answers no ${url}` }, 404);
  };
  const { default: Page } = await import("../app/contracts/page.tsx");
  const C = await import("../lib/contracts.ts");

  const figures = {}, words = {};
  let pages = 0;
  const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\s+/g, " ").trim();
  const plain = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
  const num = (s) => { const v = Number(String(s).replace(/,/g, "")); return Number.isFinite(v) ? v : null; };
  const draw = async (q, name) => {
    const html = renderToStaticMarkup(await Page({ searchParams: Promise.resolve(q) }));
    pages++;
    if (htmlDir) { fs.mkdirSync(htmlDir, { recursive: true }); fs.writeFileSync(path.join(htmlDir, `${name}.html`), html); }
    return html;
  };
  /** Every <span data-n="k">1,234</span> of a page, under a prefix. A cell drawn "none filed" has no data-n and no key. */
  const marked = (html, prefix) => {
    for (const m of html.matchAll(/<span[^>]*\bdata-n="([^"]+)"[^>]*>([^<]*)<\/span>/g)) {
      const v = num(m[2]);
      if (v !== null && m[1] !== "unpriced") figures[`${prefix}|${m[1].replace(/&amp;/g, "&")}`] = v;   // the limits box is on every view: read once, below
    }
  };
  /** A headline cell's value by its label: the first number after the label in the page's text. */
  const after = (t, label) => { const i = t.indexOf(label); if (i < 0) return null; const m = t.slice(i + label.length).match(/-?[\d,]+(\.\d+)?/); return m ? num(m[0]) : null; };
  const put = (key, v) => { if (v !== null && v !== undefined) figures[key] = v; };

  // 1. the contracts by the quarter signed: the page as it opens, then every quarter listed and every product
  const open = await draw({}, "quarter-default");
  const t0 = text(open);
  const held = [...open.matchAll(/href="\/contracts\?q=(\d{4}-Q[1-4])&amp;product=power"[^>]*>[^<]*<\/a>\s*(?:<!-- -->)?\s*<span[^>]*>([\d,]+)(?:<!-- -->)? rows<\/span>/g)].map((m) => ({ quarter: m[1], rows: num(m[2]) }));
  words["quarter|listed"] = held.map((h) => h.quarter).join(" ");
  words["quarter|default"] = (open.match(/aria-current="true"[^>]*>(\d{4} Q[1-4])</) ?? [])[1] ?? "";
  for (const h of held) put(`panel|quarter_rows|${h.quarter}`, h.rows);
  put("panel|later_rows", num((open.match(/data-later="(\d+)"/) ?? [])[1] ?? ""));
  words["panel|later_last"] = (t0.match(/the latest in (\d{4} Q[1-4])/) ?? [])[1] ?? "";
  put("limits|unpriced", num((open.match(/data-n="unpriced">([^<]*)</) ?? [])[1] ?? ""));
  put("limits|rows_held", after(t0, "Of the "));
  const ercot = t0.match(/([\d,]+) of the ([\d,]+) rows held here name ERCOT/);
  if (ercot) { put("cannot_see|ercot_rows", num(ercot[1])); put("cannot_see|rows_held", num(ercot[2])); }
  const span = t0.match(/The rows held were executed from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})/);
  if (span) { words["panel|first"] = span[1]; words["panel|last"] = span[2]; }
  words["panel|filed_for"] = (t0.match(/Filed for ([^.]+)\./) ?? [])[1] ?? "";
  words["panel|as_filed_marks_in_note"] = /executed from \S+ to \S+ as filed/.test(t0) ? "yes" : "no";
  words["panel|oldest_quarter_from"] = (open.match(/data-held-from="[^"]+">Held\s+from (?:<!-- -->)?(\d{4}-\d{2}-\d{2})/) ?? [])[1] ?? "";

  const quarterPage = async (quarter, product, ba) => {
    const html = await draw({ q: quarter, product: product.slug, ...(ba ? { ba } : {}) }, `quarter-${quarter}-${product.slug}${ba ? `-${ba.replace(/[^A-Za-z0-9]/g, "_")}` : ""}`);
    const t = text(html), k = `quarter|${quarter}|${product.slug}|${ba ?? "every"}`;
    const s = html.match(/<p[^>]*data-summary="1"[^>]*>([\s\S]*?)<\/p>/);
    if (s) for (const m of s[1].matchAll(/data-n="([^"]+)">([^<]*)</g)) put(`${k}|${m[1]}`, num(m[2]));
    put(`${k}|headline_rows`, after(t, "Contract rows signed that quarter"));
    put(`${k}|headline_priced`, after(t, "Rows with a price as a number"));
    put(`${k}|headline_unpriced`, num((t.match(/The other ([\d,]+) give words/) ?? [])[1] ?? ""));
    put(`${k}|headline_affiliate`, after(t, "Between affiliates"));
    put(`${k}|table_rows_drawn`, (html.match(/<tbody>([\s\S]*?)<\/tbody>/)?.[1].match(/<tr\b/g) ?? []).length);
    put(`${k}|as_filed_marks`, (html.match(/data-as-filed="1"/g) ?? []).length);
    const years = [...html.matchAll(/\((\d+\.\d) years\)/g)].map((m) => Number(m[1]));
    put(`${k}|terms_in_years_drawn`, years.length);
    if (years.length) put(`${k}|longest_term_years_drawn`, Math.max(...years));
    return html;
  };
  for (const h of held) {
    for (const p of C.PRODUCTS) {
      const html = await quarterPage(h.quarter, p, null);
      // the panel's "Delivered in" list: the balancing authorities of the quarter and product, most rows first
      const nav = html.match(/<nav aria-label="Delivered in"[\s\S]*?<\/nav>/)?.[0] ?? "";
      const bas = [...nav.matchAll(/<a [^>]*>([^<]+)<\/a>\s*(?:<!-- -->)?\s*<span[^>]*>([\d,]+)<\/span>/g)].map((m) => ({ ba: plain(m[1]), rows: num(m[2]) }));
      put(`panel|ba_listed|${h.quarter}|${p.slug}`, bas.length);
      bas.forEach((b, i) => { put(`panel|ba_rows|${h.quarter}|${p.slug}|${i + 1}`, b.rows); words[`panel|ba_name|${h.quarter}|${p.slug}|${i + 1}`] = b.ba; });
      if (h === held[0] && p.slug === "power") for (const b of bas) if (/^[A-Za-z0-9 ._-]{1,40}$/.test(b.ba)) await quarterPage(h.quarter, p, b.ba);
    }
  }

  // 2. the largest buyers and sellers, 3. ranked by megawatts stated: each of the three products
  for (const p of C.LARGEST_PRODUCTS) {
    const big = await draw({ view: "largest", product: p.slug }, `largest-${p.slug}`);
    marked(big, `largest|${p.slug}`);
    const tb = text(big);
    put(`largest|${p.slug}|product_rows`, after(tb, "Contracts in force ") === null ? null : num((tb.match(/([\d,]+) product rows/) ?? [])[1] ?? ""));
    put(`largest|${p.slug}|listed_top`, num((tb.match(/The first (\d+) of/) ?? [])[1] ?? ""));
    words[`largest|${p.slug}|quarter`] = (tb.match(/Contracts in force in the filings for (\d{4} Q[1-4])/) ?? [])[1] ?? "";
    for (const m of big.matchAll(/data-party="([^"]+)">([^<]*)</g)) words[`largest|${p.slug}|party|${m[1]}`] = plain(m[2]);
    put(`largest|${p.slug}|cells_none_filed`, (big.match(/>none filed</g) ?? []).length);
    const mw = await draw({ view: "mw", product: p.slug }, `mw-${p.slug}`);
    marked(mw, `mw|${p.slug}`);
    const tm = text(mw);
    put(`mw|${p.slug}|ceiling`, num((tm.match(/They state more than ([\d,]+) MW/) ?? [])[1] ?? ""));
    put(`mw|${p.slug}|rows_over_every_product`, num((tm.match(/Across every product ([\d,]+) rows do/) ?? [])[1] ?? ""));
    put(`mw|${p.slug}|in_force_in_headline`, num((tm.match(/Of ([\d,]+) in force\./) ?? [])[1] ?? ""));
    words[`mw|${p.slug}|quarter`] = (tm.match(/Contracts in force in the filings for (\d{4} Q[1-4])/) ?? [])[1] ?? "";
    for (const m of mw.matchAll(/data-party="([^"]+)">([^<]*)</g)) words[`mw|${p.slug}|party|${m[1]}`] = plain(m[2]);
  }

  // 4. what the filings state
  const terms = await draw({ view: "terms" }, "terms");
  marked(terms, "terms");
  const tt = text(terms);
  put("terms|headline_filed_number", num((tt.match(/([\d,]+) rows file a number/) ?? [])[1] ?? ""));
  put("terms|headline_neither", num((tt.match(/; ([\d,]+) file neither/) ?? [])[1] ?? ""));
  put("terms|read_usd_per_mwh", num((tt.match(/([\d,]+) of them in dollars per megawatt-hour/) ?? [])[1] ?? ""));
  for (const m of tt.matchAll(/(\d+) in (\$\/[A-Z-]+)/g)) put(`terms|read_by_unit|${m[2]}`, num(m[1]));
  put("terms|buyers_of_rows", num((tt.match(/of the ([\d,]+) rows carry a buyer name/) ?? [])[1] ?? ""));
  words["terms|quarter"] = (tt.match(/contract rows filed for (\d{4} Q[1-4])/) ?? [])[1] ?? "";

  // 5. the address a reader may type: a quarter not listed, a product not offered, a view not offered fall to the defaults
  const odd = text(await draw({ q: "2101-Q1", product: "nothing", view: "nothing" }, "odd-address"));
  words["odd_address|quarter"] = (odd.match(/were signed in (\d{4} Q[1-4])/) ?? [])[1] ?? "";

  // 6. what a server without the token draws (a visitor's server never holds one for a page in review, and the page says so)
  process.env.INTERNAL_COSTS_TOKEN = "";
  const none = await draw({}, "no-token");
  words["no_token|says"] = (text(none).match(/The contract table is internal[^.]*\./) ?? [""])[0];
  put("no_token|figures_drawn", (none.match(/data-n="/g) ?? []).length);
  put("no_token|table_rows_drawn", (none.match(/<tbody>/g) ?? []).length);

  process.stdout.write(JSON.stringify({ figures, words, pages, asked }));
}
