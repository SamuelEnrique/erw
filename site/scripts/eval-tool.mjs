// Energy Research Warehouse (ERW) site, session 5202 (chain 235): one or more calls of the chat's own tools
// (lib/chat/tools.ts runTool, the anon key, reads only), printed as JSON lines. No model. For writing an evaluation's
// questions against what the chat itself can read, and for checking a key the way the chat would read it.
//
//   node --import ./scripts/eval-register.mjs scripts/eval-tool.mjs describe_table '{"table":"storage_capacity"}' [more pairs]
//   node --import ./scripts/eval-register.mjs scripts/eval-tool.mjs --file calls.json     ([{name, input, grid?}, ...])
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "..", "..");
const envFile = [path.join(root, ".env"), path.join(root, "..", "erw", ".env")].find((p) => fs.existsSync(p));
if (envFile) {
  for (const line of fs.readFileSync(envFile, "utf8").split(/\r?\n/)) {
    const m = /^\s*(SUPABASE_URL|SUPABASE_ANON_KEY)\s*=\s*(.*?)\s*$/.exec(line);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^(["'])(.*)\1$/, "$2");
  }
}
delete process.env.SUPABASE_SERVICE_KEY;
const { runTool, scopeOf } = await import("../lib/chat/tools.ts");
const args = process.argv.slice(2);
let calls = [];
if (args[0] === "--file") calls = JSON.parse(fs.readFileSync(args[1], "utf8"));
else for (let i = 0; i + 1 < args.length; i += 2) calls.push({ name: args[i], input: JSON.parse(args[i + 1]) });
for (const c of calls) {
  try {
    const { out, isError } = await runTool(c.name, c.input, c.grid ? scopeOf(c.grid) : null);
    console.log(JSON.stringify({ name: c.name, input: c.input, grid: c.grid ?? null, isError, out }));
  } catch (e) {
    console.log(JSON.stringify({ name: c.name, input: c.input, grid: c.grid ?? null, isError: true, out: { error: String(e?.message ?? e) } }));
  }
}
