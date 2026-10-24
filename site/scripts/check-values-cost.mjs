// Energy Research Warehouse (ERW) site, session 1186 (chain 091): what check-values.mjs costs on the Grid tool's pages,
// measured without a build or a server.
//
//   node scripts/check-values-cost.mjs --env <file holding SUPABASE_URL and SUPABASE_ANON_KEY> --out <dir>
//     [--cv <a check-values script>[,<another>]] [--alone] [--kinds] [--perturb] [--only <address>[,<address>...]]
//     [--proxy <the address of a proxy started with --serve-proxy>]
//   node scripts/check-values-cost.mjs --env <file> --out <dir> --serve-proxy <port>   (the proxy alone, kept open)
//
// 1. The pages are drawn outside Next, as scripts/same-figures.mjs draws them (a child node with scripts/alias-register.mjs
//    and tsx-register.mjs, one render of React's `cache` a page), to their HTML (same-figures' reduceTree and htmlOf: every
//    host element the server draws, Num's spans among them). Each address check-values reads under /grid (and its old
//    addresses that redirect into the tool: /emissions, /mix, /network, /grid/<iso>, by next.config.ts's rules) is drawn
//    once a target. The HTML is kept in --out/pages; the answers are never written.
// 2. A local site on 127.0.0.1 serves that HTML at check-values' own addresses (and answers its /internal/unlock), and a
//    proxy on 127.0.0.1 stands where SUPABASE_URL points: each distinct request (the REST API and the public Storage
//    object alike) is sent to Supabase once, one at a time, with the anon key, and every answer is kept in memory. Every
//    request is counted against the phase it belongs to (the page drawn, or the page check-values is reading): the asks
//    (a repeat answered from memory counts, as Supabase would have answered it again), the distinct requests, the rows
//    (PostgREST's Content-Range, else the answer's array) and bytes, and an estimate of the time (the first answer's
//    milliseconds, counted at each ask). With --proxy, a proxy kept open by --serve-proxy is used, so several runs of this
//    script share its answers and no distinct request is sent to Supabase twice in a session.
// 3. Each check-values script named by --cv (default scripts/check-values.mjs) is run, unchanged, against the local site
//    and the proxy: every Grid address in one run (as a landing's run reads them, a key judged on its first page), and
//    with --alone each address in a run of its own (CHECK_VALUES_PAGES, the site answering that address only). With
//    --kinds, one run more a key kind, every page served with that kind's keys alone, so the cost of a kind is seen.
//    With --perturb, one run more with every data-raw moved, so every key must fail, and fail the same way in each script.
// 4. --out gets pages/, each run's output (cv_<tag>.out), and cost.json: per run and per page the asks, distinct requests,
//    rows, bytes and estimated ms, the page's own draw beside it, and the key lines of each run. Two scripts are compared
//    line by line: the key lines (ok, FAIL, late, revised, same, DIFF, file) must be equal, value for value within 1e-12.
//    Exit 0 when every pair of runs agrees, 1 when one differs, 2 on bad usage.
//
// Only SUPABASE_URL and SUPABASE_ANON_KEY are read from the --env file; neither is printed or written.
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));

/** The address check-values reads, to the /grid address it is drawn as (next.config.ts's redirects, a query carried). */
export function targetOf(address) {
  const u = new URL(address, "https://x.invalid");
  const q = [...u.searchParams];
  const join = (base, extra) => {
    const b = new URL(base, "https://x.invalid");
    for (const [k, v] of extra) if (!b.searchParams.has(k)) b.searchParams.append(k, v);
    return b.pathname + b.search;
  };
  if (u.pathname === "/grid" || u.pathname === "/grid/caiso/alerts") return address;
  if (u.pathname === "/emissions") return join("/grid?view=clean", q);
  if (u.pathname === "/network") {
    const v = u.searchParams.get("view");
    return join(v ? `/grid?view=network&net=${v}` : "/grid?view=network", q.filter(([k]) => k !== "view"));
  }
  if (u.pathname === "/mix") {
    const v = u.searchParams.get("view");
    const rest = q.filter(([k]) => k !== "view");
    if (v === "clean") return join("/grid?view=clean", rest);
    return join(v ? `/grid?view=mix&mix=${v}` : "/grid?view=mix", rest);
  }
  const g = /^\/grid\/(ercot|caiso|pjm|nyiso|isone|miso|spp)$/.exec(u.pathname);
  if (g) return join(`/grid?grid=${g[1]}`, q);
  return null;
}

/** A key's kind: its first part, past a fmt|<form>| wrapper. */
export function kindOf(check) {
  const p = check.split("|");
  return p[0] === "fmt" ? (p[2] ?? "fmt") : p[0];
}

const SPAN = /<span data-check="([^"]+)" data-raw="([^"]*)"/g;
const unesc = (s) => s.replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#x27;/g, "'").replace(/&amp;/g, "&");

/** The page with only the keys of one kind left as keys (the others' attribute renamed, so check-values does not see them). */
export function onlyKind(html, kind) {
  return html.replace(SPAN, (all, c, raw) => (kindOf(unesc(c)) === kind ? all : `<span data-x-check="${c}" data-raw="${raw}"`));
}

/** The page with every data-raw moved: a number by 1.5, a time by an hour, any other text marked. */
export function perturbed(html) {
  return html.replace(SPAN, (all, c, raw) => {
    const r = unesc(raw);
    let v;
    if (/^\d{4}-\d{2}-\d{2}T/.test(r) && Number.isFinite(Date.parse(r))) v = new Date(Date.parse(r) + 3_600_000).toISOString();
    else if (r !== "" && Number.isFinite(Number(r))) v = String(Number(r) + 1.5);
    else v = `${r}~moved`;
    return `<span data-check="${c}" data-raw="${v.replace(/&/g, "&amp;").replace(/"/g, "&quot;")}"`;
  });
}

/** The key lines of a check-values output: status, page, key and the rest, a line an entry. */
export function keyLines(text) {
  return text.split(/\r?\n/).filter((l) => /^(ok  |FAIL|late|revised|same|DIFF|file) \| /.test(l)).map((l) => {
    const [status, page, check, ...rest] = l.split(" | ");
    return { status: status.trim(), page, check, rest: rest.join(" | ") };
  });
}

/** Two runs' key lines the same: the same lines in the same order, a number in them equal within 1e-12 of its size. */
export function sameLines(a, b) {
  const diffs = [];
  const nums = (s) => s.split(/(-?\d+(?:\.\d+)?(?:e[-+]?\d+)?)/i);
  const eq = (x, y) => {
    if (x === y) return true;
    const p = nums(x), q = nums(y);
    if (p.length !== q.length) return false;
    return p.every((s, i) => (i % 2 ? Math.abs(Number(s) - Number(q[i])) <= 1e-12 * Math.max(1, Math.abs(Number(s))) : s === q[i]));
  };
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    const x = a[i], y = b[i];
    if (!x || !y || x.status !== y.status || x.page !== y.page || x.check !== y.check || !eq(x.rest, y.rest)) diffs.push({ i, a: x ?? null, b: y ?? null });
  }
  return diffs;
}

/** Rows an answer carried: PostgREST's Content-Range, else its JSON array's length, else one object. */
export function rowsOfAnswer(range, body) {
  const m = /^(\d+)-(\d+)\//.exec(range ?? "");
  if (m) return Number(m[2]) - Number(m[1]) + 1;
  if (/^\*\//.test(range ?? "")) return 0;
  const t = body.subarray(0, 1).toString();
  if (t === "[") { try { return JSON.parse(body.toString()).length; } catch { return 0; } }
  return t === "{" ? 1 : 0;
}

function envFrom(text) {
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    const m = /^\s*(?:export\s+)?(SUPABASE_URL|SUPABASE_ANON_KEY)\s*=\s*(.*)\s*$/.exec(line);
    if (m) out[m[1]] = m[2].replace(/^(["'])(.*)\1$/, "$2");
  }
  return out;
}

/** The child: draw each target to its HTML, one render a page, and say which page is drawn to the proxy first. */
async function drawTargets(targets, out, proxy, run) {
  process.env.ERW_PAGES_TOGETHER = "1";
  for (const k of ["ERW_READ_TIMING", "NEXT_PHASE", "NEXT_RUNTIME", "SUPABASE_SERVICE_KEY"]) delete process.env[k];
  const SF = await import("./same-figures.mjs");
  const grid = await import(pathToFileURL(path.join(here, "..", "app", "grid", "page.tsx")).href);
  const alerts = await import(pathToFileURL(path.join(here, "..", "app", "grid", "caiso", "alerts", "page.tsx")).href);
  const index = {};
  for (const [i, t] of targets.entries()) {
    await fetch(`${proxy}/__phase?name=${encodeURIComponent(`draw#${run} ${t}`)}`);
    globalThis.__erwRequestCache = new Map();
    const fn = t === "/grid/caiso/alerts" ? alerts.default : grid.default;
    const sp = t === "/grid/caiso/alerts" ? {} : SF.paramsOf(t);
    const rec = await SF.figuresOf(fn({ searchParams: Promise.resolve(sp) }));
    const html = SF.htmlOf(await SF.reduceTree(fn({ searchParams: Promise.resolve(sp) })));
    delete globalThis.__erwRequestCache;
    const file = `page_${i}.html`;
    fs.writeFileSync(path.join(out, file), html);
    const spans = [...html.matchAll(SPAN)].length;
    index[t] = { file, nums: rec.nums.length, spans, errors: rec.errors };
    console.log(`${t}: ${rec.nums.length} figures, ${spans} keyed spans in the HTML, ${rec.errors.length} errors`);
  }
  fs.writeFileSync(path.join(out, "index.json"), JSON.stringify(index, null, 1));
}

async function main(args) {
  const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
  if (opt("--draw")) return drawTargets(opt("--draw").split(","), opt("--out"), opt("--proxy"), opt("--run"));
  const envFile = opt("--env"), outDir = opt("--out");
  if (!envFile || !outDir) {
    console.log("usage: check-values-cost.mjs --env <file> --out <dir> [--cv <script>[,<script>]] [--alone] [--kinds] [--perturb] [--only <address>,...]");
    process.exit(2);
  }
  const env = envFrom(fs.readFileSync(envFile, "utf-8"));
  if (!env.SUPABASE_URL || !env.SUPABASE_ANON_KEY) { console.log(`check-values-cost: ${envFile} does not name SUPABASE_URL and SUPABASE_ANON_KEY`); process.exit(2); }
  const origin = new URL(env.SUPABASE_URL).origin;
  const work = path.resolve(outDir), pagesDir = path.join(work, "pages");
  fs.mkdirSync(pagesDir, { recursive: true });
  const cvs = (opt("--cv") ?? "scripts/check-values.mjs").split(",").map((f) => path.resolve(path.join(here, ".."), f));
  if (opt("--serve-proxy")) {   // the proxy alone, kept open, so several measuring runs share its answers
    const p = await startProxy(origin, Number(opt("--serve-proxy")));
    console.log(`proxy ready on ${p.base}`);
    return;
  }
  const own = opt("--proxy") ? null : await startProxy(origin, 0);
  const proxyBase = opt("--proxy") ?? own.base;
  const setPhase = (name) => fetch(`${proxyBase}/__phase?name=${encodeURIComponent(name)}`).then((r) => r.text());
  const statsOf = async (prefix) => (await fetch(`${proxyBase}/__stats?prefix=${encodeURIComponent(prefix)}`)).json();
  await setPhase(`start ${Date.now()}`);
  const upstream0 = (await statsOf("\u0000")).upstream;

  // the addresses check-values reads under the Grid tool
  const list = JSON.parse(await new Promise((resolve) => {
    let o = "";
    const p = spawn(process.execPath, [cvs[0], "--list"], { cwd: path.join(here, "..") });
    p.stdout.on("data", (d) => (o += d));
    p.on("close", () => resolve(o));
  })).pages;
  const only = opt("--only")?.split(",");
  const addresses = list.filter((a) => targetOf(a) !== null && (!only || only.includes(a)));
  const targets = [...new Set(addresses.map(targetOf))];
  console.log(`${addresses.length} addresses check-values reads under the Grid tool, drawn as ${targets.length} pages`);

  const t0 = new Date();
  const draw = await new Promise((resolve) => {
    const childEnv = { ...process.env, SUPABASE_URL: `${proxyBase}/rest/v1/`, SUPABASE_ANON_KEY: env.SUPABASE_ANON_KEY };
    delete childEnv.SUPABASE_SERVICE_KEY;
    const p = spawn(process.execPath, ["--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", fileURLToPath(import.meta.url),
      "--draw", targets.join(","), "--out", pagesDir, "--proxy", proxyBase, "--run", String(t0.getTime())], { cwd: path.join(here, ".."), env: childEnv, stdio: ["ignore", "pipe", "pipe"] });
    let o = "";
    p.stdout.on("data", (d) => (o += d));
    p.stderr.on("data", (d) => (o += d));
    p.on("close", (code) => resolve({ code, o }));
  });
  console.log(draw.o.split(/\r?\n/).filter((l) => !l.startsWith("[erw] license needed")).join("\n"));
  if (draw.code) { console.log(`check-values-cost: the drawing failed (exit ${draw.code})`); process.exit(1); }
  const index = JSON.parse(fs.readFileSync(path.join(pagesDir, "index.json"), "utf-8"));
  const drawStats = await statsOf(`draw#${t0.getTime()} `);
  const html = new Map(addresses.map((a) => [a, fs.readFileSync(path.join(pagesDir, index[targetOf(a)].file), "utf-8")]));
  const kinds = [...new Set([...html.values()].flatMap((h) => [...h.matchAll(SPAN)].map((m) => kindOf(unesc(m[1])))))].sort();

  // the local site: the drawn HTML at check-values' addresses
  let serve = { tag: "", allow: null, kind: null, perturb: false };
  const site = http.createServer(async (req, res) => {
    const u = new URL(req.url, "http://x.invalid");
    if (req.method === "POST" && u.pathname === "/internal/unlock") { res.writeHead(303, { "set-cookie": "erw_view=internal; Path=/", location: "/" }).end(); return; }
    const a = u.pathname + u.search;
    let h = html.get(a);
    if (h === undefined || (serve.allow && !serve.allow.has(a))) { res.writeHead(404).end("not drawn"); return; }
    await setPhase(`cv ${serve.tag} ${a}`);   // check-values reads a page, then its keys, one page at a time
    if (serve.kind) h = onlyKind(h, serve.kind);
    if (serve.perturb) h = perturbed(h);
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" }).end(h);
  });
  await new Promise((r) => site.listen(0, "127.0.0.1", r));
  const siteBase = `http://127.0.0.1:${site.address().port}`;

  const runCv = (cv, tag, pages) => new Promise((resolve) => {
    const childEnv = { ...process.env, SUPABASE_URL: `${proxyBase}/rest/v1/`, SUPABASE_ANON_KEY: env.SUPABASE_ANON_KEY, INTERNAL_COSTS_TOKEN: "cost-run",
      CHECK_VALUES_PAGES: pages, CHECK_VALUES_STATE: path.join(work, `state_${tag}.json`), CHECK_VALUES_TIMEOUT_MIN: "180", CHECK_VALUES_PAGE_S: "3600" };
    for (const k of ["SUPABASE_SERVICE_KEY", "CHECK_VALUES_RESUME", "CHECK_VALUES_WRITE_FLOOR"]) delete childEnv[k];
    const started = performance.now();
    const p = spawn(process.execPath, [cv, siteBase], { cwd: path.join(here, ".."), env: childEnv, stdio: ["ignore", "pipe", "pipe"] });
    let o = "";
    p.stdout.on("data", (d) => (o += d));
    p.stderr.on("data", (d) => (o += d));
    p.on("close", (code) => {
      fs.writeFileSync(path.join(work, `cv_${tag}.out`), o);
      resolve({ code, o, ms: Math.round(performance.now() - started) });
    });
  });
  const PREFIXES = "/grid,/emissions,/mix,/network";
  const runs = [];
  for (const [ci, cv] of cvs.entries()) {
    const name = `s${ci}`;
    const plan = [{ tag: `${name}_all`, pages: PREFIXES, serve: {} }];
    if (args.includes("--alone")) for (const [i, a] of addresses.entries()) plan.push({ tag: `${name}_alone${i}`, pages: a, serve: { allow: new Set([a]) }, alone: a });
    if (args.includes("--kinds")) for (const k of kinds) plan.push({ tag: `${name}_kind_${k}`, pages: PREFIXES, serve: { kind: k }, kind: k });
    if (args.includes("--perturb")) plan.push({ tag: `${name}_perturb`, pages: PREFIXES, serve: { perturb: true }, perturb: true });
    for (const step of plan) {
      serve = { tag: `${step.tag}#${t0.getTime()}`, allow: null, kind: null, perturb: false, ...step.serve };
      const r = await runCv(cv, step.tag, step.pages);
      await setPhase(`idle ${Date.now()}`);
      let lines = keyLines(r.o);
      if (step.alone) lines = lines.filter((l) => l.page === step.alone);
      const st = await statsOf(`cv ${serve.tag} `);
      const per = Object.fromEntries(Object.entries(st.phases).map(([k, v]) => [k.slice(`cv ${serve.tag} `.length), v]));
      const sum = Object.values(per).reduce((t, x) => ({ asks: t.asks + x.asks, rows: t.rows + x.rows, bytes: t.bytes + x.bytes, ms: t.ms + x.ms }), { asks: 0, rows: 0, bytes: 0, ms: 0 });
      runs.push({ cv: path.relative(path.join(here, ".."), cv), script: ci, tag: step.tag, alone: step.alone ?? null, kind: step.kind ?? null, perturb: !!step.perturb,
        exit: r.code, wallMs: r.ms, lines, per, sum });
      console.log(`${step.tag}: exit ${r.code}, ${lines.length} key lines (${lines.filter((l) => l.status === "FAIL").length} FAIL), ${sum.asks} requests, ${sum.rows} rows, ${sum.bytes} bytes, about ${sum.ms} ms of answers, ${r.ms} ms wall`);
    }
  }
  site.close();
  own?.server.close();
  const drawn = Object.fromEntries(Object.entries(drawStats.phases).map(([k, s]) => [k.slice(`draw#${t0.getTime()} `.length), { asks: s.asks, distinct: s.distinct, rows: s.rowsOnce, bytes: s.bytesOnce, ms: s.msOnce }]));
  let differ = 0;
  const pairs = [];
  if (cvs.length > 1) {
    for (const r of runs.filter((x) => x.script === 0)) {
      const o = runs.find((x) => x.script === 1 && x.tag === r.tag.replace(/^s0_/, "s1_"));
      if (!o) continue;
      const diffs = sameLines(r.lines, o.lines);
      if (diffs.length) differ++;
      pairs.push({ tag: r.tag.slice(3), lines: r.lines.length, diffs: diffs.slice(0, 20), nDiffs: diffs.length,
        failsBefore: r.lines.filter((l) => l.status === "FAIL").length, failsAfter: o.lines.filter((l) => l.status === "FAIL").length,
        before: r.sum, after: o.sum });
      console.log(`${diffs.length ? "DIFF" : "same"} ${r.tag.slice(3)}: ${r.lines.length} key lines before, ${o.lines.length} after; FAIL ${pairs.at(-1).failsBefore} and ${pairs.at(-1).failsAfter}; requests ${r.sum.asks} to ${o.sum.asks}, rows ${r.sum.rows} to ${o.sum.rows}, bytes ${r.sum.bytes} to ${o.sum.bytes}`);
    }
  }
  const upstream = (await statsOf("\u0000").catch(() => ({ upstream: upstream0 }))).upstream - upstream0;
  fs.writeFileSync(path.join(work, "cost.json"), JSON.stringify({ started: t0, ended: new Date(), upstream, addresses, targets, kinds, drawn, index,
    runs: runs.map((r) => ({ ...r, lines: undefined, nLines: r.lines.length, fails: r.lines.filter((l) => l.status === "FAIL").length })), pairs }, null, 1));
  fs.writeFileSync(path.join(work, "lines.json"), JSON.stringify(Object.fromEntries(runs.map((r) => [r.tag, r.lines]))));
  console.log(`distinct requests sent to Supabase by this run: ${upstream} (each once); from ${t0.toISOString()} to ${new Date().toISOString()}`);
  process.exit(differ ? 1 : 0);
}

/** The proxy: each distinct request sent to Supabase once, one at a time, its answer kept in memory; every ask counted
 *  against the phase named last at /__phase. /__stats?prefix=<p> gives the phases whose name starts with <p>. */
export async function startProxy(origin, port) {
  const kept = new Map();
  const stats = new Map();
  let phase = "start";
  let upstream = 0;
  const phaseOf = (name) => stats.get(name) ?? stats.set(name, { asks: 0, distinct: new Set(), rows: 0, bytes: 0, ms: 0, repeats: new Map(), rowsOnce: 0, bytesOnce: 0, msOnce: 0 }).get(name);
  let chain = Promise.resolve();
  const server = http.createServer(async (req, res) => {
    const u = new URL(req.url, "http://x.invalid");
    if (u.pathname === "/__phase") { phase = u.searchParams.get("name") ?? "none"; res.end("ok"); return; }
    if (u.pathname === "/__stats") {
      const pre = u.searchParams.get("prefix") ?? "";
      const phases = {};
      for (const [name, s] of stats) if (name.startsWith(pre)) {
        phases[name] = { asks: s.asks, distinct: s.distinct.size, rows: s.rows, bytes: s.bytes, ms: Math.round(s.ms), rowsOnce: s.rowsOnce, bytesOnce: s.bytesOnce, msOnce: Math.round(s.msOnce),
          repeated: [...s.repeats].filter(([, n]) => n > 1).length,
          top: [...s.repeats].filter(([, n]) => n > 1).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k, n]) => `${n}x ${decodeURIComponent(k).slice(0, 240)}`) };
      }
      res.writeHead(200, { "content-type": "application/json" }).end(JSON.stringify({ upstream, kept: kept.size, phases }));
      return;
    }
    if (req.method !== "GET" && req.method !== "HEAD") { res.writeHead(405).end("reads only"); return; }
    const key = `${req.method} ${req.url} ${req.headers.prefer ?? ""} ${req.headers.range ?? ""}`;
    let got = kept.get(key);
    if (!got) {
      got = { pending: (chain = chain.then(async () => {
        upstream++;
        const t0 = performance.now();
        try {
          const h = { apikey: req.headers.apikey ?? "", authorization: req.headers.authorization ?? "", accept: req.headers.accept ?? "application/json" };
          if (req.headers.prefer) h.prefer = req.headers.prefer;
          if (req.headers.range) h.range = req.headers.range;
          const r = await fetch(origin + req.url, { method: req.method, headers: h, signal: AbortSignal.timeout(60_000) });
          const body = Buffer.from(await r.arrayBuffer());
          return { status: r.status, range: r.headers.get("content-range"), type: r.headers.get("content-type"), body, ms: performance.now() - t0 };
        } catch (e) {
          return { status: 502, range: null, type: "text/plain", body: Buffer.from(`check-values-cost: ${e?.message ?? e}`), ms: performance.now() - t0 };
        }
      })) };
      kept.set(key, got);
    }
    const s = phaseOf(phase);   // the phase the request was asked in, before its answer came
    const a = await got.pending;
    s.asks++;
    if (!s.distinct.has(key)) {   // a page drawn by Next sends a repeated request once (its fetch cache): counted once here
      s.rowsOnce += a.status < 300 ? rowsOfAnswer(a.range, a.body) : 0;
      s.bytesOnce += a.body.length;
      s.msOnce += a.ms;
    }
    s.distinct.add(key);
    s.rows += a.status < 300 ? rowsOfAnswer(a.range, a.body) : 0;
    s.bytes += a.body.length;
    s.ms += a.ms;
    s.repeats.set(key, (s.repeats.get(key) ?? 0) + 1);
    const h = { "content-type": a.type ?? "application/json" };
    if (a.range) h["content-range"] = a.range;
    res.writeHead(a.status, h);
    res.end(req.method === "HEAD" ? undefined : a.body);
  });
  await new Promise((r) => server.listen(port, "127.0.0.1", r));
  return { server, base: `http://127.0.0.1:${server.address().port}` };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main(process.argv.slice(2));
