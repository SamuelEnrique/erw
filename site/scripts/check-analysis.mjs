// Energy Research Warehouse (ERW) site, session 170: /research rebuilt around the finding cards, on the built site.
//
//   npm run build && npx next start -p 3170
//   node scripts/check-analysis.mjs [base-url]      (default http://localhost:3170)
//
// Read as HTML in the internal view (the page is in review):
//   cards      every committed card is drawn (data-card), with its title, its subtitle, its callouts' numbers as the
//              card's JSON holds them, its why paragraph, its footnote, its three downloads and two render links
//   w40        the chart of the week is not drawn on /research (no data-finding of the old view); the week page keeps it
//   words      no model name or cost on the page; "ERCOT North Hub" words in the catalogue; the old rule's footnote gone
//   downloads  each download answers 200 with its content type
//   card page  /research/card/<id> draws the one card; ?render=1 draws the render frame alone
//   queue      the request flow and the list of requests are on the page; GET /api/analysis answers the internal view
//              (200) and a visitor (404)
// Session 182, part 4: the two single-grid cards that a five-grid card supersedes left the list of /research. Each is
// still checked, number by number, on its own address (/research/card/<id>), and /research must link it. The count of
// the list is the count of the current cards. "Ask for a finding" is the request flow (scripts/check-analysis-flow.mjs).
//   visitor    without the cookie /research is the in-review page
// Exit 1 on a failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3170").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const dir = path.join(here, "..", "data", "findings");
const cards = fs.readdirSync(dir).filter((f) => f.endsWith(".json") && f !== "catalogue.json").map((f) => JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8")));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (p, withCookie = true) => { const r = await fetch(base + p, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text(), type: r.headers.get("content-type") ?? "" }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/'/g, "&#x27;").replace(/"/g, "&quot;");

const { status, html } = await get("/research");
check(status === 200 && !html.includes('data-in-review="1"'), "/research opens in the internal view");
const t = text(html);
check(cards.length >= 3, `${cards.length} committed cards (3 expected at least)`);
const SUPERSEDED = { batteries_lunch: "batteries_lunch_grids", peak_hour_moved: "peak_hour_grids" };   // lib/findings.ts
const current = cards.filter((c) => !(c.id in SUPERSEDED));
check(fs.readFileSync(path.join(here, "..", "lib", "findings.ts"), "utf-8").includes('SUPERSEDED: Record<string, string> = { batteries_lunch: "batteries_lunch_grids", peak_hour_moved: "peak_hour_grids" }'), "the superseded cards are the two lib/findings.ts names");
check(cards.length - current.length === 2, `${cards.length - current.length} superseded cards among the ${cards.length} committed`);
check(html.includes(`data-finding-cards="${current.length}"`), `the page draws the ${current.length} current cards`);
const listHtml = html, listText = t;
for (const c of cards) {
  const tag = `${c.card_id}:`;
  // a superseded card is read where it now stands, its own address; every check below is the same for it
  const own = c.id in SUPERSEDED ? await get(`/research/card/${c.card_id}`) : null;
  const html = own ? own.html : listHtml;
  const t = own ? text(own.html) : listText;
  // the link itself is drawn by the browser in the internal view (SiteLink), so its href is proven by check-analysis-flow.mjs; here, the line and the title
  const at = listHtml.indexOf(`data-superseded="${c.card_id}"`);
  if (own) check(at > 0 && listHtml.slice(at, at + 500).includes(esc(c.title)) && !listHtml.includes(`data-card="${c.card_id}"`), `${tag} left the list, and is named there under its five-grid card`);
  check(html.includes(`data-card="${c.card_id}"`), `${tag} drawn${own ? " at its own address" : ""}`);
  check(t.includes(c.title), `${tag} title ${JSON.stringify(c.title)}`);
  check(t.includes(c.subtitle.replace(/\s+/g, " ")), `${tag} subtitle`);
  c.callouts.forEach((co, i) => {
    check(html.includes(`data-callout-before="${i}">${esc(co.before.text)}<`), `${tag} callout ${i} before ${co.before.text}`);
    check(html.includes(`data-callout-after="${i}">${esc(co.after.text)}<`), `${tag} callout ${i} after ${co.after.text}`);
  });
  check(t.includes(c.why.replace(/\s+/g, " ")), `${tag} why paragraph`);
  check(t.includes(c.footnote.replace(/\s+/g, " ").slice(0, 120)), `${tag} footnote`);
  for (const [k, f] of Object.entries(c.downloads)) {
    check(html.includes(`href="/findings/${f}"`), `${tag} download ${k} linked`);
    const r = await get(`/findings/${f}`);
    check(r.status === 200 && r.html.length > 100, `${tag} download ${k} answers 200 (${r.type})`);
  }
  check(html.includes(`${c.card_id}_1080x1350.png`) && html.includes(`${c.card_id}_1600x900.png`), `${tag} render links 1080 x 1350 and 1600 x 900`);
  check(html.includes(`data-roundup-button="${c.card_id}"`), `${tag} Use in Roundup`);
  if (c.kind === "econometric") check(html.includes('data-effect-table="1"'), `${tag} effect table`);
  if (c.placeholders) for (const p of c.placeholders) check(html.includes(`data-placeholder="${p.grid}"`) && t.includes(p.text), `${tag} placeholder ${p.words}: ${p.text}`);
  const one = await get(`/research/card/${c.card_id}`);
  check(one.status === 200 && one.html.includes(`data-card="${c.card_id}"`), `${tag} /research/card/${c.card_id} draws the card`);
  const rend = await get(`/research/card/${c.card_id}?render=1`);
  check(rend.status === 200 && rend.html.includes('data-render="1"') && !rend.html.includes("data-download="), `${tag} ?render=1 is the frame alone`);
}
// session 238: the page now draws this week's chart (the newest Roundup's), so "no chart of the week on the page" became
// "the chart of the week on the page is the newest Roundup's, never W40's" (the chart the code disowned in session 170)
const weekShown = (html.match(/data-week-chart="([^"]+)"/) ?? [])[1] ?? "";
check(/^\d{4}-W\d{2}$/.test(weekShown) && weekShown > "2026-W40" && !t.includes("ERW's Chart of the Week, 2026-W40"), `the W40 chart of the week is not drawn on /research (this week's chart is ${weekShown || "none"})`);
// session 238: the page's order, the owner's: the request form, today's chart, this week's chart, the library, the archive
const order = ['id="ask"', 'id="today"', 'id="week"', 'id="library"', 'id="archive"'].map((s) => html.indexOf(s));
check(order.every((v, i) => v > 0 && (i === 0 || v > order[i - 1])), `the page's order: the request form, today's chart, this week's chart, the library, the archive (${order.join(", ")})`);
check(html.includes('data-brand="a"') && html.includes('data-chart-tokens="1"'), "the page carries the brand, and its charts are drawn in the tokens");
check(/data-today-chart="\d{4}-\d{2}-\d{2}"/.test(html) && html.includes('data-today-fact="1"') && html.includes('data-today-source="1"'), "today's chart has its date, its one fact and its source line");
check(html.includes('data-library="1"') && /data-library-index="\d+"/.test(html) && html.includes('data-library-filter="grid"') && html.includes('data-library-filter="topic"'), "the library has its card index and its two filters");
for (const c of current) {
  check(html.includes(`id="card-${c.card_id}"`) && html.includes(`data-library-link="${c.card_id}"`) && new RegExp(`data-library-card="${c.card_id}" data-grids="[a-z ]+" data-topics="[a-z -]+"`).test(html), `${c.card_id}: a screen of its own, in the index, filed under a grid and a topic`);
}
check(!html.includes("data-not-held="), "no file of a card is missing: none is named not held");
check(/data-archive-daily="\d+"/.test(html) && /data-archive-weekly="\d+"/.test(html) && html.indexOf("data-archive-daily") > html.indexOf('id="archive"'), "the archive lists the daily and the weekly charts");
// session 238: the old address answers with the new page
const old = await fetch(`${base}/analysis`, { redirect: "manual" });
check(old.status === 308 && (old.headers.get("location") ?? "").endsWith("/research"), `/analysis redirects to /research (${old.status} ${old.headers.get("location")})`);
const oldCard = await fetch(`${base}/analysis/card/gas_sets_price?form=lines`, { redirect: "manual" });
check(oldCard.status === 308 && (oldCard.headers.get("location") ?? "").endsWith("/research/card/gas_sets_price?form=lines"), `/analysis/card/<id> redirects to /research/card/<id>, its query kept (${oldCard.status} ${oldCard.headers.get("location")})`);
const oldWeek = await fetch(`${base}/analysis/2026-W40`, { redirect: "manual" });
check(oldWeek.status === 308 && (oldWeek.headers.get("location") ?? "").endsWith("/research/2026-W40"), `/analysis/<week> redirects to /research/<week> (${oldWeek.status} ${oldWeek.headers.get("location")})`);
const wk = await get("/research/2026-W40");
check(wk.status === 200 && wk.html.includes("Chart of the Week"), "/research/2026-W40 keeps its chart");
check(!/claude-[a-z]+-\d/.test(t) && !/USD 0\.\d{4}/.test(t), "no model name or cost on the page");
check(!t.includes("robust z = |value minus the median"), "the old rule's footnote is gone");
check(t.includes("ranked among the same measure"), "the current rule is stated");
check(html.includes('data-flow="1"') && html.includes('data-flow-items="18"') && html.includes('data-request-form="1"') && html.includes('data-request-list="1"'), "the request flow (18 entries) and the list of requests are on the page");
check(html.includes('data-form-picker="1"') && html.includes("Default for this analysis"), "step two's picker is on the page, its preselected form labeled the default");
check(!t.includes("Template gallery") && !html.includes("data-request-finding"), "the template gallery and the old form are gone from the page");
check(t.includes("ERCOT North Hub"), "human labels (ERCOT North Hub) are on the page");
const api = await fetch(`${base}/api/analysis`, { headers: { Cookie: cookie } });
check(api.status === 200 || api.status === 502, `GET /api/analysis answers the internal view (${api.status}; 502 when the migration is not applied)`);
const apiVisitor = await fetch(`${base}/api/analysis`);
check(apiVisitor.status === 404, `GET /api/analysis is 404 for a visitor (${apiVisitor.status})`);
const visitor = await get("/research", false);
check(visitor.html.includes('data-in-review="1"') && !visitor.html.includes("data-card="), "a visitor sees the in-review page");
console.log(`${n - bad} of ${n} checks passed`);
process.exit(bad ? 1 : 0);
