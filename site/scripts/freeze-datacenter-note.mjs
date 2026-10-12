// Energy Research Warehouse (ERW) site, session 199: the inputs of the figures that
// docs/methods/datacenter_pays_algorithm.md quotes, frozen as one small dated file.
//
//   cd site
//   node --import ./scripts/alias-register.mjs scripts/freeze-datacenter-note.mjs
//   node --import ./scripts/alias-register.mjs scripts/freeze-datacenter-note.mjs --data C:/.../site/data/datacenter --root C:/scratch
//
// Why (the owner's ruling of 11 October 2026): the note is a dated document. It says which day's files it quotes, and
// the page's files are rebuilt by the data machine's run every day. A test that a landing must pass never compares a
// committed figure with the day's files; it recomputes the note's figures from this file with the page's own library
// (tests/test_session190.py) and with the second implementation of the rule (tests/test_session190_replication.py).
// Run this when the note's examples are written again from newer files, and name the new file in the note.
//
// What is kept, for the default case (the grid's main load zone, bought in real time) and nothing else:
//   index    the part of data/datacenter/index.json the default inputs and the tight hours of 2025 are read from
//   months   every month of the zone in real time for a flat load, as lib/datacenter.ts monthsOf() gives it (the sum
//            of the hourly prices held, the hours held and due: no hourly price), and the hub's months of the last
//            twelve: the worked table, the twelve months, the hub beside the zone, the bad month of 36, the years
//   years    the hours a flexible load's figures cannot do without: the zone's real-time and day-ahead prices of the
//            two calendar years the last twelve months lie in (the year's budget of hours and the hours "if perfectly
//            foreseen" are chosen over a whole calendar year), and the day-ahead prices of the 30 days before them
//            (the rule's threshold reads the prior 30 days)
// It refuses to write unless the flexible load's figures from the kept hours equal, to the last digit, the figures
// from the whole files, for the note's four loads under the rule and foreseen.
//
// Written to docs/methods/figures/<the day the index was built>/datacenter_pays_inputs.json. No request, no table.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const L = await import("../lib/datacenter.ts");
const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const arg = (name, d) => (args.indexOf(name) >= 0 ? args[args.indexOf(name) + 1] : d);
const DATA = path.resolve(arg("--data", path.join(here, "..", "data", "datacenter")));
const ROOT = path.resolve(arg("--root", path.join(here, "..", "..")));
const NAME = "datacenter_pays_inputs.json";
const read = (f) => JSON.parse(fs.readFileSync(path.join(DATA, f), "utf-8"));

const INDEX = read("index.json");
const x = L.inputsOf({}, INDEX);
const g = INDEX.grids[x.grid];
const zone = g.regions.find((r) => r.id === x.region);
if (!zone?.ref) throw new Error(`the default region ${x.region} names no hub beside it`);
const F = g.years.map((y) => read(`${x.grid}_${y}.json`));
const FLAT = { run: "flat", n: 0, pct: 0, shift: 0 };
const ms = L.monthsOf(F, x.region, x.buy, FLAT), l12 = L.lastTwelve(ms);
if (!l12) throw new Error("the default case holds no twelve consecutive complete months");
const hub = L.monthsOf(F, zone.ref, "rt", FLAT).filter((r) => r.m >= l12[0].m && r.m <= l12[11].m);

// the calendar years the last twelve months lie in, whole, and the 30 days of day-ahead prices before them
const first = Number(l12[0].m.slice(0, 4)), last = Number(l12[11].m.slice(0, 4));
const by = new Map(F.map((f) => [f.year, f]));
const slim = (f) => ({ grid: f.grid, year: f.year, hours: f.hours, built: f.built,
  regions: { [x.region]: { rt: f.regions[x.region].rt, da: f.regions[x.region].da } }, tight: f.tight ?? [] });
const before = by.get(first - 1);
if (!before) throw new Error(`the year ${first - 1} is not held: the rule's first threshold of ${first} cannot be frozen`);
const span30 = 24 * L.PRIOR_DAYS;
const tail = { grid: before.grid, year: before.year, hours: before.hours, built: before.built,
  regions: { [x.region]: { da: { s: before.hours - span30, v: L.expand(before, x.region, "da").slice(before.hours - span30) } } }, tight: [] };
const years = [tail];
for (let y = first; y <= last; y++) years.push(slim(by.get(y)));

// the kept hours must give the flexible load's figures of the whole files
const LOADS = [["rt", { run: "hours", n: 100, pct: 0, shift: 0 }], ["da", { run: "hours", n: 100, pct: 0, shift: 0 }],
  ["rt", { run: "shift", n: 0, pct: 0, shift: 20 }], ["da", { run: "shift", n: 0, pct: 0, shift: 20 }], ["rt", { run: "share", n: 0, pct: 5, shift: 0 }]];
const figure = (files, buy, c, rule) => { const t = L.lastTwelve(L.monthsRuled(files, x.region, buy, c, rule).months);
  const s = L.span(t); return JSON.stringify([t[0].m, t[11].m, s.flat, s.per, s.cost, s.energy, s.down, s.held]); };
for (const [buy, c] of LOADS) for (const rule of ["forecast", "hindsight"]) {
  const whole = figure(F, buy, c, rule), kept = figure(years, buy, c, rule);
  if (whole !== kept) throw new Error(`${buy} ${JSON.stringify(c)} ${rule}: the kept hours give ${kept}, the whole files ${whole}; nothing written`);
}
const again = L.monthsOf(years, x.region, x.buy, FLAT).filter((r) => r.m >= `${first}-01`);
if (JSON.stringify(again) !== JSON.stringify(ms.filter((r) => r.m >= `${first}-01`))) throw new Error("the kept hours do not give the kept months; nothing written");

const out = {
  _about: "Energy Research Warehouse (ERW), session 199. The inputs of the figures that docs/methods/datacenter_pays_algorithm.md quotes, as the page's files " +
    `(site/data/datacenter) held them in the build of ${INDEX.built}: the default case alone (${g.name}, ${x.region}, bought in real time). index: the part of ` +
    "index.json read. months: each month of a flat load as site/lib/datacenter.ts monthsOf() gives it (flat is the sum of the hourly prices held, USD per MWh). " +
    `years: the zone's hourly real-time and day-ahead prices of ${first} to ${last} in the page files' own shape (s is the first hour held, counted from the ` +
    `year's first hour in ${g.std_name}; v the prices from there, USD per MWh), and the day-ahead prices of the last ${L.PRIOR_DAYS} days of ${first - 1}. ` +
    "Written by site/scripts/freeze-datacenter-note.mjs; not edited by hand. The page reads the day's files, not this one",
  note: "docs/methods/datacenter_pays_algorithm.md",
  built: INDEX.built,
  case: { grid: x.grid, region: x.region, buy: x.buy, hub: zone.ref, last_twelve: [l12[0].m, l12[11].m] },
  index: { built: INDEX.built, grids: { [x.grid]: { name: g.name, std_hours_behind_utc: g.std_hours_behind_utc, std_name: g.std_name, main: g.main,
    years: years.map((f) => f.year), regions: [zone], demand: { "2025": g.demand["2025"] } } } },
  months: { [`${x.region}/${x.buy}`]: ms, [`${zone.ref}/rt`]: hub },
  years,
};
const file = path.join(ROOT, "docs", "methods", "figures", INDEX.built.slice(0, 10), NAME);
fs.mkdirSync(path.dirname(file), { recursive: true });
fs.writeFileSync(file, "{\n" + Object.entries(out).map(([k, v]) => ` ${JSON.stringify(k)}: ${JSON.stringify(v)}`).join(",\n") + "\n}\n");
console.log(`wrote ${path.relative(ROOT, file).replaceAll("\\", "/")}: ${fs.statSync(file).size} bytes; built ${INDEX.built}; last twelve months ${l12[0].m} to ${l12[11].m}; ` +
  `${ms.length} months of ${x.region}, ${hub.length} of ${zone.ref}; hours of ${first} to ${last} and the last ${L.PRIOR_DAYS} days of ${first - 1}; ` +
  `${LOADS.length * 2} figures of a flexible load equal from the kept hours and from the whole files`);
