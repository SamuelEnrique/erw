// Energy Research Warehouse (ERW) site, session 130: the deals tracker, version 3, on the built site.
//
//   npm run build && npx next start -p 3130
//   node --import ./scripts/alias-loader.mjs scripts/check-deals-v3.mjs [base-url]      (default http://localhost:3130)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   counts     the headline counts and the counts of the callout equal the library's, computed here from the site's
//              copy of power_deals (data/deals_v3.json)
//   rows       a row for each deal of the copy, and for each of the selections tried
//   numbers    every number shown opens a story (a link beside it), and as many numbers are shown as the copy holds
//   compare    the three tables against version 2 carry the build's counts
//   no text    no sentence of the internal table is in the page (the copy holds none)
//   visitor    without the cookie the page is the in-review page and carries no deal
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
import * as g from "../lib/deals3.ts";

const base = (process.argv[2] ?? "http://localhost:3130").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/deals_v3.json", import.meta.url), "utf-8"));
const all = file.deals.map(g.toDeal), S = file.summary;
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exitCode = 1; }
else {
  const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
  const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
  const marked = (html, attr) => Object.fromEntries([...html.matchAll(new RegExp(`<span ${attr}="([^"]+)">([^<]*)</span>`, "g"))].map((x) => [x[1], x[2]]));
  const { status, html } = await get("/deals/v3");
  check(status === 200 && !html.includes('data-in-review="1"'), "/deals/v3 opens in the internal view");
  const c = g.counts(all), w = g.whole;
  const head = marked(html, "data-deals"), call = marked(html, "data-all");
  check(head.count === w(c.deals) && head.size === w(c.size) && head.price === w(c.price) && head.term === w(c.term) && head.with_dollars === w(c.withDollars) && (!c.withMw || (head.mw === w(c.mw) && head.with_mw === w(c.withMw))),
    `the headline counts are the copy's (${c.deals} deals, ${c.size} state a size, ${c.price} a price, ${c.term} a term)`);
  check(call.deals === w(c.deals) && call.size === w(c.size) && call.price === w(c.price) && call.term === w(c.term) && call.dollars === w(c.withDollars), "the callout's counts are the copy's");
  const rows = (h) => [...h.matchAll(/data-deal="([^"]+)"/g)].map((x) => x[1]);
  check(rows(html).length === all.length && new Set(rows(html)).size === all.length, `${rows(html).length} rows, ${all.length} deals in the copy`);
  const held = all.reduce((k, d) => k + [d.mw, d.mwh, d.term, d.dollars, d.price].filter(Boolean).length, 0);
  const shown = [...html.matchAll(/<span data-number="[a-z]+">[\s\S]*?<\/span>/g)].map((x) => x[0]);
  check(shown.length === held && held === S.numbers_checked, `${shown.length} numbers shown; the copy holds ${held}, the build checked ${S.numbers_checked}`);
  check(shown.every((x) => /<a href="https?:\/\/[^"]+"[^>]*>story<\/a>/.test(x)), "every number shown opens the story it was read from");
  const t = text(html);
  check(t.includes(g.summary(all, all, g.inputsOf({}, all))), "the sentence under the title is the library's");
  let tables = 0;
  for (const [k, list] of Object.entries(S.compare)) {
    const m = html.match(new RegExp(`data-compare="${k}"[\\s\\S]*?</table>`));
    const cells = m ? [...m[0].matchAll(/data-c="([a-z]+)">([\d,]+)/g)].map((x) => x[2]) : [];
    const want = list.flatMap((r) => [r.deals, r.size, r.price, r.term, r.dollars].map(w));
    if (m && cells.join("|") === want.join("|")) tables += 1; else console.log(`     compare ${k}: page ${cells.join(" ")}, build ${want.join(" ")}`);
  }
  check(tables === 3, "the three tables against version 2 carry the build's counts");
  for (const q of [{ view: "storage" }, { view: "datacenter" }, { kind: "power_purchase" }, { states: "size" }, { states: "term", view: "datacenter" }, { tech: "nuclear", year: "2026" }, { party: "Google" }]) {
    const x = g.inputsOf(q, all), want = g.select(all, x);
    const r = await get(g.hrefOf(x));
    check(r.status === 200 && rows(r.html).join("|") === want.map((d) => d.id).join("|") && marked(r.html, "data-deals").count === w(want.length), `${g.hrefOf(x)}: ${want.length} deals, the library's selection in its order`);
  }
  const none = await get("/deals/v3?kind=tolling&tech=coal");
  check(none.status === 200 && rows(none.html).length === 0 && text(none.html).includes("No power deal held matches this selection"), "a selection with no deal says so");
  check(!/"sentence"|data-sentence/.test(html) && !JSON.stringify(file).includes('"sentence"'), "no sentence of the internal table is in the page or its copy");
  check(!/\bundefined\b|NaN/.test(t), 'no "undefined" and no NaN in the text');
  const v = await get("/deals/v3", false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-deal="), "as a visitor: the in-review page, and no deal");
  const m = await get("/data/methods/power_deals");
  check(m.status === 200 && text(m.html).includes("no number without its sentence".replace("no", "The rule: no")), "the method note opens in the internal view");
  console.log(`${n - bad} of ${n} checks pass`);
  process.exitCode = bad ? 1 : 0;
}
