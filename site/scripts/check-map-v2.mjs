// Energy Research Warehouse (ERW) site, session 105: the project map, version 2, in a real browser.
//
// Session 167: /map is one page and /map/v2 redirects to it. This check now runs the one page's check,
// scripts/check-map.mjs (the redirect with its query carried over is its second check). Version 2's own check, as it
// stood, is in git history (session 105 to session 166).
//
//   node scripts/check-map-v2.mjs [base-url]      (default http://localhost:3167)
await import("./check-map.mjs");
