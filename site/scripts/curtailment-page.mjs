// Energy Research Warehouse (ERW) site, session 7544 (chain 304, part C): the whole page /curtailment drawn to HTML
// without a build, for one address, from its reads to its last cell. The page's own function is called
// (app/curtailment/page.tsx) with the address's query, and its two reads of the live set (the monthly table and the
// grid's daily table) are answered by a stand-in for fetch, from rows the caller gives. The site's files under
// site/data/curtailment/ and site/data/curtailment_profile.json are read by the page itself, as on the site. No
// network, no table written, no click, no chart seen.
//
//   node --import ./scripts/battery-awards-page-register.mjs scripts/curtailment-page.mjs <tables dir> <out dir> [query ...]
//
// Each query is an address's query ("grid=ercot", "period=2026-04&dur=8", "" for the default); for each, <out dir>
// gets <n>.html and <n>.txt, the page as a reader meets it, one line a block, a hover as "[hover]" and "[title: ...]".
// A test imports drawPage and pageText and gives the rows itself (scripts/test-curtailment-read.mjs).
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

/** Rows of a warehouse CSV: entity, variable, ts_utc, value (the first four columns hold no comma in these tables). */
export function tableRows(file) {
  const rows = [];
  let head = false;
  for (const line of fs.readFileSync(file, "utf-8").split(/\r?\n/)) {
    if (!line || line.startsWith("#")) continue;
    if (!head) { head = true; continue; }
    const c = line.split(",");
    rows.push({ entity: c[0], variable: c[1], ts_utc: c[2], value: c[3] });
  }
  return rows;
}

/** The page drawn for one query (an object of the address's parameters) on the rows `rowsOf(table)` gives (null: the
 * table cannot be read, answered as a failed request). The day the page counts back from is `today` (a Date). */
export async function drawPage(rowsOf, query = {}, today = null) {
  process.env.SUPABASE_URL = "http://localhost:9/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  const asked = [];
  const real = globalThis.fetch, realNow = Date.now;
  if (today) Date.now = () => today.getTime();
  globalThis.fetch = async (url) => {
    const q = new URL(String(url)).searchParams;
    const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
    const entity = (q.get("entity") ?? "").replace(/^eq\./, "");
    const variable = (q.get("variable") ?? "").replace(/^eq\./, "");
    const from = (q.get("ts_utc") ?? "").replace(/^gte\./, "");
    const limit = Number(q.get("limit") ?? 100000), offset = Number(q.get("offset") ?? 0);
    const all = rowsOf(name);
    if (all === null) { asked.push(`${name} ${entity}: not answered`); return new Response("stand-in: the table is not held", { status: 404 }); }
    const rows = all.filter((r) => (!entity || r.entity === entity) && (!variable || r.variable === variable) && (!from || r.ts_utc >= from));
    rows.sort((a, b) => (a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : a.ts_utc < b.ts_utc ? -1 : a.ts_utc > b.ts_utc ? 1 : 0));
    asked.push(`${name} ${entity}: ${rows.length} rows`);
    return new Response(JSON.stringify(rows.slice(offset, offset + limit).map((r) => ({ entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value) }))),
      { status: 200, headers: { "content-type": "application/json" } });
  };
  const log = console.error;
  console.error = () => {};
  try {
    const { default: Page } = await import("../app/curtailment/page.tsx");
    // the page is an async server component and so is its downloads block: the static prerender waits for both
    const { prerenderToNodeStream } = await import("react-dom/static");
    const { prelude } = await prerenderToNodeStream(await Page({ searchParams: Promise.resolve(query) }));
    const parts = [];
    for await (const c of prelude) parts.push(Buffer.from(c));
    const html = Buffer.concat(parts).toString("utf-8").replace(/<script[\s\S]*?<\/script>/g, "").replace(/<!-- -->/g, "");
    return { html, asked };
  } finally {
    globalThis.fetch = real;
    Date.now = realNow;
    console.error = log;
  }
}

const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
/** The drawn page as lines of text, with every hover kept and marked. */
export function pageText(html) {
  const t = html
    .replace(/<title>([\s\S]*?)<\/title>/g, "\n[hover] $1\n")
    .replace(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span><\/span>/g, "\n[tip] $1\n")
    .replace(/<(span|abbr|a|div)[^>]* title="([^"]*)"[^>]*>/g, " [title: $2] ")
    .replace(/<\/(th|td)>/g, " | ")
    .replace(/<(h1|h2|h3|p|li|tr|caption|summary|figcaption|section|nav|aside|svg|figure)([ >])/g, "\n<$1$2")
    .replace(/<[^>]+>/g, " ");
  return ent(t).split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [dir, out, ...queries] = process.argv.slice(2);
  if (!dir || !out) { console.error("usage: curtailment-page.mjs <tables dir> <out dir> [query ...]"); process.exitCode = 2; }
  else {
    const cache = new Map();
    const rowsOf = (name) => {
      if (!cache.has(name)) { const f = path.join(dir, `${name}.csv`); cache.set(name, fs.existsSync(f) ? tableRows(f) : null); }
      return cache.get(name);
    };
    fs.mkdirSync(out, { recursive: true });
    const list = queries.length ? queries : [""];
    for (let i = 0; i < list.length; i += 1) {
      const query = Object.fromEntries(new URLSearchParams(list[i]));
      const { html, asked } = await drawPage(rowsOf, query);
      const text = pageText(html);
      fs.writeFileSync(path.join(out, `${i}.html`), html);
      fs.writeFileSync(path.join(out, `${i}.txt`), `/curtailment?${list[i]}\n${text}\n`);
      console.log(`${i} /curtailment?${list[i]}: ${asked.join("; ")}; ${text.split("\n").length} lines`);
    }
  }
}
