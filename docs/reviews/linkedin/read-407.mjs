// Session 407: read every figure of the ten LinkedIn posts again from Supabase, the query check-values.mjs runs for a
// series key (the series table, by table_name, entity, variable, ts_utc and, for an event page, event), and compare
// it with the raw value the page carried in the passing full check-values run of 20 October 2026 (posts.json). The
// page's text for a raw value is fixed by the page's own code, so an equal raw value is the figure the page shows.
//
//   node docs/reviews/linkedin/read-407.mjs            (SUPABASE_URL and SUPABASE_ANON_KEY from site/.env.local)
//
// Prints one line a key and exits 1 when any key cannot be read or differs. Writes nothing.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const spec = JSON.parse(fs.readFileSync(path.join(here, "posts.json"), "utf-8"));

function env(name) {
  if (process.env[name]) return process.env[name];
  const f = path.join(here, "..", "..", "..", "site", ".env.local");
  if (fs.existsSync(f)) {
    for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
      const m = line.match(/^([A-Z_]+)=(.*)$/);
      if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
    }
  }
  throw new Error(`${name} is not set`);
}

const origin = new URL(env("SUPABASE_URL")).origin;
const key = env("SUPABASE_ANON_KEY");

async function read(check) {
  const [kind, table, entity, variable, at, event] = check.split("|");
  if (kind !== "series") throw new Error(`not a series key: ${check}`);
  const params = { select: "value,ts_utc", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${variable}`, ts_utc: `eq.${at}` };
  if (event) params.event = `eq.${event}`;
  let body = "";
  for (let attempt = 0; attempt < 3; attempt++) {
    const res = await fetch(`${origin}/rest/v1/series?${new URLSearchParams(params)}`, {
      headers: { apikey: key, Authorization: `Bearer ${key}` }, signal: AbortSignal.timeout(60000),
    });
    if (res.ok) {
      const rows = await res.json();
      if (rows.length !== 1) throw new Error(`${rows.length} rows`);
      return Number(rows[0].value);
    }
    body = (await res.text()).slice(0, 160);
    if (res.status === 500 && body.includes("57014") && attempt < 2) { await new Promise((r) => setTimeout(r, attempt ? 3000 : 1000)); continue; }
    throw new Error(`HTTP ${res.status} ${body}`);
  }
  throw new Error(body);
}

let failed = 0;
for (const item of [...spec.posts.map((p) => ({ ...p, role: "figure" })), ...spec.also.map((a) => ({ ...a, role: "also" }))]) {
  try {
    const v = await read(item.key);
    const same = Math.abs(v - item.raw) < 1e-9 * Math.max(1, Math.abs(item.raw));
    if (!same) failed += 1;
    console.log(`${same ? "ok  " : "DIFF"} | post ${item.n} ${item.role} | ${item.key} | Supabase ${v} | the page read ${item.raw} and showed "${item.shown}"`);
  } catch (e) {
    failed += 1;
    console.log(`FAIL | post ${item.n} ${item.role} | ${item.key} | ${e.message ?? e}`);
  }
}
console.log(failed ? `${failed} key(s) not read or different` : "every key read, every value equal to the one the page showed");
process.exit(failed ? 1 : 0);
