const M = await import("../app/cost-of-power/model.ts");
for (const query of process.argv.slice(2)) {
  const q = Object.fromEntries(new URLSearchParams(query));
  const x = M.inputsFrom(q);
  const m = await M.loadModel(x, typeof q.buy === "string", q.grid, q);
  console.log("==", query, "| failed:", m.failed);
  console.log("  flat per:", m.s12?.flat, "held", m.s12?.held, "| ref12:", m.ref12?.flat, "| market:", m.market, "| span:", m.l12Span);
  for (const k of ["growth", "peak", "peakAt", "cf", "cy", "cv", "ll", "own", "qv", "waitsFor", "utilities", "deliveryParts"]) console.log("  ", k, "=", (JSON.stringify(m[k]) ?? "undefined").slice(0, 420));
  console.log("   rules:", (JSON.stringify(m.rules) ?? "").slice(0, 200));
}
