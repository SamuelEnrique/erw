// Energy Research Warehouse (ERW) site, session 7541 (chain 304, part C): /supply drawn whole to HTML by its own page
// function (app/supply/page.tsx), without building the site. The page reads no live table: every figure is in the
// site's own file (data/supply.json), held for a license on the day by the page itself (lib/supply.ts, holdRows). No
// network, nothing written but the caller's out files, no click, no chart seen. Used by scripts/test-supply-read.mjs,
// and on its own:
//   node --import ./scripts/battery-awards-page-register.mjs scripts/supply-read-page.mjs <out.html> <out.txt> [query]
// The text is the page as a reader meets it (a table row's cells joined by " | ", a hover as "[title: ...]";
// scripts/battery-awards-page.mjs, pageText). Neither out file is committed.
import fs from "node:fs";
import { pathToFileURL } from "node:url";
import { prerenderToNodeStream } from "react-dom/static";
import { pageText } from "./battery-awards-page.mjs";

/** The page as the server draws it for an address's query ("g=burn&s=eia-wcestus1", or "" for the whole page). */
export async function drawSupply(query = "") {
  const { default: Supply } = await import("../app/supply/page.tsx");
  const q = Object.fromEntries(new URLSearchParams(query));
  const el = await Supply({ searchParams: Promise.resolve(q) });
  const { prelude } = await prerenderToNodeStream(el);
  let html = "";
  for await (const c of prelude) html += c.toString();
  return html;
}

/** The HTML of one table row, by its data-row id. */
export function rowHtml(html, id) {
  const at = html.indexOf(`data-row="${id}"`);
  if (at < 0) return "";
  const end = html.indexOf("</tr>", at);
  return html.slice(at, end < 0 ? undefined : end);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [outHtml, outTxt, query = ""] = process.argv.slice(2);
  if (!outHtml || !outTxt) { console.error("usage: supply-read-page.mjs <out.html> <out.txt> [query]"); process.exitCode = 2; }
  else {
    const html = await drawSupply(query);
    const text = pageText(html);
    fs.writeFileSync(outHtml, html);
    fs.writeFileSync(outTxt, text + "\n");
    console.log(`${html.length} bytes of HTML; ${text.split("\n").length} lines of text`);
  }
}
