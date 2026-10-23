// Energy Research Warehouse (ERW) site, session 2300 (chain 087): the source of every figure the project map computes in
// the browser, without a browser. lib/projectmap.ts, sourceOf: a figure summed from the page's own copy of the tables
// (data/map.json) carries data-source="<tables>|<vintage>|<rule>" and a tip with the same words (components/tool/
// ToolPage.tsx, Tip). This test reads the file's header as the page does and checks:
//   1. the tables a kind names are the file's own, in the file's order: the two EIA tables for the units, energy_projects
//      for the queue, datacenter_facilities for the datacenters, all four for "all";
//   2. the vintage is the kind's: EIA's month for the units, the queue's and the tracker's days, the build day for all;
//   3. the attribute has three parts and the words name every table, the vintage and the rule;
//   4. the page's components use them: ProjectMap.tsx gives data-source to the sentence's figures, the totals, the
//      technology table's counts and MW and the rows not drawn, and a Tip to each; page.tsx to the unit count;
//      QueueCharts.tsx frames each chart with data-source naming iso_queue_statistics and the ISO's queue table.
//
//   node --import ./scripts/alias-register.mjs scripts/test-map-sources.mjs
//
// Exit 1 on a failure. No request, no browser.
import fs from "node:fs";
import { SOURCE_RULE, sourceOf, sourceTables, sourceVintage, sourceWords } from "../lib/projectmap.ts";

let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf-8");
const f = JSON.parse(read("../data/map.json"));
const head = { tables: f.tables, vintage: f.vintage, vintages: f.vintages, built: f.built };

// 1 and 2: the tables and the vintage of each kind, on the file as it stands
check(JSON.stringify(sourceTables(head, "units")) === JSON.stringify(f.tables.filter((t) => t.startsWith("eia860m"))) && sourceTables(head, "units").length === 2, `units: the two EIA tables (${sourceTables(head, "units").join(", ")})`);
check(JSON.stringify(sourceTables(head, "queue")) === JSON.stringify(["energy_projects"]), "queue: energy_projects");
check(JSON.stringify(sourceTables(head, "datacenter")) === JSON.stringify(["datacenter_facilities"]), "datacenter: datacenter_facilities");
check(JSON.stringify(sourceTables(head, "all")) === JSON.stringify(f.tables), `all: the file's ${f.tables.length} tables in its order`);
check(sourceVintage(head, "units") === f.vintage && /^\d{4}-\d{2}$/.test(f.vintage), `units: EIA's month ${f.vintage}`);
check(sourceVintage(head, "queue") === f.vintages.queue && /^\d{4}-\d{2}-\d{2}$/.test(f.vintages.queue), `queue: the day ${f.vintages.queue}`);
check(sourceVintage(head, "datacenter") === f.vintages.datacenter, `datacenter: the day ${f.vintages.datacenter}`);
check(sourceVintage(head, "all") === f.built.slice(0, 10), `all: the build day ${f.built.slice(0, 10)}`);

// a fixture, so the rule holds whatever the file says today
const fx = { tables: ["eia860m_operating_generators", "eia860m_planned_generators", "energy_projects", "datacenter_facilities"], vintage: "2026-08", vintages: { operating: "2026-08", planned: "2026-08", queue: "2026-10-19", datacenter: "2026-10-22" }, built: "2026-10-22T17:48:54Z" };
check(sourceOf(fx, "queue", SOURCE_RULE.chosen) === "energy_projects|2026-10-19|summed over the rows chosen", "fixture: the queue's attribute is energy_projects|2026-10-19|summed over the rows chosen");
check(sourceOf(fx, "units", SOURCE_RULE.file) === "eia860m_operating_generators,eia860m_planned_generators|2026-08|counted over the whole file", "fixture: the units' attribute names both EIA tables and EIA's month");
check(sourceOf(fx, "all", SOURCE_RULE.chosen).split("|").length === 3 && sourceOf(fx, "all", SOURCE_RULE.chosen).startsWith(fx.tables.join(",") + "|2026-10-22|"), "fixture: all four tables, dated by the build");

// 3: the words
for (const kind of ["units", "queue", "datacenter", "all"]) {
  const w = sourceWords(fx, kind, SOURCE_RULE.chosen);
  check(sourceTables(fx, kind).every((t) => w.includes(t)) && w.includes(kind === "units" ? "2026-08" : kind === "all" ? "built 2026-10-22" : `vintage ${sourceVintage(fx, kind)}`) && w.includes(SOURCE_RULE.chosen) && w.includes("built 2026-10-22"),
    `words (${kind}): name every table, the vintage, the build day and the rule`);
  check(!/—/.test(w), `words (${kind}): no em dash`);
}

// 4: the components carry them
const pm = read("../app/map/ProjectMap.tsx"), pg = read("../app/map/page.tsx"), qc = read("../app/map/QueueCharts.tsx"), qv = read("../app/map/QueuesView.tsx"), rm = read("../app/resources/ResourceMap.tsx");
check(/<strong data-source=\{su\}>/.test(pm) && /<strong data-source=\{sq\}>/.test(pm) && /<strong data-source=\{sd\}>/.test(pm), "ProjectMap: the sentence's figures carry data-source by kind");
check(/data-map-total=\{s\.slug\} data-source=\{srcOf\(f, s\.kind\)\}/.test(pm), "ProjectMap: every total carries data-source of its status's kind");
check(/data-tech-count=[^\n]*data-source=\{srcOf\(f, kinds\[j\]\)\}/.test(pm) && /data-tech-mw=[^\n]*data-source=\{srcOf\(f, kinds\[j\]\)\}/.test(pm), "ProjectMap: the technology table's counts and MW carry data-source");
check(/data-map-not-drawn="1" data-source=/.test(pm), "ProjectMap: the rows not drawn carry data-source");
check(/<dl [^\n]*data-source=\{`\$\{c\.table\}\|/.test(pm), "ProjectMap: the unit card's fields carry the row's table and vintage");
for (const id of ["map-sentence", "map-totals-${group}", "map-drawn", "map-by-technology"]) check(pm.includes(`id={\`${id}\`}`) || pm.includes(`id="${id}"`), `ProjectMap: a Tip ${id}`);
check(/data-map-units="1" data-source=\{sourceOf\(f, "units", SOURCE_RULE\.file\)\}/.test(pg) && pg.includes('id="map-units"'), "page: the unit count carries data-source and a Tip");
check((qc.match(/<div data-source=\{sourceOf\(iso, "/g) ?? []).length === 3 && qc.includes("iso_queue_statistics") && qc.includes("_interconnection_queue|"), "QueueCharts: each of the three charts is framed with data-source naming the table and the ISO's queue table");
check(qv.includes("iso={iso}") && qv.includes('id="queue-table"'), "QueuesView: the charts get the ISO and the table has its Tip");
check((rm.match(/data-count-value="[a-z_]+" data-source=/g) ?? []).length === 7, "ResourceMap: the seven counts carry data-source");
for (const [name, text] of [["ProjectMap", pm], ["page", pg], ["QueueCharts", qc], ["QueuesView", qv], ["projectmap.ts", read("../lib/projectmap.ts")]]) check(!/—/.test(text), `${name}: no em dash`);

// session 2301: the hover card's words of a mark, one row of each kind of the file, and a state's
{
  const { hoverOf, stateHover, KIND } = await import("../lib/projectmap.ts");
  for (const k of f.kinds) {
    if (!k.rows) continue;
    const i = k.start;
    const h = hoverOf(f, i);
    const kind = f.k[i];
    const table = kind === KIND.operating ? "eia860m_operating_generators" : kind === KIND.planned ? "eia860m_planned_generators" : kind === KIND.queue ? "energy_projects" : "datacenter_facilities";
    const when = kind <= KIND.planned ? f.vintage : kind === KIND.queue ? f.vintages.queue : f.vintages.datacenter;
    check(h.name.length > 0 && h.source.includes(table) && h.source.includes(when) && h.source.includes(f.built.slice(0, 10)) && h.click === "Click for its card."
      && (f.mw[i] === null ? h.figure === "MW not stated" : /\d MW/.test(h.figure)) && (kind !== KIND.queue || (h.figure.endsWith(" requested") && h.where.startsWith("Queue position, "))),
      `hover (${k.slug}): "${h.name}", ${h.figure}; ${h.where}; ${h.source}`);
  }
  check(stateHover("Texas", 1, false) === "Texas: 1 row chosen in it. Click to choose it." && stateHover("Texas", 1200, true) === "Texas: 1,200 rows chosen in it. Click to take it away.", "a state's hover counts the rows chosen and says what a click does");
  check(/hoverOf\(f, i\)/.test(pm) && /stateHover\(/.test(pm) && /font-family:var\(--font-mono\)/.test(pm) && !/one\(mw\)/.test(pm), "ProjectMap: the tooltip draws hoverOf's words with the figure in mono, and a state's hover from stateHover");
}

console.log(`${n - bad} of ${n} passed`);
process.exit(bad ? 1 : 0);
