// Energy Research Warehouse (ERW) site, ruling alternative 26 of /impact (session 7706, 17 November 2026;
// wip/alt-impact-26, not a default on main): the page's own view (app/impact/Forecast.tsx) drawn to HTML for one address,
// and the third column "B less A" read off it: each row's data-diff, by its row key. JEDI's rows are read from
// nlr_jedi_multipliers.csv, as scripts/impact-figures.mjs reads them. No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/alt-impact-diff.mjs <nlr_jedi_multipliers.csv> "<query string>"
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const F = await import("../lib/forecast.ts");
const D = await import("../lib/forecastdata.ts");
const U = await import("../lib/forecastui.ts");
const { Forecast } = await import("../app/impact/Forecast.tsx");

function readRows(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const at = (k) => head.indexOf(k);
  return lines.slice(1).map((l) => l.split(",")).filter((c) => ["jobs", "earnings", "output"].includes(c[at("variable")]))
    .map((c) => ({ entity: c[at("entity")], variable: c[at("variable")], ts_utc: c[at("ts_utc")], value: Number(c[at("value")]) }));
}

const P = D.params();
const jedi = F.pack(readRows(process.argv[2]));
const start = U.withProjects(U.parse(Object.fromEntries(new URLSearchParams(process.argv[3]))), {}, []);
const html = renderToStaticMarkup(h(Forecast, { P, jedi, start, rules: D.gasSeverance(), planned: [] }));
const out = { head: /data-head="d"/.test(html), diffs: {} };
for (const m of html.matchAll(/data-cell="d\|([a-z0-9]+)"(?: data-diff="([^"]+)")?>([^<]*)</g)) out.diffs[m[1]] = { raw: m[2] === undefined ? null : Number(m[2]), text: m[3] };
process.stdout.write(JSON.stringify(out));
