// Energy Research Warehouse (ERW) site, session 537: a local pass-through to Supabase's REST API that fails one table's
// reads on purpose, so a build or a server can be shown losing a read and asking for it again.
//
//   node --env-file=.env.local scripts/failing-read-proxy.mjs --port 54537 --fail caiso_grid_emergencies --while <file>
//                                                           [--host 127.0.0.2] [--log <file>]
//   SUPABASE_URL=http://127.0.0.2:54537 npm run build      (or npm start)
//
// Every GET under /rest/v1/ is sent on to the origin of SUPABASE_URL as it came (the same path, query and key headers)
// and its answer handed back (status, body, content-range). A request whose table_name is eq.<--fail> is answered
// instead with HTTP 500 and a body that is not the statement timeout's (so the site's reader does not retry it), for as
// long as the file --while exists: delete the file and the same reads pass through again. --log appends one line a
// request (time, table, table_name, failed or passed). It writes nothing else, asks for nothing the site would not, and
// no page code knows it exists: the site reads it only because SUPABASE_URL points at it. The host defaults to
// 127.0.0.2, a loopback address lib/supabase.ts does not take for a stand-in, so a required() read still fails the
// build as it would against the warehouse.
import fs from "node:fs";
import http from "node:http";

const args = process.argv.slice(2);
const opt = (name, d) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : d; };
const port = Number(opt("--port", "54537"));
const host = opt("--host", "127.0.0.2");
const fail = opt("--fail", "");
const flag = opt("--while", "");
const log = opt("--log", "");
if (!fail || !flag || !Number.isInteger(port)) { console.log("--fail <table> and --while <file> are needed"); process.exit(2); }
if (!process.env.SUPABASE_URL) { console.log("SUPABASE_URL is needed (node --env-file=.env.local ...)"); process.exit(2); }
const upstream = new URL(process.env.SUPABASE_URL).origin;
if (/^https?:\/\/(localhost|127\.)/.test(upstream)) { console.log(`SUPABASE_URL points at this machine (${upstream}), not at the warehouse`); process.exit(2); }

const note = (line) => { if (log) fs.appendFileSync(log, `${new Date().toISOString()} ${line}\n`); };

http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${host}:${port}`);
  const table = url.pathname.replace(/^\/rest\/v1\//, "");
  const named = url.searchParams.get("table_name") ?? "";
  if (req.method !== "GET" || !url.pathname.startsWith("/rest/v1/")) {
    note(`refused ${req.method} ${url.pathname}`);
    res.writeHead(405, { "content-type": "text/plain" }).end("this stand-in passes reads only");
    return;
  }
  if (named === `eq.${fail}` && fs.existsSync(flag)) {
    note(`failed ${table} ${named} offset=${url.searchParams.get("offset") ?? ""}`);
    res.writeHead(500, { "content-type": "application/json" }).end('{"message":"session 537: this read fails on purpose"}');
    return;
  }
  try {
    const headers = {};
    for (const h of ["apikey", "authorization", "prefer", "accept"]) if (req.headers[h]) headers[h] = req.headers[h];
    const r = await fetch(`${upstream}${url.pathname}${url.search}`, { headers });
    const body = Buffer.from(await r.arrayBuffer());
    const out = { "content-type": r.headers.get("content-type") ?? "application/json" };
    const range = r.headers.get("content-range");
    if (range) out["content-range"] = range;
    note(`passed ${r.status} ${table} ${named}`);
    res.writeHead(r.status, out).end(body);
  } catch (e) {
    note(`upstream failed ${table} ${named}: ${e.message}`);
    res.writeHead(502, { "content-type": "text/plain" }).end(`upstream: ${e.message}`);
  }
}).listen(port, host, () => console.log(`failing-read-proxy on http://${host}:${port}, failing ${fail} while ${flag} exists, upstream ${upstream}`));
