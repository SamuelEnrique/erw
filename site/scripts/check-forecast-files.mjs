// Energy Research Warehouse (ERW) site, session 10401 (chain 720, part C): /forecast drawn by the site's own code on the
// ERW forecast's page files, every place, both series and both metrics, and every figure the page draws set beside the
// file it names. Without a build.
//   node --import ./scripts/events-page-register.mjs scripts/check-forecast-files.mjs [folder of the files]
// The folder is site/data/predict unless one is given (a copy of the files from another branch, before they land).
// A figure on the page carries data-check="pf|predict/<file>|<path>" and data-raw: the value at that path of that file
// must be the raw value. A day's mean absolute errors (computed by the page) are computed again here from the rows.
// Exit 0 when every figure agrees and no page prints "undefined", "NaN" or "null"; 1 otherwise; 0 with a line when the
// files are not there yet (nothing to check).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const dir = path.resolve(process.argv[2] ?? path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "data", "predict"));
if (!fs.existsSync(path.join(dir, "index.json"))) { console.log(`no index.json in ${dir}: the forecast's files are not there yet, nothing to check`); process.exit(0); }
process.env.ERW_PREDICT_DIR = dir;
const { ForecastView } = await import("../app/forecast/view.tsx");
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));
const index = read("index.json");
const cache = new Map();
const doc = (name) => { if (!cache.has(name)) cache.set(name, read(name)); return cache.get(name); };
const at = (name, p) => p.split("/").reduce((v, seg) => (v === undefined || v === null ? undefined : v[/^\d+$/.test(seg) && Array.isArray(v) ? Number(seg) : decodeURIComponent(seg)]), doc(name));
const text = (html) => html.replace(/<title>[^<]*<\/title>/g, " ").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");

let pages = 0, figures = 0, wrong = [], bad = [], dayChecks = 0, blanks = {};
const states = {};
for (const p of index.places) {
  for (const s of ["demand", "price"]) {
    for (const m of ["mape", "mae"]) {
      const html = renderToStaticMarkup(h(ForecastView, { query: { a: p.place, s, m } }));
      pages++;
      const t = text(html);
      const junk = t.match(/.{0,50}(\bundefined\b|\bNaN\b|\bnull\b|\[object Object\]|Infinity).{0,50}/);
      if (junk) bad.push(`${p.place} ${s} ${m}: ${junk[0]}`);
      for (const mt of html.matchAll(/data-check="pf\|predict\/([^|"]+)\|([^"]+)" data-raw="([^"]*)"/g)) {
        figures++;
        const v = at(mt[1], mt[2]);
        if (typeof v !== "number" || String(v) !== mt[3]) wrong.push(`${p.place} ${s}: ${mt[1]} ${mt[2]} page ${mt[3]} file ${v}`);
      }
      if (m === "mape") {
        const shown = /data-fc-tomorrow="a" data-fc-shown="1"/.test(html);
        const st = p.series[s].status;
        states[`${s}:${st}:${shown ? "drawn" : "blank"}`] = (states[`${s}:${st}:${shown ? "drawn" : "blank"}`] ?? 0) + 1;
        for (const b of html.matchAll(/data-fc-blank="tomorrow[^"]*"[^>]*>([^<]*)</g)) blanks[b[1].replace(/^.*: /, "")] = (blanks[b[1].replace(/^.*: /, "")] ?? 0) + 1;
        // the day's errors, computed again
        const day = /data-fc-day-of="([^"]+)"/.exec(html)?.[1];
        if (day) {
          const ser = doc(p.file).series[s];
          const c = Object.fromEntries(ser.history_columns.map((n, i) => [n, i]));
          const rows = ser.history.filter((r) => r[c.local_day] === day);
          const methods = ["erw", "operator", "yesterday", "week_ago"].filter((k) => rows.some((r) => r[c[k]] !== null));
          const used = rows.filter((r) => r[c.actual] !== null && methods.every((k) => r[c[k]] !== null));
          for (const k of methods) {
            const mae = used.reduce((a, r) => a + Math.abs(r[c[k]] - r[c.actual]), 0) / used.length;
            const shownV = new RegExp(`data-n="fc\\|a\\|${s}\\|day\\|${k}" data-fc-day-hours="(\\d+)"[^>]*>([^<]*)<`).exec(html);
            const want = ser.unit === "MW" ? Math.round(mae).toLocaleString("en-US") : mae.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            dayChecks++;
            if (!shownV || shownV[2] !== want || Number(shownV[1]) !== used.length) wrong.push(`${p.place} ${s} day ${day} ${k}: page ${shownV?.[2]} over ${shownV?.[1]} hours, computed ${want} over ${used.length}`);
          }
        }
      }
    }
  }
}
// two places side by side, a few pairs
for (const [a, b, s] of [["region-tex", "region-cal", "demand"], ["region-tex", "region-mida", "price"], ["ba-erco", "ba-pjm", "price"], ["region-ny", "ba-tva", "demand"]]) {
  const html = renderToStaticMarkup(h(ForecastView, { query: { a, b, s } }));
  pages++;
  for (const mt of html.matchAll(/data-check="pf\|predict\/([^|"]+)\|([^"]+)" data-raw="([^"]*)"/g)) { figures++; const v = at(mt[1], mt[2]); if (typeof v !== "number" || String(v) !== mt[3]) wrong.push(`${a}+${b} ${s}: ${mt[1]} ${mt[2]} page ${mt[3]} file ${v}`); }
  const junk = text(html).match(/.{0,50}(\bundefined\b|\bNaN\b|\bnull\b).{0,50}/);
  if (junk) bad.push(`${a}+${b} ${s}: ${junk[0]}`);
}
console.log(`pages drawn: ${pages} (${index.places.length} places, two series, two metrics, and four pairs)`);
console.log(`figures with a key into a file: ${figures}; differing from the file: ${wrong.length}`);
console.log(`a day's errors computed again: ${dayChecks}`);
console.log(`"undefined", "NaN" or "null" on a page: ${bad.length}`);
console.log(`tomorrow, by the index's status: ${JSON.stringify(states)}`);
console.log(`the blanks' words: ${JSON.stringify(blanks)}`);
for (const w of wrong.slice(0, 20)) console.log(`  DIFFERS ${w}`);
for (const w of bad.slice(0, 20)) console.log(`  BAD ${w}`);
process.exitCode = wrong.length || bad.length ? 1 : 0;
