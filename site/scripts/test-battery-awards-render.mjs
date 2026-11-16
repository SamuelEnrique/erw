// Energy Research Warehouse (ERW) site, session 7505 (chain 304): /cost-of-power/battery/awards drawn to HTML with the
// site's own components, without a build (this machine cannot build the site). It holds what session 7505 changed:
//   fault 1: the node section's words follow the table's whole_days (it said "one week" beside "the 21 whole days held");
//   the decisions block at the foot of the page: every choice with its default, its source and its session on hover,
//   no grey text, each tip with its one target, and the same list as docs/methods/battery_awards.md, section 6;
//   the figures file of the replication is the one the page's functions give, with every drawn figure found.
// Made-up rows only: no table is read. No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-battery-awards-render.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const R = await import("../lib/storagerealtime.ts");
const { RealTimeSection } = await import("../app/cost-of-power/battery/awards/RealTime.tsx");
const { AwardsDecisions, AWARDS_DECISIONS } = await import("../app/cost-of-power/battery/awards/Decisions.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\s+/g, " ");
const read = (...p) => fs.readFileSync(new URL(["..", ...p].join("/"), import.meta.url), "utf-8");

// ---- fault 1: the node section, on made-up rows of one month and a node table of 7, then of 21 whole days
const month = [["days_held", 30], ["days_in_month", 30], ["mw", 1000], ["revenue_da_usd_per_mw", 500], ["revenue_rt_deviation_hub_usd_per_mw", 250], ["revenue_market_hub_usd_per_mw", 750],
  ["rt_discharge_mwh", 40000], ["rt_charge_mwh", 48000], ["da_sold_mwh", 12000], ["da_bought_mwh", 9000]].map(([variable, value]) => ({ variable, ts_utc: "2026-04-01T00:00:00Z", value }));
const basisOfDays = (days) => R.basisOf([["nodes", 200], ["nodes_with_spread", 190], ["whole_days", days], ["spread_hub", 30.5], ["spread_node_median", 41.25], ["spread_node_p10", 28], ["spread_node_p90", 77],
  ["nodes_spread_above_hub", 150], ["mean_abs_difference_median", 4.75]].map(([variable, value]) => ({ variable, ts_utc: "2026-09-28T00:00:00Z", value })));
const draw = (days) => renderToStaticMarkup(h(RealTimeSection, { months: R.rtMonthsOf(month), basis: basisOfDays(days), unread: null, basisUnread: null }));
const w7 = text(draw(7)), w21 = text(draw(21));
ok(w7.includes("one real week at the batteries' own nodes") && w7.includes("it is the week of node prices ERCOT's public list held when it was read, from 28 September 2026")
  && w7.includes("One week is one week.") && w7.includes("Over the 7 whole days held"), "fault 1: a node table of 7 whole days reads as one week, as it did");
ok(w21.includes("21 real days at the batteries' own nodes") && w21.includes("it is the 21 whole days of node prices kept from ERCOT's public list, which holds seven days at a time, from 28 September 2026")
  && w21.includes("It is 21 days of one autumn.") && w21.includes("Over the 21 whole days held"), "fault 1: a node table of 21 whole days says 21 days, in the heading, the sentence and the caution");
ok(!w21.includes("one real week") && !w21.includes("One week is one week") && !w21.includes("the week of node prices"), "fault 1: with 21 whole days no sentence of the section calls them one week");
ok(w21.includes("it is not applied to any figure above, and nothing above is adjusted by it") && w7.includes("it is not applied to any figure above, and nothing above is adjusted by it"), "fault 1: the caution that the measure is applied to nothing is kept in both");
ok(/data-rt-basis-days="21"/.test(draw(21)) && /data-rt-basis-days="week"/.test(draw(7)), "fault 1: the heading carries the days it speaks of");
const none = text(renderToStaticMarkup(h(RealTimeSection, { months: R.rtMonthsOf(month), basis: null, unread: null, basisUnread: null })));
ok(none.includes("one real week at the batteries' own nodes") && none.includes("is not loaded in the site's database"), "the node table not loaded: the section says so and draws no figure of it");

// ---- the decisions block
const html = renderToStaticMarkup(h(AwardsDecisions));
const t = text(html);
ok(/data-decisions="battery-awards"/.test(html) && html.includes(`data-decision-count="${AWARDS_DECISIONS.length}"`) && (html.match(/data-decision="/g) ?? []).length === AWARDS_DECISIONS.length && AWARDS_DECISIONS.length === 15,
  `the decisions block draws its ${AWARDS_DECISIONS.length} choices, one line each`);
ok(AWARDS_DECISIONS.every((d) => d.text && d.def && d.source && d.session && html.includes(`data-decision-default="${d.key}"`) && html.includes(`data-decision-source="${d.key}"`) && html.includes(`data-decision-session="${d.key}"`)),
  "every choice has its default, its source and its session, each in the choice's hover tip");
const ids = [...html.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]), asked = [...html.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]);
ok(asked.length === AWARDS_DECISIONS.length && asked.every((id) => ids.filter((x) => x === id).length === 1) && new Set(AWARDS_DECISIONS.map((d) => d.key)).size === AWARDS_DECISIONS.length,
  `${asked.length} tips, each with its one target, no key twice`);
// the only muted mark allowed is the tip's own "i" button (components/tool/ToolPage.tsx); no line of the block is grey text
const outsideTips = html.replace(/<span class="tip[\s\S]*?<\/span><\/span>/g, "");
ok(!/text-muted/.test(outsideTips) && !/text-xs/.test(outsideTips), "no grey or small text in the block: a default, a source and a session are in the hover tip only");
ok((html.match(/role="tooltip"/g) ?? []).length === AWARDS_DECISIONS.length && /<details[^>]*data-decisions="battery-awards"/.test(html) && /<summary/.test(html), "one fold with a summary, a tooltip for each choice");
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
ok(!dash.some((c) => html.includes(c)), "no em dash and no en dash in the block");
ok(!/\b(should|recommend|we advise|best choice)\b/i.test(t), "the block states choices and takes no view");
const page = read("app", "cost-of-power", "battery", "awards", "page.tsx");
ok(page.includes('import { AwardsDecisions } from "./Decisions";') && page.includes("<AwardsDecisions />") && page.indexOf("<AwardsDecisions />") > page.indexOf("<SourceLine"), "the page mounts the block at its foot, under the source line");
for (const kept of ["What this is not.", "What is counted", "By month", "By year", "Why the two differ", "<OffersSection", "<RealTimeSection", "<MonthBars"]) ok(page.includes(kept), `the page keeps what it had: ${kept}`);

// ---- the method note carries the same list, in the same order
const note = fs.readFileSync(new URL("../../docs/methods/battery_awards.md", import.meta.url), "utf-8");
const sec = note.slice(note.indexOf("## 6. The decisions on the page"));
const keys = [...sec.slice(0, sec.indexOf("\n## 7.")).matchAll(/^\| \d+ \| `([a-z-]+)` \|/gm)].map((m) => m[1]);
ok(JSON.stringify(keys) === JSON.stringify(AWARDS_DECISIONS.map((d) => d.key)), `the method note's section 6 lists the same ${keys.length} choices in the same order`);

// ---- the replication's figures file is the page's own
const fig = JSON.parse(fs.readFileSync(new URL("../../replication/battery_awards/page_figures.json", import.meta.url), "utf-8"));
ok(Object.keys(fig.figures).length >= 300 && fig.drawn.missing.length === 0 && fig.drawn.found === fig.drawn.looked && fig.drawn.looked >= 200,
  `page_figures.json: ${Object.keys(fig.figures).length} figures, ${fig.drawn.found} of ${fig.drawn.looked} of the two drawn sections' figures found in their HTML`);
ok(["ercot_storage_dam_awards_monthly", "battery_stack_monthly", "ercot_storage_dam_offers_monthly", "ercot_storage_rt_monthly", "ercot_storage_node_basis"].every((k) => /^\d{8}T\d{6}Z$/.test(fig.tables[k] ?? "")),
  "page_figures.json names the retrieval stamp of each of the five tables it was computed on");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
