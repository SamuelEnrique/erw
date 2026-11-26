// Session 10236: the home page (app/page.tsx), the tour (app/tour/page.tsx and each stop of app/tour/[stop]/page.tsx)
// and the Thesis Builder's report tabs (components/thesis/Report.tsx, from a saved run of 6 October 2026) drawn to HTML
// with the site's own code, so the audit reads what a visitor is printed and a words branch's sentences are read as
// drawn. Run from site/:
//   node --import ../runs/c10236/register.mjs ../runs/c10236/draw.mjs <out prefix> [needle ...]
// The database reads are answered from ../runs/c10236/home_rows.json (restate.py and make_latest.py: rows of the main
// copy's tables); no request leaves the machine. Prints each drawing's size and whether an em dash is in it; for each
// needle the sentence that holds it, or MISSING (exit 1).
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [prefix, ...needles] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
const R = JSON.parse(fs.readFileSync(path.join(site, "..", "runs", "c10236", "home_rows.json"), "utf-8"));

process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const json = (rows) => new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json", "content-range": `0-${Math.max(0, rows.length - 1)}/${rows.length}` } });
const eq = (q, k) => (q.get(k) ?? "").replace(/^eq\./, "");
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = u.searchParams;
  let rows = [];
  if (u.pathname.endsWith("/latest_prices")) rows = R.latest;
  else if (u.pathname.endsWith("/entities") && eq(q, "table_name") === "storage_capacity") rows = R.storage;
  else if (u.pathname.endsWith("/series")) {
    const t = eq(q, "table_name"), e = eq(q, "entity");
    if (t === "eia930_all_demand" && e === "eia930:ERCO") rows = R.demand;
    else if (t === "eia_fuel_spot_prices") rows = R.fuels[e] ?? [];
    else if (t === "battery_stack_monthly" && e === "ercot:HB_HUBAVG") {
      const like = (q.get("variable") ?? "").replace(/^like\./, "").replace(/\*$/, "");
      rows = R.stack.filter((r) => r.variable.startsWith(like));
    }
  }
  const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 100000);
  return json(rows.slice(off, off + lim));
};
Date.now = () => Date.parse("2026-11-26T12:00:00Z");

async function resolveTree(node) {
  if (node == null || typeof node !== "object") return node;
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  if (typeof node.type === "function" && node.type.constructor?.name === "AsyncFunction") return resolveTree(await node.type(node.props));
  const kids = node.props?.children;
  if (kids === undefined) return node;
  const rk = await resolveTree(kids);
  return React.cloneElement(node, undefined, ...(Array.isArray(rk) ? rk : [rk]));
}
const ent = (s) => s.replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&ldquo;|&rdquo;/g, '"');
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

let text = "";
const keep = (name, html) => {
  fs.writeFileSync(`${prefix}_${name}.html`, html);
  const t = words(html);
  fs.writeFileSync(`${prefix}_${name}.txt`, t);
  text += " " + t;
  const titles = Array.from(new Set(Array.from(html.matchAll(/title="([^"]*)"/g), (m) => ent(m[1]))));
  text += " " + titles.join(". ");
  console.log(`${name}: ${html.length} bytes drawn; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
};

const draw = async (el) => renderToStaticMarkup(await resolveTree(el));

const Home = (await imp("app/page.tsx")).default;
keep("home", await draw(React.createElement(Home)));

const Tour = (await imp("app/tour/page.tsx")).default;
keep("tour", await draw(React.createElement(Tour)));
const { STOPS } = await imp("lib/tour.ts");
const Stop = (await imp("app/tour/[stop]/page.tsx")).default;
for (let n = 1; n <= STOPS.length; n++) keep(`stop${n}`, await draw(React.createElement(Stop, { params: Promise.resolve({ stop: String(n) }) })));

// the Thesis Builder's report tabs from a saved run (version 1, written 6 October 2026 before the market run)
const dir = path.join(process.env.ERW_MAIN_OUTPUT ?? "", "thesis_state");
if (process.env.ERW_MAIN_OUTPUT && fs.existsSync(dir)) {
  const { ReportTabs } = await imp("components/thesis/Report.tsx");
  const f = fs.readdirSync(dir).sort()[0];
  const s = JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8"));
  const run = { run_id: s.run_id, niche: s.niche, stage: s.stage, geography: s.geography, status: "done", note: "", requested_at: s.report.built, started_at: null, finished_at: null,
    report: s.report, pitchbook_request: null, pitchbook_key: null, pitchbook: null, pitchbook_received_at: null };
  for (const tab of ["scope", "trends", "landscape", "funnel", "capital", "risks"]) {
    try { keep(`thesis_${tab}`, await draw(React.createElement(ReportTabs, { run, choice: { run: s.run_id, tab } }))); }
    catch (e) { console.log(`thesis_${tab}: not drawn (${e.message.slice(0, 160)})`); }
  }
}

let fail = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { console.log(`MISSING: ${n}`); fail = 1; continue; }
  const a = Math.max(0, text.lastIndexOf(". ", i) + 2), b = text.indexOf(". ", i + n.length);
  console.log(`FOUND: ${text.slice(a, b < 0 ? i + n.length + 80 : b + 1)}`);
}
process.exitCode = fail;
