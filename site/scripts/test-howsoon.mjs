// Energy Research Warehouse (ERW) site, session 163: the pure functions of "How long a large load waits" (/cost-of-power,
// the section "How soon"; lib/howsoon.ts). No request, no browser, no model.
//
//   node scripts/test-howsoon.mjs
//
// THE FIGURES BELOW ARE MADE UP FOR THIS TEST: no entity, count, duration, document or date in the made-up file is real,
// and none of it is in any file the site ships (the page reads data/datacenter/how_soon.json and nothing else).
//
//   1. the grid an address names: PJM and MISO too; anything else is the grid the page opened;
//   2. the block: MISO is paused whatever the file holds; no file is "not held"; a grid the file does not name is "not
//      measured yet"; a grid is measured only where the file says so and holds a stage and its copies;
//   3. the words of a figure: a median on its two bounds, a small group as its count and two bounds, one request as "too
//      few to show", none as "none yet"; the requests still waiting always as "at least", and their hover says lower bound;
//   4. the hovers name the count, the copies and their days; a stated figure's hover names who, what it covers, the
//      document, its day and page, what differs, and never holds a sentence field;
//   5. the summary sentence: for a measured grid it names the place, the count, the measured figure and the stated one;
//      for a grid not measured it says so, with the entities' own measured figures; for MISO the pause; every number in
//      it is a number of the file, for every grid;
//   6. where data/datacenter/how_soon.json is on the machine: the same on the real file, and each grid's sentence printed.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const H = await import("../lib/howsoon.ts");

let failed = 0, n = 0;
const ok = (cond, what) => { n += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed += 1; };

// MADE UP: a stated figure and a stage of the file's shape, for the tests only
const stated = (more = {}) => ({ stated_by: "Made-up Operator", figure: "eleven fortnights", basis: "expected", statistic: "", covers: "made-up study", document: "Made-up bulletin 7",
  document_type: "operator report", date: "2031-02-03", date_basis: "document", page: "4", url: "https://example.invalid/bulletin7.pdf", mark: "", note: "Not the same start: made up.", ...more });
const stage = (interval, measured, waiting, more = {}) => ({ interval, label: `Made-up stage ${interval}`, phrase: `through the made-up stage ${interval}`, requests: measured.n + waiting.n, measured,
  waiting: { lower_bound: true, ...waiting }, two_copies_only: { n: 0, lower_bound: true }, ended_before_first_copy: { n: 0 }, stated: [], ...more });
const FILE = {
  built_at_utc: "2031-03-04T05:06:07Z", unit: "days", rule: { min_for_median: 5, min_for_bounds: 2, too_few: "too few to show" }, paused: ["miso"],
  grids: {
    nyiso: { state: "measured", entity: "Made-up Operator", place: "Made-up Place",
      copies: { n: 41, first: "2030-01-02", last: "2031-01-02", requests_seen: 19, requests_followed: 17, what: "a made-up workbook", read_from: "a made-up archive" },
      stages: [
        stage("alpha", { n: 7, form: "median", median_at_least: 211, median_at_most: 322.5, least: 13, most: 977 }, { n: 6, form: "range", least: 31, most: 455 }, { stated: [stated({ mark: "proposed", figure: "88-day" }), stated()] }),
        stage("request to energized", { n: 3, form: "bounds", least: 1501, most: 1777 }, { n: 9, form: "range", least: 61, most: 2222 }),
        stage("gamma", { n: 1, form: "too few", words: "too few to show" }, { n: 1, form: "too few", words: "too few to show" }),
        stage("delta", { n: 0, form: "none" }, { n: 0, form: "none" }),
      ], stated: [] },
    ercot: { state: "not measured here", entity: "Made-up Grid Operator", place: "Made-up State", stages: [],
      reports: { n: 29, first: "2030-05-06", last: "2031-01-09", requests_named: 0, what: "made-up reports", why: "Made-up reason.", read_from: "a made-up archive" },
      stated: [stated({ stated_by: "Made-up Wires Company", basis: "measured", statistic: "average", figure: "603 days" }), stated({ stated_by: "Made-up Wires Company", basis: "measured", statistic: "median", figure: "544 days" }), stated({ figure: "17 weeks" })] },
    // a paused grid the file should never hold: the block must not show it
    miso: { state: "measured", entity: "Made-up Paused Operator", copies: { n: 5, first: "2030-01-01", last: "2030-02-01", requests_seen: 9, requests_followed: 9, what: "x", read_from: "y" },
      stages: [stage("alpha", { n: 9, form: "median", median_at_least: 1, median_at_most: 2, least: 1, most: 2 }, { n: 0, form: "none" })], stated: [] },
  },
};
const file = H.fileOf(FILE);
ok(file !== null && H.fileOf({}) === null && H.fileOf({ grids: {}, rule: {} }) === null && H.fileOf({ built_at_utc: "x", rule: {}, grids: { a: { state: "measured" } } }) === null, "a file of measured waits is read as it is; a thing of another shape is not a file");

// 1
ok(H.waitsGrid("pjm", "ercot") === "pjm" && H.waitsGrid("MISO", "ercot") === "miso" && H.waitsGrid("zz", "caiso") === "caiso" && H.waitsGrid(undefined, "spp") === "spp", "the grid an address names: PJM and MISO too; anything else is the grid the page opened");

// 2
ok(H.blockOf(file, "miso").state === "paused" && H.blockOf(file, "miso").entry === null && H.blockOf(null, "miso").state === "paused", "MISO is paused whatever the file holds, and nothing of the file is handed to the page for it");
ok(H.blockOf(null, "nyiso").state === "not held" && H.blockOf(file, "caiso").state === "not measured yet" && H.blockOf(file, "pjm").state === "not measured yet", 'no file is "not held"; a grid the file does not name is "not measured yet"');
ok(H.blockOf(file, "nyiso").state === "measured" && H.blockOf(file, "ercot").state === "not measured here", "a grid is measured where the file says so; a grid whose reports name no request is not measured here");
ok(H.blockOf({ ...file, grids: { nyiso: { ...FILE.grids.nyiso, stages: [] } } }, "nyiso").state === "not measured yet", "a grid marked measured that holds no stage is not shown as measured");

// 3
const [alpha, service, gamma, delta] = FILE.grids.nyiso.stages, copies = FILE.grids.nyiso.copies;
ok(H.measuredWords(alpha) === "median at least 211, at most 322.5 days" && H.measuredWords(service) === "between 1,501 and 1,777 days", "a median is written on its two bounds, never as one figure; a small group as its two bounds");
ok(H.measuredWords(gamma) === "too few to show" && H.measuredWords(delta) === "none yet" && H.waitingWords(gamma) === "too few to show" && H.waitingWords(delta) === "none", 'one request is "too few to show", none is "none yet"');
ok(H.waitingWords(alpha) === "at least 31 to 455 days so far" && /lower bound/.test(H.waitingTip(alpha, copies, file)) && /never averaged/.test(H.waitingTip(alpha, copies, file)) && H.LOWER === "lower bound", 'the requests still waiting read "at least", and their hover says a lower bound, never averaged');
ok(!/\b(322|323|266|267)\b(?!\.5)/.test(H.measuredWords(alpha).replace("322.5", "")) && !H.measuredWords(alpha).includes(String((211 + 322.5) / 2)), "no midpoint of the two bounds is written, and a half day is not rounded");

// 4
const mt = H.measuredTip(alpha, copies, file), bt = H.measuredTip(service, copies, file);
ok(mt.includes("7 requests of the 13 followed") && mt.includes("13 to 977 days") && mt.includes("41 dated copies of a made-up workbook, 2 January 2030 to 2 January 2031") && mt.includes("19 load requests seen, 17 followed") && mt.includes("never a midpoint"),
  "a measured figure's hover names the count behind it, the range, the copies read and their days");
ok(bt.includes("Fewer than 5, so no median") && bt.includes("1,501") && bt.includes("1,777"), "a small group's hover says why no median is given");
const st = H.statedTip(stated()), own = H.statedTip(FILE.grids.ercot.stated[0]);
ok(st.includes("eleven fortnights: expected by Made-up Operator") && st.includes("Covers: made-up study") && st.includes("Made-up bulletin 7, 3 February 2031, page 4") && st.includes("Not the same start"), "a stated figure's hover names who stated it, what it covers, the document, its day and page, and what differs");
ok(own.includes("measured by Made-up Wires Company itself, average") && own.includes("not one made here"), "an entity's own measurement is labeled its own, and not one made here");
ok(H.statedOf(FILE.grids.nyiso).length === 2 && H.statedOf(FILE.grids.ercot).length === 3 && H.statedOf(null).length === 0, "every stated figure of a grid: those beside a stage, then the rest");
ok(/29 made-up reports of Made-up Grid Operator were read \(6 May 2030 to 9 January 2031\); 0 name a request\. Made-up reason\./.test(H.notHereWhy(FILE.grids.ercot)), "why a grid is not measured here: the reports read, their days, and how many name a request");

// 5
const numbersOf = (s) => (s.match(/\d[\d,]*(?:\.\d+)?/g) ?? []).map((x) => Number(x.replace(/,/g, "")));
const fileNumbers = (v, out = new Set()) => {
  if (typeof v === "number") out.add(v);
  else if (typeof v === "string") for (const x of numbersOf(v)) out.add(x);
  else if (Array.isArray(v)) v.forEach((x) => fileNumbers(x, out));
  else if (v && typeof v === "object") Object.values(v).forEach((x) => fileNumbers(x, out));
  return out;
};
const sentenceHolds = (f, names) => H.WAIT_GRIDS.every((g) => { const all = fileNumbers(f.grids[g] ?? {}); return numbersOf(H.sentenceOf(f, g, names[g] ?? g.toUpperCase())).every((x) => all.has(x)); });
const ny = H.sentenceOf(file, "nyiso", "NYISO"), tx = H.sentenceOf(file, "ercot", "ERCOT");
ok(ny === "Made-up Place: 3 requests followed through the made-up stage request to energized took between 1,501 and 1,777 days, and 9 more are still waiting, at least 61 to 2,222 days so far (a lower bound); 7 requests followed through the made-up stage alpha took a median of at least 211 and at most 322.5 days, where Made-up Operator itself states eleven fortnights.",
  `a measured grid's sentence names the place, each count, the measured figures, the lower bound and the stated figure ("${ny}")`);
ok(tx === "Made-up State: no wait is measured here (0 requests named in 29 of Made-up Grid Operator's reports); measured by the entities themselves: Made-up Wires Company 603 days (average) and 544 days (median).",
  `a grid not measured says so, with the entities' own measured figures ("${tx}")`);
ok(H.sentenceOf(file, "caiso", "CAISO") === "CAISO: not measured yet." && H.sentenceOf(file, "miso", "MISO") === "MISO: paused while terms are reviewed." && H.sentenceOf(null, "nyiso", "NYISO") === "NYISO: not held yet.", "another grid reads not measured yet, MISO the pause, and no file not held yet");
ok(sentenceHolds(file, {}), "every number of every grid's sentence is a number of the file's entry for that grid");
{
  const few = { ...FILE, grids: { nyiso: { ...FILE.grids.nyiso, stages: [gamma, delta] } } };
  ok(H.sentenceOf(few, "nyiso", "NYISO") === "Made-up Place: 17 requests are followed here and no stage is measured yet.", "a grid whose stages hold too few requests says that no stage is measured yet, and gives no duration");
}

// 6
{
  const at = path.join(here, "..", "data", "datacenter", "how_soon.json");
  if (!fs.existsSync(at)) console.log("note: data/datacenter/how_soon.json is not on this machine; the real file was not read");
  else {
    const real = H.fileOf(JSON.parse(fs.readFileSync(at, "utf-8")));
    ok(real !== null, "the real file is a file of measured waits");
    if (real) {
      const index = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "datacenter", "index.json"), "utf-8"));
      const names = { ...Object.fromEntries(Object.entries(index.blank).map(([id, v]) => [id, v.name])), ...Object.fromEntries(Object.entries(index.grids).map(([id, v]) => [id, v.name])) };
      ok(sentenceHolds(real, names), "the real file: every number of every grid's sentence is a number of the file's entry for that grid");
      ok(H.blockOf(real, "miso").state === "paused" && !("miso" in real.grids), "the real file holds nothing for MISO");
      ok(H.WAIT_GRIDS.every((g) => { const b = H.blockOf(real, g); return b.state !== "measured" || b.entry.stages.every((s) => s.waiting.lower_bound === true && s.requests === s.measured.n + s.waiting.n + s.two_copies_only.n + s.ended_before_first_copy.n); }),
        "the real file: in every measured stage the requests still waiting are marked a lower bound, and the counts add up to the requests");
      for (const g of H.WAIT_GRIDS) console.log(`     ${g}: ${H.blockOf(real, g).state}. ${H.sentenceOf(real, g, names[g] ?? g.toUpperCase())}`);
    }
  }
}

console.log(failed ? `${failed} of ${n} failed` : `all ${n} passed`);
// the exit code is set and Node ends by itself: process.exit() here has ended with a libuv assertion on Windows (exit 127)
process.exitCode = failed ? 1 : 0;
