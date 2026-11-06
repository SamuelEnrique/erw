// Energy Research Warehouse (ERW) site, session 1309: the site's number check and unit check (lib/chat/ask.ts
// unverified, unitMismatches) on answers and sources given in a JSON file, for tests/test_session1309.py to hold equal
// to the Python checks (warehouse/chat/ask.py) on the same inputs. No model, no request.
//
//   node --import ./scripts/alias-register.mjs scripts/run-checks-1309.mjs <cases.json> <out.json>
//   cases.json: [{ "key": "...", "answer": "...", "sources": ["...", ...] }, ...]
import fs from "node:fs";

const [inPath, outPath] = process.argv.slice(2);
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
const { unverified, unitMismatches } = await import("../lib/chat/ask.ts");
const cases = JSON.parse(fs.readFileSync(inPath, "utf8"));
const out = {};
for (const c of cases) out[c.key] = { numbers: unverified(c.answer, c.sources), units: unitMismatches(c.answer, c.sources) };
fs.writeFileSync(outPath, JSON.stringify(out));
console.log(`${cases.length} cases`);
