// Energy Research Warehouse (ERW) site, session 6113 (chain 280): a table of the record the catalogue does not list
// (lib/chat/refused.ts notListedWords, NOT_LISTED_NOTE, as warehouse/chat/tools.py not_listed_words). No model, no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-6113.mjs
//
// Prints one JSON line of the words for a table whose license is not settled and for one that is public and not loaded;
// tests/test_session6113_ask.py sets the line against the Python tool's words, so the two languages agree.
import assert from "node:assert/strict";
import fs from "node:fs";

const { NOT_LISTED_NOTE, notListedWords, refusedRead, refusedWhole } = await import("../lib/chat/refused.ts");
const held = notListedWords("utility_large_load_rules", "unsettled"), open = notListedWords("forecast_tool_parameters", "public");
console.log(JSON.stringify({ unsettled: held, internal: notListedWords("large_load_waits", "internal"), public: open, note: NOT_LISTED_NOTE }));
// the loop's own readers take both as a table refused whole: it is not asked again, and an answer may not cite it
for (const [t, w] of [["utility_large_load_rules", held], ["forecast_tool_parameters", open]]) {
  assert.ok(w.startsWith(`table ${t} is not in this site's live set: `), t);
  assert.equal(refusedWhole(w, [t]), t);
  assert.ok(refusedRead(w));
  assert.match(w, /No tool here can read it, and no figure of it may be stated\./);
  assert.match(w, new RegExp(`never answer for ${t} from a table that holds something else`));
}
assert.match(held, /license is not settled \(license needed\)/);
assert.doesNotMatch(open, /license needed/);
assert.doesNotMatch(open + held, /Redivis/);   // an unsettled table is on no public copy, and a new one may not be yet
const tools = fs.readFileSync(new URL("../lib/chat/tools.ts", import.meta.url), "utf8");
assert.match(tools, /if \(verdict\) throw new ToolError\(notListedWords\(name, verdict\)\);/);
assert.match(tools, /Internal tables are not visible here\. \$\{NOT_LISTED_NOTE\}`,/);
console.log("test-ask-6113: ok");
