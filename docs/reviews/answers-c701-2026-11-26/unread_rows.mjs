// Chain 701, part E3: the rows of /cost-of-power?view=allgrids whose large-load cell says "no large-load rule read" or
// "no large-load rule found", computed with the tab's own code (app/cost-of-power/LargeLoadSection.tsx, rulesOfRow) on
// the hub rows (lib/siting.ts, hubRows) and the files main holds. Reads files only.
//   cd site && node --import ./scripts/alias-register.mjs ../runs/c701/unread_rows.mjs
const S = await import("../../site/lib/siting.ts");
const D = await import("../../site/lib/sitingdata.ts");
const LL = await import("../../site/lib/largeloadrules.ts");
const L = { rulesOfRow: (r) => { const { state, utilities } = S.rowUtilities(D.SITING_FILES, r); return { ...LL.rowRules(D.LARGE_LOAD, utilities, state, r.grid), state }; } };  // as LargeLoadSection.rulesOfRow
const rows = S.hubRows(D.SITING_FILES.index);
let unread = 0, none = 0, own = 0, statewide = 0;
for (const r of rows) {
  const rr = L.rulesOfRow(r);
  const kind = rr.own.length ? "own" : rr.statewide.length ? "state" : rr.none.length ? "none found" : "none read";
  if (kind === "own") own++; else if (kind === "state") statewide++; else if (kind === "none found") none++; else unread++;
  if (kind === "none read" || kind === "none found" || rr.unread.length)
    console.log(`${kind.padEnd(10)} | ${S.GRID_NAMES[r.grid]} ${r.label} | state ${rr.state} | unread: ${rr.unread.map((u) => u.name).join("; ")} | none: ${rr.none.map((n) => n.name).join("; ")}`);
}
console.log(`rows ${rows.length}: own rule ${own}, state rule only ${statewide}, none found ${none}, none read ${unread}`);
