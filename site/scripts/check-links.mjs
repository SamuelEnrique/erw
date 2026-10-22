// Energy Research Warehouse (ERW) site, session 581: every internal link and every anchor resolves.
//
//   npm run build && npm start                       (the site on http://localhost:3000, or another port)
//   node scripts/check-links.mjs [base-url]          default http://localhost:3000
//
// Reads every page of check-values' list (`node scripts/check-values.mjs --list`: its pages and its two internal
// drafts) and every method page under /data/methods/ (the documents content/docs.json holds, as the build wrote it), in
// the internal view, in a real browser: SiteLink draws a link to a page in review as a <span> until the browser knows
// the internal view (useInternal() is client-side), so the HTML a fetch reads holds almost no link while every page is
// in review. On each page it takes every <a href> that stays on the site, and every id the page holds. Then:
//   1. each internal address linked (its path and query) is asked for with the internal cookie, redirects followed one
//      by one: an address that does not end at 200 is listed, and so is one that answers through a redirect (the link
//      should name where it lands), and one that answers the in-review page with the internal cookie;
//   2. each fragment (#name) is looked for among the ids (and <a name>) of the page it names: a page linked with a
//      fragment and not on the list is opened in the browser for its ids. "#" and "#top" are the top of the page.
// Each finding is one line: `<kind> | <href> | "<the link's words>" | on <page> (and N more pages) | why`. A link the
// header, the menu or the footer draws on every page is one line, with the count of pages that carry it.
//
// WAITS below lists the links whose right target waits for Samuel's ruling: they are printed as "waits", not changed,
// and do not fail the run. Nothing is written but runs/check-links/links.json (CHECK_LINKS_OUT): every page read, its
// links and ids, and the findings. The browser never counts a usage (DNT and Sec-GPC are sent, /api/usage and the
// model's routes are blocked) and every request carries x-erw-check: 1.
//
// CHECK_LINKS_PAGES=/a,/b reads only those pages (a rerun after a fix). Exit codes: 0 every link and anchor resolves;
// 1 a finding; 2 the run could not be made (no browser, no INTERNAL_COSTS_TOKEN, the internal view did not open).
// Its test is scripts/test-check-links.mjs (a fixture site served in process).
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { env, sleep, unlockPost, withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const REQUEST_MS = Number(process.env.CHECK_LINKS_REQUEST_S ?? 120) * 1000;
const MAX_HOPS = 5;
const HEADERS = { "x-erw-check": "1", DNT: "1", "Sec-GPC": "1", "User-Agent": "erw-check-links (node)" };
// The routes a page may call by itself that must not be reached by a check: the usage counts, and the model's routes.
export const BLOCKED = ["*/api/usage*", "*/api/ask*", "*/api/thesis*", "*/api/analysis*", "*/api/subscribe*"];

/** The links whose right target is a ruling of Samuel's: listed as "waits", never changed by a session. */
export const WAITS = [
  // session 581: none found on the run of 22 October 2026 waits for a ruling; an entry is { href, why }
];

/** An href, read in the page as `a.href` (absolute), split into the address asked for and its fragment; null for a
 * link that leaves the site (another origin, mailto:, tel:, javascript:). */
export function internalTarget(href, base) {
  let u;
  try { u = new URL(href, base); } catch { return null; }
  if (!/^https?:$/.test(u.protocol) || u.origin !== new URL(base).origin) return null;
  const hash = u.hash ? decodeURIComponent(u.hash.slice(1)) : null;
  return { address: u.pathname + u.search, hash };
}

/** Does a fragment name a place the page holds? "" and "top" are the top of every page (the HTML standard). */
export function anchorOk(hash, ids) {
  if (hash === null || hash === "" || hash.toLowerCase() === "top") return true;
  return ids.includes(hash);
}

/** The findings, from what was read: `pages` [{ page, address, links: [{ href, words }], ids }], `answers` a Map from an
 * address to { status, chain: [addresses], inReview }, `idsOf` a Map from an address to its ids (or null: not read). */
export function judge(pages, answers, idsOf, base, waits = WAITS) {
  const found = new Map();   // one entry per (kind, href, words)
  const add = (kind, href, words, page, why) => {
    const key = `${kind}\u0000${href}\u0000${words}`;
    const f = found.get(key) ?? { kind, href, words, pages: [], why };
    if (!f.pages.includes(page)) f.pages.push(page);
    found.set(key, f);
  };
  for (const p of pages) {
    for (const l of p.links) {
      const t = internalTarget(l.href, base);
      if (!t) continue;
      const shown = t.address + (t.hash !== null ? `#${t.hash}` : "");
      const wait = waits.find((w) => w.href === t.address || w.href === shown);
      if (wait) { add("waits", shown, l.words, p.page, wait.why); continue; }
      const a = answers.get(t.address);
      if (!a) { add("unread", shown, l.words, p.page, "the address was not asked for"); continue; }
      if (a.status !== 200) {
        add("broken", shown, l.words, p.page, `answers ${a.status}${a.chain.length > 1 ? ` (through ${a.chain.join(" -> ")})` : ""}`);
        continue;
      }
      if (a.chain.length > 1) add("redirect", shown, l.words, p.page, `answers 200 at ${a.chain[a.chain.length - 1]} through ${a.chain.join(" -> ")}`);
      if (a.inReview) add("in-review", shown, l.words, p.page, "answers the in-review page with the internal cookie");
      if (t.hash !== null) {
        const ids = t.address === p.address ? p.ids : idsOf.get(a.chain[a.chain.length - 1]) ?? idsOf.get(t.address);
        if (!ids) add("unread", shown, l.words, p.page, "the page it names was not read for its anchors");
        else if (!anchorOk(t.hash, ids)) add("anchor", shown, l.words, p.page, `${a.chain[a.chain.length - 1]} holds no id "${t.hash}"`);
      }
    }
  }
  const order = { broken: 0, anchor: 1, "in-review": 2, redirect: 3, unread: 4, waits: 5 };
  return [...found.values()].sort((x, y) => order[x.kind] - order[y.kind] || x.href.localeCompare(y.href));
}

/** The line a finding prints. */
export function line(f) {
  const more = f.pages.length > 1 ? ` (and ${f.pages.length - 1} more page${f.pages.length > 2 ? "s" : ""})` : "";
  return `${f.kind} | ${f.href} | "${f.words}" | on ${f.pages[0]}${more} | ${f.why}`;
}

/** Ask for an address with the cookie, following each redirect by hand: { status, chain, inReview }. */
export async function answer(base, address, cookie) {
  const chain = [address];
  let url = new URL(address, base).href;
  for (let hop = 0; ; hop += 1) {
    let res;
    try {
      res = await fetch(url, { redirect: "manual", headers: { ...HEADERS, ...(cookie ? { Cookie: cookie } : {}) }, signal: AbortSignal.timeout(REQUEST_MS) });
    } catch (e) {
      return { status: `no answer (${e.name === "TimeoutError" ? `${REQUEST_MS / 1000} s` : e.message})`, chain, inReview: false };
    }
    const loc = res.headers.get("location");
    if (res.status >= 300 && res.status < 400 && loc) {
      await res.body?.cancel();
      if (hop >= MAX_HOPS) return { status: `${res.status}, more than ${MAX_HOPS} redirects`, chain, inReview: false };
      const next = new URL(loc, url);
      if (next.origin !== new URL(base).origin) return { status: `${res.status} to another site (${next.href})`, chain, inReview: false };
      url = next.href;
      chain.push(next.pathname + next.search);
      continue;
    }
    let inReview = false;
    if ((res.headers.get("content-type") ?? "").includes("text/html")) inReview = (await res.text()).includes('data-in-review="1"');
    else await res.body?.cancel();
    return { status: res.status, chain, inReview };
  }
}

/** Run `fn` over `items`, `n` at a time. */
export async function pool(items, n, fn) {
  const out = new Array(items.length);
  let next = 0;
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => {
    while (next < items.length) { const i = next; next += 1; out[i] = await fn(items[i], i); }
  }));
  return out;
}

// What the browser reads on a page: every link (as the browser resolves it, and its words) and every id.
const READ = `(() => ({
  links: [...document.querySelectorAll('a[href]')].map((a) => ({ href: a.href, words: (a.innerText || a.getAttribute('aria-label') || a.title || '').replace(/\\s+/g, ' ').trim().slice(0, 80) })),
  ids: [...document.querySelectorAll('[id]')].map((e) => e.id).concat([...document.querySelectorAll('a[name]')].map((a) => a.getAttribute('name'))),
  gated: document.querySelectorAll('.gate-review, .gate-plain').length,
  inReview: !!document.querySelector('[data-in-review="1"]'),
}))()`;

/** Read pages in the browser `h` ({ go, evaluate }); returns [{ page, address, links, ids, gated, inReview, error }]. */
export async function readPages(h, base, list, log = () => {}) {
  const out = [];
  for (const page of list) {
    const u = new URL(page, base);
    const rec = { page, address: u.pathname + u.search, links: [], ids: [], gated: 0, inReview: false, error: null };
    try {
      await h.go(u.href);
      await sleep(300);
      // the internal view redraws the links once the page has hydrated: wait (up to 5 s) for the review spans to go
      for (let i = 0; i < 25 && (await h.evaluate("document.querySelectorAll('.gate-review, .gate-plain').length")) > 0; i += 1) await sleep(200);
      Object.assign(rec, await h.evaluate(READ));
      const landed = await h.evaluate("location.pathname + location.search");
      if (landed !== rec.address) rec.landed = landed;
    } catch (e) {
      rec.error = e.message;
    }
    log(`read ${page}: ${rec.links.length} links, ${rec.ids.length} ids${rec.gated ? `, ${rec.gated} links still drawn as review spans` : ""}${rec.error ? `, ERROR ${rec.error}` : ""}`);
    out.push(rec);
  }
  return out;
}

/** The pages of the run: check-values' list (pages and internal drafts) and the method pages the build holds. */
export function pageList() {
  const listed = JSON.parse(execFileSync(process.execPath, [path.join(here, "check-values.mjs"), "--list"], { encoding: "utf-8" }));
  const docs = path.join(here, "..", "content", "docs.json");
  if (!fs.existsSync(docs)) throw new Error("content/docs.json is missing: build the site first (npm run build)");
  const methods = Object.keys(JSON.parse(fs.readFileSync(docs, "utf-8")).methods ?? {}).sort().map((s) => `/data/methods/${s}`);
  return [...new Set([...listed.pages, ...listed.internal, ...methods])];
}

/** The whole check against a running site; `h` is the browser, `cookie` the internal view's for the fetches. */
export async function check({ h, base, pages, cookie, log = console.log }) {
  const read = await readPages(h, base, pages, log);
  const addresses = [...new Set(read.flatMap((p) => p.links.map((l) => internalTarget(l.href, base)).filter(Boolean).map((t) => t.address)))].sort();
  log(`${addresses.length} internal addresses linked from ${read.length} pages: asking for each`);
  const answers = new Map();
  await pool(addresses, 4, async (a) => { answers.set(a, await answer(base, a, cookie)); });
  const idsOf = new Map(read.filter((p) => !p.error).map((p) => [p.address, p.ids]));
  const needIds = [...new Set(read.flatMap((p) => p.links.map((l) => internalTarget(l.href, base)).filter((t) => t && t.hash && t.hash.toLowerCase() !== "top")
    .map((t) => { const a = answers.get(t.address); return a && a.status === 200 ? a.chain[a.chain.length - 1] : null; })))].filter((a) => a && !idsOf.has(a));
  if (needIds.length) {
    log(`${needIds.length} pages linked with a fragment and not on the list: reading their anchors`);
    for (const p of await readPages(h, base, needIds, log)) if (!p.error) idsOf.set(p.address, p.ids);
  }
  const findings = judge(read, answers, idsOf, base);
  const errors = read.filter((p) => p.error || p.inReview || p.gated);
  return { read, answers: Object.fromEntries(answers), findings, errors };
}

async function main() {
  const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
  const token = env("INTERNAL_COSTS_TOKEN");
  if (!token) { console.log("check-links: INTERNAL_COSTS_TOKEN is not set: the pages in review cannot be read"); return 2; }
  const u = await unlockPost(base, token);
  const cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  if (!cookie) { console.log(`check-links: no internal cookie from ${base}/internal/unlock (status ${u.status})`); return 2; }
  const only = (process.env.CHECK_LINKS_PAGES ?? "").split(",").map((s) => s.trim()).filter(Boolean);
  const pages = only.length ? only : pageList();
  console.log(`check-links: ${pages.length} pages at ${base}, in the internal view`);
  const result = await withBrowser(async (h) => {
    await h.send("Network.setExtraHTTPHeaders", { headers: { "x-erw-check": "1", DNT: "1", "Sec-GPC": "1" } });
    await h.send("Network.setBlockedURLs", { urls: BLOCKED });
    await h.unlock(base);
    return check({ h, base, pages, cookie });
  });
  if (result === null) { console.log("check-links: NOT PROVEN (no browser on this machine)"); return 2; }
  const out = process.env.CHECK_LINKS_OUT ?? path.join(here, "..", "..", "runs", "check-links", "links.json");
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify({ base, read_utc: new Date().toISOString(), ...result }, null, 1));
  for (const p of result.errors) console.log(`page | ${p.page} | ${p.error ? `not read: ${p.error}` : p.inReview ? "the in-review page was shown in the internal view" : `${p.gated} links still drawn as review spans`}`);
  for (const f of result.findings) console.log(line(f));
  const failing = result.findings.filter((f) => f.kind !== "waits");
  const nLinks = result.read.reduce((s, p) => s + p.links.length, 0);
  console.log(`check-links: ${result.read.length} pages, ${nLinks} links, ${Object.keys(result.answers).length} addresses; ${failing.length} findings, ${result.findings.length - failing.length} waiting for a ruling, ${result.errors.length} pages not read cleanly (detail in ${out})`);
  return failing.length || result.errors.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main().then((c) => process.exit(c), (e) => { console.error(`check-links: ${e.stack ?? e.message}`); process.exit(2); });
}
