// Energy Research Warehouse (ERW) site, session 177: the security fixes and the usage route, against a running site.
//
//   npm run build && npm start                         (the site on http://localhost:3000)
//   node scripts/check-security.mjs [base-url] [--recorded]
//
// What it asks, and what must be true:
//   1. every answer carries the security headers (next.config.ts), and every /internal address is never cached,
//      never indexed and sends no referrer;
//   2. the internal view opens from the form (POST /internal/unlock, the token in the body) with the same two cookies
//      as the old link, which still works; a wrong token, another site's form and a filled trap open nothing;
//   3. /internal/costs, /internal/ask and /internal/usage open with the cookie and no token in the address, and
//      answer 404 without it;
//   4. the routes that spend or write refuse another site's page, a stock command-line client and a body of the
//      wrong type, before anything is counted, stored or sent to a model (no model is ever called from here);
//   5. /api/usage answers 204 with no cookie whatever it is sent, and /privacy says what the site records.
// With --recorded (after migration 028 is applied, on a server that holds ASK_VISITOR_SALT): one "tool opened" is
// posted for /privacy and /internal/usage must then show at least one event. That writes one real count.
// INTERNAL_COSTS_TOKEN comes from the environment, site/.env.local or ../.env. Exits 1 on any failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
function env(name) {
  if (process.env[name]) return process.env[name];
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
      const m = line.match(/^([A-Z_]+)=(.*)$/);
      if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
    }
  }
  return undefined;
}
const args = process.argv.slice(2);
const recorded = args.includes("--recorded");
const base = (args.find((a) => !a.startsWith("--")) ?? "http://localhost:3000").replace(/\/$/, "");
const token = env("INTERNAL_COSTS_TOKEN");
const BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 erw-check";
let bad = 0, n = 0;
const ok = (cond, label, shown = "") => { n += 1; if (!cond) bad += 1; console.log(`${cond ? "ok  " : "FAIL"} ${label}${shown ? ` (${shown})` : ""}`); };
const ask = (p, init = {}) => fetch(base + p, { redirect: "manual", ...init, headers: { "User-Agent": BROWSER, ...(init.headers ?? {}) } });
const form = (o) => new URLSearchParams(o).toString();
const FORM = { "Content-Type": "application/x-www-form-urlencoded" };
const cookiesOf = (r) => (r.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]);

// 1. the headers
for (const p of ["/", "/terms", "/api/play/top", "/in-review", "/internal/open"]) {
  const r = await ask(p);
  const h = (k) => r.headers.get(k) ?? "";
  ok(h("x-content-type-options") === "nosniff" && h("x-frame-options") === "DENY" && h("referrer-policy") !== "" && h("permissions-policy").includes("camera=()")
    && h("strict-transport-security").includes("max-age=63072000") && h("content-security-policy").includes("frame-ancestors 'none'")
    && h("content-security-policy").includes("form-action 'self'") && h("content-security-policy-report-only").includes("default-src 'self'") && !h("x-powered-by"),
  `${p}: the security headers`, `HTTP ${r.status}`);
}
{
  const r = await ask("/internal/open");
  const html = await r.text();
  // the form's page sends its referrer to this site only (same-origin): under no-referrer a browser would post the
  // form with "Origin: null" (scripts/check-csp.mjs submits the form in a real browser)
  ok(r.status === 200 && (r.headers.get("cache-control") ?? "").includes("no-store") && r.headers.get("referrer-policy") === "same-origin" && (r.headers.get("x-robots-tag") ?? "").includes("noindex"),
    "/internal/open: never cached, never indexed, its referrer for this site only", `${r.headers.get("cache-control")}; ${r.headers.get("referrer-policy")}`);
  const costs = await ask("/internal/costs");
  ok(costs.headers.get("referrer-policy") === "no-referrer" && (costs.headers.get("cache-control") ?? "").includes("no-store"), "every other /internal address: no referrer, never cached", `${costs.headers.get("referrer-policy")}`);
  const tag = (html.match(/<form[^>]*>/) ?? [""])[0];   // the attributes come in the order React writes them
  ok(tag.includes('method="post"') && tag.includes('action="/internal/unlock"') && /<input[^>]*type="password"[^>]*name="token"|<input[^>]*name="token"[^>]*type="password"/.test(html), "/internal/open: a form that posts the token");
  ok(!token || !html.includes(token), "/internal/open: the page holds no token");
}

// 2. the door
if (!token || token.length < 24) {
  ok(false, "INTERNAL_COSTS_TOKEN is not set: the internal view could not be checked");
} else {
  const wrong = await ask("/internal/unlock", { method: "POST", headers: FORM, body: form({ token: "not-the-token-0000000000000000" }) });
  ok(wrong.status === 303 && (wrong.headers.get("location") ?? "").includes("/internal/open?state=") && cookiesOf(wrong).length === 0, "the form: a wrong token opens nothing", `HTTP ${wrong.status} to ${new URL(wrong.headers.get("location") ?? "/", base).pathname}`);
  const trap = await ask("/internal/unlock", { method: "POST", headers: FORM, body: form({ token, website: "x" }) });
  ok(trap.status === 303 && cookiesOf(trap).length === 0, "the form: a filled trap field opens nothing");
  const other = await ask("/internal/unlock", { method: "POST", headers: { ...FORM, Origin: "https://another-site.example" }, body: form({ token }) });
  ok(other.status === 404 && cookiesOf(other).length === 0, "the form: another site's form gets 404", `HTTP ${other.status}`);
  const right = await ask("/internal/unlock", { method: "POST", headers: { ...FORM, Origin: base }, body: form({ token }) });
  const set = cookiesOf(right);
  ok(right.status === 303 && new URL(right.headers.get("location") ?? "/x", base).pathname === "/" && set.some((c) => c.startsWith("erw_internal=")) && set.some((c) => c === "erw_view=internal"),
    "the form: the right token sets the two cookies and goes home", `HTTP ${right.status}, ${set.length} cookies`);
  ok(!(right.headers.get("location") ?? "").includes(token) && (right.headers.get("cache-control") ?? "").includes("no-store") && right.headers.get("referrer-policy") === "no-referrer", "the form: no token in the address it goes to; no-store; no referrer");
  // what a browser sends when the page's policy hides the origin: accepted only with the browser's own word
  const nulled = await ask("/internal/unlock", { method: "POST", headers: { ...FORM, Origin: "null", "Sec-Fetch-Site": "same-origin" }, body: form({ token }) });
  ok(nulled.status === 303 && cookiesOf(nulled).length === 2, "the form: 'Origin: null' with the browser's same-origin word opens", `HTTP ${nulled.status}`);
  const nullOnly = await ask("/internal/unlock", { method: "POST", headers: { ...FORM, Origin: "null" }, body: form({ token }) });
  ok(nullOnly.status === 404 && cookiesOf(nullOnly).length === 0, "the form: 'Origin: null' alone gets 404", `HTTP ${nullOnly.status}`);
  const old = await ask(`/internal/unlock?token=${encodeURIComponent(token)}`);
  const oldSet = cookiesOf(old);
  ok(old.status === 303 && oldSet.some((c) => c.startsWith("erw_internal=")) && oldSet.join("|") === set.join("|"), "the old link works as it did, with the same two cookies");
  ok((await ask("/internal/unlock?token=not-the-token-0000000000000000")).status === 404 && (await ask("/internal/unlock")).status === 404, "the old link: a wrong or missing token is 404, as before");
  const cookie = set.join("; ");

  // 3. the internal pages, by the cookie
  for (const p of ["/internal/costs", "/internal/ask", "/internal/usage"]) {
    const without = await ask(p);
    const withCookie = await ask(p, { headers: { Cookie: cookie } });
    const html = await withCookie.text();
    ok(without.status === 404 && withCookie.status === 200 && !html.includes(token), `${p}: 404 without the cookie, 200 with it, no token in the page`, `${without.status}, ${withCookie.status}`);
    ok((withCookie.headers.get("cache-control") ?? "").includes("no-store"), `${p}: never cached`);
  }
  const priv = await ask("/privacy", { headers: { Cookie: cookie } });
  const privText = (await priv.text()).replace(/<[^>]+>/g, " ");
  ok(priv.status === 200 && privText.includes("sets no tracking cookies") && privText.includes("erw_internal") && privText.includes("Do Not Track"), "/privacy says what is recorded (internal view)");
  const visitor = await ask("/privacy");
  ok(visitor.status === 200 && !(await visitor.text()).includes("data-privacy"), "/privacy is in review for a visitor");
  const terms = (await (await ask("/terms", { headers: { Cookie: cookie } })).text()).replace(/<[^>]+>/g, " ");
  ok(terms.includes("This site sets no tracking cookies.") && terms.includes("Usage counts and cookies"), "/terms says the site sets no tracking cookies");

  if (recorded) {
    const sent = await ask("/api/usage", { method: "POST", headers: { "Content-Type": "text/plain;charset=UTF-8", Origin: base, Cookie: cookie }, body: JSON.stringify({ event: "tool opened", path: "/privacy" }) });
    const page = await (await ask("/internal/usage", { headers: { Cookie: cookie } })).text();
    const events = Number((page.match(/data-n="events"[^>]*>([\d,]+)</) ?? [])[1]?.replace(/,/g, "") ?? NaN);
    ok(sent.status === 204 && page.includes('data-usage="1"') && events >= 1 && page.includes('data-usage-row="/privacy"'), "--recorded: a count posted for /privacy shows on /internal/usage", `${events} events`);
  }
}

// 4. the routes that spend or write: refused before anything happens (no question is ever sent)
const JSONH = { "Content-Type": "application/json" };
const q = JSON.stringify({ question: "a check that must be refused before a model is asked" });
{
  const cross = await ask("/api/ask", { method: "POST", headers: { ...JSONH, Origin: "https://another-site.example" }, body: q });
  ok(cross.status === 403, "/api/ask: another site's page is refused", `HTTP ${cross.status}`);
  const curl = await ask("/api/ask", { method: "POST", headers: { ...JSONH, "User-Agent": "curl/8.4.0" }, body: q });
  ok(curl.status === 403, "/api/ask: a stock command-line client is refused", `HTTP ${curl.status}`);
  const typed = await ask("/api/ask", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: "question=x" });
  ok(typed.status === 415, "/api/ask: a body that is not JSON is refused", `HTTP ${typed.status}`);
  const big = await ask("/api/ask", { method: "POST", headers: JSONH, body: JSON.stringify({ question: "x", history: "y".repeat(70000) }) });
  ok(big.status === 413, "/api/ask: a body over 60,000 characters is refused", `HTTP ${big.status}`);
  const sub = await ask("/api/subscribe", { method: "POST", headers: { ...FORM, Origin: "https://another-site.example" }, body: form({ email: "nobody@example.com", daily: "on", topic: "power" }) });
  ok(sub.status === 303 && (sub.headers.get("location") ?? "").includes("state=invalid"), "/api/subscribe: another site's form stores and sends nothing", `to ${(sub.headers.get("location") ?? "").split("?")[1]}`);
  for (const p of ["/api/play/finish", "/api/play/score"]) {
    const r = await ask(p, { method: "POST", headers: { ...JSONH, Origin: "https://another-site.example" }, body: "{}" });
    ok(r.status === 403, `${p}: another site's page is refused`, `HTTP ${r.status}`);
  }
  for (const p of ["/api/thesis/run", "/api/analysis", "/api/thesis/provider"]) {
    const r = await ask(p, { method: "POST", headers: JSONH, body: "{}" });
    ok(r.status === 404 && (await r.text()) === "", `${p}: 404 with an empty body without the internal cookie`);
  }
  const conf = await ask(`/api/subscribe/confirm?e=${"a".repeat(300)}%40example.com&t=${"0".repeat(64)}`);
  ok(conf.status === 303 && (conf.headers.get("location") ?? "").includes("state=badlink"), "/api/subscribe/confirm: an address over 254 characters is a bad link");
  ok((await ask("/api/download?table=../../etc")).status === 400 && (await ask("/api/entity?table=subscribers&id=1")).status === 400, "/api/download and /api/entity refuse a name that is not theirs");
}

// 5. /api/usage: always 204, never a cookie
for (const [label, init] of [
  ["a count", { headers: { "Content-Type": "text/plain;charset=UTF-8", Origin: base }, body: JSON.stringify({ event: "tool opened", path: "/terms" }) }],
  ["Do Not Track", { headers: { "Content-Type": "text/plain;charset=UTF-8", DNT: "1" }, body: JSON.stringify({ event: "tool opened", path: "/terms" }) }],
  ["an event it does not know", { headers: JSONH, body: JSON.stringify({ event: "clicked", path: "/terms" }) }],
  ["a path that is not a page", { headers: JSONH, body: JSON.stringify({ event: "download", path: "/not-a-page?x=1" }) }],
  ["another site's page", { headers: { ...JSONH, Origin: "https://another-site.example" }, body: JSON.stringify({ event: "tool opened", path: "/terms" }) }],
  ["not JSON", { headers: JSONH, body: "{" }],
]) {
  const r = await ask("/api/usage", { method: "POST", ...init });
  ok(r.status === 204 && cookiesOf(r).length === 0 && (await r.text()) === "" && (r.headers.get("cache-control") ?? "").includes("no-store"), `/api/usage: ${label} is answered 204, with no body and no cookie`, `HTTP ${r.status}`);
}
ok((await ask("/api/usage")).status === 405, "/api/usage: GET is not a method");

console.log(`${n - bad} of ${n} checks passed`);
process.exit(bad ? 1 : 0);
