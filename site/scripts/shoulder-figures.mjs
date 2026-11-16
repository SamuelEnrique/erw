// Energy Research Warehouse (ERW) site, session 7503 (chain 304): every figure of "The shoulder hours" (/shoulder), as
// the page itself draws it, for every grid and every month the page can be asked for.
//
//   node --import ./scripts/tsx-register.mjs scripts/shoulder-figures.mjs <shoulder_hours_monthly.csv> <out.json> [--opening] [--html=<dir>]
//
// The page (app/shoulder/page.tsx) is drawn to HTML with the site's own code, once a view (a grid and a month, and each
// grid with no month named), on the rows of the table file named: the page's one read of the live set
// (app/shoulder/read.ts through lib/supabase.ts) is answered here from that file, in the process, as
// scripts/shoulder-stub.mjs answers it from a port. Nothing is asked of a server and nothing is written but <out.json>.
// From each view's HTML it keeps: every checked number (its key, the value read and the text shown), every value of the
// two charts' hover lines, and the words that carry a choice (the month opened on, "midnight", "not held").
// replication/shoulder/replicate.py sets these beside its own computation. --opening draws only the three views a
// reader meets with no month named. It runs no effect and no click.
import fs from "node:fs";
import { register } from "node:module";
import { renderToStaticMarkup } from "react-dom/server";

// The page's frame (components/Brand.tsx) names the brand's three fonts through next/font/google, which exists only
// inside a build. Here a font is its class names and nothing more: no figure of the page depends on one. The hook is
// registered by this script alone, in front of the site's two loaders, which stay as they are.
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

const [file, outFile, ...flags] = process.argv.slice(2);
if (!file || !outFile) {
  console.error("usage: node --import ./scripts/tsx-register.mjs scripts/shoulder-figures.mjs <shoulder_hours_monthly.csv> <out.json> [--opening]");
  process.exitCode = 2;
} else {
  await main();
}

async function main() {
  const lines = fs.readFileSync(file, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const cols = lines[0].split(",");
  const rows = lines.slice(1).map((l) => {
    const c = l.split(",");
    const r = Object.fromEntries(cols.map((k, i) => [k, c[i]]));
    return { entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: r.value };
  }).sort((a, b) => (a.entity + "|" + a.variable + "|" + a.ts_utc < b.entity + "|" + b.variable + "|" + b.ts_utc ? -1 : 1));

  // the page's read, answered from the file: GET <base>/rest/v1/series?table_name=eq.shoulder_hours_monthly&limit=&offset=
  process.env.SUPABASE_URL = "http://shoulder-figures.invalid";
  process.env.SUPABASE_ANON_KEY = "local";
  let asked = 0;
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    const q = Object.fromEntries(u.searchParams);
    asked++;
    let out = [];
    if (u.pathname === "/rest/v1/series" && q.table_name === "eq.shoulder_hours_monthly") {
      const offset = Number(q.offset ?? 0), limit = Number(q.limit ?? 1000);
      out = rows.slice(offset, offset + limit);
    }
    return new Response(JSON.stringify(out), { status: 200, headers: { "Content-Type": "application/json", "Content-Range": `0-${out.length}/*` } });
  };

  const S = await import("../lib/shoulder.ts");
  const { default: Shoulder } = await import("../app/shoulder/page.tsx");
  const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
  const text = (html) => decode(html.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
  const draw = async (q) => renderToStaticMarkup(await Shoulder({ searchParams: Promise.resolve(q) }));

  const typed = rows.map((r) => ({ ...r, value: Number(r.value) }));
  const views = [];
  const htmlDir = flags.find((f) => f.startsWith("--html="))?.slice(7);   // keeps each view's HTML, for a reader of it
  for (const g of S.GRIDS) {
    views.push({ grid: g.slug, month: null });
    if (!flags.includes("--opening")) {
      const months = [...new Set(typed.filter((r) => r.entity === g.entity && r.variable === "days_held").map((r) => S.monthOf(r.ts_utc)))].sort();
      for (const m of months) views.push({ grid: g.slug, month: m });
    }
  }

  const out = { table_file: file, table_rows: rows.length, views: [], keyed: {}, chart_day: {}, chart_month: {}, conflicts: [] };
  const put = (bag, key, value) => {
    if (key in bag && JSON.stringify(bag[key]) !== JSON.stringify(value)) out.conflicts.push({ key, first: bag[key], second: value });
    bag[key] = value;
  };
  for (const v of views) {
    const g = S.GRIDS.find((x) => x.slug === v.grid);
    const html = await draw(v.month ? { grid: v.grid, month: v.month } : { grid: v.grid });
    if (htmlDir) fs.writeFileSync(`${htmlDir}/shoulder_${v.grid}_${v.month ?? "opening"}.html`, html);
    const page = text(html);
    const month = (html.match(/aria-current="true"[^>]*>(\d\d)<\/a>/) ? null : null);   // the month is read from the summary below
    const summary = text(html.match(/<p[^>]*data-summary="1"[^>]*>([\s\S]*?)<\/p>/)?.[1] ?? "");
    const spans = [...html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)];
    const keys = [];
    for (const m of spans) {
      const key = decode(m[1]);
      keys.push(key);
      put(out.keyed, key, { raw: Number(m[2]), text: text(m[3]) });
    }
    // the average day's hover lines: "<series>: 00:00 41,234, 01:00 ... MW", one a line of the chart
    const dayTitle = html.match(/aria-label="[^"]*the average day of ([^,"]+), MW by local hour"/);
    const drawnMonth = dayTitle ? decode(dayTitle[1]) : null;
    const series = [];
    for (const m of html.matchAll(/<title>(demand|net load|solar|battery): ([^<]*) MW<\/title>/g)) {
      series.push(m[1]);
      for (const part of m[2].split(", ").reduce((acc, p) => { if (/^\d\d:00 /.test(p)) acc.push(p); else acc[acc.length - 1] += `,${p}`; return acc; }, [])) {
        const mm = part.match(/^(\d\d):00 (-?[\d,]+)$/);
        if (mm) put(out.chart_day, `${g.entity}|avg_${m[1].replace(" ", "_")}_mw_h${mm[1]}|${drawnMonth}`, mm[2]);
      }
    }
    // the months' hover lines: "July 2026: shoulder 5 hours; fleet covers 1.65"
    let monthsDrawn = 0;
    for (const m of html.matchAll(/<title>([A-Z][a-z]+ \d{4}): shoulder ([^;]*?) hours; fleet covers ([^<]*)<\/title>/g)) {
      monthsDrawn++;
      put(out.chart_month, `${g.entity}|${m[1]}`, { shoulder: m[2], covered: m[3] });
    }
    out.views.push({
      grid: v.grid, asked: v.month, drawn: drawnMonth, summary, keyed: keys.length, keys: v.month ? undefined : keys,
      series, months_drawn: monthsDrawn,
      opening: decode(html.match(/data-opening="([^"]*)"/)?.[1] ?? ""),
      opening_note: text(html.match(/<p[^>]*data-opening="[^"]*"[^>]*>([\s\S]*?)<\/p>/)?.[1] ?? ""),
      midnight: / \(midnight\)/.test(summary), not_held: (page.match(/not held/g) ?? []).length,
      worst_none: /data-worst="none"/.test(html), no_data: /role="status"/.test(html) && /no data/.test(page),
      heading_months: text(html.match(/<h2[^>]*>(By month[^<]*)<\/h2>/)?.[1] ?? ""),
      decisions: (html.match(/data-decision="/g) ?? []).length,
      em_dash: html.includes(String.fromCharCode(0x2014)), undefined_or_nan: /\bundefined\b|\bNaN\b/.test(page),
    });
    void month;
  }
  out.reads = asked;
  fs.writeFileSync(outFile, JSON.stringify(out));
  console.log(`/shoulder drawn with the page's own code: ${out.views.length} views, ${Object.keys(out.keyed).length} checked numbers, ${Object.keys(out.chart_day).length} values of the average day's chart, ${Object.keys(out.chart_month).length} months of the months' chart, ${out.conflicts.length} figures shown two ways; written to ${outFile}`);
  if (out.views.some((v) => v.no_data || v.undefined_or_nan || v.em_dash)) process.exitCode = 1;
}
