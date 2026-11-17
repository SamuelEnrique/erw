// Session 7615 (portable-laptop): read pages of a local build whose Num.tsx was given, for this read only, a
// data-held-key attribute on its held span (never committed), and list every held figure's table and check key.
//   node runs/ruling_impact/held_keys.mjs <base> <out.json> <path> [<path> ...]
import fs from "node:fs";
import { unlockPost } from "../../site/scripts/browser.mjs";

const [base, out, ...paths] = process.argv.slice(2);
const token = process.env.INTERNAL_COSTS_TOKEN;
if (!token) { console.error("INTERNAL_COSTS_TOKEN is not set"); process.exit(2); }
const res = await unlockPost(base, token);
const cookie = res.headers.getSetCookie().map((c) => c.split(";")[0]).join("; ");
const result = {};
for (const p of paths) {
  const r = await fetch(base + p, { headers: { cookie } });
  const html = await r.text();
  const held = [...html.matchAll(/data-license-held="([^"]*)" data-held-key="([^"]*)"/g)].map((m) => ({ table: m[1], key: m[2].replace(/&amp;/g, "&") }));
  const shown = [...html.matchAll(/data-check="([^"]*)"/g)].length;
  const words = (html.match(/license needed/g) || []).length;
  const text = (html.match(/>\s*license needed\s*</g) || []).length;   // drawn as a cell's words, not in a title
  result[p] = { status: r.status, held, shown, words, text };
  console.log(`${p}: ${r.status}; held figures ${held.length}; checked figures shown ${shown}; "license needed" in the HTML ${words}, as drawn words ${text}`);
}
fs.writeFileSync(out, JSON.stringify(result, null, 1));
