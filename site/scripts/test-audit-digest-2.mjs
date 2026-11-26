// Session 10235 (docs/reviews/digest-model-audit-2026-11-26.md, finding 2): lib/digest.ts roundupDue at the edges of a
// week's Sunday 23:00 UTC, and the ISO weeks of the Roundups held. Prints one JSON line. Run from site/:
//   node --import ./scripts/tsx-register.mjs scripts/test-audit-digest-2.mjs
const D = await import("../lib/digest.ts");
const at = (s) => new Date(s);
console.log(JSON.stringify({
  w47_on_26_nov: D.roundupDue("2026-W47", at("2026-11-26T12:00:00Z")),
  w46_on_26_nov: D.roundupDue("2026-W46", at("2026-11-26T12:00:00Z")),
  w48_on_26_nov: D.roundupDue("2026-W48", at("2026-11-26T12:00:00Z")),
  w47_before: D.roundupDue("2026-W47", at("2026-11-22T22:59:59Z")),
  w47_at: D.roundupDue("2026-W47", at("2026-11-22T23:00:00Z")),
  w01_2027_before: D.roundupDue("2027-W01", at("2027-01-10T22:59:00Z")),
  w01_2027_at: D.roundupDue("2027-W01", at("2027-01-10T23:00:00Z")),
  w53_2026_at: D.roundupDue("2026-W53", at("2027-01-03T23:00:00Z")),
  not_a_week: D.roundupDue("2026-11-21", at("2027-01-01T00:00:00Z")),
}));
