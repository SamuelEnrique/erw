// Energy Research Warehouse (ERW) site, session 5101: the curtain and the App Router's transport addresses, without a
// server and without a network (site/proxy.ts; docs/reviews/security-faults-2026-11-13.md, row 1).
//
//   node --import ./scripts/alias-register.mjs scripts/test-curtain.mjs
//
// On 13 November 2026 a visitor could read a page in review at <page>.segments/<segment>.segment.rsc: the proxy's
// matcher left every address with an extension alone. These tests hold the two halves of the fix: the matcher runs on
// those addresses, and the proxy's rule closes them. The matcher is compiled as Next compiles it: by Next's own
// function when the package is installed (site/node_modules, or the folder NEXT_DIR names), and by the same
// arithmetic written out here when it is not; with the package, the two must agree. Exits 1 on the first failure.
import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const proxy = await import("../proxy.ts");
const release = await import("../lib/release.ts");

let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };

// ---------------------------------------------------------------------------------------------------------------------
// the matcher, compiled
// ---------------------------------------------------------------------------------------------------------------------
const SOURCE = proxy.config.matcher[0];
/** Next 16.4's getMiddlewareMatchers for one source that is a single group, written out: an optional data prefix, the
 * group, an optional transport suffix, an optional closing slash. */
function compiledHere(source) {
  assert.match(source, /^\/\(.*\)$/s, "the matcher is one group after a slash");
  const inner = source.slice(2, -1).replaceAll("/", "\\/");
  return `^(?:\\/(_next\\/data\\/[^/]{1,}))?(?:\\/(${inner}))(\\.json|\\.rsc|\\.segments\\/.+\\.segment\\.rsc)?[\\/#\\?]?$`;
}
function compiledByNext(source) {
  for (const dir of [process.env.NEXT_DIR, path.join(site, "node_modules", "next")]) {
    const file = dir && path.join(dir, "dist", "build", "analysis", "get-page-static-info.js");
    if (!file || !fs.existsSync(file)) continue;
    const { getMiddlewareMatchers } = createRequire(import.meta.url)(file);
    return getMiddlewareMatchers(source, {})[0].regexp;
  }
  return null;
}
const here = compiledHere(SOURCE), byNext = compiledByNext(SOURCE);
const re = new RegExp(byNext ?? here);
console.log(byNext ? "the matcher is compiled by Next's own function" : "next is not installed here: the matcher is compiled by this file's own arithmetic");

await test("the matcher compiled here is the matcher Next compiles (when Next is installed)", () => {
  if (byNext) assert.equal(here, byNext);
});

const REVIEW_PAGES = ["/about", "/cost-of-power/battery", "/learn/problems/a", "/"];
const transportOf = (page) => {
  const base = page === "/" ? "/index" : page;
  return [`${base}.rsc`, `${base}.segments/_tree.segment.rsc`, `${base}.segments/_full.segment.rsc`, `${base}.segments${base}/__PAGE__.segment.rsc`, `${base}.segments/_index.segment.rsc`];
};

await test("the proxy runs on every page and on every transport address of a page", () => {
  for (const page of REVIEW_PAGES) {
    assert.equal(re.test(page), true, page);
    for (const t of transportOf(page)) assert.equal(re.test(t), true, t);
  }
  for (const t of ["/about.RSC", "/about.segments/_tree.segment.RSC", "/in-review.rsc"]) assert.equal(re.test(t), true, t);
});

await test("the proxy still leaves alone what it always left alone", () => {
  for (const p of ["/api/ask", "/api/usage", "/api/x.rsc", "/internal/open", "/internal/unlock", "/internal/open.rsc", "/_next/static/chunks/a.js", "/_next/static/a.rsc",
    "/in-review", "/favicon.ico", "/llms.txt", "/cost-of-power/months.csv", "/cost-of-power/battery/months.csv", "/learn/problems/a/data.csv", "/about.json", "/about.html", "/robots.txt"]) {
    assert.equal(re.test(p), false, p);
  }
});

await test("the old matcher (until session 5101) skipped the transport addresses: the fault, kept as a proof", () => {
  const old = new RegExp(compiledHere("/((?!api/|internal/|_next/|in-review$|.*\\.[a-zA-Z0-9]+$).*)"));
  assert.equal(old.test("/about"), true);
  assert.equal(old.test("/about.segments/about/__PAGE__.segment.rsc"), false);
  assert.equal(old.test("/about.segments/_full.segment.rsc"), false);
});

// ---------------------------------------------------------------------------------------------------------------------
// the rule
// ---------------------------------------------------------------------------------------------------------------------
await test("pagesOf: the page a transport address stands for, in every reading; nothing for any other path", () => {
  assert.deepEqual(proxy.pagesOf("/about.rsc"), ["/about"]);
  assert.deepEqual(proxy.pagesOf("/about.segments/_tree.segment.rsc")[0], "/about");
  assert.deepEqual(proxy.pagesOf("/about.segments/about/__PAGE__.segment.rsc")[0], "/about");
  // Next's adapter hands the proxy the address with its last ".rsc" taken off
  assert.deepEqual(proxy.pagesOf("/about.segments/about/__PAGE__.segment"), ["/about"]);
  assert.deepEqual(proxy.pagesOf("/index.rsc"), ["/"]);
  assert.deepEqual(proxy.pagesOf("/index.segments/_tree.segment.rsc")[0], "/");
  assert.deepEqual(proxy.pagesOf("/cost-of-power/battery.segments/cost-of-power/battery/__PAGE__.segment.rsc")[0], "/cost-of-power/battery");
  // two readings of one address: the lazy one and Next's greedy one
  const two = proxy.pagesOf("/x.png.segments/about.segments/_full.segment.rsc");
  assert.equal(two.includes("/x.png"), true);
  assert.equal(two.includes("/x.png.segments/about"), true);
  assert.deepEqual(proxy.pagesOf("/about.RSC"), ["/about"]);
  assert.deepEqual(proxy.pagesOf("/about.rsc/"), ["/about"]);
  for (const p of ["/about", "/", "/cost-of-power/months.csv", "/llms.txt", "/about.segments", "/a.b/c"]) assert.deepEqual(proxy.pagesOf(p), [], p);
});

await test("every page is in review today: a visitor gets the curtain at a page and 404 at its transport addresses", () => {
  for (const page of REVIEW_PAGES) {
    assert.equal(release.statusOf(page), "review", `${page} is in review (site/lib/release.ts)`);
    assert.equal(proxy.visitorGets(page), "curtain", page);
    for (const t of transportOf(page)) assert.equal(proxy.visitorGets(t), "closed", t);
    // as the adapter hands it over, and written with escapes, and in capitals
    for (const t of transportOf(page).slice(1)) assert.equal(proxy.visitorGets(t.slice(0, -4)), "closed", t.slice(0, -4));
    for (const t of transportOf(page)) assert.equal(proxy.visitorGets(t.replaceAll(".", "%2E")), "closed", t.replaceAll(".", "%2E"));
    for (const t of transportOf(page)) assert.equal(proxy.visitorGets(t.replace(/rsc$/, "RSC")), "closed");
  }
  // an address made to look like a file's: one reading names a page in review, so it is closed
  assert.equal(proxy.visitorGets("/x.png.segments/about.segments/_full.segment.rsc"), "closed");
});

await test("the in-review page's own transport addresses, and a file's, stay open", () => {
  for (const p of ["/in-review.rsc", "/in-review.segments/_tree.segment.rsc", "/in-review.segments/in-review/__PAGE__.segment.rsc"]) assert.equal(proxy.visitorGets(p), "open", p);
  for (const p of ["/cost-of-power/months.csv", "/llms.txt", "/favicon.ico"]) assert.equal(proxy.visitorGets(p), "open", p);
});

await test("the proxy answers a closed address 404 without the cookie, and passes it with the cookie", async () => {
  // the three answers of next/server the proxy gives, stood in for (the alias loader's stub has json alone)
  const { NextResponse } = await import("next/server");
  NextResponse.next = () => ({ kind: "next" });
  NextResponse.rewrite = (url) => ({ kind: "rewrite", to: `${url.pathname}${url.search}`, headers: new Map() });
  // proxy.ts answers a closed address with `new NextResponse(...)`: the stub is an object, not a class, so the 404 is
  // read from the source, and the order (the cookie first) with it
  const src = fs.readFileSync(path.join(site, "proxy.ts"), "utf-8");
  assert.match(src, /if \(gets === "closed"\) \{\s*return new NextResponse\("Not found", \{ status: 404, headers: \{ "X-Robots-Tag": "noindex", "Cache-Control": "private, no-store" \} \}\);/);
  assert.match(src, /if \(await cookieOpens\(have, token\)\) return NextResponse\.next\(\);[^\n]*\n\s*if \(gets === "closed"\)/, "the cookie is asked before the 404");
  const token = "a-stand-in-token-of-thirty-two-chars";
  process.env.INTERNAL_COSTS_TOKEN = token;
  const cookie = await release.digest(token);
  const req = (p, have) => ({ nextUrl: { pathname: p, clone: () => ({ pathname: p, search: "" }) }, cookies: { get: () => (have ? { value: have } : undefined) } });
  assert.deepEqual(await proxy.proxy(req("/about.segments/_full.segment.rsc", cookie)), { kind: "next" });
  assert.deepEqual(await proxy.proxy(req("/about", cookie)), { kind: "next" });
  const curtain = await proxy.proxy(req("/about", undefined));
  assert.equal(curtain.kind, "rewrite");
  assert.equal(curtain.to, "/in-review?path=%2Fabout");
  assert.equal(curtain.headers.get("X-Robots-Tag"), "noindex");
  assert.deepEqual(await proxy.proxy(req("/in-review.rsc", undefined)), { kind: "next" });
});

console.log(`\n${n} tests passed`);
