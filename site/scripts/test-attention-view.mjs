// Session 1880: the attention faults of 12 November 2026 (docs/reviews/attention-faults-2026-11-11.md), the pure part of
// /attention's view (lib/attention.ts), on the file the page reads (data/attention.json, built 2026-11-06T20:52:23Z)
// and its week files (public/attention/stories/<monday>.json). No build, no network.
//   node --import ./scripts/alias-register.mjs scripts/test-attention-view.mjs
import { readFileSync } from "node:fs";

const A = await import("../lib/attention.ts");
const { STATES } = await import("../lib/regions.ts");
const f = JSON.parse(readFileSync(new URL("../data/attention.json", import.meta.url), "utf-8"));
const weekFile = (monday) => {
  const j = JSON.parse(readFileSync(new URL(`../public/attention/stories/${monday}.json`, import.meta.url), "utf-8"));
  return j.rows.map((r) => Object.fromEntries(j.columns.map((c, i) => [c, r[i]])));
};
let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const wi = (d) => f.weeks.findIndex((w) => w.slice(0, 10) === d);
const si = (k) => f.sectors.indexOf(k);
const cellOf = (s, g, w) => f.cells.find((c) => c[0] === s && c[1] === f.geos.indexOf(g) && c[2] === w);

ok(f.built === "2026-11-06T20:52:23Z", `the file read is the one of the faults read (built ${f.built})`);
const W1102 = wi("2026-11-02"), W1116 = wi("2026-11-16"), W1005 = wi("2026-10-05"), W1026 = wi("2026-10-26");

// row 1: the list under the United States is the stories that name a state, not every story of the sector
const s1102 = weekFile("2026-11-02");
const dcAll = s1102.filter((s) => A.inCell(s, "datacenters", "all"));
const dcUs = s1102.filter((s) => A.inCell(s, "datacenters", "US"));
ok(dcAll.length === 63 && dcAll.length === cellOf(0, "all", W1102)[3], "row 1: data centers, every story, 2026-11-02: the list is the cell's 63");
ok(dcUs.length === 13 && dcUs.every((s) => s.state !== ""), `row 1: under the United States the list is the 13 stories that name a state (was 63), of the cell's ${cellOf(0, "US", W1102)[3]}`);
ok(dcUs.length < cellOf(0, "US", W1102)[3], "row 1: the list is a part of the cell, and the note counts it against the cell");
ok(!A.hasUsFlag(s1102), "row 1: the week file carries no us flag yet (row 2, the data machine's)");
const flagged = [{ ...s1102[0], sector: "datacenters", state: "", us: 1 }, { ...s1102[0], sector: "datacenters", state: "TX", us: 0 }];
ok(A.hasUsFlag(flagged) && flagged.filter((s) => A.inCell(s, "datacenters", "US")).length === 1 && A.inCell(flagged[0], "datacenters", "US"),
  "row 1: with the us flag the list follows it (a story with us=1 and no state is in, one with us=0 and a state is out)");
ok(s1102.filter((s) => A.inCell(s, "datacenters", "all", true)).length === cellOf(0, "all", W1102)[5], "row 1: only the stories reporting opposition: the cell's 19");

// row 3: no week after the build's week
ok(A.buildMonday(f.built) === "2026-11-02", "row 3: the build's Monday is 2026-11-02");
ok(!A.inBuild(f, W1116) && A.inBuild(f, W1102), "row 3: the week of 2026-11-16 is after the build's week, 2026-11-02 is not");
ok(!A.cellWeeks(f, 0, 0).includes(W1116) && A.cellWeeks(f, 0, 0).at(-1) === W1102, "row 3: the picker does not offer 2026-11-16 for data centers, every story; its last week is 2026-11-02");
ok(!A.spanOf(f).includes(W1116) && A.spanOf(f).at(-1) === W1102, "row 3: the charts' span ends at 2026-11-02 as before");
ok(A.openingWeek(f) === W1102, "row 3: the page opens on 2026-11-02");
ok(f.sectors.every((_, s) => f.geos.every((_, g) => !A.cellWeeks(f, s, g).some((w) => w > W1102))), "row 3: no cell of the file offers a week after the build's");

// row 4: the week that holds the build is partial
ok(A.holdsBuild(f, W1102) && A.isPartial(f, W1102), "row 4: the week of 2026-11-02 holds the build (Sunday 2026-11-08 after 2026-11-06) and is partial");
ok(!A.isPartial(f, W1026), "row 4: the week of 2026-10-26 is whole and fully judged: not partial");
ok(A.isPartial(f, W1005) && !A.holdsBuild(f, W1005), "row 4: the week of 2026-10-05 is partly classified (2,798 of 3,110 judged), not the build's");
ok(A.weekWords(f, W1102) === " (to 2026-11-06)" && A.weekWords(f, W1005) === " (partly classified)" && A.weekWords(f, W1026) === "", "row 4: the picker says (to 2026-11-06), (partly classified) or nothing");
const onSunday = { ...f, built: "2026-11-08T23:00:00Z" };
ok(!A.holdsBuild(onSunday, W1102), "row 4: a file built on the week's Sunday does not make the week partial");
ok(A.spanOf(f).map((i) => A.isPartial(f, i)).filter(Boolean).length === 2, "row 4: of the five weeks drawn two are hatched, 2026-10-05 and 2026-11-02 (was the week of 2026-11-30, not drawn)");

// row 5: the chosen week stays among the cell's weeks
const va = A.cellWeeks(f, 0, f.geos.indexOf("US-VA"));
ok(va.join() === [wi("2026-10-05"), wi("2026-10-12"), wi("2026-10-19"), W1026].join(), "row 5: data centers, Virginia, has the weeks 2026-10-05 to 2026-10-26");
ok(A.chooseWeek(va, W1102) === W1026, "row 5: from 2026-11-02 the week moves to the cell's latest, 2026-10-26");
ok(A.chooseWeek(va, W1005) === W1005, "row 5: a week the cell has stays");
ok(A.chooseWeek([], W1102) === W1102 && JSON.stringify(A.weekOptions([], W1102)) === JSON.stringify([{ i: W1102, none: true }]), "row 5: a cell with no week keeps the week, offered and marked no story");
ok(A.weekOptions(va, W1005).every((o) => !o.none) && A.weekOptions(va, W1005).length === 4, "row 5: the options are the cell's weeks when it has the chosen one");

// row 6: a missing cell is one line, with no unit
ok(A.noCellLine("datacenters", "US-VA", f.weeks[W1102], STATES) === "No story of data centers named Virginia in the week of 2026-11-02", "row 6: data centers, Virginia, 2026-11-02: one line");
ok(A.noCellLine("energy", "all", f.weeks[W1102], STATES) === "No energy story in the week of 2026-11-02" && A.noCellLine("nuclear", "US", f.weeks[W1102], STATES) === "No story of nuclear about the United States in the week of 2026-11-02", "row 6: the line under All energy and under the United States");
ok(!cellOf(0, "US-VA", W1102), "row 6: the file holds no cell for data centers, Virginia, 2026-11-02");

// row 8: every key of the rising rows, the places and the footer reads back its value; each figure has its source
let keys = 0, wrong = 0;
for (const w of A.spanOf(f)) {
  const r = A.risingOf(f, w);
  for (const x of r.sectors) for (const [fld, v] of [["mean_before", x.before], ["change", x.change], ["this", x.this]]) { keys++; if (A.attentionStat(f, A.risingKey(f.weeks[w], "sector", x.key, fld)) !== v) wrong++; }
  for (const x of r.states) for (const [fld, v] of [["mean_before", x.before], ["change", x.change]]) { keys++; if (A.attentionStat(f, A.risingKey(f.weeks[w], "state", x.key, fld)) !== v) wrong++; }
  for (const s of f.sectors.map((_, i) => i)) for (const p of A.placesOf(f, w, s)) for (const fld of ["stories", "opposition"]) { keys++; if (A.attentionStat(f, A.placeKey(f.weeks[w], f.sectors[s], p, fld)) !== p[fld]) wrong++; }
}
ok(keys > 500 && wrong === 0, `row 8: ${keys} keys of the rising rows and the places read back their value from the file (${wrong} wrong)`);
ok(["stories", "opposition", "weeks_with_stories"].every((k) => A.attentionStat(f, A.fileKey(k)) === f.counts[k]) && f.counts.stories === 8120 && f.counts.opposition === 254, "row 8: the footer's 8,120, 254 and 6 weeks are keyed");
ok(A.attentionStat(f, "attention_rising|2026-11-02|sector|nosuch|change") === null && A.attentionStat(f, "attention_place|1999-01-04|energy|x|y|stories") === null, "row 8: a key of no row reads null");
ok(f.places.every((p) => !String(p[1]).includes("|") && !String(p[2]).includes("|")), "row 8: no place name holds the key's separator");
const src = [A.seriesSource(f.built, A.ATT, "attention:datacenters:all", "attention_index", f.weeks[W1102]), A.risingSource(f.built, f.weeks[W1102], "sector", "datacenters", "change"),
  A.placeSource(f.built, f.weeks[W1102], "energy", { place: "Houston", state: "TX" }, "stories"), A.fileSource(f.built, "stories")];
ok(src.every((s) => s.includes("warehouse/derived/attention_index.py, run 2026-11-06 20:52 UTC")), "row 8: each source names the builder and its run");
ok(src[0] === "attention_index_weekly, attention:datacenters:all, attention_index, week of 2026-11-02; warehouse/derived/attention_index.py, run 2026-11-06 20:52 UTC", "row 8: a series figure's source: table, entity, variable, week, run");
ok(A.seriesKey(A.ATT, "attention:datacenters:all", "stories", f.weeks[W1102]) === "series|attention_index_weekly|attention:datacenters:all|stories|2026-11-02T00:00:00Z", "row 8: the existing series keys are unchanged");

// row 9: the map as a table, keyed
const m = A.mapRows(f, 0, W1102, "attention");
const wy = m.find((r) => r.code === "WY");
ok(m.length === f.states.filter((s) => cellOf(0, "US-" + s, W1102)).length && m.length > 0, `row 9: the table lists the ${m.length} states with a data center story in the week of 2026-11-02`);
ok(wy && wy.cell.stories === 3 && A.pct(wy.cell.attention) === "0.48" && wy.cell.opposition === 1 && A.pct(wy.cell.friction) === "33.33", "row 9: Wyoming: 3 stories, 0.48, 1 reporting opposition, 33.33, as the map's hover");
ok(m.every((r, i) => i === 0 || m[i - 1].cell.attention >= r.cell.attention), "row 9: largest Attention Index first");
const mf = A.mapRows(f, 0, W1102, "friction");
ok(mf.every((r, i) => i === 0 || mf[i - 1].cell.friction >= r.cell.friction), "row 9: largest Friction Index first under that measure");

// rows 10 and 11: the places, summed under All energy, and each opens its stories
const E = si("energy");
const p1005 = A.placesOf(f, W1005, E);
ok(p1005.filter((p) => p.place === "Houston" && p.state === "TX").length === 1 && p1005.find((p) => p.place === "Houston").stories === 4, "row 11: 2026-10-05, All energy: Houston, TX once, 4 stories (1, 1 and 2 of three sectors)");
let dup = 0;
for (const w of A.spanOf(f)) { const ps = A.placesOf(f, w, E); if (new Set(ps.map((p) => `${p.place}|${p.state}`)).size !== ps.length) dup++; }
ok(dup === 0, "row 11: no week lists a place twice under All energy");
ok(A.placesOf(f, W1005, si("transmission")).every((p) => f.places.some((x) => x[0] === si("transmission") && x[3] === W1005 && x[1] === p.place && x[4] === p.stories)), "row 11: under one sector the rows are the sector's own");
const s1005 = weekFile("2026-10-05");
let mism = 0;
for (const s of [E, si("datacenters"), si("oil_lng")]) for (const p of A.placesOf(f, W1005, s)) {
  if (s1005.filter((x) => A.inCell(x, f.sectors[s], "all", false, p)).length !== p.stories) mism++;
  if (s1005.filter((x) => A.inCell(x, f.sectors[s], "all", true, p)).length !== p.opposition) mism++;
}
ok(mism === 0, "row 10: each place row of 2026-10-05 (all energy, data centers, oil and LNG) opens a list of its own stories and opposition count");
ok(s1005.filter((x) => A.inCell(x, "energy", "all", false, { place: "Houston", state: "TX" })).length === 4, "row 10: Houston, TX opens its 4 stories");
const va1019 = weekFile("2026-10-19").filter((x) => A.inCell(x, "energy", "US-VA"));
ok(va1019.length === cellOf(E, "US-VA", wi("2026-10-19"))[3], "row 10: a state row opens the state's cell under All energy (Virginia, 2026-10-19: 9)");

console.log(`\n${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
