// Energy Research Warehouse (ERW) site, ruling alternatives of Ask, the chat (session 7707, 17 November 2026;
// wip/alt-site-ask-* branches, not a default on main). The site chat's own functions run on rows made up here (no real
// row), so that the rule under the other choice is pinned with the site's code. On wip/alt-site-ask-1: keepRows leaves
// Berkeley Lab's rows in ISO-NE and NYISO out as held and its rows in MISO as paused, whether the region is read as
// region_held (a query) or inside extra (a description's sample).
//   node --import ./scripts/tsx-register.mjs scripts/alt-site-ask-figures.mjs
const H = await import("../lib/chat/heldrows.ts");
const rows = ["ISO-NE", "NYISO", "MISO", "PJM", "ERCOT"].map((r, i) => ({ id: `lbnl_queue:${i}`, region_held: r }));
const k = H.keepRows("lbnl_interconnection_queue", "entities", rows);
const x = H.keepRows("lbnl_interconnection_queue", "entities", [{ entity_id: "lbnl_queue:9", extra: { region: "NYISO" } }]);
process.stdout.write(JSON.stringify({ kept: k.kept.map((r) => r.region_held), held: k.held, paused: k.paused, fromExtra: { kept: x.kept.length, held: x.held } }));
