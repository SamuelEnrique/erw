// Energy Research Warehouse (ERW) site, session 96: where power is cheap, on the built site.
//
//   npm run build && npx next start -p 3096
//   node --import ./scripts/alias-loader.mjs scripts/check-prices-compare.mjs [base-url]      (default http://localhost:3096)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   numbers   every number the page marks (data-n) equals the site's copy of hub_price_comparison
//             (data/price_compare.json), for both periods and both markets
//   order     the table and the chart are in the order asked for, a hub that lacks the measure last
//   sortable  each heading is a link that sorts by its column, and the one sorted by turns the order round
//   not held  a hub that lacks the market is named under the table with no number
//   hidden    MISO's hubs are named "held, not shown: license needed" with no number anywhere; PJM is "not held"
//   a hub is not a site   the sentence is on the page
//   visitor   without the cookie the page is the in-review page and carries no number
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
import * as p from "../lib/pricecompare.ts";

const base = (process.argv[2] ?? "http://localhost:3096").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/price_compare.json", import.meta.url), "utf-8"));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1].replace(/&amp;/g, "&"), x[2]]));

async function view(q) {
  const c = p.choices(q);
  const path = p.href({ period: c.period, market: c.market, sort: c.sort.slug, dir: q.dir });
  const { status, html } = await get(path);
  const tag = `${path}:`;
  check(status === 200 && !html.includes('data-in-review="1"'), `${tag} opens in the internal view`);
  const got = marked(html), rows = p.ordered(file[c.period], c);
  const wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, copy ${val}`); };
  for (const r of rows) {
    for (const m of p.MEASURES) {
      const v = p.valueOf(r, c.market, m);
      if (v === undefined) { if (`${r.entity}|${m.slug}` in got) wrong.push(`${r.entity}|${m.slug}: on the page, not in the copy`); } else want(`${r.entity}|${m.slug}`, p.two(v));
    }
    want(`${r.entity}|hours`, r[`${c.market}_hours_held`].toLocaleString("en-US"));
  }
  want("count", String(rows.length));
  const first = (slug, dir) => p.ordered(file[c.period], { ...c, sort: p.MEASURES.find((m) => m.slug === slug), dir })[0];
  want("sum|cheapest", p.two(p.valueOf(first("avg", "asc"), c.market, p.MEASURES[0])));
  want("sum|dearest", p.two(p.valueOf(first("avg", "desc"), c.market, p.MEASURES[0])));
  want("head|spread", p.two(p.valueOf(first("spread", "desc"), c.market, p.MEASURES[3])));
  want("head|negative", p.two(p.valueOf(first("neg", "desc"), c.market, p.MEASURES[1])));
  check(wrong.length === 0, `${tag} every marked number is the copy's (${Object.keys(got).length} on the page)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const bars = [...html.matchAll(/data-bar="([^"]+)"/g)].map((x) => x[1].replace(/&amp;/g, "&"));
  check(bars.join("|") === rows.map((r) => r.entity).join("|"), `${tag} ${bars.length} bars, in the order of ${c.sort.slug}, ${c.dir}`);
  const inTable = [...html.matchAll(/<span data-n="([^"|]+)\|avg">/g)].map((x) => x[1]);
  check(inTable.join("|") === rows.map((r) => r.entity).join("|"), `${tag} the table's rows in the same order`);
  const heads = [...html.matchAll(/<a [^>]*data-sort="([a-z]+)"[^>]*href="([^"]+)"/g)].map((x) => [x[1], x[2].replace(/&amp;/g, "&")]);
  const own = heads.find(([s]) => s === c.sort.slug);
  check(heads.length === p.MEASURES.length && heads.every(([s, h]) => h.includes(`sort=${s}`)) && own && own[1].includes(`dir=${c.dir === "asc" ? "desc" : "asc"}`),
    `${tag} five headings that sort, and the one sorted by turns the order round`);
  const t = text(html);
  const none = p.lacking(file[c.period], c.market);
  check(none.every((r) => t.includes(p.label(r))) && (none.length === 0) === !html.includes("data-lacking="), `${tag} ${none.length} hub${none.length === 1 ? "" : "s"} not held for this market, named with no number`);
  check(html.includes('data-not-a-site="1"') && t.includes("A hub is not a site."), `${tag} "a hub is not a site"`);
  check(file.held_not_shown.every((h) => html.includes(`data-hidden="${h.entity}"`)) && !Object.keys(got).some((k) => k.startsWith("miso:")) && !bars.some((b) => b.startsWith("miso:")),
    `${tag} MISO's ${file.held_not_shown.length} hubs: held, not shown, and no number of theirs anywhere`);
  check(html.includes('data-not-held="PJM"'), `${tag} PJM: not held, said so`);
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
  return { html, t, rows };
}

await view({});
await view({ period: "year", market: "rtm", sort: "neg" });
await view({ period: "month", market: "dam", sort: "spread" });
await view({ period: "month", market: "rtm", sort: "avg", dir: "desc" });
{
  const { html, rows } = await view({ period: "year", market: "dam", sort: "carbon" });
  check(html.includes('data-no-carbon="SPP"') && rows.at(-1).grid === "SPP", "SPP's carbon intensity over twelve months is not held (236 of 365 days): said so, and its hub sorts last");
}
{
  const d = await get("/prices/compare?period=decade&market=spot&sort=luck");
  check(d.status === 200 && marked(d.html).count === String(p.ordered(file.year, p.choices({})).length), "an address it does not understand opens the default view");
  const v = await get(p.href({ period: "month", market: "dam", sort: "avg" }), false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-n="), "as a visitor: the in-review page, and no number of the tool");
  const node = await get("/prices/ercot%3AHB_HUBAVG");
  check(node.status === 200 && !node.html.includes('data-not-a-site="1"'), "/prices/<hub> is still the hub's own page, not this one");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
