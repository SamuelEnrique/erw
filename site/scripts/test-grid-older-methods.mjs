// Energy Research Warehouse (ERW) site, session 1421 (chain 111): the Grid tool's older blocks (session 1420's named
// panels: Right now, Batteries, What it costs, What is being built, Reliability's three tables, the mix in that hour) link
// the section of the note that defines each (lib/gridAnchors.ts OLDER_BLOCKS and one METHOD_ constant a link, outside
// GRID_METHOD, whose 17 panels scripts/test-grid-methods.mjs holds and tests/test_session1184.py counts). Without a
// build, a server or a request leaving this machine.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-older-methods.mjs
//
// Each committed note is rendered by the site's own renderer (lib/markdown.ts render, as /data/methods/[slug] draws it),
// never by a copy of its rule, and for each constant:
//   heading   its fragment is an id the rendered note holds, judged by check-links.mjs's own anchorOk, the id of the
//             heading named below, and the id lib/markdown.ts headingSlugs writes for that heading among the note's
//             headings in order (a fragment is never written by hand: a heading renamed fails here by name)
//   section   the section under that heading says what the block draws (a few words of it, below)
//   judge     check-links.mjs's judge finds each method page and anchor, as a landing's run of it would
//   code      each link is written in its block's component as <Link href={METHOD_...}> whose words say Method, and
//             check-methods.mjs reads each note as one of /grid's
// scripts/test-grid-render.mjs holds the drawn side: each older block's case carries its anchor and its method links.
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
const BASE = "https://erw-session1421.invalid";

/** Each constant: the heading its fragment opens as the note writes it, words of its section that name the block, and the
 *  component that draws the link. */
const OLDER_HEADING = {
  METHOD_RIGHT_NOW: ["\"Right now\" and the mix in that hour, what each figure is (session 1421)", "\"Right now: demand\" (grid_rightnow_<grid>", "components/grid/YourGrid.tsx"],
  METHOD_NOW_MIX: ["\"Right now\" and the mix in that hour, what each figure is (session 1421)", "\"The mix in that hour\" (grid_nowmix_<grid>", "components/grid/NowView.tsx"],
  METHOD_BATTERIES: ["The figures on the page and their keys", "a grid's block \"Batteries\"", "components/grid/YourGrid.tsx"],
  METHOD_COST: ["The figures on the page and their keys", "a grid's block \"What it costs\"", "components/grid/YourGrid.tsx"],
  METHOD_BUILDING_QUEUE: ["The figures on the grid page and their keys", "a grid's block \"What is being built\"", "components/grid/YourGrid.tsx"],
  METHOD_BUILDING_DATACENTERS: ["Grid pages: which grid a facility belongs to (session 36A)", "The grid pages (/grid/<slug>, session 35) count the facilities of their grid", "components/grid/YourGrid.tsx"],
  METHOD_RELIABILITY_NOTICES: ["1. Every notice since 1998: caiso_grid_emergencies", "214 of the 232 year-type counts match", "components/grid/Reliability.tsx"],
  METHOD_RELIABILITY_DAILY: ["2. How tight was it: caiso_reliability_daily (derived)", "the evening peak less the afternoon mean", "components/grid/Reliability.tsx"],
};

const decode = (s) => s.replace(/<[^>]*>/g, "").replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const rendered = new Map();
/** A committed note rendered as /data/methods/<note> draws it: its ids (as check-links reads a page's) and each heading's
 *  id, text, html and section (the text up to the next heading of its level or above). */
function note(slug) {
  if (rendered.has(slug)) return rendered.get(slug);
  const rel = `docs/methods/${slug}.md`;
  const html = render(fs.readFileSync(path.join(ROOT, rel), "utf-8"), rel);
  const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]).concat([...html.matchAll(/<a name="([^"]+)"/g)].map((m) => m[1]));
  const heads = [...html.matchAll(/<h([1-6]) id="([^"]+)">([\s\S]*?)<\/h\1>/g)].map((m) => ({ depth: Number(m[1]), id: m[2], html: m[3], text: decode(m[3]), at: m.index, end: m.index + m[0].length }));
  for (const [i, h] of heads.entries()) {
    const next = heads.slice(i + 1).find((x) => x.depth <= h.depth);
    h.section = decode(html.slice(h.end, next ? next.at : html.length)).replace(/\s+/g, " ");
  }
  const r = { ids, heads };
  rendered.set(slug, r);
  return r;
}
const split = (href) => { const m = /^\/data\/methods\/([a-z0-9_]+)#(.+)$/.exec(href ?? ""); return m ? { slug: m[1], frag: m[2] } : null; };

test("each older block's method is a constant of lib/gridAnchors.ts, its fragment the renderer's id for its heading, its section naming the block", () => {
  const used = [...new Set(GA.OLDER_BLOCKS.flatMap((b) => b.methods))].sort();
  assert.deepEqual(used, [...new Set(Object.keys(OLDER_HEADING).map((c) => GA[c]))].sort(), "OLDER_BLOCKS links exactly the constants named here");
  for (const [c, [heading, words]] of Object.entries(OLDER_HEADING)) {
    const s = split(GA[c]);
    assert.ok(s, `${c}: ${GA[c]} is not /data/methods/<note>#<id>`);
    const n = note(s.slug);
    assert.ok(L.anchorOk(s.frag, n.ids), `${c}: /data/methods/${s.slug} holds no id "${s.frag}"`);
    const h = n.heads.find((x) => x.id === s.frag);
    assert.ok(h, `${c}: "${s.frag}" is not a heading's id`);
    assert.equal(h.text, heading, `${c}: the heading at #${s.frag}`);
    // the renderer's own slug function over the note's headings in order, as render calls it (a name met twice takes "-1")
    const slugs = headingSlugs();
    const ids = n.heads.map((x) => slugs.next(x.html));
    assert.equal(ids[n.heads.indexOf(h)], s.frag, `${c}: headingSlugs of "${heading}"`);
    assert.ok(h.section.includes(words), `${c}: the section "${h.text}" does not say "${words}"`);
  }
});

test("check-links' judge finds each older block's method page and anchor, and names an anchor one letter off", () => {
  const links = Object.keys(OLDER_HEADING).map((c) => ({ href: new URL(GA[c], BASE).href, words: `Method (${c})` }));
  const slugs = [...new Set(Object.keys(OLDER_HEADING).map((c) => split(GA[c]).slug))];
  const answers = new Map(slugs.map((s) => [`/data/methods/${s}`, { status: 200, chain: [`/data/methods/${s}`], inReview: false }]));
  const idsOf = new Map(slugs.map((s) => [`/data/methods/${s}`, note(s).ids]));
  const pages = [{ page: "/grid?grid=caiso", address: "/grid?grid=caiso", links, ids: [] }];
  assert.deepEqual(L.judge(pages, answers, idsOf, BASE, [], []).map(L.line), []);
  const bad = L.judge([{ ...pages[0], links: [{ href: `${BASE}${GA.METHOD_COST}x`, words: "Method" }] }], answers, idsOf, BASE, [], []);
  assert.equal(bad.length, 1);
  assert.equal(bad[0].kind, "anchor");
});

test("each link is written in its block's component as a Link to its constant whose words say Method, and check-methods reads each note for /grid", () => {
  for (const [c, [, , file]] of Object.entries(OLDER_HEADING)) {
    const src = fs.readFileSync(path.join(SITE, file), "utf-8");
    const m = [...src.matchAll(new RegExp(`<(?:Link|SiteLink)\\b[^>]*?href=\\{${c}\\}[^>]*>([^<]{0,80})<`, "g"))];
    assert.ok(m.length, `${c}: no <Link href={${c}}> in ${file}`);
    for (const x of m) assert.match(x[1], /\bmethod\b/i, `${c}: the link's words "${x[1]}"`);
  }
  const notes = CM.notesOf(CM.codeFiles(CM.pageFile("/grid")));
  for (const s of new Set(Object.keys(OLDER_HEADING).map((c) => split(GA[c]).slug))) assert.ok(notes.has(s), `check-methods reads no link to ${s} in /grid's code`);
});
