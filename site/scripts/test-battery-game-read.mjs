// Energy Research Warehouse (ERW) site, session 7551 (chain 304, part B): the read of the home battery game
// (/play/battery) as a student, a new analyst and a teacher would bring it (docs/reviews/battery-game-read-2026-11-16.md).
// Its site rows, drawn to HTML with the site's own components and checked.
//   node --import ./scripts/tsx-register.mjs scripts/test-battery-game-read.mjs
// 1. Row 1: the money in detail is drawn on Easy too; on Winter Storm Uri's day the perfect play's line names the fleet
//    bonus (USD 44.98 of 240.23), with its hover saying it is a game rule.
// 2. Row 2: the real-battery sentence: the trades' own money per kW (USD 39.05 for the perfect play on Uri's day, Easy),
//    the link to the battery page, and the battery page's stress-day rules (hourly, from empty, one cycle, 86 percent).
// 3. Row 3: a day's address (?day=uri or ?day=2021-02-15), the address kept on a change of mode, and the day's link.
// 4. Row 4: the fleet section draws CAISO beside ERCOT, each with its four check keys, and says both are the latest
//    inventory; drawn from storage_capacity as this machine holds it (the main copy's warehouse/output), when it is there.
// 5. Row 5: ECRS, Non-Spin and Base Point Deviation each carry a hover in the page's source.
// 6. No row or figure of a license-held grid (ISO-NE, MISO, NYISO) in the read file or in the fleet section.
// Exit 1 on any failure. No request, nothing written.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const lib = await import("../lib/battery.ts");
const G = await import("../app/play/battery/Game.tsx");
const F = await import("../app/play/battery/RealFleet.tsx");
const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf-8")).levels
  .map((l) => ({ ...l, grid: l.grid ?? "ERCOT", tz: l.tz ?? "America/Chicago" }));
let bad = 0, n = 0;
const ok = (cond, what) => { n++; if (cond) console.log(`ok   ${what}`); else { bad++; console.log(`FAIL ${what}`); } };
const words = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1").trim();

// 1 and 2. Uri's day, Easy, the perfect play
const uri = levels.find((l) => l.slug === "uri");
const r = lib.rulesOf(lib.DEFAULT_SETTINGS, "easy", []);
const best = lib.optimum(uri.price, r, undefined);
const perfect = lib.simulate(uri.price, best.actions, r, undefined);
const html = renderToStaticMarkup(h(G.EndDetail, { result: { mine: perfect, rules: r, preset: lib.presetOf(lib.DEFAULT_SETTINGS, "easy", []) }, perfect, easy: true, server: "" }));
const t = words(html);
ok(t.startsWith("In detail: $195.25 in the market, plus the fleet bonus $44.98."), `row 1: Easy draws the money in detail (${t.slice(0, 70)})`);
ok(html.includes('data-bonus-hover="1"') && /title="A game rule: in the fleet call&#x27;s hour/.test(html), "row 1: the fleet bonus carries its hover, a game rule");
ok(t.includes("Your fleet of 10,000 homes: $2,402,273.97; the perfect battery's fleet: $2,402,273.97."), "row 1: the fleet line unchanged");
ok(t.includes("Per kW of this battery's 5 kW, your trades netted $39.05 and the perfect battery's $39.05 (the market's money alone: no fleet bonus)."), "row 2: the trades per kW, Easy (no wear clause)");
ok(html.includes('href="/cost-of-power/battery"'), "row 2: the link to the battery page");
for (const w of ["2, 4 or 8 hours", "ancillary services, which the game does not hold", "hourly prices", "from an empty battery", "one cycle a day at most", "86 percent round trip", "not the same measure"])
  ok(t.includes(w), `row 2: the battery page's rules said: "${w}"`);
// Hard: the wear clause, and the per kW figures are the trades alone
const rh = lib.rulesOf(lib.DEFAULT_SETTINGS, "hard", []);
const bh = lib.optimum(uri.price, rh, undefined);
const ph = lib.simulate(uri.price, bh.actions, rh, undefined);
const th = words(renderToStaticMarkup(h(G.EndDetail, { result: { mine: ph, rules: rh, preset: lib.presetOf(lib.DEFAULT_SETTINGS, "hard", []) }, perfect: ph, easy: false, server: "" })));
const perKw = (v) => `$${(v / 5).toFixed(2)}`;
ok(th.includes(`your trades netted ${perKw(ph.cash)} and the perfect battery's ${perKw(ph.cash)} (the market's money alone: no fleet bonus, before wear).`), `row 2: Hard says "before wear" (${perKw(ph.cash)})`);
ok(th.includes("The rules: "), "Hard keeps its rules line");

// 3. the day's address
ok(G.dayIndex(levels, "uri") === levels.findIndex((l) => l.slug === "uri"), "row 3: ?day=uri opens Winter Storm Uri");
ok(G.dayIndex(levels, "2023-08-10") === levels.findIndex((l) => l.slug === "heat"), "row 3: ?day=2023-08-10 opens the summer scarcity day");
ok(G.dayIndex(levels, "caiso-duck") === levels.findIndex((l) => l.slug === "caiso-duck"), "row 3: ?day=caiso-duck opens the CAISO duck day");
ok(G.dayIndex(levels, "nope") === 0 && G.dayIndex(levels, undefined) === 0, "row 3: an unknown or absent day opens the first level");
ok(G.gameAddress("/play/battery", "easy", "today") === "/play/battery", "row 3: Easy, today: the bare address");
ok(G.gameAddress("/play/battery", "hard", "uri") === "/play/battery?mode=hard&day=uri", "row 3: Hard on Uri's day keeps both");
ok(G.gameAddress("/play/battery", "easy", "caiso-duck") === "/play/battery?day=caiso-duck", "row 3: Easy on the duck day");
const dl = renderToStaticMarkup(h(G.DayLink, { mode: "normal", level: uri }));
ok(dl.includes('href="/play/battery?mode=normal&amp;day=uri"') && words(dl).includes("The link to Winter Storm Uri, 2021-02-15"), "row 3: the day's link drawn");
const dt = renderToStaticMarkup(h(G.DayLink, { mode: "easy", level: { slug: "today", date: "2026-11-15", title: "Today's level" } }));
ok(dt.includes('href="/play/battery"') && words(dt).includes("The link to today's level") && dt.includes("opens on a newer day tomorrow"), "row 3: today's link says it moves");
const page = fs.readFileSync(new URL("../app/play/battery/page.tsx", import.meta.url), "utf-8");
ok(page.includes('initialDay={typeof q.day === "string" ? q.day : undefined}'), "row 3: the page hands the address's day to the game");

// 4. the fleet section, from storage_capacity as the main copy holds it
const CSV = "C:/Users/lossa/Documents/erw/warehouse/output/storage_capacity.csv";
if (fs.existsSync(CSV)) {
  const lines = fs.readFileSync(CSV, "utf-8").split("\n").filter((x) => x && !x.startsWith("#"));
  const parse = (line) => { const o = []; let cur = "", q = false; for (const c of line) { if (c === '"') q = !q; else if (c === "," && !q) { o.push(cur); cur = ""; } else cur += c; } o.push(cur.replace(/\r$/, "")); return o; };
  const head = parse(lines[0]);
  const at = (k) => head.indexOf(k);
  const units = lines.slice(1).map(parse).map((x) => ({ entity_id: x[at("entity_id")], capacity_mw: x[at("capacity_mw")] === "" ? null : Number(x[at("capacity_mw")]), status: x[at("status")], iso: x[at("iso")] || null, mwh: x[at("energy_capacity_mwh")] || null }))
    .filter((u) => u.iso === "ERCOT" || u.iso === "CAISO");  // the two grids the section draws: no held grid's row is read
  const fh = renderToStaticMarkup(h(F.RealFleet, { units }));
  const ft = words(fh);
  const e = F.fleetOf(units, "ERCOT"), c = F.fleetOf(units, "CAISO");
  ok(e.mw === 18204.5 && e.n === 259, `row 4: ERCOT ${e.mw} MW in ${e.n} units (the storage page and the awards page's read: 18,204.5 in 259)`);
  ok(c.mw === 17094.2 && c.n === 310, `row 4: CAISO ${c.mw} MW in ${c.n} units`);
  for (const iso of ["ERCOT", "CAISO"]) for (const k of ["iso_mw", "iso_n", "iso_mwh", "iso_n_mwh"])
    ok(fh.includes(`storage|${k}|${iso}|operating`), `row 4: ${iso}'s ${k} carries its check key`);
  ok(fh.includes("calc|ratio|storage~iso_mw~CAISO~operating|battery~fleet_mw") && fh.includes("calc|ratio|storage~iso_mw~ERCOT~operating|battery~fleet_mw"), "row 4: both ratios carry their keys");
  ok(ft.includes("ERCOT's real fleet has 364.09 times") && ft.includes("CAISO's real fleet has 341.88 times"), "row 4: the two ratios");
  ok((fh.match(/the latest inventory/g) ?? []).length === 2 && fh.includes("not on the day the game replays"), "row 4: both cards say they are the latest inventory, not the day played");
  ok(!/ISO-NE|MISO|NYISO/.test(fh), "6: no held grid in the fleet section");
} else {
  console.log(`skip row 4: ${CSV} is not on this machine`);
}

// 5. the words a student would not know
ok(/title="ERCOT Contingency Reserve Service[^"]*">ECRS</.test(page), "row 5: ECRS on hover");
ok(/title="Non-Spinning Reserve[^"]*">Non-Spin</.test(page), "row 5: Non-Spin on hover");
ok(/title="ERCOT&apos;s charge on a resource[^"]*">Base Point Deviation</.test(page) || /title="ERCOT's charge on a resource[^"]*">Base Point Deviation</.test(page), "row 5: Base Point Deviation on hover");
ok(page.includes("balancing authority is ERCOT or CAISO, in the EIA's latest monthly inventory"), "row 4: the source line names both grids");

// 6. no held row or figure in the read file
const READ = new URL("../../docs/reviews/battery-game-read-2026-11-16.md", import.meta.url);
if (fs.existsSync(READ)) {
  const md = fs.readFileSync(READ, "utf-8");
  ok(!/\b(isone|miso|nyiso):/i.test(md), "6: the read file holds no entity of a held grid");
  ok(!md.includes(String.fromCharCode(0x2014)), "the read file holds no em dash");
}

console.log(`\n${n - bad} of ${n} checks passed`);
process.exitCode = bad ? 1 : 0;
