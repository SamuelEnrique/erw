// Energy Research Warehouse (ERW) site, session 7504 (chain 304): the figures /battery/customer shows, read off the
// page's own calculator drawn to HTML, for the replication (replication/battery_customer/).
//   node --import ./scripts/tsx-register.mjs scripts/battery-customer-figures.mjs           (writes the two files)
//   node --import ./scripts/tsx-register.mjs scripts/battery-customer-figures.mjs --check   (compares, writes nothing)
// The page reads no table: a figure is arithmetic on what a reader types. So a case is a set of typed values
// (replication/battery_customer/cases.json). For each case the calculator (app/battery/customer/Calc.tsx) is drawn
// with those values in its fields, as if typed: the fields' starting values are set for the draw and put back after
// (no effect and no click runs in a draw, and the component takes its first values from the fields' list). Every
// number in the words drawn is then read with the sentence it stands in. Nothing here computes a figure: the numbers
// are the page's, as printed. No request, no file read but the cases, nothing stored.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const OUT = new URL("../../replication/battery_customer/", import.meta.url);
const cases = JSON.parse(fs.readFileSync(new URL("cases.json", OUT), "utf-8")).cases;
const lib = await import("../lib/customerbattery.ts");
const { Calc } = await import("../app/battery/customer/Calc.tsx");

const words = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1").trim();
const num = (s) => Number(s.replace(/[$,]/g, ""));
/** Half of the last digit the page shows. */
const tol = (s) => 0.5 * 10 ** -((s.split(".")[1] ?? "").length);
const N = "(-?\\$?[\\d,]+(?:\\.\\d+)?)";

// each sentence of the page with a number in it: its pattern and the figures it carries, in order
const SENTENCES = [
  { re: new RegExp(`On your numbers, a ${N} kW battery holding ${N} kWh \\(${N} hours\\) lowers the bill by ${N} a month, ${N} a year: ${N} a month from a lower peak and ${N} a month from moving energy\\.`),
    keys: [["sum_battery_kw", "The summary: the battery's power, as typed (kW)"], ["sum_battery_kwh", "The summary: the battery's energy, as typed (kWh)"], ["sum_hours", "The summary: the battery's duration (hours)"],
      ["sum_month", "The summary: saved a month (USD)"], ["sum_year", "The summary: saved a year (USD)"], ["sum_demand", "The summary: a month from a lower peak (USD)"], ["sum_energy", "The summary: a month from moving energy (USD)"]] },
  { re: new RegExp(`Saved a year ${N} ${N} a month, twelve months alike\\.`),
    keys: [["tile_year", "Saved a year (USD)"], ["tile_month", "Saved a year: its line, a month (USD)"]] },
  // ruling alternative 3 (wip/alt-battery-customer-3): the tile names the 85 percent and the kW the battery could take
  { re: new RegExp(`From shaving the peak ${N} a month ${N} kW off a ${N} kW peak \\(85 percent of the ${N} kW the battery could take\\); the demand charge was ${N} a month\\.`),
    keys: [["tile_demand", "From shaving the peak (USD a month)"], ["tile_shaved_kw", "From shaving the peak: kW off the peak"], ["tile_peak_kw", "From shaving the peak: the peak, as typed (kW)"], ["tile_could_kw", "From shaving the peak: kW the battery could take (alternative 3)"], ["tile_demand_before", "From shaving the peak: the demand charge before (USD a month)"]] },
  { re: new RegExp(`From shifting energy ${N} a month ${N} kWh a day out at the peak rate, ${N} kWh a day in at the off-peak rate, ${N} days\\.`),
    keys: [["tile_energy", "From shifting energy (USD a month)"], ["tile_out_kwh", "From shifting energy: kWh a day out"], ["tile_in_kwh", "From shifting energy: kWh a day in"], ["tile_days", "From shifting energy: the days, as typed"]] },
  { re: new RegExp(`discharge through all ${N} hours of it\\. Its power allows ${N} kW; its energy allows ${N} kW for that long; your peak is ${N} kW\\. The smallest of the three is what comes off: ${N} kW, set by (the battery's power|the battery's energy|your peak itself)\\. The bill sees 85 percent of it, ${N} kW \\(the National Renewable Energy Laboratory's figure for a 4 hour battery\\)\\. At ${N} per kW that is ${N} a month\\.`),
    keys: [["how_peak_hours", "The peak: its hours, as typed"], ["how_power_kw", "The peak: what the battery's power allows (kW)"], ["how_energy_kw", "The peak: what the battery's energy allows (kW)"], ["how_peak_kw", "The peak: the peak, as typed (kW)"],
      ["how_shaved_kw", "The peak: what comes off (kW)"], ["how_limit", "The peak: what set it"], ["how_billed_kw", "The peak: what the bill sees, 85 percent (kW; alternative 3)"], ["how_demand_charge", "The peak: the demand charge, as typed (USD per kW)"], ["how_demand", "The peak: saved a month (USD)"]] },
  { re: new RegExp(`puts out ${N} kWh in the peak hours and takes in ${N} kWh off-peak \\(more, because of the round trip\\)\\. That is ${N} a day, ${N} over ${N} days\\.`),
    keys: [["shift_out_kwh", "The energy: kWh a day out in the peak hours"], ["shift_in_kwh", "The energy: kWh a day in off-peak"], ["shift_per_day", "The energy: USD a day"], ["shift_month", "The energy: USD over the days"], ["shift_days", "The energy: the days, as typed"]] },
  { re: new RegExp(`the peak rate would have to pass ${N} per kWh\\)\\. So the battery is run only for the peak, ${N} kWh a day, and the energy it loses on the way is a cost: ${N} a month\\.`),
    keys: [["noshift_break_even", "The energy, when moving it does not pay: the peak rate it would take (USD per kWh)"], ["noshift_kwh", "The energy, when moving it does not pay: kWh a day for the peak"], ["noshift_month", "The energy, when moving it does not pay: the cost a month (USD)"]] },
  { re: new RegExp(`Fill in every field to see what the battery saves\\. ${N} of ${N} still needed\\.`),
    keys: [["waiting_needed", "As it opens: fields still needed"], ["waiting_fields", "As it opens: fields in all"]] },
];

function draw(typed) {
  const kept = lib.FIELDS.map((f) => f.start);
  lib.FIELDS.forEach((f) => { f.start = typed[f.key] ?? ""; });
  try { return renderToStaticMarkup(h(Calc)); } finally { lib.FIELDS.forEach((f, i) => { f.start = kept[i]; }); }
}

const out = [];
for (const c of cases) {
  const typed = c.id === "opens" ? Object.fromEntries(lib.FIELDS.map((f) => [f.key, f.start ?? ""])) : c.typed;
  const html = draw(typed);
  const text = words(html);
  const figures = [];
  let covered = text;
  for (const s of SENTENCES) {
    const m = text.match(s.re);
    if (!m) continue;
    covered = covered.replace(m[0], " ");
    s.keys.forEach(([key, name], i) => {
      const shown = m[i + 1];
      figures.push(key === "how_limit" ? { key, name, shown, value: shown, tolerance: null } : { key, name, shown, value: num(shown), tolerance: tol(shown.replace(/[$,-]/g, "")) });
    });
  }
  if (c.id === "opens") {
    for (const [, key, value] of html.matchAll(/data-field="(\w+)"[^>]*? value="([^"]+)"/g)) {
      figures.push({ key: `start_${key}`, name: `As it opens: the starting value of ${key}`, shown: value, value: num(value), tolerance: tol(value) });
    }
  }
  // a number of the result that no sentence above read would be a figure the replication does not see
  const result = covered.slice(Math.max(0, covered.indexOf("Round trip")));
  const stray = c.id === "opens" ? [] : (result.match(/\$[\d,]+|\d[\d,]*\.?\d* (?:kW|kWh|days|hours)\b/g) ?? []);
  out.push({ id: c.id, name: c.name, typed, figures, stray });
}

const n = out.reduce((a, c) => a + c.figures.length, 0);
const json = JSON.stringify({
  about: "ERW, What a battery saves a customer (/battery/customer): every number the page's calculator prints for each case of cases.json, read off the calculator drawn to HTML by site/scripts/battery-customer-figures.mjs. 'shown' is the page's text; 'tolerance' is half of its last shown digit. Written by session 7504; rewrite with the script, never by hand.",
  figures: n, cases: out.map(({ stray, ...c }) => c),
}, null, 1) + "\n";
const q = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
const csv = "case,key,name,shown,value,tolerance\n" + out.flatMap((c) => c.figures.map((f) => [c.id, f.key, f.name, f.shown, f.value, f.tolerance ?? ""].map(q).join(","))).join("\n") + "\n";

const strays = out.filter((c) => c.stray.length);
for (const c of strays) console.log(`NOT READ in ${c.id}: ${c.stray.join(" | ")}`);
for (const c of out) console.log(`${c.id}: ${c.figures.length} figures`);
if (process.argv.includes("--check")) {
  const same = fs.readFileSync(new URL("page_figures.json", OUT), "utf-8").replace(/\r\n/g, "\n") === json && fs.readFileSync(new URL("page_figures.csv", OUT), "utf-8").replace(/\r\n/g, "\n") === csv;
  console.log(same ? `page_figures: ${n} figures, as committed` : "page_figures: the page's figures differ from the committed files");
  if (!same || strays.length) process.exitCode = 1;
} else {
  fs.writeFileSync(new URL("page_figures.json", OUT), json);
  fs.writeFileSync(new URL("page_figures.csv", OUT), csv);
  console.log(`page_figures: ${n} figures of ${out.length} cases written`);
  if (strays.length) process.exitCode = 1;
}
