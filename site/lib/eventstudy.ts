// Session 47: the event study estimator, the TypeScript twin of warehouse/derived/event_study.py (docs/methods/
// event_study.md). The /events pages compute their "What the estimates say" block with it from event_window_daily at
// build time; scripts/check-values.mjs recomputes every number shown with it from Supabase; scripts/test-eventstudy.mjs
// holds it equal to the Python table and to a synthetic panel with a known effect. No imports: Node runs this file as it is.
//
// y_d = a + sum_k b_k 1[d = event day k] + day-of-week effects + year effects (sum to zero over the baseline years; the
// event year takes none) + e_d. A day's effect is its value less the baseline-only fit's counterfactual, with standard
// error sqrt(s2 + x'Vx) (V the HC1 covariance of the baseline fit); the pooled effect is one window indicator, HC1.

export const SPEC = "dow_year_mean_v1";
export const Z = 1.959963984540054;
export const WINDOWS: Record<string, [string, string]> = {
  uri_2021: ["2021-02-07", "2021-02-24"],
  covid_2020: ["2020-03-01", "2020-05-31"],
  caiso_heat_2020: ["2020-08-10", "2020-08-24"],
  elliott_2022: ["2022-12-19", "2022-12-29"],
  ercot_heat_2023: ["2023-08-01", "2023-09-10"],
};

export type Est = { estimate: number; se: number; lo: number; hi: number };
export type DayEst = Est & { day: string; counterfactual: number };
export type Study = { days: DayEst[]; pooled: Est; counterfactualMean: number; n: number; nBase: number };

const dow = (d: string) => (new Date(`${d}T12:00:00Z`).getUTCDay() + 6) % 7; // Monday 0 ... Sunday 6

function design(dates: string[], event: boolean[], yearsBase: number[], pooled: boolean): { X: number[][]; names: string[] } {
  const names = ["intercept", ...(pooled ? ["pooled"] : []), ...[1, 2, 3, 4, 5, 6].map((k) => `dow${k}`),
    ...(yearsBase.length >= 2 ? yearsBase.slice(0, -1).map((y) => `year${y}`) : [])];
  const last = yearsBase.at(-1);
  const X = dates.map((d, i) => {
    const yr = Number(d.slice(0, 4)), w = dow(d);
    const r = [1];
    if (pooled) r.push(event[i] ? 1 : 0);
    for (let k = 1; k <= 6; k++) r.push(w === k ? 1 : 0);
    if (yearsBase.length >= 2) for (const y of yearsBase.slice(0, -1)) r.push(event[i] ? 0 : (yr === y ? 1 : 0) - (yr === last ? 1 : 0));
    return r;
  });
  return { X, names };
}

/** The columns that are not all zero, as Python's drop_empty. */
function dropEmpty(X: number[][], names: string[]): { X: number[][]; names: string[]; keep: number[] } {
  const keep = names.map((_, j) => j).filter((j) => X.some((r) => r[j] !== 0));
  return { X: X.map((r) => keep.map((j) => r[j])), names: keep.map((j) => names[j]), keep };
}

/** The inverse of a symmetric positive definite matrix (Gauss-Jordan with partial pivoting). */
function inv(A: number[][]): number[][] {
  const n = A.length;
  const M = A.map((r, i) => [...r, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    const d = M[c][c];
    if (Math.abs(d) < 1e-12) throw new Error("singular design");
    for (let j = 0; j < 2 * n; j++) M[c][j] /= d;
    for (let r = 0; r < n; r++) {
      if (r === c) continue;
      const f = M[r][c];
      if (f !== 0) for (let j = 0; j < 2 * n; j++) M[r][j] -= f * M[c][j];
    }
  }
  return M.map((r) => r.slice(n));
}

function olsHc1(X: number[][], y: number[]): { b: number[]; V: number[][]; s2: number } {
  const n = X.length, k = X[0].length;
  const xtx = Array.from({ length: k }, (_, i) => Array.from({ length: k }, (_, j) => X.reduce((a, r) => a + r[i] * r[j], 0)));
  const xi = inv(xtx);
  const xty = Array.from({ length: k }, (_, i) => X.reduce((a, r, t) => a + r[i] * y[t], 0));
  const b = xi.map((r) => r.reduce((a, v, j) => a + v * xty[j], 0));
  const e = X.map((r, t) => y[t] - r.reduce((a, v, j) => a + v * b[j], 0));
  const meat = Array.from({ length: k }, (_, i) => Array.from({ length: k }, (_, j) => X.reduce((a, r, t) => a + r[i] * r[j] * e[t] * e[t], 0)));
  const mul = (P: number[][], Q: number[][]) => P.map((r) => Q[0].map((_, j) => r.reduce((a, v, m) => a + v * Q[m][j], 0)));
  const V = mul(mul(xi, meat), xi).map((r) => r.map((v) => (v * n) / (n - k)));
  const s2 = e.reduce((a, v) => a + v * v, 0) / (n - k);
  return { b, V, s2 };
}

const est = (estimate: number, se: number): Est => ({ estimate, se, lo: estimate - Z * se, hi: estimate + Z * se });

/** Per-day and pooled effects of one series: dates are local days (YYYY-MM-DD), event marks the window days. */
export function estimate(dates: string[], y: number[], event: boolean[]): Study {
  const yearsBase = [...new Set(dates.filter((_, i) => !event[i]).map((d) => Number(d.slice(0, 4))))].sort((a, b) => a - b);
  const all = design(dates, event, yearsBase, false);
  const base = dropEmpty(all.X.filter((_, i) => !event[i]), all.names);
  const { b, V, s2 } = olsHc1(base.X, y.filter((_, i) => !event[i]));
  const days: DayEst[] = [];
  all.X.forEach((r, i) => {
    if (!event[i]) return;
    const x = base.keep.map((j) => r[j]);
    const cf = x.reduce((a, v, j) => a + v * b[j], 0);
    const q = x.reduce((a, v, j) => a + v * V[j].reduce((s, w, m) => s + w * x[m], 0), 0);
    days.push({ day: dates[i], counterfactual: cf, ...est(y[i] - cf, Math.sqrt(s2 + q)) });
  });
  const p = design(dates, event, yearsBase, true);
  const pd = dropEmpty(p.X, p.names);
  const fit = olsHc1(pd.X, y);
  const j = pd.names.indexOf("pooled");
  return {
    days, pooled: est(fit.b[j], Math.sqrt(fit.V[j][j])),
    counterfactualMean: days.reduce((a, d) => a + d.counterfactual, 0) / days.length, n: y.length, nBase: event.filter((e) => !e).length,
  };
}

/** A study from event_window_daily rows of one event, entity and variable (daily rows only). */
export function studyOf(event: string, rows: { ts_utc: string; value: number; freq?: string | null }[]): Study {
  const [s, e] = WINDOWS[event];
  const r = rows.filter((x) => !x.freq || x.freq === "P1D").map((x) => ({ d: x.ts_utc.slice(0, 10), v: Number(x.value) })).sort((a, b) => (a.d < b.d ? -1 : 1));
  return estimate(r.map((x) => x.d), r.map((x) => x.v), r.map((x) => x.d >= s && x.d <= e));
}
