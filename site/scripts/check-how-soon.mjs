// Energy Research Warehouse (ERW) site, session 163: "How long a large load waits", in the section "How soon" of "What a
// datacenter pays" (/cost-of-power, in review), on the built site.
//
//   npm run build && npx next start -p 3163
//   node scripts/check-how-soon.mjs [base-url]      (default http://localhost:3163)
//
// As HTML, in the internal view (the page is in review), against data/datacenter/how_soon.json and lib/howsoon.ts:
//   new york   the block is measured: every stage of the file is a row with the count of requests behind it and the
//              words of lib/howsoon.ts; every figure of requests still waiting carries the mark "lower bound"; NYISO's
//              own stated figures stand beside their stage, each a link to the file's address with the document, its
//              day and page on hover; the hover of a measured figure names the copies read and their days; the summary
//              sentence is the library's, and every number in it is a number of the file
//   texas      "not measured here" with the reason on hover (the reports read, how many name a request), and what
//              Texas's own entities measured and stated, each labeled whose figure it is, each a link with its hover
//   others     CAISO, ISO-NE, SPP and PJM read "not measured yet" with a hover and show no stage; MISO reads "paused
//              while terms are reviewed" and shows nothing else
//   beneath    the block "Rules in motion" (session 154, data-rules) stands after it, in the same section
//   kept       everything the section showed before is still there (the interconnection queue's three rows, ERCOT's
//              large load approved to energize, the load in line by region, the row "How long a new large load waits")
//   internal   nothing of a request is on the page: no request-level field name, no megawatt in the block; and, where
//              the internal table large_load_waits is on the machine (../warehouse/output or ERW_TABLES_DIR), no
//              request's name from it anywhere in the page
//   face       no method prose on the block's face, no "undefined", no NaN
// In a real browser: the block is in the page as the browser holds it, each figure's hover is its element's title, a
// stated figure's link takes the keyboard's focus, the rules block is beneath, and the page makes no request for a raw
// table (no address that names large_load_waits, large_load_statements, a .csv or the aggregates file itself).
// Exit 1 on a failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env, withBrowser } from "./browser.mjs";
import { LOWER, NOT_HERE, NOT_YET, PAUSED_WHY, PAUSED_WORDS, blockOf, dayWords, fileOf, measuredTip, measuredWords, notHereWhy, notYetWhy, num, sentenceOf, statedOf, statedTip, basisWords, waitingWords } from "../lib/howsoon.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3163").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const dir = path.join(here, "..", "data", "datacenter");
const index = JSON.parse(fs.readFileSync(path.join(dir, "index.json"), "utf-8"));
const NAMES = { ...Object.fromEntries(Object.entries(index.blank).map(([id, v]) => [id, v.name])), ...Object.fromEntries(Object.entries(index.grids).map(([id, v]) => [id, v.name])) };
const FILE = fileOf(JSON.parse(fs.readFileSync(path.join(dir, "how_soon.json"), "utf-8")));
if (!FILE) { console.log("FAILED: data/datacenter/how_soon.json is not a file of measured waits (python warehouse/derived/how_soon.py builds it)"); process.exit(1); }

const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (p) => { const r = await fetch(base + p, { headers: { Cookie: cookie } }); return { status: r.status, html: await r.text() }; };
const unescape = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const plain = (html) => unescape(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const face = (html) => { const i = html.indexOf("<h1"); return i < 0 ? "" : html.slice(i); };
/** The block as HTML: from its opening tag to the opening tag of the rules block that follows it. */
const blockHtml = (html) => { const a = html.indexOf('data-waits="1"'), b = html.indexOf('data-rules="1"'); return a < 0 ? "" : html.slice(html.lastIndexOf("<div", a), b > a ? html.lastIndexOf("<div", b) : undefined); };
const sectionHtml = (html) => { const a = html.indexOf('<section id="soon"'); return a < 0 ? "" : html.slice(a, html.indexOf("</section>", a)); };
const attr = (tag, name) => { const m = new RegExp(`\\b${name}="([^"]*)"`).exec(tag); return m ? unescape(m[1]) : null; };
const numbersOf = (s) => (s.match(/\d[\d,]*(?:\.\d+)?/g) ?? []).map((x) => Number(x.replace(/,/g, "")));
const fileNumbers = (v, out = new Set()) => {
  if (typeof v === "number") out.add(v);
  else if (typeof v === "string") for (const x of numbersOf(v)) out.add(x);
  else if (Array.isArray(v)) v.forEach((x) => fileNumbers(x, out));
  else if (v && typeof v === "object") Object.values(v).forEach((x) => fileNumbers(x, out));
  return out;
};
const METHOD_PROSE = /upper bound|limitation|cannot see|interpolat|midpoint|methodolog/i;
const KEPT = ["Generation waiting to connect", "From request to operation, the median", "Of the requests entered", "Large load approved to energize", "Large load in line, by region", "How long a new large load waits"];

const pages = {};
for (const g of ["nyiso", "ercot", "caiso", "isone", "spp", "pjm", "miso"]) pages[g] = await get(`/cost-of-power?grid=${g}`);

// ---- New York ----------------------------------------------------------------------------------------------------
{
  const want = blockOf(FILE, "nyiso"), g = want.entry, html = face(pages.nyiso.html), b = blockHtml(html), text = plain(b);
  check(pages.nyiso.status === 200 && want.state === "measured" && /data-waits-for="nyiso"/.test(b) && /data-waits-state="measured"/.test(b) && text.includes(`How long a large load waits, ${g.place}`),
    `New York: the block is there and measured ("How long a large load waits, ${g?.place}")`);
  const sentence = sentenceOf(FILE, "nyiso", NAMES.nyiso), all = fileNumbers(g);
  check(text.includes(sentence) && numbersOf(sentence).length > 0 && numbersOf(sentence).every((x) => all.has(x)), `the summary sentence is the library's, and each of its ${numbersOf(sentence).length} numbers is a number of the file: "${sentence}"`);
  let rows = 0, lower = 0, marks = 0, tips = 0;
  for (const st of g.stages) {
    const cell = new RegExp(`<span[^>]*data-waits-measured="${st.interval.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"[^>]*>([\\s\\S]*?)</span></td>`).exec(b);
    const wcell = new RegExp(`<span[^>]*data-waits-waiting="${st.interval.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"[^>]*>([\\s\\S]*?)</span></td>`).exec(b);
    if (!cell || !wcell) continue;
    const m = st.measured, w = st.waiting;
    const shown = plain(cell[1]).trim(), wshown = plain(wcell[1]).trim();
    const wantShown = m.n ? `${num(m.n)} ${m.n === 1 ? "request" : "requests"}: ${measuredWords(st)}` : "none yet";
    const tip = attr(/<span[^>]*title="[^"]*"[^>]*>/.exec(cell[1])?.[0] ?? "", "title");
    if (shown === wantShown && attr(cell[0], "data-waits-n") === String(m.n) && b.includes(`data-waits-stage="${st.interval}" data-waits-requests="${st.requests}"`)) rows += 1;
    else console.log(`     ${st.interval}: shows "${shown}", wanted "${wantShown}"`);
    if (tip === measuredTip(st, g.copies, FILE) && tip.includes(`${num(g.copies.n)} dated copies`) && tip.includes(dayWords(g.copies.first)) && tip.includes(dayWords(g.copies.last))) tips += 1;
    if (w.n) {
      lower += 1;
      if (wshown.startsWith(`${num(w.n)} ${w.n === 1 ? "request" : "requests"}: ${waitingWords(st)}`) && wshown.endsWith(LOWER) && attr(wcell[0], "data-waits-lower") === "1" && /data-waits-mark="lower"/.test(wcell[1])) marks += 1;
      else console.log(`     ${st.interval}: still waiting shows "${wshown}"`);
    }
  }
  check(g.stages.length > 0 && rows === g.stages.length, `every stage of the file is a row with the count behind its figure and the library's words (${rows} of ${g.stages.length})`);
  check(tips === g.stages.length, `every measured figure's hover names the count, the ${num(g.copies.n)} copies read and their days (${dayWords(g.copies.first)} to ${dayWords(g.copies.last)})`);
  check(lower > 0 && marks === lower, `every figure of requests still waiting is written "at least" and carries the mark "${LOWER}" (${marks} of ${lower})`);
  const stated = statedOf(g), links = [...b.matchAll(/<span[^>]*data-waits-stated="[^"]*"[^>]*><a ([^>]*)>([^<]*)<\/a>/g)].map((x) => ({ href: attr(`<a ${x[1]}>`, "href"), title: attr(`<a ${x[1]}>`, "title"), text: unescape(x[2]) }));
  check(stated.length > 0 && links.length === stated.length && stated.every((s) => links.some((l) => l.href === s.url && l.title === statedTip(s) && l.text === s.figure)),
    `NYISO's ${stated.length} stated figures stand beside their stages (${stated.map((s) => s.figure).join("; ")}), each a link to its own document with the document, its day and page on hover`);
  check(stated.filter((s) => s.note).every((s) => statedTip(s).includes(s.note)) && stated.some((s) => /Not the same start/.test(s.note ?? "")) && !/Not the same start/.test(text), "where a stated figure and a measurement do not start on the same day the hover says so, and the face does not");
  check(new RegExp(`data-waits-copies="${g.copies.n}"`).test(b) && text.includes(`${num(g.copies.n)} dated copies, ${dayWords(g.copies.first)} to ${dayWords(g.copies.last)}`), "the copies read and their first and last day stand under the table");
  check(!METHOD_PROSE.test(text) && !/\bundefined\b|NaN/.test(text), "no method prose on the block's face, no \"undefined\", no NaN");
  check(/How long a new large load waits\s+measured, below/.test(plain(sectionHtml(html))), 'the section\'s own row "How long a new large load waits" reads "measured, below"');
}

// ---- Texas -------------------------------------------------------------------------------------------------------
{
  const want = blockOf(FILE, "ercot"), g = want.entry, html = face(pages.ercot.html), b = blockHtml(html), text = plain(b);
  const gap = /<p[^>]*data-waits-empty="here"[^>]*><span[^>]*data-missing="1"[^>]*>|<p[^>]*data-waits-empty="here"[^>]*><span[^>]*>/.exec(b)?.[0] ?? "";
  const gapTag = /<span[^>]*>$/.exec(gap)?.[0] ?? "";
  check(want.state === "not measured here" && /data-waits-state="not measured here"/.test(b) && text.includes(`How long a large load waits, ${g.place}`) && new RegExp(`data-waits-empty="here"[^>]*>\\s*<span[^>]*>${NOT_HERE}<`).test(b)
    && attr(gapTag, "title") === notHereWhy(g) && !/data-waits-measured=/.test(b),
    `Texas reads "${NOT_HERE}" and shows no measured stage; its hover: "${notHereWhy(g).slice(0, 110)}..."`);
  const sentence = sentenceOf(FILE, "ercot", NAMES.ercot), all = fileNumbers(g);
  check(text.includes(sentence) && numbersOf(sentence).every((x) => all.has(x)), `Texas's sentence is the library's and its numbers are the file's: "${sentence}"`);
  const links = [...b.matchAll(/<span[^>]*data-waits-stated="[^"]*"[^>]*><a ([^>]*)>([^<]*)<\/a>/g)].map((x) => ({ href: attr(`<a ${x[1]}>`, "href"), title: attr(`<a ${x[1]}>`, "title"), text: unescape(x[2]) }));
  check(g.stated.length > 0 && links.length === g.stated.length && g.stated.every((s, i) => links[i].href === s.url && links[i].title === statedTip(s) && links[i].text === s.figure && text.includes(basisWords(s)) && text.includes(s.covers)),
    `what Texas's own entities measured and stated: ${g.stated.length} figures in the file's order, each labeled whose it is and what it covers, each a link to its document with its hover`);
  const own = g.stated.filter((s) => s.basis === "measured");
  check(own.length > 0 && own.every((s) => text.includes(`measured by ${s.stated_by} itself`) && statedTip(s).includes("not one made here")), `the ${own.length} figures the entities measured themselves are labeled their own (${own.map((s) => `${s.stated_by} ${s.figure}`).join("; ")})`);
  const weeks = g.stated.filter((s) => /week/i.test(s.figure)).map((s) => numbersOf(s.figure)[0]).filter((x) => x !== undefined), sum = weeks.reduce((a, x) => a + x, 0);
  check(weeks.length < 2 || !new RegExp(`\\b${sum} weeks\\b`).test(text + " " + g.stated.map(statedTip).join(" ")), `ERCOT's ${weeks.length} steps in weeks are shown each on its own, and their sum (${sum}) is nowhere on the face or a hover`);
  check(!METHOD_PROSE.test(text) && !/\bundefined\b|NaN/.test(text), "Texas: no method prose on the block's face, no \"undefined\", no NaN");
  check(/How long a new large load waits\s+not measured here/.test(plain(sectionHtml(html))), 'the section\'s own row reads "not measured here" for ERCOT');
}

// ---- every other grid ---------------------------------------------------------------------------------------------
for (const g of ["caiso", "isone", "spp"]) {
  const b = blockHtml(face(pages[g].html)), text = plain(b), want = blockOf(FILE, g);
  const tag = /<p[^>]*data-waits-empty="yet"[^>]*><span[^>]*>/.exec(b)?.[0] ?? "";
  check(want.state === "not measured yet" && new RegExp(`data-waits-for="${g}"`).test(b) && new RegExp(`data-waits-empty="yet"[^>]*>\\s*<span[^>]*>${NOT_YET}<`).test(b) && attr(/<span[^>]*>$/.exec(tag)?.[0] ?? "", "title") === notYetWhy(NAMES[g])
    && text.includes(`${NAMES[g]}: ${NOT_YET}.`) && !/data-waits-measured=|data-waits-stated=/.test(b), `${NAMES[g]} reads "${NOT_YET}" with its reason on hover, and shows no stage and no figure`);
}
// ---- PJM: Virginia (Dominion), session 171 ------------------------------------------------------------------------
// "Not measured yet" (no dated copy of Dominion's queue has been read: the commission's robots file disallows every agent
// it does not name), and under it Dominion's own stated timelines, each labeled Dominion's, each a link to Dominion's own
// document with its day and page on hover. No stage and no measured figure. PJM's prices still read "licensed source needed".
{
  const g = "pjm", b = blockHtml(face(pages[g].html)), text = plain(b), want = blockOf(FILE, g), entry = want.entry, place = entry?.place ?? NAMES[g];
  const tag = /<p[^>]*data-waits-empty="yet"[^>]*><span[^>]*>/.exec(b)?.[0] ?? "";
  check(want.state === "not measured yet" && new RegExp(`data-waits-for="${g}"`).test(b) && new RegExp(`data-waits-empty="yet"[^>]*>\\s*<span[^>]*>${NOT_YET}<`).test(b) && attr(/<span[^>]*>$/.exec(tag)?.[0] ?? "", "title") === notYetWhy(NAMES[g])
    && text.includes(`${place}: ${NOT_YET}.`) && !/data-waits-measured=/.test(b), `${NAMES[g]} (${place}) reads "${NOT_YET}" with its reason on hover, and shows no stage`);
  const stated = statedOf(entry), own = stated.filter((s) => s.stated_by === "Dominion Energy Virginia");
  check(stated.length > 0 && own.length === stated.length && stated.every((s) => s.basis === "expected"), `every figure under PJM is Dominion's own (${stated.length}), each an expectation and none a measurement made here`);
  check(new RegExp(`data-waits-stated-table="${stated.length}"`).test(b) && (b.match(/data-waits-stated=/g) ?? []).length === stated.length, `the stated table holds the file's ${stated.length} figures and no other`);
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const html = (s) => s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  check(stated.every((s) => new RegExp(`<a href="${esc(html(s.url))}"[^>]*title="${esc(html(statedTip(s)))}"`).test(b) && text.includes(s.figure) && text.includes(basisWords(s))),
    "each of Dominion's figures is a link to Dominion's own document, with the document, its day and page on hover, and labeled whose it is");
  check(text.includes(`What ${place}'s own entities measured and stated`) && (b.match(/<table/g) ?? []).length === 1, `one table, "What ${place}'s own entities measured and stated", and no measured table`);
  check(/licensed source needed/i.test(plain(face(pages[g].html))), 'the page still reads "licensed source needed" for PJM\'s prices');
  check(!/\bundefined\b|NaN/.test(text) && !METHOD_PROSE.test(text), `${place}: no method prose on the block's face, no "undefined", no NaN`);
}
{
  const b = blockHtml(face(pages.miso.html)), tag = /<p[^>]*data-waits-paused="1"[^>]*><span[^>]*>/.exec(b)?.[0] ?? "";
  check(/data-waits-state="paused"/.test(b) && new RegExp(`data-waits-paused="1"[^>]*>\\s*<span[^>]*>${PAUSED_WORDS}<`).test(b) && attr(/<span[^>]*>$/.exec(tag)?.[0] ?? "", "title") === PAUSED_WHY && !/data-waits-measured=|data-waits-stated=|<table/.test(b),
    `MISO reads "${PAUSED_WORDS}" and shows nothing else`);
}

// ---- beneath, kept, internal ----------------------------------------------------------------------------------------
for (const g of ["nyiso", "ercot", "caiso"]) {
  const s = sectionHtml(face(pages[g].html)), text = plain(s);
  const table = s.indexOf("<table"), waits = s.indexOf('data-waits="1"'), rules = s.indexOf('data-rules="1"');
  check(table >= 0 && table < waits && waits < rules && text.includes("Rules in motion"), `${NAMES[g]}: in "How soon", the section's table, then the waits, then "Rules in motion" beneath`);
  // the two links are drawn by the site's own link (a page in review is named and marked, not linked, for a visitor)
  check(KEPT.every((k) => text.includes(k)) && text.includes("Interconnection queues") && text.includes("Datacenters") && /MW in [\d,]+ active requests/.test(text),
    `${NAMES[g]}: nothing the section showed is missing (${KEPT.length} rows, the queue's figures, the words that lead to the queues and the datacenters)`);
}
check(/Large load approved to energize\s+[\d,]+ MW, of which [\d,]+ MW observed running \(ERCOT/.test(plain(sectionHtml(face(pages.ercot.html))))
  && /Large load in line, by region\s+not published anywhere yet/.test(plain(sectionHtml(face(pages.ercot.html)))), "ERCOT's large load approved to energize and observed running is still in the section, and the load in line by region reads as before");
{
  const fields = /request_id|request_name|queue_position|queue_date_printed|size_class|mw_last|mw_first|days_at_least/;
  const blocks = ["nyiso", "ercot", "caiso"].map((g) => blockHtml(face(pages[g].html)));
  check(Object.values(pages).every((p) => !fields.test(p.html)) && blocks.every((b) => !/\bMW\b|megawatt/i.test(plain(b))), "no request-level field name is in any of the seven pages, and no megawatt is in the block");
  const tables = [process.env.ERW_TABLES_DIR, path.join(here, "..", "..", "warehouse", "output")].filter(Boolean).map((d) => path.join(d, "large_load_waits.csv")).find((p) => fs.existsSync(p));
  if (!tables) console.log("note: the internal table large_load_waits is not on this machine (ERW_TABLES_DIR names its directory); the page was not searched for its requests' names");
  else {
    // a small reader of the table: quoted fields, doubled quotes; comment lines first
    const raw = fs.readFileSync(tables, "utf-8").split(/\r?\n/).filter((l) => !l.startsWith("#")).join("\n");
    const recs = []; let rec = [], cur = "", q = false;
    for (let i = 0; i < raw.length; i += 1) {
      const c = raw[i];
      if (q) { if (c === '"' && raw[i + 1] === '"') { cur += '"'; i += 1; } else if (c === '"') q = false; else cur += c; }
      else if (c === '"') q = true; else if (c === ",") { rec.push(cur); cur = ""; } else if (c === "\n") { rec.push(cur); recs.push(rec); rec = []; cur = ""; } else cur += c;
    }
    if (cur || rec.length) { rec.push(cur); recs.push(rec); }
    const head = recs[0], col = (name) => head.indexOf(name);
    // Session 163, after session 165's write: only the entities the file shows can put a request on the page (the
    // builder leaves every other entity out of the file, and prints it). Their requests' names are the ones searched
    // for. A queue of another entity holds requests named in everyday words ("Data Center", "New Load"), which stand
    // in the page's own prose: a match there says nothing about a request.
    const shown = new Set(Object.values(FILE.grids ?? {}).map((g) => String(g?.entity ?? "")).filter(Boolean));
    const names = new Set();
    for (const r of recs.slice(1).filter((x) => shown.has(x[col("entity")]))) for (const v of [r[col("request_name")] ?? "", ...(r[col("request_names_seen")] ?? "").split(/[;|]/)]) if (v.trim().length >= 4) names.add(v.trim().toLowerCase());
    const texts = Object.values(pages).map((p) => unescape(p.html).toLowerCase());
    const found = [...names].filter((nm) => texts.some((t) => t.includes(nm)));
    check(names.size > 10 && found.length === 0, `no request's name of the entities shown (${[...shown].join(", ")}: ${names.size} names; the internal table holds ${recs.length - 1} rows) is anywhere in the seven pages${found.length ? `: ${found.length} found` : ""}`);
  }
}

// ---- a real browser ---------------------------------------------------------------------------------------------------
const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, requests, errors, sleep }) => {
  await open(base);
  const from = requests.length;
  await go(`${base}/cost-of-power?grid=nyiso`);
  await wait(`!!document.querySelector('[data-waits="1"]')`, 30000, "the block of measured waits");
  await sleep(2500);
  const ny = blockOf(FILE, "nyiso").entry;
  const dom = await evaluate(`(() => { const b = document.querySelector('[data-waits="1"]'); const r = document.querySelector('[data-rules="1"]'); const soon = document.querySelector('#soon');
    const figs = [...b.querySelectorAll('[data-waits-measured]')].map((e) => ({ id: e.dataset.waitsMeasured, n: e.dataset.waitsN, tip: e.querySelector('[title]')?.title ?? '', text: e.innerText.trim() }));
    const low = [...b.querySelectorAll('[data-waits-lower="1"]')].map((e) => ({ mark: e.querySelector('[data-waits-mark="lower"]')?.innerText ?? '', tip: e.querySelector('[data-waits-mark="lower"]')?.title ?? '', text: e.innerText }));
    const links = [...b.querySelectorAll('[data-waits-stated] a')].map((a) => ({ href: a.getAttribute('href'), title: a.title, tab: a.tabIndex, text: a.innerText }));
    const first = b.querySelector('[data-waits-stated] a'); if (first) first.focus();
    return { state: b.dataset.waitsState, figs, low, links, focused: !!first && document.activeElement === first, sentence: b.querySelector('[data-waits-sentence]').innerText,
      beneath: !!r && !!(b.compareDocumentPosition(r) & Node.DOCUMENT_POSITION_FOLLOWING) && soon.contains(b) && soon.contains(r) && b.getBoundingClientRect().top < r.getBoundingClientRect().top,
      tables: soon.querySelectorAll('table').length }; })()`);
  check(dom.state === "measured" && dom.figs.length === ny.stages.length && dom.figs.every((f, i) => f.id === ny.stages[i].interval && f.n === String(ny.stages[i].measured.n) && f.tip === measuredTip(ny.stages[i], ny.copies, FILE)),
    `in the browser, New York: the ${dom.figs.length} stages in the file's order, each count the file's, each hover its element's title`);
  check(dom.low.length > 0 && dom.low.every((l) => l.mark.toLowerCase() === LOWER && /lower bound/.test(l.tip) && /at least|too few to show/.test(l.text)), `in the browser: the ${dom.low.length} figures of requests still waiting each carry the mark "${LOWER}" with its hover`);
  const stated = statedOf(ny);
  check(dom.links.length === stated.length && dom.links.every((l) => stated.some((s) => s.url === l.href && statedTip(s) === l.title && s.figure === l.text) && l.tab === 0) && dom.focused,
    `in the browser: the ${dom.links.length} stated figures are links to the file's addresses with their hovers, and a link takes the keyboard's focus`);
  check(dom.sentence === sentenceOf(FILE, "nyiso", NAMES.nyiso), "in the browser: the summary sentence is the library's");
  check(dom.beneath, 'in the browser: "Rules in motion" stands beneath the waits, both in the section "How soon"');
  const asked = requests.slice(from).map((r) => r.url);
  const rawAsked = asked.filter((u) => /large_load_waits|large_load_statements|how_soon|\.csv(\?|$)/i.test(u));
  check(asked.length > 0 && rawAsked.length === 0, `the page makes no request for a raw table or for the aggregates file (${asked.length} requests, none names large_load_waits, large_load_statements, how_soon or a .csv)${rawAsked.length ? `: ${rawAsked[0].slice(0, 140)}` : ""}`);

  await go(`${base}/cost-of-power?grid=ercot`);
  await wait(`!!document.querySelector('[data-waits="1"]')`, 30000, "the block for Texas");
  const tx = blockOf(FILE, "ercot").entry;
  const t = await evaluate(`(() => { const b = document.querySelector('[data-waits="1"]'); const gap = b.querySelector('[data-waits-empty="here"] [data-missing]');
    return { state: b.dataset.waitsState, words: gap?.innerText ?? '', why: gap?.title ?? '', links: [...b.querySelectorAll('[data-waits-stated] a')].map((a) => ({ href: a.getAttribute('href'), title: a.title, text: a.innerText })),
      whose: [...b.querySelectorAll('[data-waits-whose]')].map((e) => e.innerText), measured: b.querySelectorAll('[data-waits-measured]').length }; })()`);
  check(t.state === "not measured here" && t.words === NOT_HERE && t.why === notHereWhy(tx) && t.measured === 0, `in the browser, Texas: "${NOT_HERE}" with the reason as its hover, and no measured stage`);
  check(t.links.length === tx.stated.length && t.links.every((l, i) => l.href === tx.stated[i].url && l.title === statedTip(tx.stated[i]) && l.text === tx.stated[i].figure) && t.whose.every((w, i) => w === basisWords(tx.stated[i])),
    `in the browser, Texas: the ${t.links.length} figures of its own entities, each labeled whose it is, each with its source as its hover`);

  await go(`${base}/cost-of-power?grid=caiso`);
  await wait(`!!document.querySelector('[data-waits="1"]')`, 30000, "the block for CAISO");
  const c = await evaluate(`(() => { const b = document.querySelector('[data-waits="1"]'); const gap = b.querySelector('[data-waits-empty="yet"] [data-missing]'); const r = document.querySelector('[data-rules="1"]');
    return { words: gap?.innerText ?? '', why: gap?.title ?? '', tables: b.querySelectorAll('table').length, beneath: !!r && !!(b.compareDocumentPosition(r) & Node.DOCUMENT_POSITION_FOLLOWING) }; })()`);
  check(c.words === NOT_YET && c.why === notYetWhy(NAMES.caiso) && c.tables === 0 && c.beneath, `in the browser, another grid (CAISO): "${NOT_YET}" with its hover, no table, and the rules beneath`);
  const rawAll = requests.map((r) => r.url).filter((u) => /large_load_waits|large_load_statements|how_soon|\.csv(\?|$)/i.test(u));
  check(rawAll.length === 0, `over the three pages opened the browser asked for no raw table (${requests.length} requests)`);
  check(errors.length === 0, `no script error on the pages${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("note: no Chrome or Edge on this machine; the browser checks were not run");
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
