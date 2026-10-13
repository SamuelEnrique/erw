// Energy Research Warehouse (ERW) site, session 213: GET /cost-of-power/months.csv?grid=..&region=..&mw=..&run=..&buy=..
// Every month and every year of "What a datacenter pays" for the load the address names, as CSV: the rows the page's
// folds "Every month" and "Every year" drew until this session (the owner's chain prompt of 12 October 2026, the
// battery page's layout: monthly rows go into the CSV download). The same read and arithmetic as the page (model.ts;
// lib/datacenter.ts). A year's rows come first (kind "year"), then the months (kind "month"). Provenance in '#' lines
// at the top. The address takes the page's status (lib/release.ts): in review, it answers a visitor as the page does.
import { statusOf } from "@/lib/release";
import { INDEX } from "@/lib/datacenterdata";
import { internalView } from "../battery/read";
import { cell, csv, text } from "../seller/csv";
import { inputsFrom, loadModel } from "../model";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;
  const q = Object.fromEntries([...sp.entries()]) as Record<string, string | undefined>;
  // the proxy (site/proxy.ts) never sees a path with an extension, so the page's status is applied here: in review, the
  // CSV answers the internal view alone, as the page does
  if (!(await internalView()) && statusOf("/cost-of-power") === "review") return text("in review: this download opens with the page it belongs to", 404);
  let M;
  try {
    M = loadModel(inputsFrom(q), typeof q.buy === "string", q.grid, q);
  } catch (e) {
    return text(`the price files could not be read: ${e instanceof Error ? e.message : String(e)}`, 503);
  }
  if (M.failed) return text(`the price files could not be read: ${M.failed}`, 503);
  const { x, g, flex, off, ms, ys, ysH, msH, market, rule, size } = M;
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const f2 = (v: number | null | undefined) => (v === null || v === undefined || !Number.isFinite(v) ? "" : v.toFixed(2));
  const head = [
    `# Energy Research Warehouse (ERW): every month and every year of "What a datacenter pays", ${size} at ${x.region} in ${g?.name ?? x.grid}, buying ${market}, ${flex ? `a flexible load (${rule})` : "a flat load"}`,
    `# source: the site's own files of hourly hub and zone prices (data/datacenter, warehouse/derived/datacenter_page.py), built ${INDEX.built.slice(0, 10)}; derived by the ERW from the grid's public prices; read at ${now}`,
    `# USD per MWh: flat is a flat load over the hours held; this load is the load as described, under a rule decided before each hour (section 5.1 of the method); foreseen is the same load with its hours chosen knowing the year's prices. A month is complete when at least 95 percent of its hours are held; a year when all twelve of its months are. usd is the cost for ${size}`,
    `# method: /data/methods/datacenter_pays_algorithm (sections 4.1, 4.6 and 5); the page: /cost-of-power`,
  ];
  const cols = ["kind", "period", "complete", "flat_usd_per_mwh", "this_load_usd_per_mwh", "foreseen_usd_per_mwh", "hours_off", "usd", "held", "due"];
  const lines = [...head, cols.join(",")];
  for (const r of [...ys].reverse()) {
    const h = ysH.find((k) => k.y === r.y);
    lines.push(["year", r.y, r.complete ? "yes" : "no", f2(r.flat), flex ? f2(r.per) : "", flex && h?.per != null ? f2(h.per) : "", off ? String(Math.round(r.down)) : "", String(Math.round(r.cost * x.mw)), `${r.months} months`, "12 months"].map(cell).join(","));
  }
  for (const r of [...ms].reverse()) {
    const h = msH.get(r.m);
    lines.push(["month", r.m, r.complete ? "yes" : "no", f2(r.flat / r.held), flex && r.energy ? f2(r.cost / r.energy) : "", flex && h?.energy ? f2(h.cost / h.energy) : "", off ? String(Math.round(r.down)) : "", String(Math.round(r.cost * x.mw)), `${Math.round(r.held)} hours`, `${Math.round(r.due)} hours`].map(cell).join(","));
  }
  return csv(lines, `erw_datacenter_months_${x.grid}_${x.region.replace(/[^A-Za-z0-9_.-]/g, "_")}_${x.buy}_${x.run}.csv`);
}
