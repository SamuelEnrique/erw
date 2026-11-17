// Chain 304 (session 7506): every figure /impact shows, read from the page's own view drawn to HTML, without building
// the site (scripts/tsx-loader.mjs), for the replication of replication/impact/ (docs/methods/forecast.md, section 12).
// The page's view component (app/impact/Forecast.tsx) is drawn for each address of the list below, once with scenario A
// in view and once with B, from this script's own read of nlr_jedi_multipliers and the page's own parameters
// (lib/forecastdata.ts, params). Read from the HTML: every keyed number of the A and B table and of the table by year
// (its key, its raw value, its text), every cell the page draws as "not held", "none" or "no figure", every default of
// the left box, and the scenario's place among the states. The two charts of "other states" draw no keyed number: their
// values are computed here with the page's own functions and the page's own rule of which states are shown, and each
// shown state's name is then looked for in the drawn chart. No server, no network, no click.
//
//   cd site; node --import ./scripts/tsx-register.mjs scripts/impact-figures.mjs <nlr_jedi_multipliers.csv> [--check] [--out <folder>]
//
// Writes replication/impact/page_figures.json and page_figures.csv; with --check it writes nothing and exits 1 when the
// files on disk differ from what the page draws today.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const home = path.join(here, "..", "..", "replication", "impact");   // projects.csv is read here; --out names another folder for the two files
const F = await import("../lib/forecast.ts");
const D = await import("../lib/forecastdata.ts");
const U = await import("../lib/forecastui.ts");
const I = await import("../lib/impact.ts");
const S = await import("../lib/severance.ts");
const { Forecast } = await import("../app/impact/Forecast.tsx");

const args = process.argv.slice(2);
const checkOnly = args.includes("--check");
const outAt = args.indexOf("--out");
const out = outAt >= 0 && args[outAt + 1] ? path.resolve(args[outAt + 1]) : home;
const jediFile = args.find((a, i) => !a.startsWith("--") && (outAt < 0 || i !== outAt + 1));
if (!jediFile || !fs.existsSync(jediFile)) {
  console.error("give the path of nlr_jedi_multipliers.csv (warehouse/output, or the page's download)");
  process.exitCode = 2;
} else {
  main();
}

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
  // a quoted field may hold a comma (a plant's name: "Grant Solar, LLC")
  const cells = (l) => [...l.matchAll(/("(?:[^"]|"")*"|[^,]*)(?:,|$)/g)].slice(0, head.length).map((m) => (m[1].startsWith('"') ? m[1].slice(1, -1).replace(/""/g, '"') : m[1]));
  return lines.slice(1).map((l) => Object.fromEntries(cells(l).map((v, i) => [head[i], v])));
}
function text(s) { return s.replace(/<[^>]+>/g, "").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").trim(); }

/** half of the page's last shown digit, by the form the page writes the figure in (lib/forecast.ts, usdText, jobsText) */
function tolerance(figure, v) {
  const p = figure.split(":");
  if (p[0] === "default") return null;
  if (p[2] === "mwh") return 0.5;
  const jobs = p[1] === "jobs" || p[2] === "jobs" || (p[0] === "states" && p[1] === "jobs");
  if (jobs) return p[0] === "states" ? 0.05 : Math.abs(v) < 100 ? 0.05 : 0.5;
  const a = Math.abs(v);
  return a >= 1e9 ? 0.005e9 : a >= 1e6 ? 0.05e6 : 0.5;
}
/** a default's tolerance from the digits the left box writes */
function defaultTolerance(shown) {
  const m = /\.(\d+)$/.exec(shown.replace(/,/g, ""));
  return m ? 0.5 / 10 ** m[1].length : 0.5;
}

function main() {
  const rows = readRows(jediFile);
  const P = D.params();
  const jedi = F.pack(rows);
  const rules = D.gasSeverance();
  const sev = (state, volume, price) => {
    const st = state.toUpperCase();
    if (rules.states[st]?.held) return NaN;   // ruling alternative 14 (wip/alt-impact-14): a held rate
    if (!rules.states[st]?.products?.gas) return null;
    const r = S.compute(rules, { state: st, product: "gas", volume, price });
    return r.baseTotal + r.fees.reduce((a, f) => a + f.amount, 0);
  };
  const projects = readCsv(path.join(home, "projects.csv"));

  // ---- the addresses: the default, the named projects, and the seven addresses check-values reads (the note, section 11)
  const cases = [{ id: "default", what: "the page as it opens: 200 MW of land-based wind in Texas, A and B alike", query: {} }];
  for (const p of projects) {
    const d = F.defaults(P, p.tech, p.state);
    const mw = Math.round(Number(p.mw) * 1000) / 1000;                 // the pick of the left box's "Planned project" list
    const start = Math.max(2026, Number(p.planned_year) - d.build);
    cases.push({ id: `project_${p.id}`, what: `${p.name}, ${p.county} County, ${I.stateName(p.state)}: ${p.mw} MW, planned for ${p.planned_year} (EIA-860M, plant ${p.plant_id}); B is EIA's case size in the same state`,
      project: p.id, query: { tech: p.tech, state: p.state, mw: String(mw), start: String(start) } });
  }
  const listed = [
    ["mn_sd_pv", "tech=utility_pv&state=mn&bstate=sd"], ["tx_gas_ca_geo", "tech=natural_gas&state=tx&instate=50&btech=geothermal&bstate=ca"],
    ["ia_ne_wind", "state=ia&iaval=1&levy=30&bstate=ne"], ["or_nd_pv", "tech=utility_pv&state=or&iaval=1&btech=utility_pv&bstate=nd"],
    ["mi_vt_pv", "tech=utility_pv&state=mi&iaval=1&bstate=vt&bown=1.4&bownyears=25"], ["il_wv_wind", "state=il&levy=80&bstate=wv"],
  ];
  for (const [id, qs] of listed) cases.push({ id: `address_${id}`, what: `an address check-values reads: /impact?${qs}`, query: Object.fromEntries(new URLSearchParams(qs)) });

  const figures = [];
  const seen = new Set();
  const add = (c, scenario, figure, page, shown, tol) => {
    const k = `${c.id}|${scenario}|${figure}`;
    if (seen.has(k)) return;
    seen.add(k);
    figures.push({ case: c.id, scenario, figure, page, shown, tolerance: tol });
  };
  let bad = 0;
  for (const c of cases) {
    const address = `/impact${Object.keys(c.query).length ? `?${new URLSearchParams(c.query)}` : ""}`;
    c.address = address;
    c.inputs = {};
    for (const view of ["a", "b"]) {
      const start = U.withProjects(U.parse({ ...c.query, ...(view === "b" ? { view: "b" } : {}) }), {}, []);
      const html = renderToStaticMarkup(h(Forecast, { P, jedi, start, rules, planned: [] }));
      const x = U.resolve(P, start[view]);
      c.inputs[view] = x;
      const key = F.inputsKey(x);
      // the keyed numbers: the A and B table (both scenarios) and the table by year (the scenario in view)
      for (const m of html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]+)"[^>]*>([\s\S]*?)<\/span>/g)) {
        const check = m[1].replace(/&amp;/g, "&");
        const cut = check.lastIndexOf("|");
        const scen = check.slice(0, cut) === key ? view : check.slice(0, cut) === F.inputsKey(U.resolve(P, start[view === "a" ? "b" : "a"])) ? (view === "a" ? "b" : "a") : null;
        if (scen === null) { bad++; console.log(`FAIL ${c.id}: a key of neither scenario: ${check}`); continue; }
        const figure = check.slice(cut + 1);
        // A and B alike (the default page): the table's two columns are the same key; both are written
        const both = F.inputsKey(U.resolve(P, start.a)) === F.inputsKey(U.resolve(P, start.b));
        for (const s of both && !figure.startsWith("year:") ? ["a", "b"] : [figure.startsWith("year:") ? view : scen]) add(c, s, figure, Number(m[2]), text(m[3]), tolerance(figure, Number(m[2])));
      }
      // the cells with no number: "not held", "none", "no figure" (their reason is the cell's hover)
      for (const m of html.matchAll(/data-cell="([ab])\|([a-z0-9]+)"><span[^>]*title="([^"]*)"[^>]*>([^<]*)<\/span>/g)) add(c, m[1], `cell:${m[2]}`, null, `${m[4]} (${text(m[3])})`, null);
      // the table by year's empty cells are a dash and carry no key: counted by the replication from the keyed ones
      // the left box's defaults for the scenario in view
      for (const m of html.matchAll(/data-default="([a-z]+)">([^<]*)</g)) {
        if (m[1] === "tech" || m[1] === "state" || m[1] === "proj") continue;
        const shown = text(m[2]).replace(/^Default /, "");
        const dflt = U.resolve(P, { tech: start[view].tech, state: start[view].state })[m[1]];
        const page = dflt === null ? null : typeof dflt === "boolean" ? (dflt ? 1 : 0) : dflt;
        add(c, view, `default:${m[1]}`, page, shown, page === null || m[1] === "iaval" || m[1] === "start" ? null : defaultTolerance(shown));
      }
      // the scenario in other states: the page's own rule (app/impact/Forecast.tsx, OtherStates), with the page's functions
      const per = Object.keys(jedi).filter((k) => k.startsWith(`${x.tech}:`) && !k.endsWith(":us")).map((k) => {
        const st = k.split(":")[1];
        const ix = U.STATE_LIST.findIndex(([s]) => s === st);
        const res = F.run(U.resolve(P, { ...start[view], state: ix, proj: NaN }), F.unpack(jedi, x.tech, st), P, sev);
        return { k: st, name: I.stateName(st), ok: res.ok, c: res.construction.jobs, taxes: res.pv.taxes };
      }).filter((v) => v.ok).sort((a, b) => b.c.total - a.c.total);
      const shown = per.filter((v, i) => i < 10 || i >= per.length - 5 || v.k === x.state);
      const taxSorted = [...per].sort((a, b) => b.taxes - a.taxes);
      const byTax = taxSorted.filter((v, i) => i < 10 || i >= taxSorted.length - 5 || v.k === x.state);
      const one = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
      const chart = html.slice(html.indexOf("data-state-chart="));
      const jobsChart = chart.slice(0, chart.indexOf("data-state-taxes=")), taxChart = chart.slice(chart.indexOf("data-state-taxes="));
      shown.forEach((v, i) => {
        if (!text(jobsChart).includes(v.name)) { bad++; console.log(`FAIL ${c.id} ${view}: ${v.name} is not in the drawn jobs chart`); }
        for (const e of ["onsite", "supply_chain", "induced"]) add(c, view, `states:jobs:${i + 1}:${v.k}:${e}`, v.c[e], one(v.c[e]), 0.05);
      });
      byTax.forEach((v, i) => {
        if (!text(taxChart).includes(v.name)) { bad++; console.log(`FAIL ${c.id} ${view}: ${v.name} is not in the drawn taxes chart`); }
        add(c, view, `states:taxes:${i + 1}:${v.k}`, v.taxes, F.usdText(v.taxes), tolerance("pv:taxes", v.taxes));
      });
      const rank = new RegExp(`${I.stateName(x.state)} is (\\d+) of (\\d+)\\.`).exec(text(html));
      if (!rank) { bad++; console.log(`FAIL ${c.id} ${view}: the scenario's place among the states is not in the page`); }
      else { add(c, view, "states:rank", Number(rank[1]), rank[1], 0); add(c, view, "states:count", Number(rank[2]), rank[2], 0); }
    }
  }

  const body = {
    _about: "Local impact (/impact): every figure the page shows for the addresses below, read from the page's own view (site/app/impact/Forecast.tsx) drawn to HTML by site/scripts/impact-figures.mjs with the page's own parameters and nlr_jedi_multipliers. A figure is its case, its scenario (a or b) and its name: the names of docs/methods/forecast.md, section 11 (c:, o:, sum:, pv:, y1:, year:), cell:<row> for a cell of the A and B table the page draws with no number (its words and hover in `shown`), default:<field> for a default of the left box, states:jobs:<place>:<state>:<effect> and states:taxes:<place>:<state> for the two charts of the scenario in other states (the ten most, the scenario's own, the five fewest), states:rank and states:count for the scenario's place. `page` is the value the page holds before rounding, `shown` the text it draws, `tolerance` half of the last digit it draws. The replication (replicate.py) recomputes each from the method note, the parameter files and the table.",
    written_by: "site/scripts/impact-figures.mjs, session 7506 (chain 304), 16 November 2026",
    table: "nlr_jedi_multipliers (the 24 jobs, earnings and output rows of each technology and state)",
    cases: cases.map((c) => ({ id: c.id, what: c.what, address: c.address, query: c.query, project: c.project ?? null, inputs_key: { a: F.inputsKey(c.inputs.a), b: F.inputsKey(c.inputs.b) } })),
    figures,
  };
  const json = `${JSON.stringify(body, (k, v) => v, 1)}\n`;
  const q = (s) => (/[",\n]/.test(String(s)) ? `"${String(s).replace(/"/g, '""')}"` : String(s));
  const csv = ["case,scenario,figure,page,shown,tolerance", ...figures.map((f) => [f.case, f.scenario, f.figure, f.page ?? "", f.shown, f.tolerance ?? ""].map(q).join(","))].join("\n") + "\n";
  const jf = path.join(out, "page_figures.json"), cf = path.join(out, "page_figures.csv");
  if (checkOnly) {
    const same = fs.existsSync(jf) && fs.readFileSync(jf, "utf8") === json && fs.existsSync(cf) && fs.readFileSync(cf, "utf8") === csv;
    console.log(`${same ? "ok  " : "FAIL"} page_figures.json and page_figures.csv ${same ? "are" : "are not"} what the page draws today: ${figures.length} figures of ${cases.length} addresses`);
    if (!same) bad++;
  } else {
    fs.writeFileSync(jf, json);
    fs.writeFileSync(cf, csv);
    console.log(`wrote ${figures.length} figures of ${cases.length} addresses (${figures.filter((f) => f.page === null).length} drawn with no number) to page_figures.json and .csv in ${out}`);
  }
  if (bad) process.exitCode = 1;
}
