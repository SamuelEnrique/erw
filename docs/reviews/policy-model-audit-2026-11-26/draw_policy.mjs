// Session 10217: the monitor view of /policy drawn to HTML with the site's own components (no build, no server, no
// browser), as it opens on the page's day: MonitorView whole (filters, calendar, table, charts and the states' laws), with
// no state chosen and with Texas chosen. Writes the visible text of each to <out>-<case>.txt and prints its size, so a
// words branch's new sentences can be read in what the page draws.
//   cd site && node --import ./scripts/tsx-register.mjs ../runs/c10217/draw_policy.mjs 2026-11-26 ../runs/c10217/draw-main
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

// react from the site's own node_modules (this script sits outside site/)
const require = createRequire(path.join(process.cwd(), "package.json"));
const { createElement: h } = require("react");
const { renderToStaticMarkup } = require("react-dom/server");

const today = process.argv[2];
const outBase = process.argv[3];
const M = await import("../../site/lib/policymonitor.ts");
const L = await import("../../site/lib/largeloadrules.ts");
const { MonitorView } = await import("../../site/app/policy/MonitorView.tsx");
const read = (p) => JSON.parse(fs.readFileSync(new URL(`../../site/${p}`, import.meta.url), "utf-8"));
const m = read("data/policy/monitor.json");
const ll = read("data/siting/large_load_rules.json");
const byState = (rows) => { const o = {}; for (const r of rows) for (const s of L.statesOf(r.state)) o[s] = (o[s] ?? 0) + 1; return o; };
const laws = { laws: ll.laws, held: ll.held_laws, built: ll.built, retrieved: ll.retrieved, searches: ll.law_searches ?? [],
  rules: byState([...ll.rules, ...ll.held_rules]), changes: byState(ll.changes) };
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\s+/g, " ");
const titles = (html) => [...html.matchAll(/title="([^"]*)"/g)].map((x) => x[1].replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&"));
const cases = { open: M.filtersOf({ view: "monitor" }), tx: M.filtersOf({ view: "monitor", state: "TX" }) };
for (const [name, opened] of Object.entries(cases)) {
  const html = renderToStaticMarkup(h(MonitorView, { rows: m.rows, built: m.built, held: m.records, opened, today, laws }));
  const t = text(html);
  fs.writeFileSync(`${outBase}-${name}.txt`, t + "\n\n---- hovers ----\n" + titles(html).join("\n") + "\n");
  const dash = html.includes(String.fromCharCode(0x2014));
  console.log(`${name}: ${html.length} characters of HTML, ${t.length} of text, ${titles(html).length} hovers, em dash ${dash ? "PRESENT" : "none"}`);
}
