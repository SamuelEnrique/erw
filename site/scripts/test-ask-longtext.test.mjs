// Energy Research Warehouse (ERW) site, session 6111 (chain 280): a column of prose is named, not listed
// (lib/chat/longtext.ts), as warehouse/chat/tools.py holds the same rule (tests/test_session6111_ask.py holds the Python
// side). No build, no network: node strips the file's types.
//
//   node --test site/scripts/test-ask-longtext.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { LONG_TEXT, LONG_TEXT_NOTE, splitLongText } from "../lib/chat/longtext.ts";

const here = path.dirname(fileURLToPath(import.meta.url));

test("a column with a value over 200 characters is prose: named with its count and its longest value's length", () => {
  const clause = "The minimum initial contract term for ESAs below 100 MW will be the greater of (a) 10 years and (b) 5 years plus the load ramp period. ".repeat(2);
  assert.ok(clause.length > LONG_TEXT);
  const { short, long } = splitLongText({ status: ["approved", "in effect", "proposed"], x_state: ["NC", "TX"], x_contract_term: [clause, "not published"] });
  assert.deepEqual(short, { status: ["approved", "in effect", "proposed"], x_state: ["NC", "TX"] });
  assert.deepEqual(long, { x_contract_term: { distinct: 2, longest_chars: clause.length } });
});

test("a value of exactly 200 characters is still listed, and a table with no prose is as it was", () => {
  const at = "x".repeat(200), over = "x".repeat(201);
  assert.deepEqual(splitLongText({ a: [at] }), { short: { a: [at] }, long: {} });
  assert.deepEqual(splitLongText({ a: [over] }), { short: {}, long: { a: { distinct: 1, longest_chars: 201 } } });
  assert.deepEqual(splitLongText({}), { short: {}, long: {} });
  // the Python tool's form: a dict of counts
  assert.deepEqual(splitLongText({ status: { approved: 21, proposed: 25 }, x_notes: { [over]: 1 } }), { short: { status: { approved: 21, proposed: 25 } }, long: { x_notes: { distinct: 1, longest_chars: 201 } } });
});

test("the note says how one row's text is read, in the Python tool's words", () => {
  assert.equal(LONG_TEXT, 200);
  assert.match(LONG_TEXT_NOTE, /^columns of prose as the source printed it \(a value is over 200 characters\): their values are not listed here\./);
  assert.match(LONG_TEXT_NOTE, /call query with aggregation count, group_by set to the column, and where narrowed to that row/);
  const py = fs.readFileSync(path.join(here, "..", "..", "warehouse", "chat", "tools.py"), "utf8").replace(/\r\n/g, "\n");   // a Windows checkout's line ends
  const said = /LONG_TEXT_NOTE = \(([\s\S]*?)\)\n\n/.exec(py)[1].split("\n").map((l) => l.trim().replace(/^"|"$/g, "")).join("");
  assert.equal(said, LONG_TEXT_NOTE);
  assert.match(py, /^LONG_TEXT = 200$/m);
});

test("describe_table uses it for a table of things or events", () => {
  const ts = fs.readFileSync(path.join(here, "..", "lib", "chat", "tools.ts"), "utf8");
  assert.match(ts, /import \{ LONG_TEXT_NOTE, splitLongText \} from "\.\/longtext";/);
  assert.match(ts, /out\.long_text_columns = split\.long;/);
  assert.match(ts, /out\.long_text_columns_note = LONG_TEXT_NOTE;/);
});
