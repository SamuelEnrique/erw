// Energy Research Warehouse (ERW) site, session 7536 (chain 304): every figure /play/ev shows a player, read off the
// game drawn to HTML with the site's own code, for the replication (replication/ev_game/).
//   node --import ./scripts/tsx-register.mjs scripts/ev-game-figures.mjs           (writes page_figures.json and .csv)
//   node --import ./scripts/tsx-register.mjs scripts/ev-game-figures.mjs --check   (compares, writes nothing)
// The game (app/play/ev/EvGame.tsx) is drawn as the page draws it (site/data/ev_prices.json, the United States at the
// defaults), then once for each state as if chosen in the menu, then once for each player's case of
// replication/ev_game/cases.json, through the game's `start` prop (what the game opens with; no effect or click runs in
// a draw). Every number in the drawn words is read with the words around it. Nothing here computes a figure: the
// numbers are the page's, as printed. No request, nothing stored.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const OUT = new URL("../../replication/ev_game/", import.meta.url);
const C = JSON.parse(fs.readFileSync(new URL("cases.json", OUT), "utf-8"));
const D = JSON.parse(fs.readFileSync(new URL("../data/ev_prices.json", import.meta.url), "utf-8"));
const { EvGame } = await import("../app/play/ev/EvGame.tsx");
const us = { code: "US", name: "United States", power: D.us.power, gas: D.us.gas };

const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (html) => ent(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1").trim();
/** The number in a shown string ("$4.354", "18.31 cents", "-$1,234", "5.0 percent"), or null for words ("never"). */
const num = (s) => { const m = String(s).match(/-?\$?-?[\d,]*\.?\d+/); return m ? Number(m[0].replace(/[$,]/g, "")) : null; };
const tol = (s) => { const m = String(s).match(/[\d,]*\.?(\d*)/g)?.find((x) => /\d/.test(x)) ?? ""; const dec = m.includes(".") ? m.split(".")[1].length : 0; return 0.5 * 10 ** -dec; };

function figuresOf(html) {
  const f = [];
  // a figure drawn as "$" then its keyed span reads "$ 5,131" once the tags are gone: the space is the tag's, not the page's
  const add = (key, name, shown0) => { const shown = String(shown0).replace(/\$ /g, "$"); const v = num(shown); f.push({ key, name, shown, value: v, tolerance: v === null ? null : tol(shown) }); };
  // the inputs: each field's value as shown, and the default its tip names
  for (const m of html.matchAll(/data-field="(\w+)">([\s\S]*?)<input/g)) {
    const [, id, block] = m;
    const shown = block.match(/<span class="font-mono[^"]*"[^>]*>([^<]+)<\/span>/);
    if (shown) add(`field_${id}`, `The input ${id}, as shown`, ent(shown[1]));
    if (shown) f.push({ key: `field_${id}_mine`, name: `The input ${id}: changed by you`, shown: /data-default="1"/.test(block) ? "default" : "changed by you", value: null, tolerance: null });
    const tip = block.match(/role="tooltip"[^>]*>([\s\S]*?)<\/span>\s*<\/span>/);
    if (tip) {
      const t = words(tip[1]);
      const d = t.match(/^Default (\$?[\d,.]+)/);
      if (d) add(`tip_${id}_default`, `The input ${id}: the default its tip names`, d[1]);
      if (id === "power") { const mo = t.match(/ in ([A-Z][a-z]+ \d{4}), the newest month/); if (mo) f.push({ key: "tip_power_month", name: "The electricity tip: the month", shown: mo[1], value: null, tolerance: null }); }
      if (id === "gas") {
        const wk = t.match(/the week of ([A-Z][a-z]+ \d+, \d{4}); (.*?)\. Table .*?, entity ([^ ]+?)\.$/);
        if (wk) { f.push({ key: "tip_gas_week", name: "The gasoline tip: the week", shown: wk[1], value: null, tolerance: null }); f.push({ key: "tip_gas_where", name: "The gasoline tip: whose price", shown: wk[2], value: null, tolerance: null }); f.push({ key: "tip_gas_entity", name: "The gasoline tip: the entity", shown: wk[3], value: null, tolerance: null }); }
      }
    }
  }
  const credit = html.match(/<label for="ev-credit">[\s\S]*?<span class="(?:font-semibold|text-muted)">(on|off)<\/span>/);
  if (credit) f.push({ key: "credit_switch", name: "The federal credit switch", shown: credit[1], value: null, tolerance: null });
  // the results
  const pb = html.match(/data-payback="true">([\s\S]*?)<div class="mt-1 font-serif[^"]*">([\s\S]*?)<\/div>/);
  if (pb) {
    add("payback", "Payback", words(pb[2]));
    const extra = words(pb[1]).match(/costs more to buy(, after the credit)?: (-?\$[\d,]+)\./);
    if (extra) { add("payback_tip_extra", "Payback's tip: what the EV costs more to buy", extra[2]); f.push({ key: "payback_tip_after_credit", name: "Payback's tip says 'after the credit'", shown: extra[1] ? "yes" : "no", value: null, tolerance: null }); }
  }
  const npv = html.match(/data-npv="true">([\s\S]*?)<div class="mt-1 font-serif[^"]*">([\s\S]*?)<\/div>/);
  if (npv) {
    add("npv", "Net present value", words(npv[2]));
    const hd = words(npv[1]).match(/Net present value, (\d+) years?/); if (hd) add("npv_years", "Net present value: the years in its heading", hd[1]);
    const rt = words(npv[1]).match(/\(at ([\d.]+) percent a year\)/); if (rt) add("npv_tip_rate", "Net present value's tip: the rate", rt[1]);
  }
  for (const [k, re] of [["gas_year", /A year of gasoline<\/th><td[^>]*>([^<]+)</], ["ev_year", /A year of electricity<\/th><td[^>]*>([^<]+)</], ["save_year", /(Saved a year with the EV|Extra a year with the EV)<\/th><td[^>]*>([^<]+)</]]) {
    const m = html.match(re);
    if (!m) continue;
    if (k === "save_year") { f.push({ key: "save_year_label", name: "The third fuel row's name", shown: m[1], value: null, tolerance: null }); add(k, m[1], ent(m[2])); }
    else add(k, k === "gas_year" ? "A year of gasoline" : "A year of electricity", ent(m[1]));
  }
  const sr = words(html).match(/The prices used: ([\d.]+) cents a kWh and ([\d.]+) dollars a gallon\./);
  if (sr) { add("sr_power_cents", "The screen reader's line: cents a kWh", sr[1]); add("sr_gas", "The screen reader's line: dollars a gallon", sr[2]); }
  const lab = html.match(/role="img" aria-label="([^"]+)"/);
  if (lab) {
    const m = ent(lab[1]).match(/Cumulative cost by year, (\d+) years\. Gasoline car from (\$[\d,]+) to (\$[\d,]+); EV from (\$[\d,]+) to (\$[\d,]+)\.(?: The lines cross at ([\d.]+) years\.)?/);
    if (m) {
      add("chart_years", "The chart's summary: years", m[1]); add("chart_gas_start", "The chart: the gasoline car at year 0", m[2]); add("chart_gas_end", "The chart: the gasoline car at the last year", m[3]);
      add("chart_ev_start", "The chart: the EV at year 0", m[4]); add("chart_ev_end", "The chart: the EV at the last year", m[5]);
      f.push({ key: "chart_summary_cross", name: "The chart's summary: where the lines cross", shown: m[6] ?? "none", value: m[6] ? Number(m[6]) : null, tolerance: m[6] ? tol(m[6]) : null });
    }
  }
  const cross = html.match(/>they cross at ([\d.]+) years</);
  f.push({ key: "chart_cross_label", name: "The chart's crossing label", shown: cross ? cross[1] : "none", value: cross ? Number(cross[1]) : null, tolerance: cross ? tol(cross[1]) : null });
  const svg = html.match(/<svg[\s\S]*?<\/svg>/);
  if (svg) {
    const yt = [...svg[0].matchAll(/text-anchor="end"[^>]*>([^<]+)<\/text>/g)].map((m) => m[1]);
    const xt = [...svg[0].matchAll(/text-anchor="middle"[^>]*>([^<]*)<\/text>/g)].map((m) => m[1]).filter((t) => t !== "years");
    f.push({ key: "chart_y_ticks", name: "The chart's money axis", shown: yt.join(" "), value: null, tolerance: null });
    f.push({ key: "chart_x_labels", name: "The chart's year axis (blank: a year not labelled)", shown: xt.map((t) => t || "_").join(" "), value: null, tolerance: null });
  }
  const wait = html.match(/data-ev-waiting="true">([^<]+)</);
  if (wait) f.push({ key: "waiting", name: "The line in place of the results", shown: ent(wait[1]), value: null, tolerance: null });
  // the table for the parents
  const par = html.match(/data-parents="true">([\s\S]*?)<\/details>/);
  if (par) {
    for (const m of par[1].matchAll(/<tr class="border-b border-rule"><th scope="row"[^>]*>([\s\S]*?)<\/th><td[^>]*>([\s\S]*?)<\/td><td[^>]*>([\s\S]*?)<\/td><\/tr>/g)) {
      const name = words(m[1]);
      add(`parents_${name.replace(/[^A-Za-z]+/g, "_").replace(/^_|_$/g, "").toLowerCase()}`, `For your parents: ${name}`, words(m[2]));
      f.push({ key: `parents_src_${name.replace(/[^A-Za-z]+/g, "_").replace(/^_|_$/g, "").toLowerCase()}`, name: `For your parents: ${name}, where it comes from`, shown: words(m[3]), value: null, tolerance: null });
    }
    const b = words(par[1]).match(/Prices built into the game on (\d{4}-\d{2}-\d{2})/);
    if (b) f.push({ key: "built", name: "The day the prices were built into the game", shown: b[1], value: null, tolerance: null });
  }
  for (const m of html.matchAll(/data-check="([^"]+)" data-raw="([^"]+)"/g)) f.push({ key: `raw_${m[1].split("|")[2]}`, name: `The key ${m[1]}: its raw value`, shown: m[2], value: Number(m[2]), tolerance: 1e-9, check: m[1] });
  return f;
}

const cases = [{ id: "opens", name: "The page as it opens: the United States, every default", start: null }];
if (C.every_state) for (const s of D.states) cases.push({ id: `state_${s.code}`, name: `${s.name} chosen in the menu, every default`, start: { code: s.code } });
for (const c of C.moved) cases.push(c);

const out = cases.map((c) => {
  const html = renderToStaticMarkup(h(EvGame, { states: D.states, us, built: D.built_at, ...(c.start ? { start: c.start } : {}) }));
  return { id: c.id, name: c.name, start: c.start, figures: figuresOf(html) };
});
const n = out.reduce((a, c) => a + c.figures.length, 0);
const json = JSON.stringify({
  about: "ERW, Should your family get an EV? (/play/ev): every figure the game shows for each case, read off the game drawn to HTML by site/scripts/ev-game-figures.mjs. 'shown' is the page's text; 'tolerance' half of its last shown digit (null for words). Written by session 7536; rewrite with the script, never by hand.",
  built_at: D.built_at, figures: n, cases: out,
}, null, 1) + "\n";
const q = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
const csv = "case,key,name,shown,value,tolerance\n" + out.flatMap((c) => c.figures.map((f) => [c.id, f.key, f.name, f.shown, f.value ?? "", f.tolerance ?? ""].map(q).join(","))).join("\n") + "\n";
for (const c of out.filter((x) => !x.id.startsWith("state_") || x.id === "state_AL")) console.log(`${c.id}: ${c.figures.length} figures`);
if (process.argv.includes("--check")) {
  const same = fs.readFileSync(new URL("page_figures.json", OUT), "utf-8").replace(/\r\n/g, "\n") === json && fs.readFileSync(new URL("page_figures.csv", OUT), "utf-8").replace(/\r\n/g, "\n") === csv;
  console.log(same ? `page_figures: ${n} figures, as committed` : "page_figures: the page's figures differ from the committed files");
  if (!same) process.exitCode = 1;
} else {
  fs.writeFileSync(new URL("page_figures.json", OUT), json);
  fs.writeFileSync(new URL("page_figures.csv", OUT), csv);
  console.log(`page_figures: ${n} figures of ${out.length} cases written`);
}
