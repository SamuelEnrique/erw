// Energy Research Warehouse (ERW) site, session 1413 (chain 107): check-values' filecalc|<function>|<data file>|<args>
// keys, a figure the energy mix views compute from a committed file's arrays (the duck curve year after year, the peak
// hours of the average day, the history by state, the availability means). The recomputation reads the file in the
// repository (site/data/, as a file| key reads it) and applies the page's own function to it: lib/mix2.ts (acrossYears,
// periodOf, highest: the functions the views already called) and lib/mixViewCalc.ts (the arithmetic that stood inline in
// components/mix/views.tsx, moved there as it stood). Its words are lib/mixViewCalc.ts's header, each function's line.
// None of these files is a build of a row the live set holds as such (a computed figure is not a column of
// generation_mix_hourly_profile), so the figure is checked against the file alone, and the line says so. Node tests:
// scripts/test-mix-view-calc.mjs (each function against the arithmetic that stood in the view, a right and a wrong key)
// and scripts/test-grid-file-keys.mjs (every key the views write, recomputed). No static import: the two libraries are
// TypeScript, imported when a key needs them (node strips their types), as check-values imports lib/ercotNotices.ts.
// Session 1414 (chain 107): and the Clean tab's cleanest hours by month, the shares in the cleanest and the dirtiest
// hour of a month's average day (clean_day_max, clean_day_min on clean/<grid>.json, lib/mixViewCalc.ts cleanDayMax and
// cleanDayMin): the file is a build of clean_energy_summary, but the highest and lowest of the 24 hours is no row of it,
// so these too are checked against the file alone.

const MIX = /^mix\/[a-z]+\.json$/, PLUS = /^mixplus\/[a-z]+\.json$/, HISTORY = /^mix_history\.json$/;
const CLEAN = /^clean\/[a-z]+\.json$/, MONTH = /^\d{4}-(0[1-9]|1[0-2])$/;   // session 1414: the clean files, a month of a year
const CAL = /^(0[1-9]|1[0-2])$/, YEAR = /^\d{4}$/, PERIOD = /^\d{4}(-(0[1-9]|1[0-2]))?$/, NAME = /^[a-z_]+$/, STATE = /^[A-Z]{2}$/;
const SEASONS = new Set(["winter", "spring", "summer", "autumn", "all"]);

/** Each function: the files it reads and its arguments' shapes (lib/mixViewCalc.ts FILECALC names the same ones). */
export const SPEC = {
  duck_solar_peak: { file: MIX, args: [CAL, YEAR] },
  duck_low: { file: MIX, args: [CAL, YEAR] },
  duck_evening: { file: MIX, args: [CAL, YEAR] },
  duck_ramp: { file: MIX, args: [CAL, YEAR] },
  day_peak: { file: MIX, args: [PERIOD, /^(solar|wind)$/] },
  hist_share: { file: HISTORY, args: [STATE, YEAR, NAME] },
  hist_mwh: { file: HISTORY, args: [STATE, YEAR, NAME] },
  avail_mean: { file: PLUS, args: [YEAR, { test: (x) => SEASONS.has(x) }, NAME] },
  avail_min: { file: PLUS, args: [YEAR, { test: (x) => SEASONS.has(x) }, NAME] },
  avail_max: { file: PLUS, args: [YEAR, { test: (x) => SEASONS.has(x) }, NAME] },
  clean_day_max: { file: CLEAN, args: [MONTH] },   // session 1414: the cleanest hours by month, on the Clean tab
  clean_day_min: { file: CLEAN, args: [MONTH] },
};

/** The function, file and arguments of a filecalc| key, or null for another key or one whose parts do not fit. */
export function filecalcParts(check) {
  const p = String(check).split("|");
  if (p[0] !== "filecalc" || p.length < 3) return null;
  const [, fn, file, ...args] = p;
  const s = Object.prototype.hasOwnProperty.call(SPEC, fn) ? SPEC[fn] : null;
  if (!s || !s.file.test(file) || args.length !== s.args.length || !args.every((a, i) => s.args[i].test(a))) return null;
  return { fn, file, args };
}

let libs = null;
async function load() {
  if (!libs) libs = Promise.all([import("../lib/mix2.ts"), import("../lib/mixViewCalc.ts")]).then(([mix, calc]) => ({ mix, calc }));
  return libs;
}

/** The value of a filecalc| key on the parsed file (json), by the page's own function; undefined when the file holds no
 *  such figure (the page draws its placeholder there and writes no key). */
export async function filecalcValue(parts, json) {
  return filecalcValueWith(await load(), parts, json);
}

/** As filecalcValue, with the two libraries given ({ mix: lib/mix2.ts, calc: lib/mixViewCalc.ts }), for a caller that
 *  has imported them already (the node tests). */
export function filecalcValueWith({ mix, calc }, parts, json) {
  const { fn, args } = parts;
  let v;
  if (fn.startsWith("duck_")) {
    const [cal, year] = args;
    const y = mix.acrossYears(json, cal).find((q) => q.year === year);
    v = !y ? undefined : fn === "duck_solar_peak" ? y.solarPeak?.value : fn === "duck_low" ? y.low?.value : fn === "duck_evening" ? y.evening?.value : y.ramp;
  } else if (fn === "day_peak") {
    const [period, source] = args;
    v = mix.highest(mix.periodOf(json, period)?.avg[source] ?? [])?.value;
  } else if (fn === "hist_share" || fn === "hist_mwh") {
    const [state, year, fuel] = args;
    const c = calc.historyCell(json, state, year, fuel);
    v = fn === "hist_share" ? c.share : c.mwh;
  } else if (fn === "clean_day_max" || fn === "clean_day_min") {
    v = fn === "clean_day_max" ? calc.cleanDayMax(json, args[0]) : calc.cleanDayMin(json, args[0]);   // session 1414
  } else {
    const [year, season, fuel] = args;
    const hours = calc.availOf(json, year, season, fuel);
    v = fn === "avail_mean" ? calc.availMean(hours) : fn === "avail_min" ? calc.availMin(hours) : calc.availMax(hours);
  }
  return typeof v === "number" && Number.isFinite(v) ? v : undefined;
}
