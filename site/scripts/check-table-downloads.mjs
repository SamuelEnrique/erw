// Energy Research Warehouse (ERW) site, session 328: the downloads line of the finished pages (components/tool/TableDownloads.tsx),
// on the built site, through the internal door.
//
//   node scripts/check-table-downloads.mjs [base-url] [page ...]          (default http://localhost:3000, /board /prices)
//   CHECK_DOWNLOADS_PY=<python> CHECK_DOWNLOADS_TABLE=<table> ...          also runs the Python reader of that table
//
//   line       each page carries the line once, with at least one table, and every table offered as a CSV has its
//              Python and Stata reader beside it
//   csv        the first table offered on each page: its CSV opens with the provenance lines ("#") and then the columns
//   readers    its Python and Stata readers name this site's own address for the CSV and are attachments
//   run        (optional) the Python reader, run, loads the table: it prints the provenance and the shape
// A download is limited to sixty an hour a visitor (lib/guard.ts): the check asks for one CSV and two readers a page.
// Exit 1 on a failure.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { env, unlockPost } from "./browser.mjs";

const args = process.argv.slice(2);
const base = (args[0] ?? "http://localhost:3000").replace(/\/$/, "");
const pages = args.length > 1 ? args.slice(1) : ["/board", "/prices"];
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

const u = await unlockPost(base, env("INTERNAL_COSTS_TOKEN") ?? "");
const cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log("FAIL no internal cookie (INTERNAL_COSTS_TOKEN missing or not the server's)"); process.exit(1); }

async function head(url, bytes = 4096) {
  const r = await fetch(url, { headers: { Cookie: cookie } });
  const reader = r.body.getReader();
  let text = "";
  while (text.length < bytes) {
    const { value, done } = await reader.read();
    if (done) break;
    text += new TextDecoder().decode(value);
  }
  await reader.cancel().catch(() => {});
  return { status: r.status, disp: r.headers.get("content-disposition") ?? "", text };
}

for (const page of pages) {
  const r = await fetch(base + page, { headers: { Cookie: cookie } });
  const html = await r.text();
  const lines = html.match(/data-downloads="[^"]*"/g) ?? [];
  check(r.status === 200 && lines.length === 1 && lines[0] !== 'data-downloads="0"' && lines[0] !== 'data-downloads="unread"', `${page}: one downloads line, its tables read (${lines.join(" ")})`);
  const csvs = [...html.matchAll(/href="\/api\/download\?table=([a-z0-9_]+)"/g)].map((m) => m[1]);
  const pys = [...html.matchAll(/href="\/api\/download\?table=([a-z0-9_]+)&amp;as=py"/g)].map((m) => m[1]);
  const dos = [...html.matchAll(/href="\/api\/download\?table=([a-z0-9_]+)&amp;as=do"/g)].map((m) => m[1]);
  check(csvs.length > 0 && JSON.stringify(csvs) === JSON.stringify(pys) && JSON.stringify(csvs) === JSON.stringify(dos), `${page}: every CSV offered has its Python and Stata reader (${csvs.length} tables)`);
  if (!csvs.length) continue;
  const t = csvs[0];
  const c = await head(`${base}/api/download?table=${t}`);
  const first = c.text.split("\n");
  const k = first.findIndex((l) => !l.startsWith("#"));
  check(c.status === 200 && k > 0 && /^[a-z_]+(,[a-z0-9_]+)+\r?$/.test(first[k]), `${page}: ${t}.csv opens with ${k} provenance lines, then its columns (${(first[k] ?? "").slice(0, 60)})`);
  for (const as of ["py", "do"]) {
    const s = await head(`${base}/api/download?table=${t}&as=${as}`, 20000);
    check(s.status === 200 && s.text.includes(`${base}/api/download?table=${t}`) && s.disp.includes(`erw_${t}.${as}`), `${page}: the ${as === "py" ? "Python" : "Stata"} reader of ${t} names this site's CSV and is an attachment`);
  }
}

const py = process.env.CHECK_DOWNLOADS_PY, table = process.env.CHECK_DOWNLOADS_TABLE;
if (py && table) {
  const s = await head(`${base}/api/download?table=${table}&as=py`, 20000);
  const f = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "erw-reader-")), `erw_${table}.py`);
  fs.writeFileSync(f, s.text);
  try {
    const out = execFileSync(py, ["-I", f], { encoding: "utf-8", timeout: 300000 });
    const shape = out.match(/^\((\d+), (\d+)\)$/m);
    check(Boolean(shape) && Number(shape[1]) > 0 && out.startsWith("#"), `the Python reader of ${table}, run, prints the provenance and loads ${shape ? shape[1] : "no"} rows`);
  } catch (e) {
    check(false, `the Python reader of ${table}, run: ${String(e.stderr ?? e.message).slice(-400)}`);
  }
}

console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
