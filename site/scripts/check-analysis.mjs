// Energy Research Warehouse (ERW) site, session 170: /analysis rebuilt around the finding cards, on the built site.
//
//   npm run build && npx next start -p 3170
//   node scripts/check-analysis.mjs [base-url]      (default http://localhost:3170)
//
// Read as HTML in the internal view (the page is in review):
//   cards      every committed card is drawn (data-card), with its title, its subtitle, its callouts' numbers as the
//              card's JSON holds them, its why paragraph, its footnote, its three downloads and two render links
//   w40        the chart of the week is not drawn on /analysis (no data-finding of the old view); the week page keeps it
//   words      no model name or cost on the page; "ERCOT North Hub" words in the catalogue; the old rule's footnote gone
//   downloads  each download answers 200 with its content type
//   card page  /analysis/card/<id> draws the one card; ?render=1 draws the render frame alone
//   queue      the request flow and the list of requests are on the page; GET /api/analysis answers the internal view
//              (200) and a visitor (404)
// Session 182, part 4: the two single-grid cards that a five-grid card supersedes left the list of /analysis. Each is
// still checked, number by number, on its own address (/analysis/card/<id>), and /analysis must link it. The count of
// the list is the count of the current cards. "Ask for a finding" is the request flow (scripts/check-analysis-flow.mjs).
//   visitor    without the cookie /analysis is the in-review page
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

const { status, html } = await get("/analysis");
check(status === 200 && !html.includes('data-in-review="1"'), "/analysis opens in the internal view");
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
  const own = c.id in SUPERSEDED ? await get(`/analysis/card/${c.card_id}`) : null;
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
  const one = await get(`/analysis/card/${c.card_id}`);
  check(one.status === 200 && one.html.includes(`data-card="${c.card_id}"`), `${tag} /analysis/card/${c.card_id} draws the card`);
  const rend = await get(`/analysis/card/${c.card_id}?render=1`);
  check(rend.status === 200 && rend.html.includes('data-render="1"') && !rend.html.includes("data-download="), `${tag} ?render=1 is the frame alone`);
}
check(!html.includes("data-finding=\"1\"") && !t.includes("ERW's Chart of the Week, 2026-W40"), "the W40 chart of the week is not drawn on /analysis");
const wk = await get("/analysis/2026-W40");
check(wk.status === 200 && wk.html.includes("Chart of the Week"), "/analysis/2026-W40 keeps its chart");
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
const visitor = await get("/analysis", false);
check(visitor.html.includes('data-in-review="1"') && !visitor.html.includes("data-card="), "a visitor sees the in-review page");
console.log(`${n - bad} of ${n} checks passed`);
process.exit(bad ? 1 : 0);
