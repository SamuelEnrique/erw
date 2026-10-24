// Energy Research Warehouse (ERW) site, session 1166 (chain 078): check-values' fmt|<form>|<key> keys. A figure the page
// writes in a form of its own (a percent to one decimal, a signed whole number) is keyed by the key that recomputes its
// value, behind fmt|<form>|. check-values recomputes the inner key as it would alone, then holds the page's text to the
// recomputed value written in that form, exactly: the text is recomputed, not only the number. A node test holds this
// file (scripts/test-grid-file-keys.mjs). No import: node runs it as it is.
//
//   f1   x.toFixed(1)                                   (Conditions.tsx: the forecast's miss in percent, the degree days)
//   n0   whole, thousands separated                     (lib/format.ts count, lib/mixpage.ts n0)
//   n1   one decimal, thousands separated               (lib/mixpage.ts n1)
//   n2   two decimals, thousands separated              (lib/mixpage.ts n2)
//   pm0  "+" at or above zero, else U+2212, then the whole size, thousands separated (Conditions.tsx: the forecast's miss in MW)
//   sn0  "+" above zero, then n0 (the forecast view's mean error)
//   sn1  "+" above zero, then n1 (the clean view's change when load moves)
//   span a stretch of hours as days and hours, "1 day 14 hours", "18 hours" (lib/stress.ts span: the dark, calm stretches'
//        longest; session 1168)
// The key's inner part is any key check-values knows (calc|..., series|..., file|...), written as it is, after the form:
// fmt|<form>| is a prefix, so an inner calc key keeps its "~" operands.

const L = (x, d) => x.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const whole = (x) => Math.round(x).toLocaleString("en-US");
/** Session 1168: lib/stress.ts span, as it stands there: whole days, then the hours left rounded, each named. */
function span(hours) {
  const d = Math.floor(hours / 24), h = Math.round(hours - d * 24);
  const days = d ? `${d} day${d === 1 ? "" : "s"}` : "", hs = h || !d ? `${h} hour${h === 1 ? "" : "s"}` : "";
  return [days, hs].filter(Boolean).join(" ");
}

export const FORMS = {
  f1: (x) => x.toFixed(1),
  n0: (x) => whole(x),
  n1: (x) => L(x, 1),
  n2: (x) => L(x, 2),
  pm0: (x) => `${x >= 0 ? "+" : "−"}${whole(Math.abs(x))}`,
  sn0: (x) => `${x > 0 ? "+" : ""}${whole(x)}`,
  sn1: (x) => `${x > 0 ? "+" : ""}${L(x, 1)}`,
  span: (x) => span(x),
};

/** The form and the inner key of a fmt| key, or null for another key (or a form not in FORMS). */
export function fmtParts(check) {
  const p = String(check).split("|");
  if (p[0] !== "fmt" || p.length < 3 || !(p[1] in FORMS)) return null;
  return { form: p[1], inner: p.slice(2).join("|") };
}

/** A value written in a form; undefined when the value is not a finite number. */
export function formText(form, x) {
  const v = Number(x);
  if (x === null || x === undefined || x === "" || !Number.isFinite(v) || !(form in FORMS)) return undefined;
  return FORMS[form](v);
}

/** The key a page writes for a figure in a form: fmt|<form>|<inner>. */
export function fmtKey(form, inner) {
  if (!(form in FORMS)) throw new Error(`unknown form ${form}`);
  return `fmt|${form}|${inner}`;
}
