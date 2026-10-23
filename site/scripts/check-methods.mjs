// Energy Research Warehouse (ERW) site, session 409: the method notes against the pages.
//
//   node scripts/check-methods.mjs                       (no site: the keys recorded in scripts/check-methods-keys.json)
//   node scripts/check-methods.mjs http://localhost:3000 (a running site: each page read as check-values reads it)
//   node scripts/check-methods.mjs --values <file>       (the output of a check-values.mjs run: each key under the first
//                                                         page that carried it, as that script reports it)
//   add --write to record the keys read (a base URL, --values, or both, each page then holding the keys of both) in
//   scripts/check-methods-keys.json
//   add --all to print the figures that are named too, not only the missing ones
//
// For every page of scripts/check-values-floor.json (the pages check-values.mjs reads) that links a method note, the
// script lists each figure the page shows, by its check-values key (data-check, components/Num.tsx), and whether a note
// of the page names it. It exits 0 when every figure of every page with a note is named, 1 when one is not, 2 when its
// input cannot be read (no floor file, no keys, a page whose code is not found).
//
// The rule, in four parts.
//
// 1. A page's notes. The page's code is its route's app/<route>/page.tsx (an address that redirects in next.config.ts
//    without a condition is read at its destination, as a visitor is sent there) and every file it imports from app/ or
//    components/, and theirs in turn. Its notes are the docs/methods/<slug>.md that this code links to as
//    /data/methods/<slug> (written out, or a constant that holds it) from a link whose words hold "method" or are
//    "Every number, step by step" (the step-by-step notes of the cost-of-power tools). A page whose code links no note
//    is listed as having none and is not checked.
//
// 2. A figure. Each key is split at "|". A key that reads a warehouse table names the table and the variable (or field):
//      series|<table>|<entity>|<variable>|<time>, series_esum|<table>|<entity>|<variable>|..., series_max and series_sum
//      |<table>|<variable>|... (and series_n, session 1154), event and entity|<table>|<id>|<field>, latest_prices|<entity>|<variable>|<time>,
//      catalogue|<table>|n_rows (and catalogue|<count>).
//    Its figure is that table and that variable; a variable part of several names, comma separated (series_sum's fuel
//    group, session 1152), is a figure of each name (session 1162). Every other key is a figure of the page's own arithmetic (the battery's
//    bs|, the datacenter's dc|, the capture prices' cap|, ...): its figure is its first word, the family, and one more word,
//    the measure: by default the first part after the family that is not a case or an instance, cut at its first ":"
//    (bs|<case>|l12_kw:total is "bs l12_kw"); the families in MEASURE_AT below take another part. A case or an instance
//    is a date or time, a number, a setting string (a=b&c=d), an id (a part that begins with one of the prefixes in
//    instance() below, eia930:ERCO, deal:..., erwco:..., or an upper-case name, HB_HUBAVG), a grid's name, a two-letter
//    state, "-" or "newest"; a part cut at ":" keeps its pieces that are not (neighbour_mwh:SWPP is neighbour_mwh).
//    calc|<op>|<A>|<B> is the two figures of A and B (calc|bal|<A>|<B>|<C>, session 1165, the three). The Digest's chart of the day, digest_chart|<date>|<table>|<figure>,
//    is a family: its table is the day's.
//
// 3. Named. A note names a table figure when its text holds both the table's name and the variable's, each as a whole
//    word, as written in the key (in the variable, an underscore may be read as a space). It names a figure of the page's
//    arithmetic when its text holds the family as a key starts it (`bs|`) and the measure as a whole word (an underscore
//    may be read as a space). Case is ignored. The note's whole text counts, its code spans included. A number in a name
//    may be written as any number or as a placeholder in angle brackets (`rt_mean_h<hour>` names rt_mean_h03 and
//    rt_mean_h22, which are one figure); a list in angle brackets names each of its names (`year_mean_<a, b>` names
//    year_mean_a and year_mean_b), as the notes already write them.
//
// 4. The keys. With a base URL, each page is read with the internal view's cookie (INTERNAL_COSTS_TOKEN, as check-values
//    does), every data-check of the page counted. With --values, the keys of a check-values run, each under the first page
//    that carried it (a key two pages share is the first one's only). Without either, scripts/check-methods-keys.json:
//    one key a figure a page, written by --write from one of the two, with the run it came from.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { unlockPost } from "./browser.mjs";   // the internal view by the form's door, no token in an address

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const ROOT = path.join(SITE, "..");
const FLOOR_FILE = path.join(here, "check-values-floor.json");
const KEYS_FILE = path.join(here, "check-methods-keys.json");

const TABLE_KEY = {
  // family: [index of the table (or null: the family is the table), index of the variable (-1: the last part)]
  series: [1, 3], series_esum: [1, 3], series_max: [1, 2], series_sum: [1, 2], series_n: [1, 2], event: [1, 3], entity: [1, 3],   // session 1154: series_n
  latest_prices: [null, 2], catalogue: [null, -1],
};
// the families whose measure is not the first part after the family that is not an instance: the part to take
export const MEASURE_AT = { digest_chart: 3, cap: -1, impact: -1, gridq: -1, shape: 3, sev: 2, ms: -1, finding: 4, awe: 2, dcd: -1, bsa: -1, es: 3, mrs: -1 };
// the families whose measure is the last piece of that part when it is cut at ":" (dcd|<mw>|<utility>:<charge>)
export const CUT_LAST = new Set(["dcd"]);
const GRIDS = new Set(["ercot", "caiso", "pjm", "miso", "nyiso", "isone", "spp", "us48", "us", "erco", "ciso", "isne", "nyis", "swpp", "west", "east", "none of the seven", "more than one"]);

/** A part of a key that is a case or an instance, not a name (rule 2). */
export function instance(x) {
  if (x === "" || x === "-" || x === "newest") return true;
  if (/^\d{4}(-\d{2}(-\d{2}(T[\d:.]+(Z|[+-]\d{2}:\d{2})?)?)?)?$/.test(x)) return true;   // a year, month, day or time
  if (/^-?\d+(\.\d+)?$/.test(x)) return true;                                          // a number
  if (x.includes("=") || x.includes("&")) return true;                                // a case's settings
  if (/^(deal|erwco|doe|federalregister|eia930|eia|ercot|caiso|pjm|miso|nyiso|isone|spp|iso|nlr_jedi|ba):/.test(x)) return true;
  if (GRIDS.has(x.toLowerCase())) return true;
  if (/^[A-Z]{2}$/.test(x)) return true;                                               // a state
  if (/^[A-Z][A-Z0-9_.-]{2,}$/.test(x)) return true;                                   // an upper-case id (HB_HUBAVG, SCE)
  return false;
}

/** The figures one key shows (rule 2): [{ kind: "table"|"family", table, measure, id }]. */
export function figures(key) {
  const p = key.split("|");
  const head = p[0];
  // session 1165: every operand, so calc|bal|<A>|<B>|<C> is the three figures (a two-operand key is its two, as before)
  if (head === "calc" && p.length >= 4) return p.slice(2).flatMap((x) => figures(x.replaceAll("~", "|")));
  if (head in TABLE_KEY) {
    const [ti, vi] = TABLE_KEY[head];
    const table = ti === null ? head : p[ti];
    const measure = vi === -1 ? p[p.length - 1] : p[vi];
    // session 1162: a key of several variables, comma separated (series_sum's fuel group, session 1152), shows a figure
    // of each; a key without a comma is one figure, as before
    if (table && measure) return measure.split(",").filter(Boolean).map((m) => ({ kind: "table", table, measure: m, id: `${table} ${shape(m)}` }));
  }
  const rest = p.slice(1);
  let part;
  if (head in MEASURE_AT) {
    const at = MEASURE_AT[head];
    part = at === -1 ? rest[rest.length - 1] : p[at];
    if (part !== undefined && instance(part)) part = undefined;
  }
  if (part === undefined) part = rest.find((x) => !instance(x));
  const pieces = part === undefined ? [] : part.split(":").filter((x) => !instance(x));
  const measure = (CUT_LAST.has(head) ? pieces[pieces.length - 1] : pieces[0]) ?? "";
  return [{ kind: "family", table: head, measure, id: measure ? `${head}| ${shape(measure)}` : `${head}|` }];
}

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const word = (s) => new RegExp(`(^|[^a-z0-9_])${s}($|[^a-z0-9_])`, "i");
// a name with its numbers set aside: rt_mean_h03 and rt_mean_h22 are one figure, rt_mean_h#
export const shape = (v) => v.replace(/\d+/g, "#");
// as a pattern: an underscore may be a space, a number any number or a placeholder in angle brackets (rt_mean_h<hour>)
const spaced = (v) => v.split(/(\d+)/).map((x, i) => (i % 2 ? "(?:\\d+|<[^<>\\s]+>)" : esc(x).replace(/_/g, "[_ ]"))).join("");

/** A note's text, with each list of names written as the notes write them, year_mean_<shoulder_hours, fleet_mw>, also
 * written out name by name (year_mean_shoulder_hours year_mean_fleet_mw) (rule 3). */
export function noteWords(md) {
  const out = [];
  for (const m of md.matchAll(/([a-z0-9_]*)<([a-z0-9_]+(?:,\s*[a-z0-9_]+)+)>([a-z0-9_]*)/gi)) {
    for (const x of m[2].split(/,\s*/)) out.push(`${m[1]}${x}${m[3]}`);
  }
  return out.length ? `${md}\n${out.join(" ")}` : md;
}

/** Whether a note's text names a figure (rule 3). */
export function named(text, f) {
  if (f.kind === "table") return word(esc(f.table)).test(text) && word(spaced(f.measure)).test(text);
  const fam = new RegExp(`(^|[^a-z0-9_])${esc(f.table)}\\|`, "i").test(text);
  return fam && (!f.measure || word(spaced(f.measure)).test(text));
}

// ---- rule 1: a page's code and its notes ----

/** next.config.ts's redirects without a condition: source path to destination path. */
function redirects() {
  const f = ["next.config.ts", "next.config.mjs", "next.config.js"].map((n) => path.join(SITE, n)).find((n) => fs.existsSync(n));
  const out = {};
  if (!f) return out;
  for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
    if (line.includes("has:")) continue;
    const m = line.match(/source:\s*"([^"]+)",\s*destination:\s*"([^"]+)"/);
    if (m && !m[1].includes(":")) out[m[1]] = m[2].split("?")[0];
  }
  return out;
}
const REDIRECT = redirects();

/** The page.tsx of a route, or null: literal folders first, then a [param] folder; route groups are not used. */
export function pageFile(route) {
  let dir = path.join(SITE, "app");
  for (const seg of decodeURIComponent(route).split("/").filter(Boolean)) {
    if (fs.existsSync(path.join(dir, seg))) { dir = path.join(dir, seg); continue; }
    const dyn = fs.readdirSync(dir, { withFileTypes: true }).find((d) => d.isDirectory() && /^\[.+\]$/.test(d.name));
    if (!dyn) return null;
    dir = path.join(dir, dyn.name);
  }
  const f = path.join(dir, "page.tsx");
  return fs.existsSync(f) ? f : null;
}

function resolveImport(from, spec) {
  let base;
  if (spec.startsWith("@/")) base = path.join(SITE, spec.slice(2));
  else if (spec.startsWith(".")) base = path.resolve(path.dirname(from), spec);
  else return null;
  const rel = path.relative(SITE, base).split(path.sep)[0];
  if (rel !== "app" && rel !== "components" && rel !== "lib") return null;
  for (const c of [base, `${base}.tsx`, `${base}.ts`, path.join(base, "index.tsx"), path.join(base, "index.ts")]) {
    if (fs.existsSync(c) && fs.statSync(c).isFile()) return c;
  }
  return null;
}

/** The files of a page: its page.tsx and every file of app/ or components/ it imports, and theirs; and the files of lib/
 * they import, read only for the constants that hold a note's address (rule 1), and not followed further. */
const isLib = (f) => path.relative(SITE, f).split(path.sep)[0] === "lib";
export function codeFiles(page) {
  const seen = new Set();
  const todo = [page];
  while (todo.length) {
    const f = todo.pop();
    if (seen.has(f)) continue;
    seen.add(f);
    if (isLib(f)) continue;
    const src = fs.readFileSync(f, "utf-8");
    for (const m of src.matchAll(/(?:import|export)\s[^;]*?from\s+["']([^"']+)["']/g)) {
      const r = resolveImport(f, m[1]);
      if (r && !seen.has(r)) todo.push(r);
    }
  }
  return [...seen];
}

const METHOD_WORDS = /\bmethods?\b|^every number, step by step$/i;

/** The notes a page's code links (rule 1), each with the file that links it. */
export function notesOf(files) {
  const srcs = files.map((f) => [f, fs.readFileSync(f, "utf-8")]);
  // a constant is read in the file that links it first, then in the files it imports (two files may each hold a METHOD)
  const constsOf = (src) => {
    const c = {};
    for (const m of src.matchAll(/\b([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*["`]\/data\/methods\/([a-z0-9_]+)/g)) c[m[1]] ??= m[2];
    // an object that holds it as its href (lib/policyweek.ts: METHOD = { href: "/data/methods/..." })
    for (const m of src.matchAll(/\b([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=\n]+)?=\s*\{[^}]*?\bhref:\s*["`]\/data\/methods\/([a-z0-9_]+)/g)) c[`${m[1]}.href`] ??= m[2];
    return c;
  };
  const consts = {};
  for (const [, s] of srcs) for (const [k, v] of Object.entries(constsOf(s))) consts[k] ??= v;
  const out = new Map();
  for (const [f, s] of srcs) {
    if (isLib(f)) continue;
    const own = constsOf(s);
    for (const m of s.matchAll(/<(?:Link|SiteLink|a)\b[^>]*?href=(?:\{\s*)?(?:"([^"]+)"|`([^`]+)`|([A-Za-z_][A-Za-z0-9_.]*))\s*\}?[^>]*>([^<]{0,80})</g)) {
      const words = m[4].replace(/&apos;/g, "'").trim();
      if (!METHOD_WORDS.test(words)) continue;
      const href = m[1] ?? m[2] ?? null;
      const slug = href ? (href.match(/^\/data\/methods\/([a-z0-9_]+)/) ?? [])[1] : own[m[3]] ?? consts[m[3]];
      if (slug && fs.existsSync(path.join(ROOT, "docs", "methods", `${slug}.md`)) && !out.has(slug)) out.set(slug, path.relative(SITE, f).replaceAll("\\", "/"));
    }
  }
  return out;
}

export function routeOf(page) {
  let r = page.split("?")[0] || "/";
  for (let i = 0; i < 5 && REDIRECT[r]; i++) r = REDIRECT[r];
  return r;
}

// ---- rule 4: the keys ----

function env(name) {
  if (process.env[name]) return process.env[name];
  const f = path.join(SITE, ".env.local");
  if (fs.existsSync(f)) {
    for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
      const m = line.match(/^([A-Z_]+)=(.*)$/);
      if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
    }
  }
  return "";
}
const decode = (s) => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#x27;|&#39;/g, "'");

async function keysFromSite(base, pages) {
  const tok = env("INTERNAL_COSTS_TOKEN");
  let cookie = "";
  if (tok) {
    const u = await unlockPost(base, tok);
    cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  }
  const out = {};
  for (const page of pages) {
    const res = await fetch(base + page, { headers: cookie ? { Cookie: cookie } : {}, signal: AbortSignal.timeout(120_000) });
    if (!res.ok) throw new Error(`${page}: HTTP ${res.status}`);
    const html = await res.text();
    if (html.includes('data-in-review="1"')) throw new Error(`${page}: the in-review page was served (no internal cookie)`);
    out[page] = [...new Set([...html.matchAll(/data-check="([^"]+)"/g)].map((m) => decode(m[1])))];
  }
  return out;
}

export function keysFromValues(text) {
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    const m = line.match(/^(?:ok|late|FAIL)\s*\| (\S+) \| ([^ ]+\|[^ ]*) \|/);
    if (m) (out[m[1]] ??= new Set()).add(m[2]);
  }
  return Object.fromEntries(Object.entries(out).map(([p, s]) => [p, [...s]]));
}

/** One key a figure (the first met), sorted: what the keys file keeps of a page. */
export function oneKeyAFigure(keys) {
  const by = new Map();
  for (const k of keys) for (const f of figures(k)) if (!by.has(f.id)) by.set(f.id, k);
  return [...new Set(by.values())].sort();
}

// ---- the check ----

export function check(pageKeys, pages) {
  const noteText = new Map();
  const text = (slug) => {
    if (!noteText.has(slug)) noteText.set(slug, noteWords(fs.readFileSync(path.join(ROOT, "docs", "methods", `${slug}.md`), "utf-8")));
    return noteText.get(slug);
  };
  const rows = [];
  const noNote = [], noCode = [], noKeys = [];
  const byRoute = new Map();
  const seenByRoute = {};
  for (const page of pages) {
    const route = routeOf(page);
    if (!byRoute.has(route)) {
      const pf = pageFile(route);
      byRoute.set(route, pf ? notesOf(codeFiles(pf)) : null);
    }
    const notes = byRoute.get(route);
    if (notes === null) { noCode.push(`${page} (route ${route})`); continue; }
    if (!notes.size) { noNote.push(page); continue; }
    const keys = pageKeys[page];
    if (!keys || !keys.length) { noKeys.push(page); continue; }
    // a figure is listed once a route: the first page of the route that shows it (the addresses of one page's views and
    // settings show it again)
    const seen = (seenByRoute[route] ??= new Set());
    for (const k of keys) {
      for (const f of figures(k)) {
        if (seen.has(f.id)) continue;
        seen.add(f.id);
        const by = [...notes.keys()].filter((s) => named(text(s), f));
        rows.push({ page, route, figure: f, key: k, notes: [...notes.keys()], by });
      }
    }
  }
  // a page with no keys of its own is reported only when no address of its route had any
  const routed = new Set(rows.map((x) => x.route));
  return { rows, noNote, noCode, noKeys: noKeys.filter((p) => !routed.has(routeOf(p))), notesByRoute: byRoute };
}

async function main() {
  const args = process.argv.slice(2);
  const flag = (n) => args.includes(n);
  const vi = args.indexOf("--values");
  const valuesFile = vi >= 0 ? args[vi + 1] : null;
  const base = args.find((a, i) => /^https?:\/\//.test(a) && args[i - 1] !== "--values") ?? null;
  if (!fs.existsSync(FLOOR_FILE)) { console.error(`check-methods: ${FLOOR_FILE} is missing`); process.exit(2); }
  const floor = JSON.parse(fs.readFileSync(FLOOR_FILE, "utf-8"));
  const pages = Object.keys(floor.floor ?? {});
  let pageKeys = {}, source;
  const said = [];
  // a base URL and --values together: each page's keys are both sources' (a read the database answered slowly drew fewer)
  if (base) { pageKeys = await keysFromSite(base.replace(/\/$/, ""), pages); said.push(`the pages at ${base}, read ${new Date().toISOString()}`); }
  if (valuesFile) {
    const v = keysFromValues(fs.readFileSync(valuesFile, "utf-8"));
    for (const [p, ks] of Object.entries(v)) pageKeys[p] = [...new Set([...(pageKeys[p] ?? []), ...ks])];
    said.push(`the check-values run ${path.basename(path.dirname(valuesFile))}/${path.basename(valuesFile)} (each key under the first page that carried it)`);
  }
  if (said.length) source = said.join(", and ");
  else {
    if (!fs.existsSync(KEYS_FILE)) { console.error(`check-methods: no base URL, no --values and no ${KEYS_FILE}`); process.exit(2); }
    const kf = JSON.parse(fs.readFileSync(KEYS_FILE, "utf-8"));
    pageKeys = kf.pages;
    source = `${path.basename(KEYS_FILE)} (${kf.source}, written ${kf.written_utc})`;
  }
  if (flag("--write") && (base || valuesFile)) {
    const kept = Object.fromEntries(pages.filter((p) => pageKeys[p]?.length).map((p) => [p, oneKeyAFigure(pageKeys[p])]));
    fs.writeFileSync(KEYS_FILE, JSON.stringify({ note: "session 409: one check-values key for each figure (scripts/check-methods.mjs, rule 2) of each page of check-values-floor.json; written with --write", written_utc: new Date().toISOString(), source, floor_written_utc: floor.written_utc, pages: kept }, null, 1) + "\n");
    console.log(`the keys file was written: ${Object.keys(kept).length} pages`);
  }
  const r = check(pageKeys, pages);
  console.log(`check-methods: the pages of ${path.basename(FLOOR_FILE)} (${pages.length}), their keys from ${source}\n`);
  for (const [route, notes] of r.notesByRoute) if (notes && notes.size) console.log(`notes | ${route} | ${[...notes].map(([s, f]) => `${s} (${f})`).join(", ")}`);
  console.log("");
  let missing = 0;
  for (const x of r.rows) {
    if (x.by.length) { if (flag("--all")) console.log(`named   | ${x.page} | ${x.figure.id} | ${x.by.join(", ")}`); continue; }
    missing++;
    console.log(`MISSING | ${x.page} | ${x.figure.id} | ${x.key} | notes: ${x.notes.join(", ")}`);
  }
  if (r.noNote.length) console.log(`\nno method note in the page's code (not checked): ${r.noNote.join(", ")}`);
  if (r.noKeys.length) console.log(`no keys recorded (not checked): ${r.noKeys.join(", ")}`);
  if (r.noCode.length) console.log(`no page code found: ${r.noCode.join(", ")}`);
  const pagesChecked = new Set(r.rows.map((x) => x.page)).size;
  console.log(`\n${r.rows.length - missing} of ${r.rows.length} figures named by a note of their page; ${pagesChecked} pages checked${missing ? `; ${missing} MISSING` : ""}`);
  if (r.noCode.length) process.exit(2);
  process.exit(missing ? 1 : 0);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((e) => { console.error(`check-methods FAILED: ${e.message}`); process.exit(2); });
}
