// Energy Research Warehouse (ERW) site, session 7548 (chain 304, part B): the problem sets read as an undergraduate
// working one set start to finish and the teacher who sets it (docs/reviews/problem-sets-read-2026-11-16.md). The pages
// are drawn to HTML with the site's own code on the reads session 7534 kept (replication/problem_sets/: no network), and
// held to the read's site rows and to the pages that share their figures.
//   node --import ./scripts/problem-sets-register.mjs scripts/test-problem-sets-read.mjs
// Checks:
//   row 1: each live question says its number in the newest edition, and each question of the edition's two copies its
//          number on the live page; the two are each other's inverse;
//   row 2: set C names each event's window, equal to /events (app/events/page.tsx) and to docs/methods/events.md, and
//          question 2 names the window's days the table holds no comparison for;
//   row 3: every "Question N" of the decisions block is the live number of the question it means; every docs/ path the
//          block cites exists; on the index each line names its set;
//   row 4: set D's battery question says the fleet's homes (lib/battery.ts FLEET);
//   row 5: set D question 1's step names the days held when they are not one run (and heldRuns on its own);
//   row 6: set E question 5 says the baseline is the same dates of earlier years;
//   shared figures: set C's four headline figures equal /events' cards' rule on the same rows; ERCOT's battery day of the
//          sets equals /storage's rule (the latest row); the bills' wholesale month and price equal /learn/bill's rule;
//   the license hold: no row or figure kept in replication/problem_sets/ (and nothing in the read file) is of a row a
//          license holds (site/lib/license.ts, licenseHeldRow; the rule of site/data/license_status.json).
// Exit 0 when all hold, 1 otherwise. No table written; no model called.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const root = path.join(site, "..");
const REP = path.join(root, "replication", "problem_sets");
const fails = [];
const check = (ok, what) => { if (!ok) fails.push(what); };
process.env.ERW_SPEND_CAP_USD = "0";

// ------------------------------------------------------------------ the kept reads, given back (as problem-sets-figures.mjs replay)
const NULL = "\\N";
function parseCsvLine(line) {
  const out = []; let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) { if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (c === '"') q = false; else cur += c; }
    else if (c === '"') q = true; else if (c === ",") { out.push(cur); cur = ""; } else cur += c;
  }
  out.push(cur);
  return out;
}
const reads = JSON.parse(fs.readFileSync(path.join(REP, "live_reads.json"), "utf-8"));
const byId = new Map(reads.reads.map((x) => [x.id, x.address]));
const kept = new Map(reads.reads.map((x) => [x.address, []]));
const lines = fs.readFileSync(path.join(REP, "live_rows.csv"), "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const head = parseCsvLine(lines[0]);
const allRows = [];
for (const l of lines.slice(1)) {
  const c = parseCsvLine(l), o = {};
  head.forEach((k, i) => { o[k] = c[i] === NULL ? null : c[i]; });
  const r = { entity: o.entity, variable: o.variable, ts_utc: o.ts_utc, value: o.value === null ? null : Number(o.value), unit: o.unit, freq: o.freq };
  const address = byId.get(Number(o.read));
  kept.get(address)?.push(r);
  allRows.push({ ...r, table: new URLSearchParams(address.split("?")[1]).get("table_name")?.replace(/^eq\./, "") ?? "" });
}
const NOW = Date.parse(reads.now);
const realNow = Date.now;
Date.now = () => NOW;
process.env.SUPABASE_URL = "https://kept-reads.invalid";
process.env.SUPABASE_ANON_KEY = "kept";
const samePaged = (a, b) => { const s = (x) => { const u = new URL(x, "http://x"); u.searchParams.delete("offset"); return u.pathname + u.search; }; return s(a) === s(b); };
const realFetch = globalThis.fetch;
globalThis.fetch = async (input) => {
  const u = new URL(typeof input === "string" ? input : input.url);
  if (!u.pathname.startsWith("/rest/v1/")) return reads.network ? new Response(JSON.stringify(reads.network), { status: 200 }) : new Response("not kept", { status: 404 });
  const address = u.pathname + u.search, offset = Number(u.searchParams.get("offset") ?? "0");
  if (!kept.has(address) && !(offset > 0)) throw new Error(`a read that was not kept: ${address}`);
  const rows = offset > 0 ? [] : [...kept.entries()].filter(([a]) => samePaged(a, address)).flatMap(([, r]) => r);
  return new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json" } });
};

const { problemSet, SETS, EVENT_WINDOWS, heldRuns } = await import("../lib/problems.ts");
const { GUIDE, liveNumber, numberIn } = await import("../lib/problemkit.ts");
const { editions, edition } = await import("../lib/problemEditions.ts");
const { FLEET } = await import("../lib/battery.ts");
const { PROBLEM_DECISIONS, ProblemDecisions } = await import("../app/learn/problems/Decisions.tsx");
const Live = (await import("../app/learn/problems/[slug]/page.tsx")).default;
const Students = (await import("../app/learn/problems/[slug]/[edition]/page.tsx")).default;
const Teacher = (await import("../app/learn/problems/[slug]/[edition]/teacher/page.tsx")).default;
const { licenseHeldRow, licenseNeeded, licenseByGrid, gridOfEntity } = await import("../lib/license.ts");
const { createElement: h } = await import("react");

// ------------------------------------------------------------------ row 1: the two numberings
const newest = editions()[0];
check(!!newest, "no edition held");
const ed = edition(newest);
const built = {};
for (const s of SETS) {
  const set = await problemSet(s.slug);
  built[s.slug] = set;
  const html = renderToStaticMarkup(await Live({ params: Promise.resolve({ slug: s.slug }) }));
  const eqs = ed.sets.find((x) => x.slug === s.slug)?.questions;
  set.questions.forEach((q, i) => {
    check(liveNumber(s.slug, q.id) === i + 1, `${s.slug} ${q.id}: the live page draws it as question ${i + 1}, liveNumber says ${liveNumber(s.slug, q.id)}`);
    const n = numberIn(eqs, q.id);
    check(n !== null && html.includes(`data-edition-number="${q.id}"`) && html.includes(`this is question ${n}.</p>`), `${s.slug} ${q.id}: the live page does not say its number in the edition (${n})`);
    // the edition's number of this question, drawn in this question's own line
    const at = html.indexOf(`data-edition-number="${q.id}"`);
    check(at > 0 && html.slice(at, at + 400).includes(`this is question ${n}.`), `${s.slug} ${q.id}: the edition number is not in its own line`);
  });
  for (const [Copy, name] of [[Students, "students"], [Teacher, "teacher"]]) {
    const e = renderToStaticMarkup(await Copy({ params: Promise.resolve({ slug: s.slug, edition: newest }) }));
    for (const q of eqs) {
      const at = e.indexOf(`data-live-number="${q.id}"`);
      check(at > 0 && e.slice(at, at + 400).includes(`this is question ${liveNumber(s.slug, q.id)}.`), `${s.slug} ${name} ${q.id}: no live number`);
      // each other's inverse: the live page's question at that number is this question
      check(built[s.slug].questions[liveNumber(s.slug, q.id) - 1]?.id === q.id, `${s.slug} ${q.id}: not the inverse`);
    }
  }
}
// the case of the read: set C's live question 1 is the edition's question 3 (Elliott), and the edition's question 1 (Uri's price) is the live page's 4
check(liveNumber("when-the-grid-broke", "c3") === 1 && numberIn(ed.sets.find((x) => x.slug === "when-the-grid-broke").questions, "c3") === 3, "set C: Elliott is not live 1 and edition 3");
check(liveNumber("when-the-grid-broke", "c1") === 4, "set C: Uri's price is not live 4");

// ------------------------------------------------------------------ row 2: the event windows, equal to /events and the note
const eventsPage = fs.readFileSync(path.join(site, "app", "events", "page.tsx"), "utf-8");
const notes = fs.readFileSync(path.join(root, "docs", "methods", "events.md"), "utf-8");
for (const [ev, [a, b]] of Object.entries(EVENT_WINDOWS)) {
  const m = new RegExp(`event: "${ev}",[\\s\\S]*?within: \\["([\\d-]+)", "([\\d-]+)"\\]`).exec(eventsPage);
  check(!!m && m[1] === a && m[2] === b, `${ev}: the window ${a} to ${b} is not /events' (${m ? `${m[1]} to ${m[2]}` : "none"})`);
  const sec = notes.slice(notes.search(new RegExp(`^##.*\\(\`${ev}\``, "m")));
  check(new RegExp(`\\*\\*Window:\\*\\* ${a} to ${b}`).test(sec.slice(0, 600)), `${ev}: the window is not docs/methods/events.md's`);
}
const C = Object.fromEntries([built["when-the-grid-broke"].example, ...built["when-the-grid-broke"].questions].map((q) => [q.id, q]));
check(C.cx.q.includes("the storm window is 2021-02-07 to 2021-02-24"), "set C example: no window");
check(C.c1.q.includes("the storm window is 2021-02-07 to 2021-02-24"), "c1: no window");
check(C.c2.q.includes("(the window 2020-08-10 to 2020-08-24)"), "c2: no window");
check(C.c3.q.includes("in the window (2022-12-19 to 2022-12-29)"), "c3: no window");
check(C.c4.q.includes("(the window 2023-08-01 to 2023-09-10;"), "c4: no window");
// the price questions name the hub whose price they ask about (the table's rows of ercot:HB_HUBAVG)
for (const id of ["c1", "c4"]) check(C[id].q.includes("the price at ERCOT's hub average, HB_HUBAVG"), `${id}: the hub not named`);
check(C.c5.q.includes("at ERCOT's hub average (HB_HUBAVG)"), "c5: the hub not named");
const c2step = C.c2.steps[0].filter((p) => typeof p === "string").join("");
check(c2step.includes("no comparison for 2020-08-10, 2020-08-11 and 2020-08-23"), `c2: the days with no comparison: ${c2step}`);

// ------------------------------------------------------------------ row 3: the decisions' question numbers
const MEANT = { "full-day": ["know-your-grid", "a1", "a2"], "local-day": ["know-your-grid", "a5"], "public-hubs": ["prices-and-your-bill", "b2"],
  bill: ["prices-and-your-bill", "b3", "b4"], "seven-days": ["storage-and-taxes", "d1"], credit: ["storage-and-taxes", "d5"],
  "network-hour": ["networks-and-money", "e1", "e2"], "storm-days": ["networks-and-money", "e5"] };
for (const d of PROBLEM_DECISIONS) {
  const said = [...d.text.matchAll(/\bQuestions? ([\d, and]+?)(?= (?:take|adds|ranks|sets)|'s)/g)].flatMap((m) => m[1].match(/\d+/g).map(Number));
  if (!MEANT[d.key]) { check(said.length === 0, `${d.key}: names a question the test does not know`); continue; }
  const [slug, ...ids] = MEANT[d.key];
  const want = ids.map((id) => liveNumber(slug, id)).sort((x, y) => x - y);
  check(JSON.stringify(said) === JSON.stringify(want), `${d.key}: says ${said}, the live page asks them as ${want}`);
  for (const p of d.source.match(/docs\/[\w/.-]+\.md/g) ?? []) check(fs.existsSync(path.join(root, p)), `${d.key}: cites ${p}, which does not exist`);
}
for (const d of PROBLEM_DECISIONS) for (const p of d.source.match(/docs\/[\w/.-]+\.md/g) ?? []) check(fs.existsSync(path.join(root, p)), `${d.key}: cites ${p}, which does not exist`);
check(!PROBLEM_DECISIONS.some((d) => d.source.includes("event_window.md")), "a decision cites docs/methods/event_window.md");
const idx = renderToStaticMarkup(h(ProblemDecisions, {}));
check(idx.includes('data-decision-sets="live">Every set: ') && idx.includes('data-decision-sets="bill">Prices and your bill: '), "the index: a line without its set");
check(!renderToStaticMarkup(h(ProblemDecisions, { slug: "prices-and-your-bill" })).includes("data-decision-sets"), "a set's page names the set on each line");

// ------------------------------------------------------------------ rows 4 to 6: words a student needs
const D = Object.fromEntries(built["storage-and-taxes"].questions.map((q) => [q.id, q]));
check(FLEET === 10000 && D.d3.q.includes(`fictional fleet of ${FLEET.toLocaleString("en-US")} homes`), "d3: the fleet's homes not said");
check(D.d3.line.filter((p) => typeof p === "string").join("").includes(`times the fleet's ${FLEET.toLocaleString("en-US")} homes`), "d3: the line does not say the homes");
const d1step = D.d1.steps[0].join("");
check(d1step.includes("the days held are 2026-11-03 and 2026-11-09 to 2026-11-14"), `d1: ${d1step}`);
check(heldRuns(["2026-11-08", "2026-11-09", "2026-11-10"]) === "", "heldRuns: one run");
check(heldRuns(["2026-10-31", "2026-11-01", "2026-11-05"]) === ": the days held are 2026-10-31 to 2026-11-01 and 2026-11-05", "heldRuns: across a month");
const E5 = built["networks-and-money"].questions.find((q) => q.id === "e5");
check(E5.q.includes("against as many normal days (the same dates of earlier years)?") && !E5.q.includes("before the storm"), `e5: ${E5.q}`);

// ------------------------------------------------------------------ shared figures: /events, /storage, /learn/bill
const rowsOf = (table, entity, variable, event) => allRows.filter((r) => r.table === table && r.entity === entity && r.variable === variable);
const maxIn = (xs, [a, b]) => xs.filter((r) => r.ts_utc.slice(0, 10) >= a && r.ts_utc.slice(0, 10) <= b).reduce((m, r) => (m === null || r.value > m.value ? r : m), null);
const fig = (q, unit) => q.answer.find((p) => typeof p !== "string" && p.u === unit);
const card = (ev) => { const m = new RegExp(`event: "${ev}",\\s*entity: "([^"]+)", variable: "([^"]+)", how: "max", within: \\["([\\d-]+)", "([\\d-]+)"\\]`).exec(eventsPage); return m ? { entity: m[1], variable: m[2], within: [m[3], m[4]] } : null; };
// the event rows were read by event (the reads' addresses name it); the kept rows of one entity and variable are of one event each here
const evRows = (ev, entity, variable) => {
  const id = reads.reads.find((x) => x.address.includes(`event=eq.${ev}`) && x.address.includes(`entity=eq.${encodeURIComponent(entity)}`) && x.address.includes(`variable=eq.${variable}`))?.id;
  return id === undefined ? [] : kept.get(byId.get(id));
};
for (const [ev, qid, unit] of [["uri_2021", "c1", "USD/MWh"], ["caiso_heat_2020", "c2", "%"], ["elliott_2022", "c3", "MW"], ["ercot_heat_2023", "c4", "USD/MWh"]]) {
  const c = card(ev);
  check(!!c, `${ev}: no card on /events`);
  if (!c) continue;
  const top = maxIn(evRows(ev, c.entity, c.variable), c.within);
  const ours = fig(C[qid], unit);
  check(top && ours && Math.abs(top.value - ours.v) < 1e-9, `${ev}: /events' card ${top?.value} against set C's ${ours?.v}`);
}
// /storage: each grid's latest row of storage_daily_cycle (app/storage/page.tsx, Cycle: dis.at(-1)); ERCOT here
const ercotDis = allRows.filter((r) => r.table === "storage_daily_cycle" && r.entity === "eia930:ERCO" && r.variable === "mwh_discharged").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
const ex = built["storage-and-taxes"].example;
const exDis = ex.answer.find((p) => typeof p !== "string" && p.k.includes("|mwh_discharged|"));
check(ercotDis.length && exDis && ercotDis.at(-1).value === exDis.v && exDis.k.includes(ercotDis.at(-1).ts_utc.slice(0, 10)), `/storage's ERCOT day ${ercotDis.at(-1)?.ts_utc} ${ercotDis.at(-1)?.value} against set D's example ${exDis?.k} ${exDis?.v}`);
// /learn/bill: the latest month whose rt_hours equals hours_in_month, its rt_load_weighted (app/learn/bill/page.tsx, wholesaleOf)
const bills = JSON.parse(fs.readFileSync(path.join(site, "data", "bill_rules.json"), "utf-8")).bills;
for (const [qid, bill] of [["b3", "CA"], ["b4", "TX"]]) {
  const entity = bills[bill]?.wholesale_entity;
  check(!!entity, `${bill}: no wholesale entity in bill_rules.json`);
  const by = new Map();
  for (const r of allRows.filter((x) => x.table === "cost_of_power_monthly" && x.entity === entity)) (by.get(r.ts_utc.slice(0, 7)) ?? by.set(r.ts_utc.slice(0, 7), {}).get(r.ts_utc.slice(0, 7)))[r.variable] = r;
  const full = [...by.keys()].filter((m) => by.get(m).rt_load_weighted && by.get(m).rt_hours?.value === by.get(m).hours_in_month?.value).sort();
  const q = built["prices-and-your-bill"].questions.find((x) => x.id === qid);
  const price = q.line.find((p) => typeof p !== "string" && p.k.includes("|rt_load_weighted|"));
  check(full.length && price && price.v === by.get(full.at(-1)).rt_load_weighted.value && price.k.includes(full.at(-1)), `${qid}: /learn/bill's month ${full.at(-1)} against the set's ${price?.k}`);
}

// ------------------------------------------------------------------ the license hold: nothing held is kept
const heldRow = (table, entity) => licenseNeeded(table) && licenseHeldRow(table, entity ?? null);
let held = 0;
for (const r of allRows) if (heldRow(r.table, r.entity)) { held++; if (held < 4) fails.push(`a held row kept: ${r.table} ${r.entity} ${r.variable} ${r.ts_utc}`); }
const HELD_GRIDS = ["isone", "miso", "nyiso"];
const keys = [];
const pf = JSON.parse(fs.readFileSync(path.join(REP, "page_figures.json"), "utf-8"));
for (const s of Object.values(pf.sets)) for (const q of s.questions) for (const f of q.figures) keys.push(f.k);
for (const k of keys) for (const part of k.split(/[|~]/)) {
  const g = gridOfEntity(part);
  if (HELD_GRIDS.includes(g)) { fails.push(`a figure of a held grid kept: ${k}`); break; }
}
// the event rows the sets keep are of four entities, none of a held grid (EIA-930's ERCO, PJM and CISO; ERCOT's hub)
const evEntities = [...new Set(allRows.filter((r) => r.table === "event_window_daily").map((r) => r.entity))].sort();
check(JSON.stringify(evEntities) === JSON.stringify(["eia930:CISO", "eia930:ERCO", "eia930:PJM", "ercot:HB_HUBAVG"]), `event rows of ${evEntities}`);
// every held-by-grid table's kept rows: no entity of a held grid
for (const r of allRows) if (licenseByGrid(r.table) && HELD_GRIDS.includes(gridOfEntity(r.entity))) { fails.push(`a held grid's row: ${r.table} ${r.entity}`); break; }
const readFile = path.join(root, "docs", "reviews", "problem-sets-read-2026-11-16.md");
if (fs.existsSync(readFile)) {
  const t = fs.readFileSync(readFile, "utf-8");
  check(!/\b(isone|miso|nyiso):/i.test(t), "the read file names an entity of a held grid");
  check(!t.includes(String.fromCharCode(0x2014)), "an em dash in the read file");
} else fails.push("no read file");

Date.now = realNow;
globalThis.fetch = realFetch;
if (fails.length) { console.log(`FAIL ${fails.length}:\n  ${fails.join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${SETS.length} sets read; both numberings, 4 windows equal to /events, ${Object.keys(MEANT).length} decision lines, 4 + 1 + 2 shared figures, ${allRows.length} kept rows and ${keys.length} figure keys with none held`);
