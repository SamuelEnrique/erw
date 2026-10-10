// Energy Research Warehouse (ERW) site, session 182, part 4: the request flow's rules (lib/analysisflow.ts,
// lib/chartforms.ts) against the committed cards and the weekly gallery. No server, no browser, no network.
//
//   node scripts/test-analysis-flow.mjs            the assertions; exits 1 if any fails
//   node scripts/test-analysis-flow.mjs --json     prints, as JSON, step one's list, and for every committed card and
//                                                  every template's default chart: its shape, its default form and the
//                                                  forms offered (tests/test_session182_flow.py reads it)
import fs from "node:fs";
import path from "node:path";
import { register } from "node:module";
import { fileURLToPath } from "node:url";

register("./alias-loader.mjs", import.meta.url);
const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const F = await import("../lib/chartforms.ts");
const A = await import("../lib/analysisflow.ts");

const read = (...p) => JSON.parse(fs.readFileSync(path.join(...p), "utf-8"));
const dir = path.join(site, "data", "findings");
const catalogue = read(dir, "catalogue.json");
const cards = fs.readdirSync(dir).filter((f) => f.endsWith(".json") && f !== "catalogue.json").map((f) => read(dir, f));
const docs = path.join(site, "..", "docs", "analysis");
const templates = read(docs, "templates.json").templates;
const gallery = read(docs, "gallery", "index.json");
const items = A.flowList(catalogue, templates);

const cardRows = cards.map((c) => ({ card_id: c.card_id, id: c.id, kind: c.chart.kind, shape: F.shapeOfSpec(c.chart), forms: F.formsOfSpec(c.chart) }));
const tplRows = gallery.templates.map((g) => {
  const names = A.inputNames(g);
  const params = A.defaultParams(g);
  const combo = A.comboOf(g, params);
  const chart = combo?.file ? read(docs, "gallery", combo.file) : null;
  const all = Object.values(g.combos);
  // every chart the weekly run wrote for this template: the forms offered for each
  const sets = new Set();
  for (const c of all) if (c.file) sets.add(F.formsOfOption(read(docs, "gallery", c.file).option).join(","));
  return { template: g.template, names, params, file: combo?.file ?? null, shape: chart ? F.shapeOfOption(chart.option) : null, forms: chart ? F.formsOfOption(chart.option) : [],
    combos: all.length, held: all.filter((c) => c.file).length, form_sets: [...sets].sort(),
    choices: Object.fromEntries(names.map((n) => [n, [...new Set(all.map((c) => String(c.params[n])))].sort()])) };
});
const out = { items, groups: A.GROUPS, forms: F.FORMS, native: F.NATIVE, internal_form: A.INTERNAL_FORM, templates_order: A.TEMPLATES, cards: cardRows, templates: tplRows,
  max_bar_positions: F.MAX_BAR_POSITIONS, max_panels: F.MAX_PANELS };

if (process.argv.includes("--json")) {
  // the exit waits until stdout has taken every byte (a pipe on Linux takes 64 KiB at a time)
  await new Promise((done) => process.stdout.write(JSON.stringify(out) + "\n", done));
  process.exit(0);
}

let failed = 0;
const check = (ok, what, detail = "") => { if (!ok) failed += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`); };

// step one: every catalogue id and every template, each once
const versionIds = items.flatMap((i) => i.versions.map((v) => v.id));
check(catalogue.every((c) => versionIds.filter((v) => v === c.id).length === 1), "every analysis of the catalogue is in the list exactly once", `${catalogue.length} ids`);
check(items.filter((i) => i.group === "findings").length === 7 && items.filter((i) => i.group === "impact").length === 1, "seven findings and the impact study");
const tItems = items.filter((i) => i.group === "templates");
check(tItems.length === 10 && A.TEMPLATES.every((t, k) => tItems[k]?.template === t), "the ten templates, in the weekly run's order", tItems.map((i) => i.template).join(", "));
check(tItems.filter((i) => i.internal).map((i) => i.template).join() === "chokepoint_transits", "one template is internal: chokepoint_transits");
check(gallery.templates.length === 9 && gallery.templates.every((g) => tItems.some((i) => i.template === g.template && !i.internal)), "the nine templates of the gallery are the nine public entries");

// the default is the form the card's own kind declares, and it is always offered first
for (const r of cardRows) {
  if (r.kind === "none") { check(r.forms.length === 0, `${r.card_id}: a card that draws nothing offers no form`); continue; }
  check(r.forms[0] === F.NATIVE[r.kind], `${r.card_id}: default ${r.forms[0]} is the form of its kind ${r.kind}`, r.forms.join(", "));
}
// each form drawn for each card it fits: an option with the card's own values, and no option where it does not fit
const flat = (o) => JSON.stringify(o, (k, v) => (typeof v === "function" ? undefined : v));
for (const c of cards) {
  if (c.chart.kind === "none") continue;
  const forms = F.formsOfSpec(c.chart);
  for (const f of F.FORMS.map((x) => x.id)) {
    const multiNative = F.isMulti(c.chart) && f === "multiples";
    const o = F.specOption(c.chart, f, 340);
    if (!forms.includes(f)) { check(o === null, `${c.card_id}: ${f} does not fit and draws nothing`); continue; }
    if (multiNative) { check(o === null && F.thumbOfSpec(c.chart, f, 112) !== null, `${c.card_id}: its own small multiples are MultiChart's; the example is drawn`); continue; }
    const p = F.plainSeries(c.chart);
    const held = c.chart.kind === "scatter" ? c.chart.points.length : p.series.reduce((n, s) => n + s.values.length, 0);
    const drawn = c.chart.kind === "scatter" ? o.series[0].data.length : o.series.filter((s) => s.data?.length).reduce((n, s) => n + s.data.length, 0);
    check(o !== null && drawn === held && held > 0, `${c.card_id}: ${f} draws the card's ${held} values`, `${drawn}`);
    if (f !== forms[0] && c.chart.kind !== "scatter") {
      const same = p.series.every((s, i) => flat(o.series[i].data) === flat(s.values));
      check(same, `${c.card_id}: ${f} holds the same numbers, series by series`);
    }
    const t = F.thumbOfSpec(c.chart, f, 112);
    check(t !== null && t.tooltip !== undefined, `${c.card_id}: the example of ${f} is drawn, and answers the mouse`);
  }
}
// the templates: the default is the form the weekly run drew; another form holds the same data
for (const g of gallery.templates) {
  const combo = A.comboOf(g, A.defaultParams(g));
  check(Boolean(combo?.file), `${g.template}: its default inputs hold a chart`);
  if (!combo?.file) continue;
  const chart = read(docs, "gallery", combo.file);
  const forms = F.formsOfOption(chart.option);
  for (const f of forms) {
    const o = F.reformOption(chart.option, f, 360);
    check(o !== null && o.series.length === chart.option.series.length && o.series.every((s, i) => flat(s.data) === flat(chart.option.series[i].data)), `${g.template}: ${f} holds the weekly chart's data`);
    check(F.thumbOfOption(chart.option, f, 112) !== null, `${g.template}: the example of ${f} is drawn`);
  }
  check(F.reformOption(chart.option, forms[0], 360) === chart.option, `${g.template}: the default form is the weekly run's own option, untouched`);
}
// the gallery's inputs: every combination the weekly run wrote can be chosen
for (const g of gallery.templates) {
  const names = A.inputNames(g);
  let reach = 0;
  for (const c of Object.values(g.combos)) {
    const want = Object.fromEntries(names.map((n) => [n, String(c.params[n])]));
    const got = A.validParams(g, want);
    if (names.every((n) => got[n] === want[n]) && A.comboOf(g, got) === c) reach += 1;
  }
  check(reach === Object.keys(g.combos).length, `${g.template}: all ${Object.keys(g.combos).length} combinations of its inputs can be chosen`, `${reach}`);
}
// a grid changed: the hub follows to one the new grid holds; a hub picked by hand is kept, held or not
{
  const g = gallery.templates.find((x) => x.template === "da_rt_spread_by_hour");
  const names = A.inputNames(g);
  const from = A.defaultParams(g);
  const moved = A.validParams(g, { ...from, iso: "caiso" }, "iso");
  check(moved.iso === "caiso" && moved.hub !== from.hub && Boolean(A.comboOf(g, moved)?.file), "da_rt_spread_by_hour: changing the grid moves the hub to one that holds a chart", `${from.hub} to ${moved.hub}`);
  const byHand = A.validParams(g, { ...from, iso: "caiso" }, "hub");
  check(byHand.hub === from.hub && A.comboOf(g, byHand) && !A.comboOf(g, byHand).file, "a hub picked by hand is kept even when the weekly run holds no chart for it", `${byHand.hub}: ${A.comboOf(g, byHand)?.reason}`);
  const held = A.inputChoices(g, names, moved, "hub");
  check(held.findIndex((c) => !c.held) === held.filter((c) => c.held).length, "the choices that hold a chart come first", `${held.filter((c) => c.held).length} of ${held.length}`);
}
console.log(failed ? `${failed} FAILED` : "all passed");
process.exit(failed ? 1 : 0);
