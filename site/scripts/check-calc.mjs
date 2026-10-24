// Energy Research Warehouse (ERW) site, session 1165 (chain 078): the arithmetic of check-values' calc|<op>|<A>|<B>[|<C>]
// keys (session 44), moved here so a node test can hold it (scripts/test-grid-balance.mjs). Each operand is a check key
// with "~" for "|", recomputed by check-values on its own; this file only combines the values.
//   ratio: A / B; diff: A - B; pct: A / B x 100 (two operands, as since session 44)
//   bal: A - B - C (three operands, session 1165: the Grid tool's balance, net generation less demand less net export)
//   diffpct: (A - B) / A x 100 (two operands, session 1166: the Mix tab's forecast miss at the peak, demand less the
//   day-ahead forecast over demand, components/grid/Conditions.tsx)
//   add: A + B + ... (two operands or more, session 1406: the Lower 48's Network panel, the seven grids' demand summed and
//   their exchange with the grids around them, components/grid/Lower48Demand.tsx)
//   addpct: (A + B + ...) / Z x 100, Z the last operand (three operands or more, session 1406: the seven grids' demand as
//   a percent of the Lower 48's)
// Any other op, or another count of operands, has no value (undefined), as an unknown op had none before.

const ARITY = { ratio: 2, diff: 2, pct: 2, bal: 3 };
ARITY.diffpct = 2;   // session 1166: (A - B) / A x 100
// session 1406: the ops that take any count of operands from the least given; added left to right, as the page adds them
const AT_LEAST = { add: 2, addpct: 3 };

/** The operand keys of a calc key's parts after "calc" and the op, "~" turned back into "|". */
export function calcOperands(parts) {
  return parts.map((k) => k.replaceAll("~", "|"));
}

/** The value of op over the operands' values; undefined for an unknown op, a wrong count, or a value not finite. */
export function calcOf(op, xs) {
  if (AT_LEAST[op] !== undefined) {   // session 1406
    if (xs.length < AT_LEAST[op] || !xs.every((v) => Number.isFinite(v))) return undefined;
    const sum = (vs) => vs.reduce((a, v) => a + v, 0);
    return op === "add" ? sum(xs) : (sum(xs.slice(0, -1)) / xs[xs.length - 1]) * 100;
  }
  if (ARITY[op] === undefined || xs.length !== ARITY[op] || !xs.every((v) => Number.isFinite(v))) return undefined;
  const [x, y, w] = xs;
  if (op === "diffpct") return ((x - y) / x) * 100;   // session 1166
  return op === "ratio" ? x / y : op === "diff" ? x - y : op === "pct" ? (x / y) * 100 : x - y - w;
}
