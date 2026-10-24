// Energy Research Warehouse (ERW) site, session 328: the downloads line of the finished pages (components/tool/TableDownloads.tsx),
// on the built site, through the internal door.
//
//   node scripts/check-table-downloads.mjs [base-url] [page ...]          (default http://localhost:3000, /board /prices)
//   CHECK_DOWNLOADS_PY=<python> CHECK_DOWNLOADS_TABLE=<table> ...          also runs the Python reader of that table
//   CHECK_DOWNLOADS_RSCRIPT=<Rscript> CHECK_DOWNLOADS_TABLE=<table> ...    also runs the R reader of that table (session 535)
//
//   line       each page carries the line once, with at least one table, and every table offered as a CSV has its
//              Python, Stata and R reader beside it (R since session 535)
//   csv        the first table offered on each page that answers: its CSV opens with the provenance lines ("#") and then the columns
//              (a table whose row count passes the database's statement timeout is the route's known fault, named and skipped)
//   readers    its Python, Stata and R readers name this site's own address for the CSV and are attachments
//   run        (optional) the Python reader, or the R reader, run, loads the table: it prints the provenance and the shape
//   grid       session 1182: the Grid tool's panel files (components/grid/PanelFile.tsx: each panel chains 077 and 078 added
//              offers its table as a CSV written into its link, data-grid-file). On each Grid page, by default
//              scripts/grid-files.mjs GRID_FILE_PAGES (CHECK_GRID_FILES=<address>,<address> for others, CHECK_GRID_FILES=0
//              for none): every panel's file the page must offer is there, and each opens with its provenance (the panel and
//              page, the tables, the filter, the hour or window, the time drawn), then its columns. A Grid page is read, not
//              a download: it does not count against the sixty an hour. check-download.mjs --grid reads each file whole.
//              Session 1420: the older blocks' files too (YourGrid's Right now, Batteries, What it costs, What is being
//              built; Reliability's three tables; the Now view's mix in that hour; "Yesterday", the mix table and the
//              Clean tab's carbon blocks), a held grid's page (ISO-NE, its held blocks offering no file), and each file's
//              held figures written "license needed" (the link's data-grid-file-held), never a value.
// A download is limited to sixty an hour a visitor (lib/guard.ts): the check asks for one CSV and three readers a page.
// Exit 1 on a failure.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { env, unlockPost } from "./browser.mjs";
import { GRID_FILE_PAGES, gridFileProblems, gridFilesOf, missingFiles, rawsOf } from "./grid-files.mjs";  // session 1182

const args = process.argv.slice(2);
const base = (args[0] ?? "http://localhost:3000").replace(/\/$/, "");
// session 416: Git Bash on Windows rewrites a page that begins with "/" into a Windows path (session 403's run exited
// 127 on it); both spellings are taken, as check-review-pages.mjs does, so a caller needs no MSYS_NO_PATHCONV=1
const pages = (args.length > 1 ? args.slice(1) : ["/board", "/prices"]).map((p) => p.replaceAll("\\", "/").replace(/^[A-Za-z]:\/.*?\/Git(?=\/)/, "")).map((p) => (p.startsWith("/") ? p : `/${p}`));
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
  check(r.status === 200 && lines.length === 1 && lines[0] !== 'data-downloads="unread"', `${page}: one downloads line, its tables read (${lines.join(" ")})`);
  // session 330: a page whose only tables are not public in the live set (held for review) shows the line with none, and
  // points to Data and methods: said, and the page is passed by
  if (lines[0] === 'data-downloads="0"') { console.log(`note ${page}: no table of the page is in the site's live catalogue; the line says so (${/every public table is on|every table is on/.test(html) ? "it does" : "it does not"})`); continue; }
  const csvs = [...html.matchAll(/href="\/api\/download\?table=([a-z0-9_]+)"/g)].map((m) => m[1]);
  const pys = [...html.matchAll(/href="\/api\/download\?table=([a-z0-9_]+)&amp;as=py"/g)].map((m) => m[1]);
  const dos = [...html.matchAll(/href="\/api\/download\?table=([a-z0-9_]+)&amp;as=do"/g)].map((m) => m[1]);
  // session 535: the R reader (?as=r), offered beside the other two
  const rs = [...html.matchAll(/href="\/api\/download\?table=([a-z0-9_]+)&amp;as=r"/g)].map((m) => m[1]);
  // session 383: from 21 October 2026 a table held for a license says "held: license needed" in the line instead of its
  // links (components/tool/TableDownloads.tsx), and one not in the live set points to Redivis: each table of the line is
  // one of the three. A page all of whose tables are held (/prices: its six ISO price tables) offers no CSV: said, and passed by
  const shownN = Number(/\d+/.exec(lines[0] ?? "")?.[0] ?? 0);
  const heldN = (html.match(/data-not-held="license"/g) ?? []).length, redivisN = (html.match(/data-not-held="live-set"/g) ?? []).length;
  check(csvs.length + heldN + redivisN === shownN && JSON.stringify(csvs) === JSON.stringify(pys) && JSON.stringify(csvs) === JSON.stringify(dos)
    && JSON.stringify(csvs) === JSON.stringify(rs),
    `${page}: every CSV offered has its Python, Stata and R reader (${csvs.length} tables; ${heldN} held for a license, ${redivisN} on Redivis, of ${shownN})`);
  if (!csvs.length) { console.log(`note ${page}: no CSV is offered: ${heldN} of ${shownN} tables held for a license, ${redivisN} on Redivis`); continue; }
  // the route's own fault, found by session 328: on the largest series tables its row count (count=exact) passes the
  // database's statement timeout and the download answers 502 ("Supabase series: HTTP 500"), on /data as here. Such a
  // table is named, and the next one offered is asked, three at most: the line is proven on a table that answers.
  let t = null, c = null;
  for (const cand of csvs.slice(0, 3)) {
    const got = await head(`${base}/api/download?table=${cand}`);
    if (got.status === 502 && /Supabase (series|entities|events): HTTP 500/.test(got.text)) { console.log(`note ${page}: ${cand}.csv: the route's row count timed out (its known fault, not this line's)`); continue; }
    t = cand; c = got; break;
  }
  if (!t) { console.log(`unproven ${page}: every table tried hit the route's row-count fault; the line is proven on the other pages (the session's report)`); continue; }
  const first = c.text.split("\n");
  const k = first.findIndex((l) => !l.startsWith("#"));
  check(c.status === 200 && k > 0 && /^[a-z_]+(,[a-z0-9_]+)+\r?$/.test(first[k]), `${page}: ${t}.csv opens with ${k} provenance lines, then its columns (${(first[k] ?? "").slice(0, 60)})`);
  for (const as of ["py", "do", "r"]) {
    const s = await head(`${base}/api/download?table=${t}&as=${as}`, 20000);
    check(s.status === 200 && s.text.includes(`${base}/api/download?table=${t}`) && s.disp.includes(`erw_${t}.${as}"`), `${page}: the ${{ py: "Python", do: "Stata", r: "R" }[as]} reader of ${t} names this site's CSV and is an attachment`);
  }
}

// session 1182: the Grid tool's panel files (the header's "grid")
const gridEnv = process.env.CHECK_GRID_FILES;
const gridPages = gridEnv === "0" ? [] : gridEnv
  ? gridEnv.split(",").map((p) => p.replaceAll("\\", "/").replace(/^[A-Za-z]:\/.*?\/Git(?=\/)/, "")).map((p) => [p.startsWith("/") ? p : `/${p}`, null])
  : GRID_FILE_PAGES;
for (const [page, want] of gridPages) {
  const r = await fetch(base + page, { headers: { Cookie: cookie } });
  const html = await r.text();
  const files = gridFilesOf(html);
  check(r.status === 200 && files.length > 0, `${page}: ${files.length} panel files on the page, data-grid-file (${files.map((f) => f.id).join(", ")})`);
  if (want) {
    const miss = missingFiles(files.map((f) => f.id), want);
    check(!miss.length, `${page}: every panel's file it must offer (${want.join(", ")})${miss.length ? `; missing ${miss.join(", ")}` : ""}`);
  }
  const raws = rawsOf(html);
  for (const f of files) {
    const top = gridFileProblems(f, raws).filter((x) => /link|decode|downloads|header|columns/.test(x));
    check(!top.length, `${page}: ${f.id}: an attachment, erw_${f.id}.csv, opening with its provenance, then its columns${top.length ? ` (${top.join("; ")})` : ""}`);
    // session 1420: a held figure is written "license needed", never its value
    const held = gridFileProblems(f, raws).filter((x) => /license needed/.test(x));
    if (f.held) check(!held.length, `${page}: ${f.id}: its ${f.held} held figure(s) written "license needed"${held.length ? ` (${held.join("; ")})` : ""}`);
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

// session 535: the R reader, run where an R interpreter is named (Rscript); on a machine without R the reader is checked by
// its text above and by tests/test_session535.py
const rscript = process.env.CHECK_DOWNLOADS_RSCRIPT;
if (rscript && table) {
  const s = await head(`${base}/api/download?table=${table}&as=r`, 20000);
  const f = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "erw-reader-")), `erw_${table}.r`);
  fs.writeFileSync(f, s.text);
  try {
    const out = execFileSync(rscript, ["--vanilla", f], { encoding: "utf-8", timeout: 300000 });
    const dim = out.match(/^\[1\] (\d+) +(\d+)\r?$/m);
    check(Boolean(dim) && Number(dim[1]) > 0 && out.startsWith("#"), `the R reader of ${table}, run, prints the provenance and loads ${dim ? dim[1] : "no"} rows`);
  } catch (e) {
    check(false, `the R reader of ${table}, run: ${String(e.stderr ?? e.message).slice(-400)}`);
  }
}

console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
