// Energy Research Warehouse (ERW) site, session 1167 (chain 078): no held grid's rows are drawn on the Grid tool
// (lib/license.ts; chain 077's rules). Needs no build, no server and no database: the committed files of site/data/,
// the views drawn on the server through the tsx loader, and lib/gridHeld.ts on fixed days.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-held.mjs
//
// 1. The Clean tab's "The seven grids": ISO-NE's, MISO's and NYISO's cells read "license needed" (the view's own
//    placeholder, session 1159's one look), none of their figures is in their row; the four other grids' figures are
//    as they were, text and key.
// 2. The average day and year after year with the price beside the mix: a held grid's hub price reads "license
//    needed"; ERCOT's, CAISO's and SPP's are drawn; MISO keeps its paused words.
// 3. lib/gridHeld.ts: the network's hub prices by code, the queue's positions of energy_projects, on fixed days.
// 4. Session 1415 (chain 107): the Clean tab's carbon blocks (components/grid/Emissions.tsx): no ISO's carbon rows are
//    held on either day (both tables public); heldCarbonRow is licenseHeldRow's rule by entity; and lib/gridKeys.ts
//    carbonRanked and carbonMonthEnds set a held ISO apart (none of its rows returned, the others' ranking as without
//    it), on committed real rows (fixtures/grid_failed_reads.json's hours, fixtures/carbon_monthly.json's months).
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import * as clean from "../lib/clean.ts";
import * as H from "../lib/gridHeld.ts";
import * as K from "../lib/gridKeys.ts";   // session 1415: the carbon blocks' rows
import { LICENSE_NEEDED, licenseHeldRow } from "../lib/license.ts";
import { n1, choiceOf } from "../lib/mixpage.ts";
import * as V from "../components/mix/views.tsx";

const here = path.dirname(fileURLToPath(import.meta.url));
const read = (f) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", f), "utf-8"));
const GRIDS = ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp"];
const HELD = ["isone", "miso", "nyiso"];
const NAME = { caiso: "CAISO", ercot: "ERCOT", isone: "ISO-NE", miso: "MISO", nyiso: "NYISO", pjm: "PJM", spp: "SPP" };
const BEFORE = new Date("2026-10-20T12:00:00Z"), AFTER = new Date("2026-10-24T12:00:00Z");
const text = (h) => h.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "").replace(/&#x27;/g, "'").replace(/&amp;/g, "&");

/** The rows of the table whose caption is `caption`, by the grid name in its row head: { name: html }. */
function rowsOf(html, caption) {
  const at = html.indexOf(`<caption class="sr-only">${caption}</caption>`);
  assert.ok(at >= 0, `the table "${caption}" is drawn`);
  const body = html.slice(at, html.indexOf("</table>", at));
  const out = {};
  for (const m of body.matchAll(/<tr[^>]*><th scope="row"[^>]*>([^<]*)<\/th>(.*?)<\/tr>/g)) out[m[1]] = m[2];
  return out;
}

test("the held grids are ISO-NE, MISO and NYISO on the day (clean_energy_summary, iso_hub_prices_history)", () => {
  for (const g of GRIDS) {
    assert.equal(licenseHeldRow("clean_energy_summary", `iso:${g}`), HELD.includes(g), g);
    assert.equal(licenseHeldRow(H.HUB_PRICE_TABLE, `iso:${g}`), HELD.includes(g), g);
  }
});

test("the Clean tab's seven grids: a held grid's six cells read license needed, none of its figures is drawn", () => {
  for (const inView of GRIDS) {
    const html = renderToStaticMarkup(createElement(V.CleanView, { c: choiceOf({ view: "clean", grids: inView }) }));
    const rows = rowsOf(html, "The seven grids");
    assert.deepEqual(Object.keys(rows).sort(), GRIDS.map((g) => NAME[g]).sort(), `${inView}: a row for each of the seven`);
    for (const g of HELD) {
      const r = rows[NAME[g]];
      const cells = [...r.matchAll(/<td[^>]*>(.*?)<\/td>/g)].map((m) => text(m[1]).trim());
      assert.deepEqual(cells, Array(6).fill(LICENSE_NEEDED), `${inView}: ${g}'s cells`);
      assert.ok(!/data-check=/.test(r), `${inView}: ${g}: no key`);
      assert.ok(!/\d/.test(text(r)), `${inView}: ${g}: no figure in the row ("${text(r)}")`);
      assert.ok(/data-missing="1"/.test(r) && r.includes('title="ISO-NE; MISO; NYISO: '), `${inView}: ${g}: the view's placeholder, the publishers on hover`);
    }
  }
});

test("the Clean tab's seven grids: the four other grids' figures are as they were, text and key", () => {
  const html = renderToStaticMarkup(createElement(V.CleanView, { c: choiceOf({ view: "clean", grids: "ercot" }) }));
  const rows = rowsOf(html, "The seven grids");
  const year = clean.defaultYear(read("clean/ercot.json")) ?? clean.yearsOf(read("clean/ercot.json")).at(-1);
  for (const g of GRIDS.filter((x) => !HELD.includes(x))) {
    const r = rows[NAME[g]], f = read(`clean/${g}.json`);
    assert.ok(!r.includes(LICENSE_NEEDED), `${g}: not held`);
    if (!f.years[year]) continue;
    const v = clean.yearView(f, year);
    const key = `fmt|n1|file|clean/${g}.json|years.${year}.carbon_free_share_pct`;
    assert.ok(r.includes(`data-check="${key}"`), `${g}: the share's key`);
    assert.ok(text(r).includes(`${v.months ?? 0} of ${v.due ?? 12}`), `${g}: months held`);
    assert.ok(text(r).includes(`${n1(v.share)}%`), `${g}: the share, ${n1(v.share)}%`);
  }
});

test("the price beside the mix: a held grid's hub price reads license needed; the others' are drawn; MISO keeps paused", () => {
  for (const [view, View] of [["day", V.DayView], ["duck", V.DuckView]]) {
    for (const g of GRIDS) {
      const html = renderToStaticMarkup(createElement(View, { c: choiceOf({ view, grids: g, factor: "price" }) }));
      const factor = [...html.matchAll(/Factor: (<span[^>]*>[^<]*<\/span>)/g)].map((m) => m[1]);
      if (g === "miso") assert.ok(factor.length && factor.every((s) => s.includes("paused while terms are reviewed")), `${view} ${g}: paused`);
      else if (g === "pjm") assert.ok(factor.length && factor.every((s) => s.includes("licensed source needed")), `${view} ${g}: licensed`);
      else if (HELD.includes(g)) assert.ok(factor.length && factor.every((s) => s.includes(`>${LICENSE_NEEDED}<`) && s.includes(`title="ISO-NE; MISO; NYISO: `)), `${view} ${g}: license needed`);
      else assert.ok(!html.includes(LICENSE_NEEDED), `${view} ${g}: drawn, no hold`);
      // the file holds a held grid's prices: the hold is the page's, not the file's
      if (HELD.includes(g) && g !== "miso") assert.ok(Object.keys(read(`mixplus/${g}.json`).factors.price_da.months).length > 0, `${g}: the file holds prices`);
    }
  }
});

test("lib/gridHeld.ts: the network's hub prices by code, on fixed days", () => {
  for (const [ba, g] of Object.entries(H.BA_GRID)) {
    assert.equal(H.heldHubPrice(ba, BEFORE), null, `${ba} before the hold`);
    const h = H.heldHubPrice(ba, AFTER);
    if (HELD.includes(g)) assert.deepEqual(h && h.words, LICENSE_NEEDED, ba);
    else assert.equal(h, null, ba);
  }
  assert.equal(H.heldHubPrice("AECI", AFTER), null);
  assert.ok(H.heldHubPrice("ISNE", AFTER).why.startsWith("ISO-NE; MISO; NYISO: "));
  // the replay's files hold the held grids' prices (so the page must leave them out)
  const y25 = JSON.parse(fs.readFileSync(path.join(here, "..", "public", "network", "daily_2025.json"), "utf-8"));
  for (const ba of ["ISNE", "NYIS"]) assert.ok(y25.hub_prices[ba].some((v) => v !== null), `${ba} in the 2025 file`);
});

test("lib/gridHeld.ts: the queue's positions of energy_projects, ISO-NE's left out, on fixed days", () => {
  const rows = [{ entity_id: "isone_queue:137" }, { entity_id: "isone_queue:358:2" }, { entity_id: "ercot_queue:24INR0001" }, { entity_id: "nyiso_queue:1630" }, { entity_id: "spp_queue:GEN-1" }];
  assert.deepEqual(H.shownQueue(rows, BEFORE).map((r) => r.entity_id), rows.map((r) => r.entity_id));
  assert.deepEqual(H.shownQueue(rows, AFTER).map((r) => r.entity_id), ["ercot_queue:24INR0001", "nyiso_queue:1630", "spp_queue:GEN-1"]);
  assert.equal(H.heldQueue("isone_interconnection_queue", AFTER)?.words, LICENSE_NEEDED);
  assert.equal(H.heldQueue("isone_interconnection_queue", BEFORE), null);
  for (const t of ["ercot_interconnection_queue", "caiso_interconnection_queue", "nyiso_interconnection_queue", "miso_interconnection_queue", "spp_interconnection_queue", null])
    assert.equal(H.heldQueue(t, AFTER), null, String(t));
  // session 1415 (chain 107), part 4 of the header, in this test so that the count tests/test_session1167.py reads stands:
  // the Clean tab's carbon blocks: no ISO held today; a held ISO is set apart, never ranked, none of its rows returned
  const ENT = Object.keys(H.BA_GRID).map((ba) => `eia930:${ba}`);
  for (const e of ENT) for (const t of [H.CARBON_HOURLY_TABLE, H.CARBON_MONTHLY_TABLE]) for (const d of [BEFORE, AFTER]) assert.equal(H.heldCarbonRow(t, e, d), null, `${t} ${e}`);
  assert.equal(H.CARBON_MONTHLY_TABLE, "carbon_intensity_monthly");
  // the rule is licenseHeldRow's, by entity: on a table held by grid (clean_energy_summary after the hold) a held grid's
  // entity reads license needed with the publishers on hover, another grid's is not held
  assert.equal(H.heldCarbonRow("clean_energy_summary", "iso:isone", AFTER)?.words, LICENSE_NEEDED);
  assert.ok(H.heldCarbonRow("clean_energy_summary", "iso:isone", AFTER).why.startsWith("ISO-NE; MISO; NYISO: "));
  assert.equal(H.heldCarbonRow("clean_energy_summary", "iso:ercot", AFTER), null);
  assert.equal(H.heldCarbonRow("clean_energy_summary", "iso:isone", BEFORE), null);
  // the ranking on real hours, with and without ISO-NE held
  const fx = (f) => JSON.parse(fs.readFileSync(path.join(here, "fixtures", f), "utf-8"));
  const hours = fx("grid_failed_reads.json").rows.carbon_intensity_hourly.map(([entity, variable, ts_utc, value]) => ({ entity, variable, ts_utc, value }));
  const all = K.carbonRanked(hours, ENT), held = K.carbonRanked(hours, ENT, (e) => e === "eia930:ISNE");
  assert.equal(all.ranked.length, 7);
  assert.deepEqual(all.held, []);
  for (let i = 1; i < 7; i++) assert.ok(all.ranked[i - 1].g.value <= all.ranked[i].g.value, "lowest first");
  for (const x of all.ranked) assert.equal(x.d?.ts_utc, x.g.ts_utc, `${x.entity}: demand of the same hour`);
  assert.deepEqual(held.held, ["eia930:ISNE"]);
  assert.deepEqual(held.ranked.map((x) => x.entity), all.ranked.map((x) => x.entity).filter((e) => e !== "eia930:ISNE"));
  // the months on real rows, ISO-NE held: no row of it, the others' first and latest as without the hold
  const months = fx("carbon_monthly.json").rows.map(([entity, ts_utc, value]) => ({ entity, variable: "intensity_generation", ts_utc, value }));
  const open = K.carbonMonthEnds(months, ENT, () => true), shut = K.carbonMonthEnds(months, ENT, () => true, (e) => e === "eia930:ISNE");
  for (const [i, e] of ENT.entries()) {
    if (e === "eia930:ISNE") { assert.ok(shut[i].held && !shut[i].rows.length && !shut[i].first, e); continue; }
    assert.deepEqual([shut[i].first, shut[i].last], [open[i].first, open[i].last], e);
    assert.ok(open[i].first.ts_utc.startsWith("2018-"), `${e}: the first month in 2018`);
  }
  assert.match(K.carbonTip(H.CARBON_MONTHLY_TABLE, open[0].first, "the first complete month"), /^carbon_intensity_monthly, entity eia930:\w+, intensity_generation, the first complete month: month 2018-\d\d \(UTC\)$/);
});
