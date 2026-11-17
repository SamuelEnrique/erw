// Energy Research Warehouse (ERW) site, ruling alternatives of /shoulder (session 7703, 17 November 2026; wip/alt-shoulder-*
// branches, not a default on main). Draws the page with its own code, without a build, on the rows of a
// shoulder_hours_monthly file (the table in warehouse/output, or a fixture), for each address given, and prints what a
// test pins: the summary sentence, the headline cells' words, and every checked figure (data-check, data-raw).
//   node --import ./scripts/tsx-register.mjs scripts/alt-shoulder-draw.mjs <shoulder_hours_monthly.csv> '<[{"grid":"ercot","month":"2026-08"}]>'
import fs from "node:fs";
import { register } from "node:module";
import { renderToStaticMarkup } from "react-dom/server";

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

const lines = fs.readFileSync(process.argv[2], "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const cols = lines[0].split(",");
const rows = lines.slice(1).map((l) => { const c = l.split(","); const r = Object.fromEntries(cols.map((k, i) => [k, c[i]])); return { entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: r.value }; })
  .sort((a, b) => (a.entity + "|" + a.variable + "|" + a.ts_utc < b.entity + "|" + b.variable + "|" + b.ts_utc ? -1 : 1));
process.env.SUPABASE_URL = "http://alt-shoulder.invalid";
process.env.SUPABASE_ANON_KEY = "local";
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = Object.fromEntries(u.searchParams);
  const out = u.pathname === "/rest/v1/series" && q.table_name === "eq.shoulder_hours_monthly" ? rows.slice(Number(q.offset ?? 0), Number(q.offset ?? 0) + Number(q.limit ?? 1000)) : [];
  return new Response(JSON.stringify(out), { status: 200, headers: { "Content-Type": "application/json", "Content-Range": `0-${out.length}/*` } });
};
const { default: Shoulder } = await import("../app/shoulder/page.tsx");
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const out = [];
for (const q of JSON.parse(process.argv[3])) {
  const html = renderToStaticMarkup(await Shoulder({ searchParams: Promise.resolve(q) }));
  const summary = words((html.match(/<p[^>]*data-summary="1"[^>]*>([\s\S]*?)<\/p>/) ?? ["", ""])[1]);
  const checks = Object.fromEntries([...html.matchAll(/data-check="([^"]+)" data-raw="([^"]*)"/g)].map((m) => [m[1], Number(m[2])]));
  const marks = [...html.matchAll(/data-(headline-measure|one-source|monitor-fleet|by-duration|worst-by)="([^"]*)"/g)].map((m) => `${m[1]}=${m[2]}`);
  out.push({ q, summary, checks, marks, text: words(html).slice(0, 20000) });
}
process.stdout.write(JSON.stringify(out));
