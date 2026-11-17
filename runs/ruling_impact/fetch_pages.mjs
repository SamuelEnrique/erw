// Session 7618 (portable-laptop): save the HTML of pages of the local build (internal view) under runs/ruling_impact/cache/pages/.
//   node runs/ruling_impact/fetch_pages.mjs <base> <path> [<path> ...]
import fs from "node:fs";
import path from "node:path";
import { unlockPost } from "../../site/scripts/browser.mjs";

const [base, ...paths] = process.argv.slice(2);
const token = process.env.INTERNAL_COSTS_TOKEN;
if (!token) { console.error("INTERNAL_COSTS_TOKEN is not set"); process.exit(2); }
const res = await unlockPost(base, token);
const cookie = res.headers.getSetCookie().map((c) => c.split(";")[0]).join("; ");
const dir = path.join(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "cache", "pages");
fs.mkdirSync(dir, { recursive: true });
for (const p of paths) {
  const r = await fetch(base + p, { headers: { cookie } });
  const html = await r.text();
  const f = path.join(dir, p.replace(/[^a-z0-9]+/gi, "_").replace(/^_+|_+$/g, "") + ".html");
  fs.writeFileSync(f, html);
  console.log(`${p}: ${r.status}, ${html.length} bytes -> ${path.basename(f)}`);
}
