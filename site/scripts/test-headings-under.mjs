// Energy Research Warehouse (ERW) site, session 9818: a document drawn inside a page that has its own title has its
// headings set one level down (lib/markdown.ts, render's `under`), so the page keeps one h1 and no level is skipped.
//
//   node --import ./scripts/alias-register.mjs scripts/test-headings-under.mjs
//
// Needs site/node_modules (the renderer imports marked). Exits 1 on the first failure.
import assert from "node:assert/strict";

const { render, headingsUnder } = await import("../lib/markdown.ts");

let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };
const md = "# The note\n\nWords.\n\n## A part\n\n### A step\n\n###### The deepest\n";

await test("as it was without the option", () => {
  const h = render(md, "docs/methods/x.md");
  assert.match(h, /<h1[\s>]/);
  assert.match(h, /<h2[\s>]/);
});

await test("one level down with under: no h1, an h2 where the h1 was, h6 kept", () => {
  const h = render(md, "docs/methods/x.md", { under: true });
  assert.doesNotMatch(h, /<h1[\s>]/);
  assert.match(h, /<h2[^>]*>The note<\/h2>/);
  assert.match(h, /<h3[^>]*>A part<\/h3>/);
  assert.match(h, /<h4[^>]*>A step<\/h4>/);
  assert.match(h, /<h6[^>]*>The deepest<\/h6>/);
});

await test("only heading tags move", () => {
  assert.equal(headingsUnder('<p>h1 and <hr> <h1 id="a">x</h1><header>y</header></p>'), '<p>h1 and <hr> <h2 id="a">x</h2><header>y</header></p>');
});

console.log(`${n} passed`);
