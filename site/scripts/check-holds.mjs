// Energy Research Warehouse (ERW) site, session 505: a check for held figures that show.
//
//   node scripts/check-holds.mjs [base] [--json <file>] [--csv <file>] [--browser] [--pages <prefix>[,<prefix>]]
//
// From 21 October 2026 a table whose publisher's own page asks for permission is "license needed" (lib/license.ts,
// warehouse/metadata/license_status.csv): a figure read from it is drawn as those words, through components/Num.tsx for
// a checked number and components/NoData.tsx for a held read. Session 474 found figures that escape the rule: the
// five-grid research cards draw NYISO's and ISO-NE's panels, callouts and regression tables through
// components/analysis/MultiChart.tsx, which never asks lib/license.ts. This check lists every such figure it can see on
// the pages check-values reads (`node scripts/check-values.mjs --list`), and changes no page: how a held panel is drawn
// is Samuel's ruling. It reads three things:
//
//   1. the checked numbers: every data-check key on a page, judged by Num's own rule (heldBy: the table a key names, by
//      its first word or its second, and the grid of its entity, or of iso=, or of a finding's last word). A key Num
//      would hold but which is drawn with data-check is a leak (a component writing the attribute itself); so is a key
//      whose first word Num does not read but which names a held table and, for a table held by grid, a held grid. The
//      catalogue's row counts, the licensing record's own figures (lic|) and a header's counts (series_hdr|) are records
//      about a table, not its figures, and are passed by.
//   2. the research cards' charts (data-finding on the card, data-finding-chart on its charts): a card whose tables
//      (site/data/findings/<card>.json) include a table held by grid, and whose small multiples draw a panel of one of
//      those grids (the panel's title or its series names the grid), leaks that panel. With --browser, each held grid's
//      one-grid view (?<param>=<grid>, drawn in the browser only) is opened, and its chart, callouts and table, if drawn
//      without the words, are listed.
//   3. possible leaks, to read by hand and not counted in the exit: on a page whose downloads line names a table held
//      by grid, a chart series (data-series) named for one of its held grids. Such a series may come from a public
//      table (EIA-930 reports every balancing authority), so it is listed, not judged.
//
// Exit 0: no leak on the pages read. 1: a leak (each listed). 2: bad input, or no page could be read. A page that does
// not answer within its timeout is tried once more, then listed as not read.
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { env, unlockPost, withBrowser } from "./browser.mjs";  // session 506: the door named as session 301 requires

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");

// the same maps as site/lib/license.ts and components/Num.tsx (tests/test_session505.py holds them equal)
export const GRID_PREFIX = { "ISO-NE": "isone", MISO: "miso", NYISO: "nyiso", PJM: "pjm", SPP: "spp", CAISO: "caiso", ERCOT: "ercot" };
const GRID_NAME = Object.fromEntries(Object.entries(GRID_PREFIX).map(([k, v]) => [v, k]));
export const KEY_TABLE = {
  deals: "energy_deals", event: "", es: "event_window_daily", griddc: "datacenter_facilities", datacenters: "datacenter_facilities",
  bill: "cost_of_power_monthly", cop: "cost_of_power_monthly", mr: "merchant_revenue_monthly", ms: "merchant_revenue_monthly", projects: "energy_projects",
  gridnews: "news_index",
};
// the grid a card's words name, as components/analysis/FindingCard.tsx and scripts/check-analysis.mjs read it
export const GRID_WORD = [[/\bERCOT\b/i, "ercot"], [/\bCAISO\b/i, "caiso"], [/\bPJM\b/i, "pjm"], [/\bMISO\b/i, "miso"], [/\bSPP\b/i, "spp"], [/\bNYISO\b/i, "nyiso"], [/\bISO-NE\b/i, "isone"]];
// first words whose keys are records about a table, not figures read from it
export const RECORD_HEADS = new Set(["catalogue", "lic", "series_hdr"]);

/** The rows of license_status.csv (quoted cells, an unquoted comma in the last column kept with it). */
export function readStatusCsv(text) {
  const rows = [];
  for (const line of text.split(/\r?\n/)) {
    if (!line.trim()) continue;
    const cells = [];
    let cur = "", q = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (q) { if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (c === '"') q = false; else cur += c; }
      else if (c === '"') q = true;
      else if (c === ",") { cells.push(cur); cur = ""; }
      else cur += c;
    }
    cells.push(cur);
    rows.push(cells);
  }
  const [head, ...body] = rows;
  return body.filter((r) => r.length >= head.length)
    .map((r) => [...r.slice(0, head.length - 1), r.slice(head.length - 1).join(",")])
    .map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}

/** The held tables on the day: table -> { publishers, byGrid, grids } (grids: the prefixes of its grid publishers). */
export function heldTables(rows, day) {
  const out = new Map();
  for (const r of rows) {
    if (r.status !== "license needed" || !(day >= r.from)) continue;
    const pubs = (r.publishers || "").split(";").map((x) => x.trim()).filter(Boolean);
    const byGrid = pubs.length > 0 && pubs.every((p) => p in GRID_PREFIX);
    out.set(r.table, { publishers: pubs, byGrid, grids: new Set(pubs.filter((p) => p in GRID_PREFIX).map((p) => GRID_PREFIX[p])) });
  }
  return out;
}

/** The grids that decide any held table: their own rows are held wherever they are read. */
export function heldGridsOf(held) {
  const g = new Set();
  for (const t of held.values()) for (const x of t.grids) g.add(x);
  return g;
}

/** lib/license.ts gridOfEntity: "isone:.H.INTERNAL_HUB" and "iso:isone" are ISO-NE's; "" when none. */
export function gridOfEntity(entity) {
  if (!entity) return "";
  const m = /^([a-z0-9_-]+):(.*)$/i.exec(entity);
  if (!m) return "";
  const head = m[1].toLowerCase();
  if (head in GRID_NAME) return head;
  if (head === "iso" && m[2].toLowerCase() in GRID_NAME) return m[2].toLowerCase();
  return "";
}

/** lib/license.ts gridEntityOfKey: the grid an input names as iso=<grid> or grid=<grid>. */
function gridOfParam(parts) {
  for (const x of parts) {
    const m = /(?:^|&)(?:iso|grid)=([a-z0-9_-]+)(?=&|$)/i.exec(x);
    if (m && m[1].toLowerCase() in GRID_NAME) return m[1].toLowerCase();
  }
  return "";
}

/** A word that is a grid's name or prefix ("NYISO", "ISO-NE", "isone"), as the Digest's keys carry their grid. */
function gridOfWord(x) {
  const w = String(x).trim();
  if (w in GRID_PREFIX) return GRID_PREFIX[w];
  if (w.toLowerCase() in GRID_NAME) return w.toLowerCase();
  return "";
}

export function gridOfWords(s) {
  for (const [re, g] of GRID_WORD) if (re.test(s)) return g;
  return "";
}

/**
 * One checked number's key judged: null when the figure may show, else { table, grid, why }.
 * Num's own rule first (components/Num.tsx heldBy); then, for a first word Num does not read, any held table the key
 * names among its words.
 */
export function judgeKey(key, held, heldGrids) {
  const p = key.split("|");
  const head = p[0];
  if (RECORD_HEADS.has(head)) return null;
  const body = p.slice(1);
  if (head === "finding") {
    const g = p[p.length - 1];
    return g && g !== "-" && heldGrids.has(g) ? { table: `finding ${p[1]}`, grid: g, why: "a finding card's figure of a held grid, drawn with its number" } : null;
  }
  if (head === "latest_prices") {
    const g = gridOfEntity(p[1]);
    return g && heldGrids.has(g) ? { table: "latest_prices", grid: g, why: "a held grid's latest price, drawn with its number" } : null;
  }
  const entityGrid = body.map(gridOfEntity).find((g) => g) || gridOfParam(body);
  const rowHeld = (table, grid, named) => {
    const t = held.get(table);
    if (!t) return null;
    if (!t.byGrid) return { table, grid: "", why: named ? "a figure of a table held whole, drawn with its number" : "a figure of a table held whole, under a first word Num does not read" };
    if (!grid) return { table, grid: "", why: named ? "a figure of a table held by grid, with no grid in its key (Num holds such a figure), drawn with its number" : "a figure of a table held by grid, with no grid in its key, under a first word Num does not read" };
    return t.grids.has(grid) ? { table, grid, why: named ? "a held grid's figure, drawn with its number" : "a held grid's figure, under a first word Num does not read" } : null;
  };
  let table = "";
  if (head.startsWith("series")) table = p[1] ?? "";
  else if (head === "event" || head === "entity") table = p[1] ?? "";
  else if (head in KEY_TABLE) table = KEY_TABLE[head];
  else if (head === "digest_chart") table = p[2] ?? "";
  if (table) {
    // Num's grid: the entity among the key's words, or iso=; a series or event-window key without one asks about the
    // table whole (held), as licenseHeldRow(table, undefined) does
    return rowHeld(table, entityGrid, true);
  }
  // a first word Num does not read (it shows the number): any held table the key names, with the grid of its words
  const grid = entityGrid || body.map(gridOfWord).find((g) => g) || "";
  for (const x of body) {
    if (held.has(x)) {
      const r = rowHeld(x, grid, false);
      if (r) return r;
    }
  }
  return null;
}

/** Every data-check key on a page, with the text drawn. */
export function keysOf(html) {
  const out = [];
  const re = /data-check="([^"]+)"/g;
  let m;
  while ((m = re.exec(html))) out.push(m[1].replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#x27;/g, "'"));
  return out;
}

/** The cards on a page: [{ card, html }] where html runs from the card's article to the next card (or the end). */
export function cardsOf(html) {
  const re = /data-finding="([a-z0-9_]+)"/g;
  const at = [];
  let m;
  while ((m = re.exec(html))) at.push([m.index, m[1]]);
  return at.map(([i, card], k) => ({ card, html: html.slice(i, k + 1 < at.length ? at[k + 1][0] : html.length) }));
}

/** The grids a card's small multiples draw in the all-grids view: each panel's title, and the names of its series. */
export function multipleGridsOf(cardHtml) {
  const g = new Set();
  const start = cardHtml.indexOf('data-finding-chart="multiples"');
  if (start < 0) return g;
  const seg = cardHtml.slice(start);
  const re = /data-panel="\d+"[^>]*>\s*(?:<p[^>]*>([^<]*)<\/p>)?/g;
  let m;
  while ((m = re.exec(seg))) if (m[1]) { const x = gridOfWords(m[1]); if (x) g.add(x); }
  const rs = /data-series="([^"]+)"/g;
  while ((m = rs.exec(seg))) { const x = gridOfWords(m[1]); if (x) g.add(x); }
  return g;
}

/** The held tables a card reads, and the grids by which they are held (a card held whole if any of its tables is). */
export function cardHolds(cardJson, held) {
  const tables = (cardJson.tables || []).filter((t) => held.has(t));
  const grids = new Set();
  let whole = false;
  for (const t of tables) {
    const h = held.get(t);
    if (h.byGrid) for (const x of h.grids) grids.add(x);
    else whole = true;
  }
  return { tables, grids, whole };
}

/** The tables a page's downloads line names (components/tool/TableDownloads.tsx, data-download-table). */
export function downloadTablesOf(html) {
  const out = new Set();
  const re = /data-download-table="([a-z0-9_]+)"/g;
  let m;
  while ((m = re.exec(html))) out.add(m[1]);
  return out;
}

/** Chart series named for a grid: [{ series, grid }]. */
export function seriesGridsOf(html) {
  const out = [];
  const re = /data-series="([^"]+)"/g;
  let m;
  while ((m = re.exec(html))) { const g = gridOfWords(m[1]); if (g) out.push({ series: m[1], grid: g }); }
  return out;
}

/** The whole judgment of one page's HTML: { leaks, possible, keys, held_words }. */
export function judgePage(page, html, held, heldGrids, readCard) {
  const leaks = [], possible = [];
  const keys = keysOf(html);
  const seen = new Set();
  for (const k of keys) {
    if (seen.has(k)) continue;
    seen.add(k);
    const r = judgeKey(k, held, heldGrids);
    if (r) leaks.push({ page, kind: "number", key: k, table: r.table, grid: r.grid, why: r.why });
  }
  for (const { card, html: ch } of cardsOf(html)) {
    const j = readCard(card);
    if (!j) continue;
    const h = cardHolds(j, held);
    if (!h.tables.length) continue;
    const drawn = multipleGridsOf(ch);
    for (const g of drawn) {
      if (h.whole || h.grids.has(g)) {
        leaks.push({ page, kind: "panel", key: `card ${card}`, table: h.tables.join("; "), grid: g,
          why: `the small multiples draw ${GRID_NAME[g] ?? g}'s panel from a held table (components/analysis/MultiChart.tsx asks no hold)` });
      }
    }
  }
  const dl = [...downloadTablesOf(html)].filter((t) => held.get(t)?.byGrid);
  if (dl.length) {
    const grids = new Set(dl.flatMap((t) => [...held.get(t).grids]));
    const named = new Set();
    for (const { series, grid } of seriesGridsOf(html)) {
      if (!grids.has(grid) || named.has(series)) continue;
      named.add(series);
      possible.push({ page, kind: "series", key: series, table: dl.join("; "), grid, why: "a chart series named for a held grid on a page that reads a table held by grid: read by hand" });
    }
  }
  const heldWords = (html.match(/data-license-held=/g) || []).length;
  return { leaks, possible, keys: seen.size, held_words: heldWords };
}

// ---- the run ----

function arg(name) {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : undefined;
}

async function fetchPage(base, url, cookie, ms) {
  for (let attempt = 1; attempt <= 2; attempt++) {
    const ac = new AbortController();
    const t = setTimeout(() => ac.abort(), ms);
    try {
      const res = await fetch(base + url, { headers: cookie ? { Cookie: cookie } : {}, signal: ac.signal });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const html = await res.text();
      if (html.includes('data-in-review="1"')) throw new Error("the in-review page was served (no internal cookie)");
      return { html };
    } catch (e) {
      if (attempt === 2) return { error: String(e.message || e) };
    } finally {
      clearTimeout(t);
    }
  }
}

async function oneGridViews(base, leaks, cardsSeen, held, heldGrids, readCard) {
  // the one-grid view is chosen in the browser (MultiChart reads the address after the page loads)
  const out = [];
  const code = await withBrowser(async ({ go, evaluate, wait, unlock }) => {
    await unlock(base);
    for (const [card, page] of cardsSeen) {
      const j = readCard(card);
      const h = cardHolds(j, held);
      const param = j.chart?.param;
      if (!param || j.chart?.kind !== "multiples") continue;
      for (const p of j.chart.panels || []) {
        if (!(h.whole || h.grids.has(p.grid))) continue;
        const sep = page.includes("?") ? "&" : "?";
        const url = `${base}${page}${sep}${param}=${p.grid}`;
        await go(url);
        try { await wait(`!!document.querySelector('[data-multi-grid="${p.grid}"]')`, 20000, `${card}: ${p.grid}'s one-grid view`); }
        catch { out.push({ page: `${page}${sep}${param}=${p.grid}`, kind: "view", key: `card ${card}`, table: h.tables.join("; "), grid: p.grid, why: "the one-grid view did not open in 20 s (not judged)" }); continue; }
        const r = await evaluate(`(() => {
          const v = document.querySelector('[data-multi-grid="${p.grid}"]');
          const chart = !!v.querySelector('[data-grid-chart="1"] svg, [data-grid-chart="1"][data-option-kind]');
          const calls = [...v.querySelectorAll('[data-grid-before],[data-grid-after]')].map((x) => x.textContent.trim()).filter((t) => t && t !== "license needed").length;
          const table = !!v.querySelector('[data-grid-table]') && !v.querySelector('[data-grid-table] [data-license-held]');
          return { chart, calls, table };
        })()`);
        const what = [r.chart ? "its chart" : "", r.calls ? `${r.calls} callout figures` : "", r.table ? "its regression table" : ""].filter(Boolean);
        if (what.length) out.push({ page: `${page}${sep}${param}=${p.grid}`, kind: "view", key: `card ${card}`, table: h.tables.join("; "), grid: p.grid,
          why: `the one-grid view draws ${what.join(", ")} for a held grid` });
      }
    }
    return 0;
  });
  if (code === null) return { out, proven: false };
  return { out, proven: true };
}

async function main() {
  const base = process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : "http://localhost:3000";
  const day = new Date().toISOString().slice(0, 10);
  const statusFile = path.join(SITE, "..", "warehouse", "metadata", "license_status.csv");
  if (!fs.existsSync(statusFile)) { console.error(`check-holds: ${statusFile} not found`); process.exit(2); }
  const held = heldTables(readStatusCsv(fs.readFileSync(statusFile, "utf-8")), day);
  const heldGrids = heldGridsOf(held);
  const list = spawnSync(process.execPath, [path.join(here, "check-values.mjs"), "--list"], { encoding: "utf-8" });
  if (list.status !== 0) { console.error(`check-holds: check-values --list exited ${list.status}: ${list.stderr}`); process.exit(2); }
  let pages = JSON.parse(list.stdout.trim().split(/\r?\n/).pop()).pages;
  const only = arg("--pages");
  if (only) pages = pages.filter((p) => only.split(",").some((x) => p.startsWith(x)));
  const ms = Number(arg("--timeout") || 90000);
  const tok = env("INTERNAL_COSTS_TOKEN");
  let cookie = "";
  if (tok) {
    const u = await unlockPost(base, tok);
    cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  }
  if (!cookie) console.log(`check-holds: no internal cookie from ${base}: pages in review answer the in-review page and are listed as not read`);
  const cache = new Map();
  const readCard = (card) => {
    if (!cache.has(card)) {
      const f = path.join(SITE, "data", "findings", `${card}.json`);
      cache.set(card, fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf-8")) : null);
    }
    return cache.get(card);
  };
  console.log(`check-holds: ${held.size} tables held on ${day} (grids held: ${[...heldGrids].sort().join(", ")}); ${pages.length} pages from check-values' list, at ${base}`);
  const leaks = [], possible = [], notRead = [], perPage = [];
  const cardsSeen = new Map();
  for (const page of pages) {
    const r = await fetchPage(base, page, cookie, ms);
    if (r.error) { notRead.push({ page, why: r.error }); console.log(`not read  ${page}: ${r.error}`); continue; }
    const j = judgePage(page, r.html, held, heldGrids, readCard);
    for (const { card } of cardsOf(r.html)) if (!cardsSeen.has(card) && readCard(card)?.chart?.kind === "multiples") cardsSeen.set(card, page.split("?")[0]);
    leaks.push(...j.leaks);
    possible.push(...j.possible);
    perPage.push({ page, keys: j.keys, held_words: j.held_words, leaks: j.leaks.length, possible: j.possible.length });
    console.log(`${j.leaks.length ? "LEAK" : "ok  "}  ${page}: ${j.keys} checked numbers, ${j.held_words} drawn as "license needed", ${j.leaks.length} held figures shown, ${j.possible.length} to read by hand`);
  }
  let views = { out: [], proven: false };
  if (process.argv.includes("--browser") && cardsSeen.size) {
    views = await oneGridViews(base, leaks, cardsSeen, held, heldGrids, readCard);
    if (!views.proven) console.log("check-holds: no browser on this machine: the one-grid views were not read");
    leaks.push(...views.out.filter((x) => !x.why.includes("not judged")));
    for (const x of views.out) console.log(`${x.why.includes("not judged") ? "not read" : "LEAK"}  ${x.page}: ${x.why}`);
  }
  for (const x of leaks) console.log(`  leak: ${x.page} | ${x.kind} | ${x.key} | ${x.table} | ${x.grid || "-"} | ${x.why}`);
  for (const x of possible) console.log(`  read by hand: ${x.page} | ${x.key} | ${x.grid} | ${x.why}`);
  const read = perPage.length;
  console.log(`check-holds: ${read} of ${pages.length} pages read, ${notRead.length} not read; ${leaks.length} held figures shown on ${new Set(leaks.map((x) => x.page)).size} pages; ${possible.length} series to read by hand`);
  const out = { day, base, held_tables: [...held.keys()].sort(), held_grids: [...heldGrids].sort(), pages: perPage, not_read: notRead, leaks, possible,
    one_grid_views: process.argv.includes("--browser") ? (views.proven ? "read" : "no browser") : "not asked (--browser)" };
  const jf = arg("--json");
  if (jf) fs.writeFileSync(jf, JSON.stringify(out, null, 1) + "\n");
  const cf = arg("--csv");
  if (cf) {
    // one line a page (docs/licenses_holds.csv, read by scripts/licenses.py write)
    const byPage = new Map();
    for (const x of leaks) {
      const k = x.page;
      if (!byPage.has(k)) byPage.set(k, { page: k, figures: 0, tables: new Set(), grids: new Set(), kinds: new Set() });
      const b = byPage.get(k);
      b.figures++; x.table.split("; ").forEach((t) => b.tables.add(t)); if (x.grid) b.grids.add(GRID_NAME[x.grid] ?? x.grid); b.kinds.add(x.kind);
    }
    const q = (s) => (/[",]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s);
    const lines = ["page,figures,kinds,tables,grids,day"];
    for (const b of [...byPage.values()].sort((a, c) => a.page.localeCompare(c.page)))
      lines.push([b.page, String(b.figures), [...b.kinds].sort().join("; "), [...b.tables].sort().join("; "), [...b.grids].sort().join("; "), day].map(q).join(","));
    fs.writeFileSync(cf, lines.join("\n") + "\n");
  }
  if (!read) process.exit(2);
  process.exit(leaks.length ? 1 : 0);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  main().catch((e) => { console.error(`check-holds: ${e.stack || e}`); process.exit(2); });
}
