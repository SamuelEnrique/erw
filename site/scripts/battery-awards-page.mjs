// Energy Research Warehouse (ERW) site, session 7514 (chain 304, part B): the whole page /cost-of-power/battery/awards
// drawn to HTML without a build, from its reads to its last cell. Session 7505's battery-awards-figures.mjs drew the two
// section components and wrote the head of the page cell by cell; here the page's own function is called
// (app/cost-of-power/battery/awards/page.tsx) and its reads are answered by a stand-in for fetch, from rows given by the
// caller. No network, no table written, no click, no chart seen.
//
//   node --import ./scripts/battery-awards-page-register.mjs scripts/battery-awards-page.mjs <tables dir> <out.html> <out.txt>
//
// <tables dir> holds the tables as the warehouse writes them (CSV with a "#" header). out.txt is the page as a reader
// meets it, one line a block: a table row's cells joined by " | ", a bar's hover as "[hover]", a tip as "[tip]", and a
// cell's own hover as "[title]".
// A test imports drawPage and gives it the rows itself (scripts/test-battery-awards-read.mjs).
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";

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

/** The page drawn on the rows `rowsOf(table)` gives (an array of { entity, variable, ts_utc, value }, or null for a
 * table that cannot be read, which answers as a failed request). Returns the HTML and the reads the page made. */
export async function drawPage(rowsOf) {
  process.env.SUPABASE_URL = "http://localhost:9/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  const asked = [];
  const real = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const q = new URL(String(url)).searchParams;
    const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
    const entity = (q.get("entity") ?? "").replace(/^eq\./, "");
    const vars = new Set((q.get("variable") ?? "").replace(/^in\.\(/, "").replace(/^eq\./, "").replace(/\)$/, "").split(","));   // eq.: wip/alt-battery-awards-4
    const from = (q.get("ts_utc") ?? "").replace(/^gte\./, "");
    const limit = Number(q.get("limit") ?? 1000), offset = Number(q.get("offset") ?? 0);
    const all = rowsOf(name);
    if (all === null) { asked.push(`${name} ${entity}: not answered`); return new Response("stand-in: the table is not held", { status: 404 }); }
    const rows = all.filter((r) => (!entity || r.entity === entity) && vars.has(r.variable) && (!from || r.ts_utc >= from));   // no entity: every entity (wip/alt-battery-awards-4)
    rows.sort((a, b) => (a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : a.ts_utc < b.ts_utc ? -1 : a.ts_utc > b.ts_utc ? 1 : 0));
    asked.push(`${name} ${entity}: ${rows.length} rows`);
    return new Response(JSON.stringify(rows.slice(offset, offset + limit).map((r) => ({ entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value) }))),
      { status: 200, headers: { "content-type": "application/json" } });
  };
  const log = console.error;
  console.error = () => {};  // a read that fails is said on the page; the server's own line about it is not wanted here
  try {
    const { default: Awards } = await import("../app/cost-of-power/battery/awards/page.tsx");
    return { html: renderToStaticMarkup(await Awards()), asked };
  } finally {
    globalThis.fetch = real;
    console.error = log;
  }
}

const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
/** The drawn page as lines of text, with every hover kept and marked. */
export function pageText(html) {
  const t = html
    .replace(/<title>([\s\S]*?)<\/title>/g, "\n[hover] $1\n")
    .replace(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span><\/span>/g, "\n[tip] $1\n")
    .replace(/<(span|abbr)[^>]* title="([^"]*)"[^>]*>/g, " [title: $2] ")
    .replace(/<\/(th|td)>/g, " | ")
    .replace(/<(h1|h2|h3|p|li|tr|caption|summary|figcaption|section|nav|aside|svg)([ >])/g, "\n<$1$2")
    .replace(/<[^>]+>/g, " ");
  return ent(t).split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [dir, outHtml, outTxt] = process.argv.slice(2);
  if (!dir || !outHtml || !outTxt) { console.error("usage: battery-awards-page.mjs <tables dir> <out.html> <out.txt>"); process.exitCode = 2; }
  else {
    const cache = new Map();
    const rowsOf = (name) => {
      if (!cache.has(name)) { const f = path.join(dir, `${name}.csv`); cache.set(name, fs.existsSync(f) ? tableRows(f) : null); }
      return cache.get(name);
    };
    const { html, asked } = await drawPage(rowsOf);
    const text = pageText(html);
    fs.writeFileSync(outHtml, html);
    fs.writeFileSync(outTxt, text + "\n");
    console.log(asked.join("\n"));
    console.log(`${html.length} bytes of HTML; ${text.split("\n").length} lines of text`);
  }
}
