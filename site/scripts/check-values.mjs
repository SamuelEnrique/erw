// Energy Research Warehouse (ERW) site: check rendered numbers against direct Supabase queries.
//
//   npm run build && npm start           (the site on http://localhost:3000)
//   node scripts/check-values.mjs [base-url]
//
// Every number the pages render through components/Num.tsx carries data-check (the Supabase
// table and key it was read from) and data-raw (the value as read). For each one, this script
// runs its own query against Supabase's REST API with SUPABASE_URL and SUPABASE_ANON_KEY (from the
// environment or site/.env.local), independent of lib/, and checks:
//   1. the value Supabase returns equals data-raw;
//   2. the text on the page equals data-raw rounded as displayed (2 decimals, or a whole count).
// Prints one line per value and a summary; exits 1 if any value fails or fewer than ten were checked.
//
// Session 268, the floor a page (sessions 241a and 241b saw /cost-of-power carry 16 keys on a cold cache where it
// carries 76, and pass): scripts/check-values-floor.json holds, for each page of a passing full run, the smaller of ten
// and the keys it carried. A page read with fewer keys than its floor fails, with a line that says so. A page not in
// the file has no floor. CHECK_VALUES_WRITE_FLOOR=1 writes the file again from a run that passes in full (no
// CHECK_VALUES_PAGES); a page added to the list gets its floor that way. Session 403: or from a restricted run that
// passes in full (CHECK_VALUES_PAGES set), which sets the floors of the pages it read and leaves every other line.
//
// Session 72: it cannot hang. Every request has a hard timeout (CHECK_VALUES_REQUEST_S, default 60 s) and the whole run
// one too (CHECK_VALUES_TIMEOUT_MIN, default 15 minutes): past it the run fails, loudly, with exit 1 (session 71's third
// run hung for 70 minutes on the network). And it does not flake on the latest prices: their key carries the interval
// the page shows (latest_prices|<entity>|<variable>|<ts_utc>). Supabase's latest_prices holds one row per entity, the
// newest interval, and no earlier one anywhere. So: the same interval in Supabase, the values must be equal; a newer
// interval in Supabase (the page was cached before the 15-minute refresh), the key is "superseded", reported on its own
// line and in the summary, and passes only if the page's interval is at most 45 minutes behind Supabase's (the page's
// 15-minute cache, the refresh and the run's own length); any other case fails. No key is dropped.
//
// Session 430: it finishes on a slow database. The full run passed its 15-minute limit three times on 21 October 2026
// and so reported nothing. The pages are now read one at a time, in batches (CHECK_VALUES_BATCH, default 10), each under
// a limit of its own (CHECK_VALUES_PAGE_S, default 300 s) that aborts the page's requests; a page that timed out is tried
// once more after the last page. At the run's limit (CHECK_VALUES_TIMEOUT_MIN) no page starts, and the run reports what
// it read and lists every page it did not ("not read | <page> | why | its numbers and its floor are not judged"). Exit
// codes: 0 every page read and every value and floor passed; 1 a value differs, a floor fails, a page or a query failed
// for any reason but slowness, or fewer than ten values; 3 every value read passed but some pages were not read (never 0:
// no landing takes an incomplete run for a pass). After each batch the run writes its state (CHECK_VALUES_STATE, default
// runs/check-values/state.json); CHECK_VALUES_RESUME=1 keeps the pages an earlier run of the same base and the same
// CHECK_VALUES_PAGES read and reads only the others. CHECK_VALUES_WRITE_FLOOR=1 writes floors only from a run (resumed or
// not) that read every page and passed. scripts/check-values-run.mjs holds the scheduling; its test is
// scripts/test-check-values-run.mjs.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { unlockPost } from "./browser.mjs";   // session 301: the internal view by the form's door, no token in an address
import * as ED from "./event-dates.mjs";   // session 369: the date of every event-page figure (todo 008)
import * as RUN from "./check-values-run.mjs";   // session 430: the pages in batches, each under its own timeout

const REQUEST_MS = Number(process.env.CHECK_VALUES_REQUEST_S ?? 60) * 1000;
const RUN_MIN = Number(process.env.CHECK_VALUES_TIMEOUT_MIN ?? 15);
const LATEST_LAG_MIN = 45;
// Session 430: one page's limit (CHECK_VALUES_PAGE_S, default 300 s) and the pages a batch (CHECK_VALUES_BATCH, default 10)
const PAGE_S = Number(process.env.CHECK_VALUES_PAGE_S ?? 300);
const BATCH = Number(process.env.CHECK_VALUES_BATCH ?? 10);
const RUN_START = Date.now();
let pageSignal = null;   // session 430: the page being read; its timeout aborts its requests
{
  const plain = globalThis.fetch;
  globalThis.fetch = (url, opts = {}) => {
    const own = opts.signal ?? AbortSignal.timeout(REQUEST_MS);
    return plain(url, { ...opts, signal: pageSignal ? AbortSignal.any([own, pageSignal]) : own });
  };
  // session 430: at the run's limit no page starts and the run reports what it read (scripts/check-values-run.mjs); this
  // stop, five minutes later, is only for a run that hangs past it all the same
  setTimeout(() => {
    console.error(`check-values FAILED: the run passed its ${RUN_MIN}-minute limit (CHECK_VALUES_TIMEOUT_MIN) by five minutes and did not stop; nothing is reported as checked`);
    process.exit(1);
  }, (RUN_MIN + 5) * 60 * 1000).unref();
}

const here = path.dirname(fileURLToPath(import.meta.url));
const base = process.argv[2] ?? "http://localhost:3000";
const FLOOR_FILE = path.join(here, "check-values-floor.json");
const FLOOR = fs.existsSync(FLOOR_FILE) ? JSON.parse(fs.readFileSync(FLOOR_FILE, "utf-8")).floor : {};
// Session 178: CHECK_VALUES_PAGES=<prefix>[,<prefix>] reads only the pages whose address starts with one of them: one
// tool's checks on their own (the weekly brief is then not parsed, and the summary says the run was restricted). The
// gate of a landing is the full run, with the variable unset.
const ONLY = (process.env.CHECK_VALUES_PAGES ?? "").split(",").map((v) => v.trim()).filter(Boolean);
const wanted = (page) => !ONLY.length || ONLY.some((pre) => page.startsWith(pre));
const PAGES = ["/", "/board", "/emissions", "/storage", "/prices", "/prices/ercot%3AHB_HUBAVG", "/data", "/prices?tab=ercot", "/deals", "/deals?tab=tracker", "/deals?view=comparables", "/deals?tab=companies", "/grid", "/map", "/datacenters", "/datacenters?view=grids", "/roundup",
  // session 18
  "/mix", "/mix?ba=erco&state=TX", "/curtailment", "/demand?view=consumption",
  // session 404: the demand growth explorer (the default, ERCOT's whole-year average; the peak with the Lower 48's missing
  // peak; the year so far in PJM; a calendar month and a local hour of the day, whose growth sits on the last whole year)
  "/explore/demand-growth", "/explore/demand-growth?grid=us48&window=peak", "/explore/demand-growth?grid=pjm&window=ytd",
  "/explore/demand-growth?grid=caiso&window=m08", "/explore/demand-growth?grid=ercot&window=h17",
  // session 332: every action's significance (event|policy_actions|<id>|significance)
  "/policy",
  // session 471: the licensing record's short reading (lic|held|..., lic|verdict|...), recomputed from warehouse/metadata
  "/data/licenses",
  // session 19
  // session 35: the seven grid pages
  "/grid/ercot", "/grid/caiso", "/grid/pjm", "/grid/nyiso", "/grid/isone", "/grid/miso", "/grid/spp",
  // session 36B: the Historical Event Analyzer
  "/events/uri-2021",
  // session 36C
  "/events/covid-2020",
  // session 37: the cost-of-power model (session 138: what the tab showed until then is the page's view "Grid by grid")
  "/cost-of-power?view=grids",
  // session 228: "Your load", the page's own view, with the three answers' keys (dc|...), flat and off in 100 hours
  "/cost-of-power", "/cost-of-power?run=hours",
  "/cost-of-power?grid=caiso",  // session 280: CAISO's hub counts (scarcity_hours_by_grid) and its list of statements (large_load_public)
  // session 700: the All grids tab (lib/siting.ts), its hub and zone rows and its ERCOT nodes
  "/cost-of-power?view=allgrids", "/cost-of-power?view=allgrids&rows=nodes",
  // session 702: the three other profiles, each at its defaults
  "/cost-of-power?view=allgrids&profile=flexible", "/cost-of-power?view=allgrids&profile=electrolyzer", "/cost-of-power?view=allgrids&profile=industry",
  // session 710: the screen sorted by the all-in figure with A and B set (ERCOT's hub average against CAISO's SP15), and the
  // node list sorted by energy, largest first
  "/cost-of-power?view=allgrids&sort=allin&a=ercot%3AHB_HUBAVG&b=nyiso%3AN.Y.C.", "/cost-of-power?view=allgrids&rows=nodes&nsort=energy&ndir=desc",
  // session 711: a node's panel
  "/cost-of-power?view=allgrids&rows=nodes&node=ercot%3A7RNCHSLR_ALL",
  // session 719: the tracker's link's form, a row as A and the facility's MW as the load
  "/cost-of-power?view=allgrids&mw=1400&a=ercot%3ALZ_NORTH",
  // session 51: the seller's tab, its defaults and three other assets
  // session 347: the economic impact tool, its defaults and three other views (a size, cost, local content and life given)
  "/map?tab=queues", "/map?tab=queues&iso=ercot", "/map?tab=queues&iso=spp",  // session 349: the map's Queues tab (iso_queue_statistics)
  // session 405: the interconnection explorer (the default, CAISO in positions; ERCOT in MW over a window; SPP; a held queue)
  "/explore/interconnection", "/explore/interconnection?queue=ercot&measure=mw&from=2018&to=2025", "/explore/interconnection?queue=spp",
  "/explore/interconnection?queue=nyiso",
  "/impact", "/impact?tech=utility_pv&state=la&mw=200&life=30", "/impact?tech=natural_gas&state=nm&capex=120&local=80", "/impact?tech=geothermal&state=us&life=25",
  "/cost-of-power/seller", "/cost-of-power/seller?asset=battery", "/cost-of-power/seller?asset=peaker", "/cost-of-power/seller?iso=spp&asset=wind",  // session 145: MISO is blank on the page, so the fourth view is SPP's wind
  // session 38: today's level's price range
  "/play/battery", "/play/battery?mode=hard",  // session 63: the simple page and the full game; session 289: one page, three modes (?more=1 redirects)
  // session 39: three more events
  "/events", "/events/caiso-heat-2020", "/events/elliott-2022", "/events/ercot-heat-2023",
  // session 58: CAISO's September 2022 heat
  "/events/caiso-heat-2022",
  // session 64: the January 2025 cold and the June 2025 heat
  "/events/cold-2025", "/events/east-heat-2025",
  "/events/cold-2026",   // session 319
  // session 43: the bill explainer's default bills
  "/learn/bill",
  // session 44: every computed answer of the problem sets
  "/learn/problems/know-your-grid", "/learn/problems/prices-and-your-bill", "/learn/problems/when-the-grid-broke", "/learn/problems/storage-and-taxes",
  // session 55: set E, networks and money
  "/learn/problems/networks-and-money",
  // session 49: the network's default node card (ERCOT)
  "/network",
  // session 72 (session 69's finish): the storage build-out
  // session 239: the merged pages are read at the tabs they became (lib/tabs.ts): /prices?tab=ercot was
  // /explorer/ercot-peak-premium, /demand?view=consumption was /consumption, the three below were /storage/buildout;
  // the tracker, the companies, the owners, the lease tool and the resource map are read too (they were not before)
  "/storage?tab=buildout", "/storage?tab=buildout&grid=ercot&measure=mwh", "/storage?tab=buildout&grid=caiso",
  "/storage?tab=owners", "/severance", "/severance?tab=lease", "/map?tab=resources",
  "/shoulder", "/shoulder?grid=caiso&month=2025-07",  // session 75
  // session 67: what a battery earns: both grids, the three durations, both strategies, another size
  // session 315: the Research tool (every card figure a Num with its card; today's record's figures) and one card's own page
  "/research", "/research/card/batteries_lunch_grids", "/research/card/gas_sets_price",
  "/cost-of-power/battery", "/cost-of-power/battery?grid=ercot&dur=2&strat=foresight", "/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead",
  "/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead", "/cost-of-power/battery?grid=caiso&dur=4&strat=foresight", "/cost-of-power/battery?grid=caiso&dur=2&strat=dayahead",
  "/cost-of-power/battery?grid=caiso&dur=8&strat=foresight&mw=250",
  "/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead",  // session 257: the case the market monitor's fleet is set beside, read from the page's own rows
  // session 297: one non-default setting each of the investment tax credit, the fade method, augmentation and the stress repeats
  // (the page's table keys are the same at these addresses: the four prove the page draws with each set)
  "/cost-of-power/battery?ai=30", "/cost-of-power/battery?ao=1", "/cost-of-power/battery?ao=1&am=5", "/cost-of-power/battery?ax=2",
  // session 60: the Flex Alert scorecard
  "/grid/caiso/alerts",
  // session 237: the Grid tool, one page. Now, Clean and Exchange for each of the eight choices, the Mix and the Network
  // for ERCOT and the Lower 48. The addresses above that redirect into it (/emissions, /grid/<iso>, /mix, /network) stay
  // in the list: each is read through its redirect, as a visitor's old link is
  ...["ercot", "caiso", "pjm", "miso", "nyiso", "isone", "spp", "us48"].flatMap((g) => [`/grid?grid=${g}`, `/grid?grid=${g}&view=clean`, `/grid?grid=${g}&view=exchange`]),
  "/grid?grid=ercot&view=mix", "/grid?grid=us48&view=mix", "/grid?grid=pjm&view=mix&mix=stress", "/grid?grid=ercot&view=network", "/grid?grid=us48&view=network",
  // session 299: the Gravity tab (the network's gravity shape with the exchange blocks under it)
  "/grid?grid=ercot&view=gravity&shape=gravity", "/grid?grid=us48&view=gravity&shape=gravity",
  // session 403: the ERCOT peak premium explorer (the thesis's default; another hub and two years; one month across the
  // years, from the monthly table; Houston's February of Winter Storm Uri against the year before)
  "/explore/ercot-peak-premium", "/explore/ercot-peak-premium?hub=ercot%3AHB_WEST&from=2018&to=2024", "/explore/ercot-peak-premium?month=8",
  "/explore/ercot-peak-premium?hub=ercot%3AHB_HOUSTON&month=2&from=2020&to=2021"];  // (the line ended "// session 46: set D" before session 60)
// session 402: the Energy Digest, today's page and each Digest of the archive whose operating day the live set still holds
// (its ISO prices are kept 35 days: warehouse/supabase/live_set.yaml). Older Digests are traced by scripts/check_digest.py
// against the warehouse's CSVs. A held figure (lib/license.ts) carries no key and is not read here.
PAGES.push("/digest", ...fs.readdirSync(path.join(here, "..", "..", "docs", "digest")).map((f) => /^(\d{4}-\d{2}-\d{2})\.md$/.exec(f)?.[1])
  .filter((d) => d && Date.now() - Date.parse(`${d}T00:00:00Z`) <= 33 * 86_400_000).sort().reverse().map((d) => `/digest/${d}`));
// session 48: the draft report behind the internal token (INTERNAL_COSTS_TOKEN, in .env.local or the environment); left
// out, and said so, where the token is not set (the page answers 404 without it)
const INTERNAL = ["/reports/draft/shape-premium", "/reports/draft/ai-gigawatts"];  // session 62: the AI gigawatts draft
// session 35: the grid pages' config, for their news and datacenter keys (the same file the pages read)
const GRIDS = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "docs", "grids", "grids.json"), "utf-8")).grids;

// Session 408: the routes under app/ that show a warehouse figure (tests/test_session408.py holds the rule: a page whose
// code renders a Num with a check key, or reads Supabase through lib/supabase.ts) and were not read here: the contract
// tracker and the battery fleet's awards. Neither draws its figures through Num yet, so each carries no checked number
// and its floor is 0; it is read so its address answers and is not the in-review page.
PAGES.push("/contracts", "/cost-of-power/battery/awards");
// Session 408: `node scripts/check-values.mjs --list` prints the addresses this script reads ({pages, internal}, JSON)
// and stops, before any variable is read or any request made: tests/test_session408.py holds them against site/app/.
if (process.argv[2] === "--list") {
  console.log(JSON.stringify({ pages: PAGES, internal: INTERNAL }));
  process.exit(0);
}

function env(name) {
  if (process.env[name]) return process.env[name];
  const f = path.join(here, "..", ".env.local");
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

async function q(table, params, countOnly = false) {
  // session 44: a statement timeout (Postgres 57014) is retried twice, after 1 and 3 seconds, as the site's reader does:
  // while the daily run loads Supabase, a query that takes a fraction of a second can pass the anon role's 3 s limit
  let res, body = "";
  for (let attempt = 0; attempt < 3; attempt++) {
    res = await fetch(`${origin}/rest/v1/${table}?${new URLSearchParams(params)}`, {
      headers: { apikey: key, Authorization: `Bearer ${key}`, ...(countOnly ? { Prefer: "count=exact", Range: "0-0" } : {}) },
    });
    if (res.ok) break;
    body = (await res.text()).slice(0, 200);
    if (attempt < 2 && res.status === 500 && body.includes("57014")) { await new Promise((r) => setTimeout(r, attempt ? 3000 : 1000)); continue; }
    break;
  }
  if (!res.ok) throw new Error(`${table}: HTTP ${res.status} ${body}`);
  if (countOnly) return Number(res.headers.get("content-range").split("/")[1]);
  return res.json();
}

async function all(table, params) {
  const out = [];
  for (let off = 0; ; off += 1000) {
    const b = await q(table, { ...params, limit: "1000", offset: String(off) });
    out.push(...b);
    if (b.length < 1000) return out;
  }
}

const impactRows = new Map(), impactAll = new Map();   // session 347: /impact's rows, by technology and state, and by technology
const dcAnswers = new Map();   // session 228: the answers of one address of /cost-of-power, read once
const dcllRows = new Map();
const dcqRows = new Map();   // session 468: the view by grid of /datacenters, one grid's groups read once
let R_statOf = null;
/** Session 471: a CSV file's rows as objects, by its header (quoted cells, doubled quotes inside them). */
function licCsv(text) {
  const rows = [];
  let row = [], cell = "", q = false;
  text = text.replace(/\r\n/g, "\n");
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (ch === '"') q = false;
      else cell += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") { row.push(cell); cell = ""; }
    else if (ch === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; }
    else cell += ch;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const [head, ...body] = rows;   // extra cells (an unquoted comma in the last column) are the last column's
  return body.filter((r) => r.length >= head.length).map((r) => [...r.slice(0, head.length - 1), r.slice(head.length - 1).join(",")])
    .map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}

/** The value Supabase holds for one data-check key. */
async function truth(check) {
  if (R_statOf === null) R_statOf = (await import("../lib/datacenter/answers.ts")).statOf;
  const p = check.split("|");
  if (p[0] === "catalogue") {
    // session 149: the home page counts the tables a visitor may see: public, and not held for a page in review
    // (in_live_set "review": lib/data.ts catalogue(), session 102's review_hold). The check asks Supabase the same
    // question; until now it counted every public row, so it read 113 tables where the page, rightly, showed 97.
    const SEEN = { license: "eq.public", in_live_set: "neq.review" };
    if (p[1] === "count") return q("catalogue", { select: "table_name", ...SEEN }, true);
    if (p[1] === "n_pass") return q("catalogue", { select: "table_name", ...SEEN, validator_status: "eq.pass" }, true);
    if (p[1] === "sum_n_rows") return (await all("catalogue", { select: "n_rows", ...SEEN })).reduce((a, r) => a + Number(r.n_rows), 0);
    if (p[1] === "max_last_run") return (await q("catalogue", { select: "last_run", ...SEEN, order: "last_run.desc.nullslast", limit: "1" }))[0].last_run;
    return (await q("catalogue", { select: "n_rows", table_name: `eq.${p[1]}` }))[0]?.n_rows;
  }
  if (p[0] === "held") {
    // session 500: held|<shape>|<table>|rows, how many rows of a table held by row are held (lib/supabase.ts
    // heldRowsQuery: the row's own license, extra->>row_license, missing or not public); a count, never a row
    return q(p[1], { select: "table_name", table_name: `eq.${p[2]}`, or: "(extra->>row_license.is.null,extra->>row_license.neq.public)" }, true);
  }
  if (p[0] === "latest_prices") {
    const r = (await q("latest_prices", { select: "value,ts_utc", entity: `eq.${p[1]}`, variable: `eq.${p[2]}` }))[0];
    if (p[3] === undefined || r === undefined) return r?.value;  // a key without its interval: the value alone
    return { latest: true, value: r.value, ts: r.ts_utc, pageTs: p[3] };
  }
  // session 54: demand from the hourly network refresh, netsnap|<BA>|demand_mw|<ts>: not in the database (the hourly job
  // never writes it), so it is read from the hourly snapshot itself, the public Storage object, whose demand_recent keeps
  // each ISO BA's last 48 hours (a page cached an hour ago still finds its hour)
  if (p[0] === "netsnap") {
    const res = await fetch(`${origin}/storage/v1/object/public/erw-public/network/grid_network.json`, { cache: "no-store" });
    if (!res.ok) throw new Error(`network snapshot in Storage: HTTP ${res.status}`);
    return (await res.json()).nodes.find((n) => n.id === p[1])?.demand_recent?.[p[3]];
  }
  // session 55: problem set E's network answers, net|ties|<BA>|<hour>, net|maxflow|<BA>|<hour>, net|topexport|<hour>:
  // recomputed by lib/network.ts on the snapshot that holds the hour, the hourly one in Storage first, else the committed
  // data/grid_network.json (the page draws the Storage one unless it is unreachable or older)
  if (p[0] === "net") {
    const N = await import("../lib/network.ts");
    const res = await fetch(`${origin}/${N.NETWORK_OBJECT}`, { cache: "no-store" });
    const stored = res.ok ? await res.json() : null;
    if (stored && N.isSnapshot(stored)) {
      const v = N.netValue(stored, check);
      if (v !== undefined) return v;
    }
    return N.netValue(JSON.parse(fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8")), check);
  }
  // session 58: /grid/caiso's Reliability timeline, awe|days|<type>|<year>: the distinct local days with a CAISO notice of the
  // type in the year (caiso_grid_emergencies, the events table)
  if (p[0] === "awe") {
    const rows = await all("events", { select: "event_date", table_name: "eq.caiso_grid_emergencies", event_type: `eq.${p[2]}`,
      and: `(event_date.gte.${p[3]}-01-01,event_date.lte.${p[3]}-12-31T23:59:59Z)` });
    return new Set(rows.map((r) => String(r.event_date).slice(0, 10))).size;
  }
  // session 44: a derived answer of the problem sets, calc|<op>|<A>|<B>: A and B are check keys with "~" for "|", each
  // recomputed here on its own, then combined
  if (p[0] === "calc") {
    const [, op, a, b] = p;
    const x = Number(await truth(a.replaceAll("~", "|"))), y = Number(await truth(b.replaceAll("~", "|")));
    if (!Number.isFinite(x) || !Number.isFinite(y)) return undefined;
    return op === "ratio" ? x / y : op === "diff" ? x - y : op === "pct" ? (x / y) * 100 : undefined;
  }
  // session 43: the bill explainer's default bills, recomputed here from data/bill_rules.json (California by the tariff's
  // total rates, not its unbundled lines; Texas by its charges), and the wholesale share from cost_of_power_monthly
  // session 315: a finding card's figures, from the card's own JSON (site/data/findings/<card>.json): a callout's text
  // (finding|<card>|callout|<i>|before or after|<grid>) or a cell of its table of estimates (finding|<card>|effect|<row>|<column>|<grid>)
  if (p[0] === "finding") {
    const card = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "findings", `${p[1]}.json`), "utf-8"));
    if (p[2] === "callout") return card.callouts?.[Number(p[3])]?.[p[4]]?.text;
    if (p[2] === "effect") return card.effect_table?.rows?.[Number(p[3])]?.[p[4]];
    return card.numbers?.[p[2]];
  }
  // session 315: the Digest's chart of the day, its record's numbers (docs/digest/charts/<date>.json): digest_chart|<date>|<table>|<key>
  // session 471: /data/licenses' figures, recomputed from the licensing record's own files, not from lib/ or the page's
  // bundle: lic|held|count, lic|held|pub|<publisher> (warehouse/metadata/license_status.csv, the rows "license needed");
  // lic|verdict|both|count and lic|verdict|today_only|count (license_verdicts.csv: "may be public" today, and if the
  // ERW sold anything, "may be public" or not)
  if (p[0] === "lic") {
    const meta = (f) => licCsv(fs.readFileSync(path.join(here, "..", "..", "warehouse", "metadata", f), "utf-8"));
    if (p[1] === "held") {
      const held = meta("license_status.csv").filter((r) => r.status === "license needed");
      if (p[2] === "count") return held.length;
      if (p[2] === "pub") return held.filter((r) => r.publishers.split(";").map((x) => x.trim()).includes(p[3])).length;
    }
    if (p[1] === "verdict") {
      const today = meta("license_verdicts.csv").filter((r) => r.verdict === "may be public");
      if (p[2] === "both") return today.filter((r) => r.if_commercial === "may be public").length;
      if (p[2] === "today_only") return today.filter((r) => r.if_commercial !== "may be public").length;
    }
    return undefined;
  }
  if (p[0] === "digest_chart") {
    return JSON.parse(fs.readFileSync(path.join(here, "..", "..", "docs", "digest", "charts", `${p[1]}.json`), "utf-8")).numbers?.[p[3]];
  }
  // session 402: the Energy Digest's numbers section (lib/digest.ts), recomputed by the Digest's own rule (warehouse/news/brief.py):
  // digest_dam|<ISO>|<table>|<node>|<day>: the mean of the ISO's local operating day's hourly day-ahead prices, every hour
  // held, exact and rounded half up to cents (as brief.mean2 and the Roundup's check below); digest_rt|<table>|<node>|
  // <variable>|<ts_utc>: the real-time price at its interval; digest_fuel|eia_fuel_spot_prices|<entity>|<day>: the close.
  // A table consolidated since (session 29) is read from its new table. The live set holds ISO prices for 35 days.
  if (p[0] === "digest_dam") {
    const [, iso, table, node, d] = p;
    const tz = HUB[iso]?.[1];
    if (!tz) throw new Error(`unknown grid in ${check}`);
    const [y, m, dd] = d.split("-").map(Number);
    const s0 = localMidnight(y, m - 1, dd, tz), s1 = localMidnight(y, m - 1, dd + 1, tz);
    const [t, f] = current(table, { node: `eq.${node}`, and: `(ts_utc.gte.${s0.toISOString()},ts_utc.lt.${s1.toISOString()})` });
    const rows = await all("series", { select: "value", table_name: `eq.${t}`, ...f, order: "ts_utc" });
    const hours = Math.round((s1 - s0) / 36e5);
    if (rows.length !== hours) return undefined;   // a day not held whole in the live set: no value to compare
    const micro = rows.reduce((a, r) => a + Math.round(r.value * 1e6), 0);
    const x = micro / rows.length / 1e4;
    return Math.sign(x) * Math.floor(Math.abs(x) + 0.5) / 100;
  }
  if (p[0] === "digest_rt") {
    const [, table, node, variable, ts] = p;
    const [t, f] = current(table, { node: `eq.${node}`, variable: `eq.${variable}`, ts_utc: `eq.${ts}` });
    const r = (await q("series", { select: "value", table_name: `eq.${t}`, ...f }))[0];
    return r ? Number(r.value.toFixed(2)) : undefined;
  }
  if (p[0] === "digest_fuel") {
    const [, table, entity, d] = p;
    const r = (await q("series", { select: "value", table_name: `eq.${table}`, entity: `eq.${entity}`, ts_utc: `eq.${d}T00:00:00Z` }))[0];
    return r ? Number(r.value.toFixed(2)) : undefined;
  }
  // session 300: the home page's count of findings, from the library's own catalogue (site/data/findings/catalogue.json)
  if (p[0] === "findings" && p[1] === "count") {
    return JSON.parse(fs.readFileSync(path.join(here, "..", "data", "findings", "catalogue.json"), "utf-8")).length;
  }
  if (p[0] === "bill") {
    const R = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "bill_rules.json"), "utf-8")).bills;
    const [, st, what, ts] = p;
    let total, kwh;
    if (st === "CA") {
      const c = R.CA, d = c.defaults, s = c.seasons[d.season];
      kwh = d.kwh;
      const q = c.baseline_quantities.code_B[d.territory][d.season === "summer" ? 0 : 1] * d.days;
      total = kwh * (d.peak_share * s.peak + (1 - d.peak_share) * s.offpeak) + Math.min(kwh, q) * c.baseline_credit.rate
        + d.days * c.base_services.tiers[d.income_tier] + (d.climate_credit ? c.climate_credit.rate : 0);
    } else if (st === "SCE" || st === "SDGE") {
      // session 52: by period, the delivery and generation (SCE) or total (SDG&E) rates summed per period, here
      const c = R[st], d = c.defaults;
      kwh = d.kwh;
      const p = d.peak_share, sp = d.super_share;
      const sh = c.kind === "sce"
        ? (d.season === "summer" ? { on: p * d.weekday_share, mid: p * (1 - d.weekday_share), off: 1 - p } : { mid: p, super: sp, off: 1 - p - sp })
        : { on: p, super: sp, off: 1 - p - sp };
      const perPeriod = {};
      for (const comp of c.components) for (const [k, v] of Object.entries(comp.basis === "per_kWh_period" ? comp.rate[d.season] : Object.fromEntries(Object.keys(sh).map((k) => [k, comp.rate])))) perPeriod[k] = (perPeriod[k] ?? 0) + v;
      const base = c.kind === "sce" ? Math.min(kwh, c.baseline_quantities.basic[d.region][d.season === "summer" ? 0 : 1] * d.days) : Math.min(kwh, (d.baseline_kwh ?? 0) * c.baseline_credit.share);
      total = Object.entries(sh).reduce((a, [k, x]) => a + kwh * x * perPeriod[k], 0) + base * c.baseline_credit.rate + d.days * c.base_services.rate
        + (d.climate_credit && c.climate_credit ? c.climate_credit.rate : 0);
    } else {
      const t = R[st];  // TX (Oncor) or, since session 52, TXC (CenterPoint)
      kwh = t.defaults.kwh;
      total = kwh * t.energy_default.rate + t.fixed.reduce((a, f) => a + f.rate, 0) + kwh * t.per_kwh.reduce((a, f) => a + f.rate, 0);
    }
    if (what === "total") return total;
    const row = (await q("series", { select: "value", table_name: "eq.cost_of_power_monthly", entity: `eq.${R[st].wholesale_entity}`, variable: "eq.rt_load_weighted", ts_utc: `eq.${ts}` }))[0];
    if (!row) return undefined;
    const w = (kwh * Number(row.value)) / 1000;
    return what === "wholesale" ? w : (w / total) * 100;
  }
  // session 37: the cost-of-power calculator's defaults, recomputed here from the tables (docs/methods/cost_of_power.md)
  if (p[0] === "cop") {
    const [, what] = p;
    if (what === "energy") {
      const [, , mw, lf, days, share] = p.map(Number);
      return mw * lf * 24 * days * share;
    }
    const entity = p[2];
    if (what === "flat_price" || what === "flat_cost") {
      const rows = await all("series", { select: "variable,ts_utc,value", table_name: "eq.cost_of_power_monthly", entity: `eq.${entity}`,
        variable: "in.(rt_hours,rt_simple_mean)", order: "ts_utc" });
      const by = {};
      for (const r of rows) (by[r.ts_utc.slice(0, 7)] ??= {})[r.variable] = Number(r.value);
      // session 49: a key that ends in a month (flat_price|<e>|<m>, flat_cost|<e>|<mw>|<lf>|<days>|<m>) uses that month only
      const only = what === "flat_price" ? p[3] : p[6];
      const months = Object.keys(by).filter((m) => by[m].rt_hours !== undefined && by[m].rt_simple_mean !== undefined && (!only || m === only))
        .sort().reverse().slice(0, 12);
      let num = 0, den = 0;
      for (const m of months) { num += by[m].rt_simple_mean * by[m].rt_hours; den += by[m].rt_hours; }
      const price = den ? num / den : null;
      if (price === null || what === "flat_price") return price;
      const [mw, lf, days] = p.slice(3).map(Number);
      return mw * lf * 24 * days * price;
    }
    if (what === "cheap_price" || what === "cheap_cost") {
      const rows = await all("series", { select: "variable,ts_utc,value", table_name: "eq.cost_of_power_hourly_profile", entity: `eq.${entity}`, order: "ts_utc" });
      const cells = {};
      for (const r of rows) {
        const m = /^rt_(mean|days)_h(\d\d)$/.exec(r.variable);
        if (m) (cells[`${r.ts_utc.slice(0, 7)}|${m[2]}`] ??= {})[m[1]] = Number(r.value);
      }
      const onlyM = what === "cheap_price" ? p[4] : p[7];  // session 49: the month, where the key names one
      const cs = Object.entries(cells).filter(([k, c]) => c.mean !== undefined && c.days !== undefined && (!onlyM || k.split("|")[0] === onlyM))
        .map(([k, c]) => ({ month: k.split("|")[0], hour: Number(k.split("|")[1]), price: c.mean, hours: c.days }))
        .sort((a, b) => a.price - b.price || a.month.localeCompare(b.month) || a.hour - b.hour);
      const share = Number(what === "cheap_price" ? p[3] : p[6]);
      const target = share * cs.reduce((a, c) => a + c.hours, 0);
      if (!target) return null;
      let left = target, cost = 0;
      for (const c of cs) { if (left <= 0) break; const take = Math.min(c.hours, left); cost += c.price * take; left -= take; }
      const price = cost / target;
      if (what === "cheap_price") return price;
      const [mw, lf, days] = p.slice(3, 6).map(Number);
      return mw * lf * 24 * days * share * price;
    }
  }
  // session 347: /impact's figures, impact|<tech>|<state>|<mw>|<capex>|<local>|<life>|<stat>: recomputed by lib/impact.ts
  // (the page's own arithmetic) from this script's own read of nlr_jedi_multipliers: the rows of the technology and
  // state, and every state's construction jobs for the state's rank
  if (p[0] === "impact") {
    const I = await import("../lib/impact.ts");
    const { x, stat } = I.parseKey(check);
    const num = (r) => ({ ...r, value: Number(r.value) });
    const k = `${x.tech}|${x.state}`;
    if (!impactRows.has(k)) impactRows.set(k, (await all("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${I.TABLE}`, entity: `like.nlr_jedi:${x.tech}:${x.state}:*`, order: "entity,variable" })).map(num));
    if (!impactAll.has(x.tech)) impactAll.set(x.tech, (await all("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${I.TABLE}`, entity: `like.nlr_jedi:${x.tech}:*:construction:*`, variable: "eq.jobs", order: "entity" })).map(num));
    return I.stat(impactRows.get(k), x, stat, impactAll.get(x.tech)) ?? undefined;
  }
  if (p[0] === "series") {
    const [, table, entity, variable, at, event] = p;
    const params = { select: "value,ts_utc", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${variable}` };
    if (event) params.event = `eq.${event}`; // session 36C: event_window_daily's key includes its event
    if (at === "newest") Object.assign(params, { order: "ts_utc.desc", limit: "1" });
    else params.ts_utc = `eq.${at}`;
    return (await q("series", params))[0]?.value;
  }
  // session 405: a count a series table's header states for one name, series_hdr|<table>|<entity naming the grid>|<line
  // prefix>|<name>: the header line that begins with the prefix, "...: ERCOT 456, CAISO 169", read for "<name> <count>"
  if (p[0] === "series_hdr") {
    const [, table, , prefix, name] = p;
    const line = (await q("headers", { select: "line", table_name: `eq.${table}`, order: "line_no" })).map((r) => r.line).find((l) => l.startsWith(prefix));
    const item = line?.slice(line.indexOf(":") + 1).split(",").map((s) => s.trim()).find((s) => s.startsWith(`${name} `));
    return item === undefined ? undefined : Number(item.slice(name.length + 1).replace(/,/g, ""));
  }
  // session 15: /deals and /grid
  // session 466: the comparables view, deals|comp_<stat>|<dimension>|<value>: the page's own functions (lib/deals2.ts)
  // on every row of energy_deals as the page reads it, with the register's folded pairs shown once
  if (p[0] === "deals" && String(p[1]).startsWith("comp_")) {
    const D = await import("../lib/deals2.ts");
    const [, stat, dim, value] = p;
    const rows = await all("events", { select: "event_id,event_date,status,mw,price,currency,parties,source,source_url,extra", table_name: "eq.energy_deals", order: "event_date.desc,event_id" });
    const pairs = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "deal_duplicates.json"), "utf-8")).pairs;
    const cell = D.comparables(D.fold(rows.map(D.toDeal), pairs), dim).find((c) => c.value === (value === "-" ? "" : value));
    if (!cell) return undefined;
    const v = { comp_deals: cell.deals, comp_with_price: cell.withPrice, comp_with_mw: cell.withMw, comp_median_price: cell.medianPrice, comp_median_mw: cell.medianMw }[stat];
    return v ?? undefined;
  }
  if (p[0] === "deals") {
    const [, what, month] = p;
    const rows = await all("events", { select: "event_date,mw,ai:extra->>ai_power", table_name: "eq.energy_deals" });
    const m = rows.filter((r) => String(r.event_date).slice(0, 7) === month);
    if (what === "month_count") return m.length;
    if (what === "month_mw") return m.reduce((a, r) => a + (r.mw === null ? 0 : Number(r.mw)), 0);
    // session 149: energy_deals writes the tag as "True" (rows extracted to 3 October 2026) and as "true" (since): one
    // flag, two spellings. The page has read both since session 114; the check read only "true" and so undercounted.
    if (what === "month_ai_pct") return m.length ? Math.round((100 * m.filter((r) => String(r.ai ?? "").toLowerCase() === "true").length) / m.length) : null;
  }
  if (p[0] === "event") {
    const [, table, id, field] = p;
    const col = field === "mw" ? "v:mw" : `v:extra->>${field}`;
    const r = (await q("events", { select: col, table_name: `eq.${table}`, event_id: `eq.${id}` }))[0];
    return r ? Number(r.v) : undefined;
  }
  // session 329: one field of one row of an entities table (the companies tab's confidence: entity|energy_companies|<id>|confidence)
  if (p[0] === "entity") {
    const [, table, id, field] = p;
    const col = field === "capacity_mw" ? "v:capacity_mw" : `v:extra->>${field}`;
    const r = (await q("entities", { select: col, table_name: `eq.${table}`, entity_id: `eq.${id}` }))[0];
    return r ? Number(r.v) : undefined;
  }
  // session 369: the day a problem set's figures belong to, fullday|<set>|<YYYY-MM-DD>, checked with the page's own rule
  // (lib/gridday.ts, the same function): the newest day every table of the set holds in full, up to the page's day. A
  // page that names a day missing hours in any table reads an earlier day here and fails; a newer day the tables have
  // gained since the page was built is not counted against it (a cached page names the day it was built on)
  if (p[0] === "fullday") {
    const G = await import("../lib/gridday.ts");
    const [, set, d] = p;
    if (set !== "know-your-grid") throw new Error(`unknown problem set in ${check}`);
    const from = new Date(Date.parse(`${d}T00:00:00Z`) - 3 * 86_400_000).toISOString(), to = new Date(Date.parse(`${d}T00:00:00Z`) + 86_400_000).toISOString();
    const held = [];
    for (const { table, variables } of G.KNOW_YOUR_GRID.tables) {
      const rows = await all("series", { select: "entity,variable,ts_utc", table_name: `eq.${table}`, variable: `in.(${variables.join(",")})`,
        entity: `in.(${G.KNOW_YOUR_GRID.entities.map((e) => `"${e}"`).join(",")})`, and: `(ts_utc.gte.${from},ts_utc.lt.${to})`, order: "entity,variable,ts_utc" });
      held.push({ table, variables, rows });
    }
    return G.newestCommonFullDay(held, G.KNOW_YOUR_GRID.entities, d);
  }
  if (p[0] === "series_max" || p[0] === "series_sum") {
    // session 29: an optional sixth part names the entity (one BA of the consolidated EIA-930 tables)
    const [, table, variable, start, end, entity] = p;
    const rows = await all("series", { select: "value", table_name: `eq.${table}`, variable: `eq.${variable}`,
      and: `(ts_utc.gte.${start},ts_utc.lt.${end})`, order: "entity,ts_utc", ...(entity ? { entity: `eq.${entity}` } : {}) });
    if (!rows.length) return undefined;
    return p[0] === "series_max" ? Math.max(...rows.map((r) => r.value)) : rows.reduce((a, r) => a + r.value, 0);
  }
  // session 18: a sum over one entity's rows in a time range (/mix, /curtailment, /consumption)
  if (p[0] === "series_esum") {
    const [, table, entity, variable, start, end] = p;
    const rows = await all("series", { select: "value", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${variable}`,
      and: `(ts_utc.gte.${start},ts_utc.lt.${end})`, order: "ts_utc" });
    if (!rows.length) return undefined;
    return rows.reduce((a, r) => a + r.value, 0);
  }
  // session 16: /map (energy_projects, and datacenter_facilities as the kind datacenter; session 22) and /datacenters
  if (p[0] === "projects") {
    const [, what, kind, arg] = p;
    // session 22: datacenters come from datacenter_facilities, whose extra.kind is the source kind (news,
    // operator, queue): every row is the map's kind datacenter, and the operator's coordinates count as a point
    const dc = kind === "datacenter";
    const base = dc
      ? { select: "entity_id", table_name: "eq.datacenter_facilities" }
      : { select: "entity_id", table_name: "eq.energy_projects", "extra->>kind": `eq.${kind}` };
    if (what === "count") {
      if (arg === "all") return q("entities", base, true);
      const prec = dc && arg === "county" ? "in.(county,place)" : dc && arg === "point" ? "in.(point,operator)" : `eq.${arg}`;
      return q("entities", { ...base, "extra->>geo_precision": prec }, true);
    }
    if (what === "tech_count") return q("entities", { ...base, "extra->>technology_group": `eq.${arg}` }, true);
    if (what === "mw") {
      const rows = await all("entities", { ...base, select: "capacity_mw", order: "entity_id" });
      return rows.reduce((a, r) => a + (r.capacity_mw === null ? 0 : Number(r.capacity_mw)), 0);
    }
  }
  if (p[0] === "datacenters") {
    // session 177: since session 166 (part F) the page's totals count only the rows in a named US state that are not
    // cancelled (app/datacenters/Body.tsx, counted), and it shows three counts this check did not know (counted,
    // no_us_state, cancelled): the whole run stopped at "unknown check datacenters|counted". The rule is the page's
    // own (lib/largeload.ts); the rows are read here, from Supabase, as before.
    const [, what, key] = p;
    const { cancelled, countryOf } = await import("../lib/largeload.ts");
    const rows = (await all("entities", { select: "operator,status,mw:capacity_mw,state:extra->>state,country:extra->>country,first:extra->>first_story_at,kind:extra->>kind", table_name: "eq.datacenter_facilities", order: "entity_id" }))
      .map((r) => ({ ...r, us: countryOf(r.country, r.state) === "US" }));
    const inTotals = rows.filter((r) => r.us && !cancelled(r.status));
    const withMw = inTotals.filter((r) => r.mw !== null);
    if (what === "count") return rows.length;
    if (what === "counted") return inTotals.length;
    if (what === "no_us_state") return rows.filter((r) => !r.us).length;
    if (what === "cancelled") return rows.filter((r) => r.us && cancelled(r.status)).length;
    if (what === "n_with_mw") return withMw.length;
    if (what === "mw_total") return withMw.reduce((a, r) => a + Number(r.mw), 0);
    if (what === "state_mw") return withMw.filter((r) => (r.state ?? "") === key).reduce((a, r) => a + Number(r.mw), 0);
    if (what === "operator_mw") return withMw.filter((r) => (r.operator ?? "") === key).reduce((a, r) => a + Number(r.mw), 0);
    // session 240: the top block and the list grouped by operator. The megawatts by status (a blank status is its own
    // line), the facilities whose first story is dated on or after the day in the key (the page's "this week"), the
    // facilities that carry a first story at all, and an operator's rows in the table (all of them, as the list shows)
    if (what === "status_mw") return withMw.filter((r) => (r.status ?? "") === (key ?? "")).reduce((a, r) => a + Number(r.mw), 0);
    if (what === "first_week") return rows.filter((r) => r.first && r.first.slice(0, 10) >= key).length;
    if (what === "n_first_story") return rows.filter((r) => r.first).length;
    if (what === "operator_count") return rows.filter((r) => (r.operator ?? "") === (key ?? "")).length;
    // session 241: the sentence /datacenters/v2 wrote, now on /datacenters (app/datacenters/LargeLoad.tsx), counted as
    // lib/largeload.ts facilityCounts counts: every row held, the cancelled and those with no US state among them. The
    // sites in a named US state, the sites in Texas, the sites that state a size and their megawatts (all, and Texas),
    // and the sites by where each came from (a blank kind is "not stated")
    const sized = (x) => x.filter((r) => r.mw !== null && Number.isFinite(Number(r.mw)));
    const texas = rows.filter((r) => (r.state ?? "") === "TX");
    if (what === "sites_us") return rows.filter((r) => r.us).length;
    if (what === "sites_texas") return texas.length;
    if (what === "sites_n_with_mw") return sized(rows).length;
    if (what === "sites_mw") return sized(rows).reduce((a, r) => a + Number(r.mw), 0);
    if (what === "texas_n_with_mw") return sized(texas).length;
    if (what === "texas_mw") return sized(texas).reduce((a, r) => a + Number(r.mw), 0);
    if (what === "kind_count") return rows.filter((r) => (r.kind || "not stated") === key).length;
  }
  // session 31: /storage, sums of storage_capacity's nameplate MW (rounded to 0.1 MW, as the page rounds them);
  // session 34: and of its energy capacity, MWh (storage|mwh|<status>, storage|n_mwh|<status>)
  if (p[0] === "storage") {
    storageRows ??= await all("entities", { select: "capacity_mw,status,state:extra->>state,iso:extra->>iso,planned_year:extra->>planned_year,mwh:extra->>energy_capacity_mwh",
      table_name: "eq.storage_capacity", order: "entity_id" });
    const rows = storageRows;
    const build = (r) => r.status === "under_construction" || r.status === "planned";
    const sum = (f) => Math.round(rows.filter(f).reduce((a, r) => a + (r.capacity_mw === null ? 0 : Number(r.capacity_mw)), 0) * 10) / 10;
    const [, what, a, b] = p;
    if (what === "n") return rows.filter((r) => r.status === a).length;
    if (what === "mw") return sum((r) => r.status === a);
    if (what === "iso_mw") return sum((r) => (a === "none" ? !r.iso : r.iso === a) && r.status === b);
    if (what === "state_mw") return sum((r) => r.state === a && (b === "build" ? build(r) : r.status === b));
    if (what === "year_mw") return sum((r) => build(r) && r.planned_year === a);
    const hasMwh = (r) => r.mwh !== null && r.mwh !== undefined && r.mwh !== "";
    if (what === "mwh") return Math.round(rows.filter((r) => r.status === a && hasMwh(r)).reduce((s, r) => s + Number(r.mwh), 0) * 10) / 10;
    if (what === "n_mwh") return rows.filter((r) => r.status === a && hasMwh(r)).length;
    // session 35: a grid's battery MWh (units whose balancing authority is the grid's ISO)
    if (what === "iso_mwh") return Math.round(rows.filter((r) => r.iso === a && r.status === b && hasMwh(r)).reduce((s, r) => s + Number(r.mwh), 0) * 10) / 10;
    // session 46: the battery game's fleet panel, a grid's unit counts (all, and those with an energy capacity)
    if (what === "iso_n") return rows.filter((r) => r.iso === a && r.status === b).length;
    if (what === "iso_n_mwh") return rows.filter((r) => r.iso === a && r.status === b && hasMwh(r)).length;
  }
  // session 46: the battery game's fictional fleet, from lib/battery.ts's constants (FLEET homes x 5 kW, x 13.5 kWh)
  if (p[0] === "battery") {
    const b = await import("../lib/battery.ts");
    if (p[1] === "fleet_mw") return b.FLEET_MW;
    if (p[1] === "fleet_mwh") return b.FLEET_MWH;
    // problem set D: the assumed battery's round trip, one full cycle's kWh, and one cycle between two series values
    // (battery|cycle|<table>|<entity>|<ts>|<buy variable>|<sell variable>), for one home or the fleet
    if (p[1] === "round_trip_pct") return b.BATTERY.roundTrip * 100;
    if (p[1] === "bought_kwh") return b.fullCycle(0, 0).bought;
    if (p[1] === "delivered_kwh") return b.fullCycle(0, 0).delivered;
    if (p[1] === "cycle" || p[1] === "cycle_fleet") {
      const [, , table, entity, ts, buyVar, sellVar] = p;
      const val = async (v) => (await q("series", { select: "value", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${v}`, ts_utc: `eq.${ts}` }))[0]?.value;
      const buy = await val(buyVar), sell = await val(sellVar);
      if (buy === undefined || sell === undefined) return undefined;
      const usd = b.fullCycle(Number(buy), Number(sell)).usd;
      return p[1] === "cycle" ? usd : usd * b.FLEET;
    }
  }
  // session 46 (problem set D): a month's mean of an EIA daily spot series (spotmean|<entity>|<YYYY-MM>), a month's
  // severance tax at that mean (sev|<state>|<product>|<volume>|<YYYY-MM>|<option id or base>, by lib/severance.ts on
  // data/severance_rules.json), and a Texas low-producing credit's certified price and percent (sevcert, sevcredit)
  const spotMean = async (entity, month) => {
    const next = new Date(Date.UTC(Number(month.slice(0, 4)), Number(month.slice(5, 7)), 1)).toISOString().slice(0, 7);
    const rows = await all("series", { select: "value", table_name: "eq.eia_fuel_spot_prices", entity: `eq.${entity}`, variable: "eq.spot_price",
      and: `(ts_utc.gte.${month}-01T00:00:00Z,ts_utc.lt.${next}-01T00:00:00Z)`, order: "ts_utc" });
    return rows.length ? rows.reduce((a, r) => a + Number(r.value), 0) / rows.length : undefined;
  };
  // session 47: the event studies on the /events pages, es|<event>|<entity>|<variable>|<term>|<field>, recomputed from
  // event_window_daily with lib/eventstudy.ts (term pooled, or day|<YYYY-MM-DD>; field est, lo, hi, cf, pct)
  if (p[0] === "es") {
    const [, ev, entity, variable] = p;
    const term = p[4] === "day" ? `day|${p[5]}` : p[4], field = p.at(-1);
    const k = `${ev}|${entity}|${variable}`;
    const { studyOf, gridWeather, STATION_BA, ENTITY_BA } = await import("../lib/eventstudy.ts");
    if (!studies.has(k)) {
      const rows = await all("series", { select: "ts_utc,value,freq", table_name: "eq.event_window_daily", event: `eq.${ev}`, entity: `eq.${entity}`,
        variable: `eq.${variable}`, order: "ts_utc" });
      const rs = rows.map((r) => ({ ts_utc: r.ts_utc, value: Number(r.value), freq: r.freq }));
      // session 49: the station rows of the event, for the temperature-controlled study
      const wx = await all("series", { select: "entity,variable,ts_utc,value", table_name: "eq.event_window_daily", event: `eq.${ev}`,
        entity: "like.noaa:*", variable: "in.(hdd_65f,cdd_65f)", order: "entity,ts_utc,variable" });
      const ws = gridWeather(wx.filter((r) => STATION_BA[r.entity] === ENTITY_BA(entity)).map((r) => ({ ...r, value: Number(r.value) })));
      let t = null;
      try { t = ws.size ? studyOf(ev, rs, ws) : null; } catch { t = null; }
      studies.set(k, { s: studyOf(ev, rs), t });
    }
    const { s, t } = studies.get(k);
    if (term === "pooled") {
      if (field === "cf") return s.counterfactualMean;
      if (field === "pct") return (s.pooled.estimate / s.counterfactualMean) * 100;
      return { est: s.pooled.estimate, lo: s.pooled.lo, hi: s.pooled.hi }[field];
    }
    if (term === "pooled_temp") return t ? { est: t.pooled.estimate, lo: t.pooled.lo, hi: t.pooled.hi }[field] : undefined;
    if (term === "weather_share") return t ? (1 - t.pooled.estimate / s.pooled.estimate) * 100 : undefined;
    const d = s.days.find((x) => x.day === p[5]);
    return d ? { est: d.estimate, lo: d.lo, hi: d.hi }[field] : undefined;
  }
  // session 48: the shape premium report's period statistics, shape|<entity>|<market>|<stat>|<start>|<end>, by
  // lib/shapepremium.ts from every cost_of_power_monthly row of the hub
  // session 228: the three answers of "What a datacenter pays", dc|<address>|<stat>: the address names the load (grid,
  // region, market, how it runs, size); the figure is recomputed by lib/datacenter/answers.ts from this script's own
  // read of carbon_intensity_monthly, carbon_intensity_hourly, ercot_large_load_status and caiso_grid_emergencies in
  // Supabase, and from the page's own price files (scripts/datacenter-ways.mjs), as the page computes it
  if (p[0] === "dc") {
    const key = p[1];
    if (!dcAnswers.has(key)) {
      const W = await import("./datacenter-ways.mjs");
      const R = await import("../lib/datacenter/answers.ts");
      const q = Object.fromEntries(new URLSearchParams(key));
      const page = W.pageOf(q);
      const x = page.x, g = W.INDEX.grids[x.grid];
      const l12 = (page.l12 ?? []).map((r) => r.m);
      dcAnswers.set(key, R.readAnswers({ grid: x.grid, mw: x.mw, l12, behind: g.std_hours_behind_utc, ruled: await W.ruledWays(page), rows: (t, params) => all(t, params) }));
    }
    const a = await dcAnswers.get(key);
    return R_statOf(a, p.slice(2).join("|"));
  }
  // session 236: Texas's delivery charges by component on "What a datacenter pays", dcd|<mw>|<utility>:<component or
  // total>: recomputed by lib/datacenter/delivery.ts from the site's own file of tariff lines
  // (data/datacenter/texas_delivery.json, not Supabase), as the page computes it
  // session 265b: the large-load statements on a public document for the load's grid on "What a datacenter pays",
  // dcll|<grid>|<stat>: recomputed by lib/datacenter/statements.ts from this script's own read of large_load_public
  if (p[0] === "dcll") {
    const S = await import("../lib/datacenter/statements.ts");
    if (!dcllRows.has(p[1])) dcllRows.set(p[1], all("events", { select: "event_date,parties,mw,source_url,row_kind:extra->>row_kind,duration_as_stated:extra->>duration_as_stated,wait_basis:extra->>wait_basis,stage_class:extra->>stage_class,document_title:extra->>document_title,page:extra->>page,statement_id:extra->>statement_id", table_name: "eq.large_load_public", "extra->>grid": `eq.${p[1]}`, order: "event_date.desc,event_id" }));
    const rows = await dcllRows.get(p[1]);  // session 280: one read a grid, however many of its rows the page lists
    // session 280: one row's figure, dcll|<the row's grid>|row:<statement_id>:mw or :wait (the list under "How soon?")
    if (p[2]?.startsWith("row:")) return S.rowStat(rows, p.slice(2).join("|"));
    return S.statedStat(S.statedOf(rows), p.slice(2).join("|"));
  }
  // session 467: the datacenter tracker's power side, dcpow|<grid>|<region>|per: what a flat load paid at a region under
  // the cost-of-power calculator's defaults (its last twelve complete months, real time where held, else day-ahead),
  // recomputed from the page's own price files by the calculator's own steps (scripts/datacenter-ways.mjs, pageOf), so it
  // is the headline /cost-of-power?grid=<grid>&region=<region> shows
  if (p[0] === "dcpow") {
    const W = await import("./datacenter-ways.mjs");
    if (!W.INDEX.grids[p[1]]) return undefined;
    const page = W.pageOf({ grid: p[1], region: p[2] });
    if (page.x.grid !== p[1] || page.x.region !== p[2]) return undefined;
    if (p[3] === "per") return page.s12?.per ?? undefined;
    // session 468: dcpow|<grid>|<region>|year|<YYYY>, a complete calendar year in the same market, as the view by grid shows it
    if (p[3] === "year") {
      const L = await import("../lib/datacenter.ts");
      const y = L.years(page.ms).find((r) => r.y === p[4] && r.complete);
      return y?.per ?? undefined;
    }
    return undefined;
  }
  // session 468: the datacenter tracker by grid, dcq|<grid>|<zone or ->|<stat>: the queue positions that name a datacenter
  // or a large load (the builder's pattern, read from the grid's own queue table by name and by fuel field, as
  // lib/data.ts queueSites reads them) and the grid's active positions, grouped by lib/datacenter/bygrid.ts
  if (p[0] === "dcq") {
    const B = await import("../lib/datacenter/bygrid.ts");
    const table = `${p[1]}_interconnection_queue`;
    if (!dcqRows.has(p[1])) {
      dcqRows.set(p[1], (async () => {
        const sel = "entity_id,table_name,capacity_mw,status,zone:extra->>zone";
        const byName = await all("entities", { select: sel, table_name: `eq.${table}`, name: `imatch.${B.QUEUE_SITE_PATTERN}`, order: "entity_id" });
        const byFuel = await all("entities", { select: sel, table_name: `eq.${table}`, "extra->>fuel_technology": `imatch.${B.QUEUE_SITE_PATTERN}`, order: "entity_id" });
        const sites = [...new Map([...byName, ...byFuel].map((r) => [r.entity_id, r])).values()];
        const active = await all("entities", { select: "table_name,capacity_mw,status,zone:extra->>zone", table_name: `eq.${table}`, status: "eq.active", order: "entity_id" });
        return B.groups(sites, active);
      })());
    }
    return B.groupStat(await dcqRows.get(p[1]), p[1], p[2], p[3]);
  }
  // session 700: the All grids tab of /cost-of-power, allgrids|<column>|<row>[|<inputs>]: recomputed by lib/siting.ts from
  // the files the tab reads (data/datacenter/index.json, data/siting/*.json; not Supabase), as the tab computes it
  if (p[0] === "allgrids") {
    const S = await import("../lib/siting.ts");
    const F = await import("./siting-files.mjs");
    return S.sitingStat(F.files(), check, await F.dc());
  }
  if (p[0] === "dcd") {
    const D = await import("../lib/datacenter/delivery.ts");
    const file = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "datacenter", "texas_delivery.json"), "utf-8"));
    return D.deliveryStat(file.rows, Number(p[1]), p.slice(2).join("|"));
  }
  // session 51: the seller's tab: recomputed from the snapshot the page reads (data/merchant_snapshot.json, not Supabase),
  // with lib/merchant.ts; tests/test_session51.py checks the snapshot against the warehouse table and by hand
  // session 235: the capture table of /cost-of-power/seller, cap|<grid>|<hub>|<market>|<fuel>|<span>|<stat>: recomputed
  // from the file the page reads (data/seller/capture.json, not Supabase; warehouse/derived/capture_price.py builds it
  // and tests/test_session145.py holds it against the warehouse) with lib/capture.ts. <span> is l12 or a year; <stat>
  // is price, flat or rate (the capture rate in whole percent, as the table writes it)
  // session 264: every generator key names its grid (cap|<grid>|..., mr| and ms| by the inputs' iso=); a key that does
  // not, or that names a hub's model (&hub=, which the snapshot does not hold), is not recomputed and fails
  const namesGrid = (inputs) => /(^|&)iso=(ercot|caiso|nyiso|isone|spp|miso)(&|$)/.test(inputs) && !/(^|&)hub=/.test(inputs);
  if (p[0] === "cap") {
    const C = await import("../lib/capture.ts");
    const file = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "seller", "capture.json"), "utf-8"));
    if (!file.grids[p[1]]) return null;
    return C.stat(file, p[1], p[2], p[3], p[4], p[5], p[6]);
  }
  if (p[0] === "mr") {
    const M = await import("../lib/merchant.ts");
    const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "merchant_snapshot.json"), "utf-8"));
    if (!namesGrid(p[1])) return null;
    return M.stat(snap, M.parseKey(p[1]), p[2]);
  }
  // session 288 (problem set E, question 5, Samuel's ruling 6a): a stress event's window against as many baseline days,
  // mrs|<inputs>|<event>|<days|base_mean|base_window>, from lib/merchant.ts's stress() on the snapshot (days: the
  // window's days held; base_mean: the baseline days' mean; base_window: that mean times the window's days)
  if (p[0] === "mrs") {
    const M = await import("../lib/merchant.ts");
    const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "merchant_snapshot.json"), "utf-8"));
    if (!namesGrid(p[1])) return null;
    const e = (M.stress(snap, M.parseKey(p[1])) ?? []).find((x) => x.event === p[2]);
    if (!e) return undefined;
    return p[3] === "days" ? e.days : p[3] === "base_mean" ? e.baseMean : p[3] === "base_window" ? e.baseMean * e.days : undefined;
  }
  // session 264: the seller page's spans, ms|<inputs>|<twelve|three|every>|<revenue|energy|capture|flat|rate>, per MW of
  // nameplate at the main hub: recomputed here from the snapshot's months (lib/merchant.ts) by the rules of
  // lib/seller2.ts (which Node cannot import: it names @/ paths), an independent second reading of the page's own spans
  if (p[0] === "ms") {
    const M = await import("../lib/merchant.ts");
    const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "merchant_snapshot.json"), "utf-8"));
    if (!namesGrid(p[1])) return null;
    const x = M.parseKey(p[1]);
    const ms = M.months(snap, { ...x, mw: 1, mwh: x.asset === "battery" ? x.mwh / x.mw : 0, ds: 0, fom: 0 });
    const by = new Map(ms.map((r) => [r.m, r]));
    const back = (m, k) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1 - k, 1)).toISOString().slice(0, 7);
    const yearsHeld = {};
    for (const r of ms) if (r.held) yearsHeld[r.m.slice(0, 4)] = (yearsHeld[r.m.slice(0, 4)] ?? 0) + 1;
    const full = Object.keys(yearsHeld).filter((y) => yearsHeld[y] === 12).sort();
    let rows = null, n = 1;
    if (p[2] === "twelve") {
      for (const r of [...ms].reverse()) {
        if (!r.held) continue;
        const t = Array.from({ length: 12 }, (_, k) => by.get(back(r.m, k)));
        if (t.every((v) => v && v.held)) { rows = t.reverse(); break; }
      }
    } else if (p[2] === "three" && full.length) {
      const want = [2, 1, 0].map((k) => String(Number(full.at(-1)) - k));
      if (want.every((y) => full.includes(y))) { rows = ms.filter((r) => r.held && want.includes(r.m.slice(0, 4))); n = 3; }
    } else if (p[2] === "every" && full.length) { rows = ms.filter((r) => r.held && full.includes(r.m.slice(0, 4))); n = full.length; }
    if (!rows || !rows.length) return null;
    const energy = rows.reduce((a, r) => a + r.energy, 0), sales = rows.reduce((a, r) => a + (r.capture !== null ? r.capture * r.energy : 0), 0);
    const flat = rows.reduce((a, r) => a + r.flat, 0) / rows.length, capture = energy > 0 ? sales / energy : null;
    const v = { revenue: rows.reduce((a, r) => a + r.revenue, 0) / n / 1000, energy: Math.round(energy / n), capture, flat,
      rate: capture !== null && flat ? Math.round((100 * capture) / flat) : null }[p[3]];
    return v === undefined ? null : v;
  }
  // session 178: the battery page's one line beside ERCOT's real awards, bsa|<strategy>_<N>h|<stat>: from the snapshot the
  // page reads (data/battery_awards_beside.json, not Supabase), with lib/batterystack.ts; tests/test_session178.py checks
  // the snapshot against the two warehouse tables
  if (p[0] === "bsa") {
    const B = await import("../lib/batterystack.ts");
    const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "battery_awards_beside.json"), "utf-8"));
    return B.awardsStat(snap, p[1], p[2]);
  }
  // session 67: what a battery earns, bs|<inputs>|<stat>: recomputed by lib/batterystack.ts from this script's own read
  // of battery_stack_monthly and battery_stack_stress_daily in Supabase
  if (p[0] === "bs") {
    const B = await import("../lib/batterystack.ts");
    const x = B.parseKey(p[1], true);
    const entity = B.gridOf(x.grid).entity;
    const k = `${entity}|${x.strat}|${x.dur}`;
    if (!stackRows.has(k) && B.gridOf(x.grid).review) {
      // session 86: a grid in review is read from the committed snapshot, as its page reads it; it has no stress day
      const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "battery_stack_review.json"), "utf-8"));
      const pre = `${x.strat}_${x.dur}h_`;
      stackRows.set(k, [(snap.grids[x.grid]?.rows ?? []).filter((r) => r[0].startsWith(pre)).map(([variable, ts_utc, value]) => ({ variable, ts_utc, value: Number(value) })), []]);
    }
    if (!stackRows.has(k)) {
      const f = { entity: `eq.${entity}`, variable: `like.${x.strat}_${x.dur}h_*`, order: "variable,ts_utc" };
      const rows = await all("series", { select: "variable,ts_utc,value", table_name: `eq.${B.TABLE}`, ...f });
      const stress = await all("series", { select: "variable,ts_utc,value,event", table_name: `eq.${B.STRESS_TABLE}`, ...f });
      const num = (r) => ({ ...r, value: Number(r.value) });
      stackRows.set(k, [rows.map(num), stress.map(num)]);
    }
    const [rows, stress] = stackRows.get(k);
    return B.stat(rows, stress, x, p[2]);
  }
  // session 68: /network's last twelve months, bsup|<BA>|<stat>: recomputed by lib/basupply.ts from this script's own read
  // of ba_supply_monthly (the variables the panel uses)
  if (p[0] === "bsup") {
    const S = await import("../lib/basupply.ts");
    if (!supplyRows.has(p[1])) {
      const vars = ["days_in_month", "days_held", "days_left_out", "thin_month", "share_days", "demand_mwh", "net_import_mwh", "net_import_share_pct",
        "net_import_pairs_mwh", "net_import_total_interchange_mwh", "net_import_balance_mwh", "net_import_pairs_share_pct",
        "net_import_total_interchange_share_pct", "net_import_balance_share_pct"];
      supplyRows.set(p[1], (await all("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${S.TABLE}`, and: `(entity.gte.eia930:${p[1]},entity.lt.eia930:${p[1].slice(0, -1)}${String.fromCharCode(p[1].charCodeAt(p[1].length - 1) + 1)})`,
        variable: `in.(${vars.join(",")})`, order: "entity,variable,ts_utc" })).map((r) => ({ ...r, value: Number(r.value) })));
    }
    return S.supplyStat(supplyRows.get(p[1]), p[1], p[2]);
  }
  if (p[0] === "shape") {
    const [, entity, market, stat, start, end] = p;
    const { stats } = await import("../lib/shapepremium.ts");
    const rows = await all("series", { select: "entity,variable,ts_utc,value", table_name: "eq.cost_of_power_monthly", entity: `eq.${entity}`, order: "ts_utc,variable" });
    return stats(rows.map((r) => ({ ...r, value: Number(r.value) })), entity, market, start, end)[stat];
  }
  if (p[0] === "spotmean") return spotMean(p[1], p[2]);
  if (p[0] === "sev" || p[0] === "sevcert" || p[0] === "sevcredit") {
    const S = await import("../lib/severance.ts");
    const R = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "severance_rules.json"), "utf-8"));
    if (p[0] !== "sev") {
      const [, id, month] = p;
      const o = Object.values(R.states).flatMap((st) => Object.values(st.products)).flatMap((pr) => pr.options).find((x) => x.id === id);
      const c = o ? S.creditPct(o, { period: month }) : undefined;
      return c ? (p[0] === "sevcert" ? c.price : c.pct) : undefined;
    }
    const [, state, product, volume, month, option] = p;
    const price = await spotMean(product === "gas" ? "eia:henry_hub" : "eia:wti_cushing", month);
    if (price === undefined) return undefined;
    const x = { state, product, volume: Number(volume), price, ...(state === "LA" && product === "oil" ? { variant: "la_oil_pre2025" } : {}) };
    const o = R.states[state].products[product].options.find((y) => y.id === option);
    const r = S.compute(R, o ? { ...x, [o.group === "credit" ? "credit" : "option"]: { id: option, period: month } } : x);
    return o ? r.withTotal : r.baseTotal;
  }
  // session 35: the grid pages. gridq|<queue table>|<status>|<technology_group>|n or mw: its positions in energy_projects
  if (p[0] === "gridq") {
    const [, table, status, tech, what] = p;
    const rows = await all("entities", { select: "capacity_mw,status,tech:extra->>technology_group,src:extra->>source_table", table_name: "eq.energy_projects",
      entity_id: `like.${table.replace(/_interconnection_queue$/, "_queue")}:*`, order: "entity_id" }).then((x) => x.filter((r) => r.src === table));
    const m = rows.filter((r) => r.status === status && (r.tech ?? "unknown") === tech);
    if (what === "n") return m.length;
    return Math.round(m.reduce((a, r) => a + (r.capacity_mw === null ? 0 : Number(r.capacity_mw)), 0) * 10) / 10;
  }
  // griddc|<slug>|n or mw: datacenter_facilities mapped to the grid (session 36A): its queue's rows, rows naming one of
  // its utilities, then the others by its states (docs/methods/datacenter_facilities.md, "Grid pages")
  if (p[0] === "griddc") {
    const [, slug, what] = p;
    const g = GRIDS.find((x) => x.slug === slug);
    const gridOf = (r) => {
      const ids = (r.member_ids ?? "").split(";");
      for (const x of GRIDS) {
        const pre = x.queue_table ? x.queue_table.replace(/_interconnection_queue$/, "_queue:") : null;
        if (pre && ids.some((i) => i.startsWith(pre))) return x.slug;
      }
      const u = (r.utility ?? "").trim();
      return u ? (GRIDS.find((x) => (x.utilities ?? []).includes(u))?.slug ?? null) : null;
    };
    const rows = (await all("entities", { select: "capacity_mw,state:extra->>state,utility:extra->>utility,member_ids:extra->>member_ids",
      table_name: "eq.datacenter_facilities", order: "entity_id" }))
      .filter((r) => { const by = gridOf(r); return by ? by === slug : !!r.state && r.state in g.states; });
    if (what === "n") return rows.length;
    return Math.round(rows.reduce((a, r) => a + (r.capacity_mw === null ? 0 : Number(r.capacity_mw)), 0) * 10) / 10;
  }
  // gridnews|<slug>|<since>|n: news_index stories since then whose headline names the grid or whose region is one of its states
  if (p[0] === "gridnews") {
    const [, slug, since] = p;
    const g = GRIDS.find((x) => x.slug === slug);
    const rows = await all("events", { select: "headline:extra->>headline,region:extra->>region", table_name: "eq.news_index", event_date: `gte.${since}`, order: "event_id" });
    const esc = (x) => x.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return rows.filter((r) => g.names.some((n) => new RegExp(`\\b${esc(n)}\\b`).test(r.headline ?? "")) || Object.values(g.states).includes((r.region ?? "").trim())).length;
  }
  throw new Error(`unknown check ${check}`);
}
let storageRows = null;
const stackRows = new Map();
const supplyRows = new Map();  // session 68: ba_supply_monthly, one ISO grid at a time  // session 67: the battery stack's rows, by entity|strategy|duration
const studies = new Map();  // session 47: event studies, by event|entity|variable
// session 369: an event page's rows of one entity and variable (every date the table holds for the event), read once;
// the figure is compared with the row of its key's own date among them (event-dates.mjs rowOfKey)
const evRows = new Map();
async function eventRows(check) {
  const [, table, entity, variable, , event] = check.split("|");
  const k = [table, entity, variable, event ?? ""].join("|");
  if (!evRows.has(k)) evRows.set(k, await all("series", { select: "ts_utc,value", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${variable}`,
    ...(event ? { event: `eq.${event}` } : {}), order: "ts_utc" }));
  return evRows.get(k);
}

/** US dollars, short, as site/app/deals/DealsTable.tsx writes them (data-format usd). */
function usd(v) {
  const t = (x) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}

/** Session 402: the chart-maker's rounding (warehouse/analysis/findings/daily_chart.py nd_for; lib/digest.ts chartText). */
function digestChartText(v) {
  const a = Math.abs(v);
  const nd = a >= 10000 ? 0 : a >= 100 ? 1 : a >= 1 ? 2 : 4;
  return v.toLocaleString("en-US", { minimumFractionDigits: nd, maximumFractionDigits: nd });
}

function shown(raw) {
  // how the page writes a raw value: a timestamp as "YYYY-MM-DD HH:MM UTC", a whole number with commas, else 2 decimals
  if (/^\d{4}-\d{2}-\d{2}T/.test(raw)) return new Date(raw).toISOString().slice(0, 16).replace("T", " ") + " UTC";
  const x = Number(raw);
  return Number.isInteger(x) ? x.toLocaleString("en-US") : x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function decode(s) {
  return s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#x27;/g, "'");
}

// Session 17: /weekly. The weekly brief is markdown (docs/weekly/), not Num spans, so its numbers are
// parsed from the rendered page and recomputed here from Supabase: the day-ahead weekly means (the ISO's
// local week), the real-time peak's value at its interval, the fuel closes on their dates, and the US48
// peak demand (the maximum of the week to the hour the brief read to).
const HUB = {
  ERCOT: ["ercot_dam_hub_prices", "America/Chicago"], CAISO: ["caiso_dam_hub_prices", "America/Los_Angeles"],
  NYISO: ["nyiso_dam_zone_prices", "America/New_York"], MISO: ["miso_dam_hub_prices", "Etc/GMT+5"],
  SPP: ["spp_dam_hub_prices", "America/Chicago"], "ISO-NE": ["isone_dam_zone_prices", "America/New_York"],
};
// Session 29: a table consolidated into another (warehouse/metadata/table_migrations.csv) is read from its new
// table, filtered to its partition (market, or ba through the entity). A published Roundup names tables as they were.
const MIGRATED = (() => {
  const f = path.join(here, "..", "..", "warehouse", "metadata", "table_migrations.csv");
  if (!fs.existsSync(f)) return {};
  const out = {};
  for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/).slice(1)) {
    const [old, neu, part] = line.split(",");
    if (old) out[old] = [neu, Object.fromEntries(part.split(";").map((kv) => kv.split("=")))];
  }
  return out;
})();
function current(table, filters) {
  const m = MIGRATED[table];
  if (!m) return [table, filters];
  const [neu, part] = m;
  const f = { ...filters };
  if (part.market) f.market = `eq.${part.market}`;
  if (part.ba) f.entity = `eq.eia930:${part.ba.toUpperCase()}`;
  return [neu, f];
}
const FUEL = { "Henry Hub natural gas": "eia:henry_hub", "WTI Cushing crude": "eia:wti_cushing", "Brent crude": "eia:brent" };

function tzOffsetMs(utcMs, tz) {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit",
    day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" }).formatToParts(new Date(utcMs)).map((x) => [x.type, x.value]));
  return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second) - utcMs;
}
function localMidnight(y, m, d, tz) {
  const guess = Date.UTC(y, m, d);
  return new Date(guess - tzOffsetMs(guess - tzOffsetMs(guess, tz), tz));
}
function isoWeekMonday(label) {
  const [y, w] = label.split("-W").map(Number);
  const jan4 = new Date(Date.UTC(y, 0, 4));
  const mon = new Date(jan4.getTime() - ((jan4.getUTCDay() + 6) % 7) * 864e5);
  return new Date(mon.getTime() + (w - 1) * 7 * 864e5);
}
const cells = (row) => [...row.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((m) => decode(m[1].replace(/<[^>]+>/g, "")).trim());

async function checkWeekly(lines) {
  // session 23: Energy Week became the Energy Roundup (/roundup; /weekly redirects there)
  const html = await fetch(base + "/roundup").then((r) => r.text());
  const label = (html.match(/(?:Energy Week|Energy Roundup|ERW&#x27;s Roundup|ERW's Roundup), (\d{4}-W\d{2})/) || [])[1];
  if (!label) return [0, 0];
  const mon = isoWeekMonday(label);
  let ok = 0, bad = 0;
  const report = (pass, what, shown, truth) => {
    pass ? ok++ : bad++;
    lines.push(`${pass ? "ok  " : "FAIL"} | /roundup | ${what} | page shows "${shown}" | Supabase ${truth}`);
  };
  for (const row of html.split("<tr>").slice(1)) {
    const c = cells(row);
    if (HUB[c[0]] && c.length >= 5) {
      const [table, tz] = HUB[c[0]];
      for (const [k, back] of [[2, 0], [3, 7]]) {
        if (!/^-?\d+\.\d{2}$/.test(c[k])) continue;
        const d0 = new Date(mon.getTime() - back * 864e5);
        const s0 = localMidnight(d0.getUTCFullYear(), d0.getUTCMonth(), d0.getUTCDate(), tz);
        const s1 = localMidnight(d0.getUTCFullYear(), d0.getUTCMonth(), d0.getUTCDate() + 7, tz);
        const [t, f] = current(table, { node: `eq.${c[1]}`, and: `(ts_utc.gte.${s0.toISOString()},ts_utc.lt.${s1.toISOString()})` });
        const rows = await all("series", { select: "value", table_name: `eq.${t}`, ...f, order: "ts_utc" });
        const hours = (s1 - s0) / 36e5;
        // exact: prices summed as integers of millionths, the mean rounded half up to cents (as brief.mean2)
        const micro = rows.reduce((a, r) => a + Math.round(r.value * 1e6), 0);
        const x = micro / rows.length / 1e4;
        const cents = rows.length ? Math.sign(x) * Math.floor(Math.abs(x) + 0.5) : NaN; // half away from zero, as ROUND_HALF_UP
        const truth = rows.length === hours ? (cents / 100).toFixed(2) : `${rows.length} of ${hours} hours`;
        report(truth === c[k], `dam_week_mean|${table}|${c[1]}|${back ? "week before" : "week"}`, c[k], truth);
      }
    }
    if (FUEL[c[0]]) {
      for (const k of [1, 2]) {
        const m = c[k].match(/^(\d+\.\d{2}) .*?on (\d{4}-\d{2}-\d{2})$/);
        if (!m) continue;
        const r = (await q("series", { select: "value", table_name: "eq.eia_fuel_spot_prices", entity: `eq.${FUEL[c[0]]}`,
          ts_utc: `eq.${m[2]}T00:00:00Z` }))[0];
        report(r && r.value.toFixed(2) === m[1], `fuel_close|${FUEL[c[0]]}|${m[2]}`, m[1], r ? r.value.toFixed(2) : "absent");
      }
    }
  }
  const text = decode(html.replace(/<[^>]+>/g, ""));
  // session 21: the table is a footnote ("lmp_rtm_15m_mean [2]", and "[2] nyiso_rtm_zone_prices (...)" in the Tables list)
  const foot = Object.fromEntries([...text.matchAll(/\[(\d+)\] ([a-z0-9_]+) \(/g)].map((m) => [m[1], m[2]]));
  const m0 = text.match(/Highest real-time price of the week:\s*([\d,.]+) USD\/MWh at (.+?) \([A-Z-]+\), interval starting .*?\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\), (\w+) \[(\d+)\]/);
  const rt = m0 ? [m0[0], m0[1], m0[2], m0[3], m0[4], foot[m0[5]]] : null;
  if (rt && rt[5]) {
    const [t, f] = current(rt[5], { node: `eq.${rt[2]}`, variable: `eq.${rt[4]}`, ts_utc: `eq.${rt[3].replace(" ", "T")}:00Z` });
    const r = (await q("series", { select: "value", table_name: `eq.${t}`, ...f }))[0];
    report(r && r.value.toFixed(2) === rt[1], `rt_peak|${rt[5]}|${rt[2]}|${rt[3]}`, rt[1], r ? r.value.toFixed(2) : "absent");
  }
  const pk = text.match(/US48 peak demand of the week:\s*([\d,]+) MW in the hour starting (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC.*?to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC/);
  if (pk) {
    const to = new Date(pk[3].replace(" ", "T") + ":00Z");
    const [t, f] = current("eia930_us48_demand", { variable: "eq.demand_mw",
      and: `(ts_utc.gte.${mon.toISOString()},ts_utc.lte.${to.toISOString()})` });
    const rows = await all("series", { select: "value,ts_utc", table_name: `eq.${t}`, ...f, order: "ts_utc" });
    const top = rows.reduce((a, r) => (a === null || r.value > a.value ? r : a), null);
    const truth = top ? `${Math.round(top.value).toLocaleString("en-US")} at ${new Date(top.ts_utc).toISOString().slice(0, 16).replace("T", " ")}` : "absent";
    report(truth === `${pk[1]} at ${pk[2]}`, "us48_peak_week", `${pk[1]} at ${pk[2]}`, truth);
  }
  return [ok, bad];
}

async function main() {
  const tok = env("INTERNAL_COSTS_TOKEN");
  // session 67, the release gate (lib/release.ts): the pages are read with the internal cookie, so the pages in review
  // are still checked; without it they would answer the in-review page, which carries no number
  let cookie = "";
  if (tok) {
    const u = await unlockPost(base, tok);
    cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  }
  if (!cookie) console.log(`no internal cookie from ${base}/internal/unlock: pages in review answer the in-review page and are counted as failures`);
  const urls = PAGES.filter(wanted).map((page) => ({ page, url: page }));
  // session 371 (docs/security.md, S2): the two drafts open with the internal cookie, so the token is no longer written into
  // their address (until then `${page}?token=...`, which put the production token in a production address at each landing)
  if (tok) urls.push(...INTERNAL.filter(wanted).map((page) => ({ page, url: page, internal: true })));
  else console.log(`internal pages not checked (INTERNAL_COSTS_TOKEN not set here): ${INTERNAL.join(", ")}`);

  // Session 430: the pages are read one at a time, in batches, each under its own timeout (scripts/check-values-run.mjs).
  // A page and the keys first seen on it are one unit, judged when the page is read; the weekly brief is one more unit.
  const WEEKLY = "/roundup (the weekly brief's table)";
  const ids = urls.map((u) => u.page);
  if (!ONLY.length) ids.push(WEEKLY);
  const byPage = new Map(urls.map((u) => [u.page, u]));
  const STATE_FILE = process.env.CHECK_VALUES_STATE ?? path.join(here, "..", "..", "runs", "check-values", "state.json");
  const skey = RUN.stateKey(base, ONLY);
  let state = { key: skey, started_utc: new Date().toISOString(), pages: {} };
  if (process.env.CHECK_VALUES_RESUME === "1") {
    const { state: s, why } = RUN.loadState(STATE_FILE, skey);
    if (s) {
      state = s;
      console.log(`resumed from ${STATE_FILE}: ${Object.keys(s.pages).length} of ${ids.length} pages read by an earlier run are kept, the others read now`);
    } else console.log(why);
  }
  const seen = new Set(Object.values(state.pages).flatMap((r) => r.keys ?? []));   // the keys judged on an earlier page
  const truths = new Map();   // one query a key, whichever page it is judged on

  async function readOne({ page, url, internal }, signal) {
    const out = { page, lines: [], ok: 0, bad: 0, superseded: 0, n: 0, keys: [], count: 0 };
    const res = await fetch(base + url, { headers: cookie ? { Cookie: cookie } : {} });
    if (internal && res.status === 404) {  // the server has no INTERNAL_COSTS_TOKEN (or another): the page is off there
      out.skipped = `internal page not checked: ${page} answers 404 at ${base} (its INTERNAL_COSTS_TOKEN is not this one)`;
      return out;
    }
    if (!res.ok) throw new Error(`${page}: HTTP ${res.status}`);
    const html = await res.text();
    if (html.includes('data-in-review="1"')) throw new Error(`${page}: the in-review page was served (no internal cookie, or the server's token is not this one)`);
    const re = /<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g;
    const ms = [...html.matchAll(re)];
    out.count = ms.length;   // session 268: the keys the page carried, counted before keys shared with a page read earlier are set aside
    // session 369 (todo 008): on an event page, the date the page writes beside the figure (from the text between the
    // figures around it), and every event page that carries the key, each reported on its own line
    const ev = ED.isEventPage(page);
    const onPage = new Map();
    for (const [i, m] of ms.entries()) {
      const text = decode(m[3].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).trim();
      const check = decode(m[1]);
      const usdFormat = html.slice(Math.max(0, m.index - 30), m.index).endsWith('<span data-format="usd">');
      const written = ev ? ED.besideOf(html, ms, i) : null;
      const o = onPage.get(check);
      if (!o) onPage.set(check, { raw: decode(m[2]), text, usdFormat, written: written ? [written] : [] });
      else if (written && !o.written.includes(written)) o.written.push(written);
    }
    for (const [check, { raw, text, usdFormat, written }] of onPage) {
      const first = !seen.has(check);
      if (!first && !ev) continue;   // a key judged on an earlier page is not judged again, but on an event page
      out.keys.push(check);
      let t;
      if (truths.has(check)) t = truths.get(check);
      else {
        try {
          t = await truth(check);
        } catch (e) {
          if (RUN.isTimeout(e)) throw e;   // the database's slowness: the page waits for its second try
          out.bad++;
          out.n++;
          out.lines.push(`FAIL | ${page} | ${check} | the check's own query failed: ${e.message}`);
          continue;
        }
        truths.set(check, t);
      }
      if (t && t.latest) {
        const lag = (new Date(t.ts).getTime() - new Date(t.pageTs).getTime()) / 60000;
        if (lag !== 0 && !first) continue;   // a latest price not comparable by value is reported once, on its first page
        if (lag > 0) {
          const pass = lag <= LATEST_LAG_MIN && text.startsWith(shown(raw));
          pass ? out.superseded++ : out.bad++;
          out.n++;
          out.lines.push(`${pass ? "late" : "FAIL"} | ${page} | ${check} | page shows "${text}" for the interval starting ${t.pageTs} | Supabase now holds ${t.ts} (${lag} minutes later; the earlier interval is held nowhere to compare)${pass ? "" : `: more than ${LATEST_LAG_MIN} minutes behind`}`);
          continue;
        }
        if (lag < 0) {
          out.bad++;
          out.n++;
          out.lines.push(`FAIL | ${page} | ${check} | the page's interval ${t.pageTs} is newer than Supabase's ${t.ts}`);
          continue;
        }
        t = t.value;
      }
      const isTime = /^\d{4}-\d{2}-\d{2}T/.test(raw);
      // sums of floats may differ in the last bits with the order of addition: relative tolerance
      // session 315: a figure written as text in its own file (a card's callout, "126.6x") is compared as text
      const same = isTime ? new Date(t).getTime() === new Date(raw).getTime() : (typeof t === "string" && Number.isNaN(Number(t))) ? t === raw : Math.abs(Number(t) - Number(raw)) < 1e-9 * Math.max(1, Math.abs(Number(t)));
      // session 16: MW sums are written as whole MW (lib/format.ts count)
      // session 90: /storage/buildout writes its MW and MWh whole too (lib/buildout.ts WHOLE; the ratios keep two decimals)
      // session 354: ERCOT's load in each of the four summer peak intervals, written whole (/cost-of-power)
      // session 461's landing: the datacenter queue's active MW by grid, written whole (/datacenters?view=grids, session 468)
      // session 497: the queue's active MW on /datacenters?view=grids, written whole (app/datacenters/GridsView.tsx whole())
      // session 712: the All grids tab writes MW coming, the year's USD and MWh, B less A in USD and capacity over peak whole
      const whole = /(^projects\|mw\|)|(^dcq\|[^|]+\|[^|]+\|active_mw$)|(^datacenters\|(mw_total|state_mw|operator_mw|status_mw|sites_mw|texas_mw))|(^series\|ercot_large_load_status\|)|(^series\|ercot_4cp_intervals\|)|(^series\|storage_buildout_monthly\|[^|]+\|(battery|solar)_(operating|planned)_(mw|mwh)(?!_per_)(_|\|))|(^series\|eia930_demand_growth\|[^|]+\|(avg_demand_mw|peak_demand_mw|ytd_avg_demand_mw|growth_mw_))|(^allgrids\|(planned|year|mwh|yeardiff|capratio)\|)/.test(check);
      // session 76: an hour of the day (a variable named ..._hour, a whole number 0 to 23) may be written "09:00" (/shoulder):
      // "16:00" passed the rule below by accident, "09:00" could not
      const hourText = /\|[a-z0-9_]*_hour\|/.test(check) && /^\d{1,2}$/.test(raw) && text.startsWith(`${raw.padStart(2, "0")}:00`);
      // session 315: a figure the page shows as its own raw text (a card's callout "126.6x", a record's figure as written) is its text
      // a card's p value (FindingCard fmtP): "< 0.001" under a thousandth, else three decimals
      const pText = /^finding\|[^|]+\|effect\|\d+\|p\|/.test(check) && (Number(raw) < 0.001 ? text === "< 0.001" : text === Number(raw).toFixed(3));
      // session 402: a figure of the Digest's chart of the day is written as the chart-maker rounds it (lib/digest.ts chartText)
      const chartOk = /^digest_chart\|/.test(check) && text === digestChartText(Number(raw));
      const textOk = hourText || pText || text === raw || text.startsWith(usdFormat ? usd(Number(raw)) : whole ? Math.round(Number(raw)).toLocaleString("en-US") : shown(raw)) || chartOk;
      let pass = t !== undefined && t !== null && same && textOk;
      // session 369 (todo 008): on an event page, the date the figure belongs to is named on its line; a series figure
      // is compared with the row of that date among its entity's rows (never another day's), an estimate of a day with
      // that day's, and a date the page writes beside the figure must be the same date
      let of = "";
      if (ev) {
        const kd = ED.keyDate(check);
        const rows = !kd || kd.window ? [] : check.startsWith("series|") ? await eventRows(check) : [{ ts_utc: `${kd.date}T00:00:00Z`, value: t }];
        const w = written.find((x) => kd && !kd.window && x !== kd.date) ?? written[0] ?? null;
        const d = ED.compareDated({ check, raw, written: w }, rows);
        if (d.pass === false) pass = false;
        of = ` of ${d.label}${d.why ? ` (${d.why})` : ""} |`;
      }
      pass ? out.ok++ : out.bad++;
      out.n++;
      out.lines.push(`${pass ? "ok  " : "FAIL"} | ${page} | ${check} |${of} page shows "${text}" | page read ${raw} | Supabase ${t}`);
    }
    const floor = FLOOR[page];
    if (floor !== undefined && out.count < floor) {
      out.bad++;
      out.lines.push(`FAIL | ${page} | the floor | the page carries ${out.count} checked numbers; its floor is ${floor} (scripts/check-values-floor.json): a read failed and the page drew fewer numbers, or a number lost its key`);
    }
    // session 408: a page read here with no floor is said on its own line (not a failure): a run with
    // CHECK_VALUES_WRITE_FLOOR=1 that passes in full gives it one
    if (floor === undefined) out.lines.push(`note | ${page} | the floor | the page carries ${out.count} checked numbers and has no floor in scripts/check-values-floor.json`);
    if (!signal.aborted) for (const k of out.keys) seen.add(k);   // a page that ran out of time leaves its keys to the next
    return out;
  }
  async function readWeekly() {
    const lines = [];
    const [wok, wbad] = await checkWeekly(lines);
    return { page: WEEKLY, lines, ok: wok, bad: wbad, superseded: 0, n: wok + wbad, keys: [], weekly: true };
  }
  async function readPage(page, signal) {
    pageSignal = signal;
    // a timeout leaves a cached read rejected: the page's second try reads again
    signal.addEventListener("abort", () => { dcAnswers.clear(); dcllRows.clear(); dcqRows.clear(); }, { once: true });
    try {
      return page === WEEKLY ? await readWeekly() : await readOne(byPage.get(page), signal);
    } finally {
      if (pageSignal === signal) pageSignal = null;
    }
  }
  const t0 = Date.now();
  function commit(results) {
    for (const [page, r] of results) {
      if (state.pages[page]) continue;
      state.pages[page] = r.error
        ? { page, lines: [`FAIL | ${page} | the page | ${r.error.message}`], ok: 0, bad: 1, superseded: 0, n: 0, keys: [] }
        : r;
    }
    try {
      RUN.saveState(STATE_FILE, { ...state, saved_utc: new Date().toISOString() });
    } catch (e) {
      console.log(`the state file could not be written (${e.message}); a second run cannot resume this one`);
    }
  }
  const { results, notRead } = await RUN.runPages({
    pages: ids, readPage, pageMs: PAGE_S * 1000, deadline: RUN_START + RUN_MIN * 60 * 1000, batch: BATCH,
    done: new Set(Object.keys(state.pages)),
    onBatch: ({ results: rs, notRead: nr, pending }) => {
      commit(rs);
      console.log(`progress | ${Object.keys(state.pages).length} of ${ids.length} read | ${pending.length} waiting for a second try | ${nr.length} not read | ${((Date.now() - t0) / 60000).toFixed(1)} minutes`);
    },
    onRetry: (page) => console.log(`retry | ${page} | timed out once; tried again`),
  });
  commit(results);

  const done = ids.filter((p) => state.pages[p]).map((p) => state.pages[p]);
  for (const r of done) if (r.skipped) console.log(r.skipped);
  const lines = done.flatMap((r) => r.lines);
  let ok = 0, bad = 0, superseded = 0, n = 0;
  for (const r of done) { ok += r.ok; bad += r.bad; superseded += r.superseded; n += r.n; }
  const wk = state.pages[WEEKLY];
  const [wok, wbad] = [wk?.ok ?? 0, wk?.bad ?? 0];
  // session 430: what this run could not read, a page a line; their floors are not judged and the run is not a pass
  const why = new Map(notRead.map((x) => [x.page, x.why]));
  const missing = ids.filter((p) => !state.pages[p]);
  for (const p of missing) lines.push(`not read | ${p} | ${why.get(p) ?? "not reached"} | its numbers and its floor are not judged`);
  console.log(lines.join("\n"));
  if (ONLY.length) console.log(`\nRESTRICTED RUN (CHECK_VALUES_PAGES): only the pages starting with ${ONLY.join(", ")}; not the gate of a landing`);
  console.log(`\n${ok} of ${n} values match Supabase${superseded ? `; ${superseded} latest prices superseded by a newer interval within ${LATEST_LAG_MIN} minutes (checked for staleness, not comparable by value)` : ""}${bad ? `; ${bad} FAILED` : ""} (/roundup: ${wok} of ${wok + wbad})${missing.length ? `; ${missing.length} of ${ids.length} pages NOT READ` : ""}`);
  if (n < 10) console.log(`check-values FAILED: ${n} values checked, fewer than the floor of ten a run`);
  const perPage = new Map(done.filter((r) => !r.weekly && !r.skipped && r.count !== undefined).map((r) => [r.page, r.count]));
  if (process.env.CHECK_VALUES_WRITE_FLOOR === "1") {
    if (bad || n < 10 || missing.length) console.log(`the floor file was not written: the run did not pass${missing.length ? " (not every page was read)" : ""}`);
    else if (ONLY.length) {
      // session 403: a restricted run that passes in full adds (or sets again) the floors of the pages it read and only
      // those, so a new page gets its floor without a full run moving every other page's; the other lines stay as written
      const kept = fs.existsSync(FLOOR_FILE) ? JSON.parse(fs.readFileSync(FLOOR_FILE, "utf-8")) : { floor: {} };
      const merged = { ...kept.floor };
      for (const [page, count] of perPage) merged[page] = Math.min(10, count);
      const floor = Object.fromEntries(Object.entries(merged).sort(([a], [b]) => a.localeCompare(b)));
      fs.writeFileSync(FLOOR_FILE, JSON.stringify({ ...kept, floor }, null, 2) + "\n");
      console.log(`the floor file was updated for ${perPage.size} pages of a restricted run (${ONLY.join(", ")}); every other page's floor is as it was`);
    } else {
      const floor = Object.fromEntries([...perPage].sort(([a], [b]) => a.localeCompare(b)).map(([page, count]) => [page, Math.min(10, count)]));
      fs.writeFileSync(FLOOR_FILE, JSON.stringify({ note: "session 268: the smaller of ten and the checked numbers each page carried in a passing full run of check-values.mjs; written with CHECK_VALUES_WRITE_FLOOR=1", written_utc: new Date().toISOString(), base, floor }, null, 2) + "\n");
      console.log(`the floor file was written: ${perPage.size} pages`);
    }
  }
  // session 430: a run that read some pages and failed none, but could not read them all, is incomplete: exit 3, never 0,
  // so no landing takes it for a pass; CHECK_VALUES_RESUME=1 reads only the pages it left
  if (!bad && missing.length) {
    console.log(`check-values INCOMPLETE: ${missing.length} pages not read; every value read matched. Run again with CHECK_VALUES_RESUME=1 to read only those (state: ${STATE_FILE})`);
    // the run ends by itself with this code rather than by process.exit: on Windows, process.exit while a socket is
    // closing can end node with 0xC0000409 (a libuv assertion, seen once in six runs on 21 October), and a script that
    // reads 3 to resume must get 3
    process.exitCode = 3;
    return;
  }
  if (bad || n < 10) process.exit(1);
}

main().catch((e) => {
  console.error(`check-values FAILED: ${e.message}`);
  process.exit(1);
});
