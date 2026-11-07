// Energy Research Warehouse (ERW) site, session 3306 (chain 200): the company pages (/companies, /companies/<id>) on a
// served build, read back against their files (site/data/companies/, warehouse/derived/companies_page.py).
//
//   npm run build && npx next start -p 3330
//   node --import ./scripts/alias-register.mjs scripts/check-companies.mjs [base-url]     (default http://localhost:3330)
//
// As HTML, in the internal view (the pages are in review):
//   numbers     every figure the pages mark (data-n, company_directory|<id>|<column> and company_links|<link>|<mw|usd>)
//               equals the file: data-raw is the file's value, and the text is that value as the page writes it. Read on
//               the index (the first page, and three filters) and on twenty company pages: the ten largest by
//               footprint, and ten drawn with a fixed seed (CHECK_COMPANIES_SEED, default 3306)
//   held        no company page carries a row of a held table; each held table it names carries its count
//   downloads   each company page's CSV holds as many rows as the page says, with its provenance first; the readers
//               name the CSV's address
//   visitor     without the cookie a company page is the in-review page and carries no figure
// Exit 1 on a failure, or when fewer than 200 figures were read.
import fs from "node:fs";
import crypto from "node:crypto";
import { env, unlockPost } from "./browser.mjs";
import * as db from "../lib/companydb.ts";

const base = (process.argv[2] ?? "http://localhost:3330").replace(/\/$/, "");
let bad = 0, n = 0, figures = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const dir = new URL("../data/companies/", import.meta.url);
const ix = JSON.parse(fs.readFileSync(new URL("index.json", dir), "utf-8"));
const shard = (id) => JSON.parse(fs.readFileSync(new URL(`c/${crypto.createHash("sha1").update(`company:${id}`).digest("hex").slice(0, 2)}.json`, dir), "utf-8"))[id];
const rows = db.indexRows(ix);

const unlock = await unlockPost(base, env("INTERNAL_COSTS_TOKEN") ?? "");
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const unent = (s) => s.replace(/&amp;/g, "&").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const marks = (html) => [...html.matchAll(/<span[^>]*data-n="([^"]+)"[^>]*data-raw="([^"]*)"[^>]*>([^<]*)</g)].map((x) => ({ key: unent(x[1]), raw: unent(x[2]), text: unent(x[3]) }));

const asWritten = (col, v) => (col.startsWith("n_") ? db.count(v) : db.mw(v));

function readCompanyMarks(page, c) {
  const links = new Map(db.linksOf(c, ix).map((l) => [l.link, l]));
  let ok = 0;
  for (const m of page) {
    const p = m.key.split("|");
    figures += 1;
    if (p[0] === "company_directory") {
      const col = p[2];
      const want = col.startsWith("mw_") ? c.fuel[col.slice(3)] : c.figures[col];
      if (p[1] !== c.entity_id || want === undefined || Number(m.raw) !== Number(want) || m.text !== asWritten(col, Number(want))) {
        check(false, `${c.id}: ${m.key} reads ${m.raw} (${m.text}), the file ${want}`); continue;
      }
    } else if (p[0] === "company_links") {
      const l = links.get(p[1]);
      const want = l ? l[p[2]] : undefined;
      const shown = p[2] === "mw" ? Number(want).toLocaleString("en-US", { maximumFractionDigits: 1 }) : Number(want).toLocaleString("en-US");
      if (!l || m.raw !== want || m.text !== shown) { check(false, `${c.id}: ${m.key} reads ${m.raw} (${m.text}), the file ${want}`); continue; }
    } else { check(false, `${c.id}: an unknown key ${m.key}`); continue; }
    ok += 1;
  }
  return ok;
}

// the index
for (const q of ["", "?kind=utility", "?state=TX&has=queue", "?q=energy&grid=PJM&page=2"]) {
  const r = await get(`/companies${q}`);
  check(r.status === 200, `/companies${q} answers 200 (${r.status})`);
  const ms = marks(r.html);
  const byId = new Map(rows.map((x) => [x.id, x]));
  let good = 0;
  for (const m of ms) {
    figures += 1;
    const [, id, col] = m.key.split("|");
    const row = byId.get(id.replace(/^company:/, ""));
    const want = row ? row[col] : undefined;
    if (want === undefined || Number(m.raw) !== Number(want) || m.text !== asWritten(col, Number(want))) check(false, `/companies${q}: ${m.key} reads ${m.raw} (${m.text}), the file ${want}`);
    else good += 1;
  }
  const query = db.queryOf(Object.fromEntries(new URLSearchParams(q.slice(1))), ix);
  const kept = db.filterRows(rows, query);
  check(r.html.includes(`data-companies-count="${kept.length}"`), `/companies${q}: the count is ${kept.length}`);
  check(good === ms.length && (kept.length === 0 || ms.length > 0), `/companies${q}: ${good} of ${ms.length} figures equal the file`);
}

// twenty company pages
let seed = Number(process.env.CHECK_COMPANIES_SEED ?? 3306);
const rand = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
const picks = rows.slice(0, 10).map((r) => r.id);
while (picks.length < 20) { const id = rows[Math.floor(rand() * rows.length)].id; if (!picks.includes(id)) picks.push(id); }
for (const id of picks) {
  const c = shard(id);
  const r = await get(`/companies/${id}`);
  check(r.status === 200, `/companies/${id} answers 200 (${r.status})`);
  const ms = marks(r.html);
  const good = readCompanyMarks(ms, c);
  // a company with no figure (a small utility with EIA-861 rows alone: no MW, no count) carries no keyed figure
  const hasFigure = ["plants_mw", "planned_mw", "owned_mw", "queue_mw", "n_reactors", "n_policy_actions"].some((k) => c.figures[k] > 0)
    || c.links.some((l) => l[6] !== "" || l[7] !== "");
  check(good === ms.length && (ms.length > 0) === hasFigure, `/companies/${id}: ${good} of ${ms.length} figures equal the file${hasFigure ? "" : " (it has none)"}`);
  for (const t of ix.held_tables) {
    check(!r.html.includes(`data-rows-table="${t}"`), `/companies/${id}: no row of the held ${t}`);
    if (c.held[t]) check(r.html.includes(`data-held-table="${t}"`), `/companies/${id}: the held ${t} is counted (${c.held[t]})`);
  }
  const csv = await get(`/companies/${id}/rows`);
  const lines = csv.html.split("\n").filter((l) => l && !l.startsWith("#"));
  check(csv.status === 200 && csv.html.startsWith("# Energy Research Warehouse (ERW)") && lines.length - 1 === c.links.length, `/companies/${id}/rows: ${lines.length - 1} rows, the file ${c.links.length}`);
  for (const as of ["python", "stata"]) {
    const rd = await get(`/companies/${id}/rows/${as}`);
    check(rd.status === 200 && rd.html.includes(`/companies/${id}/rows`), `/companies/${id}/rows/${as} names its CSV`);
  }
}

// the visitor
const v = await get(`/companies/${picks[0]}`, false);
check(!v.html.includes("data-n="), `without the cookie /companies/${picks[0]} carries no figure`);

check(figures >= 200, `${figures} figures read (at least 200)`);
console.log(bad ? `FAILED: ${bad} of ${n} checks` : `${n} of ${n} checks passed; ${figures} figures read`);
process.exit(bad ? 1 : 0);
