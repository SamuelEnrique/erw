// Energy Research Warehouse (ERW) site, session 196: the line "Checked against: ..." of the three decision pages, and
// the section of each Method note it links to. Session 538: the same section of the Grid tool's note and of Research's.
//
//   npm run build && npm start
//   node scripts/check-cross-checks.mjs [base-url]
//   node scripts/check-cross-checks.mjs --files [--root <repository>]   (no browser, no server: the files only)
//
// In the internal view, for /cost-of-power/battery, /cost-of-power/seller and /cost-of-power:
//   1. the page's source line says "Checked against: N published figures (...)", with a link;
//   2. the link opens the page's step-by-step Method note at its section "Cross-checks";
//   3. that section's table has N rows, each with our figure, the published figure, its source, the gap and the reason,
//      and no cell is empty;
//   4. every source of the table is a link to its publisher, the warehouse's own table, or "the same" as the row above.
//
// Session 538 (session 381 wrote the two sections; this script read only the three decision pages until then): for the
// Grid tool's note (docs/methods/grid_network.md) and Research's (docs/methods/automated_analysis_findings.md), which no
// page links to by a "Checked against" line (adding one to /grid and /research is session 381's ruling item, and this
// script changes no page):
//   5. the note's section "Cross-checks" is on the built note at its anchor, its table in the five columns, with as many
//      rows as the note's markdown holds and never fewer than session 381 wrote (11 and 4);
//   6. every row has our figure, the published figure, its source, the gap and a reason longer than 30 characters;
//   7. every source is a link, "the same", or an ERW Method note it names (docs/methods/<note>.md) that opens on the
//      site: the owner's thesis has no public address, and its figures are held in two notes; the row's own check (8)
//      then reads the published figure in that note;
//   8. where a row names a figure by its key (a finding card's id, the Network view's replication file), the figure's
//      own source equals the row: the card's JSON ("numbers", site/data/findings/<card>.json, the file the build
//      bundles), the thesis's table in the note it cites, the replication file's rows for the hour the row names; the gap
//      is ours less theirs; and on the built card page the callout that draws the figure (its check key) shows the
//      row's figure. A callout held for a license ("license needed" in place, lib/license.ts) is named, not failed.
// With --files, 5 to 8 are read from the repository's files instead of the built site (the page callouts are then not
// read). Prints every check. Exits 1 if any assertion fails; with no browser on the machine, the files are checked and
// the built site is named as not proven here.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

const argv = process.argv.slice(2);
const FILES = argv.includes("--files");
const ri = argv.indexOf("--root");
const ROOT = ri >= 0 ? path.resolve(argv[ri + 1]) : path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const base = (argv.find((a, i) => !a.startsWith("--") && argv[i - 1] !== "--root") ?? "http://localhost:3000").replace(/\/$/, "");
let failed = 0, n = 0;
const check = (ok, what, detail = "") => { n += 1; if (!ok) failed += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`); };
const note_ = (what) => console.log(`note ${what}`);
const PAGES = [["/cost-of-power/battery", "battery_earns_algorithm"], ["/cost-of-power/seller", "generator_earns_algorithm"], ["/cost-of-power", "datacenter_pays_algorithm"]];
const COLUMNS = ["Our figure", "Published figure", "Source and date", "Gap", "Reason"];

// ---- session 538: the two notes without a "Checked against" line ----
const NOTES = [{ note: "grid_network", floor: 11, page: "/grid" }, { note: "automated_analysis_findings", floor: 4, page: "/research" }];
const read = (...p) => fs.readFileSync(path.join(ROOT, ...p), "utf-8");
/** A markdown cell as the page shows its text: links to their words, no code ticks, no emphasis marks. */
const plain = (s) => s.replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1").replace(/`/g, "").replace(/\*\*?/g, "").replace(/\\\|/g, "|").replace(/\s+/g, " ").trim();
const splitRow = (line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split(/(?<!\\)\|/);
/** Every table of a markdown text: { head, rows }, each cell { text, link }. */
function mdTables(md) {
  const out = []; let cur = null;
  for (const line of md.split(/\r?\n/)) {
    if (line.trim().startsWith("|")) { (cur ??= []).push(line); continue; }
    if (cur) { out.push(cur); cur = null; }
  }
  if (cur) out.push(cur);
  return out.filter((t) => t.length >= 2).map((t) => ({
    head: splitRow(t[0]).map(plain),
    rows: t.slice(2).map((l) => splitRow(l).map((c) => ({ text: plain(c), link: /\]\(https:\/\//.test(c) }))),
  }));
}
/** The lines of a markdown text from a heading to the next heading of its level. */
function mdSection(md, heading) {
  const lines = md.split(/\r?\n/);
  const i = lines.findIndex((l) => l.trim() === heading);
  if (i < 0) return null;
  const j = lines.findIndex((l, k) => k > i && l.startsWith("## "));
  return lines.slice(i + 1, j < 0 ? lines.length : j).join("\n");
}
const N = (s) => Number(String(s).replace(/,/g, "").replace(/^\+/, ""));
const NUM = /[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[+-]?\d+(?:\.\d+)?/g;
const nums = (s) => [...String(s).matchAll(NUM)].map((m) => N(m[0]));
const grab = (re, s) => { const m = re.exec(s); return m ? m.slice(1) : []; };
const fmt0 = (v) => Math.round(v).toLocaleString("en-US");
const near = (a, b, tol) => Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= tol;
const BA = { ERCOT: "ERCO", "ISO-NE": "ISNE", NYISO: "NYIS", CAISO: "CISO", MISO: "MISO", PJM: "PJM", SPP: "SWPP" };

/** The Network view's replication file (site/public/grid/erw_2026_grid_replication.csv, session 266): its hour and,
 *  for each balancing authority, the net imports by its ties (a tie's value is positive when `id` exports to `other`)
 *  and EIA-930's demand less net generation. */
function replication(csv) {
  const hour = (/^# hour_shown,(\S+)/m.exec(csv) ?? [])[1] ?? "";
  const ties = {}, dem = {}, gen = {};
  for (const line of csv.split(/\r?\n/)) {
    if (!line || line.startsWith("#") || line.startsWith("kind,")) continue;
    const [kind, id, other, , value] = line.split(",");
    const v = Number(value);
    if (kind === "tie") { ties[id] = (ties[id] ?? 0) - v; ties[other] = (ties[other] ?? 0) + v; }
    if (kind === "demand") dem[id] = v;
    if (kind === "generation") gen[id] = v;
  }
  return { hour, ties, balance: (ba) => (ba in dem && ba in gen ? dem[ba] - gen[ba] : NaN) };
}

/** The rows that name a figure by its key. `find` is words of the row's "Our figure"; `test` returns [ok, what, detail]
 *  lines from the row's cells (text), the other rows of its table, and the reading context. */
const FIGURES = [
  { note: "automated_analysis_findings", find: "the median real-time price", key: "card batteries_lunch_grids, numbers.ercot_median_last", test: async (c, rows, ctx) => {
    const [ours] = grab(/USD ([\d.,]+) per MWh/, c[0]).map(N), [theirs] = grab(/USD ([\d.,]+) per MWh/, c[1]).map(N), gap = N(c[3]);
    const card = await ctx.card("batteries_lunch_grids");
    const thesis = await ctx.thesis("all_median");
    return [
      [card.numbers.ercot_median_last.toFixed(2) === ours?.toFixed(2), "the card's figure (numbers.ercot_median_last) is the row's", `${card.numbers.ercot_median_last} and ${ours}`],
      [String(card.numbers.ercot_last_full_year) === "2025" && /, 2025,/.test(c[0]), "the card's year (numbers.ercot_last_full_year) is the row's", String(card.numbers.ercot_last_full_year)],
      [thesis === theirs?.toFixed(2), "the published figure is the thesis's in the note the row cites (ercot_peak_premium, all_median, 2025)", `${thesis} and ${theirs}`],
      [near(ours - theirs, gap, 0.005), "the gap is ours less theirs", `${c[3]}`],
    ];
  } },
  { note: "automated_analysis_findings", find: "the 99.9th percentile", key: "card batteries_lunch_grids, numbers.ercot_p999_last; callout 0, after", test: async (c, rows, ctx) => {
    const [ours] = grab(/USD ([\d.,]+) per MWh/, c[0]).map(N), [theirs] = grab(/USD ([\d.,]+) per MWh/, c[1]).map(N), gap = N(c[3]);
    const card = await ctx.card("batteries_lunch_grids");
    const thesis = await ctx.thesis("all_p999");
    const want = `${(ours / card.numbers.ercot_median_last).toFixed(1)}x`;
    return [
      [card.numbers.ercot_p999_last.toFixed(2) === ours?.toFixed(2), "the card's figure (numbers.ercot_p999_last) is the row's", `${card.numbers.ercot_p999_last} and ${ours}`],
      [thesis === theirs?.toFixed(2), "the published figure is the thesis's in the note the row cites (ercot_peak_premium, all_p999, 2025)", `${thesis} and ${theirs}`],
      [near(ours - theirs, gap, 0.005), "the gap is ours less theirs", `${c[3]}`],
      ...(await ctx.figure("/research/card/batteries_lunch_grids", "finding|batteries_lunch_grids|callout|0|after|ercot", want, "the card page's ERCOT worst-interval multiple for 2025 is the row's percentile over the median")),
    ];
  } },
  { note: "automated_analysis_findings", find: "Requests withdrawn, 2000 to 2020", key: "card queue_divorce, numbers.withdrawn_pct and requested_gw; callout 0, before", test: async (c, rows, ctx) => {
    const [pct, gw] = grab(/([\d.]+) percent of ([\d,]+) GW/, c[0]).map(N), [tpct, tgw] = grab(/([\d.]+) percent of ([\d,]+) GW/, c[1]).map(N);
    const [gp] = grab(/([+-][\d.]+) points/, c[3]).map(N), [gg] = grab(/([+-][\d,]+) GW/, c[3]).map(N);
    const card = await ctx.card("queue_divorce");
    const text = await ctx.text("automated_analysis_findings");
    return [
      [card.numbers.withdrawn_pct.toFixed(1) === pct?.toFixed(1) && fmt0(card.numbers.requested_gw) === fmt0(gw), "the card's figures (numbers.withdrawn_pct, requested_gw) are the row's", `${card.numbers.withdrawn_pct.toFixed(1)} percent of ${fmt0(card.numbers.requested_gw)} GW`],
      [text.includes(`The thesis's ${tpct} percent of ${fmt0(tgw)} GW`), "the published figure is the thesis's as Finding 3 of the note quotes it", `${tpct} percent of ${fmt0(tgw)} GW`],
      [near(pct - tpct, gp, 0.05) && near(gw - tgw, gg, 0.5), "the gap is ours less theirs", c[3]],
      ...(await ctx.figure("/research/card/queue_divorce", "finding|queue_divorce|callout|0|before|-", `${Math.round(pct)}% of ${fmt0(gw)} GW`, "the card page's withdrawn share is the row's, to the whole percent")),
    ];
  } },
  { note: "automated_analysis_findings", find: "The marriage and divorce rates", key: "card queue_divorce, numbers.cdc_marriage_rate and cdc_divorce_rate; callout 2", test: async (c, rows, ctx) => {
    const [m, d] = grab(/([\d.]+) and ([\d.]+) per 1,000/, c[0]).map(N), [tm, td] = grab(/([\d.]+) and ([\d.]+) per 1,000/, c[1]).map(N);
    const [ratio] = grab(/([\d.]+) percent/, c[4]).map(N), [times] = grab(/([\d.]+) times/, c[4]).map(N);
    const card = await ctx.card("queue_divorce");
    const text = await ctx.text("automated_analysis_findings");
    return [
      [card.numbers.cdc_marriage_rate === m && card.numbers.cdc_divorce_rate === d, "the card's rates (numbers.cdc_marriage_rate, cdc_divorce_rate) are the row's", `${card.numbers.cdc_marriage_rate} and ${card.numbers.cdc_divorce_rate}`],
      [card.numbers.cdc_ratio_pct.toFixed(1) === ratio?.toFixed(1) && card.numbers.queue_over_cdc.toFixed(1) === times?.toFixed(1), "the reason's ratio and multiple are the card's (cdc_ratio_pct, queue_over_cdc)", `${ratio} percent, ${times} times`],
      [text.includes(`Marriage rate: ${tm} per 1,000`) && text.includes(`Divorce rate: ${td} per 1,000`), "the published rates are the CDC's as the note quotes the page"],
      [m - tm === N(c[3]) && d - td === N(c[3]), "the gap is ours less theirs", c[3]],
      ...(await ctx.figure("/research/card/queue_divorce", "finding|queue_divorce|callout|2|before|-", `${d} / ${m}`, "the card page's rates are the row's")),
      ...(await ctx.figure("/research/card/queue_divorce", "finding|queue_divorce|callout|2|after|-", `${Math.round(ratio)}%`, "the card page's ratio is the reason's, to the whole percent")),
    ];
  } },
  { note: "grid_network", find: "Net imports by ties in the hour shown", key: "the Network view's replication file, kind tie, demand and generation", test: async (c, rows, ctx) => tiesRow(c, c, ctx) },
  { note: "grid_network", find: "The same hour, the four others", key: "the Network view's replication file, kind tie, demand and generation", test: async (c, rows, ctx) => {
    const first = rows.find((r) => r[0].includes("Net imports by ties in the hour shown"));
    return first ? tiesRow(c, first, ctx) : [[false, "the row names the hour of the row above it", "no such row"]];
  } },
];
/** A row of net imports by ties: our figures are the replication file's ties, the published ones its demand less
 *  generation, at the hour the row (or the row it follows, `hourRow`) names. */
async function tiesRow(c, hourRow, ctx) {
  const [day, hh] = grab(/\((\d{4}-\d{2}-\d{2}) (\d{2}):00 UTC\)/, hourRow[0]);
  const hour = day ? `${day}T${hh}:00:00Z` : "";
  const grids = [...c[0].matchAll(/\b(ERCOT|ISO-NE|NYISO|CAISO|MISO|PJM|SPP) (-?\d[\d,]*)/g)].map((m) => [m[1], N(m[2])]);
  const theirs = nums(c[1].split(":").pop()), gaps = nums(c[3]);   // the figures after the cell's words ("EIA-930's ...: 128, 156")
  const rep = replication(await ctx.replication());
  const out = [[!!hour && rep.hour === hour, "the replication file's hour is the row's", `${rep.hour} and ${hour || "none named"}`],
    [grids.length > 0 && theirs.length === grids.length && gaps.length === grids.length, "the row gives each grid our figure, the published one and the gap", grids.map(([g]) => g).join(", ")]];
  grids.forEach(([g, ours], i) => {
    const ba = BA[g];
    out.push([rep.ties[ba] === ours, `${g}: net imports by ties (${ba}) are the row's`, `${rep.ties[ba]} and ${ours}`]);
    out.push([rep.balance(ba) === theirs[i], `${g}: EIA-930's demand less net generation is the row's published figure`, `${rep.balance(ba)} and ${theirs[i]}`]);
    out.push([ours - theirs[i] === gaps[i], `${g}: the gap is ours less theirs`, String(gaps[i])]);
  });
  return out;
}

/** The checks of one note's section: its table (rows of { text, link }) against the markdown's own count. */
async function noteRules(note, floor, head, rows, mdCount, ctx) {
  check(JSON.stringify(head) === JSON.stringify(COLUMNS), `${note}: the section's table has the five columns`, head.join(" | "));
  check(rows.length === mdCount && rows.length >= floor, `${note}: the table has the ${mdCount} rows of the note's markdown (never fewer than ${floor})`, `${rows.length} rows`);
  const bad = rows.filter((r) => !(r.length === 5 && r.every((x) => x.text.length > 0) && r[4].text.length > 30));
  check(bad.length === 0, `${note}: every row has our figure, the published figure, its source, the gap and a reason`, bad.map((r) => r[0]?.text.slice(0, 50)).join("; "));
  const byNote = [], noSource = [];
  for (const r of rows) {
    const s = r[2] ?? { text: "", link: false };
    if (s.link || s.text === "the same") continue;
    const named = [...s.text.matchAll(/docs\/methods\/([\w-]+)\.md/g)].map((m) => m[1]);
    if (named.length && (await Promise.all(named.map((x) => ctx.noteExists(x)))).every(Boolean)) byNote.push(`${r[0].text.slice(0, 40)}... (${named.join(", ")})`);
    else noSource.push(r[0].text.slice(0, 60));
  }
  check(noSource.length === 0, `${note}: every source is a link, "the same", or an ERW Method note that opens`, noSource.join("; "));
  for (const b of byNote) note_(`${note}: a source by an ERW Method note, not a publisher's link: ${b}`);
  const cells = rows.map((r) => r.map((x) => x.text));
  const tied = new Set();
  for (const f of FIGURES.filter((x) => x.note === note)) {
    const i = cells.findIndex((r) => r[0].includes(f.find));
    check(i >= 0, `${note}: the row "${f.find}" is in the table`);
    if (i < 0) continue;
    tied.add(i);
    console.log(`     ${f.key}`);
    let lines;
    try { lines = await f.test(cells[i], cells, ctx); } catch (e) { lines = [[false, "the row's figures could be read", String(e?.message ?? e)]]; }
    for (const [ok, what, detail] of lines) {
      if (ok === "held") note_(`${note}: ${what}: ${detail}`);
      else check(!!ok, `${note}: ${what}`, detail ?? "");
    }
  }
  cells.forEach((r, i) => { if (!tied.has(i)) note_(`${note}: names no figure by a key a check can read: ${r[0].slice(0, 70)}`); });
}

/** The reading context from the repository's files (--files, and a machine with no browser). */
function filesContext() {
  return {
    card: async (id) => JSON.parse(read("site", "data", "findings", `${id}.json`)),
    text: async (slug) => plain(read("docs", "methods", `${slug}.md`)),
    noteExists: async (slug) => fs.existsSync(path.join(ROOT, "docs", "methods", `${slug}.md`)),
    thesis: async (metric) => thesisFrom(mdTables(read("docs", "methods", "ercot_peak_premium.md")).map((t) => ({ head: t.head, rows: t.rows.map((r) => r.map((x) => x.text)) })), metric),
    replication: async () => read("site", "public", "grid", "erw_2026_grid_replication.csv"),
    figure: async () => [],
  };
}
/** The 2025 column of the thesis's table (ercot_peak_premium.md, "Thesis reproduction (HB_HUBAVG)": Metric, 2015, 2025). */
function thesisFrom(tables, metric) {
  const t = tables.find((x) => JSON.stringify(x.head) === JSON.stringify(["Metric", "2015", "2025"]));
  return t?.rows.find((r) => r[0] === metric)?.[2] ?? null;
}

async function checkFiles(ctx) {
  for (const { note, floor } of NOTES) {
    const md = read("docs", "methods", `${note}.md`);
    check(/<a id="cross-checks"><\/a>\s*\n\s*## Cross-checks/.test(md), `${note}: the note has its section "Cross-checks" at its anchor`);
    const sec = mdSection(md, "## Cross-checks");
    const t = sec ? mdTables(sec)[0] : null;
    if (!t) { check(false, `${note}: the section holds a table`); continue; }
    await noteRules(note, floor, t.head, t.rows, t.rows.length, ctx);
  }
}

if (FILES) {
  console.log(`check-cross-checks --files: the Grid's and Research's sections, read from ${ROOT}`);
  note_("the card pages' callouts are read on a built site only (run without --files)");
  await checkFiles(filesContext());
  console.log(failed ? `\ncheck-cross-checks --files FAILED: ${failed} of ${n}` : `\ncheck-cross-checks --files: all ${n} passed`);
  process.exit(failed ? 1 : 0);
}

const code = await withBrowser(async ({ go, evaluate, unlock, sleep }) => {
  await unlock(base);
  for (const [path, note] of PAGES) {
    await go(base + path);
    await sleep(1200);
    const line = await evaluate(`(() => { const e = document.querySelector("[data-checked-against]"); return e ? { n: Number(e.getAttribute("data-checked-against")), text: e.textContent.replace(/\\s+/g, " ").trim(), href: e.querySelector("a")?.getAttribute("href") ?? "" } : null; })()`);
    check(!!line && line.n > 0 && line.text.startsWith(`Checked against: ${line.n} published figures (`), `${path}: the source line says what the page was checked against`, line ? line.text : "no line");
    if (!line) continue;
    console.log(`     ${line.text}`);
    check(line.href === `/data/methods/${note}#cross-checks`, `${path}: the line links to its Method note's section`, line.href);
    await go(base + line.href);
    await sleep(800);
    const sec = await evaluate(`(() => {
      const a = document.getElementById("cross-checks");
      const h = [...document.querySelectorAll("h2")].find((x) => x.textContent.trim() === "Cross-checks");
      let t = h; while (t && t.tagName !== "TABLE") t = t.nextElementSibling;
      const rows = t ? [...t.querySelectorAll("tbody tr")].map((r) => [...r.children].map((c) => ({ text: c.textContent.trim(), link: !!c.querySelector('a[href^="https://"]') }))) : [];
      return { anchor: !!a, head: t ? [...t.querySelectorAll("thead th")].map((c) => c.textContent.trim()) : [], rows, review: !!document.querySelector("[data-in-review]") };
    })()`);
    check(sec.anchor && !sec.review, `${note}: the section "Cross-checks" is on the note, at its anchor`);
    check(JSON.stringify(sec.head) === JSON.stringify(["Our figure", "Published figure", "Source and date", "Gap", "Reason"]) && sec.rows.length === line.n, `${note}: the table has the ${line.n} rows the page counts`, `${sec.rows.length} rows`);
    check(sec.rows.every((r) => r.length === 5 && r.every((c) => c.text.length > 0) && r[4].text.length > 30), `${note}: every row has a gap and a reason`);
    check(sec.rows.every((r) => r[2].link || /ercot_storage_dam_awards_monthly/.test(r[2].text) || r[2].text === "the same"), `${note}: every published figure names where it was read`);
  }

  // session 538: the Grid tool's note and Research's, read on the built site
  let at = "";
  const open = async (p) => { if (at !== p) { await go(base + p); await sleep(800); at = p; } };
  const tablesJs = `[...document.querySelectorAll("article table")].map((t) => ({ head: [...t.querySelectorAll("thead th")].map((c) => c.textContent.replace(/\\s+/g, " ").trim()), rows: [...t.querySelectorAll("tbody tr")].map((r) => [...r.children].map((c) => c.textContent.replace(/\\s+/g, " ").trim())) }))`;
  const status = async (p) => evaluate(`fetch(${JSON.stringify(p)}, { cache: "no-store" }).then((r) => r.status)`);
  const ctx = {
    card: filesContext().card,   // the file the build bundles (lib/findings.ts reads site/data/findings at build)
    text: async (slug) => { await open(`/data/methods/${slug}`); return evaluate(`(document.querySelector("article")?.textContent ?? "").replace(/\\s+/g, " ")`); },
    noteExists: async (slug) => (await status(`/data/methods/${slug}`)) === 200,
    thesis: async (metric) => { await open("/data/methods/ercot_peak_premium"); return thesisFrom(await evaluate(tablesJs), metric); },
    replication: async () => evaluate(`fetch("/grid/erw_2026_grid_replication.csv", { cache: "no-store" }).then((r) => r.ok ? r.text() : "")`),
    figure: async (p, key, want, what) => {
      await open(p);
      const got = await evaluate(`(() => { const e = document.querySelector('[data-check="${key}"]'); if (e) return { text: e.textContent.trim() };
        const p = ${JSON.stringify(key)}.split("|"); const h = document.querySelector('[data-card="' + p[1] + '"] [data-callout="' + p[3] + '"]');
        return h && h.querySelector("[data-license-held]") ? { held: h.querySelector("[data-license-held]").textContent.trim() } : null; })()`);
      if (got?.held !== undefined) return [["held", `${what} (${p}, ${key})`, `held for a license, "${got.held}" in place: not compared`]];
      return [[got?.text === want, `${what} (${p}, ${key})`, `${got ? got.text : "no such figure on the page"} and ${want}`]];
    },
  };
  for (const { note, floor, page } of NOTES) {
    const md = read("docs", "methods", `${note}.md`);
    const mdRows = mdTables(mdSection(md, "## Cross-checks") ?? "")[0]?.rows.length ?? 0;
    await open(`/data/methods/${note}`);
    const sec = await evaluate(`(() => {
      const a = document.getElementById("cross-checks");
      const h = [...document.querySelectorAll("h2")].find((x) => x.textContent.trim() === "Cross-checks");
      let t = h; while (t && t.tagName !== "TABLE") t = t.nextElementSibling;
      const rows = t ? [...t.querySelectorAll("tbody tr")].map((r) => [...r.children].map((c) => ({ text: c.textContent.replace(/\\s+/g, " ").trim(), link: !!c.querySelector('a[href^="https://"]') }))) : [];
      return { anchor: !!a, head: t ? [...t.querySelectorAll("thead th")].map((c) => c.textContent.trim()) : [], rows, review: !!document.querySelector("[data-in-review]") };
    })()`);
    console.log(`     ${note} (the tool's page ${page}: no "Checked against" line, session 381's ruling item)`);
    check(sec.anchor && !sec.review, `${note}: the section "Cross-checks" is on the note, at its anchor`);
    await noteRules(note, floor, sec.head, sec.rows, mdRows, ctx);
  }
  return failed ? 1 : 0;
});
if (code === null) {
  console.log("no Chrome or Edge on this machine: the built pages are not proven here; the files are checked instead");
  await checkFiles(filesContext());
  console.log(failed ? `\ncheck-cross-checks FAILED: ${failed} of ${n}` : `\ncheck-cross-checks (files only): all ${n} passed`);
  process.exit(failed ? 1 : 0);
}
console.log(failed ? `\ncheck-cross-checks FAILED: ${failed} of ${n}` : `\ncheck-cross-checks: all ${n} passed`);
process.exit(code);
