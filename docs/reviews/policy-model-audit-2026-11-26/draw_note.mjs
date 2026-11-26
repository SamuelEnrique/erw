// Session 10217: the method note docs/methods/policy_monitor.md drawn as /data/methods/policy_monitor draws it (the site's
// own lib/markdown.ts render, on the note's text as it stands in this checkout), its visible text written to <out>.
//   cd site && node --import ./scripts/tsx-register.mjs ../runs/c10217/draw_note.mjs ../runs/c10217/note-b4.txt
import fs from "node:fs";
import path from "node:path";

const { render } = await import("../../site/lib/markdown.ts");
const md = fs.readFileSync(path.join(process.cwd(), "..", "docs", "methods", "policy_monitor.md"), "utf8");
const html = render(md, "docs/methods/policy_monitor.md");
const text = html.replace(/<[^>]+>/g, " ").replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\s+/g, " ");
fs.writeFileSync(process.argv[2], text + "\n");
console.log(`${html.length} characters of HTML, ${text.length} of text, em dash ${html.includes(String.fromCharCode(0x2014)) ? "PRESENT" : "none"}`);
