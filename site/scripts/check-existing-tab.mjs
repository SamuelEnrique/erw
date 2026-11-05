// Energy Research Warehouse (ERW) site, session 700: "No default figure of the existing tab moves" (chain 050). The
// All grids tab is a view of /cost-of-power; this reads the existing views' addresses on two builds (production and a
// local build, say) with the internal cookie, and compares every checked figure (data-check and data-raw): the same keys,
// the same values. A key on one build only, or a value that differs, is listed and the exit is 1. No database read.
//
//   node scripts/check-existing-tab.mjs <base-a> <base-b> [page ...]
//   (default pages: /cost-of-power, /cost-of-power?run=hours, /cost-of-power?grid=caiso, /cost-of-power?view=grids)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { unlockPost } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
function env(name) {
  if (process.env[name]) return process.env[name];
  const f = path.join(here, "..", ".env.local");
  if (!fs.existsSync(f)) return "";
  for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
    const m = line.match(/^([A-Z_]+)=(.*)$/);
    if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
  }
  return "";
}
const [a, b, ...given] = process.argv.slice(2);
if (!a || !b) { console.error("usage: node scripts/check-existing-tab.mjs <base-a> <base-b> [page ...]"); process.exit(2); }
const PAGES = given.length ? given : ["/cost-of-power", "/cost-of-power?run=hours", "/cost-of-power?grid=caiso", "/cost-of-power?view=grids"];
const tok = env("INTERNAL_COSTS_TOKEN");

async function cookieOf(base) {
  const u = await unlockPost(base, tok);
  return (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
}
const decode = (s) => s.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
async function keysOf(base, cookie, page) {
  const r = await fetch(`${base}${page}`, { headers: { cookie, "User-Agent": "erw-check (node)" }, signal: AbortSignal.timeout(180_000) });
  if (r.status !== 200) throw new Error(`${base}${page}: HTTP ${r.status}`);
  const html = await r.text();
  const out = new Map();
  for (const m of html.matchAll(/data-check="([^"]*)" data-raw="([^"]*)"/g)) out.set(decode(m[1]), decode(m[2]));
  return out;
}

let bad = 0;
const [ca, cb] = [await cookieOf(a), await cookieOf(b)];
if (!ca || !cb) { console.error("check-existing-tab FAILED: no internal cookie from one of the two builds"); process.exit(1); }
for (const page of PAGES) {
  const [ka, kb] = [await keysOf(a, ca, page), await keysOf(b, cb, page)];
  const diff = [];
  for (const [k, v] of ka) if (!kb.has(k)) diff.push(`only on ${a}: ${k} = ${v}`); else if (kb.get(k) !== v) diff.push(`differs: ${k}: ${v} against ${kb.get(k)}`);
  for (const [k, v] of kb) if (!ka.has(k)) diff.push(`only on ${b}: ${k} = ${v}`);
  console.log(`${diff.length ? "FAIL" : "ok  "} | ${page} | ${ka.size} keys on ${a}, ${kb.size} on ${b}, ${diff.length} differences`);
  for (const d of diff) console.log(`     | ${d}`);
  bad += diff.length;
}
console.log(bad ? `check-existing-tab: ${bad} differences` : "check-existing-tab: every figure the same");
process.exitCode = bad ? 1 : 0;
