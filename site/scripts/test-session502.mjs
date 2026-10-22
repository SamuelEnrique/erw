// Energy Research Warehouse (ERW) site, session 502: the license line's words (lib/license.ts, licenseWords), read on a
// day before the holds (2026-10-20) and on a day after (2026-10-22). No request, no browser, no model.
//
//   node --import ./scripts/alias-register.mjs scripts/test-session502.mjs
//
// Prints one line per assertion; exits 1 if any fails.
const L = await import("../lib/license.ts");
const G = await import("../lib/gridtables.ts");

let failed = 0, n = 0;
const ok = (cond, what) => { n += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed += 1; };
const before = new Date("2026-10-20T12:00:00Z"), after = new Date("2026-10-22T12:00:00Z");

ok(L.licenseWords("eia930_all_demand", after) === "public", "a table the record does not hold is public");
ok(L.licenseWords("news_index", after) === "held: license needed", "a table held whole: held, license needed");
ok(L.licenseWords("iso_dam_hub_prices", after) === "held for MISO: license needed", "a table held by grid names its grid");
ok(L.licenseWords("price_board_latest", after) === "held for ISO-NE, MISO, NYISO: license needed", "several grids, in the record's order");
ok(L.licenseWords("news_index", before) === "public" && L.licenseWords("iso_dam_hub_prices", before) === "public", "before the record's day nothing is held");
ok(L.licenseWords("no_such_table", after) === "public", "a name the record does not hold reads public (the python test keeps such names off the lines)");

const views = Object.keys(G.GRID_VIEW_TABLES).sort().join(",");
ok(views === "clean,gravity,mix,network", "every view of the Grid tool has its list");
for (const [v, ts] of Object.entries(G.GRID_VIEW_TABLES)) ok(ts.length > 0 && new Set(ts).size === ts.length, `the ${v} view's list has no repeat`);

console.log(`\n${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
