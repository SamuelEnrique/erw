// Energy Research Warehouse (ERW) site: GET /api/entity?table=<table>&id=<entity_id>, one row
// of a public entities table in the live set, for the project map's click card (session 16).
// Reads Supabase with the anon key on the server (public rows only); writes nothing.
import { NextResponse } from "next/server";
import { entity } from "@/lib/data";

export const runtime = "nodejs";

// only the tables the map reads; anything else is refused
const TABLES = new Set(["energy_projects", "datacenter_projects"]);

export async function GET(req: Request) {
  const url = new URL(req.url);
  const table = url.searchParams.get("table") ?? "";
  const id = url.searchParams.get("id") ?? "";
  if (!TABLES.has(table) || !id || id.length > 200) {
    return NextResponse.json({ error: "table must be energy_projects or datacenter_projects, with an id" }, { status: 400 });
  }
  try {
    const row = await entity(table, id);
    if (!row) return NextResponse.json({ error: `${id} is not in ${table} in the live set` }, { status: 404 });
    return NextResponse.json(row, { headers: { "Cache-Control": "public, max-age=3600" } });
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 502 });
  }
}
