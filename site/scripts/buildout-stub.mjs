// Energy Research Warehouse (ERW) site, session 69: a local stand-in for Supabase's REST API, for /storage/buildout.
//
//   node scripts/buildout-stub.mjs [port]                (default 54369)
//   SUPABASE_URL=http://localhost:54369 SUPABASE_ANON_KEY=local npm start
//
// storage_buildout_monthly is not in Supabase until session 69's finish step, so the page cannot be seen against the
// live set. This serves GET /rest/v1/series from the test fixture (tests/fixtures/session69/, real values cut from the
// scratch table) with the PostgREST filters the page's reader uses: table_name, entity and variable (eq), ts_utc (eq,
// in), order (the key, or ts_utc.desc), limit and offset. Every other table answers with no rows. It writes nothing
// and no page code knows it exists: the site reads it only because SUPABASE_URL points at it.
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const FIXTURE = path.join(here, "..", "..", "tests", "fixtures", "session69", "storage_buildout_monthly.csv");
export const TABLE = "storage_buildout_monthly";

/** The fixture's rows as { entity, variable, ts_utc, value, unit, freq }. The table has no quoted cell. */
export function fixtureRows(file = FIXTURE) {
  const lines = fs.readFileSync(file, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const cols = lines[0].split(",");
  return lines.slice(1).map((l) => {
    const c = l.split(",");
    if (c.length !== cols.length) throw new Error(`a fixture row does not have ${cols.length} cells: ${l}`);
    const r = Object.fromEntries(cols.map((k, i) => [k, c[i]]));
    return { entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value), unit: r.unit, freq: r.freq };
  });
}

const eq = (f) => (f && f.startsWith("eq.") ? f.slice(3) : null);
const instant = (s) => new Date(s.replace(/^"|"$/g, "")).getTime();

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.argv[2] ?? 54369);
  const rows = fixtureRows();
  http.createServer((req, res) => {
    const url = new URL(req.url, `http://localhost:${port}`);
    const q = Object.fromEntries(url.searchParams);
    let out = [];
    if (req.method === "GET" && url.pathname === "/rest/v1/series" && eq(q.table_name) === TABLE) {
      out = rows.filter((r) => (!q.entity || r.entity === eq(q.entity)) && (!q.variable || r.variable === eq(q.variable)));
      if (q.ts_utc?.startsWith("eq.")) out = out.filter((r) => instant(r.ts_utc) === instant(q.ts_utc.slice(3)));
      if (q.ts_utc?.startsWith("in.(")) {
        const want = new Set(q.ts_utc.slice(4, -1).split(",").map(instant));
        out = out.filter((r) => want.has(instant(r.ts_utc)));
      }
      const desc = (q.order ?? "").startsWith("ts_utc.desc");
      out = [...out].sort((a, b) => desc ? b.ts_utc.localeCompare(a.ts_utc)
        : a.entity.localeCompare(b.entity) || a.variable.localeCompare(b.variable) || a.ts_utc.localeCompare(b.ts_utc));
      const offset = Number(q.offset ?? 0), limit = Number(q.limit ?? 1000);
      const fields = (q.select ?? "entity,variable,ts_utc,value,unit,freq").split(",");
      // Supabase writes a timestamptz as +00:00, not Z: the page must read both
      out = out.slice(offset, offset + limit).map((r) => Object.fromEntries(fields.map((f) => [f, f === "ts_utc" ? r.ts_utc.replace("Z", "+00:00") : r[f]])));
    }
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(out));
  }).listen(port, () => console.log(`buildout stub: ${rows.length} fixture rows of ${TABLE} on http://localhost:${port}`));
}
