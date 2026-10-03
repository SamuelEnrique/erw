// Energy Research Warehouse (ERW) site, session 69: /storage/buildout as rendered, against the fixture.
//
//   node scripts/buildout-stub.mjs &                                         (the stand-in for Supabase)
//   SUPABASE_URL=http://localhost:54369 SUPABASE_ANON_KEY=local npm run build
//   SUPABASE_URL=http://localhost:54369 SUPABASE_ANON_KEY=local npx next start -p 3069
//   node scripts/check-buildout.mjs [base-url]                               (default http://localhost:3069)
//
// What scripts/check-values.mjs and scripts/check-routes.mjs will do against Supabase after the finish step, done now
// against the fixture, read here from its file and not through the site: for the United States and every ISO, in MW and
// MWh, the page answers 200, shows no "no data" and no "undefined", every number's data-raw equals the fixture's row
// under its check key, its text is that value as the site writes numbers, the summary sentence is the fixture's, the
// headline numbers are there, the selected grid's row is highlighted, and both charts are drawn. Exits 1 on a failure.
import { GRIDS, shown } from "../lib/buildout.ts";
import { fixtureRows, TABLE } from "./buildout-stub.mjs";

const base = process.argv[2] ?? "http://localhost:3069";
let bad = 0, n = 0, values = 0;
const check = (ok, what) => { n++; if (!ok) { bad++; console.log(`FAIL ${what}`); } };
const truth = new Map(fixtureRows().map((r) => [`series|${TABLE}|${r.entity}|${r.variable}|${r.ts_utc}`, r.value]));
const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
const visible = (html) => decode(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const val = (e, v, m) => truth.get(`series|${TABLE}|${e}|${v}|${m}-01T00:00:00Z`);

for (const grid of GRIDS) {
  for (const measure of ["mw", "mwh"]) {
    const page = `/storage/buildout?grid=${grid.slug}&measure=${measure}`;
    const res = await fetch(base + page);
    const html = await res.text();
    const text = visible(html);
    check(res.status === 200, `${page}: status ${res.status}`);
    check(!/\bno data\b/.test(text) && !/\bundefined\b/.test(text) && !/\bNaN\b/.test(text), `${page}: no "no data", "undefined" or "NaN"`);
    check(!html.includes("—"), `${page}: no em dash`);
    const spans = [...html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)];
    check(spans.length >= 150, `${page}: ${spans.length} checked numbers`);
    for (const m of spans) {
      const key = decode(m[1]), raw = Number(m[2]), shownText = decode(m[3].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).trim();
      values++;
      check(truth.has(key) && truth.get(key) === raw, `${page}: ${key} page read ${m[2]}, fixture ${truth.get(key)}`);
      check(shownText === shown(raw), `${page}: ${key} shown "${shownText}", expected "${shown(raw)}"`);
    }
    const e = grid.entity;
    const [mw, mwh, hours, before] = [val(e, "battery_operating_mw", "2026-08"), val(e, "battery_operating_mwh", "2026-08"), val(e, "battery_operating_mwh_per_mw", "2026-08"), val(e, "battery_operating_mw", "2025-08")];
    const sentence = `${grid.name} has ${shown(mw)} MW of batteries holding ${shown(mwh)} MWh, an average of ${shown(hours)} hours, ${mw > before ? "up from" : mw < before ? "down from" : "unchanged from"} ${shown(before)} MW a year ago.`;
    check(text.includes(sentence), `${page}: the summary sentence: ${sentence}`);
    check(text.includes(`Operating power ${shown(mw)} MW`) && text.includes(`Operating energy ${shown(mwh)} MWh average duration ${shown(hours)} hours`)
      && text.includes(`net of retirements ${shown(val(e, "battery_operating_mw_net_added_12m", "2026-08"))} MW ${shown(val(e, "battery_operating_mwh_net_added_12m", "2026-08"))} MWh`), `${page}: the three headline numbers`);
    check(text.includes("How much storage has been built") && text.includes("Operating storage by year, by duration") && text.includes("Storage against solar") && text.includes("By grid"), `${page}: title and sections`);
    check(text.includes("How generators are assigned to a grid, and how many were not") && text.includes("What EIA-860M covers and misses") && text.includes("The newest month held") && text.includes("Source: ERW table storage_buildout_monthly"), `${page}: folded sections and the source line`);
    check((html.match(/<svg /g) ?? []).length >= 2 && (html.match(/<rect /g) ?? []).length >= 12 && (html.match(/<circle /g) ?? []).length >= 2, `${page}: both charts are drawn`);
    // the bars: one hover title per bucket and year with a value above zero, in the measure's unit
    const unit = measure === "mw" ? "MW" : "MWh";
    const titles = [...html.matchAll(/<title>([^<]*)<\/title>/g)].map((m) => decode(m[1]));
    for (const y of ["2020", "2025", "2026 to August"]) {
      const month = y.startsWith("2026") ? "2026-08" : `${y}-12`;
      const v4 = val(e, `battery_operating_${measure}_4to6h`, month);
      if (v4 > 0) check(titles.includes(`${y}, 4 to under 6 hours: ${shown(v4)} ${unit}`), `${page}: the ${y} bar's 4 to 6 hour segment is ${shown(v4)} ${unit}`);
    }
    const perSolar = val(e, "battery_mwh_per_solar_mw", "2026-08");
    check(titles.includes(`2026 to August: ${shown(perSolar)} MWh of batteries per MW of solar`), `${page}: the solar line's last point is ${shown(perSolar)}`);
    // the table by grid: nine rows, the chosen grid's row in fog beige, the United States row for the default
    const rows = html.split("<tr").map((r) => r.split("</tr>")[0]).filter((r) => /battery_planned_mw\|/.test(r));
    check(rows.length === 9, `${page}: the table by grid has nine rows (${rows.length})`);
    const on = rows.filter((r) => /class="[^"]*bg-paper/.test(r.slice(0, 200)));
    check(on.length === 1 && on[0].includes(`|${e}|battery_operating_mw|`), `${page}: the chosen grid's row is highlighted`);
    check(html.includes(`aria-current="true"`) && new RegExp(`aria-current="true"[^>]*>${grid.label}<`).test(html.replace(/class="[^"]*"/g, "")), `${page}: the panel marks ${grid.label}`);
  }
}
// a grid or measure the page does not know falls back to the United States in MW
const fallback = visible(await (await fetch(`${base}/storage/buildout?grid=nope&measure=x`)).text());
check(fallback.includes("The United States has "), "an unknown grid shows the United States");
console.log(bad ? `${bad} of ${n} checks FAILED` : `/storage/buildout as rendered: ${n} checks pass, ${values} numbers equal the fixture's rows (16 pages)`);
process.exit(bad ? 1 : 0);
