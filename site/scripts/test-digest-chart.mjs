// Energy Research Warehouse (ERW) site, session 232: the Digest's chart of the day on the digest's page.
// warehouse/news/brief.py writes "![...](charts/<date>.png)" into docs/digest/<date>.md; lib/markdown.ts points it at
// /digest-charts/<date>.png, where scripts/build-content.mjs copies the picture.
//
//   node --import ./scripts/alias-register.mjs scripts/test-digest-chart.mjs      (needs content/docs.json: npm run content)
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const { render } = await import("../lib/markdown.ts");
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };

test("the chart of a digest is an image served by the site", () => {
  const html = render("## ERW's Chart of the Day\n\n![A fact](charts/2026-10-13.png)\n\nA fact.\n", "docs/digest/2026-10-13.md");
  assert.ok(/<img src="\/digest-charts\/2026-10-13\.png" alt="A fact"/.test(html), html);
});

test("the same link in latest.md points at the same picture", () => {
  const html = render("![A fact](charts/2026-10-13.png)\n", "docs/digest/latest.md");
  assert.ok(html.includes('src="/digest-charts/2026-10-13.png"'), html);
});

test("only a dated picture of docs/digest/charts is served from there", () => {
  for (const other of ["charts/notes.txt", "charts/2026-10-13.json", "charts/../2026-10-13.png", "email/2026-10-13.png"]) {
    const html = render(`![x](${other})\n`, "docs/digest/2026-10-13.md");
    assert.ok(!html.includes("/digest-charts/"), `${other} -> ${html}`);
  }
});

test("every picture in docs/digest/charts was copied by the build", () => {
  const from = path.join(here, "..", "..", "docs", "digest", "charts");
  const to = path.join(here, "..", "public", "digest-charts");
  const want = fs.existsSync(from) ? fs.readdirSync(from).filter((f) => /^\d{4}-\d{2}-\d{2}\.png$/.test(f)).sort() : [];
  const have = fs.existsSync(to) ? fs.readdirSync(to).sort() : [];
  assert.deepEqual(have, want);
});

console.log(`${n} tests passed`);
