// Energy Research Warehouse (ERW) site: how check-values.mjs reads its pages on a slow database (session 430).
//
// On 21 October 2026 the full run passed its 15-minute limit three times (sessions 461, 474 and 423): the live set
// answered its heavier reads slowly, and a run that stops at its limit reports nothing. This module runs the pages one at
// a time, in batches, each under a timeout of its own, so the run ends with what it read and a list of what it did not:
//   1. a page has PAGE_MS to be read and judged; past it the page's requests are aborted and the page waits;
//   2. after the last page, each page that timed out is tried once more, while the run's own limit allows;
//   3. a page that timed out twice, or that the run's limit reached, is "not read": its floor is not judged, and
//      check-values says so on a line of its own and ends with exit 3 (incomplete), never with exit 0;
//   4. after each batch the state is written (CHECK_VALUES_STATE, under runs/), so a second run with CHECK_VALUES_RESUME=1
//      reads only the pages the first did not.
// Nothing here reads Supabase or a page: readPage does, and check-values.mjs gives it. tests: scripts/test-check-values-run.mjs.
import fs from "node:fs";
import path from "node:path";

/** Whether an error is the slowness this module waits out (a timeout or an abort), rather than a fault to report. */
export function isTimeout(e) {
  if (!e) return false;
  if (e.name === "TimeoutError" || e.name === "AbortError") return true;
  const m = String(e.message ?? e);
  return m.includes("57014") || /HTTP 50[34]\b/.test(m) || m.includes("statement timeout");
}

function timeoutError(what) {
  const e = new Error(what);
  e.name = "TimeoutError";
  return e;
}

/** One page under its own timeout: readPage(page, signal) settles, or the signal aborts it and this rejects. */
async function attempt(page, readPage, ms) {
  const ctl = new AbortController();
  let timer;
  const expired = new Promise((_, reject) => {
    timer = setTimeout(() => {
      const e = timeoutError(`${page}: not read within ${Math.round(ms / 1000)} s`);
      ctl.abort(e);
      reject(e);
    }, Math.max(0, ms));
  });
  try {
    return await Promise.race([readPage(page, ctl.signal), expired]);
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Read every page of `pages` not in `done`, in order, in batches of `batch`.
 *   readPage(page, signal): resolves with the page's result; rejects with a timeout (isTimeout) to be tried again, or with
 *   any other error, which is the page's result as { error } (check-values reports it as a failure, never as not read).
 *   pageMs: one page's limit; deadline: the time (ms since the epoch) after which no page starts and a running one stops.
 *   onBatch({ results, notRead, pending }): called after each batch and after the retries (check-values writes its state).
 * Returns { results: Map(page -> result), notRead: [{ page, why }], retried: [page] }.
 */
export async function runPages({ pages, readPage, pageMs, deadline, batch = 10, done = new Set(), onBatch = () => {}, now = () => Date.now(), onRetry = () => {} }) {
  const results = new Map();
  const notRead = [];
  const timedOut = [];
  const retried = [];
  const todo = pages.filter((p) => !done.has(p));
  const left = () => deadline - now();
  async function one(page) {
    if (left() <= 0) return "limit";
    try {
      results.set(page, await attempt(page, readPage, Math.min(pageMs, left())));
      return "read";
    } catch (e) {
      if (!isTimeout(e)) { results.set(page, { error: e }); return "read"; }
      return left() <= 0 ? "limit-during" : "timeout";
    }
  }
  for (let i = 0; i < todo.length; i += batch) {
    for (const page of todo.slice(i, i + batch)) {
      const r = await one(page);
      if (r === "timeout") timedOut.push(page);
      else if (r === "limit") notRead.push({ page, why: "the run's limit was reached before it was read" });
      else if (r === "limit-during") notRead.push({ page, why: "the run's limit was reached while it was read" });
    }
    onBatch({ results, notRead, pending: timedOut });
  }
  for (const page of timedOut) {
    if (left() <= 0) { notRead.push({ page, why: "timed out once; the run's limit left no time to try it again" }); continue; }
    onRetry(page);
    retried.push(page);
    const r = await one(page);
    const why = { limit: "timed out once; the run's limit left no time to try it again", "limit-during": "timed out once; the run's limit was reached while it was tried again", timeout: "timed out twice" }[r];
    if (why) notRead.push({ page, why });
  }
  if (timedOut.length) onBatch({ results, notRead, pending: [] });
  return { results, notRead, retried };
}

/** The state file of a run: its pages read (with their results as check-values stores them), for CHECK_VALUES_RESUME=1. */
export function stateKey(base, only) {
  return JSON.stringify({ base, only: [...only].sort() });
}

export function loadState(file, key) {
  try {
    const s = JSON.parse(fs.readFileSync(file, "utf-8"));
    if (s.key !== key) return { state: null, why: `the state file was written for another run (${s.key}); this run starts afresh` };
    return { state: s, why: "" };
  } catch {
    return { state: null, why: "no state file to resume from; this run starts afresh" };
  }
}

export function saveState(file, state) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(state, null, 1) + "\n");
  fs.renameSync(tmp, file);
}
