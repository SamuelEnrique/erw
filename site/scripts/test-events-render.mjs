// Energy Research Warehouse (ERW) site, session 7531 (chain 304): /events and its nine event pages drawn to HTML with
// the site's own components, without a build (this machine cannot build the site), on the public rows the replication
// keeps beside it (replication/events/window_rows.csv and notice_rows.csv): no table of the warehouse, no server, no
// network, no click. It holds what session 7531 changed:
//   fault 2: the COVID-19 page says its seven ISO grids are set against 2019 and 2018 (it said 2019 alone), and draws 2018;
//   fault 3: the index's COVID-19 card reads from the week of 2020-03-22 (it led with the week of 2020-03-01);
//   fault 4: the ERCOT 2023 page gives ERCOT's later September records beside the 82,705 MW of September 6;
//   the decisions block on all ten pages (each choice's default, source and session in its hover tip, no grey text,
//   each tip with its one target), the same list as docs/methods/events.md; the replication's figures file.
// It also holds that the license hold of 21 October 2026 is drawn as it stands (fault 1 is a ruling): run without
// EVENTS_DRAW_UNHELD, no figure of an EIA-930 grid or of ISO-NE's, MISO's or NYISO's hub is drawn as a number.
//   node --import ./scripts/events-page-register.mjs scripts/test-events-render.mjs
import fs from "node:fs";
import { csvRows, drawPage, pageText, PAGES } from "./events-pages.mjs";

const { EVENT_DECISIONS, decisionsOf } = await import("../app/events/Decisions.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const here = (p) => new URL(p, import.meta.url);
const tables = {
  event_window_daily: csvRows(here("../../replication/events/window_rows.csv")),
  caiso_grid_emergencies: csvRows(here("../../replication/events/notice_rows.csv")),
};
const rowsOf = (name) => tables[name] ?? null;
const drawn = {};
for (const [slug, file] of PAGES) {
  const { html } = await drawPage(file, rowsOf);
  drawn[slug] = { html, text: pageText(html) };
}
const unheld = process.env.EVENTS_DRAW_UNHELD === "1";
ok(!unheld, "drawn as a visitor's build draws it (EVENTS_DRAW_UNHELD is not set)");

// ---- fault 2: the COVID-19 page's baseline
const cv = drawn["covid-2020"].text;
ok(cv.includes("The baseline of the seven ISO grids is the mean of the same weekday of 2019 and of 2018") && cv.includes("the Lower 48 is not in that file and is set against 2019 alone"),
  "fault 2: the COVID-19 page says the seven grids' baseline is 2019 and 2018, the Lower 48's 2019 alone");
ok(!cv.includes("The baseline is one year, 2019") && !cv.includes("against the same weeks of 2019, all grids") && !cv.includes("Deepest weekly drop against 2019"),
  "fault 2: no sentence of the page says the weekly figures are against 2019 alone");
ok(cv.includes("Weekly demand against the same weeks of earlier years, all grids") && cv.includes("Deepest weekly drop against the baseline"),
  "fault 2: the chart's title and each grid's line name the baseline");
ok(/data-covid-baseline="2018-2019"/.test(drawn["covid-2020"].html), "fault 2: the caveat carries its mark");
ok((cv.match(/2018, same weekday/g) ?? []).length >= 7, "fault 2: each of the seven ISO grids' charts draws its 2018 days");
for (const kept of ["COVID-19: demand in the seven ISO grids, spring 2020", "Price context: ERCOT hub average", "What the estimates say", "Executive Order N-33-20"])
  ok(cv.includes(kept), `the COVID-19 page keeps what it had: ${kept}`);

// ---- fault 3: the index's COVID-19 card
const ix = drawn.index.text;
ok(/Lower 48, deepest weekly drop from the week of 2020-03-22: .*2020-05-17/.test(ix), "fault 3: the index's COVID-19 card reads from the week of 2020-03-22 and picks the week of 2020-05-17");
ok(!/Lower 48, deepest weekly drop: .*2020-03-01/.test(ix), "fault 3: the card no longer leads with the week of 2020-03-01");
ok(["2021-02-07 to 2021-02-24. ERCOT.", "2020-03-01 to 2020-05-31. CAISO", "2026-01-23 to 2026-02-02. PJM"].every((s) => ix.includes(s)), "the index keeps its cards' windows");

// ---- fault 4: ERCOT's later September 2023 records
const er = drawn["ercot-heat-2023"];
ok(er.text.includes("85,464 MW on August 10, 2023") && er.text.includes("84,182 MW on September 8") && er.text.includes("83,911 MW") && er.html.includes("https://www.ercot.com/news/release/09142023-ercot-provides-new"),
  "fault 4: the ERCOT 2023 page quotes ERCOT's release of September 14, 2023, linked");
ok(!er.text.includes("ERCOT's September record of 82,705 MW") && er.text.includes("the 82,705 MW ERCOT announced that evening as its September record"),
  "fault 4: the 82,705 MW is named as what ERCOT announced on September 6, not as the month's record");
ok(er.text.includes("No power outages associated with the ERCOT power grid were necessary"), "the ERCOT 2023 page keeps its quotes of September 6");

// ---- the decisions block on all ten pages
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
for (const [slug] of PAGES) {
  const html = drawn[slug].html;
  const ev = slug === "index" ? undefined : slug.replace(/-/g, "_");
  const list = decisionsOf(ev);
  const block = (/<details[^>]*data-decisions="[^"]*"[\s\S]*?<\/details>/.exec(html) ?? [""])[0];
  const ids = [...block.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]), asked = [...block.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]);
  ok(block.includes(`data-decision-count="${list.length}"`) && (block.match(/data-decision="/g) ?? []).length === list.length
    && list.every((d) => block.includes(`data-decision-default="${d.key}"`) && block.includes(`data-decision-source="${d.key}"`) && block.includes(`data-decision-session="${d.key}"`))
    && asked.length === list.length && asked.every((id) => ids.filter((x) => x === id).length === 1),
    `${slug}: the decisions block draws its ${list.length} choices, each with its default, source and session in its one tip`);
  const outsideTips = block.replace(/<span class="tip[\s\S]*?<\/span><\/span>/g, "");
  ok(!/text-muted|text-xs/.test(outsideTips) && !dash.some((c) => block.includes(c)) && !/\b(should|recommend|we advise)\b/i.test(pageText(block)),
    `${slug}: no grey or small text outside the tips, no dash, no advice in the block`);
}
ok(EVENT_DECISIONS.length === 15 && decisionsOf().length === 13 && decisionsOf("covid_2020").length === 15 && decisionsOf("uri_2021").length === 13, "15 choices: 13 on every page, two more on the COVID-19 page");
ok(drawn["uri-2021"].html.includes("The same calendar days of 2019 and 2020") && drawn["cold-2026"].html.includes("2026-01-23 to 2026-02-02, chosen from EIA"),
  "a choice's default is the event's own where it has one");
const note = fs.readFileSync(here("../../docs/methods/events.md"), "utf-8");
const sec = note.slice(note.indexOf("## The decisions on the pages"));
const keys = [...sec.slice(0, sec.indexOf("\n## ", 5)).matchAll(/^\| \d+ \| `([a-z-]+)` \|/gm)].map((m) => m[1]);
ok(JSON.stringify(keys) === JSON.stringify(EVENT_DECISIONS.map((d) => d.key)), `the method note lists the same ${keys.length} choices in the same order`);

// ---- the hold as it stands (fault 1, a ruling: no hold is lifted here)
let held = 0, eiaShown = 0, heldHubShown = 0;
for (const [slug] of PAGES) {
  const html = drawn[slug].html;
  held += (html.match(/data-license-held="event_window_daily"/g) ?? []).length;
  eiaShown += (html.match(/data-check="(series\|event_window_daily|es)\|[^"]*eia930:/g) ?? []).length;
  heldHubShown += (html.match(/data-check="series\|event_window_daily\|(isone|miso|nyiso):/g) ?? []).length;
}
ok(held > 1000 && eiaShown === 0 && heldHubShown === 0, `the hold is drawn as it stands: ${held} figures "license needed", no EIA-930 figure and no ISO-NE, MISO or NYISO hub figure drawn as a number`);
ok(drawn.index.html.includes('data-check="series|event_window_daily|ercot:HB_HUBAVG|rt_max|2021-02-17'), "ERCOT's hub figures are not held and are drawn");

// ---- the replication's figures file
const fig = JSON.parse(fs.readFileSync(here("../../replication/events/page_figures.json"), "utf-8"));
const count = Object.values(fig.pages).reduce((a, p) => a + p.figures.length, 0);
// session 7531's held-row fix: the 27 figures of ISO-NE's, MISO's and NYISO's hubs are counted (heldFigures), not written
const heldFigures = Object.values(fig.pages).reduce((a, p) => a + (p.heldFigures ?? 0), 0);
ok(count === 1100 && heldFigures === 27 && Object.keys(fig.pages).length === 10 && /^\d{8}T\d{6}Z$/.test(fig.tables.event_window_daily) && fig.pages["caiso-heat-2022"].lines.length === 10,
  `page_figures.json: ${count} figures of ten pages (${heldFigures} held, counted and not written) drawn on the table retrieved ${fig.tables.event_window_daily}, and the ten days of CAISO's notices`);
ok(!/"check": "(series\|event_window_daily|es\|[^|]+)\|(isone|miso|nyiso):/.test(JSON.stringify(fig, null, 1)), "page_figures.json holds no figure of ISO-NE's, MISO's or NYISO's rows");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
