// Chain 780 (session 11600): "Where the next gigawatts can go", the regions section of the All grids tab, drawn to HTML
// without a build (scripts/tsx-loader.mjs) and held to what a reader sees. Twice: on the files main holds (the
// contract's own examples until the data machine's builder has run: the section says so and draws no table), and on
// the tests' fixture (tests/fixtures/siting_regions: MADE-UP values in the contract's shape, never deployed), where
// every figure, blank, sort, choice and link is checked. No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-regions-section.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE = path.join(HERE, "..", "..", "tests", "fixtures", "siting_regions");
const L = await import("../app/cost-of-power/regions.ts");
const { pfValue } = await import("../lib/pagefile.ts");
const { RegionsSection } = await import("../app/cost-of-power/RegionsSection.tsx");
const { AllGridsView } = await import("../app/cost-of-power/AllGridsView.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n += 1; if (!c) { failed += 1; console.log(`FAIL ${what}`); } };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const noTips = (s) => s.replace(/<span role="tooltip"[^>]*>[\s\S]*?<\/span>/g, "");
const words = (s) => ent(noTips(s).replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const tips = (s) => [...s.matchAll(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span>/g)].map((m) => ent(m[1].replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim());
const draw = (query) => renderToStaticMarkup(h(RegionsSection, { q: Object.fromEntries(new URLSearchParams(query)) }));
const figs = (html) => [...html.matchAll(/data-check="(pf\|siting\/regions\/[^"]+)" data-raw="([^"]+)"[^>]*>([^<]*)</g)].map((m) => ({ key: ent(m[1]), raw: m[2], text: m[3] }));
const rowIds = (html) => [...html.matchAll(/<tr[^>]*data-sr-row="([^"]+)"/g)].map((m) => m[1]);
const colKeys = (html) => [...html.matchAll(/<th[^>]*data-sr-col="([^"]+)"/g)].map((m) => m[1]);
const rowHtml = (html, id) => (html.match(new RegExp(`<tr[^>]*data-sr-row="${id}"[^>]*>([\\s\\S]*?)</tr>`)) ?? ["", ""])[1];
const cellHtml = (row, key) => (row.match(new RegExp(`<td[^>]*data-sr-cell="${key.replace(/\./g, "\\.")}"[^>]*>([\\s\\S]*?)</td>`)) ?? ["", ""])[1];
const shown = (raw) => { const x = Number(raw); return Number.isInteger(x) ? x.toLocaleString("en-US") : x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };

// ---- 1. the files main holds -----------------------------------------------------------------------------------------
delete process.env.ERW_SITING_REGIONS_DIR;
const mainIndex = JSON.parse(fs.readFileSync(path.join(HERE, "..", "data", "siting", "regions", "index.json"), "utf-8"));
const onMain = draw("view=allgrids");
ok(/<section[^>]*id="regions"[^>]*data-llr="regions"[^>]*data-sr="1"/.test(onMain) && onMain.includes(">Where the next gigawatts can go</h2>"), "the section is drawn under its own h2, with the tab's hovers");
if (mainIndex.example === true) {
  ok(onMain.includes('data-sr-state="example"') && onMain.includes('data-sr-not-built="1"'), "on the contract's example files the section says it is not built");
  ok(!onMain.includes("<table") && figs(onMain).length === 0, "on the example files no table and no figure is drawn");
  ok(words(onMain).endsWith("not built yet") && tips(onMain).some((t) => t.startsWith("not built yet: the files on this build are the contract's own examples")), "the section says not built yet, and why on hover: the files are the contract's examples");
} else {
  ok(onMain.includes('data-sr-state="files"') && rowIds(onMain).length === mainIndex.places.length, `on the data machine's files the table has a row for each of the ${mainIndex.places.length} places`);
  const bad = figs(onMain).filter((f) => f.text !== shown(f.raw) || pfValue(f.key) !== Number(f.raw));
  ok(figs(onMain).length > 0 && bad.length === 0, `every figure drawn (${figs(onMain).length}) is its file's own, written whole or to two decimals (${JSON.stringify(bad.slice(0, 2))})`);
}

// ---- 2. the fixture ----------------------------------------------------------------------------------------------------
process.env.ERW_SITING_REGIONS_DIR = FIXTURE;
const table = JSON.parse(fs.readFileSync(path.join(FIXTURE, "siting", "regions", "table.json"), "utf-8"));
const index = JSON.parse(fs.readFileSync(path.join(FIXTURE, "siting", "regions", "index.json"), "utf-8"));
ok(/MADE-UP/.test(table.fixture) && /MADE-UP/.test(index.fixture) && table.example === false, "the fixture says of itself that its values are made up");
const open = draw("view=allgrids");
ok(open.includes('data-sr-state="files"'), "on files that are not examples the section draws them");
ok(JSON.stringify(rowIds(open)) === JSON.stringify(index.places.map((p) => p.id)), "as it opens: a row a place, in the file's order");
const firstOfEach = L.defaultCols(table.columns);
ok(firstOfEach.length === 10 && JSON.stringify(colKeys(open)) === JSON.stringify(firstOfEach), `as it opens: the first column of each of the ten sections (${colKeys(open).join(", ")})`);
ok(open.includes('data-sr-shown="4|4"') && open.includes('data-sr-sorted="name|asc"') && words(open).includes("The order is the column's, not a ranking of places."), "the line above the table says how many places, the order, and that it is no ranking");
// every figure: its key leads to the same value in its file, and its words are the value whole or to two decimals
for (const [query, least] of [["view=allgrids", 20], ["view=allgrids&srcols=" + table.columns.map((c) => c.key).join(","), 60], ["view=allgrids&sropen=op-ercot", 120], ["view=allgrids&sra=op-ercot&srb=op-nyiso", 50], ["view=allgrids&sropen=op-nyiso", 30]]) {
  const f = figs(draw(query));
  const bad = f.filter((x) => x.text !== shown(x.raw) || pfValue(x.key, FIXTURE) !== Number(x.raw));
  ok(f.length >= least && bad.length === 0, `${query.slice(0, 60)}: each of the ${f.length} figures is its file's own under its key, in the value check's form (${JSON.stringify(bad.slice(0, 2))})`);
}
const tex = rowHtml(open, "region-tex");
ok(cellHtml(tex, "price.mean_da").includes('data-check="pf|siting/regions/table.json|rows/@id=region-tex/v/0" data-raw="46.31"') && words(cellHtml(tex, "price.mean_da")) === "46.31", "Texas: the day-ahead mean price is the table's value under its key");
ok(words(cellHtml(tex, "tightness.peak_mw")) === "85,111" && words(cellHtml(tex, "queue.active_mw")) === "204,512.50", "a whole value is written whole with commas, any other to two decimals");
// a count held for a license: blank, "license needed" on hover and to a screen reader, no digit
const ny = rowHtml(open, "op-nyiso"), nyPrice = cellHtml(ny, "price.mean_da");
ok(nyPrice.includes('data-license-held="iso_hub_prices_history"') && /aria-label="Day-ahead price, mean, NYISO: license needed"/.test(nyPrice) && words(nyPrice) === "" && tips(nyPrice)[0].startsWith("license needed: NYISO's prices need a paid data license"), "NYISO's price is a blank with license needed on hover, and no figure");
// a count not shown for another reason: the reason's kind in a word, the reason on hover
const soco = rowHtml(open, "ba-soco"), socoPrice = cellHtml(soco, "price.mean_da");
ok(words(socoPrice) === "not a market" && socoPrice.includes('data-sr-held="not a market"') && tips(socoPrice)[0].startsWith("not a market: Southern Company's area"), "an authority that is no market says so in a word, with the reason on hover");
ok(words(cellHtml(tex, "congestion.share_pct")) === "not published", "a count the operator does not print says not published");
// the site's own hold wins over the file: the fixture carries the held datacenter tables' counts as if shown
const dcCells = index.places.map((p) => cellHtml(rowHtml(open, p.id), "datacenters.facilities_n"));
ok(dcCells.every((c) => c.includes('data-license-held="datacenter_facilities"') && words(c) === "") && !figs(open).some((f) => /\/v\/2[34]$/.test(f.key)), "a count of a table the site holds for a license is a blank whatever the file carries (datacenter_facilities)");
ok(tips(dcCells[0])[0].startsWith("license needed: the site holds datacenter_facilities for a license"), "its hover says the site holds the table");
// a cell whose period and source are its own says so in a hover of its own
const all = draw("view=allgrids&srcols=" + table.columns.map((c) => c.key).join(","));
ok(colKeys(all).length === 25, "every column chosen: 25 columns");
const nyMargin = cellHtml(rowHtml(all, "op-nyiso"), "tightness.reserve_margin_pct");
ok(nyMargin.includes('data-sr-own="1"') && tips(nyMargin)[0].includes("Period: summer 2027 (NYISO's made-up report).") && words(nyMargin) === "18.60", "a cell with a period of its own gives it on hover, in the file's own words");
// the builder's form: a column that carries no period and no source, every cell carrying its own. The column's hover
// gives what its cells share, and a cell says its own only where it differs
ok(table.columns.find((c) => c.key === "tightness.peak_mw").period === null && table.rows.every((r) => r.cell["6"]), "the fixture holds the builder's form for a column: no period on the column, one on every cell");
const peakHead = (all.match(/<th[^>]*data-sr-col="tightness\.peak_mw"[^>]*>([\s\S]*?)<\/th>/) ?? ["", ""])[1];
ok(tips(peakHead)[0].includes("Period: 1 Nov 2025 to 31 Oct 2026.") && tips(peakHead)[0].includes("ERW table eia930_ba_demand_hourly"), "such a column's hover gives the period and the source its cells share");
ok(index.places.every((p) => !cellHtml(rowHtml(all, p.id), "tightness.peak_mw").includes("data-sr-own")) && (all.match(/data-sr-own="1"/g) ?? []).length === 1, "and no cell repeats them: one cell of the table has a period of its own");
// a column's head: its section, its name as a link that sorts, its unit with the period and the source on hover
const head = (open.match(/<th[^>]*data-sr-col="price\.mean_da"[^>]*>([\s\S]*?)<\/th>/) ?? ["", ""])[1];
ok(words(head).startsWith("Price Day-ahead price, mean USD/MWh") && /href="\/cost-of-power\?view=allgrids&amp;srsort=price\.mean_da"/.test(head), `a column's head names its section, its count and its unit, and sorts by it (${words(head)})`);
ok(tips(head)[0].includes("Period: 1 Nov 2025 to 31 Oct 2026.") && tips(head)[0].includes("ERW table ercot_all_hub_prices_history") && tips(head)[0].includes("retrieved 2026-11-28 06:10 UTC"), "the head's hover gives the period, the publisher's report, the table and its retrieval");
ok(!open.includes("example.org/made-up-source"), "a source's address is drawn nowhere: it is one document for every place (data request 586)");

// the sort: by a column, largest first; a second press turns it round; a place with no figure last in either direction
const byPeak = draw("view=allgrids&srsort=tightness.peak_mw");
ok(JSON.stringify(rowIds(byPeak)) === JSON.stringify(["region-tex", "op-ercot", "ba-soco", "op-nyiso"]) && byPeak.includes('data-sr-sorted="tightness.peak_mw|desc"'), "sorted by peak demand: largest first, equal figures in the file's order");
ok(colKeys(byPeak)[0] === "tightness.peak_mw" && /aria-sort="descending" data-sr-col="tightness\.peak_mw"/.test(byPeak), "the column sorted by is drawn first, and says so to a screen reader");
ok(/href="\/cost-of-power\?view=allgrids&amp;srsort=tightness\.peak_mw&amp;srdir=asc"[^>]*data-sr-sort="tightness\.peak_mw"/.test(byPeak), "its head's next press turns the order round");
ok(JSON.stringify(rowIds(draw("view=allgrids&srsort=tightness.peak_mw&srdir=asc"))) === JSON.stringify(["op-nyiso", "ba-soco", "region-tex", "op-ercot"]), "smallest first");
ok(JSON.stringify(rowIds(draw("view=allgrids&srsort=price.mean_da"))) === JSON.stringify(["region-tex", "op-ercot", "op-nyiso", "ba-soco"]) && JSON.stringify(rowIds(draw("view=allgrids&srsort=price.mean_da&srdir=asc"))) === JSON.stringify(["region-tex", "op-ercot", "op-nyiso", "ba-soco"]), "a place with no figure in the column is last in either direction");
ok(JSON.stringify(rowIds(draw("view=allgrids&srsort=nonsense"))) === JSON.stringify(index.places.map((p) => p.id)), "a column the file does not hold sorts nothing");
// the choices: the columns kept, the kind listed
const two = draw("view=allgrids&srcols=queue.active_mw,price.mean_da,nonsense");
ok(JSON.stringify(colKeys(two)) === JSON.stringify(["price.mean_da", "queue.active_mw"]), "the columns the address keeps, in the file's order; a name the file does not hold is dropped");
ok(JSON.stringify(rowIds(draw("view=allgrids&srkind=operator"))) === JSON.stringify(["op-ercot", "op-nyiso"]) && draw("view=allgrids&srkind=operator").includes('data-sr-shown="2|4"'), "the market operators alone: two of four places");
ok(/data-sr-picker="10\|25"/.test(open) && (open.match(/data-sr-col-pick="/g) ?? []).length === 25 && (open.match(/data-sr-col-pick="[^"]+"[^>]*checked=""|checked=""[^>]*data-sr-col-pick="/g) ?? []).length === 10, "the picker lists the 25 columns by section, the ten shown ticked");
// the tab's own names in the address are kept by every link of the section
const kept = draw("view=allgrids&profile=flexible&mw=300&sort=energy&rstate=TX&bad%20key=1");
const hrefs = [...kept.matchAll(/href="(\/cost-of-power\?[^"]+)"/g)].map((m) => ent(m[1]));
ok(hrefs.length > 10 && hrefs.every((u) => u.includes("view=allgrids") && u.includes("profile=flexible") && u.includes("mw=300") && u.includes("sort=energy") && u.includes("rstate=TX") && !u.includes("bad")), "every link keeps the tab's load, its hub table's sort and its rules' filter; a name of no known form is dropped");

// a place opened: its own file
const er = draw("view=allgrids&sropen=op-ercot");
ok(/<section[^>]*id="regions-place"[^>]*data-sr-place="op-ercot" data-sr-place-state="file"/.test(er) && />ERCOT<a[^>]*data-sr-close="op-ercot"/.test(er), "ERCOT opened: a panel of its own with a way to close it");
ok(index.sections.every((s) => er.includes(`data-sr-section="${s.id}"`)) && (er.match(/data-sr-section-state="shown"/g) ?? []).length === 10, "its ten sections, in the file's order");
ok(er.includes('data-check="pf|siting/regions/op-ercot.json|sections/tightness/peak_mw/v" data-raw="85111"') && er.includes('data-check="pf|siting/regions/op-ercot.json|sections/price/hubs/1/p95/v" data-raw="131.25"'), "its counts and its hubs' figures carry keys into its own file");
ok(er.includes('data-sr-list="congestion.top_by_hours" data-sr-list-rows="10"') && er.includes('data-sr-list="congestion.top_by_cost" data-sr-list-rows="10"') && er.includes("MADE-UP CONSTRAINT 1"), "its top constraints: ten by hours and ten by cost, by the operator's own names");
ok(er.includes('data-sr-list="imports.partners" data-sr-list-rows="3"') && words(er).includes("Southwest Power Pool (SWPP)"), "its three partners");
ok(/<a href="https:\/\/example\.org\/made-up-rule-1" rel="noopener" data-sr-source="rule">Made-up Wires Company<\/a>/.test(er) && !er.includes("javascript:"), "a rule that carries its document's address opens it; an address that is not a web address is never a link");
ok(/href="\/cost-of-power\?view=allgrids&amp;sropen=op-ercot&amp;rule=made-up-rule-3#large-load-rules"[^>]*data-sr-rule="made-up-rule-3"[^>]*>Made-up Power and Light</.test(er) && er.includes('data-sr-rule="made-up-rule-2"'), "a rule that carries its id alone opens the tab's own rule of that id, under the tab's large-load rules");
ok(tips(er).some((t) => t === "As the rule's document prints it: 75 MW or more at a single site, as the made-up rule prints it") && er.includes('data-check="pf|siting/regions/op-ercot.json|sections/large_load/rules/0/threshold_mw" data-raw="75"'), "a rule's smallest load is the figure, with the document's own words on hover");
ok(words(er).includes("a made-up contract term that runs on for well over ninety-six characters so that the table... ") && !words(er).includes("so that the table cuts it") &&tips(er).some((t) => t.endsWith("as the tab's own rules table does")), "a document's long words are cut at a word, the whole on hover");
ok(er.includes('data-sr-list-source="large_load.rules"') && er.includes('data-sr-states="1"') && words(er).includes("The states it reaches: TX."), "the rules' source is on hover; the states the place reaches are named");
// a count's small trend: its 24 months as the file holds them
const trends = [...er.matchAll(/data-sr-trend="months" data-sr-trend-points="(\d+)"/g)].map((m) => Number(m[1]));
ok(JSON.stringify(trends) === JSON.stringify([24, 24, 24, 24, 24, 12]), `the counts that carry their months draw them: two hubs' mean price, the peak, carbon, net imports (24 months each) and wind curtailed (the 12 months held); one month alone draws no line (${trends.join(", ")})`);
ok(er.includes('aria-label="ERCOT Hub Average, day-ahead, Mean price by month, USD/MWh, Nov 2024 to Oct 2026"') && er.includes('aria-label="Wind curtailed, ERCOT by month, MWh, Nov 2025 to Oct 2026"'), "a trend says what it is, its unit and the months it runs over");
// a hub the file lists with a status of its own and no figures
const heldHub = (er.match(/<tr[^>]*>(?:(?!<\/tr>)[\s\S])*A made-up hub held whole[\s\S]*?<\/tr>/) ?? [""])[0];
ok((heldHub.match(/data-license-held="siting_regions"/g) ?? []).length === 5 && tips(heldHub).every((t) => t === "license needed: a made-up hub whose prices need a license"), "a hub held whole is five blanks, each license needed with the hub's own reason");
ok(/data-sr-trend="intensity_by_hour"[\s\S]*?<svg[^>]*role="img"[^>]*aria-label="ERCOT: carbon intensity by hour of day, kg CO2\/MWh"/.test(er) && er.includes('data-check="pf|siting/regions/op-ercot.json|sections/mix_carbon/intensity_by_hour/12" data-raw="333.5"') && er.includes('data-check="pf|siting/regions/op-ercot.json|sections/mix_carbon/intensity_by_hour/6" data-raw="401.7"'), "its one small trend, carbon by hour of day, with its lowest and highest hour");
ok(words(er).includes("2026-08-20 21:00 UTC"), "the hour of its peak, as the site writes a time");
const dc = (er.match(/data-sr-section="datacenters"[\s\S]*$/) ?? [""])[0];
ok(!dc.includes("Made-up Campus One") && (dc.match(/data-license-held="datacenter_(facilities|projects)"/g) ?? []).length >= 5 && !/data-check="pf\|siting\/regions\/op-ercot\.json\|sections\/datacenters/.test(dc), "the datacenters there: every count and the list are blank, license needed (the site holds both tables)");
const nyOpen = draw("view=allgrids&sropen=op-nyiso");
ok(/data-sr-section="price" data-sr-section-state="not-shown"/.test(nyOpen) && nyOpen.includes('data-license-held="siting_regions"'), "NYISO opened: a section none of which can be shown is one blank, license needed");
ok(tips(nyOpen).some((t) => t.startsWith("too few: fewer than 300 days")) && !/data-sr-trend="intensity_by_hour"[\s\S]{0,900}<svg/.test(nyOpen), "a trend the file holds too little of is said so, and no line is drawn");
ok(tips(nyOpen).some((t) => t.startsWith("not held: no net generation by source is held")) && tips(nyOpen).some((t) => t === "license needed: the list is held with its tables (made-up words of the builder)"), "an empty list says why in the file's own words: the mix, and the datacenters there");
const socoOpen = draw("view=allgrids&sropen=ba-soco");
ok(socoOpen.includes('data-sr-place-state="none"') && tips(socoOpen).some((t) => t.startsWith("not held: this place's own file is not on this build")), "a place with no file of its own says so");
ok(!draw("view=allgrids&sropen=nowhere").includes('id="regions-place"'), "a place the index does not hold opens nothing");
// headings: h2 the section, h3 a panel, h4 a panel's parts; no level skipped
const levels = [...er.matchAll(/<h([1-6])/g)].map((m) => Number(m[1]));
ok(levels[0] === 2 && levels.every((v, i) => i === 0 || v <= levels[i - 1] + 1) && levels.includes(3) && levels.includes(4), `no heading level is skipped (${levels.join("")})`);

// A and B, side by side
const ab = draw("view=allgrids&sra=op-ercot&srb=op-nyiso");
ok(/<section[^>]*id="regions-ab"[^>]*data-sr-ab="op-ercot\|op-nyiso"/.test(ab) && (ab.match(/data-sr-ab-row="/g) ?? []).length === 25, "A and B: every one of the 25 counts, A beside B");
const abRow = (ab.match(/<tr[^>]*data-sr-ab-row="tightness\.peak_mw"[^>]*>([\s\S]*?)<\/tr>/) ?? ["", ""])[1];
ok(/data-sr-ab-cell="a"[\s\S]*?>85,111<[\s\S]*data-sr-ab-cell="b"[\s\S]*?>31,005\.50</.test(abRow), "A's and B's figures stand in one row");
ok(!draw("view=allgrids&sra=op-ercot&srb=op-ercot").includes('data-sr-ab="op-ercot|op-ercot"'), "B is not A a second time");

// no score, no rank, no advice
for (const html of [open, er, ab]) {
  // "Hours scored" is the contract's own name of a count (the hours the forecast's errors are taken over), not a score of places
  const w = words(html).replace("nothing is scored or ranked", "").replace("not a ranking of places", "").replace(/Hours scored/g, "");
  ok(!/\b(best|worst|winner|rank\w*|score\w*|recommend\w*|should|ideal|attractive|favou?rable)\b/i.test(w), "no word ranks, scores or advises");
}

// ---- 3. the pure parts ------------------------------------------------------------------------------------------------
const c0 = L.choiceOf({}, table, index);
ok(c0.sort === "name" && c0.dir === "asc" && c0.kind === "all" && !c0.colsChosen && c0.open === null, "nothing asked: the file's order, every place, the opening columns");
ok(L.choiceOf({ srcols: "x".repeat(5000) }, table, index).cols.length === 10 && L.choiceOf({ sropen: "op-ercot", sra: "op-ercot", srb: "op-ercot" }, table, index).b === null, "an address is held to what the files offer");
ok(L.srHref({ view: "grids", mw: "300", "x y": "1", long: "v".repeat(2000) }, { srsort: "price.mean_da" }, null) === "/cost-of-power?view=allgrids&mw=300&srsort=price.mean_da", "an address the section writes: the tab's view, the names it came with, bounded");
ok(L.figure(85111) === "85,111" && L.figure(204512.5) === "204,512.50" && L.figure(-2.6) === "-2.60" && L.unitWords("pct") === "%" && L.unitWords("count") === "", "a figure whole or to two decimals; a unit as a reader reads it");
ok(L.heldKind("license needed: x") === "license needed" && L.heldKind("paused: y") === "paused" && L.heldKind("something else") === "not held" && L.heldKind(null) === "not held", "a reason's kind is its first words, or not held");
ok(L.periodWords("2025-11-01..2026-10-31") === "1 Nov 2025 to 31 Oct 2026" && L.periodWords("2027") === "2027" && L.periodWords(null) === "", "a period in words");
ok(L.periodWords("the 730 days to 2026-11-25") === "the 730 days to 25 Nov 2026" && L.periodWords("2025-12-31") === "31 Dec 2025" && L.periodWords("2000..2020") === "2000 to 2020" && L.periodWords("summer 2027 (ERCOT's report)") === "summer 2027 (ERCOT's report)"
  && L.periodWords("2024-11-01..2025-10-31 to 2025-11-01..2026-10-31") === "1 Nov 2024 to 31 Oct 2025 to 1 Nov 2025 to 31 Oct 2026", "a period the builder writes in words of its own is kept, its days written as the site writes a day");
ok(L.ruleHref({ view: "allgrids", mw: "300", rule: "old" }, "texas-04") === "/cost-of-power?view=allgrids&mw=300&rule=texas-04#large-load-rules", "a rule's link: the tab's address with the tab's own name for a rule, at the tab's rules");
ok(L.trendPoints({ months: ["2026-09", "2026-10"], period: "x", v: [1.5, null] }).length === 1 && L.trendPoints(null).length === 0 && L.monthWords("2026-10") === "Oct 2026", "a trend's months that hold a figure; a month in words");
ok(JSON.stringify(L.columnAbout(table, 6)) === JSON.stringify({ period: "2025-11-01..2026-10-31", src: "eia930_demand" }) && JSON.stringify(L.columnAbout(table, 0)) === JSON.stringify({ period: "2025-11-01..2026-10-31", src: "ercot_prices" }), "a column's period and source: its own, or what most of its shown cells share");
const csv = L.tableCsv(table, L.rowsShown(table, c0), L.colsDrawn(table, c0), "/cost-of-power?view=allgrids#regions");
const lines = csv.trim().split("\n"), nHead = lines.findIndex((l) => !l.startsWith("#"));
ok(nHead === 12 && lines[nHead].startsWith("place_id,kind,name,price.mean_da,price.mean_da.not_shown,") && lines.length === nHead + 5, "the CSV: what it is and a line a column above the header, then a row a place");
ok(lines[nHead + 1].startsWith("region-tex,region,Texas,46.31,,,not published,85111,,") && lines[nHead + 3].startsWith("op-nyiso,operator,NYISO,,license needed,"), "the CSV writes a figure as held and a count not shown as an empty cell with its reason's kind beside it");
ok(L.pythonReader(nHead).includes(`skiprows=${nHead}`) && L.stataReader(nHead).includes(`varnames(${nHead + 1})`), "the Python and the Stata reader skip the lines above the header");

// ---- 4. the tab ---------------------------------------------------------------------------------------------------------
const tab = renderToStaticMarkup(h(AllGridsView, { q: { view: "allgrids" } }));
const at = (s) => tab.indexOf(s);
ok(at('data-allgrids-table="1"') > 0 && at('id="regions"') > at('data-allgrids-table="1"') && at('id="large-load-rules"') > at('id="regions"'), "on the tab the section stands after the hub table and before the large-load rules; both are still drawn");
ok((tab.match(/id="regions"/g) ?? []).length === 1 && (tab.match(/<h1/g) ?? []).length === 0, "the section is drawn once");

console.log(failed ? `${failed} of ${n} checks FAILED` : `ok: ${n} checks of the regions section of the All grids tab`);
process.exit(failed ? 1 : 0);
