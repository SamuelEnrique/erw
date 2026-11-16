// Energy Research Warehouse (ERW) site, session 7404 (chain 303): every figure of the deal tracker (/deals and its
// views: the table, the tracker tab, the comparables with the disclosed prices, the AI-power view, the charts, and
// /deals/capital), as the page computes it.
//
//   node scripts/deal-tracker-figures.mjs <rows dir> [month YYYY-MM]
//
// <rows dir> holds energy_deals.json, the table as the live set serves it (replication/deals/fetch_rows.py). The page's
// own functions are run on those rows (lib/dealsview.ts, lib/deals2.ts, lib/dealsai.ts) with the register's folded
// pairs (data/deal_duplicates.json) and the capital view's file (data/capital.json). energy_deals is held (license
// needed), so the built page draws none of these figures: this is what it draws once the hold allows. Prints one JSON
// object: { month, figures: {key: value}, words: {key: text} }. replication/deals/replicate.py compares it with its own
// computation. No network, nothing written.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const V = await import("../lib/dealsview.ts");
const D = await import("../lib/deals2.ts");
const A = await import("../lib/dealsai.ts");

const dir = process.argv[2];
const month = process.argv[3] ?? new Date().toISOString().slice(0, 7);
const rows = JSON.parse(fs.readFileSync(path.join(dir, "energy_deals.json"), "utf-8"));
const site = (...p) => JSON.parse(fs.readFileSync(path.join(here, "..", ...p), "utf-8"));
const pairs = site("data", "deal_duplicates.json").pairs;
const out = {}, words = {};
const dash = (v) => (v === "" ? "-" : v);

// 1. the table (app/deals/page.tsx, DealsTable.tsx): the rows as the table lists them, the month's three cells, and
//    the counts its filters give (the table lists every row of the table: the register's pairs are not folded here)
const table = rows.map(V.rowOf);
const m = V.monthBlock(table, month);
out["table|rows"] = table.length;
out[`deals|month_count|${m.month}`] = m.deals;
out[`deals|month_mw|${m.month}`] = m.mw;
out[`table|month_with_mw|${m.month}`] = m.withMw;
if (m.aiPct !== null) out[`deals|month_ai_pct|${m.month}`] = m.aiPct;
words["table|month"] = `${m.month}${m.empty ? " (the month before: no deal dated in the month drawn)" : ""}`;
const f = (patch) => V.filterRows(table, { ...V.NO_INPUTS, ...patch }).length;
out["table|filter|ai|yes"] = f({ ai: "yes" });
out["table|filter|ai|no"] = f({ ai: "no" });
out["table|filter|price|yes"] = f({ price: "yes" });
out["table|filter|mw_from|500"] = f({ mwMin: "500" });
for (const [k] of V.KINDS) out[`table|filter|kind|${k}`] = f({ kind: k });
for (const s of [...V.STAGES, "none"]) out[`table|filter|stage|${s}`] = f({ stage: s });
out["table|with_mw"] = table.filter((d) => d.mw !== null).length;
out["table|with_usd"] = table.filter((d) => d.dollars !== null).length;
out["table|with_flags"] = table.filter((d) => d.flags.length).length;
const sure = table.flatMap((d) => (d.confidence === null ? [] : [d.confidence])).sort((a, b) => a - b);
if (sure.length) { out["table|sure_min"] = sure[0]; out["table|sure_max"] = sure[sure.length - 1]; }

// 2. the tracker tab (app/deals/v2/view.tsx): the folded deals, their counts, the panel's brackets, the months
const all = D.fold(rows.map(D.toDeal), pairs);
const c = D.counts(all);
Object.assign(out, { "tracker|deals": c.deals, "tracker|with_mw": c.withMw, "tracker|mw": c.mw, "tracker|with_price": c.withPrice,
  "tracker|with_other_price": c.withOtherPrice, "tracker|with_dollars": c.withDollars });
out["tracker|folded"] = pairs.filter((p) => p.ruling === "fold" && all.some((d) => d.folded.includes(p.duplicate))).length;
for (const g of D.GROUPS) out[`tracker|type|${g.id}`] = c.byGroup[g.id];
for (const k of D.KINDS) out[`tracker|kind|${k.id}`] = all.filter((d) => d.kinds.includes(k.id)).length;
for (const t of D.technologies(all)) out[`tracker|technology|${t.value}`] = t.n;
for (const g of D.GRIDS) out[`tracker|grid|${g}`] = all.filter((d) => d.grid === g).length;
for (const y of new Set(all.map((d) => d.year))) out[`tracker|year|${y}`] = all.filter((d) => d.year === y).length;
for (const s of D.STATUSES) out[`tracker|status|${s}`] = all.filter((d) => d.status === s).length;
out["tracker|view|storage"] = all.filter((d) => d.storage).length;
out["tracker|view|ai"] = all.filter((d) => d.ai).length;
for (const p of D.parties(all)) out[`tracker|party|${p.name}`] = p.n;
for (const x of D.months(all, all)) out[`tracker|month|${x.month}`] = x.n;
out["tracker|with_state"] = all.filter((d) => d.state).length;
out["tracker|with_grid"] = all.filter((d) => d.grid).length;
words["tracker|summary"] = D.summary(all, all, D.inputsOf({}, all));

// 3. the comparables and the disclosed prices (app/deals/comparables/view.tsx)
for (const dim of D.DIMENSIONS.map((d) => d.id)) {
  for (const cell of D.comparables(all, dim)) {
    out[D.compKey("deals", dim, cell.value)] = cell.deals;
    out[D.compKey("with_price", dim, cell.value)] = cell.withPrice;
    out[D.compKey("with_mw", dim, cell.value)] = cell.withMw;
    if (cell.medianPrice !== null) out[D.compKey("median_price", dim, cell.value)] = cell.medianPrice;
    if (cell.medianMw !== null) out[D.compKey("median_mw", dim, cell.value)] = cell.medianMw;
  }
}
out["deals|priced"] = D.priced(all).length;
for (const dim of D.PRICE_DIMENSIONS.map((d) => d.id)) {
  for (const cell of D.priceCells(all, dim)) {
    out[D.priceKey("count", dim, cell.value)] = cell.count;
    for (const stat of ["median", "low", "high"]) if (cell[stat] !== null) out[D.priceKey(stat, dim, cell.value)] = cell[stat];
  }
}

// 4. the AI-power view (app/deals/ai/view.tsx): the tagged deals by four dimensions, and the two lists of ten
out["deals|ai_tagged"] = all.filter((d) => d.ai).length;
for (const dim of A.AI_DIMENSIONS.map((d) => d.id)) {
  for (const cell of A.aiCells(all, dim)) {
    out[A.aiKey("deals", dim, cell.value)] = cell.deals;
    if (cell.mw !== null) out[A.aiKey("mw", dim, cell.value)] = cell.mw;
    out[A.aiKey("with_mw", dim, cell.value)] = cell.withMw;
    if (cell.usd !== null) out[A.aiKey("usd", dim, cell.value)] = cell.usd;
    out[A.aiKey("with_usd", dim, cell.value)] = cell.withUsd;
  }
}
const supply = all.filter((d) => A.supplyOf(d) !== "capital");   // the lists leave out the capital deals (deals faults row 3)
for (const by of ["mw", "usd"]) {
  A.largest(supply, by).forEach((d, i) => {
    out[`deals|ai_top_${by}|${i + 1}`] = by === "mw" ? d.mw : d.dollars;
    words[`deals|ai_top_${by}|${i + 1}`] = d.id;
  });
}

// 5. the four charts (app/deals/charts/view.tsx: lib/dealsai.ts figures)
Object.assign(out, A.figures(all));

// 6. /deals/capital: under the hold its file holds the table's row count alone
const cap = site("data", "capital.json");
out["capital|n_rows"] = cap.n_rows;
words["capital|file"] = `built ${cap.built}; held ${cap.held}`;

console.log(JSON.stringify({ month, figures: out, words }));
