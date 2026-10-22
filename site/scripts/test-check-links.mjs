// Energy Research Warehouse (ERW) site, session 581: the test of scripts/check-links.mjs on a fixture site.
//
//   node scripts/test-check-links.mjs                 the judging, the redirects and the anchors, on a site served here
//   CHECK_LINKS_BROWSER_TEST=1 node scripts/...       and the same fixture read end to end in the machine's browser
//
// The fixture is a small site served in this process on a free port of 127.0.0.1: one page links to a page that
// answers, one that answers 404, one through a redirect, one that loops, one that answers the in-review page, one
// fragment it holds and one it does not, a link that waits for a ruling, and three links that leave the site. No
// request leaves the machine. Exit 0 when every case is judged as it should be.
import http from "node:http";
import * as L from "./check-links.mjs";
import { withBrowser } from "./browser.mjs";

let bad = 0, n = 0;
const ok = (cond, what) => { n += 1; if (!cond) bad += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); };

const page = (body, ids = []) => `<!doctype html><html><body>${ids.map((i) => `<h2 id="${i}">${i}</h2>`).join("")}${body}</body></html>`;
const A = page([
  '<a href="/b">to b</a>', '<a href="/c">to c</a>', '<a href="/old">the old address</a>', '<a href="/loop">round</a>',
  '<a href="/review">a page in review</a>', '<a href="/b#here">b, here</a>', '<a href="/b#nowhere">b, nowhere</a>',
  '<a href="#self">this page</a>', '<a href="#top">top</a>', '<a href="/waiting">a ruling</a>', '<a href="/b?x=1&amp;y=2">b with a query</a>',
  '<a href="https://example.com/">elsewhere</a>', '<a href="mailto:x@example.com">mail</a>', '<a href="//example.org/c">another site</a>',
].join(" "), ["self"]);
const ROUTES = {
  "/a": [200, A], "/b": [200, page("b", ["here"])], "/b?x=1&y=2": [200, page("b again", ["here"])],
  "/review": [200, page('<div data-in-review="1">in review</div>')], "/waiting": [404, page("not yet")],
};
const server = http.createServer((req, res) => {
  if (req.url === "/old") { res.writeHead(308, { Location: "/b" }); return res.end(); }
  if (req.url === "/loop") { res.writeHead(307, { Location: "/loop" }); return res.end(); }
  const r = ROUTES[req.url] ?? [404, page("not found")];
  res.writeHead(r[0], { "Content-Type": "text/html; charset=utf-8" });
  res.end(r[1]);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

try {
  // 1. the pure parts
  ok(L.internalTarget(`${base}/b#here`, base)?.address === "/b" && L.internalTarget(`${base}/b#here`, base)?.hash === "here", "internalTarget splits the address and the fragment");
  ok(L.internalTarget(`${base}/b?x=1`, base)?.hash === null, "internalTarget: no fragment is null");
  ok(L.internalTarget("https://example.com/", base) === null && L.internalTarget("mailto:x@example.com", base) === null && L.internalTarget("javascript:void(0)", base) === null, "internalTarget: a link off the site is not checked");
  ok(L.internalTarget(`${base}/b#a%20b`, base)?.hash === "a b", "internalTarget decodes the fragment");
  ok(L.anchorOk(null, []) && L.anchorOk("", []) && L.anchorOk("top", []) && L.anchorOk("x", ["x"]) && !L.anchorOk("y", ["x"]), "anchorOk: the top, a held id, a missing id");

  // 2. the answers, against the fixture
  const a = async (p) => L.answer(base, p, "erw_view=internal");
  const b = await a("/b"), c = await a("/c"), old = await a("/old"), loop = await a("/loop"), rev = await a("/review");
  ok(b.status === 200 && b.chain.length === 1 && !b.inReview, "answer: /b answers 200 directly");
  ok(c.status === 404, "answer: /c answers 404");
  ok(old.status === 200 && old.chain.join(" ") === "/old /b", "answer: /old answers 200 through its redirect to /b");
  ok(typeof loop.status === "string" && loop.status.includes("more than"), "answer: a redirect loop stops and says so");
  ok(rev.status === 200 && rev.inReview, "answer: the in-review page is seen");

  // 3. the judging, from pages as the browser reads them (absolute hrefs)
  const links = [...A.matchAll(/<a href="([^"]+)">([^<]+)<\/a>/g)].map((m) => ({ href: new URL(m[1].replace(/&amp;/g, "&"), `${base}/a`).href, words: m[2] }));
  const read = [{ page: "/a", address: "/a", links, ids: ["self"] }];
  const addresses = [...new Set(links.map((l) => L.internalTarget(l.href, base)).filter(Boolean).map((t) => t.address))];
  ok(addresses.length === 8 && !addresses.some((x) => x.includes("example")), `the addresses asked for are the eight on the site, /a for its own fragments (${addresses.join(" ")})`);
  const answers = new Map();
  await L.pool(addresses, 3, async (x) => answers.set(x, await a(x)));
  const waits = [{ href: "/waiting", why: "the fixture's ruling" }];
  const f = L.judge(read, answers, new Map([["/b", ["here"]]]), base, waits);
  const kinds = (k) => f.filter((x) => x.kind === k).map((x) => x.href).sort().join(" ");
  ok(kinds("broken") === "/c /loop", `broken: /c and /loop (${kinds("broken")})`);
  ok(kinds("anchor") === "/b#nowhere", `anchor: /b#nowhere (${kinds("anchor")})`);
  ok(kinds("redirect") === "/old", `redirect: /old (${kinds("redirect")})`);
  ok(kinds("in-review") === "/review", `in-review: /review (${kinds("in-review")})`);
  ok(kinds("waits") === "/waiting", `waits: /waiting, listed and not failing (${kinds("waits")})`);
  ok(f.length === 6, `six findings in all, none for /b, /b#here, #self, #top or the query (${f.length})`);
  ok(f[0].kind === "broken" && f[f.length - 1].kind === "waits", "the findings are ordered: broken first, waits last");
  ok(L.line(f.find((x) => x.href === "/c")) === 'broken | /c | "to c" | on /a | answers 404', "a finding's line names the kind, the href, the words, the page and why");
  const two = L.judge([...read, { ...read[0], page: "/a2", address: "/a2" }], answers, new Map([["/b", ["here"]]]), base, waits);
  ok(two.find((x) => x.href === "/c").pages.length === 2 && L.line(two.find((x) => x.href === "/c")).includes("(and 1 more page)"), "a link on two pages is one finding with the count");
  ok(L.judge(read, new Map(), new Map(), base, []).every((x) => x.kind === "unread"), "an address not asked for is listed as unread, never as a pass");
  ok(L.WAITS.every((w) => typeof w.href === "string" && typeof w.why === "string"), "every entry of WAITS names its href and why");

  // 4. end to end in a browser, on request (a heavy process: take the build lock first)
  if (process.env.CHECK_LINKS_BROWSER_TEST === "1") {
    const r = await withBrowser(async (h) => L.check({ h, base, pages: ["/a"], cookie: "", log: () => {} }));
    if (r === null) console.log("skip the browser part: no browser on this machine");
    else {
      const k = (kind) => r.findings.filter((x) => x.kind === kind).map((x) => x.href).sort().join(" ");
      ok(r.read[0].links.length === 14 && r.read[0].ids.includes("self"), `browser: /a read with its 14 links and its id (${r.read[0].links.length})`);
      ok(k("broken") === "/c /loop /waiting" && k("anchor") === "/b#nowhere" && k("redirect") === "/old" && k("in-review") === "/review", "browser: the same findings as the judging alone (with /waiting broken: the run's WAITS is empty)");
    }
  }
} finally {
  // closed and left to end by itself: process.exit() with a socket closing trips a libuv assertion on Windows
  server.closeAllConnections();
  await new Promise((r) => server.close(r));
}
console.log(`test-check-links: ${n - bad} of ${n} pass`);
process.exitCode = bad ? 1 : 0;
