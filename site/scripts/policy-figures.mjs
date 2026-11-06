// Session 3061 (chain 166): every key the policy monitor's page can show (lib/policymonitor.ts, keysOf), as JSON on one
// line, for scripts/check_policy.py, which traces each to its row of policy_actions (as digest-figures.mjs serves
// scripts/check_digest.py).
//   node --import ./scripts/alias-register.mjs scripts/policy-figures.mjs [path of monitor.json]
import { readFileSync } from "node:fs";

const M = await import("../lib/policymonitor.ts");
const path = process.argv[2] ?? new URL("../data/policy/monitor.json", import.meta.url);
const file = JSON.parse(readFileSync(path, "utf-8"));
console.log(JSON.stringify({ built: file.built, records: file.records, keys: M.keysOf(file) }));
