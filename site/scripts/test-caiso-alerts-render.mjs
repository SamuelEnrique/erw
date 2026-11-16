// Energy Research Warehouse (ERW) site, session 7532 (chain 304): /grid/caiso/alerts, the Flex Alert scorecard, drawn to
// HTML with the site's own page function, without a build (this machine cannot build the site). It holds what session
// 7532 changed:
//   fault 1: a value under a million dollars is printed in whole dollars (it printed "-479,791.004");
//   fault 2: the title's years and the last caution (how far CAISO's notices run, and any alert day after the scorecard's
//            last) are read from the rows (the title said "2018 to 2024" and the caution "runs to 2025-04-30");
//   fault 4: the alert day CAISO's notices hold and the scorecard does not score is said on hover;
//   the decisions block at the foot of the page: every choice with its default, its source and its session on hover,
//   no grey text, each tip with its one target, and the same list as docs/methods/caiso_alerts.md, section 6;
//   the replication's figures file is the page's own, drawn on the tables of the machine that wrote it.
// Made-up rows only, except the last part, which reads replication/caiso_alerts/page_figures.json. No server, no network.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-caiso-alerts-render.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const { drawPage, figuresOf, text } = await import("./caiso-alerts-figures.mjs");
const { AlertsDecisions, ALERTS_DECISIONS } = await import("../app/grid/caiso/alerts/Decisions.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const read = (...p) => fs.readFileSync(new URL(["..", ...p].join("/"), import.meta.url), "utf-8");

// ---- made-up tables: two alert days, 2019-07-28 (no price) and 2023-07-20 (a price, a value under a million)
const s = (entity, variable, ts_utc, value, freq = "") => ({ entity, variable, ts_utc, value: String(value), unit: "", freq });
function effects() {
  const rows = [];
  for (const [day, cut, value] of [["2019-07-28", 250.5, null], ["2023-07-20", -900.25, -479791.0043]]) {
    const ts = `${day}T00:00:00Z`;
    for (const [v, x] of [["reduction_mw", cut], ["reduction_mw_lo", cut - 1000], ["reduction_mw_hi", cut + 1000], ["reduction_pct", cut / 400], ["alert_first_hour", 18], ["alert_last_hour", 21],
      ["hours_assumed", 0], ["temp_max_f", 95.5], ["train_days_as_hot", 4]]) rows.push(s("eia930:CISO", v, ts, x, "P1D"));
    if (value !== null) for (const [v, x] of [["value_usd", value], ["value_usd_lo", value * 2], ["value_usd_hi", value / 2]]) rows.push(s("eia930:CISO", v, ts, x, "P1D"));
    for (let hr = 12; hr <= 23; hr++) {
      const t = new Date(Date.parse(ts) + (hr + 7) * 3600_000).toISOString().replace(".000Z", "Z");
      for (const [v, x] of [["actual_mw", 40000 + hr * 100], ["predicted_mw", 40000 + hr * 100 + cut], ["predicted_mw_lo", 39000 + hr * 100], ["predicted_mw_hi", 41500 + hr * 100], ["alert_hour", hr >= 18 && hr < 21 ? 1 : 0]])
        rows.push(s("eia930:CISO", v, t, x, "PT1H"));
    }
  }
  for (const [y, d] of [["2019", 1], ["2023", 1]]) for (const [v, x] of [["year_days", d], ["year_hours", 3], ["year_reduction_mw", 10], ["year_reduction_mw_lo", -500], ["year_reduction_mw_hi", 600], ["year_reduction_mwh", 30]])
    rows.push(s("eia930:CISO", v, `${y}-01-01T00:00:00Z`, x, "P1Y"));
  return { header: [], rows };
}
function model() {
  const T0 = "2018-07-01T00:00:00Z", rows = [];
  for (const [v, x] of [["pooled_days", 2], ["pooled_hours", 6], ["pooled_reduction_mw", -324.875], ["pooled_reduction_mw_lo", -900], ["pooled_reduction_mw_hi", 300], ["pooled_reduction_pct", -0.8], ["pooled_reduction_mwh", -1949.25],
    ["pooled_reduction_mwh_lo", -5000], ["pooled_reduction_mwh_hi", 2000], ["oos_bias_mw", -239.34], ["oos_rmse_mw", 1598.6], ["oos_mape_pct", 3.18], ["oos_days", 2], ["heldout_threshold_temp_f", 87.008],
    ["alert_days_hotter_than_threshold", 2], ["pooled_value_hours", 3], ["pooled_value_usd", -479791.0043], ["pooled_value_usd_lo", -900000], ["pooled_value_usd_hi", -100000], ["heldout_price_mean_usd_mwh", 137.07]]) rows.push(s("erw:flex_alert_model", v, T0, x));
  for (const id of ["minimal", "base", "base_prev24sq", "base_cdh_dew", "chosen"]) for (const v of ["oos_bias_mw", "oos_rmse_mw", "pooled_reduction_mw", "pooled_reduction_mw_lo", "pooled_reduction_mw_hi"]) rows.push(s("erw:flex_alert_model", `variant_${id}_${v}`, T0, 1.5));
  rows.push(s("erw:flex_alert_model", "coef_h00_cdh", T0, 10.1));
  for (const [d, e, t] of [["2019-08-01", -300, 88.1], ["2024-07-02", 150, 92.4]]) for (const [v, x] of [["heldout_error_mw", e], ["heldout_temp_max_f", t], ["heldout_price_usd_mwh", 137.07]]) rows.push(s("erw:flex_alert_model", v, `${d}T00:00:00Z`, x, "P1D"));
  return { header: [], rows };
}
const notice = (id, date, type) => ({ event_id: id, event_date: date, event_type: type, x_region: "ISO", x_time_frame: "", x_start: "", x_end: "" });
const base = [notice("a1", "2019-07-28", "warning"), notice("a2", "2023-07-20", "eea1"), notice("a3", "2023-07-20", "rmo"), notice("a4", "2026-10-08", "rmo")];
const drawn = async (notices) => figuresOf((await drawPage({ flex_alert_effects: effects(), flex_alert_model: model(), caiso_grid_emergencies: { header: [], rows: notices } })).html);

const f0 = await drawn(base);
const html0 = (await drawPage({ flex_alert_effects: effects(), flex_alert_model: model(), caiso_grid_emergencies: { header: [], rows: base } })).html;
const tn = (x) => x.replace(/ ([,;:.)])/g, "$1").replace(/\( /g, "(");  // React writes a text break as a comment, which reads as a space
const t0 = tn(text(html0));
// fault 1
const v2023 = f0.ranked.find((r) => r.day === "2023-07-20");
ok(v2023 && v2023.value === "-479,791" && !t0.includes("479,791.004"), `fault 1: a value under a million is in whole dollars (${v2023?.value})`);
ok(t0.includes("-479,791 USD"), "fault 1: the pooled value under a million is in whole dollars too");
// fault 2
ok(f0.words.h1 === "The Flex Alert scorecard: CAISO, 2019 to 2023", `fault 2: the title's years are the rows' first and last alert days (${f0.words.h1})`);
ok(f0.words.report_ends === "2026-10-08" && f0.words.later_alert_days === 0 && t0.includes("it lists no Flex Alert or emergency notice after 2023-07-20, so the seasons since have none here"),
  "fault 2: the caution says how far the notices run, and that no alert notice follows the last scored day");
ok(!t0.includes("runs to 2025-04-30") && !t0.includes("the 2025 season has none here"), "fault 2: the old fixed words are gone");
const f1 = await drawn([...base, notice("b1", "2025-08-14", "flex_alert"), notice("b2", "2025-08-15", "flex_alert"), notice("b3", "2025-08-15", "eea_watch")]);
const t1 = tn(text((await drawPage({ flex_alert_effects: effects(), flex_alert_model: model(), caiso_grid_emergencies: { header: [], rows: [...base, notice("b1", "2025-08-14", "flex_alert"), notice("b2", "2025-08-15", "flex_alert"), notice("b3", "2025-08-15", "eea_watch")] } })).html));
ok(f1.words.later_alert_days === 2 && t1.includes("it lists 2 days with a Flex Alert or emergency notice after 2023-07-20 (2025-08-14, 2025-08-15) that the scorecard does not yet hold"),
  "fault 2: alert days after the scorecard's last are counted and named, not called none");
const t2 = tn(text((await drawPage({ flex_alert_effects: effects(), flex_alert_model: model() })).html));
ok(t2.includes("whose notices could not be read here: how far it runs is not said") && t2.includes("The Flex Alert scorecard: CAISO, 2019 to 2023"),
  "fault 2: the notices unread, the caution says so and the rest of the page draws");
// fault 4
ok(f0.words.tip_left_out && /data-tip="alerts-left-out"/.test(html0) && t0.includes("2021-07-12 (a Flex Alert, 16:00 to 21:00) lacks a complete day of demand and weather"),
  "fault 4: the unscored alert day is said in a hover tip beside the ranked table's lead");
// the page keeps what it had
for (const kept of ["The answer, pooled", "Every alert day, ranked", "Year by year", "Each alert day through the evening", "What it was worth, at the day-ahead price", "The model's check: the hottest days it did not see", "What the estimate can and cannot say"])
  ok(t0.includes(kept), `the page keeps its section: ${kept}`);
ok(f0.ranked.length === 2 && f0.panels.length === 2 && f0.svgs.length === 4, "the ranked table, the day panels and the four charts draw on the made-up rows");
ok(f0.nums.length > 60 && !f0.nums.some((x) => x.key.includes("coef_")), `${f0.nums.length} checked numbers, no coefficient among them`);
ok(f0.ranked.find((r) => r.day === "2019-07-28")?.notices === "Warning" && f0.ranked.find((r) => r.day === "2023-07-20")?.notices === "EEA 1", "the notices cell lists the day's kinds, RMO left out");

// ---- the decisions block
const html = renderToStaticMarkup(h(AlertsDecisions));
const t = text(html);
ok(/data-decisions="caiso-alerts"/.test(html) && html.includes(`data-decision-count="${ALERTS_DECISIONS.length}"`) && (html.match(/data-decision="/g) ?? []).length === ALERTS_DECISIONS.length && ALERTS_DECISIONS.length === 11,
  `the decisions block draws its ${ALERTS_DECISIONS.length} choices, one line each`);
ok(ALERTS_DECISIONS.every((d) => d.text && d.def && d.source && d.session && html.includes(`data-decision-default="${d.key}"`) && html.includes(`data-decision-source="${d.key}"`) && html.includes(`data-decision-session="${d.key}"`)),
  "every choice has its default, its source and its session, each in the choice's hover tip");
const ids = [...html.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]), asked = [...html.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]);
ok(asked.length === ALERTS_DECISIONS.length && asked.every((id) => ids.filter((x) => x === id).length === 1) && new Set(ALERTS_DECISIONS.map((d) => d.key)).size === ALERTS_DECISIONS.length,
  `${asked.length} tips, each with its one target, no key twice`);
const outsideTips = html.replace(/<span class="tip[\s\S]*?<\/span><\/span>/g, "");
ok(!/text-muted/.test(outsideTips) && !/text-xs/.test(outsideTips), "no grey or small text in the block: a default, a source and a session are in the hover tip only");
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
ok(!dash.some((c) => html.includes(c)), "no em dash and no en dash in the block");
ok(!/\b(should|recommend|we advise|best choice)\b/i.test(t), "the block states choices and takes no view");
ok(f0.words.decisions === ALERTS_DECISIONS.length && html0.indexOf('data-decisions="caiso-alerts"') > html0.indexOf("Source:"), "the page mounts the block at its foot, under the source line");
const page = read("app", "grid", "caiso", "alerts", "page.tsx");
ok(page.includes('import { AlertsDecisions } from "./Decisions";') && page.includes("<AlertsDecisions />"), "the page imports and mounts the block");

// ---- the method note carries the same list, in the same order
const note = fs.readFileSync(new URL("../../docs/methods/caiso_alerts.md", import.meta.url), "utf-8");
const sec = note.slice(note.indexOf("## 6. The decisions on the page"));
const keys = [...sec.slice(0, sec.indexOf("\n## 7.")).matchAll(/^\| \d+ \| `([a-z-]+)` \|/gm)].map((m) => m[1]);
ok(JSON.stringify(keys) === JSON.stringify(ALERTS_DECISIONS.map((d) => d.key)), `the method note's section 6 lists the same ${keys.length} choices in the same order`);

// ---- the replication's figures file is the page's own
const fig = JSON.parse(fs.readFileSync(new URL("../../replication/caiso_alerts/page_figures.json", import.meta.url), "utf-8"));
ok(fig.nums.length >= 400 && fig.ranked.length === 38 && fig.panels.length === 38 && fig.svgs.length === 40, `page_figures.json: ${fig.nums.length} checked numbers, 38 ranked rows, 38 panels, 40 charts`);
ok(["flex_alert_effects", "flex_alert_model", "caiso_grid_emergencies"].every((k) => /^\d{8}T\d{6}Z$/.test(fig.tables[k] ?? "")), "page_figures.json names the retrieval stamp of each table it was drawn on");
ok(fig.words.report_ends === "2026-10-08" && fig.words.later_alert_days === 0 && fig.words.h1.endsWith("2018 to 2024"), "on the machine's tables: the notices run to 2026-10-08, no alert day after 2024-07-24");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
