// Chain 304, part B (session 7512): "The shoulder hours" (/shoulder) read as the reader it is for, a fund analyst
// testing whether four hours of batteries is enough for the evening (docs/reviews/shoulder-read-2026-11-16.md). The
// page is drawn to HTML with the site's own code, without a build, on real rows of its table
// (tests/fixtures/session7512: the five cases' months), and each site fault the read found is held here as fixed: the
// row numbers are the review's. No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-shoulder-read.mjs [<shoulder_hours_monthly.csv>]
import fs from "node:fs";
import { register } from "node:module";
import { renderToStaticMarkup } from "react-dom/server";

// the page's frame names the brand's fonts through next/font/google, which exists only inside a build (as
// scripts/shoulder-figures.mjs: a font is its class names here, and no figure depends on one)
register(`data:text/javascript,${encodeURIComponent(`
export async function resolve(specifier, context, next) {
  if (specifier === "next/font/google") return { url: "erw-font-stub:google", shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url === "erw-font-stub:google") return { format: "module", shortCircuit: true, source:
    "const f = () => ({ className: '', variable: '', style: { fontFamily: 'stand-in' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;" };
  return next(url, context);
}`)}`);

const file = process.argv[2] ?? new URL("../../tests/fixtures/session7512/shoulder_hours_monthly.csv", import.meta.url);
const lines = fs.readFileSync(file, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const cols = lines[0].split(",");
const rows = lines.slice(1).map((l) => { const c = l.split(","); const r = Object.fromEntries(cols.map((k, i) => [k, c[i]])); return { entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: r.value }; })
  .sort((a, b) => (a.entity + "|" + a.variable + "|" + a.ts_utc < b.entity + "|" + b.variable + "|" + b.ts_utc ? -1 : 1));
const held = new Map(rows.map((r) => [`${r.entity}|${r.variable}|${r.ts_utc.slice(0, 10)}`, Number(r.value)]));

// the page's one read, answered from the file in the process
process.env.SUPABASE_URL = "http://shoulder-read.invalid";
process.env.SUPABASE_ANON_KEY = "local";
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = Object.fromEntries(u.searchParams);
  let out = [];
  if (u.pathname === "/rest/v1/series" && q.table_name === "eq.shoulder_hours_monthly") out = rows.slice(Number(q.offset ?? 0), Number(q.offset ?? 0) + Number(q.limit ?? 1000));
  return new Response(JSON.stringify(out), { status: 200, headers: { "Content-Type": "application/json", "Content-Range": `0-${out.length}/*` } });
};

const S = await import("../lib/shoulder.ts");
const B = await import("../lib/batterystack.ts");
const { default: Shoulder } = await import("../app/shoulder/page.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const draw = async (q) => renderToStaticMarkup(await Shoulder({ searchParams: Promise.resolve(q) }));
const key = (entity, variable, date) => `series|shoulder_hours_monthly|${entity}|${variable}|${date}T00:00:00Z`;
const raw = (html, k) => { const m = html.match(new RegExp(`data-check="${k.replace(/[|.*+?^${}()[\]\\]/g, "\\$&")}" data-raw="([^"]*)"`)); return m ? Number(m[1]) : undefined; };
const two = (v) => (Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
const notShown = (html) => [...html.matchAll(/<p[^>]*data-not-shown="([a-z]+)"[^>]*>([\s\S]*?)<\/p>/g)].map((m) => [m[1], words(m[2]), m[2]]);
const dash = new RegExp(`[${String.fromCharCode(0x2013)}${String.fromCharCode(0x2014)}]`);

// ---- case 1: is four hours enough for ERCOT's evening in August 2025, and was it in August 2023
const e25 = await draw({ grid: "ercot", month: "2025-08" }), e23 = await draw({ grid: "ercot", month: "2023-08" });
const sum25 = words((e25.match(/<p[^>]*data-summary="1"[^>]*>([\s\S]*?)<\/p>/) ?? ["", ""])[1]);
ok(/^In August 2025, ERCOT's evening shoulder lasted 5 hours, from 19:00 to 24:00 \(midnight\)/.test(sum25) && sum25.includes("they would need 4.30 hours on the average day"), `the case's answer is the summary's: "${sum25.slice(0, 96)}..."`);
ok(notShown(e25).length === 0 && notShown(e23).length === 0, "a month the grid holds draws no line about what is not shown");
// row 3: the daily mean the shoulder is measured against is written, not only drawn
const mean25 = held.get("iso:ercot|net_load_mean_mw|2025-08-01");
ok(mean25 !== undefined && raw(e25, key("iso:ercot", "net_load_mean_mw", "2025-08-01")) === mean25 && words(e25).includes(`the dashed line is net load's daily mean, ${two(mean25)} MW.`), `row 3: the chart's note writes net load's daily mean (${two(mean25)} MW), a row of the table`);
// row 2: the same month of another year is read on the months' chart: its hover gives the hours needed too
const need23 = held.get("iso:ercot|shoulder_hours_needed|2023-08-01");
ok(e25.includes(`<title>August 2023: shoulder 4 hours; fleet covers 1.37; hours needed ${two(need23)}</title>`) && two(need23) === "11.75", `row 2: on the August 2025 view, the months' chart says of August 2023 "hours needed ${two(need23)}"`);
ok([...e25.matchAll(/<title>[A-Z][a-z]+ \d{4}: shoulder [^<]*; hours needed ([\d.,]+|not held)<\/title>/g)].length === 2, "row 2: every month of the chart carries it (the fixture's two ERCOT months)");
// row 4: a figure not held keeps no unit
ok(!/not held hours/.test(words(e23)) && e23.includes('data-battery-hours="not held"') && words(e23).includes("the batteries' output in those shoulders is not held for ERCOT in 2023."), "row 4: 2023, when Texas's battery output is not held: no \"not held hours\", the words say what is not held");
ok(!e25.includes('data-battery-hours="not held"') && /the batteries ran 1\.00 hours at rated power in those shoulders\./.test(words(e25)), "row 4: 2025, where it is held, reads as before");

// ---- case 3: the worst day of ERCOT's 2025, how long and how deep
const worst = [...e25.matchAll(/<tr[^>]*>([\s\S]*?)<\/tr>/g)].map((m) => m[1]).filter((r) => r.includes("|worst_rank|"));
const first = worst[0] ?? "";
const pk = held.get("iso:ercot|day_evening_peak_mw|2025-01-31"), mn = held.get("iso:ercot|day_net_load_mean_mw|2025-01-31");
ok(worst.length === 10 && words(first).startsWith("1 January 31, 2025 118,152.54"), "the worst day of ERCOT's 2025 is 31 January, the first row of the ten");
ok(pk !== undefined && mn !== undefined && raw(first, key("iso:ercot", "day_evening_peak_mw", "2025-01-31")) === pk && raw(first, key("iso:ercot", "day_net_load_mean_mw", "2025-01-31")) === mn && pk > mn,
  `row 6: the day's own mean net load and its evening peak are in its row (${two(mn)} and ${two(pk)} MW), rows of the table`);
ok(worst.every((r) => /\|day_evening_peak_mw\|/.test(r) && /\|day_net_load_mean_mw\|/.test(r)) && ["Its mean net load, MW", "Evening peak, MW", "Batteries ran, h"].every((h) => words(e25).includes(h)), "row 6: each of the ten days has both, under two plain column names; no column the table had is gone");
ok((first.match(/<t[dh][ >]/g) ?? []).length === 12, "row 6: twelve cells a day (ten before)");

// ---- case 2: California, April 2026 against April 2024: two sources
const c26 = await draw({ grid: "caiso", month: "2026-04" });
const ns = notShown(c26);
ok(ns.length === 1 && ns[0][0] === "month" && ns[0][1].startsWith("April 2026 is not held for CAISO by EIA-930, which holds 7 months from April 2024 to November 2025, so August 2025 is shown."), `row 1: a month the grid does not hold is said, not replaced in silence: "${ns[0]?.[1].slice(0, 90)}..."`);
ok(ns[0]?.[2].includes('data-other-source="caiso-own"') && ns[0][2].includes('href="/shoulder?grid=caiso-own&amp;month=2026-04"') && ns[0][1].includes("CAISO by its own data holds it: April 2026, CAISO, its own data"), "row 1: the line names California's other source, which holds April 2026, as a link to it");
const o24 = notShown(await draw({ grid: "caiso-own", month: "2024-04" }));
ok(o24.length === 1 && o24[0][2].includes('href="/shoulder?grid=caiso&amp;month=2024-04"') && o24[0][1].includes("is not held for CAISO by its own data"), "row 1: and the other way round, for April 2024 asked of CAISO's own data");
const noGrid = notShown(await draw({ grid: "pjm" }));
ok(noGrid.length === 1 && noGrid[0][0] === "grid" && noGrid[0][1] === 'Grid: "pjm" is not held here (ERCOT; CAISO; CAISO, its own data are), so ERCOT is shown.', "row 1: a grid the page does not hold is said");
const noMonth = notShown(await draw({ grid: "ercot", month: "2025-13" }));
ok(noMonth.length === 1 && noMonth[0][1] === 'Month: "2025-13" is not a month as the address writes one (YYYY-MM), so August 2025 is shown.', "row 1: an address that names no month says so");
const e19 = notShown(await draw({ grid: "ercot", month: "2019-01" }));
ok(e19.length === 1 && !e19[0][2].includes("data-other-source") && e19[0][1].startsWith("January 2019 is not held for ERCOT, which holds 2 months"), "row 1: a grid with one source offers no other");
ok(notShown(await draw({ grid: "ercot" })).length === 0 && notShown(await draw({})).length === 0, "the page opened with no month named says nothing of the kind");

// ---- cases 2 and 5: California's two sources side by side over the months both hold
const c25 = await draw({ grid: "caiso", month: "2025-08" }), o26 = await draw({ grid: "caiso-own", month: "2026-04" }), c24 = await draw({ grid: "caiso", month: "2024-04" });
const both = S.bothHold(rows.map((r) => ({ ...r, value: Number(r.value) })), S.GRIDS[1], S.GRIDS[2]);
ok(both.join(" ") === "2025-06 2025-07 2025-08 2025-09 2025-10 2025-11", "California's two sources both hold June to November 2025");
const section = (html) => (html.match(/<section id="two-sources"[\s\S]*?<\/section>/) ?? [""])[0];
for (const [name, html] of [["CAISO by EIA-930, August 2025", c25], ["CAISO's own data, April 2026", o26], ["CAISO by EIA-930, April 2024", c24]]) {
  const sec = section(html);
  const drawn = [...sec.matchAll(/data-two-sources-row="([a-z-]+)\|(\d{4}-\d\d)"/g)].map((m) => `${m[1]}|${m[2]}`);
  const want = both.flatMap((m) => ["caiso", "caiso-own"].map((g) => `${g}|${m}`));
  const figures = both.flatMap((m) => ["iso:caiso", "iso:caiso_own"].flatMap((e) => ["shoulder_hours", "shoulder_start_hour", "shoulder_mwh_above_mean", "net_load_mean_mw", "evening_peak_mw", "shoulder_hours_needed", "shoulder2_hours_needed"].map((v) => [e, v, m])));
  ok(sec.includes('data-two-sources="6"') && drawn.join(" ") === want.join(" ") && figures.every(([e, v, m]) => raw(sec, key(e, v, `${m}-01`)) === held.get(`${e}|${v}|${m}-01`)),
    `row 5: ${name}: the two sources side by side, 12 rows, ${figures.length} figures, each the table's row`);
}
const aug = section(c25);
ok(two(raw(aug, key("iso:caiso", "shoulder_hours_needed", "2025-08-01"))) === "3.63" && two(raw(aug, key("iso:caiso_own", "shoulder_hours_needed", "2025-08-01"))) === "4.65", "row 5: August 2025 needs 3.63 hours by EIA-930 and 4.65 by CAISO's own data, in one table");
ok((aug.match(/<tr class="[^"]*bg-paper font-semibold[^"]*"/g) ?? []).length === 1 && /<tr class="[^"]*bg-paper font-semibold[^"]*">\s*<th[^>]*><a[^>]*data-two-sources-row="caiso\|2025-08"/.test(aug), "row 5: the row of the view drawn is the one marked");
ok((section(o26).match(/<tr class="[^"]*bg-paper font-semibold/g) ?? []).length === 0, "row 5: a month outside the six marks none");
ok(aug.includes('id="tip-shoulder-two-sources"') && !/<p[^>]*text-muted/.test(aug) && words(aug).includes("The battery fleet (EIA-860M) and the curtailment (CAISO's own count) are the same rows for both."), "row 5: what is the same and what differs is a hover tip, no grey text");
ok(section(e25) === "" && !e25.includes("two-sources"), "Texas, one source, has no such section");
// row 7: the tip's sentence on demand, held on the real rows of August 2025 (the average day of each source, hour by hour)
const hourOf = (e, s, h) => held.get(`${e}|avg_${s}_mw_h${String(h).padStart(2, "0")}|2025-08-01`);
const hours = Array.from({ length: 24 }, (_, h) => h);
const gap = hours.reduce((a, h) => a + hourOf("iso:caiso", "demand", h) - hourOf("iso:caiso_own", "demand", h), 0), charged = hours.reduce((a, h) => a - Math.min(0, hourOf("iso:caiso_own", "battery", h)), 0);
ok(words(aug).includes("CAISO's own demand leaves the fleet's charging out; over these months EIA-930's demand is higher by about what the batteries charge, hour by hour") && charged > 30000 && Math.abs(gap - charged) / charged < 0.02
  && hours.filter((h) => hourOf("iso:caiso_own", "battery", h) < -1000).every((h) => { const g = hourOf("iso:caiso", "demand", h) - hourOf("iso:caiso_own", "demand", h), c = -hourOf("iso:caiso_own", "battery", h); return Math.abs(g - c) / c < 0.15; }),
  `row 7: the tip says why the two differ, and the rows bear it out: August 2025, EIA-930's demand above the sum of CAISO's sources by ${two(Math.round(gap))} MWh a day, the batteries' charging ${two(Math.round(charged))} MWh`);

// row 8: hours needed against the hours the fleet holds, said in words beside the two figures
const head2 = (html) => words((html.match(/Hours the battery fleet covers[\s\S]*?The midday surplus/) ?? [""])[0]);
ok(o26.includes('data-needed-against-held="less"') && head2(o26).includes("would take 3.27 hours , less than the 3.43 hours it holds ."), "row 8: California, April 2026: \"would take 3.27 hours, less than the 3.43 hours it holds\"");
ok(e25.includes('data-needed-against-held="more"') && head2(e25).includes("would take 4.30 hours , more than the 1.52 hours it holds ."), "row 8: ERCOT, August 2025: \"would take 4.30 hours, more than the 1.52 hours it holds\"");
ok(c24.includes('data-needed-against-held="more"') && head2(c24).includes("would take 4.13 hours , more than the 3.39 hours it holds ."), "row 8: California, April 2024: 4.13 hours against 3.39 held");

// ---- the price: the page holds none, says so, and sends the reader to the page that does, for the grid shown
const ready = B.GRIDS.filter((g) => g.ready && g.hub && g.from);
const tight = (s) => words(s).replace(/ ([;:.,])/g, "$1");   // a tag's end leaves a space before the mark that follows it
const priceWords = `What a battery of 2, 4 or 8 hours earned, month by month, is on what a battery earns: ${ready.map((g) => `${g.name} at ${g.id === "ercot" ? "its hub average" : `${g.hub}, one hub of the grid`} from ${g.from}`).join("; ")}.`;
for (const [name, html, grid] of [["ERCOT", e25, "ercot"], ["CAISO by EIA-930", c25, "caiso"], ["CAISO's own data", o26, "caiso"]]) {
  const li = (html.match(/<li data-no-price="([a-z]+)">([\s\S]*?)<\/li>/) ?? ["", "", ""]);
  ok(li[1] === grid && tight(li[2]).startsWith("A price. The page counts hours and MWh, not what an hour of the evening is worth.") && tight(li[2]).includes(priceWords) && (html.match(new RegExp(`href="/cost-of-power/battery\\?grid=${grid}"`, "g")) ?? []).length === 2 && !html.includes('href="/cost-of-power/battery"'),
    `rows 9 and 10: ${name}: "What this cannot see" opens with the price, and both links to the battery page carry grid=${grid}`);
}
ok(ready.length === 2 && priceWords.includes("ERCOT at its hub average from 2018; CAISO at SP15, one hub of the grid from August 2023") && B.DURATIONS.join(",") === "2,4,8", "row 10: what the battery page holds is read from its own library (2, 4 and 8 hours; ERCOT from 2018, CAISO at SP15 from August 2023)");

// ---- nothing the page had is dropped, and nothing is written that should not be
for (const [name, html] of [["ERCOT, August 2025", e25], ["ERCOT, August 2023", e23], ["CAISO by EIA-930, August 2025", c25], ["CAISO's own data, April 2026", o26]]) {
  const t = words(html);
  ok(["The evening shoulder", "Hours the battery fleet covers", "The midday surplus", "The average day", "The shoulder, second measure", "Hours needed, second measure", "The shoulder hours by year",
    "By year: the second measure and the ten worst days", "The definitions, exactly as computed", "What this cannot see", "Decisions on this page"].every((w) => t.includes(w))
    && (html.match(/<svg /g) ?? []).length === 2 && !dash.test(html) && !/\bundefined\b|\bNaN\b/.test(t), `${name}: every block the page had is there, two charts, no dash, no "undefined"`);
}
// ruling alternative 1 (wip/alt-shoulder-1): the hover says the low is looked for while the sun is up, in every month; a table of main's rule with a night low adds a sentence
ok(e23.includes('data-sun-up="2023-08"') && e25.includes('data-sun-up="2025-08"') && words(e23).includes("lowest hour of the whole day falls before 08:00") && !words(e25).includes("lowest hour of the whole day falls before 08:00"), "case 4 under alternative 1: both months say the sun-up rule on hover; August 2023, lowest before dawn in main's table, says so");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
