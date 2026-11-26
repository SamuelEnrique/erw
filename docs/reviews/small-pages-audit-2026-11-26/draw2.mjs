// Session 10238: the two method notes this audit changes (docs/methods/resources.md, docs/methods/attention.md), read
// fresh from the branch's files and rendered as the site renders a note (lib/markdown.ts, render). Run from site/:
//   node --import ../runs/c10238/register.mjs ../runs/c10238/draw2.mjs <out prefix> [needle ...]
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [prefix, ...needles] = process.argv.slice(2);
const site = process.cwd();
const { render } = await import(pathToFileURL(path.join(site, "lib", "markdown.ts")).href);
const ent = (s) => s.replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
let text = "";
for (const name of ["resources", "attention"]) {
  const html = render(fs.readFileSync(path.join(site, "..", "docs", "methods", `${name}.md`), "utf-8"), `docs/methods/${name}.md`, { under: true });
  fs.writeFileSync(`${prefix}_${name}_note.html`, html);
  text += " " + words(html);
  console.log(`${name}: ${html.length} bytes rendered; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
}
let fail = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { console.log(`MISSING: ${n}`); fail = 1; continue; }
  const a = Math.max(0, text.lastIndexOf(". ", i) + 2), b = text.indexOf(". ", i + n.length);
  console.log(`FOUND: ${text.slice(a, b < 0 ? i + n.length + 80 : b + 1).slice(0, 500)}`);
}
process.exitCode = fail;
