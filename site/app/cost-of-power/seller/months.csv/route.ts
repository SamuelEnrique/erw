// Energy Research Warehouse (ERW) site, session 212: GET /cost-of-power/seller/months.csv?iso=..&asset=..&hub=..&mw=..
// Every month of "What a generator earns" for the plant the address names, as CSV: the rows the page's section "Month
// by month" and its fold "Every month" drew until this session (the owner's chain prompt of 12 October 2026, the
// battery page's layout: monthly rows go into the CSV download). The same read and arithmetic as the page (model.ts;
// lib/merchant.ts, months), and scenario A's fixed O&M and debt payments as the address has them
// (lib/seller/finance.ts), so each month's coverage is the page's. Provenance in '#' lines at the top, as in the ERW's
// own CSVs. The address takes the seller page's status (lib/release.ts): in review, it answers a visitor as the page does.
import { hubAt } from "@/lib/capture";
import { statusOf } from "@/lib/release";
import { internalView } from "../../battery/read";
import { cell, csv, text } from "../csv";
import { modelOf } from "../model";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;
  const q = Object.fromEntries([...sp.entries()]) as Record<string, string | undefined>;
  // the proxy (site/proxy.ts) never sees a path with an extension, so the page's status is applied here: in review, the
  // CSV answers the internal view alone, as the page does
  if (!(await internalView()) && statusOf("/cost-of-power/seller") === "review") return text("in review: this download opens with the page it belongs to", 404);
  let M;
  try {
    M = await modelOf(q);
  } catch (e) {
    return text(`the model could not be read: ${e instanceof Error ? e.message : String(e)}`, 503);
  }
  const { x, g, a, hub, at, ms, snap, atHub, sizeLabel } = M;
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const head = [
    `# Energy Research Warehouse (ERW): every month of "What a generator earns", ${a.name.toLowerCase()}, ${sizeLabel}, ${g.name}, priced at ${at}`,
    `# source: the model's snapshot data/merchant_snapshot.json (warehouse/derived/merchant_revenue.py), built ${snap.built.slice(0, 10)}${atHub ? `, solved again at ${hubAt(hub.id)}'s own price (data/seller/hubs)` : ""}; derived by the ERW from ${g.name}'s public prices and EIA-930's hourly generation by source; read at ${now}`,
    `# USD for ${sizeLabel}; energy in MWh. A month is held when at least 90 percent of its hours (a battery: its days) are priced; the others are shown and not counted`,
    `# coverage: the month's revenue less a twelfth of fixed O&M (USD ${x.fom} per kW a year), over a twelfth of the debt payments (USD ${x.ds} a year): scenario A's as the address has them; blank with no debt`,
    `# method: /data/methods/generator_earns_algorithm (sections 3 and 4); the page: /cost-of-power/seller`,
  ];
  const cols = ["month", "held", "share_of_hours_held", "revenue_usd", "energy_mwh", "capture_usd_per_mwh", "flat_usd_per_mwh", "capture_rate_pct", "coverage"];
  const lines = [...head, cols.join(",")];
  const f = (v: number | null, d: number) => (v === null || !Number.isFinite(v) ? "" : v.toFixed(d));
  for (const r of ms) {
    lines.push([r.m, r.held ? "yes" : "no", f(r.share, 4), String(Math.round(r.revenue)), f(r.energy, 2), f(r.capture, 4), f(r.flat, 4), f(r.rate, 2), f(r.dscr, 4)].map(cell).join(","));
  }
  return csv(lines, `erw_generator_months_${x.iso}_${x.asset}_${hub.id.replace(/[^A-Za-z0-9_.-]/g, "_")}.csv`);
}
