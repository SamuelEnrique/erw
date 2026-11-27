// Energy Research Warehouse (ERW): /impact's datacenter, window F's findings I4 and I5 (session 10821, chain 740).
// Run: cd site; node --import ./scripts/tsx-register.mjs --test scripts/test-datacenter-ui.test.mjs
// I4: a document's figure the pick does not take is said, with the row's note. I5: an address naming a project without
// its figures takes the project's figures, as a pick in the left box does; a figure the address gives is kept.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const A = JSON.parse(fs.readFileSync(new URL("../data/forecast/datacenter_announced.json", import.meta.url), "utf8"));
const D = JSON.parse(fs.readFileSync(new URL("../data/forecast/deflator.json", import.meta.url), "utf8"));
const M = await import("../lib/dcui.ts");
const U = await import("../lib/forecastui.ts");
const list = M.dcProjects(A.rows, D.index);
const ids = list.map((p) => p.id);

test("I4: Paducah's investment and Starwood's jobs are said not taken, with the rows' notes", () => {
  const pad = list.find((p) => p.id === "ky_paducah_2026");
  assert.equal(pad.invest, null);
  assert.match(pad.skipped, /investment is not taken/);
  assert.match(pad.skipped, /energy infrastructure/);
  const sw = list.find((p) => p.id === "wv_starwood_mason_2026");
  assert.equal(sw.perm, null);
  assert.match(sw.skipped, /jobs figure is not taken/);
  const meta = list.find((p) => p.id === "la_meta_richland_2026");
  assert.equal(meta.skipped, null);
});

test("I5: the project alone in the address sets its figures; a figure the address gives is kept", () => {
  const q = { tech: "datacenter", state: "la", dcproj: "la_meta_richland_2026" };
  const s = U.withProjects(U.parse(q), q, [], ids, list);
  assert.deepEqual([s.a.dmw, s.a.invest, s.a.perm, s.a.cons], [5000, 50000, 1000, 7500]);
  const q2 = { ...q, dmw: "800" };
  const s2 = U.withProjects(U.parse(q2), q2, [], ids, list);
  assert.equal(s2.a.dmw, 800);
  assert.equal(s2.a.invest, 50000);
  assert.ok(Number.isNaN(s2.b.dmw));  // B names no project
  const q3 = { tech: "datacenter", state: "va", bdcproj: "va_cleanarc_caroline_2025" };
  const s3 = U.withProjects(U.parse(q3), q3, [], ids, list);
  const cl = list.find((p) => p.id === "va_cleanarc_caroline_2025");
  assert.equal(s3.b.dmw, cl.mw);
  assert.ok(Number.isNaN(s3.a.dmw));
});

test("I6: the page says its defaults are medians of the projects read, with each count and the date", () => {
  for (const k of ["mw_stated", "investment_per_mw", "permanent_jobs_per_mw", "construction_jobs_per_billion"]) {
    assert.ok(Number.isInteger(A.defaults[k].n) && A.defaults[k].n > 0, k);
  }
  assert.match(A.computed, /^\d{4}-\d{2}-\d{2}$/);
  const src = fs.readFileSync(new URL("../app/impact/Datacenter.tsx", import.meta.url), "utf8");
  const note = src.slice(src.indexOf('data-defaults-note="dc"'), src.indexOf("They move when another project is read."));
  assert.ok(note.length > 0);
  for (const k of ["mw_stated", "investment_per_mw", "permanent_jobs_per_mw", "construction_jobs_per_billion"]) {
    assert.ok(note.includes(`P2.announced.defaults.${k}.n`), k);
  }
  assert.ok(note.includes("dcList.length") && note.includes("P2.announced.computed"));
  // session 10822: the campuses to date are counted and said to enter no median; the picker's rows carry the flag
  assert.ok(note.includes("p.toDate") && note.includes("which enter no median"));
  const td = list.filter((p) => p.toDate).map((p) => p.id);
  assert.equal(td.length, A.rows.filter((r) => r.to_date).length);
  assert.ok(td.includes("or_meta_prineville_2026") && !td.includes("tx_meta_elpaso_2026"));
});
