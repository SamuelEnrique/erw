// Energy Research Warehouse (ERW) site, session 9871 (chain 610, part E): the five pages with the fewest tests drawn to
// HTML with the site's own code, without a build, from the files on main: /ai-energy, /industry, /queues/places,
// /storage/places and /curtailment/where-when. It holds what a reader sees on each as it opens, and what a screen reader
// and a checker would say: the page draws without an error; one h1, no heading level skipped; every button has a name,
// every tip its one target, every table a caption; and /ai-energy's three headline figures are the file's own counts.
// No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-reader-pages-render.mjs
import fs from "node:fs";
import { register } from "node:module";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

// <Brand> loads its fonts through next/font/google, which exists only inside a build: stand-ins with no file behind them,
// as scripts/contracts-figures.mjs does; next/navigation's notFound and redirect throw, as they do inside Next
register(`data:text/javascript,${encodeURIComponent(`
const SRC = "const f = (o) => ({ variable: o?.variable ?? '', className: '', style: { fontFamily: 'stand-in' } }); export const Inter = f, IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
const NAV = "export function notFound() { throw new Error('notFound'); } export function redirect(u) { throw new Error('redirect ' + u); } export const usePathname = () => '/'; export const useRouter = () => ({ push() {}, replace() {}, refresh() {} }); export const useSearchParams = () => new URLSearchParams();";
export async function resolve(s, c, next) { return s === "next/font/google" ? { url: "erw-font-stub:google", shortCircuit: true } : s === "next/navigation" ? { url: "erw-nav-stub:navigation", shortCircuit: true } : next(s, c); }
export async function load(u, c, next) { return u === "erw-font-stub:google" ? { format: "module", source: SRC, shortCircuit: true } : u === "erw-nav-stub:navigation" ? { format: "module", source: NAV, shortCircuit: true } : next(u, c); }
`)}`);

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");

const PAGES = [
  ["/ai-energy", "../app/ai-energy/page.tsx"],
  ["/industry", "../app/industry/page.tsx"],
  ["/queues/places", "../app/queues/places/page.tsx"],
  ["/storage/places", "../app/storage/places/page.tsx"],
  ["/curtailment/where-when", "../app/curtailment/where-when/page.tsx"],
  // session 9873: the tier after (three to five test files each)
  ["/states", "../app/states/page.tsx"],
  ["/conditions", "../app/conditions/page.tsx"],
  ["/congestion", "../app/congestion/page.tsx"],
  ["/attention", "../app/attention/page.tsx"],
  ["/deals/capital", "../app/deals/capital/page.tsx"],
];

// the pages read files; what a shared component would ask of the database is answered with no rows by a stand-in for
// fetch, so no request leaves the machine; an async server component is awaited in place (scripts/events-pages.mjs)
const { resolveAsync } = await import("./events-pages.mjs");
process.env.SUPABASE_URL = "http://localhost:9/";
process.env.SUPABASE_ANON_KEY = "stand-in";
globalThis.fetch = async () => new Response("[]", { status: 200, headers: { "content-type": "application/json" } });
async function draw(file) {
  const mod = await import(file);
  const el = await mod.default({ searchParams: Promise.resolve({}) });
  return renderToStaticMarkup(await resolveAsync(el));
}

const drawn = {};
for (const [page, file] of PAGES) {
  let html = "";
  try { html = await draw(file); } catch (e) { ok(false, `${page}: draws (${e?.message ?? e})`); continue; }
  drawn[page] = html;
  ok(html.length > 2000, `${page}: draws (${html.length} characters)`);
  const levels = [...html.matchAll(/<h([1-6])[\s>]/g)].map((m) => Number(m[1]));
  const skips = levels.filter((l, i) => i > 0 && l > levels[i - 1] + 1);
  ok(levels.filter((l) => l === 1).length === 1 && skips.length === 0, `${page}: one h1 and no level skipped (${levels.join(" ")})`);
  const ids = [...html.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]);
  const lost = [...html.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]).filter((id) => !ids.includes(id));
  const twice = ids.filter((id, i) => ids.indexOf(id) !== i);
  const nameless = [...html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)].filter((b) => !/aria-label="[^"]+"/.test(b[1]) && !text(b[2]).trim());
  ok(!lost.length && !twice.length && !nameless.length, `${page}: every tip has its one target, every button a name${lost.length ? `; lost ${lost[0]}` : ""}${twice.length ? `; twice ${twice[0]}` : ""}`);
  const tables = (html.match(/<table\b/g) ?? []).length, captions = (html.match(/<caption\b/g) ?? []).length;
  ok(tables === 0 || captions >= tables, `${page}: every table has a caption (${tables} tables)`);
  const imgs = [...html.matchAll(/<img\b[^>]*>/g)].filter((m) => !/\balt="/.test(m[0]));
  ok(!imgs.length, `${page}: every image has its words`);
}

// The next tier (one or two test files each): /data/standard, every stop of the tour, and the three largest company
// pages of the directory, each drawn with its own address's parts, the same reads
const { STOPS } = await import("../lib/tour.ts");
const companies = JSON.parse(fs.readFileSync(new URL("../data/companies/index.json", import.meta.url), "utf-8")).rows.slice(0, 3).map((r) => r[0]);
const MORE = [
  ["/data/standard", "../app/data/standard/page.tsx", {}],
  ...STOPS.map((_, i) => [`/tour/${i + 1}`, "../app/tour/[stop]/page.tsx", { params: Promise.resolve({ stop: String(i + 1) }) }]),
  ...companies.map((id) => [`/companies/${id}`, "../app/companies/[id]/page.tsx", { params: Promise.resolve({ id }) }]),
];
for (const [page, file, props] of MORE) {
  let html = "";
  try {
    const mod = await import(file);
    html = renderToStaticMarkup(await resolveAsync(await mod.default({ searchParams: Promise.resolve({}), ...props })));
  } catch (e) { ok(false, `${page}: draws (${e?.message ?? e})`); continue; }
  const levels = [...html.matchAll(/<h([1-6])[\s>]/g)].map((m) => Number(m[1]));
  const skips = levels.filter((l, i) => i > 0 && l > levels[i - 1] + 1);
  const ids = [...html.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]);
  const lost = [...html.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]).filter((id) => !ids.includes(id));
  const nameless = [...html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)].filter((b) => !/aria-label="[^"]+"/.test(b[1]) && !text(b[2]).trim());
  const tables = (html.match(/<table\b/g) ?? []).length, captions = (html.match(/<caption\b/g) ?? []).length;
  ok(html.length > 1000 && levels.filter((l) => l === 1).length === 1 && !skips.length && !lost.length && !nameless.length && (tables === 0 || captions >= tables || page === "/data/standard"),
    `${page}: draws, one h1, no level skipped (${levels.join(" ")}), tips and buttons named, ${tables} tables${page === "/data/standard" ? " (a document's own, not captioned)" : " captioned"}`);
}

// /ai-energy's headline: the file's own counts (data/ai_energy.json), as the page says them
const ai = JSON.parse(fs.readFileSync(new URL("../data/ai_energy.json", import.meta.url), "utf-8"));
if (drawn["/ai-energy"]) {
  const fig = (k) => (new RegExp(`data-fig="${k}">([^<]*)<`).exec(drawn["/ai-energy"]) ?? [])[1];
  const pubs = new Set(ai.rows.map((r) => r.x_title)).size;
  ok(fig("h-figures") === String(ai.rows.length), `/ai-energy: Figures ${fig("h-figures")}, the file's ${ai.rows.length} rows`);
  ok(fig("h-publications") === String(pubs), `/ai-energy: Publications ${fig("h-publications")}, the file's ${pubs} titles`);
  const newest = [...ai.rows].sort((a, b) => b.event_date.localeCompare(a.event_date))[0];
  const words = new Date(`${newest.event_date}T00:00:00Z`).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
  ok(fig("h-newest") === words, `/ai-energy: Newest ${fig("h-newest")}, the file's newest date`);
  ok((drawn["/ai-energy"].match(/data-ai-row="/g) ?? []).length === ai.rows.length, `/ai-energy: one table row a figure (${ai.rows.length})`);
}

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
