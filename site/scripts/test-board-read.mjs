// Energy Research Warehouse (ERW) site, session 7538 (chain 304, part C): the price board (/board) read as a trader or a
// fund analyst checking the morning's prices across hubs, gas and carbon against the day before and a year before
// (docs/reviews/board-read-2026-11-16.md). The board is drawn to HTML with the page's own components on the site's own
// file after the page's own hold of the day (lib/board.ts, holdRows), and on copies of it changed in memory where a rule
// needs a date placed (each says so). No server, no network, nothing written. It holds the read's site rows:
//   row 1: a stale close in the headline strip says "(stale)" with its age on hover, as its tile and its row do;
//   row 4: the strip's lowest and highest grid count the grids compared and name them, and the grids not on the board;
//   row 5: the strip's two range cells give their value's date;
//   row 8: the week table's "RT minus DA" says its sign against the group "Day-ahead minus real time" (equal and opposite);
//   row 9: a week-table volatility measured more than 3 days before the build is marked stale;
//   row 10: the formula mark "f" says what it is on hover;
// and that the upgrade drops nothing and draws no figure of a held grid.
//   node --import ./scripts/tsx-register.mjs scripts/test-board-read.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const B = await import("../lib/board.ts");
const { BoardView } = await import("../components/board/BoardView.tsx");
const { gridName, licenseHeldGrids } = await import("../lib/license.ts");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const unesc = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const text = (html) => unesc(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const raw = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf-8"));
const held = licenseHeldGrids().map(gridName);
const file = B.holdRows(raw, held);
const draw = (f) => renderToStaticMarkup(h(BoardView, { file: f }));
const html = draw(file), words = text(html);
const cell = (doc, k) => { const m = doc.match(new RegExp(`<button[^>]*data-head-cell="${k}"[^>]*>([\\s\\S]*?)</button>`)); return m ? { tag: m[0].slice(0, m[0].indexOf(">") + 1), text: text(m[1]) } : null; };
const titleOf = (tag) => unesc((tag.match(/title="([^"]*)"/) ?? [, ""])[1]);
const copy = () => JSON.parse(JSON.stringify(file));
const shift = (t, days) => new Date(Date.parse(`${t.slice(0, 10)}T00:00:00Z`) + days * 86400000).toISOString().slice(0, 10);

// ---- row 1: the headline strip's closes, against the same rule as the tile (closeAge)
for (const id of ["eia-henry-hub-spot", "eia-wti-cushing-spot", "eia-brent-spot", "erw-brent-minus-wti"]) {
  const r = file.rows.find((x) => x.id === id && x.status === "ok");
  if (!r) { ok(!cell(html, id), `row 1: ${id} is not on the file and the strip draws no cell for it`); continue; }
  const age = B.closeAge(r, file.built), c = cell(html, id);
  ok(!!c && c.text.includes(B.dateWords(r.last.t)) && c.text.includes("(stale)") === !!age.stale && /data-head-stale=/.test(c.tag) === !!age.stale,
    `row 1: ${id} on the site's file: "${B.dateWords(r.last.t)}"${age.stale ? " (stale)" : ""}, as its tile says`);
  ok(titleOf(c.tag).includes(age.words), `row 1: ${id}: the age's words on hover ("${age.words.slice(0, 40)}...")`);
}
{
  // made up in memory: Henry Hub's close moved to 20 days before the build, then to the build's day
  const f = copy(), r = f.rows.find((x) => x.id === "eia-henry-hub-spot");
  r.last = { ...r.last, t: shift(f.built, -20) };
  const c = cell(draw(f), "eia-henry-hub-spot");
  ok(c.text.includes(`${B.dateWords(r.last.t)} (stale)`) && /data-head-stale="eia-henry-hub-spot"/.test(c.tag) && titleOf(c.tag).includes("Stale: a daily series is marked stale past 10 days"),
    "row 1: a close 20 days before the build reads \"(stale)\" in the strip, with the method's threshold on hover");
  r.last = { ...r.last, t: f.built.slice(0, 10) };
  const d = cell(draw(f), "eia-henry-hub-spot");
  ok(!d.text.includes("stale") && !/data-head-stale=/.test(d.tag), "row 1: a close of the build's day carries no stale mark");
}

// ---- row 4: the lowest and highest grid
for (const market of ["da"]) {
  const ex = B.gridExtremes(file, market);
  const low = cell(html, "low"), high = cell(html, "high");
  ok(ex && low.text.trim().startsWith(`Lowest of ${ex.grids} grids, day-ahead`) && high.text.trim().startsWith(`Highest of ${ex.grids} grids, day-ahead`),
    `row 4: the strip says "Lowest of ${ex?.grids} grids" and "Highest of ${ex?.grids} grids" (it said "Lowest grid")`);
  const t = titleOf(high.tag);
  ok(ex.priced.every((g) => t.includes(g)) && t.includes(`Among the main hubs of the ${ex.grids} grids priced on ${B.dateWords(ex.day)}: ${ex.priced.join(", ")}`),
    `row 4: the hover names the grids compared: ${ex.priced.join(", ")}`);
  ok((file.held ?? []).every((g) => t.includes(`${g} (license needed)`)) && t.includes("MISO (paused while its terms are reviewed)") && t.includes("PJM (licensed source needed)"),
    "row 4: the hover names the grids not on the board, each in the page's own status words");
  ok(ex.priced.every((g) => !/^(ISO-NE|NYISO|MISO|PJM)$/.test(g)), "row 4: no held or paused grid is among those compared");
  ok(!t.includes(".."), "row 4: the hover reads as sentences (no double stop)");
}
ok(B.gridExtremesWords({ day: "2026-11-16", grids: 1, priced: ["ERCOT"] }, ["NYISO"]) === "Among the main hubs of the 1 grid priced on 16 Nov 2026: ERCOT. Not on the board: NYISO (license needed), MISO (paused while its terms are reviewed), PJM (licensed source needed).",
  "row 4: the words for one grid, pure");

// ---- row 5: the range cells' dates
{
  const rx = B.rangeExtremes(file);
  for (const [k, r] of [["top", rx.top], ["bottom", rx.bottom]]) {
    const c = cell(html, k), d = B.headDate(r, file.built);
    ok(c.text.includes(`${r.label}, ${r.at}, ${d.words}:`) && c.text.includes("of the way up"), `row 5: the ${k} range cell gives its value's date ("${r.label}, ${r.at}, ${d.words}")`);
  }
}

// ---- row 8: the week table's sign
{
  const th = html.match(/<th[^>]*data-week-sign="1"[^>]*>/);
  ok(!!th && titleOf(th[0]).includes("Real time less day-ahead") && titleOf(th[0]).includes("its 7-day avg is this figure with its sign turned"), "row 8: \"RT minus DA, week\" says its order and the group's opposite order on hover");
  // the claim on the site's file: each public hub's week figure is the group's 7-day avg with its sign turned, on the same 7 days
  let pairs = 0, agree = 0;
  for (const w of file.week) {
    const m = w.means.da_rt_spread_mean_usd, r = file.rows.find((x) => x.id === `${w.hub}-da-minus-rt` && x.status === "ok");
    if (!m || !r?.avg7 || r.avg7.n !== 7 || r.last.t !== m.end) continue;
    pairs++; if (Math.abs(m.v + r.avg7.v) <= 0.0002) agree++;
  }
  ok(pairs > 0 && agree === pairs, `row 8: on the site's file the week's RT minus DA is minus the group's 7-day avg for ${agree} of ${pairs} hubs held on the same 7 days`);
}

// ---- row 9: the week table's volatility
{
  const vols = file.week.filter((w) => w.vol);
  const staleOnes = vols.filter((w) => B.weekStale(w.vol.t, file.built));
  ok(vols.every((w) => html.includes(`data-week-stale="${w.hub}|vol"`) === !!B.weekStale(w.vol.t, file.built)), `row 9: a volatility older than 3 days is marked stale on the site's file (${staleOnes.length} of ${vols.length})`);
  const f = copy();
  f.week = f.week.map((w) => (w.vol ? { ...w, vol: { ...w.vol, t: f.built.slice(0, 10) } } : w));
  ok(!draw(f).includes("data-week-stale="), "row 9: made up in memory, every volatility dated the build's day: no stale mark");
  f.week = f.week.map((w) => (w.vol ? { ...w, vol: { ...w.vol, t: shift(f.built, -4) } } : w));
  const four = draw(f);
  ok(f.week.filter((w) => w.vol).every((w) => four.includes(`data-week-stale="${w.hub}|vol"`)) && four.includes("Stale: a market&#x27;s daily figure is marked stale past 3 days"), "row 9: made up in memory, 4 days before the build: every volatility marked, the threshold on hover");
  ok(B.weekStale("2026-11-13", "2026-11-16T19:08:45Z") === null && B.weekStale("2026-11-12", "2026-11-16T19:08:45Z") !== null, "row 9: 3 days is current, 4 days is stale (the power groups' rule), pure");
}

// ---- row 10: the formula mark
{
  const marks = [...html.matchAll(/<sup[^>]*data-formula-mark="([^"]*)"[^>]*>f<\/sup>/g)];
  const formulaRows = file.rows.filter((r) => r.formula && B.rowsOf(file, file.groups.find((g) => g.id === r.group), {}).includes(r));
  ok(marks.length > 0 && marks.every((m) => titleOf(m[0]) === "A formula of other rows of the board: the formula is in the name's hover."), `row 10: every "f" says what it is on hover (${marks.length} marks)`);
  ok(!/<sup[^>]*>f<\/sup>/.test(html.replace(/<sup[^>]*data-formula-mark="[^"]*"[^>]*>f<\/sup>/g, "")), "row 10: no \"f\" without its hover");
  ok(formulaRows.length > 0, `row 10: the file holds formula rows in its groups' default views (${formulaRows.length})`);
}

// ---- nothing dropped, nothing held drawn
ok((html.match(/data-head-cell=/g) ?? []).length === 8, "the strip keeps its eight cells");
ok(html.includes("The twelve numbers to check first") && words.includes("Click any row to open it in the markets workbench") && words.includes("Hours RT over DA + 50") && words.includes("30-day volatility"),
  "the page's other parts are drawn as before");
const heldIds = file.rows.filter((r) => r.status === "license").map((r) => r.id);
ok(heldIds.length > 0 && heldIds.every((id) => !html.includes(`data-n="${id}|`)), `no figure of a held row is drawn (${heldIds.length} held rows, none with a marked figure)`);
ok(!/—/.test(html), "no em dash in the drawn page");

console.log(`\n${n - failed} of ${n} passed`);
process.exitCode = failed ? 1 : 0;
