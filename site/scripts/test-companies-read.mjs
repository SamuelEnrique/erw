// Energy Research Warehouse (ERW) site, session 7562: the company database read as a fund analyst would read it
// (docs/reviews/companies-read-2026-11-16.md, rows 3 and 4). The index page drawn to HTML by its own function on the
// site's own file (site/data/companies/index.json, built 2026-11-16) for two searches.
//   cd site && node --import ./scripts/battery-awards-page-register.mjs scripts/test-companies-read.mjs
import { renderToStaticMarkup } from "react-dom/server";

const { default: CompaniesPage } = await import("../app/companies/page.tsx");
const { FOOTPRINT_WORDS } = await import("../lib/companydb.ts");

let failed = 0;
const check = (ok, what) => { console.log(`${ok ? "ok  " : "FAIL"} ${what}`); if (!ok) failed++; };
const draw = async (sp) => renderToStaticMarkup(await CompaniesPage({ searchParams: Promise.resolve(sp) }));

const amazon = await draw({ q: "amazon" });
check(amazon.includes('data-companies-none="1"'), "q=amazon: no listed company matches");
check(/companies are named only in tables held for a license/.test(amazon) && amazon.includes("only from a deal or a datacenter"), "the empty answer says companies named only in held tables are not listed");

const talen = await draw({ q: "talen" });
const tip = FOOTPRINT_WORDS.replace(/'/g, "&#x27;");
check(talen.includes("counted twice") && talen.includes(tip.slice(0, 60)), "the Footprint cell's hover says a plant both operated and owned counts twice");
check(talen.includes("TalenEnergy Susquehanna LLC") && talen.includes(">4,811<") && talen.includes(">2,532<"), "Susquehanna reads 4,811 MW of footprint beside its 2,532 MW operating (2,278.8 owned counted again)");
check(!talen.includes('data-companies-none="1"'), "q=talen lists its companies, no empty line");

console.log(failed ? `${failed} failed` : "all passed");
process.exitCode = failed ? 1 : 0;
