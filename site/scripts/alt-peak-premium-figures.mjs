// Energy Research Warehouse (ERW) site, ruling alternative 1 of /explore/ercot-peak-premium (session 7708, 17 November
// 2026; branch wip/alt-ercot-peak-premium-1, not a default on main). The page drawn to HTML by its own function on two
// table files (the annual table with the branch builder's means added by the test, and the monthly table), its reads
// answered from them as scripts/peak-premium-figures.mjs answers them, for one view: HB_HUBAVG, 2024 against 2025.
// Prints whether the means section is drawn and the figures in it, by their check keys.
//   node --import ./scripts/tsx-register.mjs scripts/alt-peak-premium-figures.mjs <annual.csv> <monthly.csv>
import fs from "node:fs";
import { register } from "node:module";
import { createElement as h } from "react";

register(`data:text/javascript,${encodeURIComponent(`
export async function resolve(specifier, context, next) {
  if (specifier === "next/font/google") return { url: "erw-font-stub:google", shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url === "erw-font-stub:google") return { format: "module", shortCircuit: true, source:
    "const f = () => ({ className: '', variable: '', style: { fontFamily: 'stand-in' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;" };
  return next(url, context);
}`)}`);

function readTable(file) {
  const all = fs.readFileSync(file, "utf-8").split(/\r?\n/);
  const header = all.filter((l) => l.startsWith("#")).map((l) => l.replace(/^#\s?/, ""));
  const lines = all.filter((l) => l && !l.startsWith("#"));
  const ix = Object.fromEntries(lines[0].split(",").map((k, i) => [k, i]));
  return { header, rows: lines.slice(1).map((l) => { const c = l.split(","); return { entity: c[ix.entity], variable: c[ix.variable], ts_utc: c[ix.ts_utc], value: Number(c[ix.value]) }; }) };
}
const [annualFile, monthlyFile] = process.argv.slice(2);
const T = { ercot_peak_premium_annual: readTable(annualFile), ercot_peak_premium_monthly: readTable(monthlyFile) };
process.env.SUPABASE_URL = "http://alt-peak-premium.invalid";
process.env.SUPABASE_ANON_KEY = "local";
const eq = (f) => (f?.startsWith("eq.") ? f.slice(3) : null);
const among = (f) => (f?.startsWith("in.(") ? f.slice(4, -1).split(",").map((x) => x.replace(/^"|"$/g, "")) : null);
const one = (f) => (f === undefined ? null : eq(f) !== null ? [eq(f)] : among(f));
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = Object.fromEntries(u.searchParams);
  let out = [];
  const t = T[eq(q.table_name) ?? ""];
  if (u.pathname === "/rest/v1/series" && t) {
    const ent = one(q.entity), vars = one(q.variable), when = one(q.ts_utc)?.map((x) => new Date(x).getTime());
    out = t.rows.filter((r) => (!ent || ent.includes(r.entity)) && (!vars || vars.includes(r.variable)) && (!when || when.includes(new Date(r.ts_utc).getTime())));
    const keys = (q.order ?? "").split(",").filter(Boolean);
    out = out.slice().sort((a, b) => { for (const k of keys) { if (a[k] < b[k]) return -1; if (a[k] > b[k]) return 1; } return 0; });
  } else if (u.pathname === "/rest/v1/headers" && t) {
    out = t.header.map((line) => ({ line }));
  }
  const offset = Number(q.offset ?? 0), limit = Number(q.limit ?? 1000);
  return new Response(JSON.stringify(out.slice(offset, offset + limit)), { status: 200, headers: { "Content-Type": "application/json" } });
};
const { prerenderToNodeStream } = await import("react-dom/static");
const { default: Page } = await import("../app/explore/ercot-peak-premium/page.tsx");
const { prelude } = await prerenderToNodeStream(h(Page, { searchParams: Promise.resolve({ hub: "ercot:HB_HUBAVG", from: "2024", to: "2025" }) }));
const parts = [];
for await (const c of prelude) parts.push(Buffer.from(c));
const html = Buffer.concat(parts).toString("utf-8");
const section = html.split('data-means="1"')[1]?.split("</section>")[0] ?? "";
const shown = {};
for (const m of section.matchAll(/data-check="series\|ercot_peak_premium_annual\|ercot:HB_HUBAVG\|([a-z_]+)\|(\d{4})[^"]*"[^>]*>([^<]*)</g)) shown[`${m[1]}|${m[2]}`] = m[3];
process.stdout.write(JSON.stringify({ drawn: html.includes('data-means="1"'), shown }));
