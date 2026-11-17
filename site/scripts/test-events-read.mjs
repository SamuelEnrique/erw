// Energy Research Warehouse (ERW) site, session 7549 (chain 304, part B): /events read as the reader it is for, an
// operator's or a regulator's analyst taking a named event start to finish and checking each figure against the
// operator's own account (docs/reviews/events-read-2026-11-16.md). The pages are drawn with the site's own code on the
// public rows beside the replication (replication/events/window_rows.csv: no license-held row), as the render test
// draws them. It holds what the read fixed:
//   row 1: the Uri page prints the window's highest hour of demand served and the baseline days' highest (the same rows
//          and rule as /learn/problems' worked example), with FERC's 69,871 MW and its 20,000 MW of load shed, linked;
//   row 5: the CAISO 2022 page no longer promises a temperature it does not draw;
//   row 6: the CAISO 2022 page quotes CAISO's record of 52,061 MW, linked, and says why EIA's hour is lower;
//   row 7: the Elliott page gives the inquiry report's two PJM figures beside EIA's hour;
// and that nothing the read added is a figure of a held grid's rows.
//   node --import ./scripts/events-page-register.mjs scripts/test-events-read.mjs
import fs from "node:fs";
import { csvRows, drawPage, pageText, PAGES } from "./events-pages.mjs";

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const here = (p) => new URL(p, import.meta.url);
const window = csvRows(here("../../replication/events/window_rows.csv"));
const tables = { event_window_daily: window, caiso_grid_emergencies: csvRows(here("../../replication/events/notice_rows.csv")) };
const rowsOf = (name) => tables[name] ?? null;
const want = new Set(["uri-2021", "caiso-heat-2022", "elliott-2022"]);
const drawn = {};
for (const [slug, file] of PAGES) {
  if (!want.has(slug)) continue;
  const { html } = await drawPage(file, rowsOf);
  drawn[slug] = { html, text: pageText(html) };
}
ok(process.env.EVENTS_DRAW_UNHELD !== "1", "drawn as a visitor's build draws it (EVENTS_DRAW_UNHELD is not set)");

// The highest of a variable over some years of an event's rows, the first of equal values in day order (the note's rule).
const top = (event, entity, variable, keep) => {
  const xs = window.filter((r) => r.event === event && r.entity === entity && r.variable === variable && keep(r.ts_utc.slice(0, 10)))
    .sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  return xs.reduce((a, b) => (Number(b.value) > Number(a.value) ? b : a), xs[0]);
};
const key = (r, event) => `series|event_window_daily|${r.entity}|${r.variable}|${r.ts_utc}|${event}`;

// ---- row 1: Uri's highest hour, the baseline's, and FERC's account
const uri = drawn["uri-2021"];
const hi = top("uri_2021", "eia930:ERCO", "demand_max_mw", (d) => d.startsWith("2021"));
const hb = top("uri_2021", "eia930:ERCO", "demand_max_mw", (d) => d.startsWith("2019") || d.startsWith("2020"));
ok(hi.ts_utc.startsWith("2021-02-14") && Number(hi.value) === 69215 && hb.ts_utc.startsWith("2020-02-14") && Number(hb.value) === 54634,
  "the rows: the window's highest hour 69,215 MW on 2021-02-14, the baseline days' 54,634 MW on 2020-02-14");
// As a visitor's build draws it today the two are "license needed" (part A's fault 1, a ruling: the hold reads a key of
// no grid as the table whole); the figures file, drawn with the hold set aside, gives each with its row's key.
const peakSpan = (/data-events-read="uri-peak"([\s\S]*?)<\/span>\.?\s*Lowest/.exec(uri.html) ?? [])[1] ?? "";
ok((peakSpan.match(/data-license-held="event_window_daily"/g) ?? []).length === 2, "row 1: as the hold stands, both figures are drawn \"license needed\" (fault 1), not left off");
const figs = JSON.parse(fs.readFileSync(here("../../replication/events/page_figures.json"), "utf-8")).pages["uri-2021"].figures;
const fk = (r) => figs.find((f) => f.check === key(r, "uri_2021"));
ok(fk(hi)?.shown === "69,215" && fk(hb)?.shown === "54,634", "row 1: the page prints both through the checked-number component, each with its row's key (the replication's figures file)");
ok(uri.text.includes("Highest hour of demand served in the window:") && uri.text.includes("on 2021-02-14; the highest on the same days of 2019 and 2020 was")
  && uri.text.includes("(2020-02-14)"), "row 1: the sentence names both days");
ok(uri.text.includes("69,871 MW") && uri.text.includes("ERCOT's 2021 all-time winter peak load") && uri.text.includes("20,000 MW as the firm load ERCOT shed")
  && uri.html.includes("https://www.ferc.gov/sites/default/files/2022-12/A-3%20-%20The%20February%202021%20Cold%20Weather%20Outages"),
  "row 1: FERC's peak and load shed are quoted, linked to FERC's copy of the report");
ok(uri.text.includes("Lowest hour of demand served in the window:") && uri.text.includes("the first day of rotating outages"), "row 1: the Uri page keeps its lowest-hour sentence");
// /learn/problems' worked example (lib/problems.ts, set C) reads the same rows by the same rule: the two pages agree
const problems = fs.readFileSync(here("../lib/problems.ts"), "utf-8");
ok(/ev\("uri_2021", "eia930:ERCO", "demand_max_mw"\)/.test(problems) && problems.includes('ud.filter((x) => x.ts_utc.startsWith("2021"))')
  && problems.includes('pick(ud21, "max"), hib = pick(udb, "max")'), "row 1: /learn/problems' Uri example takes the same rows and rule, so the two pages print the same two figures");

// ---- rows 5 and 6: CAISO, September 2022
const ca = drawn["caiso-heat-2022"];
ok(!ca.text.includes("against the same weekdays 364 and 728 days earlier, with the temperature at Sacramento and Los Angeles.")
  && ca.text.includes("the temperature at Sacramento and Los Angeles enters the second estimate at the foot of the page"),
  "row 5: the framing no longer promises a temperature the page does not draw, and says where the temperature is used");
ok(ca.text.includes("set a record load of 52,061 MW on Sept. 6") && ca.html.includes("https://www.caiso.com/documents/summerheatwave-presentation-nov21_2022.pdf")
  && ca.text.includes("gives the mean of each hour"), "row 6: CAISO's record is quoted, linked, with why EIA's hour is lower");
ok(ca.text.includes("CAISO's highest hour of demand served in the window was") && ca.text.includes("Energy Emergency Alert 3"), "the CAISO 2022 page keeps its peak sentence and its notices");

// ---- row 7: Elliott, the inquiry report's PJM figures
const el = drawn["elliott-2022"];
ok(el.text.includes("135,296 MW as PJM's peak reported elsewhere") && el.text.includes("134,189 MW") && /data-events-read="pjm-ferc"[\s\S]*?24_Winter-Storm_Elliot_0207_UPDATE\.pdf/.test(el.html),
  "row 7: the Elliott page gives the report's 135,296 MW and 134,189 MW, linked");
ok(el.text.includes("about 136,000 MW") && el.text.includes("A date that does not match."), "the Elliott page keeps PJM's quote and the SPP paragraph");

// ---- no held grid in what the read added
const marks = Object.values(drawn).flatMap(({ html }) => [...html.matchAll(/data-events-read="([^"]+)"/g)].map((m) => html.slice(m.index, m.index + 2000)));
ok(marks.length === 3, `the read's three additions are marked (${marks.length})`);
ok(marks.every((s) => !/data-check="series\|[^|"]+\|(isone|miso|nyiso)[:_]/i.test(s)), "no figure the read added is of ISO-NE's, MISO's or NYISO's rows");
ok(!window.some((r) => /^(isone|miso|nyiso)(_load)?(_queue)?:|^iso:(isone|miso|nyiso)/i.test(r.entity)), "the rows drawn on hold no row of a held grid");

console.log(`${n - failed} of ${n} pass`);
if (failed) process.exitCode = 1;
