// Session 10209: the board's week table drawn to HTML with the site's own code (BoardView, holdRows), no build.
// node --import ./scripts/tsx-register.mjs ../runs/c10209/draw_week.mjs <out file>   (run from site/)
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const { createElement: h } = await import(pathToFileURL(req.resolve("react")).href);
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const B = await import(pathToFileURL(path.join(site, "lib", "board.ts")).href);
const { BoardView } = await import(pathToFileURL(path.join(site, "components", "board", "BoardView.tsx")).href);
const raw = JSON.parse(fs.readFileSync(path.join(site, "data", "board.json"), "utf-8"));
const html = renderToStaticMarkup(h(BoardView, { file: B.holdRows(raw, ["NYISO", "ISO-NE", "MISO", "PJM"]) }));
const start = html.indexOf('<section id="week"');
const end = html.indexOf("</section>", start);
const week = html.slice(start, end + 10);
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const titles = [...week.matchAll(/title="([^"]*)"/g)].map((m) => unq(m[1]));
const text = unq(week.replace(/<[^>]+>/g, " ").replace(/\s+/g, " "));
const counts = {};
for (const t of titles) counts[t] = (counts[t] || 0) + 1;
const lines = [`week section: ${week.length} characters; em dashes in it: ${week.split(String.fromCharCode(0x2014)).length - 1}`, "", "== hovers (count, words)"];
for (const [t, n] of Object.entries(counts)) if (!/^Code: |^the 7 days to |^\d|^as of |^[A-Z][a-z]+ \d|interval starting/.test(t)) lines.push(`${n}x ${t}`);
lines.push("", "== visible text", text);
fs.writeFileSync(process.argv[2], lines.join("\n"));
console.log(`written ${process.argv[2]}: ${titles.length} hovers`);
