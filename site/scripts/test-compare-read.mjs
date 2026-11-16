// Energy Research Warehouse (ERW) site, session 7540 (chain 304, part C): "Where power is cheap" (/prices/compare) read
// as a fund analyst setting two hubs or two grids side by side over the same months to choose where a project earns more
// (docs/reviews/compare-read-2026-11-16.md). The page is drawn to HTML whole by calling its own function on the site's
// own file (data/price_compare.json), with the license hold of the day; next/font/google is stood in for by
// scripts/font-stub-loader.mjs. No server, no network, nothing written. It holds the read's site rows:
//   row 1: ISO-NE's and NYISO's rows (hub_price_comparison is held for ISO-NE, MISO and NYISO) are named in the table and
//          the chart, every cell "license needed", and no figure of theirs is anywhere in the page, the headline included;
//   row 3: A and B side by side over the same hours, B less A on the figures drawn; a held pick "license needed", a pick
//          not in the period said so; the choice rides on every link;
//   row 4: both markets of A and B in one table;
//   row 6: the A and B note names the cost of power page's own twelve months and its standard time, with a link;
//   row 7: the table's note says clock time, daylight saving included;
//   row 8: the spread's words say it is the average day's, not the mean of each day's own spread;
//   row 10: the lead no longer says "every" hub and zone price the warehouse holds; ERCOT's load zones are named as not
//          compared;
//   row 12: ERCOT's Hub Average and Bus Average say what they average, on hover, and the Hub Average's figure is the mean
//          of the four hubs' on both windows and both markets (so the words are true of the file);
//   row 13: the page's own "not held" and its line of grids are in ink, the reason on hover;
// and that the upgrade drops nothing, and that no figure of a held row is in the read's own files.
//   node --import ./scripts/tsx-register.mjs scripts/test-compare-read.mjs
import fs from "node:fs";
import { register } from "node:module";
import { renderToStaticMarkup } from "react-dom/server";

register("./font-stub-loader.mjs", import.meta.url);
const { default: Compare } = await import("../app/prices/compare/page.tsx");
const P = await import("../lib/pricecompare.ts");
const { licenseHeldRow } = await import("../lib/license.ts");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const unesc = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const text = (html) => unesc(html.replace(/<style[\s\S]*?<\/style>/g, " ").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const file = JSON.parse(fs.readFileSync(new URL("../data/price_compare.json", import.meta.url), "utf-8"));
const draw = async (q) => renderToStaticMarkup(await Compare({ searchParams: Promise.resolve(q) }));
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [unesc(x[1]), x[2]]));
const isHeld = (e) => licenseHeldRow(P.TABLE, e);
const split = (period) => P.hold(file[period], isHeld);
const FIG = ["avg_price", "negative_hours_share_pct", "above_200_hours_share_pct", "day_spread_top4_bottom4"];

// ---- the pure parts
{
  const { shown, held } = split("year");
  ok(held.map((h) => h.entity).join("|") === "isone:.H.INTERNAL_HUB|nyiso:N.Y.C." && shown.length === 9, "hold: the twelve months hold ISO-NE's hub and NYISO's New York City zone; 9 rows shown");
  ok(held.every((h) => Object.keys(h).sort().join(",") === "entity,grid,node"), "hold: a held row keeps its name and no figure");
  const m = split("month");
  ok(m.held.length === 20 && m.held.every((h) => /^(isone|nyiso):/.test(h.entity)) && m.shown.every((r) => /^(caiso|ercot|spp):/.test(r.entity)), "hold: the month holds ISO-NE's 9 and NYISO's 11; the rest shown");
  ok(P.hold(file.year, () => false).held.length === 0, "hold: nothing held when no grid is");
  ok(JSON.stringify(P.pairOf({ a: "ercot:HB_WEST", b: "nyiso:HUD VL" })) === JSON.stringify({ a: "ercot:HB_WEST", b: "nyiso:HUD VL" }), "pairOf: two entities as the table writes them");
  ok(JSON.stringify(P.pairOf({ a: "<script>", b: "x".repeat(90) })) === "{}", "pairOf: anything else is no pick");
  ok(P.href({ period: "year", market: "dam", sort: "neg" }) === "/prices/compare?period=year&market=dam&sort=neg", "href: unchanged without A and B");
  ok(P.href({ period: "year", market: "dam", sort: "avg", a: "ercot:HB_WEST", b: "nyiso:HUD VL" }) === "/prices/compare?period=year&market=dam&sort=avg&a=ercot%3AHB_WEST&b=nyiso%3AHUD%20VL", "href: A and B ride along, encoded");
}

// ---- row 1: the hold, drawn, in four views
for (const q of [{}, { period: "year", market: "rtm", sort: "neg" }, { period: "month", market: "dam", sort: "spread" }, { period: "month", market: "rtm", sort: "avg", dir: "desc" }]) {
  const c = P.choices(q), html = await draw(q), got = marked(html), { shown, held } = split(c.period);
  const tag = P.href({ period: c.period, market: c.market, sort: c.sort.slug, dir: q.dir });
  ok(held.every((h) => html.includes(`data-held-row="${h.entity}"`)), `${tag}: the ${held.length} held rows are named in the table`);
  ok(held.every((h) => html.includes(`data-bar="${h.entity}" data-bar-held="1"`)), `${tag}: and in the chart, with no bar`);
  ok(!Object.keys(got).some((k) => held.some((h) => k.startsWith(`${h.entity}|`))), `${tag}: no marked number of a held row`);
  // no figure of a held row in the page's words: every held figure that no shown row also carries
  const shownFigs = new Set(shown.flatMap((r) => ["dam", "rtm"].flatMap((m) => FIG.map((f) => r[`${m}_${f}`]))).filter((v) => v !== undefined).map(P.two));
  const heldFigs = [...new Set(file[c.period].filter((r) => isHeld(r.entity)).flatMap((r) => ["dam", "rtm"].flatMap((m) => FIG.map((f) => r[`${m}_${f}`]))).filter((v) => v !== undefined && v >= 10).map(P.two))].filter((s) => !shownFigs.has(s));
  const t = text(html);
  const leak = heldFigs.filter((s) => new RegExp(`(^|[^0-9.])${s.replace(".", "\\.")}([^0-9]|$)`).test(t));
  ok(heldFigs.length > 0 && leak.length === 0, `${tag}: none of the ${heldFigs.length} figures of a held row is in the page's words${leak.length ? `: ${leak.join(", ")}` : ""}`);
  const dearest = P.ordered(shown, { ...c, sort: P.MEASURES[0], dir: "desc" })[0];
  ok(got["sum|dearest"] === P.two(P.valueOf(dearest, c.market, P.MEASURES[0])) && got.count === String(P.ordered(shown, c).length), `${tag}: the headline's highest is of the rows shown (${P.label(dearest)}), of ${got.count}`);
  ok(html.includes(`data-summary-held="${P.heldGrids(held).join(",")}"`) && (html.match(/data-held-grid="/g) ?? []).length === P.heldGrids(held).length, `${tag}: the sentence and the held section name ${P.heldGrids(held).join(" and ")}`);
  const cells = (html.match(/data-license-held="hub_price_comparison"/g) ?? []).length;
  ok(cells === held.length * 6, `${tag}: ${cells} cells "license needed" (6 a held row)`);
}

// ---- rows 3 and 4: A and B
{
  const q = { a: "ercot:HB_WEST", b: "ercot:HB_HOUSTON" };
  const html = await draw(q), got = marked(html);
  const W = file.year.find((r) => r.entity === q.a), H = file.year.find((r) => r.entity === q.b);
  const pairs = [["dam|avg", "dam_avg_price"], ["dam|neg", "dam_negative_hours_share_pct"], ["dam|high", "dam_above_200_hours_share_pct"], ["dam|spread", "dam_day_spread_top4_bottom4"],
    ["rtm|avg", "rtm_avg_price"], ["rtm|neg", "rtm_negative_hours_share_pct"], ["rtm|high", "rtm_above_200_hours_share_pct"], ["rtm|spread", "rtm_day_spread_top4_bottom4"], ["carbon", "grid_carbon_intensity"]];
  const bad = pairs.filter(([k, f]) => got[`ab|a|${k}`] !== P.two(W[f]) || got[`ab|b|${k}`] !== P.two(H[f]) || got[`ab|diff|${k}`] !== P.two(Math.round((H[f] - W[f]) * 100) / 100 || 0));
  ok(bad.length === 0, `row 3: West hub and Houston hub, twelve months: nine figures each, both markets and the grid, and B less A on the figures drawn${bad.length ? `: ${bad.map((x) => x[0]).join(", ")}` : ""}`);
  ok(got["ab|a|dam|avg"] === "33.00" && got["ab|b|dam|avg"] === "35.22" && got["ab|diff|dam|avg"] === "2.22" && got["ab|diff|rtm|neg"] === "-10.39", "row 3: the case as read: 33.00 and 35.22 (+2.22) day-ahead; below zero in real time 12.01 and 1.62 (-10.39)");
  ok(got["ab|a|dam|hours"] === "8,760" && got["ab|diff|dam|hours"] === "0", "row 3: hours held in whole hours");
  ok(/<option value="ercot:HB_WEST" selected="">/.test(html) && /<option value="ercot:HB_HOUSTON" selected="">/.test(html), "row 3: the form shows the two picks");
  ok((html.match(/<option value="[^"]+"/g) ?? []).length === 2 * file.year.length, `row 3: each of A and B offers the period's ${file.year.length} rows`);
  const links = [...html.matchAll(/href="(\/prices\/compare\?[^"]+)"/g)].map((x) => unesc(x[1]));
  ok(links.length >= 10 && links.every((l) => l.includes("&a=ercot%3AHB_WEST&b=ercot%3AHB_HOUSTON")), `row 3: the ${links.length} links of period, market and order keep A and B`);
  ok(html.includes('<input type="hidden" name="period" value="year"/>') && html.includes('<input type="hidden" name="sort" value="avg"/>'), "row 3: the form keeps the period, the market and the order");
  ok(/<th scope="colgroup"[^>]*>Day-ahead<\/th>/.test(html) && /<th scope="colgroup"[^>]*>Real-time<\/th>/.test(html), "row 4: both markets in the one table");
  const h2 = await draw({ period: "year", a: "ercot:HB_NORTH", b: "nyiso:N.Y.C." }), g2 = marked(h2);
  ok(!Object.keys(g2).some((k) => k.startsWith("ab|b|") || k.startsWith("ab|diff|")) && g2["ab|a|dam|avg"] === "34.43" && (h2.match(/data-license-held="hub_price_comparison"/g) ?? []).length === 6 * 2 + 11,
    "row 3: a held B is \"license needed\" in each of its 11 cells, and no B less A");
  const h3 = await draw({ period: "year", a: "caiso:TH_ZP26_GEN-APND", b: "spp:SPPNORTH_HUB" }), t3 = text(h3);
  ok(t3.includes("A: caiso:TH_ZP26_GEN-APND") && (t3.match(/not in this period/g) ?? []).length === 11 && marked(h3)["ab|b|carbon"] === undefined,
    "row 3: a zone or hub held only in the month, picked in the twelve months, says \"not in this period\"; SPP's carbon over the year is \"not held\"");
  const h4 = await draw({ a: "<b>", b: "" });
  ok(h4.includes('data-ab-empty="1"') && !h4.includes('data-ab-table="1"'), "row 3: no pick, no table: the line that asks for A and B");
}

// ---- rows 6, 7, 8, 10, 12, 13 and what is kept
{
  const html = await draw({}), t = text(html);
  const ab = await draw({ a: "ercot:HB_WEST", b: "spp:SPPNORTH_HUB" });
  const note = (ab.match(/<p[^>]*data-ab-note="1"[^>]*>([\s\S]*?)<\/p>/) ?? [, ""])[1];
  ok(text(note).includes("its own last twelve whole months and in each grid's standard time (no daylight saving)") && note.includes('href="/cost-of-power?view=allgrids"'), "row 6: the A and B note names the cost of power page's twelve months and its time, with a link");
  ok(t.includes("in each grid's own clock time (daylight saving included)"), "row 7: the table's note says clock time, daylight saving included");
  ok(t.includes("It is not the mean of each day's own spread, which is larger, since the dearest and the cheapest hours move from day to day."), "row 8: the spread is the average day's, said beside the measure");
  ok(!t.includes("Every public hub and zone price the warehouse holds") && t.includes("The hub and zone prices of five grids, side by side:"), "row 10: the lead no longer says \"every\"");
  ok(t.includes("ERCOT's eight load zones. Their prices are held in the warehouse since 2015"), "row 10: ERCOT's load zones are named as not compared");
  ok(html.includes('data-name-words="ercot:HB_HUBAVG"') && html.includes('data-name-words="ercot:HB_BUSAVG"') && html.includes(`title="${P.NAME_WORDS["ercot:HB_HUBAVG"].replace(/'/g, "&#x27;")}"`), "row 12: the Hub Average and the Bus Average say what they average, on hover");
  for (const period of ["year", "month"]) for (const m of ["dam", "rtm"]) {
    const v = (e) => file[period].find((r) => r.entity === e)[`${m}_avg_price`];
    const four = (v("ercot:HB_NORTH") + v("ercot:HB_SOUTH") + v("ercot:HB_HOUSTON") + v("ercot:HB_WEST")) / 4;
    ok(Math.abs(four - v("ercot:HB_HUBAVG")) <= 0.01, `row 12: ${period}, ${m}: the Hub Average ${P.two(v("ercot:HB_HUBAVG"))} is the mean of the four hubs' ${four.toFixed(4)} (within the cent of rounding)`);
  }
  const sppYear = await draw({ sort: "carbon" });
  ok(sppYear.includes('<span title="Fewer than 95 percent of the period&#x27;s hours are held') && !/<span class="text-muted">not held<\/span>/.test(sppYear), "row 13: \"not held\" is in ink, its reason on hover");
  ok(html.includes('<p class="mt-2 max-w-3xl text-xs">Grids in this view:'), "row 13: the line of grids is in ink");
  // the upgrade drops nothing
  ok(html.includes('data-not-a-site="1"') && html.includes('data-summary="1"') && (html.match(/data-sort="/g) ?? []).length === 5, "kept: a hub is not a site, the sentence, five headings that sort");
  ok(file.held_not_shown.every((h) => html.includes(`data-hidden="${h.entity}"`)) && html.includes('data-not-held="PJM"'), "kept: MISO's 8 hubs held, not shown, and PJM not held");
  for (const s of ["The price at a site.", "A delivered price:", "Next year.", "The carbon of the power a site would take.", "Whether power can be had there at all:", "How it is computed", "Decisions on this page", "Built 2026-"]) ok(t.includes(s), `kept: "${s}"`);
  const { shown } = split("year");
  ok(shown.every((r) => html.includes(`data-bar="${r.entity}"`) && html.includes(`data-n="${r.entity}|avg"`)), "kept: every row shown has its bar and its figures");
}

// ---- nothing held in the read's own files (the repository is public)
{
  const root = new URL("../../", import.meta.url);
  const shownFigs = new Set(["year", "month"].flatMap((p) => split(p).shown.flatMap((r) => ["dam", "rtm"].flatMap((m) => FIG.map((f) => r[`${m}_${f}`])))).filter((v) => v !== undefined).map(P.two));
  const heldFigs = [...new Set(["year", "month"].flatMap((p) => file[p].filter((r) => isHeld(r.entity)).flatMap((r) => ["dam", "rtm"].flatMap((m) => FIG.map((f) => r[`${m}_${f}`]))))
    .filter((v) => v !== undefined && v >= 10).map(P.two))].filter((s) => !shownFigs.has(s));
  for (const rel of ["docs/reviews/compare-read-2026-11-16.md", "archive/sessions/SESSION_7540_REPORT.md", "site/scripts/test-compare-read.mjs"]) {
    const path = new URL(rel, root);
    if (!fs.existsSync(path)) { ok(rel.startsWith("archive/"), `${rel}: not yet written`); continue; }
    const body = fs.readFileSync(path, "utf-8");
    const leak = heldFigs.filter((s) => new RegExp(`(^|[^0-9.])${s.replace(".", "\\.")}([^0-9]|$)`).test(body));
    ok(leak.length === 0, `${rel}: none of the ${heldFigs.length} figures of a held row${leak.length ? `: ${leak.join(", ")}` : ""}`);
  }
}

console.log(`${n - failed} of ${n} checks pass`);
process.exitCode = failed ? 1 : 0;
