// Energy Research Warehouse (ERW) site, session 8460 (chain 503, part E): every figure the section "The whole country"
// of /supply prints, for every region and every year its files hold, written to one JSON file for the replication
// (replication/supply/replicate_regions.py), which recomputes each from the files on its own.
//
//   node --import ./scripts/tsx-register.mjs scripts/supply-regions-figures.mjs <out.json>
//   node --import ./scripts/tsx-register.mjs scripts/supply-regions-figures.mjs --fixture <dir>
//
// The files are read where the site reads them (site/data/regions/, or ERW_REGIONS_DIR in a test). The section is
// drawn by the site's own code once for each region and each year (Region B "None"), and what it prints is read off
// the HTML:
//   figures   every checked figure (its data-cn key and the text shown); beside a count of months its "of" (key|of);
//             from the month table's hover, the three figures that stand nowhere on the face: the neighbour's report,
//             the gap and its percent (key|their, key|gap, key|gap_pct); a mix month's days (key days_held and
//             days_in_month) and a mix year's count of months
//   large     the keys of the figures drawn with the mark of a large gap
//   words     for each pair of a year, who the row says sent and who received
//   first     the year drawn when the address names none
// With --fixture the test's fixtures (scripts/regions-fixture-trade.mjs: values made by a rule, not data) are written
// to <dir> in the folder's own form and nothing is drawn. A held file gives no figure, as the page gives none.
import fs from "node:fs";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { CODES, indexFixture, matrixFixture, mixFixture, tradeFixture } from "./regions-fixture-trade.mjs";

const args = process.argv.slice(2);
const put = (dir, rel, v) => { const at = path.join(dir, ...rel.split("/")); fs.mkdirSync(path.dirname(at), { recursive: true }); fs.writeFileSync(at, JSON.stringify(v)); };

if (args[0] === "--fixture") {
  const dir = args[1];
  if (!dir) { console.error("usage: supply-regions-figures.mjs --fixture <dir>"); process.exitCode = 2; }
  else {
    for (const c of CODES) { put(dir, `trade/${c.toLowerCase()}.json`, tradeFixture(c)); put(dir, `mix/${c.toLowerCase()}.json`, mixFixture(c)); }
    put(dir, "trade_matrix.json", matrixFixture());
    put(dir, "index.json", indexFixture());
    console.log(`wrote the fixtures of ${CODES.length} regions, the matrix and the index to ${dir}`);
  }
} else if (!args[0]) {
  console.error("usage: supply-regions-figures.mjs <out.json> | --fixture <dir>");
  process.exitCode = 2;
} else {
  const F = await import("../lib/countryfiles.ts");
  const T = await import("../lib/countrytrade.ts");
  const S = await import("../components/supply/Country.tsx");
  const text =(html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
  const rows = (html) => html.split("<tr").slice(1).map((r) => r.slice(0, r.indexOf("</tr>")));
  const cells = (row) => [...row.matchAll(/<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/g)].map((m) => text(m[1]));

  /** What one drawing of the section prints. */
  function read(html, year) {
    const figures = Object.fromEntries([...html.matchAll(/<span data-cn="([^"]+)">([^<]*)<\/span>/g)].map((m) => [m[1], m[2]]));
    for (const m of html.matchAll(/<span data-cn="([^"]+\|months)">\d+<\/span> of (\d+)/g)) figures[`${m[1]}|of`] = m[2];
    // a month's figure with a neighbour: its hover holds the neighbour's report, the gap and its percent
    for (const m of html.matchAll(/title="([^"]*)"><span data-cn="(trade\|[A-Z]+\|\d{4}-\d\d\|[A-Z]+)">/g)) {
      const their = /reported the same flow as ([-+\d.,]+) GWh/.exec(m[1]), gap = /the gap is ([-+\d.,]+) GWh/.exec(m[1]), pct = /GWh, ([\d.,]+) percent of the mean size/.exec(m[1]);
      if (their) figures[`${m[2]}|their`] = their[1];
      if (gap) figures[`${m[2]}|gap`] = gap[1];
      if (pct) figures[`${m[2]}|gap_pct`] = pct[1];
    }
    const large = [...html.matchAll(/data-gap-large="1"[^>]*><span data-cn="([^"]+)">/g)].map((m) => m[1]);
    const words = {};
    for (const row of rows(html)) {
      const p = /data-wc-pair="([^"]+)" data-wc-kind="([^"]+)"/.exec(row);
      if (!p) continue;
      const c = cells(row);
      words[`${p[2]}|${p[1]}|${year}`] = { sent: c[0], received: c[1] };
    }
    // the mix view: a month's days and the year's count of months
    const at = html.indexOf('data-wc-mix="a" data-wc-region="');
    if (at >= 0) {
      const code = /data-wc-region="([A-Z]+)"/.exec(html.slice(at))[1];
      for (const row of rows(html.slice(at))) {
        const m = /data-wc-month="(\d{4}(?:-\d\d)?)"/.exec(row);
        if (!m) continue;
        const c = cells(row);
        if (m[1].length === 7) {
          const d = /^(\d+)(?: of (\d+))?$/.exec(c[c.length - 1]);
          if (d) { figures[`mix|${code}|${m[1]}|days_held`] = d[1]; if (d[2]) figures[`mix|${code}|${m[1]}|days_in_month`] = d[2]; }
        } else {
          const y = /^\d{4}, (\d+) months?$/.exec(c[0]);
          if (y) figures[`mix|${code}|${m[1]}|months`] = y[1];
        }
      }
    }
    return { figures, large, words };
  }

  const draw = (q) => renderToStaticMarkup(createElement(S.Country, { q }));
  const out = {
    what: "The figures of the section The whole country of /supply, as the site's own code draws them from the files of the whole country: for each region (Region B None) and each year its files hold.",
    large_gap_pct: T.LARGE_GAP_PCT, files: {}, first: null, figures: {}, large: [], words: {},
  };
  const state = (rel, file) => { out.files[rel] = file ? { file: true, held: !!S.heldWhy(file), built: file.built ?? "" } : { file: false }; return file; };
  const matrix = state("trade_matrix.json", T.matrixFile());
  const large = new Set();
  let draws = 0;
  for (const code of F.REGION_CODES) {
    const lower = code.toLowerCase();
    const trade = state(`trade/${lower}.json`, T.tradeFile(code)), mix = state(`mix/${lower}.json`, T.mixFile(code));
    // a region with neither file is drawn only for the matrix, and only while no other drawing has shown it
    if (!trade && !mix && (!matrix || draws)) continue;
    const years = [...new Set([...T.yearsOf(Array.isArray(trade?.months) ? trade.months : []), ...T.yearsOf(Object.keys(mix?.months ?? {})), ...(matrix?.years ?? []).map(String)])].sort();
    const before = Object.keys(out.figures).length;
    for (const year of years) {
      const html = draw({ region: lower, b: "none", year });
      if (!html.includes(`data-wc-a="${code}"`) || !html.includes(`data-wc-year="${year}"`)) { console.error(`${code} ${year}: the section did not draw the region and the year asked for`); process.exitCode = 1; continue; }
      const r = read(html, year);
      Object.assign(out.figures, r.figures);
      Object.assign(out.words, r.words);
      for (const k of r.large) large.add(k);
      draws++;
    }
    console.log(`${code}: ${years.length} years, ${Object.keys(out.figures).length - before} figures more`);
  }
  if (draws) {
    // the year drawn when the address names none (the regions drawn first are the page's own two)
    const y = /data-wc-year="(\d{4})"/.exec(draw({}));
    out.first = { a: S.FIRST_A, b: S.FIRST_B, year: y ? y[1] : null };
  }
  out.large = [...large].sort();
  fs.writeFileSync(args[0], JSON.stringify(out, null, 1) + "\n");
  console.log(`wrote ${args[0]}: ${Object.keys(out.figures).length} figures, ${out.large.length} marked large, ${Object.keys(out.words).length} pairs' words, ${draws} drawings`);
}
