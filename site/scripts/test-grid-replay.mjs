// Energy Research Warehouse (ERW) site, session 1170 (chain 078): a replayed day's figures on the Grid tool (the Grid
// pack's blind spot 11), on the replay's committed daily file, recomputed as scripts/check-values.mjs recomputes them.
// Needs no build, no server and no database: the file is the figure's source (eia930_daily_demand and
// eia930_daily_interchange are not in the live set).
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-replay.mjs
//
// 1. lib/gridReplay.ts on a real day, 2021-02-15 (the Uri storm): BPAT, outside the seven ISO grids, and ERCO; each key
//    is the one the page writes, its value the file's.
// 2. Every key it writes, for every balancing authority of the file that day, recomputed: file| through
//    scripts/check-file.mjs (the "@<day>" segment), netday| through netdayValue, each text in its form
//    (scripts/check-format.mjs); and the net against a sum of the links written out here, not through the library.
// 3. Not held: a balancing authority the file holds no demand for, a day its demand is blank, a day not in the file.
// 4. The components drawn on the server (components/grid/ReplayDay.tsx): every key in the markup recomputes to the
//    page's raw value and text; "not held" in the tool's one look where the file holds none.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import * as FMT from "./check-format.mjs";
import * as FILE from "./check-file.mjs";
import * as R from "../lib/gridReplay.ts";
import { ReplayDayDemand, ReplayDayFigures } from "../components/grid/ReplayDay.tsx";

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const read = (f) => JSON.parse(fs.readFileSync(FILE.fileOnDisk(SITE, f), "utf-8"));
const DAY = "2021-02-15";
const Y21 = read("public/network/daily_2021.json");
const at = (y, day) => y.days.indexOf(day);

/** check-values' recomputation of a key on the committed files (scripts/check-values.mjs: fmt, file, netday). */
function truth(check) {
  const f = FMT.fmtParts(check);
  const inner = f ? f.inner : check;
  let v;
  const fk = FILE.fileParts(inner);
  if (fk) v = FILE.readPath(read(fk.file), fk.path);
  else if (inner.startsWith("netday|")) v = R.netdayValue(inner, read(R.replayFileOf(inner.split("|")[3])));
  else throw new Error(`not a key of the replay: ${check}`);
  return { v, form: f ? f.form : null };
}

test("1. BPAT and ERCO on 2021-02-15: the keys and the file's values", () => {
  const i = at(Y21, DAY);
  assert.ok(i >= 0);
  const b = R.replayDay(Y21, "BPAT", DAY);
  assert.equal(b.file, "public/network/daily_2021.json");
  assert.equal(b.inFile, true);
  assert.equal(b.demand.check, "fmt|n0|file|public/network/daily_2021.json|demand.BPAT.@2021-02-15");
  assert.equal(b.demand.raw, Y21.demand.BPAT[i]);
  assert.equal(b.demand.raw, 7929.6);
  assert.equal(b.demand.text, "7,930");
  assert.equal(b.demandWhy, null);
  // BPAT's ties that day, written out from the file: positive when the first code exported to the second
  const bt = Y21.links.filter((l) => (l.a === "BPAT" || l.b === "BPAT") && l.mw[i] !== null);
  assert.equal(b.ties.raw, bt.length);
  assert.equal(b.ties.check, "netday|ties|BPAT|2021-02-15");
  assert.equal(b.net.kind, "export");
  assert.equal(b.net.check, "fmt|n0|netday|export|BPAT|2021-02-15");
  const e = R.replayDay(Y21, "ERCO", DAY);
  assert.equal(e.demand.raw, 50151.8);
  assert.equal(e.demand.text, "50,152");
  // ERCO: CEN to ERCO 107.1 (CEN exported), ERCO to SWPP -779.2 (ERCO took 779.2): a net import of 886.3 MW over 2 ties
  assert.equal(e.ties.raw, 2);
  assert.equal(e.net.kind, "import");
  assert.equal(e.net.check, "fmt|n0|netday|import|ERCO|2021-02-15");
  assert.equal(e.net.raw, 886.3);
  assert.equal(e.net.text, "886");
  assert.equal(e.withDemand, 52);
  for (const f of [b.demand, b.net, b.ties, e.demand, e.net, e.ties]) assert.ok(f.tip.includes(DAY) && f.tip.includes("site/public/network/daily_2021.json"), f.tip);
});

test("2. every key of every balancing authority that day recomputes from the file", () => {
  const i = at(Y21, DAY);
  const bas = new Set([...Object.keys(Y21.demand), ...Y21.links.flatMap((l) => [l.a, l.b])]);
  let n = 0;
  for (const ba of bas) {
    const r = R.replayDay(Y21, ba, DAY);
    // the net written out here, not through the library
    let sum = 0, ties = 0;
    for (const l of Y21.links) {
      if ((l.a !== ba && l.b !== ba) || l.mw[i] === null || l.mw[i] === undefined) continue;
      sum += l.a === ba ? l.mw[i] : -l.mw[i];
      ties += 1;
    }
    assert.equal(r.ties.raw, ties, ba);
    if (ties) assert.ok(Math.abs((r.net.kind === "export" ? r.net.raw : -r.net.raw) - sum) < 0.051, `${ba}: ${r.net.raw} against ${sum}`);
    else assert.equal(r.net, null, ba);
    for (const f of [r.demand, r.net, r.ties].filter(Boolean)) {
      const t = truth(f.check);
      assert.equal(t.v, f.raw, `${f.check}: file ${t.v}, page ${f.raw}`);
      assert.equal(f.text, t.form ? FMT.formText(t.form, t.v) : String(t.v), `${f.check}: the text`);
      n += 1;
    }
    // the other direction has no value: an export key of a day that imports is not that day's figure
    if (r.net) assert.equal(R.netdayValue(`netday|${r.net.kind === "export" ? "import" : "export"}|${ba}|${DAY}`, Y21), undefined, ba);
  }
  assert.ok(n > 150, `${n} keys`);
  // the file| path and its file, as check-values reads them
  assert.deepEqual(FILE.fileParts("file|public/network/daily_2021.json|demand.BPAT.@2021-02-15"), { file: "public/network/daily_2021.json", path: "demand.BPAT.@2021-02-15" });
  assert.equal(FILE.fileParts("file|public/network/../secret.json|x"), null);
  assert.equal(FILE.fileParts("file|public/network/daily_21.json|x"), null);
  assert.equal(FILE.fileParts("file|public/network/story_uri_2021.json|x"), null);
  assert.equal(FILE.tableRow("public/network/daily_2021.json", "demand.BPAT.@2021-02-15", Y21), null);
  assert.equal(FILE.readPath(Y21, "demand.BPAT.@2021-13-01"), undefined);
  assert.equal(FILE.readPath(Y21, "demand.NOBA.@2021-02-15"), undefined);
  // a file of site/data/ is read where it was (session 1166)
  assert.ok(FILE.fileOnDisk(SITE, "stress/ercot.json").endsWith("/data/stress/ercot.json"));
});

test("3. not held: no demand for the balancing authority, a blank day, a day not in the file", () => {
  // CEN (Mexico's CENACE) has ties and no demand in the file
  const c = R.replayDay(Y21, "CEN", DAY);
  assert.equal(c.demand, null);
  assert.match(c.demandWhy, /holds a daily demand for 52 balancing authorities, and none for CEN/);
  assert.ok(c.net && c.ties.raw >= 1);
  // LGEE's demand of 2021-03-04 is blank in the file (session 109's band, or not reported)
  assert.equal(Y21.demand.LGEE[at(Y21, "2021-03-04")], null);
  const l = R.replayDay(Y21, "LGEE", "2021-03-04");
  assert.equal(l.demand, null);
  assert.match(l.demandWhy, /holds no demand for LGEE on 2021-03-04/);
  assert.equal(truth("fmt|n0|file|public/network/daily_2021.json|demand.LGEE.@2021-03-04").v, null);
  // a day of another year is not in this file
  const o = R.replayDay(Y21, "BPAT", "2022-01-01");
  assert.equal(o.inFile, false);
  assert.equal(o.demand, null);
  assert.equal(o.net, null);
  assert.equal(o.ties.raw, 0);
  assert.equal(R.netdayValue("netday|ties|BPAT|2022-01-01", Y21), undefined);
  assert.equal(R.replayFileOf("2022-01-01"), "public/network/daily_2022.json");
});

// ---- 4. the components, drawn

const KEY = /<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g;
const decode = (s) => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#x27;/g, "'");
const html = (el) => renderToStaticMarkup(el);
const keysOf = (h) => [...h.matchAll(KEY)].map((m) => ({ check: decode(m[1]), raw: decode(m[2]), text: decode(m[3].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).trim() }));
const ask = (day, asked = day) => ({ day, asked, first: "2019-01-01", last: "2026-10-21", read: { ok: true, y: read(R.replayFileOf(day)) } });

test("4. the Network tab's day and the Gravity tab's line, drawn: every key recomputes", () => {
  for (const [ba, name, want] of [["BPAT", "Bonneville Power Administration", 3], ["ERCO", "ERCOT", 3], ["CEN", "CENACE", 2]]) {
    const h = html(createElement(ReplayDayFigures, { ask: ask(DAY), ba, name }));
    assert.ok(h.includes(`data-grid-replay-day="${ba}"`) && h.includes(`data-replay-day="${DAY}"`), ba);
    const ks = keysOf(h);
    assert.equal(ks.length, want, `${ba}: ${ks.length} keys`);
    for (const k of ks) {
      const t = truth(k.check);
      assert.equal(String(t.v), k.raw, k.check);
      assert.equal(k.text, t.form ? FMT.formText(t.form, t.v) : String(t.v), k.check);
    }
    if (ba === "CEN") assert.ok(h.includes('data-missing="1"') && h.includes(">not held</span>"), "CEN: not held, the tool's one look");
  }
  // the Gravity tab's one line: ERCOT's demand that day, and the shape's live hour said
  const g = html(createElement(ReplayDayDemand, { ask: ask(DAY), ba: "ERCO", label: "ERCOT" }));
  assert.ok(g.includes(`data-gravity-day="${DAY}"`));
  assert.ok(g.includes("still draws the live hour") && g.includes("ruling 1a"));
  const gk = keysOf(g);
  assert.deepEqual(gk.map((k) => k.check), ["fmt|n0|file|public/network/daily_2021.json|demand.ERCO.@2021-02-15"]);
  assert.equal(gk[0].text, "50,152");
  // the Lower 48: no demand in the files, said, no key
  const u = html(createElement(ReplayDayDemand, { ask: ask(DAY), ba: "US48", label: "US48" }));
  assert.equal(keysOf(u).length, 0);
  assert.ok(u.includes(">not held</span>"));
  // a day held to the replay's last day is said
  const m = html(createElement(ReplayDayFigures, { ask: ask("2026-10-21", "2027-01-01"), ba: "BPAT", name: "BPAT" }));
  assert.ok(m.includes("The address asks for 2027-01-01") && m.includes("so it opens on 2026-10-21"));
  // a file that could not be read is said, no figure drawn
  const bad = html(createElement(ReplayDayFigures, { ask: { ...ask(DAY), read: { ok: false, why: "the replay's file of 2021 could not be read on the server (ENOENT)" } }, ba: "BPAT", name: "BPAT" }));
  assert.equal(keysOf(bad).length, 0);
  assert.ok(bad.includes("could not be read on the server"));
});
