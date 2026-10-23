// Energy Research Warehouse (ERW) site, session 1165 (chain 078): the arithmetic of check-values' calc|<op>|<A>|<B>[|<C>]
// keys (session 44), moved here so a node test can hold it (scripts/test-grid-balance.mjs). Each operand is a check key
// with "~" for "|", recomputed by check-values on its own; this file only combines the values.
//   ratio: A / B; diff: A - B; pct: A / B x 100 (two operands, as since session 44)
//   bal: A - B - C (three operands, session 1165: the Grid tool's balance, net generation less demand less net export)
//   diffpct: (A - B) / A x 100 (two operands, session 1166: the Mix tab's forecast miss at the peak, demand less the
//   day-ahead forecast over demand, components/grid/Conditions.tsx)
// Any other op, or another count of operands, has no value (undefined), as an unknown op had none before.

const ARITY = { ratio: 2, diff: 2, pct: 2, bal: 3 };
ARITY.diffpct = 2;   // session 1166: (A - B) / A x 100

/** The operand keys of a calc key's parts after "calc" and the op, "~" turned back into "|". */
export function calcOperands(parts) {
  return parts.map((k) => k.replaceAll("~", "|"));
}

/** The value of op over the operands' values; undefined for an unknown op, a wrong count, or a value not finite. */
export function calcOf(op, xs) {
  if (ARITY[op] === undefined || xs.length !== ARITY[op] || !xs.every((v) => Number.isFinite(v))) return undefined;
  const [x, y, w] = xs;
  if (op === "diffpct") return ((x - y) / x) * 100;   // session 1166
  return op === "ratio" ? x / y : op === "diff" ? x - y : op === "pct" ? (x / y) * 100 : x - y - w;
}
