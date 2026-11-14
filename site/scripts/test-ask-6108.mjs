// Energy Research Warehouse (ERW) site, session 6108 (chain 280): a percentile's ordinal is the name of a statistic
// (lib/chat/ask.ts withoutPercentileNames, as warehouse/chat/ask.py without_percentile_names). No model, no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-6108.mjs
//
// Prints one JSON line of what the check returns for each answer, then asserts; tests/test_session6108_ask.py sets the
// line against the Python check on the same strings, so the two languages agree.
import assert from "node:assert/strict";
import fs from "node:fs";

const { unverified, withoutPercentileNames } = await import("../lib/chat/ask.ts");
const fx = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session6108/percentiles.json", import.meta.url), "utf8"));
const got = Object.fromEntries(fx.answers.map((a) => [a.id, unverified(a.answer, a.named === false ? fx.sources_unnamed : fx.sources)]));
console.log(JSON.stringify({ unverified: got, stripped: withoutPercentileNames(fx.phrase, fx.sources) }));
for (const a of fx.answers) assert.deepEqual(got[a.id], a.untraced, a.id);
assert.equal(withoutPercentileNames(fx.phrase, fx.sources), fx.phrase_stripped);
assert.equal(withoutPercentileNames(fx.phrase, fx.sources_unnamed), fx.phrase);
console.log("test-ask-6108: ok");
