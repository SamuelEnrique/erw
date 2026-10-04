// Energy Research Warehouse (ERW) site, session 99: the largest buyers and sellers on /contracts, on the built site,
// against a stand-in for the database. The contract table is internal: its figures are in no file of this repository
// and, until a load after session 99, not in the stored summary either. So this check serves the summary itself, from
// a file made on the data machine and kept out of git, and the site reads it as it would read the database.
//
//   python warehouse/supabase/eqr_fixture.py runs/session99/summary.json     (the summary the loader would store)
//   npm run build
//   SUPABASE_URL=http://127.0.0.1:39990 SUPABASE_ANON_KEY=stand-in npx next start -p 3099
//   node --import ./scripts/alias-loader.mjs scripts/check-contracts-largest.mjs ../runs/session99/summary.json [base-url] [stand-in port]
//
//   numbers    every figure of the view (data-n) equals the summary's, for energy, capacity and tolling; the names in
//              the summary's order
//   views      the page has two views; the first is the page as it was (by the quarter signed) and reads no largest
//   not loaded with a summary stored before this view existed, the view says so and shows no table
//   visitor    without the cookie the page is the in-review page: no name and no number of the table
// Exit 1 on a failure.
import fs from "node:fs";
import http from "node:http";
import { env } from "./browser.mjs";
import * as c from "../lib/contracts.ts";

const fixture = process.argv[2];
const base = (process.argv[3] ?? "http://localhost:3099").replace(/\/$/, "");
const port = Number(process.argv[4] ?? 39990);
if (!fixture || !fs.existsSync(fixture)) { console.log(`FAILED: no summary file (${fixture}); make it with warehouse/supabase/eqr_fixture.py`); process.exit(1); }
const summary = JSON.parse(fs.readFileSync(fixture, "utf-8"));
let bad = 0, n = 0, withLargest = true, asked = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };

// the stand-in: the two internal functions answer as the database would with the internal token; every other read is empty
const server = http.createServer((req, res) => {
  let body = "";
  req.on("data", (d) => { body += d; });
  req.on("end", () => {
    res.setHeader("Content-Type", "application/json");
    if (req.url.startsWith("/rest/v1/rpc/internal_eqr_summary")) {
      asked += 1;
      const { largest, ...rest } = summary;
      res.end(JSON.stringify(withLargest ? summary : rest));
    } else if (req.url.startsWith("/rest/v1/rpc/internal_eqr_contracts")) res.end("[]");
    else res.end("[]");
  });
});
await new Promise((r) => server.listen(port, "127.0.0.1", r));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((x) => x.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie`); server.close(); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const unescape = (s) => s.replace(/&amp;/g, "&").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [unescape(x[1]), x[2]]));
const parties = (html) => Object.fromEntries([...html.matchAll(/<span [^>]*data-party="([^"]+)">([^<]*)<\/span>/g)].map((x) => [unescape(x[1]), unescape(x[2])]));
const count = (v) => v.toLocaleString("en-US");

const L = summary.largest;
check(!!L && c.LARGEST_PRODUCTS.every((p) => L.lists.buyer[p.slug] && L.lists.seller[p.slug]), "the summary holds the largest buyers and sellers of the three products");
for (const p of c.LARGEST_PRODUCTS) {
  const path = c.largestHref(p.slug);
  const { status, html } = await get(path);
  const tag = `${path}:`;
  check(status === 200 && html.includes('data-largest="1"') && html.includes('data-view="largest"'), `${tag} the view opens in the internal view`);
  const got = marked(html), names = parties(html), wrong = [];
  const want = (k, v) => { if (got[k] !== v) wrong.push(`${k}: page ${got[k]}, summary ${v}`); };
  const buyers = L.lists.buyer[p.slug], sellers = L.lists.seller[p.slug];
  want("contracts", count(buyers.contracts));
  want("buyers", count(buyers.parties));
  want("sellers", count(sellers.parties));
  want("top|buyer", count(buyers.top[0].contracts));
  want("top|seller", count(sellers.top[0].contracts));
  want("names|filed", count(L.names.filed));
  want("names|after", count(L.names.after_rules));
  want("names|merged", count(L.names.merged_names));
  want("names|doubtful", count(L.names.doubtful_pairs));
  for (const [role, list] of [["buyer", buyers], ["seller", sellers]]) {
    for (const r of list.top) {
      want(`${role}|${r.rank}|contracts`, count(r.contracts));
      want(`${role}|${r.rank}|rows`, count(r.rows));
      want(`${role}|${r.rank}|counterparties`, count(r.counterparties));
      want(`${role}|${r.rank}|rows_with_mw`, count(r.rows_with_mw));
      if (r.rows_with_mw > 0) want(`${role}|${r.rank}|mw`, r.mw_filed.toLocaleString("en-US", { maximumFractionDigits: 1 }));
      if (names[`${role}|${r.rank}`] !== r.name) wrong.push(`${role} ${r.rank}: page ${names[`${role}|${r.rank}`]}, summary ${r.name}`);
    }
  }
  check(wrong.length === 0, `${tag} every figure and every name is the summary's (${Object.keys(got).length} figures, ${Object.keys(names).length} names)${wrong.length ? `: ${wrong.slice(0, 4).join("; ")}` : ""}`);
  const ranks = buyers.top.map((r) => r.contracts);
  check(ranks.every((v, i) => i === 0 || v <= ranks[i - 1]) && Object.keys(names).length === buyers.top.length + sellers.top.length, `${tag} ${buyers.top.length} buyers and ${sellers.top.length} sellers, most contracts first`);
  check(html.includes("By rule, never by a guess") && html.includes("ferc_eqr_buyer_doubtful") && html.includes("By contracts, not by megawatts"), `${tag} how the names are brought together, the doubtful pairs, and what the ranking is not`);
}
{
  const { status, html } = await get("/contracts");
  check(status === 200 && html.includes('data-view="quarter"') && !html.includes('data-largest="1"') && html.includes("The largest buyers and sellers"), "/contracts opens on the view by the quarter signed, with a link to the other");
  const d = await get("/contracts?view=nonsense&product=steam");
  check(d.status === 200 && d.html.includes('data-view="quarter"'), "a view it does not understand opens the first");
}
{
  withLargest = false;
  const { status, html } = await get(c.largestHref("energy"));
  check(status === 200 && html.includes('data-largest="unavailable"') && !html.includes("data-party="), "with a summary stored before this view existed: it says the view is not loaded, and shows no table");
  withLargest = true;
}
{
  const { status, html } = await get(c.largestHref("energy"), false);
  const first = L.lists.buyer.energy.top[0].name;
  check(status === 200 && html.includes('data-in-review="1"') && !html.includes("data-party=") && !unescape(html).includes(first), "as a visitor: the in-review page, with no name and no figure of the table");
}
check(asked >= 5, `the site read the stand-in (${asked} reads of the summary), not the database`);
server.close();
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
