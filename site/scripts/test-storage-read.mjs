// Energy Research Warehouse (ERW) site, session 7542 (chain 304, part C): the site rows of the read of /storage as a
// lender's analyst reads it (docs/reviews/storage-read-2026-11-16.md, rows 2, 4, 5, 6 and 7). No server, no network,
// nothing written: the helpers are called on made-up rows, the line chart is drawn to HTML with the site's own code, and
// the page files are read as text.
//   node --import ./scripts/tsx-register.mjs scripts/test-storage-read.mjs
import fs from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { DISCHARGED_TITLE, inventory, notHeld } from "../lib/storagefleet.ts";
import { LineChart, gapped } from "../components/LineChart.tsx";

let failed = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { failed += 1; console.log(`FAIL ${what}`); } };
const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf-8");

// row 2: the fleet tab names the inventory its rows are of
check(inventory([{ vintage: "2026-08" }, { vintage: "2026-09" }, { vintage: null }]) === "September 2026", "the newest vintage, as a month");
check(inventory([{}, { vintage: "" }]) === "", "no vintage, no month");
const page = read("../app/storage/page.tsx");
const data = read("../lib/data.ts");
check(/mwh:extra->>energy_capacity_mwh,vintage"/.test(data), "storageUnits reads each unit's vintage");
check(page.includes("(EIA-860M){inventory(operating) ?"), "the headline's note names the month");
check(!/^export (function|const) (inventory|notHeld)/m.test(page), "a page file exports nothing Next.js does not allow");

// row 6: days a sparkline does not hold are named on its hover
const day = (d) => ({ ts_utc: `${d}T05:00:00Z` });
check(notHeld([day("2026-11-03"), day("2026-11-09"), day("2026-11-10")]) === "; not held: 2026-11-04 to 2026-11-08", "a run of days not held");
check(notHeld([day("2026-10-31"), day("2026-11-02")]) === "; not held: 2026-11-01", "one day not held");
check(notHeld([day("2026-11-01"), day("2026-11-02")]) === "", "every day held");
check(page.includes("the last 30 days held${notHeld(dis.slice(-30))}"), "the spark's hover carries the days not held");

// row 5: hours not held break the line instead of a straight line across them
const pts = [{ t: 0, v: 1 }, { t: 3600, v: 2 }, { t: 5 * 86400, v: 3 }, { t: 5 * 86400 + 3600, v: 4 }];
const g = gapped(pts, 3600);
check(g.length === 5 && g[2].v === null && g[2].t === 7200, "one break after the last hour before the gap");
check(gapped(pts) === pts, "no gap given: the points as they are");
check((page.match(/gap: 3_600/g) ?? []).length === 3, "the three hourly line sources of the page carry the gap");
const tc = read("../components/TimeChart.tsx");
check(tc.includes("if (q[1] === null) { flush(); out.push(q); bucket = -1; continue; }"), "the thinning keeps a break, so a narrow chart breaks too");
const html = renderToStaticMarkup(createElement(LineChart, { lines: [{ label: "x", color: "accent", gap: 3600, points: pts }], unit: "MW", ariaLabel: "x" }));
const moves = (html.match(/d="M[^"]*"/g) ?? []).map((d) => (d.match(/M/g) ?? []).length);
check(moves.length === 0 || moves.some((k) => k >= 2), `drawn, the line is two pieces (${JSON.stringify(moves)})`);

// row 7: the discharge column says what it counts and names the other count of ERCOT's
check(page.includes("title={DISCHARGED_TITLE}"), "the column's hover");
check(DISCHARGED_TITLE.includes("/cost-of-power/battery/awards") && DISCHARGED_TITLE.includes("net output"), "the hover names the awards page and the net count");
check(!DISCHARGED_TITLE.includes(String.fromCharCode(0x2014)), "no em dash");

// row 4: the build-out's column of planned units says it holds those under construction too
const parts = read("../app/storage/buildout/parts.tsx");
check(parts.includes(">Under construction and planned, MW, by the year expected online</th>") && parts.includes('data-planned-head="1"'), "the column's words");
check(!parts.includes(">Planned, MW, by the year expected online<"), "the old words are gone");

// every table the read cites is public: no held row or figure is in what this session commits
const licFile = JSON.parse(read("../data/license_status.json"));
const lic = licFile.all; // every table with its status; `tables` lists only the held ones
for (const t of ["storage_capacity", "storage_daily_cycle", "eia930_all_storage", "caiso_battery_storage", "storage_buildout_monthly", "storage_owners_monthly"]) {
  check(lic[t]?.status === "public", `${t} is public`);
}
const review = fs.readFileSync(new URL("../../docs/reviews/storage-read-2026-11-16.md", import.meta.url), "utf-8");
for (const held of Object.entries(lic).filter(([, v]) => v.status !== "public").map(([k]) => k)) {
  if (new RegExp(`\\b${held}\\b`).test(review)) check(false, `the read names held table ${held}`);
}

console.log(`${n - failed} of ${n}`);
process.exitCode = failed ? 1 : 0;
