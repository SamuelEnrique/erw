// Energy Research Warehouse (ERW) site, session 95: the interconnection queue explorer, on the built site.
//
//   npm run build && npx next start -p 3095
//   node --import ./scripts/alias-loader.mjs scripts/check-queues.mjs [base-url]      (default http://localhost:3095)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   numbers   every number the page marks (data-n) equals the site's copy of interconnection_queue_summary
//             (data/queues.json), for six views
//   charts    a bar per year entered with active capacity; an outcome bar per year with a request; a point per
//             operation year with a median, or the sentence that says there are too few
//   kinds     storage and solar with storage each have their own row, with the copy's figures
//   not held  a view with too few past requests gives no share, and says so; a view the file does not hold says so
//   license   the attribution the license asks for is on the page
//   visitor   without the cookie the page is the in-review page and carries no number
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
import * as q from "../lib/queues.ts";

const base = (process.argv[2] ?? "http://localhost:3095").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/queues.json", import.meta.url), "utf-8"));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1], x[2]]));

async function view(grid, tech) {
  const path = q.href(grid, tech);
  const { status, html } = await get(path);
  const tag = `${path}:`;
  check(status === 200 && !html.includes('data-in-review="1"'), `${tag} opens in the internal view`);
  const got = marked(html), v = q.viewOf(file, grid, tech), w = v.whole;
  const wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, copy ${val}`); };
  const absent = (k) => { if (k in got) wrong.push(`${k}: on the page (${got[k]}), not in the copy`); };
  want("total_active_requests", q.whole(w.total_active_requests));
  want("total_active_mw", q.whole(w.total_active_mw));
  want("past_requests", q.whole(w.past_requests));
  want("head|active_mw", q.whole(w.total_active_mw));
  want("head|active_requests", q.whole(w.total_active_requests));
  want("head|suspended_requests", q.whole(w.total_suspended_requests));
  want("head|suspended_mw", q.whole(w.total_suspended_mw));
  want("head|dated", q.whole(w.years_to_operation_n));
  want("head|operating_requests", q.whole(w.operating_requests));
  want("without_year", q.whole(w.requests_without_year));
  want("total_requests", q.whole(w.total_requests));
  for (const [k, field] of [["past_operating_share_pct", "past_operating_share_pct"], ["past_withdrawn_share_pct", "past_withdrawn_share_pct"], ["median_years_to_operation", "median_years_to_operation"],
    ["head|operating", "past_operating_share_pct"], ["head|withdrawn", "past_withdrawn_share_pct"], ["head|operating_mw", "past_mw_operating_share_pct"], ["head|withdrawn_mw", "past_mw_withdrawn_share_pct"],
    ["head|open", "past_open_share_pct"], ["head|median", "median_years_to_operation"]]) {
    if (w[field] === undefined) absent(k); else want(k, q.two(w[field]));
  }
  for (const t of q.TECHS.filter((x) => x.slug !== "all")) {
    const kv = q.viewOf(file, grid, t.slug);
    if (!kv) { absent(`kind|${t.slug}|total_active_mw`); continue; }
    want(`kind|${t.slug}|total_active_mw`, q.whole(kv.whole.total_active_mw));
    want(`kind|${t.slug}|total_active_requests`, q.whole(kv.whole.total_active_requests));
    for (const f of ["past_operating_share_pct", "past_withdrawn_share_pct", "median_years_to_operation"]) {
      if (kv.whole[f] === undefined) absent(`kind|${t.slug}|${f}`); else want(`kind|${t.slug}|${f}`, q.two(kv.whole[f]));
    }
  }
  check(wrong.length === 0, `${tag} every marked number is the copy's (${Object.keys(got).length} on the page)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const ys = q.yearsOf(v, file.last_year).filter((y) => y.year >= 2000);
  const bars = [...html.matchAll(/data-bar="(\d{4})"/g)].map((x) => Number(x[1]));
  check(bars.join() === ys.filter((y) => (y.row?.mw_active ?? 0) > 0).map((y) => y.year).join(), `${tag} a bar for each year with active capacity (${bars.length})`);
  const outs = [...html.matchAll(/data-outcome="(\d{4})"/g)].map((x) => Number(x[1]));
  check(outs.join() === ys.filter((y) => q.outcome(y.row)).map((y) => y.year).join(), `${tag} an outcome bar for each year with a request (${outs.length})`);
  const on = Object.keys(v.on).map(Number).filter((y) => y >= 2000).sort();
  const pts = [...html.matchAll(/data-on="(\d{4})"/g)].map((x) => Number(x[1]));
  check(on.length >= 2 ? pts.join() === on.join() : html.includes('data-chart="years-none"') && pts.length === 0, `${tag} ${on.length >= 2 ? `a point for each of ${on.length} operation years` : "too few dated years: a sentence, no line"}`);
  const t = text(html);
  check(t.includes("Lawrence Berkeley National Laboratory and GridTracker") && t.includes("CC BY 4.0"), `${tag} the attribution the license asks for`);
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
  return { html, t, w };
}

await view("us", "all");
await view("ercot", "battery");
await view("caiso", "solar_battery");
await view("pjm", "solar");
{
  const { t, w } = await view("isone", "all");
  check(w.median_years_to_operation === undefined && t.includes("The file dates too few of those that were built to give a median wait"), "ISO-NE: no operation date is held, so no median, said in words");
}
{
  const { t, w } = await view("nyiso", "battery");
  check(w.past_operating_share_pct !== undefined || t.includes("too few for a share"), `New York's standalone storage: ${w.past_requests} past requests, ${w.past_operating_share_pct === undefined ? "no share, said in words" : "a share"}`);
}
{
  const small = Object.entries(file.views).find(([, v]) => v.whole.past_requests < file.min_share && v.whole.total_requests > 0);
  if (small) {
    const [grid, tech] = small[0].split("|");
    const { t } = await view(grid, tech);
    check(t.includes("too few for a share") && t.includes(`Fewer than ${file.min_share} requests entered in those years`), `${small[0]}: ${small[1].whole.past_requests} past requests, no share on the page`);
  }
}
{
  const { status, html } = await get(q.href("miso", "offshore_wind"));
  check(status === 200 && html.includes('data-empty="1"') && !html.includes('data-chart="active"'), "a view the file does not hold (offshore wind in MISO): a sentence, no chart");
  const d = await get("/queues?grid=mars&tech=coal");
  check(d.status === 200 && marked(d.html).total_active_requests === q.whole(file.views["us|all"].whole.total_active_requests), "an address it does not understand opens every region, every technology");
}
{
  const { status, html } = await get(q.href("ercot", "battery"), false);
  check(status === 200 && html.includes('data-in-review="1"') && !html.includes("data-n="), "as a visitor: the in-review page, and no number of the tool");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
