// Energy Research Warehouse (ERW) site, session 1184 (chain 091): each panel chains 077, 078 and 091 added to the Grid
// tool links its method, the section of its note that defines it (lib/gridAnchors.ts GRID_METHOD,
// /data/methods/<note>#<heading id>). Without a build, a server or a request leaving this machine.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-methods.mjs
//
// Each committed note (docs/methods/<note>.md) is rendered by the site's own renderer (lib/markdown.ts render, the one
// /data/methods/[slug] draws, its heading ids from headingSlugs), never by a copy of its rule, and:
//   ids        each panel's fragment is an id the rendered note holds, judged by check-links.mjs's own logic
//              (internalTarget, anchorOk, judge on the method page's ids), under the heading named below
//   section    the section under that heading says what the panel draws (a few words of it, below)
//   code       each panel's link is written in its component as <Link href={METHOD_<PANEL>}>Method...</Link> (or
//              SiteLink), so check-methods.mjs reads it as a note of /grid (notesOf), every note of GRID_METHOD among them
//   others     every other /data/methods/<note>#<id> the Grid tool's code writes (lib/gridStress.ts STRESS_METHOD and any
//              later one) is an id of its note too
// scripts/test-grid-files.mjs holds the drawn side: each panel drawn on committed real rows carries its link.
// Exit 0 when every test passes.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import * as GA from "../lib/gridAnchors.ts";
import { headingSlugs, render } from "../lib/markdown.ts";
import * as L from "./check-links.mjs";
import * as CM from "./check-methods.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const ROOT = path.join(SITE, "..");
const BASE = "https://erw-session1184.invalid";

/** The heading each panel's link opens, as the note writes it, and words of its section that name what the panel draws. */
const HEADING = {
  network: ["The Grid tool's panels, every figure keyed (chain 077, 23 October 2026)", "grid_network_<grid>"],
  replay: ["The outside grids' demand in the replay (chain 078, 24 October 2026)", "data-grid-replay-day"],
  balance: ["The balance, said where the figures are (chain 078, 24 October 2026)", "data-grid-balance"],
  gravity: ["The Grid tool's panels, every figure keyed (chain 077, 23 October 2026)", "grid_gravity_<grid>"],
  exchangeGrids: ["The Exchange blocks under the gravity shape (session 1167)", "the Lower 48's and a grid's"],
  exchangeTies: ["The Exchange blocks under the gravity shape (session 1167)", "Each neighbour, that hour"],
  exchangeMonths: ["Who supplies a grid (session 68)", "ba_supply_monthly"],
  clean24: ["The Grid tool's panels, every figure keyed (chain 077, 23 October 2026)", "grid_clean24_<grid>"],
  mix: ["The Mix tab's energy mix, keyed, hourly and by month (chain 077, 23 October 2026)", "mixp=month"],
  scarcity: ["On the Grid tool (session 1154, 23 October 2026)", "grid_scarcity_"],
  caisoAlerts: ["On the Grid tool: the alert state (session 1155, 23 October 2026)", "grid_caisoalert_caiso"],
  ercotNotices: ["6. On the Grid tool: the notice state (session 1174, 24 October 2026)", "grid_ercotnotice_ercot"],
  ask: ["The Grid tool's panels, every figure keyed (chain 077, 23 October 2026)", "The stored answers of the Ask panel"],
  stressRamp: ["The views' figures, keyed from the committed files (chain 078, 24 October 2026)", "the evening ramp and the lowest net load, by year"],
  stressTight: ["The large tables, keyed whole (session 1168)", "what each fuel gave in the 100 tightest hours"],
  stressCalm: ["The large tables, keyed whole (session 1168)", "dark, calm stretches, by year"],
  stressGrids: ["The views' figures, keyed from the committed files (chain 078, 24 October 2026)", "The seven grids"],
};

const decode = (s) => s.replace(/<[^>]*>/g, "").replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const rendered = new Map();
/** A committed note rendered as /data/methods/<note> draws it: its html, its ids (as check-links reads a page's), and
 *  each heading's id, text and section (the text up to the next heading of its level or above). */
function note(slug) {
  if (rendered.has(slug)) return rendered.get(slug);
  const rel = `docs/methods/${slug}.md`;
  const html = render(fs.readFileSync(path.join(ROOT, rel), "utf-8"), rel);
  const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]).concat([...html.matchAll(/<a name="([^"]+)"/g)].map((m) => m[1]));
  const heads = [...html.matchAll(/<h([1-6]) id="([^"]+)">([\s\S]*?)<\/h\1>/g)].map((m) => ({ depth: Number(m[1]), id: m[2], text: decode(m[3]), at: m.index, end: m.index + m[0].length }));
  for (const [i, h] of heads.entries()) {
    const next = heads.slice(i + 1).find((x) => x.depth <= h.depth);
    h.section = decode(html.slice(h.end, next ? next.at : html.length)).replace(/\s+/g, " ");
  }
  const r = { html, ids, heads };
  rendered.set(slug, r);
  return r;
}
const split = (href) => { const m = href.match(/^\/data\/methods\/([a-z0-9_]+)#(.+)$/); return m ? { slug: m[1], frag: m[2] } : null; };

test("every panel of lib/gridAnchors.ts has a method, a section of a committed note, and no method is for no panel", () => {
  assert.deepEqual(Object.keys(GA.GRID_METHOD).sort(), Object.keys(GA.GRID_ANCHOR).sort());
  assert.deepEqual(Object.keys(HEADING).sort(), Object.keys(GA.GRID_ANCHOR).sort());
  for (const [k, href] of Object.entries(GA.GRID_METHOD)) {
    const s = split(href);
    assert.ok(s, `${k}: ${href} is not /data/methods/<note>#<id>`);
    assert.ok(fs.existsSync(path.join(ROOT, "docs", "methods", `${s.slug}.md`)), `${k}: docs/methods/${s.slug}.md`);
  }
});

test("each fragment is an id the site's renderer writes for the note, under the heading the panel follows (check-links' logic)", () => {
  for (const [k, href] of Object.entries(GA.GRID_METHOD)) {
    const { slug } = split(href);
    const n = note(slug);
    const t = L.internalTarget(new URL(href, BASE).href, BASE);
    assert.equal(t.address, `/data/methods/${slug}`, k);
    assert.ok(L.anchorOk(t.hash, n.ids), `${k}: /data/methods/${slug} holds no id "${t.hash}"`);
    const h = n.heads.find((x) => x.id === t.hash);
    assert.ok(h, `${k}: "${t.hash}" is an id but not a heading's`);
    assert.equal(h.text, HEADING[k][0], `${k}: the heading at #${t.hash}`);
    // the id is the renderer's own for that heading text, the first of its name in the note (no "-1")
    const slugs = headingSlugs();
    assert.equal(slugs.next(HEADING[k][0].replace(/&/g, "&amp;").replace(/'/g, "&#39;")), t.hash, `${k}: headingSlugs of the heading`);
    assert.ok(h.section.includes(HEADING[k][1]), `${k}: the section "${h.text}" does not say "${HEADING[k][1]}"`);
  }
});

test("check-links' judge finds each panel's method page and anchor, and names an anchor one letter off", () => {
  const links = Object.entries(GA.GRID_METHOD).map(([k, href]) => ({ href: new URL(href, BASE).href, words: `Method (${k})` }));
  const pages = [{ page: "/grid", address: "/grid", links, ids: [] }];
  const slugs = [...new Set(Object.values(GA.GRID_METHOD).map((h) => split(h).slug))];
  const answers = new Map(slugs.map((s) => [`/data/methods/${s}`, { status: 200, chain: [`/data/methods/${s}`], inReview: false }]));
  const idsOf = new Map(slugs.map((s) => [`/data/methods/${s}`, note(s).ids]));
  const found = L.judge(pages, answers, idsOf, BASE, [], []);
  assert.deepEqual(found.map(L.line), []);
  const off = [{ ...pages[0], links: [{ href: `${BASE}${GA.GRID_METHOD.balance}x`, words: "Method" }] }];
  const bad = L.judge(off, answers, idsOf, BASE, [], []);
  assert.equal(bad.length, 1);
  assert.equal(bad[0].kind, "anchor");
  assert.ok(L.line(bad[0]).includes(`holds no id "${split(GA.GRID_METHOD.balance).frag}x"`), L.line(bad[0]));
});

/** A panel's constant in lib/gridAnchors.ts: METHOD_ and its key in capitals, a word a capital (exchangeGrids is
 *  METHOD_EXCHANGE_GRIDS). */
const constOf = (k) => `METHOD_${k.replace(/([a-z0-9])([A-Z])/g, "$1_$2").toUpperCase()}`;

test("each panel's link is written in its component as a Link to its METHOD_<PANEL> whose words say Method, and check-methods reads every note", () => {
  for (const k of Object.keys(GA.GRID_METHOD)) assert.equal(GA[constOf(k)], GA.GRID_METHOD[k], `${k}: ${constOf(k)} is its GRID_METHOD`);
  const files = ["components/grid", "components/mix"].flatMap((d) => fs.readdirSync(path.join(SITE, d)).filter((f) => f.endsWith(".tsx")).map((f) => path.join(SITE, d, f)));
  const src = files.map((f) => fs.readFileSync(f, "utf-8")).join("\n");
  for (const k of Object.keys(GA.GRID_METHOD)) {
    const m = [...src.matchAll(new RegExp(`<(?:Link|SiteLink)\\b[^>]*?href=\\{${constOf(k)}\\}[^>]*>([^<]{0,80})<`, "g"))];
    assert.ok(m.length, `${k}: no <Link href={${constOf(k)}}> in components/grid or components/mix`);
    for (const x of m) assert.match(x[1], /\bmethods?\b/i, `${k}: the link's words "${x[1]}"`);
  }
  assert.ok(!/href=\{GRID_METHOD/.test(src), "a component links GRID_METHOD itself: scripts/page_tables.py would read every note's name in it as a table");
  const notes = CM.notesOf(CM.codeFiles(CM.pageFile("/grid")));
  for (const s of new Set(Object.values(GA.GRID_METHOD).map((h) => split(h).slug))) assert.ok(notes.has(s), `check-methods reads no link to ${s} in /grid's code (it reads ${[...notes.keys()].join(", ")})`);
});

test("every other /data/methods/<note>#<id> the Grid tool's code writes is an id of its note", () => {
  const dirs = ["components/grid", "components/mix", "app/grid", "lib"];
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(path.join(d, e.name)) : /\.tsx?$/.test(e.name) ? [path.join(d, e.name)] : []));
  const files = dirs.flatMap((d) => (d === "lib" ? fs.readdirSync(path.join(SITE, d)).filter((f) => /^(grid|network|mix|scarcity|caiso)/i.test(f) && /\.ts$/.test(f)).map((f) => path.join(SITE, d, f)) : walk(path.join(SITE, d))));
  let n = 0;
  for (const f of files) {
    for (const m of fs.readFileSync(f, "utf-8").matchAll(/\/data\/methods\/([a-z0-9_]+)#([A-Za-z0-9_-]+)/g)) {
      n += 1;
      assert.ok(fs.existsSync(path.join(ROOT, "docs", "methods", `${m[1]}.md`)), `${path.relative(SITE, f)}: ${m[0]}`);
      assert.ok(L.anchorOk(m[2], note(m[1]).ids), `${path.relative(SITE, f)}: /data/methods/${m[1]} holds no id "${m[2]}"`);
    }
  }
  assert.ok(n >= Object.keys(GA.GRID_METHOD).length + 1, `${n} links read`);   // the seventeen and STRESS_METHOD at least
});
