// Energy Research Warehouse (ERW) site, session 7545 (chain 304, part C): /queues read as a developer deciding where
// to file reads it, for five cases (docs/reviews/queues-read-2026-11-16.md). The page is drawn to HTML by its own
// function (scripts/queues-page.mjs) on the site's own file (data/queues.json, Queued Up, CC BY 4.0), and each site
// fault the read found is held here as fixed: the row numbers are the review's. It also holds the page to the two
// other pages that read the same source (the All grids tab's file and the cost of power's model) and checks that no
// figure of a license-held table is drawn or committed. Real rows; no server, no network, no click.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-queues-read.mjs
import fs from "node:fs";
import { drawQueues, pageText } from "./queues-page.mjs";

const q = await import("../lib/queues.ts");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const read = (...p) => fs.readFileSync(new URL(["..", ...p].join("/"), import.meta.url), "utf-8");
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const file = JSON.parse(read("data", "queues.json"));
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1], x[2]]));
const pages = {};
const draw = async (grid, tech) => { const k = `${grid}|${tech}`; if (!pages[k]) { const html = await drawQueues({ grid, tech }); pages[k] = { html, text: pageText(html) }; } return pages[k]; };

/** Every number a drawn page marks, against the file: the page's own keys and the keys this session added. */
function wrongKeys(html, grid, tech) {
  const got = marked(html), v = q.viewOf(file, grid, tech), wrong = [];
  const want = (k, val) => { if (k in got && got[k] !== val) wrong.push(`${k}: page ${got[k]}, file ${val}`); };
  const two = (x) => (x === undefined ? undefined : q.two(x));
  for (const [k, val] of Object.entries(got)) {
    const p = k.split("|");
    if (p[0] === "grid" || p[0] === "kind") {
      const kv = p[0] === "grid" ? q.viewOf(file, p[1], tech) : q.viewOf(file, grid, p[1]);
      const x = kv?.whole[p[2]];
      want(k, p[2].startsWith("total_") ? q.whole(x) : two(x));
    } else if (p[0] === "year") want(k, q.whole(v.years[p[1]][p[2]]));
    else if (p[0] === "on") want(k, p[2] === "on_requests_dated" ? q.whole(v.on[p[1]][p[2]]) : q.two(v.on[p[1]][p[2]]));
    else if (val === undefined) wrong.push(k);
  }
  return { wrong, count: Object.keys(got).length };
}

// ---- case 1: a 200 MW standalone battery, ERCOT against CAISO
{
  const { html, text } = await draw("ercot", "battery");
  ok(text.includes("At the end of 2025, 660 standalone battery requests were active in ERCOT's queue, for 120,941 MW. Of the 75 that entered from 2000 to 2020, 14.67 percent reached operation and 26.67 percent were withdrawn. Those that were built took a median of 3.93 years from request to operation."),
    "case 1: the page's sentence for ERCOT's standalone batteries, as it was");
  // row 1: every grid for the chosen technology, side by side
  const rows = [...html.matchAll(/data-n="grid\|([a-z]+)\|total_active_mw"/g)].map((x) => x[1]);
  ok(rows.join() === q.GRIDS.filter((g) => q.viewOf(file, g.slug, "battery")).map((g) => g.slug).join(), `row 1: the technology's table has a row for each of the ${rows.length} grids that hold it`);
  const lines = text.split("\n");
  ok(lines.includes("ERCOT | 120,941 | 660 | 14.67 | 26.67 | 3.93 |") && lines.includes("CAISO | 47,499 | 170 | 10.63 | 71.65 | 6.84 |"), "row 1: ERCOT and CAISO side by side in one table, the file's figures");
  const { wrong, count } = wrongKeys(html, "ercot", "battery");
  ok(wrong.length === 0 && count > 100, `every marked number on the page is the file's (${count})${wrong.length ? ": " + wrong.slice(0, 3).join("; ") : ""}`);
  // row 2: the one operation year that holds a median is written out
  ok(html.includes('data-chart="years-one"') && text.includes("those that began operating in 2025 took a median of 3.94 years from request to operation, over 37 dated requests"),
    "row 2: ERCOT's standalone batteries: 2025, 3.94 years over 37 dated requests, in words (no line from one point)");
}
{
  const one = Object.entries(file.views).filter(([, v]) => q.onYears(v).filter((p) => p.year >= 2000).length === 1).map(([k]) => k);
  let good = 0;
  for (const k of one) { const [g, t] = k.split("|"); const { html } = await draw(g, t); if (html.includes('data-chart="years-one"') && !html.includes("data-on=")) good++; }
  ok(one.length > 0 && good === one.length, `row 2: each of the ${one.length} views with one operation year writes it in a sentence`);
}

// ---- case 2: a solar-with-storage project, ERCOT against PJM
{
  const flat = Object.entries(file.views).filter(([, v]) => q.noneWithdrawn(v, file.min_share)).map(([k]) => k);
  ok(flat.join() === "ercot|solar_battery", `row 3: one view of the file labels no withdrawn request at all though it counts a share (${flat.join()})`);
  const { html } = await draw("ercot", "solar_battery");
  const tips = [...html.matchAll(/title="([^"]*)" data-none-withdrawn="ercot\|solar_battery"/g)].map((x) => ent(x[1]));
  ok(tips.length === 3 && tips.every((t) => t.startsWith("The file holds no withdrawn and no suspended solar-with-storage requests in ERCOT, in any year, while 1,100 of ERCOT's requests of every technology with a year entered are withdrawn.")),
    `row 3: ERCOT's 0.00 percent withdrawn carries the hover in the headline, the technology table and the grid table (${tips.length})`);
  const all = q.viewOf(file, "ercot", "all");
  ok(q.withdrawnOf(all) === 1100, "row 3: the 1,100 of the hover is the file's withdrawn ERCOT requests with a year entered");
  const pjm = await draw("pjm", "solar_battery");
  const marks = [...pjm.html.matchAll(/data-none-withdrawn="([^"]+)"/g)].map((x) => x[1]);
  ok(marks.join() === "ercot|solar_battery" && pjm.text.split("\n").includes("PJM | 13,667 | 146 | 3.07 | 83.33 | 1.46 |"), "row 3: on PJM's page the hover is on ERCOT's row of the grid table only, not where the file holds withdrawn requests (PJM: 83.33)");
}

// ---- case 3: a wind developer in SPP, the requests that entered in 2018
{
  const { html, text } = await draw("spp", "wind");
  ok(html.includes('data-years-table="1"') && text.split("\n").includes("2018 | 41 | 8,210 | 1 | 28 | 12 | 0 | 1,893 |"),
    "row 4: the year 2018 in counts (41 entered, 1 reached operation, 28 withdrawn, 12 still active), not only in a bar's hover");
  const v = q.viewOf(file, "spp", "wind");
  const years = [...html.matchAll(/data-n="year\|(\d{4})\|requests_entered"/g)].map((x) => x[1]);
  ok(years.join() === Object.keys(v.years).sort().join(), `row 4: a row for each of the ${years.length} years the view holds`);
  const { wrong } = wrongKeys(html, "spp", "wind");
  ok(wrong.length === 0, `row 4: every count of the years table is the file's${wrong.length ? ": " + wrong.slice(0, 3).join("; ") : ""}`);
  // row 5: the operators' own lists, counted elsewhere, named with links
  ok(html.includes('data-other-source="1"') && html.includes('href="/explore/interconnection"') && html.includes('href="/map?tab=queues"'), "row 5: the lead names the explorer and the map's Queues tab as another source");
  const other = read("lib", "explore", "interconnection.ts") + read("app", "explore", "interconnection", "page.tsx");
  ok(/\/queues/.test(other), "row 5: the explorer names this page in turn");
}

// ---- case 4: offshore wind in NYISO and ISO-NE
{
  const ny = await draw("nyiso", "offshore_wind"), ne = await draw("isone", "offshore_wind");
  ok(ny.text.includes("At the end of 2025, 5 offshore wind requests were active in NYISO's queue, for 4,371 MW.") && ne.text.includes("At the end of 2025, 8 offshore wind requests were active in ISO-NE's queue, for 6,027 MW."),
    "case 4: NYISO 4,371 MW in 5 requests, ISO-NE 6,027 MW in 8 (Queued Up, public under CC BY 4.0)");
  const dateless = [...ne.html.matchAll(/data-dateless="isone"/g)].length;
  ok(dateless >= 3 && ne.html.includes("ISO-NE&#x27;s requests that reached operation carry no operation date in the file"), `row 9: ISO-NE's "not held" wait says why on hover (${dateless} cells)`);
  ok([...ny.html.matchAll(/data-dateless="isone"/g)].length === 1, "row 9: on NYISO's page only ISO-NE's row of the grid table carries the hover; NYISO's own \"not held\" keeps the floor's meaning");
}

// ---- case 5: a 500 MW data center in ERCOT
{
  const { html } = await draw("ercot", "all");
  const li = (html.match(/<li data-no-load="1">([\s\S]*?)<\/li>/) ?? ["", ""])[1];
  ok(li.includes("no edition of the file") && li.includes('href="/datacenters"') && li.includes('href="/cost-of-power?view=allgrids"'), "row 6: the fold says the file holds no load and names the two pages that hold the load side");
}

// ---- rows 7 and 8: words
{
  const caiso = await draw("caiso", "battery"), us = await draw("us", "all");
  ok(caiso.text.includes("Suspended, and not counted here: 1 request, 59 MW.") && !/\b1 requests\b/.test(caiso.text), "row 7: one suspended request is \"1 request\"");
  ok(us.text.includes("were active in the United States' queues") && !us.text.includes("United States's"), "row 8: \"the United States' queues\"");
}

// ---- the figures this page shares with other pages
{
  // the All grids tab's "Time to connect" (site/data/siting/connect.json): plants that came online 2023 to 2025, the
  // same file. Its count of each grid is this page's three operation years added, where each year holds a median.
  const c = JSON.parse(read("data", "siting", "connect.json"));
  const res = [];
  for (const [g, x] of Object.entries(c.grids)) {
    const v = q.viewOf(file, g, "all");
    const ys = [2023, 2024, 2025].map((y) => v.on[String(y)]);
    if (ys.every(Boolean)) res.push([g, x.n, ys.reduce((a, r) => a + r.on_requests_dated, 0)]);
  }
  ok(res.length >= 5 && res.every(([, a, b]) => a === b), `the All grids tab's count of plants online 2023 to 2025 is this page's, grid by grid (${res.map(([g, a, b]) => `${g} ${a}/${b}`).join(", ")})`);
  ok(c.vintage === file.vintage, `the All grids tab and this page read the same edition (${file.vintage})`);
  // the cost of power's "how soon" reads this page's own file, by the same function
  const model = read("app", "cost-of-power", "model.ts");
  ok(model.includes('import queuesJson from "@/data/queues.json"') && model.includes('viewOf(QUEUES, x.grid, "all")'), "the cost of power's model reads the same file through the same viewOf");
}

// ---- the license: nothing held is drawn or committed
{
  const L = JSON.parse(read("data", "license_status.json"));
  const st = (t) => (L.tables[t] ?? L.all[t])?.status;
  ok(st("interconnection_queue_summary") === "public" && st("lbnl_interconnection_queue") === "public", "the page's two tables are public (Queued Up, CC BY 4.0)");
  ok(["iso_queue_statistics", "nyiso_interconnection_queue", "miso_interconnection_queue", "isone_interconnection_queue"].every((t) => st(t) === "license needed"), "the operators' queue tables of NYISO, MISO and ISO-NE are held, as the read assumed");
  const page = read("app", "queues", "page.tsx");
  ok(!/lib\/supabase|rest\(|iso_queue_statistics|(nyiso|miso|isone)_interconnection_queue/.test(page), "the page reads no live table and no operator's queue table (held for NYISO, MISO, ISO-NE)");
  const review = fs.readFileSync(new URL("../../docs/reviews/queues-read-2026-11-16.md", import.meta.url), "utf-8");
  ok(!/(miso|nyiso|isone):queue_\d{4}/.test(review) && !/^(miso|nyiso|isone):/m.test(review), "the read names no row of a held operator's queue table");
  const dash = String.fromCharCode(0x2014);
  ok(![page, read("lib", "queues.ts"), review, read("scripts", "test-queues-read.mjs"), read("scripts", "queues-page.mjs")].some((t) => t.includes(dash)), "no em dash in the files this session wrote");
}

console.log(`${n - failed} of ${n} checks pass`);
process.exitCode = failed ? 1 : 0;
