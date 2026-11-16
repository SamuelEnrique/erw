// Energy Research Warehouse (ERW) site, session 7537 (chain 304, part C): /map read as a developer checking what is
// planned within 30 miles of a candidate site, for five cases (docs/reviews/map-read-2026-11-16.md). The Projects tab
// is drawn to HTML by its own component on the page's own file (scripts/map-read-page.mjs), and each site fault the
// read found is held here as fixed: the row numbers are the review's. Every distance is computed again here with this
// file's own formula, from the file's latitudes and longitudes, and the page's rows are held to it. No server, no
// network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-map-read.mjs
import fs from "node:fs";
import { drawView, file as f, textOf } from "./map-read-page.mjs";

const L = await import("../lib/projectmap.ts");
const { MAP_DECISIONS } = await import("../app/map/Decisions.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const src = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf-8");

// this test's own distance: the haversine formula on a sphere of 3,958.8 miles, written again, not imported
const R = 3958.8, rad = (d) => (d * Math.PI) / 180;
const miles = (a, b, c, d) => 2 * R * Math.asin(Math.sqrt(Math.sin(rad(c - a) / 2) ** 2 + Math.cos(rad(a)) * Math.cos(rad(c)) * Math.sin(rad(d - b) / 2) ** 2));
const within = (la, lo, mi, kinds) => {
  const out = [];
  for (let i = 0; i < f.k.length; i++) {
    if (kinds && !kinds.includes(f.k[i])) continue;
    if (f.la[i] === null || f.lo[i] === null) continue;
    const d = miles(la, lo, f.la[i], f.lo[i]);
    if (d <= mi) out.push({ i, d });
  }
  return out.sort((x, y) => x.d - y.d || x.i - y.i);
};

// the five cases: a named place, its point, the kinds the developer asks for (what is planned: planned units, queue
// positions and datacenters)
const PLANNED = "kind=planned,queue,datacenter";
const CASES = [
  { n: 1, place: "Abilene, Texas (Taylor County, ERCOT)", la: 32.4487, lo: -99.7331 },
  { n: 2, place: "Amarillo, Texas (Potter County)", la: 35.222, lo: -101.8313 },
  { n: 3, place: "New Albany, Ohio (PJM)", la: 40.0812, lo: -82.8088 },
  { n: 4, place: "Mason City, Iowa (MISO)", la: 43.1536, lo: -93.201 },
  { n: 5, place: "Bakersfield, California (Kern County, CAISO)", la: 35.3733, lo: -119.0187 },
];
const views = {};
for (const c of CASES) {
  const address = `?${PLANNED}&at=${c.la},${c.lo}&within=30`;
  const html = drawView(address);
  views[c.n] = { address, html, text: textOf(html), mine: within(c.la, c.lo, 30, [1, 2, 3]) };
}
const rowsOf = (html) => [...html.matchAll(/data-near-miles="(\d+)">([\d,.]+)</g)].map((m) => ({ i: Number(m[1]), shown: Number(m[2].replace(/,/g, "")) }));

// ---- row 1: a point and a distance, in the address and in the choice
const c1 = L.parseChoice("?at=32.4487,-99.7331&within=30", f);
ok(c1.at === "32.4487,-99.7331" && c1.within === "30" && L.queryOf(c1, f) === "?at=32.4487,-99.7331&within=30", "row 1: the address keeps a point and a distance and gives them back");
ok(L.parseChoice("?at=north&within=ten", f).at === "" && L.parseChoice("?at=north&within=ten", f).within === "", "row 1: words are no point and no distance");
ok(L.pointOf("32.4487, -99.7331")?.lo === -99.7331 && L.pointOf("91, 0") === null && L.pointOf("0, 181") === null, "row 1: a point is typed as latitude, longitude, inside the globe");
ok(L.select(f, L.parseChoice("?at=32.4487,-99.7331", f)).length === f.k.length && L.select(f, L.parseChoice("?within=30", f)).length === f.k.length, "row 1: a point alone or a distance alone chooses nothing");
ok(L.parseChoice("", f).at === "" && L.select(f, L.parseChoice("", f)).length === f.k.length, "row 1: with no point every row is chosen, as before");
for (const c of CASES) {
  const picked = L.select(f, L.parseChoice(views[c.n].address, f));
  const mine = views[c.n].mine.map((r) => r.i).sort((a, b) => a - b);
  ok(JSON.stringify(picked) === JSON.stringify(mine), `row 1, case ${c.n} (${c.place}): the page chooses the same ${mine.length} rows as this test's own distance`);
}
const ab = L.select(f, L.parseChoice("?kind=planned,queue&at=32.4487,-99.7331&within=30", f));
ok(ab.filter((i) => f.k[i] === 1).length === 9 && ab.filter((i) => f.k[i] === 2).length === 38, "row 1, case 1: within 30 miles of Abilene, 9 planned units and 38 queue positions");
ok(views[1].text.includes("In every grid and every state, within 30 miles of 32.4487, -99.7331, the map holds 9 planned units of EIA's inventory of 2026-09, 2,232 MW; and 38 queue positions, 11,559 MW requested"), "row 1, case 1: the sentence says the distance and its figures");
ok(views[1].html.includes('data-map-choice="at"') && views[1].html.includes('data-map-choice="within"') && views[1].html.includes('data-tip="map-near"'), "row 1: the panel has the point, the distance and the tip that says how it is measured");
const near = { la: 32.4487, lo: -99.7331, miles: 30 };
ok(L.circleOf(near).every((p) => Math.abs(miles(near.la, near.lo, p.la, p.lo) - 30) < 0.01), "row 1: the circle drawn is 30 miles from the point all round");
ok(MAP_DECISIONS.some((d) => d.key === "near" && d.source.includes("3,958.8")) && src("../../docs/methods/map.md").includes("?at=32.4487,-99.7331&within=30"), "row 1: the distance is a line of the decisions block and of the note");

// ---- row 2: the rows within the distance, by name, nearest first
for (const c of CASES) {
  const v = views[c.n], got = rowsOf(v.html);
  const same = got.length === v.mine.length && got.every((r, k) => r.i === v.mine[k].i && Math.abs(r.shown - v.mine[k].d) <= 0.05 + 1e-9);
  ok(same, `row 2, case ${c.n}: the list holds the ${v.mine.length} rows nearest first, each distance inside half a tenth of a mile of this test's`);
}
ok(/data-near-name="\d+">Summerhill BESS</.test(views[1].html) && rowsOf(views[1].html)[0].shown === 5.7, "row 2, case 1: the nearest is Summerhill BESS, 5.7 miles, a planned battery of 143 MW (2028-12)");
ok(views[3].text.includes("4.1 | Flint | Planned unit | Batteries | Under construction, half or less complete | 200.0 | 2027-07 (planned operation) | exact coordinates"), "row 2, case 3: Flint, a 200 MW battery under construction 4.1 miles from New Albany, planned for 2027-07");
ok(views[4].html.includes('data-map-near-none="1"'), "row 2, case 4: within 30 miles of Mason City the list says no row is chosen");
ok(views[1].text.includes("(entered the queue)") && views[1].text.includes("(planned operation)"), "row 7: the list's date says what it is: a queue's date of entry is not a planned operation date");
ok(src("../app/map/ProjectMap.tsx").includes("`, ${dateOf(f.d[i])} (${DATE_WORDS[kind]})`") && L.DATE_WORDS.length === 4, "row 7: the mark's hover says what its date is too");

// ---- row 3: the queues the map holds none of are named where a reader meets their absence
ok(views[4].text.includes("Queue positions are those of ERCOT, CAISO, SPP and ISO-NE alone: no queue position of PJM, MISO or NYISO is on this map."), "row 3, case 4: Mason City's empty answer says MISO's queue is not on the map");
ok(views[3].html.includes('data-map-queues-drawn="1"'), "row 3, case 3: New Albany's says PJM's is not");
ok(!drawView("?kind=queue&grid=ercot").includes('data-map-queues-drawn="1"') && !drawView("?kind=operating").includes('data-map-queues-drawn="1"'), "row 3: not said when only a grid with its queue, or no queue position, is chosen");

// ---- row 4: a queue position is measured from its county's point; the list and the note say so
const kern = views[5];
ok(kern.html.includes('data-map-near-county="1">89<') && /89 of the 89 queue positions are measured from their county's or town's point/.test(kern.text), "row 4, case 5: 89 of the 89 queue positions near Bakersfield are at a county's or town's point, and the list says so");
ok(rowsOf(kern.html).filter((r) => f.k[r.i] === 2).every((r) => r.shown === 16.4), "row 4, case 5: every one of them stands 16.4 miles off, at Kern County's one point");
ok([...kern.html.matchAll(/data-near-placed="(\d+)">([^<]*)</g)].every((m) => m[2] === L.PLACED_AT[f.pr[Number(m[1])]]), "row 4: each row's \"Placed at\" is its file's precision code");

// ---- row 5: ERCOT's "Completed" in plain words
const statuses = [...views[1].html.matchAll(/data-near-status="(\d+)">([^<]*)</g)];
const ercotDone = statuses.filter((m) => f.k[Number(m[1])] === 2 && f.statuses[f.st[Number(m[1])]].slug === "q-completed");
ok(ercotDone.length === 14 && ercotDone.every((m) => m[2].startsWith("Agreement signed, built or not")), "row 5, case 1: ERCOT's 14 completed positions near Abilene read \"Agreement signed, built or not\"");
ok([...kern.html.matchAll(/data-near-status="(\d+)">([^<]*)</g)].some((m) => m[2] === "Completed"), "row 5, case 5: CAISO's completed positions keep the word");
ok(views[1].text.includes("For ERCOT's positions, \"Completed\" is a signed interconnection agreement, built or not"), "row 5: the tip of the queue's tiles says it too");

// ---- row 6: a card's point as the point of the distance
ok(src("../app/map/ProjectMap.tsx").includes("data-card-measure") && src("../app/map/ProjectMap.tsx").includes("measure={(at) => change((c) => ({ ...c, at }))}"), "row 6: a row's card offers its point as the point of the distance");

// nothing else moved: the tab with no point draws no list
ok(!drawView("").includes('id="near"') && !drawView("?kind=planned").includes('data-near-miles'), "the tab with no point draws no list, as before");

const EM = String.fromCharCode(0x2014), EN = String.fromCharCode(0x2013);
for (const p of ["../app/map/ProjectMap.tsx", "../lib/projectmap.ts", "../app/map/Decisions.tsx", "./map-read-page.mjs", "./test-map-read.mjs", "../../docs/methods/map.md"]) ok(!src(p).includes(EM) && !src(p).includes(EN), `no dash in ${p}`);

console.log(`\n${n - failed} of ${n} passed`);
process.exitCode = failed ? 1 : 0;
