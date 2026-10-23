// Energy Research Warehouse (ERW) site, session 1166 (chain 078): check-values' file|<data file>|<path> keys, a figure
// the page reads from a committed file of site/data/ (lib/mixdata.ts: the energy mix views and "How clean, and when").
// The recomputation reads the file in the repository, not the database, and follows the path; the page reads the same
// file through its own library (lib/clean.ts, lib/stress.ts, lib/mix2.ts), so the key holds the page's reading of it.
// Where the file is a build of a live-set table, tableRow() names the row of that table the value was built from, and
// check-values compares the two on a line of its own (sameWithin: within the rounding of the less precise of the two).
// A node test holds this file on the committed files (scripts/test-grid-file-keys.mjs). No import: node runs it as it is.
//
// The path: segments joined by ".", each an object's key ("years", "2025", "carbon_free_share_pct"), or an array's
// element chosen by its fields, "records[variable=solar_share_max_pct,period=all]" (the first element whose fields
// all equal those, as lib/mix2.ts recordOf finds it). No key of these files holds a ".", "[" or "|".
//
// The files that are builds of a live-set table (warehouse/derived/, docs/methods/):
//   stress/<grid>.json   years.<Y>.<v>      grid_stress_yearly             iso:<grid>  <v>         <Y>-01-01
//   clean/<grid>.json    years.<Y>.<v>      clean_energy_summary (P1Y)     iso:<grid>  year_<v>    <Y>-01-01
//   clean/<grid>.json    months.<M>.<v>     clean_energy_summary (P1M)     iso:<grid>  <v>         <M>-01
//   mix/<grid>.json      months.<M>.<v>     generation_mix_hourly_profile  iso:<grid>  <v>         <M>-01
//   mix/<grid>.json      records[...].value generation_mix_records         iso:<grid>  the record's variable, at its ts_utc
// Not a build of a table, or not of a row the table holds: mix/<grid>.json's years (the builder sums its months; the
// table holds months only), mixplus/, mix_forecast.json and mix_history.json (warehouse/derived/mix_views.py writes
// files only). Their keys are checked against the file alone, and the line says so.

const SEG = /^([^[\]]+)(?:\[([^\]]+)\])?$/;

/** The segments of a path: [{ key, where }] with where the fields an array's element must match, or null. */
export function segments(path) {
  return String(path).split(".").map((s) => {
    const m = SEG.exec(s);
    if (!m) throw new Error(`bad path segment ${s} in ${path}`);
    const where = m[2] ? Object.fromEntries(m[2].split(",").map((kv) => { const i = kv.indexOf("="); return [kv.slice(0, i), kv.slice(i + 1)]; })) : null;
    return { key: m[1], where };
  });
}

/** The value at a path of a parsed file, or undefined. */
export function readPath(json, path) {
  let v = json;
  for (const { key, where } of segments(path)) {
    if (v === null || typeof v !== "object") return undefined;
    v = v[key];
    if (where) {
      if (!Array.isArray(v)) return undefined;
      v = v.find((x) => x && Object.entries(where).every(([k, w]) => String(x[k]) === w));
    }
  }
  return v;
}

/** The data file and path of a file| key, or null for another key. */
export function fileParts(check) {
  const p = String(check).split("|");
  if (p[0] !== "file" || p.length !== 3 || !/^[a-z0-9_]+(\/[a-z0-9_]+)?\.json$/.test(p[1])) return null;
  return { file: p[1], path: p[2] };
}

const day1 = (s) => (s.length === 4 ? `${s}-01-01T00:00:00Z` : `${s}-01T00:00:00Z`);

/** The live-set row a file's value was built from, or null when the file is not a build of one (the header above). */
export function tableRow(file, path, json) {
  const m = /^(stress|clean|mix)\/([a-z]+)\.json$/.exec(file);
  if (!m) return null;
  const [, kind, grid] = m;
  const entity = `iso:${grid}`;
  const s = segments(path);
  if (kind === "mix" && s.length === 2 && s[0].key === "records" && s[0].where && s[1].key === "value") {
    const rec = readPath(json, s[0].key + `[${Object.entries(s[0].where).map(([k, v]) => `${k}=${v}`).join(",")}]`);
    return rec ? { table: "generation_mix_records", entity, variable: rec.variable, ts_utc: rec.ts_utc, freq: null } : null;
  }
  if (s.length !== 3 || s.some((x) => x.where)) return null;
  const [top, period, v] = [s[0].key, s[1].key, s[2].key];
  if (kind === "stress" && top === "years" && /^\d{4}$/.test(period)) return { table: "grid_stress_yearly", entity, variable: v, ts_utc: day1(period), freq: null };
  if (kind === "clean" && top === "years" && /^\d{4}$/.test(period)) return { table: "clean_energy_summary", entity, variable: `year_${v}`, ts_utc: day1(period), freq: "P1Y" };
  if (kind === "clean" && top === "months" && /^\d{4}-\d{2}$/.test(period)) return { table: "clean_energy_summary", entity, variable: v, ts_utc: day1(period), freq: "P1M" };
  if (kind === "mix" && top === "months" && /^\d{4}-\d{2}$/.test(period)) return { table: "generation_mix_hourly_profile", entity, variable: v, ts_utc: day1(period), freq: null };
  return null;
}

/** The decimals a number is written with (up to 9). */
export function decimals(x) {
  const s = String(x);
  if (/e/i.test(s)) return 9;
  const i = s.indexOf(".");
  return i < 0 ? 0 : Math.min(9, s.length - i - 1);
}

/** Whether a file's value and its table's are the same within the rounding of the less precise of the two: half a unit
 *  of its last decimal (the builders round once, as they write; docs/methods/grid_stress.md, generation_mix_hourly.md). */
export function sameWithin(a, b) {
  const x = Number(a), y = Number(b);
  if (!Number.isFinite(x) || !Number.isFinite(y)) return false;
  const d = Math.min(decimals(a), decimals(b));
  return Math.abs(x - y) <= 0.5 * 10 ** -d + 1e-9 * Math.max(1, Math.abs(x));
}
