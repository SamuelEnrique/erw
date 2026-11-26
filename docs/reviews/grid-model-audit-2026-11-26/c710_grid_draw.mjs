// Session 10205 (Grid audit): the Lower 48's and PJM's Now, Exchange and Clean blocks drawn to HTML with the site's own
// components, no build and no database: every read of the site's REST layer is answered from runs/c710_grid/fixture.json
// (rows of the main copy's tables, read only); every other request is refused, so the exchange falls back to the
// committed snapshot. Writes the visible text of each block, one file each, to OUT_DIR.
//   cd site && node --import ./scripts/tsx-register.mjs ../runs/c710_grid_draw.mjs ../runs/c710_grid
import fs from "node:fs";
import path from "node:path";
const { prerenderToNodeStream } = await import("../site/node_modules/react-dom/static.js");

const outDir = process.argv[2];
const fx = JSON.parse(fs.readFileSync(path.join(outDir, "fixture.json"), "utf-8"));
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const asked = [];
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  if (!u.pathname.endsWith("/series")) { asked.push(`refused ${u.pathname}`); return new Response("stand-in: not held", { status: 404 }); }
  const q = u.searchParams;
  const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
  const ent = q.get("entity") ?? "";
  const ents = ent.startsWith("eq.") ? new Set([ent.slice(3)]) : ent.startsWith("in.(") ? new Set(ent.slice(4, -1).split(",").map((s) => s.replace(/"/g, ""))) : null;
  const v = q.get("variable") ?? "";
  const vars = v.startsWith("eq.") ? new Set([v.slice(3)]) : v.startsWith("in.(") ? new Set(v.slice(4, -1).split(",")) : null;
  const all = fx[name];
  if (!all) { asked.push(`refused ${name}`); return new Response("stand-in: not held", { status: 404 }); }
  const rows = all.filter((r) => (!ents || ents.has(r.entity)) && (!vars || vars.has(r.variable)));
  const limit = Number(q.get("limit") ?? 100000), offset = Number(q.get("offset") ?? 0);
  asked.push(`${name} ${ent} ${v}: ${rows.length}`);
  return new Response(JSON.stringify(rows.slice(offset, offset + limit).map((r) => ({ ...r, unit: "", freq: "PT1H" }))), { status: 200, headers: { "content-type": "application/json" } });
};
console.error = () => {};

async function html(el) {
  const { prelude } = await prerenderToNodeStream(el);
  let s = "";
  for await (const c of prelude) s += c;
  return s;
}
const text = (h) => h.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;|&apos;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();

const { GRID_CHOICES } = await import("../site/lib/gridtool.ts");
const { NowView } = await import("../site/components/grid/NowView.tsx");
const { ExchangeView } = await import("../site/components/grid/ExchangeView.tsx");
const { EmissionsParts } = await import("../site/components/grid/Emissions.tsx");
const React = (await import("../site/node_modules/react/index.js")).default;
for (const slug of ["us48", "pjm"]) {
  const grid = GRID_CHOICES.find((g) => g.slug === slug);
  for (const [name, el] of [["now", React.createElement(NowView, { grid, cfg: null, data: null })], ["exchange", React.createElement(ExchangeView, { grid })],
    ["clean", React.createElement(EmissionsParts, { focus: `eia930:${grid.ba}`, grid: slug })]]) {
    try {
      const h = await html(el);
      fs.writeFileSync(path.join(outDir, `draw_${slug}_${name}.txt`), text(h) + "\n");
      console.log(`${slug} ${name}: ${h.length} bytes`);
    } catch (e) {
      console.log(`${slug} ${name}: failed ${String(e).slice(0, 300)}`);
    }
  }
}
fs.writeFileSync(path.join(outDir, "draw_asked.txt"), asked.join("\n") + "\n");
process.exitCode = 0;
