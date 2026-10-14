// Energy Research Warehouse (ERW) site, session 266: the Grid tool's replication file against the page, value by value.
//
//   node scripts/check-grid-replication.mjs <base-url> [csv]
//
// Runs public/grid/erw_2026_grid_replication.py on the file (default: the one in public/grid) and compares each line it
// prints with the number the page shows for it, as the page renders it on <base-url>: the Now view of each of the seven
// ISO grids (net|ties, net|export or net|import and net|lag, read from their data-check keys), the Network view's line
// under the chart (data-network-lag, the count of balancing authorities, data-newest-complete), and, in a browser, the
// gravity shape's circles (data-gen, data-net, data-share, data-r, data-d). Prints one line a value; exit 1 on any
// difference, 2 on bad input. The file and the page must be read from the same snapshot: write the file just before.
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env, withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const [base, csvArg] = process.argv.slice(2);
if (!base) { console.log("usage: check-grid-replication.mjs <base-url> [csv]"); process.exit(2); }
const py = process.env.PYTHON || "python";
const script = path.join(here, "..", "public", "grid", "erw_2026_grid_replication.py");
const lines = execFileSync(py, [script, ...(csvArg ? [csvArg] : [])], { encoding: "utf-8" }).split(/\r?\n/).filter(Boolean);
const mirror = Object.fromEntries(lines.map((l) => l.split(" = ")));
const SLUG = { CISO: "caiso", ERCO: "ercot", ISNE: "isone", MISO: "miso", NYIS: "nyiso", PJM: "pjm", SWPP: "spp" };
let bad = 0, n = 0;
const same = (what, ours, page) => {
  n += 1;
  const ok = page !== undefined && page !== null && (Number.isFinite(Number(ours)) && Number.isFinite(Number(page)) ? Math.abs(Number(ours) - Number(page)) < 1e-6 * Math.max(1, Math.abs(Number(ours))) : String(ours) === String(page));
  if (!ok) bad += 1;
  console.log(`${ok ? "same" : "DIFFERENT"}  ${what}: replication ${ours}, page ${page}`);
};
const checks = (html) => Object.fromEntries([...html.matchAll(/data-check="([^"]+)" data-raw="([^"]*)"/g)].map((m) => [m[1].replaceAll("&amp;", "&"), m[2]]));

// the pages are in review (lib/release.ts): read with the internal cookie, as check-values reads them
const tok = env("INTERNAL_COSTS_TOKEN");
let cookie = "";
if (tok) { const u = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(tok)}`, { redirect: "manual" }); cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; "); }
if (!cookie) { console.log("no internal cookie: the pages in review cannot be read"); process.exit(2); }
const get = async (p) => { const r = await fetch(`${base}${p}`, { headers: cookie ? { cookie } : {} }); return r.text(); };
const hour = mirror.hour_shown, built = mirror.snapshot_built;
for (const [ba, slug] of Object.entries(SLUG)) {
  const k = checks(await get(`/grid?grid=${slug}&view=now`));
  same(`${ba} ties reporting (Now)`, mirror[`ties_${ba}`], k[`net|ties|${ba}|${hour}`]);
  const net = Number(mirror[`net_import_${ba}`]);
  same(`${ba} net ${net > 0 ? "import" : "export"}, MW (Now)`, Math.abs(net), net > 0 ? k[`net|import|${ba}|${hour}`] : k[`net|export|${ba}|${hour}`]);
  same(`${ba} the hour's lag, hours (Now)`, mirror.lag_hours, k[`net|lag|${hour}|${built}`]);
}
const nv = await get("/grid?grid=ercot&view=network");
same("the hour shown (Network)", hour, (nv.match(/data-newest-complete="([^"]+)"/) ?? [])[1]);
same("the lag, hours (Network, under the chart)", mirror.lag_hours, (nv.match(/data-network-lag="([^"]+)"/) ?? [])[1]);
same("balancing authorities drawn (Network)", mirror.nodes, (nv.match(/The (?:<!-- -->)?(\d+)(?:<!-- -->)? balancing authorities that report/) ?? [])[1]);

const code = await withBrowser(async ({ go, evaluate, wait, unlock }) => {
  await unlock(base);
  await go(`${base}/grid?grid=ercot&view=network&shape=gravity`);
  await wait(`document.querySelectorAll('[data-gravity-grid][data-r]').length === 7`, 30000, "the gravity shape");
  const got = await evaluate(`JSON.stringify([...document.querySelectorAll('[data-gravity-grid][data-r]')].map((g) => ({ id: g.getAttribute('data-gravity-grid'), gen: g.getAttribute('data-gen'),
    net: g.getAttribute('data-net'), share: g.getAttribute('data-share'), r: g.getAttribute('data-r'), d: g.getAttribute('data-d') })))`);
  const center = await evaluate(`document.querySelector('[data-gravity-center]')?.getAttribute('data-gravity-center')`);
  same("generation US48, MW (Gravity)", mirror.generation_US48, center);
  for (const g of JSON.parse(got)) {
    same(`${g.id} generation, MW (Gravity)`, mirror[`generation_${g.id}`], g.gen);
    same(`${g.id} net imports, MW (Gravity)`, mirror[`net_import_${g.id}`], g.net);
    same(`${g.id} share of generation (Gravity)`, Number(mirror[`gravity_share_${g.id}`]).toFixed(6), Number(g.share).toFixed(6));
    same(`${g.id} radius (Gravity)`, mirror[`gravity_r_${g.id}`], g.r);
    same(`${g.id} distance from the center (Gravity)`, mirror[`gravity_d_${g.id}`], g.d);
  }
  return 0;
});
if (code === null) console.log("the gravity shape: not proven here (no browser on this machine)");
console.log(`${n} values compared, ${bad} different`);
process.exit(bad ? 1 : 0);
