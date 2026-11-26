// Session 10235 (docs/reviews/digest-model-audit-2026-11-26.md, finding 1): the hold that /roundup/<week> draws a stored
// Roundup with (lib/digest.ts holdRoundupGrids, called by lib/markdown.ts renderRoundup) on the newest Roundup, W45, as
// of 26 November 2026. Prints one JSON line. Run from site/: node --import ./scripts/tsx-register.mjs scripts/test-audit-digest-1.mjs
import fs from "node:fs";
import path from "node:path";

const D = await import("../lib/digest.ts");
const md = fs.readFileSync(path.join(process.cwd(), "..", "docs", "roundup", "2026-W45.md"), "utf-8");
const held = D.holdRoundupGrids(md, new Date("2026-11-26T00:00:00Z"));
console.log(JSON.stringify({ stored: ["40.90", "40.28"].map((x) => md.includes(x)), drawn: ["40.90", "40.28"].map((x) => held.includes(x)) }));
