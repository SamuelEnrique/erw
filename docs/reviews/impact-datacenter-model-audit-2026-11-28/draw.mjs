// Session 11404 (chain 770): /impact drawn to HTML with the page's own components for datacenter addresses, and the A and
// B table's datacenter cells printed as text, to read the words a fix branch adds. No server, no network.
// Run from site/: node --import ./scripts/tsx-register.mjs ../runs/c770/s11404/draw.mjs <address> [<address> ...]
import fs from "node:fs";
import { createRequire } from "node:module";
const req = createRequire(new URL("../../../site/package.json", import.meta.url));
const { createElement: h } = req("react");
const { renderToStaticMarkup } = req("react-dom/server");

const F = await import("../../../site/lib/forecast.ts");
const D = await import("../../../site/lib/forecastdata.ts");
const U = await import("../../../site/lib/forecastui.ts");
const { Forecast } = await import("../../../site/app/impact/Forecast.tsx");
const lines = fs.readFileSync("C:/Users/lossa/Documents/erw/warehouse/output/nlr_jedi_multipliers.csv", "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const head = lines[0].split(",");
const at = (k) => head.indexOf(k);
const rows = lines.slice(1).map((l) => l.split(",")).filter((c) => ["jobs", "earnings", "output"].includes(c[at("variable")]))
  .map((c) => ({ entity: c[at("entity")], variable: c[at("variable")], ts_utc: c[at("ts_utc")], value: Number(c[at("value")]) }));
const P = D.params(), P2 = D.dcParams(), dcList = D.dcProjectList(), jedi = F.pack(rows), rules = D.gasSeverance();
const text = (s) => s.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/&#x27;|&apos;/g, "'").replace(/&quot;/g, "\"").replace(/\s+/g, " ").trim();
for (const qs of process.argv.slice(2)) {
  const q = Object.fromEntries(new URLSearchParams(qs));
  const start = U.withProjects(U.parse(q), q, [], dcList.map((p) => p.id), dcList);
  const html = renderToStaticMarkup(h(Forecast, { P, P2, dcList, jedi, start, rules, planned: [] }));
  console.log(`\n== /impact?${qs}  (${html.length} characters)`);
  for (const m of html.matchAll(/<tr[^>]*data-row="([^"]+)"[^>]*>([\s\S]*?)<\/tr>/g)) {
    const cells = [...m[2].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((c) => text(c[1]));
    const titles = [...m[2].matchAll(/<td[^>]*>[\s\S]*?title="([^"]*)"/g)].map((c) => c[1].replace(/&#x27;|&apos;/g, "'"));
    console.log(`  ${m[1]}: ${cells.join(" | ")}${titles.length ? `   [hover: ${titles.join(" / ").slice(0, 300)}]` : ""}`);
  }
  for (const m of html.matchAll(/data-(left-out|before-exemption|onsite-only)="([^"]*)"/g)) console.log(`  mark ${m[1]}=${m[2]}`);
  if (process.env.DRAW_GREP) for (const w of process.env.DRAW_GREP.split("|")) console.log(`  "${w}": ${text(html).includes(w) ? "present" : "absent"}`);
}
