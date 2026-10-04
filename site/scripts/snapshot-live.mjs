// Energy Research Warehouse (ERW) site: a snapshot of the live pages, and the comparison of two snapshots.
//
//   node scripts/snapshot-live.mjs take <name> [base-url]     reads every live page as a visitor, writes runs/snapshots/<name>/
//   node scripts/snapshot-live.mjs compare <before> <after>   lists every difference; exit 0 none, 1 some, 2 bad input
//   node scripts/snapshot-live.mjs pages                      prints the pages it reads
//
// The rule it serves (CLAUDE.md, "The live pages and the freeze"): no deploy without a snapshot of the live pages before
// and after, every difference listed. Session 76 wrote the first version as runs/session76/snapshot.mjs on the personal
// laptop; runs/ is not in git, so session 77 rewrote it here from that session's report, on the old laptop.
//
// A page is read with a plain request and no cookie, as a visitor's browser asks for it. For each page the snapshot keeps:
//   <n>.html           the response as served
//   <n>.numbers.json   every checked number: data-check (the table and key it was read from), data-raw (the value as
//                      read) and the text shown (components/Num.tsx; the same marks scripts/check-values.mjs reads)
//   <n>.text.txt       the visible text, one block per line, scripts and styles removed
// and index.json names the pages, the base address, the time and each response's status.
//
// The comparison reports, page by page: a status that changed; a checked number whose key exists on one side only; a key
// whose raw value or shown text differs; and every line of visible text on one side only. It does not judge a difference:
// the latest prices and their times move by themselves, and the person deploying says which differences were expected.
// Requests have a hard timeout (SNAPSHOT_REQUEST_S, default 60 s); a page that cannot be read fails the run with exit 1,
// and a snapshot with a failed page is not written as complete (index.json says complete: false).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(here, "..", "..");
const OUT = path.join(ROOT, "runs", "snapshots");
const PRODUCTION = "https://erw-flame.vercel.app";
const REQUEST_MS = Number(process.env.SNAPSHOT_REQUEST_S ?? 60) * 1000;

// The live pages (site/lib/release.ts) as a visitor sees them: the five tools and About, with the battery page for both
// grids at 2, 4 and 8 hours under both strategies: the 18 pages session 76 compared. Session 82 added California's solar
// and wind on the seller tab (the default page is Texas's solar, and the hour correction of that session moved only
// California's): 20 pages. New pages go at the end, so an older snapshot's files keep their numbers. Session 90 added the
// live pages that hold no tool: /terms, which prints the source registry, and the four methods pages the tools link to.
// That session's deploy changed two of them (the MISO pause's note in the registry and in one method) and the script did
// not look: 25 pages.
const BATTERY = ["ercot", "caiso"].flatMap((g) => [2, 4, 8].flatMap((d) => ["foresight", "dayahead"].map((s) => `/cost-of-power/battery?grid=${g}&dur=${d}&strat=${s}`)));
const SELLER = ["/cost-of-power/seller?iso=caiso&asset=solar", "/cost-of-power/seller?iso=caiso&asset=wind"];
const WORDS = ["/terms", "/data/methods/battery_stack", "/data/methods/cost_of_power", "/data/methods/grid_network", "/data/methods/storage"];
export const LIVE_PAGES = ["/", "/about", "/storage", "/cost-of-power/seller", "/network", "/cost-of-power/battery", ...BATTERY, ...SELLER, ...WORDS];

/** The paths release.ts marks live, read from the file as text (it has no imports, by design). */
function liveInRelease() {
  const src = fs.readFileSync(path.join(here, "..", "lib", "release.ts"), "utf8");
  return [...src.matchAll(/^\s*"(\/[^"]*)":\s*"live"/gm)].map((m) => m[1]);
}

const decode = (s) => s.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"')
  .replace(/&#x27;|&#39;|&apos;/g, "'").replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16))).replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)));

export function numbers(html) {
  const re = /<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g;
  return [...html.matchAll(re)].map((m) => ({ key: decode(m[1]), raw: decode(m[2]), text: decode(m[3].replace(/<[^>]+>/g, "")).trim() }));
}

export function visibleText(html) {
  const body = html.replace(/<script[\s\S]*?<\/script>/gi, "").replace(/<style[\s\S]*?<\/style>/gi, "").replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<template[\s\S]*?<\/template>/gi, "").replace(/<head[\s\S]*?<\/head>/i, "");
  const blocks = body.replace(/<\/(p|div|li|dd|dt|tr|h[1-6]|section|article|header|footer|nav|table|ul|ol|dl|details|summary|figure|figcaption|label|option|button)>|<br\s*\/?>/gi, "\n");
  return blocks.split("\n").map((l) => decode(l.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim()).filter(Boolean);
}

const fileOf = (i) => String(i + 1).padStart(2, "0");

async function take(name, base) {
  if (!/^[A-Za-z0-9_.-]+$/.test(name)) { console.error("snapshot name: letters, digits, dot, dash and underscore only"); process.exit(2); }
  const dir = path.join(OUT, name);
  if (fs.existsSync(dir)) { console.error(`${path.relative(ROOT, dir)} exists; a snapshot is never overwritten, choose another name`); process.exit(2); }
  const live = liveInRelease();
  const notLive = LIVE_PAGES.filter((p) => !live.includes(p.split("?")[0]));
  if (notLive.length) { console.error(`not live in lib/release.ts: ${notLive.join(", ")}`); process.exit(2); }
  fs.mkdirSync(dir, { recursive: true });
  const index = { name, base, taken_utc: new Date().toISOString(), complete: false, pages: [] };
  let failed = 0, n = 0;
  for (const [i, page] of LIVE_PAGES.entries()) {
    const entry = { page, file: fileOf(i) };
    try {
      const res = await fetch(base + page, { redirect: "manual", signal: AbortSignal.timeout(REQUEST_MS), headers: { "cache-control": "no-cache" } });
      const html = await res.text();
      const nums = numbers(html), text = visibleText(html);
      Object.assign(entry, { status: res.status, bytes: html.length, numbers: nums.length, lines: text.length });
      fs.writeFileSync(path.join(dir, `${entry.file}.html`), html);
      fs.writeFileSync(path.join(dir, `${entry.file}.numbers.json`), JSON.stringify(nums, null, 1));
      fs.writeFileSync(path.join(dir, `${entry.file}.text.txt`), text.join("\n") + "\n");
      if (res.status !== 200) failed++;
      n += nums.length;
      console.log(`${res.status} ${page}: ${nums.length} checked numbers, ${text.length} lines of text`);
    } catch (e) {
      failed++;
      entry.error = String(e?.message ?? e);
      console.error(`FAILED ${page}: ${entry.error}`);
    }
    index.pages.push(entry);
  }
  index.complete = failed === 0;
  fs.writeFileSync(path.join(dir, "index.json"), JSON.stringify(index, null, 1));
  console.log(`${name}: ${LIVE_PAGES.length} pages, ${n} checked numbers, ${failed} failed, at ${index.taken_utc} from ${base} -> ${path.relative(ROOT, dir)}`);
  process.exit(failed ? 1 : 0);
}

function load(name) {
  const dir = path.join(OUT, name), f = path.join(dir, "index.json");
  if (!fs.existsSync(f)) { console.error(`no snapshot ${path.relative(ROOT, dir)}`); process.exit(2); }
  const index = JSON.parse(fs.readFileSync(f, "utf8"));
  if (!index.complete) { console.error(`snapshot ${name} is not complete (a page failed when it was taken)`); process.exit(2); }
  const pages = {};
  for (const p of index.pages) {
    pages[p.page] = { status: p.status, nums: JSON.parse(fs.readFileSync(path.join(dir, `${p.file}.numbers.json`), "utf8")),
      text: fs.readFileSync(path.join(dir, `${p.file}.text.txt`), "utf8").split("\n").filter(Boolean) };
  }
  return { index, pages };
}

const byKey = (nums) => { const m = new Map(); for (const x of nums) m.set(x.key, [...(m.get(x.key) ?? []), `${x.raw} (shown ${x.text})`]); return m; };
const countOf = (lines) => { const m = new Map(); for (const l of lines) m.set(l, (m.get(l) ?? 0) + 1); return m; };

function compare(a, b) {
  const A = load(a), B = load(b);
  console.log(`before: ${a}, ${A.index.taken_utc}, ${A.index.base}`);
  console.log(`after:  ${b}, ${B.index.taken_utc}, ${B.index.base}`);
  let diffs = 0, checked = 0;
  for (const page of [...new Set([...Object.keys(A.pages), ...Object.keys(B.pages)])]) {
    const pa = A.pages[page], pb = B.pages[page], out = [];
    if (!pa || !pb) { out.push(`page only in ${pa ? "before" : "after"}`); }
    else {
      if (pa.status !== pb.status) out.push(`status ${pa.status} became ${pb.status}`);
      const ka = byKey(pa.nums), kb = byKey(pb.nums);
      checked += ka.size;
      for (const k of new Set([...ka.keys(), ...kb.keys()])) {
        const va = ka.get(k), vb = kb.get(k);
        if (!va) out.push(`number, new key: ${k} = ${vb.join("; ")}`);
        else if (!vb) out.push(`number, key gone: ${k} was ${va.join("; ")}`);
        else if (va.join("; ") !== vb.join("; ")) out.push(`number, changed: ${k}: ${va.join("; ")} became ${vb.join("; ")}`);
      }
      const ta = countOf(pa.text), tb = countOf(pb.text);
      for (const [l, c] of ta) if ((tb.get(l) ?? 0) < c) out.push(`text, before only: ${l}`);
      for (const [l, c] of tb) if ((ta.get(l) ?? 0) < c) out.push(`text, after only: ${l}`);
    }
    console.log(`${page}: ${out.length} difference${out.length === 1 ? "" : "s"}`);
    for (const o of out) console.log(`  ${o}`);
    diffs += out.length;
  }
  console.log(`${diffs} difference${diffs === 1 ? "" : "s"} in all; ${checked} checked number keys in the before snapshot`);
  process.exit(diffs ? 1 : 0);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const [cmd, x, y] = process.argv.slice(2);
  if (cmd === "take" && x) await take(x, (y ?? PRODUCTION).replace(/\/$/, ""));
  else if (cmd === "compare" && x && y) compare(x, y);
  else if (cmd === "pages") { for (const p of LIVE_PAGES) console.log(p); }
  else { console.error("usage: snapshot-live.mjs take <name> [base-url] | compare <before> <after> | pages"); process.exit(2); }
}
