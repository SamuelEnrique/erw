// Energy Research Warehouse (ERW) site, session 7546 (chain 304, part B): /grid/caiso/alerts read as a demand-response
// analyst reads it, for five cases (docs/reviews/caiso-alerts-read-2026-11-16.md). The whole page is drawn to HTML by its
// own function (scripts/caiso-alerts-figures.mjs), its reads answered from the public rows committed beside the
// replication (replication/caiso_alerts/public_rows.csv and notices_rows.csv), and each site fault the read found is
// held here as fixed: the row numbers are the review's. Real rows; no server, no network, no click.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-caiso-alerts-read.mjs
import fs from "node:fs";

const { drawPage, figuresOf, readTable, text } = await import("./caiso-alerts-figures.mjs");
const { hourTip } = await import("../app/grid/caiso/alerts/page.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const at = (...p) => new URL(["..", "..", ...p].join("/"), import.meta.url);
const file = (...p) => fs.readFileSync(at(...p), "utf-8");
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");

// ---- the committed public rows, by table, and the notices
const pub = readTable(at("replication", "caiso_alerts", "public_rows.csv"));
const T = {};
for (const r of pub.rows) (T[r.table] ??= { header: [], rows: [] }).rows.push(r);
T.caiso_grid_emergencies = readTable(at("replication", "caiso_alerts", "notices_rows.csv"));
const { html, asked } = await drawPage(T);
const f = figuresOf(html);
const t = text(html);
ok(asked.filter((a) => /^(flex_alert_effects|flex_alert_model|caiso_grid_emergencies): \d+ rows$/.test(a)).length === 3 && !asked.some((a) => /^(flex|caiso).*(: 0 rows|not answered)$/.test(a)),
  `the page makes its three reads and each is answered from the committed rows (${asked.join("; ")})`);
ok(f.ranked.length === 38 && f.panels.length === 38, "the page draws the 38 scored alert days, ranked and in panels");

// the rows of the two named days, from the committed file
const eff = T.flex_alert_effects.rows;
const hourly = (day) => {
  const by = new Map();
  for (const r of eff.filter((r) => r.freq === "PT1H")) {
    const ms = Date.parse(r.ts_utc) - 7 * 3600_000, d = new Date(ms).toISOString().slice(0, 10), h = new Date(ms).getUTCHours();
    if (d !== day) continue;
    (by.get(h) ?? by.set(h, { ts: {} }).get(h))[r.variable] = Number(r.value);
    by.get(h).ts[r.variable] = r.ts_utc;
  }
  return by;
};
const ranked = (day) => f.ranked.find((r) => r.day === day);

// ---- the five cases as the page answers them
const s6 = ranked("2022-09-06"), a17 = ranked("2020-08-17");
ok(s6 && s6.hours.replace(/\s+/g, "") === "16:00to21:00" && s6.cut.startsWith("-1,452.00") && s6.cut.includes("-4,565.31 to 1,494.75") && s6.as_hot === "1",
  "case 1: 2022-09-06, 16:00 to 21:00, -1,452.00 MW (-4,565.31 to 1,494.75), one training day as hot");
ok(a17 && a17.hours.replace(/\s+/g, "") === "15:00to22:00" && a17.cut.startsWith("460.11") && a17.cut.includes("-2,013.70 to 2,723.91") && a17.as_hot === "21" && a17.notices === "Alert, Flex Alert, Stage 2, Warning",
  "case 2: 2020-08-17, 15:00 to 22:00, 460.11 MW (-2,013.70 to 2,723.91), 21 training days as hot, its four kinds of notice");

// ---- row 1 (cases 1 and 2): the published figures for the two evenings, beside the page's own, with what each measures against
const pubLi = (html.match(/<li data-alerts-published="1">([\s\S]*?)<\/li>/) ?? ["", ""])[1];
const pubT = text(pubLi);
ok(pubT.includes("Published figures for these evenings are measured against a forecast, not against this model."), "row 1: the point says what the published figures are measured against");
ok(pubT.includes("day-ahead peak forecast, 49,824 MW, against the peak, 45,169 MW: 4,655 MW lower") && pubT.includes("Table 5.1") && pubLi.includes('href="https://www.caiso.com/Documents/Final-Root-Cause-Analysis-Mid-August-2020-Extreme-Heat-Wave.pdf"'),
  "row 1: 2020-08-17, CAISO's day-ahead forecast against the peak (49,824, 45,169, 4,655 MW), with the Final Root Cause Analysis's table and link");
const h17 = hourly("2020-08-17"), top = [...h17.values()].reduce((m, v) => (!m || v.predicted_mw > m.predicted_mw ? v : m), null);
const k17 = `series|flex_alert_effects|eia930:CISO|predicted_mw|${top.ts.predicted_mw}`;
ok(pubLi.includes(`data-check="${k17}"`) && f.nums.some((x) => x.key === k17 && x.shown === "45,349.58" && x.section === "What the estimate can and cannot say") && Math.abs(top.predicted_mw - 45349.5832) < 0.001,
  `row 1: the model's highest hour of 2020-08-17 is drawn from its row (${k17}): 45,349.58 MW`);
ok(pubT.includes("more than 2,100 MW within five minutes") && pubT.includes("hour-ahead forecast") && pubLi.includes('href="https://www.eia.gov/todayinenergy/detail.php?id=54039"')
  && pubLi.includes('data-check="series|flex_alert_effects|eia930:CISO|reduction_mw|2022-09-06T00:00:00Z"') && pubT.includes("is -1,452.00 MW"),
  "row 1: 2022-09-06, the EIA's 2,100 MW against the hour-ahead forecast, with its link, beside the page's -1,452.00 MW from its row");

// ---- row 2 (case 3): each hour of a day's chart says its figures on hover
const tips = f.svgs.filter((s) => s.label.startsWith("Actual and predicted")).flatMap((s) => s.hours);
const hoursHeld = new Set(eff.filter((r) => r.freq === "PT1H").map((r) => r.ts_utc)).size;
ok(tips.length === hoursHeld && tips.length === 38 * 12, `row 2: every hour of the 38 charts carries a hover (${tips.length} of ${hoursHeld} hours held)`);
const tipOf = (day, h) => (tips.find((x) => x.at === `${day}|${h}`) ?? {}).tip;
ok(tipOf("2022-09-06", 18) === "18:00 to 19:00: served 50,378 MW, model 49,006 (band 45,513 to 52,196), predicted less served -1,372, alert hour",
  "row 2: 2022-09-06, the hour 18:00 to 19:00: served 50,378 MW, model 49,006, band 45,513 to 52,196, predicted less served -1,372");
ok(tipOf("2022-09-06", 21) === "21:00 to 22:00: served 45,116 MW, model 43,507 (band 41,150 to 45,951), predicted less served -1,609",
  "row 2: an hour after the alert hours says no alert hour");
const h6 = hourly("2022-09-06");
ok([...h6.entries()].every(([h, v]) => tipOf("2022-09-06", h) === hourTip(h, v)), "row 2: each hover of 2022-09-06 is the page's own words over the hour's rows");
ok(f.svgs.filter((s) => s.label.startsWith("Actual and predicted")).reduce((a, s) => a + s.rects, 0) === 204, "row 2: the alert-hour boxes are unchanged (204, the hover strips are not boxes)");
ok(t.includes("Hover over an hour for its figures in MW"), "row 2: the section's lead says the hours carry their figures on hover");
ok(hourTip(19, { actual_mw: 100 }) === "19:00 to 20:00: served 100 MW, model not held (band not held to not held), predicted less served not held", "row 2: an hour with a row missing says not held and fills nothing in");

// ---- row 3 (cases 1 and 2): the event pages' measure is named where the page links them
const evs = text((html.match(/<span data-alerts-events="1">([\s\S]*?)<\/span>/) ?? ["", ""])[1]);
ok(evs.includes("is another measure: each whole day's demand served against the same weekdays one and two years earlier, with and without temperature. It measures the heat, not an alert's cut."),
  "row 3: where the page links the two heat-wave pages it says their day estimates are another measure");

// ---- row 4 (case 2): the programs the first caution names, with their years, and what ran in August 2020
const prog = text((html.match(/<span data-alerts-programs="1">([\s\S]*?)<\/span>/) ?? ["", ""])[1]);
ok(prog.includes("ELRP began in 2021 (CPUC, Decision 21-03-056) and DSGS in 2022 (Assembly Bill 205), so neither ran in 2018 to 2020.") && prog.includes("reliability demand response from the 16th to the 18th") && prog.includes("section 3.3.4"),
  "row 4: the caution gives the two programs' first years and what CAISO and the Governor did in August 2020, with the report's section");
ok(t.includes("On the same days the state dispatches paid programs (the Demand Side Grid Support program, DSGS, and the Emergency Load Reduction Program, ELRP)"), "row 4: the caution's own words are kept");

// ---- rows 5 and 6: the two heat-wave pages link the scorecard, and the 2020 page's sentence that the warehouse holds no weather is gone
const code = (p) => file(...p).replace(/\{\/\*[\s\S]*?\*\/\}/g, "");
const e20 = code(["site", "app", "events", "caiso-heat-2020", "page.tsx"]), e22 = code(["site", "app", "events", "caiso-heat-2022", "page.tsx"]);
ok(!e20.includes("holds no weather or supply data") && e20.includes('<Link href="/grid/caiso/alerts">The Flex Alert scorecard</Link> sets each of 14 to 19 August, hour by hour,') && e20.includes('import { SiteLink as Link } from "@/components/SiteLink";'),
  "row 5: /events/caiso-heat-2020 no longer says the warehouse holds no weather data, and links the scorecard through the release gate");
ok(e22.includes('<Link href="/grid/caiso/alerts">The Flex Alert scorecard</Link> sets each alert day of 2022-08-31 to 2022-09-09') && e22.indexOf("data-events-scorecard") > e22.indexOf("<strong>The peak.</strong>") && e22.indexOf("data-events-scorecard") > e22.indexOf("after={(rows)"),
  "row 6: /events/caiso-heat-2022 links the scorecard in its own paragraph (not in the grey caveat)");
const days20 = ["2020-08-14", "2020-08-15", "2020-08-16", "2020-08-17", "2020-08-18", "2020-08-19"], days22 = ["2022-08-31", "2022-09-01", "2022-09-02", "2022-09-03", "2022-09-04", "2022-09-05", "2022-09-06", "2022-09-07", "2022-09-08", "2022-09-09"];
ok([...days20, ...days22].every((d) => ranked(d)), "rows 5 and 6: every day the two sentences name is a scored alert day");

// ---- the page standard on what this session added: no grey text, no em dash, no view
const added = [pubLi, html.match(/<span data-alerts-events="1">[\s\S]*?<\/span>/)?.[0] ?? "", html.match(/<span data-alerts-programs="1">[\s\S]*?<\/span>/)?.[0] ?? "", html.match(/<span data-alerts-hover="1">[\s\S]*?<\/span>/)?.[0] ?? ""];
ok(added.every((a) => a && !/text-muted|text-xs/.test(a)), "the additions carry no grey or small text");
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
const changed = [["site", "app", "grid", "caiso", "alerts", "page.tsx"], ["site", "app", "events", "caiso-heat-2020", "page.tsx"], ["site", "app", "events", "caiso-heat-2022", "page.tsx"], ["docs", "reviews", "caiso-alerts-read-2026-11-16.md"]];
ok(changed.every((p) => !dash.some((c) => file(...p).includes(c))), "no em dash and no en dash in the files this session changed");
ok(!added.some((a) => /\b(should|recommend|we advise|best choice|plausibl)/i.test(ent(a))), "the additions state facts and take no view");

// ---- no row or figure of a license-held table is committed
const lic = JSON.parse(file("site", "data", "license_status.json"));
const statusOf = (tb) => (lic.all[tb] ?? {}).status ?? "unknown";
const pubTables = [...new Set(pub.rows.map((r) => r.table))];
ok(pubTables.length === 3 && pubTables.every((tb) => statusOf(tb) === "public"), `the committed rows are of public tables only (${pubTables.map((tb) => `${tb} ${statusOf(tb)}`).join(", ")})`);
const fig = JSON.parse(file("replication", "caiso_alerts", "page_figures.json"));
const figTables = [...new Set(fig.nums.map((x) => x.key.split("|")[1]))];
ok(figTables.every((tb) => statusOf(tb) === "public"), `the committed figures file names public tables only (${figTables.join(", ")})`);
const read = file("docs", "reviews", "caiso-alerts-read-2026-11-16.md");
// a table held whole: named only as held, with no figure on its line; a table held by grid: its lines speak of CAISO's
// rows only (the held grids are ISO-NE, MISO and NYISO) and name none of the held grids
const heldNamed = Object.keys(lic.all).filter((tb) => lic.all[tb].status === "license needed" && read.includes("`" + tb + "`"));
const byGrid = (tb) => (lic.all[tb] ?? {}).hold === "by grid";
const linesOf = (tb) => read.split("\n").filter((l) => l.includes("`" + tb + "`"));
ok(heldNamed.filter((tb) => !byGrid(tb)).every((tb) => linesOf(tb).every((l) => /held/i.test(l) && !/\d[.,]\d/.test(l.replace(/\d{4}-\d{2}-\d{2}/g, "")))),
  `the read names a table held whole only as held, with no figure of it (${heldNamed.filter((tb) => !byGrid(tb)).join(", ") || "none named"})`);
ok(heldNamed.filter(byGrid).every((tb) => linesOf(tb).every((l) => /CAISO|2022-09-06|2020-08-17/.test(l) && !/ISO-NE|MISO|NYISO/.test(l))),
  `the read's figures of tables held by grid are CAISO's public rows only (${heldNamed.filter(byGrid).join(", ") || "none named"})`);

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
