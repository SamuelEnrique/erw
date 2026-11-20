// Energy Research Warehouse (ERW) site, ruling alternative 2 of /grid/caiso/alerts (session 7714, 17 November 2026; branch
// wip/alt-caiso-alerts-2, not a default on main). The cells the page draws with its own rule (app/grid/caiso/alerts/page.tsx,
// `t`: toLocaleString en-US, at most two decimals) from a figure stored to four decimals (main) and to six (the branch).
//   node scripts/alt-caiso-alerts-figures.mjs
const t = (x) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
const stored = (v, d) => Number(v.toFixed(d));
// the day's percent at the builder's full precision, as the replication sums it from the hours (docs/reviews/ruling-impact-caiso-alerts-2026-11-17.md, line 2)
const cases = { "2021-07-29 percent": -0.174972 };
const out = {};
for (const [k, v] of Object.entries(cases)) out[k] = { main: t(stored(v, 4)), branch: t(stored(v, 6)), true: t(v) };
process.stdout.write(JSON.stringify(out));
