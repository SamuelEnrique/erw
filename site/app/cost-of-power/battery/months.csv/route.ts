// Energy Research Warehouse (ERW) site, session 208: GET /cost-of-power/battery/months.csv?grid=..&dur=..&strat=..&mw=..
// Every month of "What a battery earns" for the battery the address names, as CSV: the rows the page's fold "Every
// month" drew until this session (the owner's ruling of 12 October 2026: monthly rows go into the CSV download).
// The same read as the page (read.ts), the same library (lib/batterystack.ts), and scenario A's fixed O&M and debt
// payments as the address has them (lib/battery/finance.ts), so each month's coverage is the page's. Provenance in
// '#' lines at the top, as in the ERW's own CSVs. The address takes the battery page's status (lib/release.ts): in
// review, it answers a visitor as the page does.
import { COSTS, PRODUCTS, REVIEW_TABLE, TABLE, gridOf, inputsOf, last36, monthsOf, type Inputs, type Month } from "@/lib/batterystack";
import stepsData from "@/data/battery_scenario_steps.json";
import { debtUsd, defaultsOf, parseScenarios, stepState, stepsOffered, type StepFile } from "@/lib/battery/finance";
import { statusOf } from "@/lib/release";
import { internalView, reviewRows, rowsOf } from "../read";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const text = (msg: string, status: number) => new Response(msg + "\n", { status, headers: { "Content-Type": "text/plain; charset=utf-8" } });
const cell = (v: unknown): string => {
  if (v === null || v === undefined) return "";
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
/** A month's coverage at the page's rule: the month's revenue less a month of fixed O&M, over a month of debt payments. */
const coverOf = (r: Month, x: Inputs) => (r.total === null || !r.held || x.ds <= 0 ? "" : ((r.total * 12 * x.mw - x.fom * 1000 * x.mw) / x.ds).toFixed(4));

export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;
  const q = Object.fromEntries([...sp.entries()]) as Record<string, string | undefined>;
  const internal = await internalView();
  // the proxy (site/proxy.ts) never sees a path with an extension, so the page's status is applied here: in review, the
  // CSV answers the internal view alone, as the page does
  if (!internal && statusOf("/cost-of-power/battery") === "review") return text("in review: this download opens with the page it belongs to", 404);
  const asked = inputsOf(q, internal);
  const g = gridOf(asked.grid);
  let rows;
  try {
    rows = g.review ? reviewRows(asked.grid, asked) : await rowsOf(g.entity!, asked);
  } catch (e) {
    return text(`the table could not be read: ${e instanceof Error ? e.message : String(e)}`, 503);
  }
  const ms = monthsOf(rows, asked.strat, asked.dur);
  const steps = stepsData as unknown as StepFile;
  const stepCase = steps.cases[`${asked.grid}|${asked.strat}|${asked.dur}`] ?? null;
  const offered = stepsOffered(steps, stepState(stepCase, ms, (last36(ms)?.months ?? []).map((r) => r.m)));
  const A = parseScenarios(q, defaultsOf(COSTS[asked.dur]), offered, asked.mw).a;
  const x: Inputs = { ...asked, fom: A.fom, ds: debtUsd(A, asked.mw) };
  const products = PRODUCTS[x.grid] ?? [];
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const head = [
    `# Energy Research Warehouse (ERW): every month of "What a battery earns", ${g.name}, ${x.dur}-hour, ${x.strat === "foresight" ? "perfect foresight" : "day-ahead schedule"}, ${x.mw} MW`,
    `# source table: ${g.review ? REVIEW_TABLE : TABLE} (warehouse/derived/battery_stack.py), derived by the ERW from ${g.name}'s public prices; read ${g.review ? "from the site's own copy" : "from the live set"} at ${now}`,
    `# USD for ${x.mw} MW; total_usd_per_kw is the month's total per kW of rated power. A month is held when at least 90 percent of its days are solved; a day is left out, never estimated, when an hour of its energy price or of an ancillary price is not held`,
    `# coverage: the month's revenue times twelve, less a year of fixed O&M (USD ${x.fom} per kW a year), over a year of debt payments (USD ${x.ds}): scenario A's as the address has them; blank for a month not held`,
    `# method: /data/methods/battery_earns_algorithm (sections 3 to 5); the page: /cost-of-power/battery`,
  ];
  const cols = ["month", "held", "energy_usd", "ancillary_usd", "total_usd", "total_usd_per_kw", "coverage", "days_held", "days_in_month", "days_left_out", "days_left_out_ancillary", ...products.map((p) => `${p.key}_usd`)];
  const lines = [...head, cols.join(",")];
  for (const r of ms) {
    const usd = (v: number | null | undefined) => (v === null || v === undefined ? "" : String(Math.round(v * x.mw)));
    lines.push([r.m, r.held ? "yes" : "no", usd(r.energy), usd(r.ancillary), usd(r.total), r.total === null ? "" : (r.total / 1000).toFixed(2), coverOf(r, x),
      String(r.daysHeld), String(r.daysInMonth), String(r.daysOut), String(r.daysOutAncillary), ...products.map((p) => (r.total === null ? "" : usd(r.products[p.key] ?? 0)))].map(cell).join(","));
  }
  const name = `erw_battery_months_${x.grid}_${x.dur}h_${x.strat}.csv`;
  return new Response(lines.join("\n") + "\n", {
    status: 200,
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="${name}"`, "Cache-Control": "no-store" },
  });
}
