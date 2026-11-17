// Energy Research Warehouse (ERW) site, session 7545 (chain 304, part C): the page /queues drawn to HTML without a
// build. The page's own function (app/queues/page.tsx) is called with an address's choices; it reads only the site's
// own file (data/queues.json, Berkeley Lab and GridTracker's Queued Up, CC BY 4.0), so no read is stood in for.
// No network, no table written, no click, no chart seen.
//
//   node --import ./scripts/battery-awards-page-register.mjs scripts/queues-page.mjs <grid> <tech> <out.txt> [out.html]
//
// out.txt is the page as a reader meets it, one line a block: a table row's cells joined by " | ", a bar's hover as
// "[hover]", a tip as "[tip]", and a cell's own hover as "[title]".
// A test imports drawQueues and pageText (scripts/test-queues-read.mjs).
import fs from "node:fs";
import { pathToFileURL } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";

/** The page drawn for the address ?grid=<grid>&tech=<tech> (either may be left out). */
export async function drawQueues(q = {}) {
  const { default: Queues } = await import("../app/queues/page.tsx");
  return renderToStaticMarkup(await Queues({ searchParams: Promise.resolve(q) }));
}

const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
/** The drawn page as lines of text, with every hover kept and marked. */
export function pageText(html) {
  const t = html
    .replace(/<title>([\s\S]*?)<\/title>/g, "\n[hover] $1\n")
    .replace(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span><\/span>/g, "\n[tip] $1\n")
    .replace(/<(span|abbr|a)[^>]* title="([^"]*)"[^>]*>/g, " [title: $2] ")
    .replace(/<\/(th|td)>/g, " | ")
    .replace(/<(h1|h2|h3|p|li|tr|caption|summary|figcaption|section|nav|aside|svg)([ >])/g, "\n<$1$2")
    .replace(/<[^>]+>/g, " ");
  return ent(t).split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [grid, tech, outTxt, outHtml] = process.argv.slice(2);
  if (!grid || !tech || !outTxt) { console.error("usage: queues-page.mjs <grid> <tech> <out.txt> [out.html]"); process.exitCode = 2; }
  else {
    const html = await drawQueues({ grid, tech });
    const text = pageText(html);
    fs.writeFileSync(outTxt, text + "\n");
    if (outHtml) fs.writeFileSync(outHtml, html);
    console.log(`${html.length} bytes of HTML; ${text.split("\n").length} lines of text`);
  }
}
