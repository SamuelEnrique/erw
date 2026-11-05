// Energy Research Warehouse (ERW) site, session 419: three faults of session 401's list (docs/reviews/tooling-pass-2026-10-20.md).
// The research rule's percentile as an ordinal (lib/ordinal.ts); the carbon note's year from the page's own twelve
// months, not the reader's clock (lib/datacenter/answers.ts, yearOfThrough); the fold an address names, opened
// (lib/foldhash.ts). No request, no browser, no model.
//
//   node --import ./scripts/alias-register.mjs scripts/test-session419.mjs
//
// Prints one line per assertion; exits 1 if any fails.
const O = await import("../lib/ordinal.ts");
const F = await import("../lib/foldhash.ts");
const A = await import("../lib/datacenter/answers.ts");

let failed = 0, n = 0;
const ok = (cond, what) => { n += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed += 1; };

// 1. the ordinal
const want = { 1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 10: "10th", 11: "11th", 12: "12th", 13: "13th", 21: "21st", 22: "22nd", 23: "23rd", 100: "100th", 101: "101st", 111: "111th", 112: "112th", 0: "0th" };
for (const [k, v] of Object.entries(want)) ok(O.ordinal(Number(k)) === v, `${k} is written ${v}`);
ok(O.ordinal(13.4) === "13.4th" && O.ordinal(21.1) === "21.1st" && O.ordinal(42.2) === "42.2nd" && O.ordinal(99.9) === "99.9th", "a decimal takes its last digit's suffix");
ok(O.ordinal(11.5) === "11.5th" && O.ordinal(12.3) === "12.3rd", "a decimal between 11 and 13 is not a whole 11 to 13");

// 2. the year of the page's twelve months
ok(A.yearOfThrough("2026-09") === 2026, "the page's last month gives its year");
ok(A.yearOfThrough("2025-12") === 2025, "December of the year before stays that year whatever the clock says");
ok(A.yearOfThrough(null) === null && A.yearOfThrough(undefined) === null && A.yearOfThrough("") === null && A.yearOfThrough("Sept") === null, "no month, no year");

// 3. the fold an address names
ok(F.idOfHash("#financing") === "financing" && F.idOfHash("financing") === "financing", "the hash names its id");
ok(F.idOfHash("") === null && F.idOfHash("#") === null, "no hash, no id");
ok(F.idOfHash("#a%20b") === "a b" && F.idOfHash("#%E0%A4%A") === "%E0%A4%A", "an encoded id is read; a broken one is kept as written");
const fold = { open: false };
const el = (tag, closest, child) => ({ tagName: tag, closest: () => closest, querySelector: () => child });
ok(F.foldFor(el("DETAILS", null, null)) !== null && F.foldFor(Object.assign(el("details", null, null), { open: false })).open === false, "a fold named by its own id is that fold");
ok(F.foldFor(el("DIV", fold, null)) === fold, "an element inside a fold opens the fold it sits in");
ok(F.foldFor(el("DIV", null, fold)) === fold, "a wrapper whose first child is a fold opens that fold (the battery's #financing)");
ok(F.foldFor(el("DIV", null, null)) === null && F.foldFor(null) === null, "an element with no fold opens nothing");

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
