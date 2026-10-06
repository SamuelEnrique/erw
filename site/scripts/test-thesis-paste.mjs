// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis). The two halves of the PitchBook stage
// agree: the format the server's paste text shows a Claude chat (warehouse/thesis/run.py, pitchbook_request) is the
// format the site's validator accepts (lib/thesis/pitchbook.ts).
//
//   node --import ./scripts/alias-register.mjs scripts/test-thesis-paste.mjs <file holding one run's paste text>
//
// The example block of the paste text is read as an answer: its date placeholder filled, its example companies kept
// as they are (they are the template's examples and no company's figures). Nothing is requested or stored.
import assert from "node:assert/strict";
import fs from "node:fs";
import * as pb from "../lib/thesis/pitchbook.ts";

const text = fs.readFileSync(process.argv[2], "utf8");
const block = text.split("```json")[1].split("```")[0];
const example = JSON.parse(block);
const run = /^Run: (\S+)$/m.exec(text)[1];
const key = /^Key: (\S+)$/m.exec(text)[1];
assert.equal(example.run_id, run, "the example names the run");
assert.equal(example.key, key, "the example carries the key");
assert.equal(pb.validatePitchbook({ ...example, key: undefined }, run).ok, false, "the unfilled template is refused: its date is a placeholder");

const sub = pb.readSubmission({ ...example, pulled_on: "2026-10-07" });
assert.equal(sub.ok, true, sub.reason);
assert.equal(sub.run_id, run);
assert.equal(sub.key, key);
const checked = pb.validatePitchbook(sub.payload, sub.run_id);
assert.equal(checked.ok, true, checked.reason);
assert.equal(checked.payload.label, "PitchBook");
assert.equal(checked.payload.companies.length, 2);
assert.deepEqual(checked.payload.companies[1], { name: "a company PitchBook does not hold", found: false });
assert.equal(checked.payload.companies[0].last_round.size_usd_m, 12.5);
assert.equal(checked.payload.additional_companies.length, 1);
assert.equal("key" in checked.payload, false, "the key is not stored with the answer");
console.log("ok   the paste text's example, with its date filled, passes the validator; the key is taken from it and not stored");
