// Energy Research Warehouse (ERW) site, session 143: the spending cap of an evaluation run, as two pure functions, so
// that a test can hold the rule without a request (scripts/eval-ask-speed.mjs is the runner that uses them).
// A session's spend is the sum of its runs. One more question may be asked only while that spend plus a reserve for the
// question does not pass the stop: asked before the question, never after it.

/** What the session has spent so far: the sum of every run in the spend file. */
export function sessionSpend(file) { return (file.runs ?? []).reduce((a, r) => a + (r.usd ?? 0), 0); }
/** May one more question be asked? */
export function mayAsk(spentSoFar, reserveUsd, stopUsd) { return spentSoFar + reserveUsd <= stopUsd; }
