// Session 10217: every figure the monitor view of /policy prints as it opens (/policy?view=monitor, the opening
// filters, the page's day given), computed by the page's OWN functions (site/lib/policymonitor.ts, largeloadrules.ts,
// policyweek.ts) on the page's own files (site/data/policy/monitor.json, site/data/siting/large_load_rules.json,
// site/data/policy/*.json). Writes one JSON of keyed figures for compare.py.
//   cd site && node --import ./scripts/tsx-register.mjs ../runs/c10217/page_figures.mjs 2026-11-26 ../runs/c10217/page.json
import fs from "node:fs";
import path from "node:path";
import * as M from "@/lib/policymonitor";
import * as L from "@/lib/largeloadrules";
import * as W from "@/lib/policyweek";

const today = process.argv[2];
const outPath = process.argv[3];
const read = (p) => JSON.parse(fs.readFileSync(path.join(process.cwd(), p), "utf8"));
const m = read("data/policy/monitor.json");
const ll = read("data/siting/large_load_rules.json");
const out = {};
const put = (k, v) => { out[k] = v; };

// ---- the monitor as it opens (MonitorView.tsx) -------------------------------------------------------------------------
const f = M.filtersOf({ view: "monitor" });
const rows = m.rows;
const shown = M.sortRows(M.filterRows(rows, f), "date", "desc", today);
put("count|shown", shown.length);
put("count|held", m.records);
put("count|rows", rows.length);
put("built", m.built);
const opts = M.options(rows, f);
for (const [list, os] of Object.entries(opts)) for (const o of os) put(`option|${list}|${o.key}`, o.n);
for (const [list, os] of Object.entries(opts)) put(`optorder|${list}`, os.map((o) => o.key).join(","));
for (const [list, os] of Object.entries(opts)) for (const o of os) put(`optionlabel|${list}|${o.key}`, o.label);

// the calendar (MonitorCalendar.tsx): the rows the filters leave, dates aside
const last = M.lastDateOf(rows);
put("calendar|last", last);
const c = M.calendarOf(M.filterRows(rows, { ...f, from: "", to: "" }), today, last);
put("calendar|stale", c.stale);
put("calendar|weekFrom", c.weekFrom);
put("calendar|weekTo", c.weekTo);
put("calendar|aheadTo", c.aheadTo);
put("calendar|week|n", c.week.length);
c.week.slice(0, 60).forEach((r, i) => put(`calendar|week|${i}`, `${r.date}|${r.id}|${r.body}|${M.INSTRUMENT_WORDS[r.instrument] ?? r.instrument}|${(M.STATUS_WORDS[r.status] ?? r.status).toLowerCase()}`));
put("calendar|ahead|n", c.ahead.length);
c.ahead.slice(0, 80).forEach(({ row, step }, i) => put(`calendar|ahead|${i}`, `${step.date}|${M.KIND_WORDS[step.kind] ?? step.kind}|${row.id}|${step.event_id}`));
put("calendar|hidden", M.floorHidden(rows, f, today));

// the table: the first MONITOR_PAGE rows drawn
put("table|page", M.MONITOR_PAGE);
shown.slice(0, M.MONITOR_PAGE).forEach((r, i) => {
  const nx = M.nextOf(r, today);
  put(`table|${i}`, [r.id, r.date, r.body, M.INSTRUMENT_WORDS[r.instrument] ?? r.instrument, M.STATUS_WORDS[r.status] ?? r.status, M.sectorWords(r.sector),
    r.significance ?? "", nx ? `${nx.date} ${M.KIND_WORDS[nx.kind] ?? nx.kind}${nx.passed ? ", passed" : ""}` : "", r.figure ? M.figureText(r.figure) : "", r.n].join("|"));
});
// every shown row's next step and figure (they are drawn page by page with "Next 50")
let passed = 0, ahead = 0, none = 0;
for (const r of shown) { const nx = M.nextOf(r, today); if (!nx) none++; else if (nx.passed) passed++; else ahead++; }
put("table|next|ahead", ahead); put("table|next|passed", passed); put("table|next|none", none);
put("table|figure|n", shown.filter((r) => r.figure).length);

// the charts (MonitorCharts.tsx): every record of the file
const bm = M.byBodyMonth(rows);
put("chart|bodymonth|months", M.monthLabels(bm.months, last).join(","));
for (const s of bm.series) put(`chart|bodymonth|${s.name}`, s.values.join(","));
const ss = M.sigBySector(rows);
put("chart|sigsector|sectors", ss.sectors.join(","));
for (const s of ss.series) put(`chart|sigsector|${s.name}`, s.values.join(","));
for (const x of M.figureMonths(rows)) put(`chart|fig|${x.month}|${x.unit}`, `${x.n}|${x.top.id}|${M.figureText(x.top.figure)}`);

// ---- the laws block (StateLaws.tsx), no state chosen ------------------------------------------------------------------
put("laws|public", ll.laws.length);
put("laws|held", ll.held_laws.length);
for (const s of L.LAW_STATUSES) { const n = ll.laws.filter((l) => l.status === s).length; if (n) put(`laws|status|${s}`, n); }
const haveLaw = new Set([...ll.laws, ...ll.held_laws].map((l) => l.state));
const others = (ll.law_searches ?? []).filter((x) => !haveLaw.has(x.state));
put("laws|shown", ll.laws.length + ll.held_laws.length);
put("laws|total", ll.laws.length + ll.held_laws.length);
put("laws|withheldRows", others.filter((x) => x.kind === "withheld").length);
put("laws|searched|n", others.length);
put("laws|searched|list", others.map((x) => `${x.state}:${L.lawSearchOf(ll.law_searches, x.state).kind}`).join(","));
put("laws|states", haveLaw.size);
put("laws|retrievedWords", ll.retrieved[L.LAWS_TABLE]?.slice(0, 8).replace(/^(\d{4})(\d{2})(\d{2})$/, "$1-$2-$3") ?? "");
for (const l of ll.laws) put(`law|${l.id}`, [l.state, l.bill, l.status, L.statusDateWords(l.status_date), L.dateWords(l.effective), l.threshold && l.threshold !== "not published" ? "threshold" : "not published", L.requirementsOf(l).map((p) => p.topic).join(";")].join("|"));
// page.tsx's countByState over rules (public and held) and changes, for the line a chosen state draws
const countByState = (states) => { const o = {}; for (const s of states) for (const st of L.statesOf(s)) o[st] = (o[st] ?? 0) + 1; return o; };
const rules = countByState([...ll.rules, ...ll.held_rules].map((r) => r.state));
const changes = countByState(ll.changes.map((x) => x.state));
for (const [s, n] of Object.entries(rules)) put(`laws|rules|${s}`, n);
for (const [s, n] of Object.entries(changes)) put(`laws|changes|${s}`, n);

// ---- the paused line (Paused.tsx) -------------------------------------------------------------------------------------
const paused = read("data/policy/paused.json"), refresh = read("data/policy/refresh.json"), grids = read("data/policy/grids.json");
const names = {};
for (const r of refresh.regulators ?? []) if (r && typeof r.key === "string") names[r.key] = (r.short ?? "").trim() || r.regulator;
for (const g of grids.grids ?? []) if (g && typeof g.key === "string" && !(g.key in names)) names[g.key] = g.name;
const pl = W.pausedLine(paused, names);
put("paused|words", pl.words);
pl.items.forEach((i) => put(`paused|${i.key}`, `${i.name}, ${i.words}`));

// ---- the week view's docket rows (WeekView.tsx; the actions of policy_actions are held, so the dockets are what it draws)
const stateFile = read("data/policy/state_rules.json"), tagRules = read("data/policy/tag_rules.json");
const bodies = W.bodiesOf(refresh, [], paused);
const topics = W.topicsOf(tagRules, stateFile.topics ?? []);
for (const days of [7, 30]) {
  const inw = stateFile.rows.filter((s) => W.inWindow(String(s.date ?? ""), today, days));
  const kept = [], dropped = [];
  for (const s of inw) { const g = W.docketRow(s, bodies, topics, tagRules); if (g.row) kept.push(g.row); else dropped.push(g.dropped); }
  put(`week|${days}|since`, W.sinceDay(today, days));
  put(`week|${days}|inwindow`, inw.length);
  put(`week|${days}|shown`, kept.length);
  put(`week|${days}|dropped`, dropped.length);
  const by = {};
  for (const r of kept) by[r.body] = (by[r.body] ?? 0) + 1;
  for (const [b, n] of Object.entries(by)) put(`week|${days}|body|${b}`, n);
}
put("week|statefile|built", stateFile.built_at_utc);
put("week|statefile|rows", stateFile.rows.length);

fs.writeFileSync(outPath, JSON.stringify(out, null, 1));
console.log(`${Object.keys(out).length} keys written to ${outPath}`);
