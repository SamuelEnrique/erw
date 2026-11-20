// Energy Research Warehouse (ERW) site, ruling alternative 2 of /severance (session 7702, finished by session 7900,
// 17 November 2026; branch wip/alt-severance-2, not a default on main): the page says, in a hover by "Tax at the base
// rate", that the base rate read as a state's collections is 22 to 25 percent above what Texas collected for oil
// (docs/reviews/ruling-impact-severance-2026-11-17.md, line 2). main says it in the method note only. No figure that
// stands on the page moves. The figures pinned are the replication's cross-check (replication/severance/crosscheck.json):
// the copy the page reads (data/severance_collections.json) is held to it row by row, and the hover is drawn with the
// calculator's own code.
//   node --import ./scripts/tsx-register.mjs scripts/test-alt-severance-2.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), "utf-8"));
const rules = read("../data/severance_rules.json");
const copy = read("../data/severance_collections.json");
const cross = read("../../replication/severance/crosscheck.json");
const { Calculator } = await import("../app/severance/Calculator.tsx");
let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const words = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();

// the copy against the replication's cross-check, row by row
const rowOf = (r) => cross.rows.find((x) => x.what.startsWith(`Texas oil production tax, fiscal ${r.fiscal_year}:`) && x.what.includes(r.price.startsWith("WTI") ? "WTI Cushing monthly mean" : "Texas first purchase price"));
ok(copy.texas_oil.length === 4 && copy.texas_oil.every((r) => { const x = rowOf(r); return x && x.ours === r.ours_usd && x.theirs === r.collected_usd; }),
  "the four Texas oil rows the page reads equal the replication's cross-check: ours and the Comptroller's, to the dollar");
const pc = (r) => ((r.ours_usd / r.collected_usd - 1) * 100).toFixed(1);
const by = (fy, wti) => copy.texas_oil.find((r) => r.fiscal_year === fy && r.price.startsWith("WTI") === wti);
ok(pc(by(2025, true)) === "25.0" && pc(by(2026, true)) === "22.8", "at the tool's default price (WTI Cushing): 25.0 percent above for fiscal 2025, 22.8 for fiscal 2026");
ok(pc(by(2025, false)) === "23.0" && pc(by(2026, false)) === "22.1", "at EIA's Texas first purchase price: 23.0 percent above for fiscal 2025, 22.1 for fiscal 2026");

// the hover as the calculator draws it
const html = renderToStaticMarkup(h(Calculator, { rules, prices: { oil: 102.07, gas: 2.99, label: { oil: "WTI Cushing, October 2026 mean", gas: "Henry Hub, October 2026 mean" } } }));
const m = html.match(/<span role="tooltip" id="tip-sev-base-collections"[^>]*>([\s\S]*?)<\/span><\/span>/);
const tip = m ? words(m[1]) : "";
console.log(`     ${tip}`);
ok(tip.includes("$6,729,074,711 for fiscal 2025 against $5,383,668,225 collected (25.0 percent above)") && tip.includes("$7,215,622,875 for fiscal 2026 against $5,876,551,070 collected (22.8 percent above)"),
  "the hover gives both fiscal years at the default price: $6,729,074,711 against $5,383,668,225 (25.0 percent above), $7,215,622,875 against $5,876,551,070 (22.8)");
ok(tip.includes("23.0 percent above for fiscal 2025 and 22.1 percent above for fiscal 2026"), "the hover gives the first purchase price's 23.0 and 22.1 percent");
ok(tip.includes("Default on the site: said in the method note only.") && tip.includes("Source: Texas Comptroller, Historical All Funds (Excluding Trusts) Revenue") && tip.includes("Not measured here:"),
  "the hover names the site's default, its source and what is not measured");
ok(words(html).includes("$4,695.22") && words(html).includes("$102,070.00"), "no figure that stands moves: the calculator opens on gross $102,070.00 and tax $4,695.22, as on main");
console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
