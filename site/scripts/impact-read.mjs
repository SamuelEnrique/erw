// Chain 304, part B (session 7515): /impact read as its reader. The page's own view (app/impact/Forecast.tsx) is drawn
// to HTML for each address of the list below, once with scenario A in view and once with B, with the page's own
// parameters and this script's own read of nlr_jedi_multipliers, and written as text a person can read cell by cell:
// the left box (every field, its value, its default, its hover), the A and B table (every row, its hover, both cells
// and a missing cell's hover), the table by year, every chart column's hover words, and the run's CSV as the page's
// download button would write it. No server, no network, no click. docs/reviews/impact-read-2026-11-16.md is the read.
//
//   cd site; node --import ./scripts/tsx-register.mjs scripts/impact-read.mjs <nlr_jedi_multipliers.csv> <out folder>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const home = path.join(here, "..", "..", "replication", "impact");
const F = await import("../lib/forecast.ts");
const D = await import("../lib/forecastdata.ts");
const U = await import("../lib/forecastui.ts");
const S = await import("../lib/severance.ts");
const X = await import("../lib/forecastfiles.ts");
const { Forecast } = await import("../app/impact/Forecast.tsx");

const [jediFile, outDir] = process.argv.slice(2);

// the five cases of the read, and the clicks each takes (an address is what the page would write after the click)
export const CASES = [
  ["1a_lone_mountain_first", "tech=geothermal&state=nv&mw=36&cost=4956.83&start=2026"],
  ["1b_lone_mountain_abated_against_not", "tech=geothermal&state=nv&mw=36&cost=4956.83&start=2026&iaval=1&own=1.0917&ownyears=60&bmw=36&bcost=4956.83&bstart=2026&bown=1.0917&bownyears=60"],
  ["2a_grant_solar", "tech=utility_pv&state=sd&mw=99&start=2026&proj=69981-utility_pv"],
  ["3a_silver_queen_first", "tech=land_based_wind&state=ia&mw=252&start=2027&proj=64835-land_based_wind"],
  ["3b_silver_queen_ordinance_levy", "tech=land_based_wind&state=ia&mw=252&start=2027&proj=64835-land_based_wind&iaval=1&levy=30&bmw=252&bstart=2027&blevy=30"],
  ["4a_cpv_basin_ranch_first", "tech=natural_gas&state=tx&mw=1445&start=2027&proj=69566-natural_gas"],
  ["4b_cpv_basin_ranch_fuel", "tech=natural_gas&state=tx&mw=1445&start=2027&proj=69566-natural_gas&instate=100&bmw=1445&bstart=2027"],
  ["5a_cape_utah_against_nevada", "tech=geothermal&state=ut&mw=86&start=2026&proj=68068-geothermal&bstate=nv&bmw=86&bstart=2026"],
];

function readRows(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const at = (k) => head.indexOf(k);
  return lines.slice(1).map((l) => l.split(",")).filter((c) => ["jobs", "earnings", "output"].includes(c[at("variable")]))
    .map((c) => ({ entity: c[at("entity")], variable: c[at("variable")], ts_utc: c[at("ts_utc")], value: Number(c[at("value")]) }));
}
function readCsv(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const cells = (l) => [...l.matchAll(/("(?:[^"]|"")*"|[^,]*)(?:,|$)/g)].slice(0, head.length).map((m) => (m[1].startsWith('"') ? m[1].slice(1, -1).replace(/""/g, '"') : m[1]));
  return lines.slice(1).map((l) => Object.fromEntries(cells(l).map((v, i) => [head[i], v])));
}
const un = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");

/** the drawn HTML as lines of text: a hover's words in [tip: ] or [hover: ], a field's value in [= ], a column's in [bar: ] */
export function asText(html) {
  let s = html;
  s = s.replace(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span>/g, (_m, t) => ` [tip: ${t.replace(/<[^>]+>/g, "")}]`);
  s = s.replace(/<button type="button" class="relative ml-1[^>]*>i<\/button>/g, "");
  s = s.replace(/<title>([\s\S]*?)<\/title>/g, (_m, t) => `\n[bar: ${t}]\n`);
  s = s.replace(/<select[^>]*aria-label="([^"]*)"[^>]*>([\s\S]*?)<\/select>/g, (_m, label, body) => {
    const sel = /<option[^>]*selected=""[^>]*>([^<]*)<\/option>/.exec(body);
    const n = (body.match(/<option/g) ?? []).length;
    return `[list ${label} = ${sel ? sel[1] : "(first)"}; ${n} options]`;
  });
  s = s.replace(/<input[^>]*>/g, (m) => {
    const v = /\svalue="([^"]*)"/.exec(m), l = /aria-label="([^"]*)"/.exec(m), p = /placeholder="([^"]*)"/.exec(m);
    return `[= ${v ? v[1] : ""}${p ? ` (empty: ${p[1]})` : ""}${l ? ` : ${l[1]}` : ""}]`;
  });
  s = s.replace(/<span[^>]*title="([^"]*)"[^>]*>([^<]*)<\/span>/g, (_m, t, w) => `${w} [hover: ${t}]`);
  s = s.replace(/<button[^>]*aria-pressed="(true|false)"[^>]*>([\s\S]*?)<\/button>/g, (_m, on, w) => `(${w.replace(/<[^>]+>/g, "")}${on === "true" ? ", in view" : ""}) `);
  s = s.replace(/<button[^>]*>([\s\S]*?)<\/button>/g, (_m, w) => `(button ${w.replace(/<[^>]+>/g, "")}) `);
  s = s.replace(/<\/(td|th)>/g, " | ").replace(/<\/(tr|p|div|h1|h2|h3|summary|li|section|figure|caption|details)>/g, "\n").replace(/<(tr|details|section|h2)[^>]*>/g, "\n");
  s = un(s.replace(/<[^>]+>/g, ""));
  return s.split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
}

if (!jediFile || !fs.existsSync(jediFile) || !outDir) {
  console.error("give the path of nlr_jedi_multipliers.csv and an output folder");
  process.exitCode = 2;
} else {
  fs.mkdirSync(outDir, { recursive: true });
  const P = D.params();
  const jedi = F.pack(readRows(jediFile));
  const rules = D.gasSeverance();
  const sev = (state, volume, price) => {
    const st = state.toUpperCase();
    if (!rules.states[st]?.products?.gas) return null;
    const r = S.compute(rules, { state: st, product: "gas", volume, price });
    return r.baseTotal + r.fees.reduce((a, f) => a + f.amount, 0);
  };
  // the left box's list, from the ten projects of the replication (the page reads the whole list from the live set)
  const planned = readCsv(path.join(home, "projects.csv")).map((p) => ({ id: p.id, name: p.name, tech: p.tech, state: p.state, county: p.county, mw: Number(p.mw), year: Number(p.planned_year) }));
  const ids = planned.map((p) => p.id);
  for (const [id, qs] of CASES) {
    const q = Object.fromEntries(new URLSearchParams(qs));
    const out = [`/impact?${qs}`, ""];
    for (const view of ["a", "b"]) {
      const start = U.withProjects(U.parse({ ...q, ...(view === "b" ? { view: "b" } : {}) }), q, ids);
      const html = renderToStaticMarkup(h(Forecast, { P, jedi, start, rules, planned }));
      out.push(`==================== scenario ${view.toUpperCase()} in view ====================`, asText(html), "");
      if (view === "a") {
        const x = { a: U.resolve(P, start.a), b: U.resolve(P, start.b) };
        const r = { a: F.run(x.a, F.unpack(jedi, x.a.tech, x.a.state), P, sev), b: F.run(x.b, F.unpack(jedi, x.b.tech, x.b.state), P, sev) };
        out.push("==================== the inputs as resolved ====================", JSON.stringify(x, null, 1), "");
        out.push("==================== the model's unrounded figures (what a hover or the CSV would give) ====================");
        for (const p of ["a", "b"]) {
          const g = r[p];
          out.push(`${p}: construction jobs ${JSON.stringify(g.construction.jobs)}; earnings ${JSON.stringify(g.construction.earnings)}`);
          out.push(`${p}: operating jobs ${JSON.stringify(g.operations.jobs)}; earnings ${JSON.stringify(g.operations.earnings)}`);
          out.push(`${p}: sums ${JSON.stringify(g.sums)}`, `${p}: pv ${JSON.stringify(g.pv)}`, `${p}: property ${JSON.stringify(g.property)}; sales ${JSON.stringify(g.sales)}; severance ${JSON.stringify(g.severance)}`);
        }
        const csv = X.csvOf(x, r).split("\n");
        out.push("", "==================== the run's CSV (the first 14 lines of the download) ====================", ...csv.slice(0, 14), `(${csv.length} lines)`, "");
      }
    }
    fs.writeFileSync(path.join(outDir, `${id}.txt`), out.join("\n"));
    console.log(`wrote ${id}.txt`);
  }
}
