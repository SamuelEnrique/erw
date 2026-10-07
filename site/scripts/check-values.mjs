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
// Session 72: it cannot hang. Every request has a hard timeout (CHECK_VALUES_REQUEST_S, default 60 s) and the whole run
// one too (CHECK_VALUES_TIMEOUT_MIN, default 15 minutes): past it the run fails, loudly, with exit 1 (session 71's third
// run hung for 70 minutes on the network). And it does not flake on the latest prices: their key carries the interval
// the page shows (latest_prices|<entity>|<variable>|<ts_utc>). Supabase's latest_prices holds one row per entity, the
// newest interval, and no earlier one anywhere. So: the same interval in Supabase, the values must be equal; a newer
// interval in Supabase (the page was cached before the 15-minute refresh), the key is "superseded", reported on its own
// line and in the summary, and passes only if the page's interval is at most 45 minutes behind Supabase's (the page's
// 15-minute cache, the refresh and the run's own length); any other case fails. No key is dropped.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const REQUEST_MS = Number(process.env.CHECK_VALUES_REQUEST_S ?? 60) * 1000;
const RUN_MIN = Number(process.env.CHECK_VALUES_TIMEOUT_MIN ?? 15);
const LATEST_LAG_MIN = 45;
{
  const plain = globalThis.fetch;
  globalThis.fetch = (url, opts = {}) => plain(url, { ...opts, signal: opts.signal ?? AbortSignal.timeout(REQUEST_MS) });
  setTimeout(() => {
    console.error(`check-values FAILED: the run passed its ${RUN_MIN}-minute limit (CHECK_VALUES_TIMEOUT_MIN); nothing is reported as checked`);
    process.exit(1);
  }, RUN_MIN * 60 * 1000).unref();
}

const here = path.dirname(fileURLToPath(import.meta.url));
const base = process.argv[2] ?? "http://localhost:3000";
const PAGES = ["/", "/board", "/emissions", "/storage", "/prices", "/prices/ercot%3AHB_HUBAVG", "/data", "/explorer/ercot-peak-premium", "/deals", "/grid", "/map", "/datacenters", "/roundup",
  // session 18
  "/mix", "/mix?ba=erco&state=TX", "/curtailment", "/consumption",
  // session 19
  // session 35: the seven grid pages
  "/grid/ercot", "/grid/caiso", "/grid/pjm", "/grid/nyiso", "/grid/isone", "/grid/miso", "/grid/spp",
  // session 36B: the Historical Event Analyzer
  "/events/uri-2021",
  // session 36C
  "/events/covid-2020",
  // session 37: the cost-of-power model (session 138: what the tab showed until then is the page's view "Grid by grid")
  "/cost-of-power?view=grids",
  // session 51: the seller's tab, its defaults and three other assets
  "/cost-of-power/seller", "/cost-of-power/seller?asset=battery", "/cost-of-power/seller?asset=peaker", "/cost-of-power/seller?iso=spp&asset=wind",  // session 145: MISO is blank on the page, so the fourth view is SPP's wind
  // session 38: today's level's price range
  "/play/battery", "/play/battery?more=1",  // session 63: the simple page and the full game
  // session 39: three more events
  "/events", "/events/caiso-heat-2020", "/events/elliott-2022", "/events/ercot-heat-2023",
  // session 58: CAISO's September 2022 heat
  "/events/caiso-heat-2022",
  // session 64: the January 2025 cold and the June 2025 heat
  "/events/cold-2025", "/events/east-heat-2025",
  // session 43: the bill explainer's default bills
  "/learn/bill",
  // session 44: every computed answer of the problem sets
  "/learn/problems/know-your-grid", "/learn/problems/prices-and-your-bill", "/learn/problems/when-the-grid-broke", "/learn/problems/storage-and-taxes",
  // session 55: set E, networks and money
  "/learn/problems/networks-and-money",
  // session 49: the network's default node card (ERCOT)
  "/network",
  // session 72 (session 69's finish): the storage build-out
  "/storage/buildout", "/storage/buildout?grid=ercot&measure=mwh", "/storage/buildout?grid=caiso",
  "/shoulder", "/shoulder?grid=caiso&month=2025-07",  // session 75
  // session 67: what a battery earns: both grids, the three durations, both strategies, another size
  "/cost-of-power/battery", "/cost-of-power/battery?grid=ercot&dur=2&strat=foresight", "/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead",
  "/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead", "/cost-of-power/battery?grid=caiso&dur=4&strat=foresight", "/cost-of-power/battery?grid=caiso&dur=2&strat=dayahead",
  "/cost-of-power/battery?grid=caiso&dur=8&strat=foresight&mw=250",
  // session 60: the Flex Alert scorecard
  "/grid/caiso/alerts"];  // (the line ended "// session 46: set D" before session 60)
// session 48: the draft report behind the internal token (INTERNAL_COSTS_TOKEN, in .env.local or the environment); left
// out, and said so, where the token is not set (the page answers 404 without it)
const INTERNAL = ["/reports/draft/shape-premium", "/reports/draft/ai-gigawatts"];  // session 62: the AI gigawatts draft
// session 35: the grid pages' config, for their news and datacenter keys (the same file the pages read)
const GRIDS = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "docs", "grids", "grids.json"), "utf-8")).grids;

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

/** The value Supabase holds for one data-check key. */
async function truth(check) {
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
  if (p[0] === "series") {
    const [, table, entity, variable, at, event] = p;
    const params = { select: "value,ts_utc", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${variable}` };
    if (event) params.event = `eq.${event}`; // session 36C: event_window_daily's key includes its event
    if (at === "newest") Object.assign(params, { order: "ts_utc.desc", limit: "1" });
    else params.ts_utc = `eq.${at}`;
    return (await q("series", params))[0]?.value;
  }
  // session 15: /deals and /grid
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
    const [, what, key] = p;
    const rows = await all("entities", { select: "operator,mw:capacity_mw,state:extra->>state", table_name: "eq.datacenter_facilities", order: "entity_id" });
    const withMw = rows.filter((r) => r.mw !== null);
    if (what === "count") return rows.length;
    if (what === "n_with_mw") return withMw.length;
    if (what === "mw_total") return withMw.reduce((a, r) => a + Number(r.mw), 0);
    if (what === "state_mw") return withMw.filter((r) => r.state === key).reduce((a, r) => a + Number(r.mw), 0);
    if (what === "operator_mw") return withMw.filter((r) => r.operator === key).reduce((a, r) => a + Number(r.mw), 0);
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
  // session 51: the seller's tab: recomputed from the snapshot the page reads (data/merchant_snapshot.json, not Supabase),
  // with lib/merchant.ts; tests/test_session51.py checks the snapshot against the warehouse table and by hand
  if (p[0] === "mr") {
    const M = await import("../lib/merchant.ts");
    const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "merchant_snapshot.json"), "utf-8"));
    return M.stat(snap, M.parseKey(p[1]), p[2]);
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

/** US dollars, short, as site/app/deals/DealsTable.tsx writes them (data-format usd). */
function usd(v) {
  const t = (x) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
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
  const found = new Map();
  const tok = env("INTERNAL_COSTS_TOKEN");
  // session 67, the release gate (lib/release.ts): the pages are read with the internal cookie, so the pages in review
  // are still checked; without it they would answer the in-review page, which carries no number
  let cookie = "";
  if (tok) {
    const u = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(tok)}`, { redirect: "manual" });
    cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  }
  if (!cookie) console.log(`no internal cookie from ${base}/internal/unlock: pages in review answer the in-review page and are counted as failures`);
  const urls = PAGES.map((page) => ({ page, url: page }));
  if (tok) urls.push(...INTERNAL.map((page) => ({ page, url: `${page}?token=${encodeURIComponent(tok)}`, internal: true })));
  else console.log(`internal pages not checked (INTERNAL_COSTS_TOKEN not set here): ${INTERNAL.join(", ")}`);
  for (const { page, url, internal } of urls) {
    const res = await fetch(base + url, { headers: cookie ? { Cookie: cookie } : {} });
    if (internal && res.status === 404) {  // the server has no INTERNAL_COSTS_TOKEN (or another): the page is off there
      console.log(`internal page not checked: ${page} answers 404 at ${base} (its INTERNAL_COSTS_TOKEN is not this one)`);
      continue;
    }
    if (!res.ok) throw new Error(`${page}: HTTP ${res.status}`);
    const html = await res.text();
    if (html.includes('data-in-review="1"')) throw new Error(`${page}: the in-review page was served (no internal cookie, or the server's token is not this one)`);
    const re = /<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g;
    for (const m of html.matchAll(re)) {
      const text = decode(m[3].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).trim();
      const check = decode(m[1]);
      const usdFormat = html.slice(Math.max(0, m.index - 30), m.index).endsWith('<span data-format="usd">');
      if (!found.has(check)) found.set(check, { page, raw: decode(m[2]), text, usdFormat });
    }
  }
  let ok = 0, bad = 0, superseded = 0;
  const lines = [];
  for (const [check, { page, raw, text, usdFormat }] of found) {
    let t = await truth(check);
    if (t && t.latest) {
      const lag = (new Date(t.ts).getTime() - new Date(t.pageTs).getTime()) / 60000;
      if (lag > 0) {
        const pass = lag <= LATEST_LAG_MIN && text.startsWith(shown(raw));
        pass ? superseded++ : bad++;
        lines.push(`${pass ? "late" : "FAIL"} | ${page} | ${check} | page shows "${text}" for the interval starting ${t.pageTs} | Supabase now holds ${t.ts} (${lag} minutes later; the earlier interval is held nowhere to compare)${pass ? "" : `: more than ${LATEST_LAG_MIN} minutes behind`}`);
        continue;
      }
      if (lag < 0) {
        bad++;
        lines.push(`FAIL | ${page} | ${check} | the page's interval ${t.pageTs} is newer than Supabase's ${t.ts}`);
        continue;
      }
      t = t.value;
    }
    const isTime = /^\d{4}-\d{2}-\d{2}T/.test(raw);
    // sums of floats may differ in the last bits with the order of addition: relative tolerance
    const same = isTime ? new Date(t).getTime() === new Date(raw).getTime() : Math.abs(Number(t) - Number(raw)) < 1e-9 * Math.max(1, Math.abs(Number(t)));
    // session 16: MW sums are written as whole MW (lib/format.ts count)
    // session 90: /storage/buildout writes its MW and MWh whole too (lib/buildout.ts WHOLE; the ratios keep two decimals)
    const whole = /(^projects\|mw\|)|(^datacenters\|(mw_total|state_mw|operator_mw))|(^series\|storage_buildout_monthly\|[^|]+\|(battery|solar)_(operating|planned)_(mw|mwh)(?!_per_)(_|\|))/.test(check);
    // session 76: an hour of the day (a variable named ..._hour, a whole number 0 to 23) may be written "09:00" (/shoulder):
    // "16:00" passed the rule below by accident, "09:00" could not
    const hourText = /\|[a-z0-9_]*_hour\|/.test(check) && /^\d{1,2}$/.test(raw) && text.startsWith(`${raw.padStart(2, "0")}:00`);
    const textOk = hourText || text.startsWith(usdFormat ? usd(Number(raw)) : whole ? Math.round(Number(raw)).toLocaleString("en-US") : shown(raw));
    const pass = t !== undefined && t !== null && same && textOk;
    pass ? ok++ : bad++;
    lines.push(`${pass ? "ok  " : "FAIL"} | ${page} | ${check} | page shows "${text}" | page read ${raw} | Supabase ${t}`);
  }
  const [wok, wbad] = await checkWeekly(lines);
  ok += wok;
  bad += wbad;
  const n = found.size + wok + wbad;
  console.log(lines.join("\n"));
  console.log(`\n${ok} of ${n} values match Supabase${superseded ? `; ${superseded} latest prices superseded by a newer interval within ${LATEST_LAG_MIN} minutes (checked for staleness, not comparable by value)` : ""}${bad ? `; ${bad} FAILED` : ""} (/roundup: ${wok} of ${wok + wbad})`);
  if (bad || n < 10) process.exit(1);
}

main().catch((e) => {
  console.error(`check-values FAILED: ${e.message}`);
  process.exit(1);
});
