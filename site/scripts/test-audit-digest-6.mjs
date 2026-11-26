// Session 10235 (docs/reviews/digest-model-audit-2026-11-26.md, finding 6): what of a stored issue's stories the pages
// draw while news_index is held (lib/license.ts, "license needed" whole since 21 October 2026), as of 26 November 2026.
// The Digest of 12 November through lib/digest.ts digestMarkdown (its story sections held); the Roundup of W45 through
// holdRoundupGrids (no story held). Prints one JSON line. Run from site/:
//   node --import ./scripts/tsx-register.mjs scripts/test-audit-digest-6.mjs
import fs from "node:fs";
import path from "node:path";

const D = await import("../lib/digest.ts");
const L = await import("../lib/license.ts");
const now = new Date("2026-11-26T00:00:00Z");
const read = (...p) => fs.readFileSync(path.join(process.cwd(), "..", ...p), "utf-8");
const dg = D.digestMarkdown(read("docs", "digest", "2026-11-12.md"), "2026-11-12", null, now).md;
const rd = D.holdRoundupGrids(read("docs", "roundup", "2026-W45.md"), now);
console.log(JSON.stringify({
  news_index_held: L.licenseNeeded("news_index", now),
  digest_story_sections_held: (dg.match(/the stories of this section come from the news index/g) ?? []).length,
  digest_opening_story_shown: /SpaceX plans USD 74 billion in data center projects in Arizona and Texas, as Bloomberg\.com reported/.test(dg),
  // the figure itself is a keyed span's placeholder in this markdown (ERWDIGESTFIG<n>Z); the row around it is the story's
  digest_block_story_rows_shown: [/Storage capacity, USA: ERWDIGESTFIG\d+Z MW \(Sunrun, Tesla; pv magazine USA/.test(dg), /Deal value: ERWDIGESTFIG\d+Z \(Strathcona, Greenfire; JPT Homepage/.test(dg)],
  roundup_story_items_shown: (rd.match(/^\d+\. \*\*/gm) ?? []).length,
  roundup_google_news_links_shown: (rd.match(/news\.google\.com/g) ?? []).length,
  roundup_says_held: /news index/.test(rd),
}));
