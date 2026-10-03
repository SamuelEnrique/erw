// Energy Research Warehouse (ERW) site, session 75: a local stand-in for Supabase's REST API, for /shoulder, as
// scripts/buildout-stub.mjs is for /storage/buildout.
//
//   node scripts/shoulder-stub.mjs [port]                (default 54375)
//   SUPABASE_URL=http://localhost:54375 SUPABASE_ANON_KEY=local npm run build && ... npx next start -p 3075
//   node scripts/check-shoulder.mjs http://localhost:3075
//
// shoulder_hours_monthly is not in Supabase until session 75's finish step (loading it would add a row to the catalogue
// the live home page counts), so the page cannot be seen against the live set. This serves GET /rest/v1/series from the
// table as built in warehouse/output, with the filters the page's reader uses (table_name eq, order, limit, offset).
// Every other table answers with no rows. It writes nothing.
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
// session 80: SHOULDER_TABLE_FILE points the stub (and check-shoulder) at a trial build, for a table not yet in warehouse/output
export const TABLE_FILE = process.env.SHOULDER_TABLE_FILE ?? path.join(here, "..", "..", "warehouse", "output", "shoulder_hours_monthly.csv");
export const TABLE = "shoulder_hours_monthly";

/** The table's rows as { entity, variable, ts_utc, value }. The table has no quoted cell. */
export function tableRows(file = TABLE_FILE) {
  const lines = fs.readFileSync(file, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const cols = lines[0].split(",");
  return lines.slice(1).map((l) => {
    const c = l.split(",");
    const r = Object.fromEntries(cols.map((k, i) => [k, c[i]]));
    return { entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value) };
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.argv[2] ?? 54375);
  const rows = tableRows();
  http.createServer((req, res) => {
    const url = new URL(req.url, `http://localhost:${port}`);
    const q = Object.fromEntries(url.searchParams);
    let out = [];
    if (req.method === "GET" && url.pathname === "/rest/v1/series" && q.table_name === `eq.${TABLE}`) {
      out = [...rows].sort((a, b) => a.entity.localeCompare(b.entity) || a.variable.localeCompare(b.variable) || a.ts_utc.localeCompare(b.ts_utc));
      const offset = Number(q.offset ?? 0), limit = Number(q.limit ?? 1000);
      out = out.slice(offset, offset + limit).map((r) => ({ ...r, ts_utc: r.ts_utc.replace("Z", "+00:00") }));
    }
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(out));
  }).listen(port, () => console.log(`shoulder stub: ${rows.length} rows of ${TABLE} on http://localhost:${port}`));
}
