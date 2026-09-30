// Energy Research Warehouse (ERW) site: GET /api/download?table=<table>, one public table of the live set
// as CSV (session 21, ruling 10). Streams from Supabase with the anon key (public rows only), page by
// page, with the table's provenance header lines at the top (as '#' lines, as in the ERW's own CSVs),
// then the table's columns in their CSV order. At most 200,000 rows: a larger table answers 413 and
// points to Redivis. A windowed table (for example the last 35 days of prices) gives what the live set
// holds; the full history is on Redivis.
import site from "@/data/site.json";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_ROWS = 200_000;
const PAGE = 1000;
const STD: Record<string, string[]> = {
  series: ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"],
  entities: ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"],
  events: ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"],
};
const ORDER: Record<string, string> = { series: "entity,variable,ts_utc", entities: "entity_id", events: "event_id" };

function supa() {
  const url = process.env.SUPABASE_URL, key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL or SUPABASE_ANON_KEY is not set on the server");
  return { base: new URL(url).origin, headers: { apikey: key, Authorization: `Bearer ${key}` } };
}

async function get(path: string, extra: Record<string, string> = {}) {
  const { base, headers } = supa();
  const res = await fetch(`${base}/rest/v1/${path}`, { headers: { ...headers, ...extra }, cache: "no-store" });
  if (!res.ok) throw new Error(`Supabase ${path.split("?")[0]}: HTTP ${res.status}`);
  return res;
}

// the ERW writes UTC times with Z; Supabase returns +00:00
const cell = (v: unknown): string => {
  if (v === null || v === undefined) return "";
  let s = typeof v === "object" ? JSON.stringify(v) : String(v);
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$/.test(s)) s = s.replace("+00:00", "Z");
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

const text = (msg: string, status: number) => new Response(msg + "\n", { status, headers: { "Content-Type": "text/plain; charset=utf-8" } });

export async function GET(req: Request) {
  const table = new URL(req.url).searchParams.get("table") ?? "";
  if (!/^[a-z0-9_]{3,64}$/.test(table)) return text("table must be an ERW table name", 400);
  try {
    const cat = (await (await get(`catalogue?select=table_name,in_live_set,columns,license&table_name=eq.${table}`)).json()) as {
      in_live_set: string; columns: string | null; license: string;
    }[];
    if (!cat.length || cat[0].license !== "public") return text(`${table} is not a public ERW table`, 404);
    if (cat[0].in_live_set !== "yes" || !cat[0].columns) {
      return text(`${table} is not in the site's live set. Every table is on Redivis (${site.redivis.url}); version 1 is pending release.`, 404);
    }
    const columns = JSON.parse(cat[0].columns) as string[];
    const shape = columns[0] === "entity_id" ? "entities" : columns[0] === "event_id" ? "events" : "series";
    const countRes = await get(`${shape}?select=table_name&table_name=eq.${table}&limit=1`, { Prefer: "count=exact" });
    const n = Number((countRes.headers.get("content-range") ?? "").split("/")[1]);
    if (!Number.isFinite(n)) return text(`${table}: Supabase gave no row count`, 502);
    if (n > MAX_ROWS) {
      return text(`${table} holds ${n.toLocaleString("en-US")} rows in the live set, more than the ${MAX_ROWS.toLocaleString("en-US")} a download allows. `
        + `Every table is on Redivis (${site.redivis.url}); version 1 is pending release.`, 413);
    }
    const hdr = (await (await get(`headers?select=line&table_name=eq.${table}&order=line_no`)).json()) as { line: string }[];
    const std = STD[shape];
    const select = shape === "series" ? std.join(",") : [...std, "extra"].join(",");
    const enc = new TextEncoder();
    const stream = new ReadableStream<Uint8Array>({
      async start(ctl) {
        try {
          ctl.enqueue(enc.encode(hdr.map((h) => `# ${h.line}\n`).join("")
            + `# Downloaded from the ERW site's live set (Supabase) at ${new Date().toISOString().replace(/\.\d{3}Z$/, "Z")}: ${n} rows.\n`
            + columns.join(",") + "\n"));
          for (let off = 0; off < n; off += PAGE) {
            const rows = (await (await get(`${shape}?select=${select}&table_name=eq.${table}&order=${ORDER[shape]}&limit=${PAGE}&offset=${off}`)).json()) as Record<string, unknown>[];
            ctl.enqueue(enc.encode(rows.map((r) => columns.map((c) => cell(c in r ? r[c] : (r.extra as Record<string, unknown> | null)?.[c])).join(",")).join("\n") + (rows.length ? "\n" : "")));
            if (rows.length < PAGE) break;
          }
          ctl.close();
        } catch (e) {
          ctl.error(e);
        }
      },
    });
    return new Response(stream, {
      headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="${table}.csv"`, "Cache-Control": "public, max-age=3600" },
    });
  } catch (e) {
    return text(`the download failed: ${(e as Error).message}`, 502);
  }
}
