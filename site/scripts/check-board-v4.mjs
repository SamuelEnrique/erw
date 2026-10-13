// Energy Research Warehouse (ERW) site, session 127: the price board, version 4, on the built site.
//
//   npm run build && npx next start -p 3127
//   node --import ./scripts/alias-loader.mjs scripts/check-board-v4.mjs [base-url]      (default http://localhost:3127)
//
// Session 241 (batch C): rewritten for where version 4 is today. /board/v4 was retired by session 132 and redirects to
// the one price board, /board. Until this session the script read /board/v4 as a page and looked for its keys
// (ercot:HB_HUBAVG|da|last, from data/board_v4.json) and marks (data-formula, data-withheld), none of which /board
// writes: 4 of 10 passed on every build since session 132. Each thing it checked is checked on /board, read as HTML in
// the internal view through the old address:
//   redirect  /board/v4 answers a permanent redirect to /board, a query carried
//   numbers   every number the page marks (data-n) for a row shown equals the site's file (data/board.json): its
//             latest value, its moves and the two ends of its one-year range
//   lines     a row for each row of the file under the default filters, and a range mark for each that holds a range
//   formulas  each row that is computed carries its formula where the board prints it now, on hover of its name
//             (the page face carries no method words since session 132)
//   spark     the spark spread is labeled indicative, and its formula says why
//   not held  the rows no free source gives are on the page, blank, each with the source that would supply it; PJM
//             reads "licensed source needed" and MISO "paused while terms are reviewed", and neither has a figure
//   visitor   without the cookie the old address ends on the in-review page and carries no number
// Gone, and so not checked: version 4's own file (data/board_v4.json is read by no page), its sentence of how many
// prices and spreads are held (sum|prices, sum|spreads), and the formulas printed under each table.
// The board's own check, with its top block, its folds and its workbench in a browser, is check-board.mjs.
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
import * as b from "../lib/board.ts";

const base = (process.argv[2] ?? "http://localhost:3127").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf-8"));
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exitCode = 1; }
else {
  const get = async (path, withCookie = true, redirect = "follow") => { const r = await fetch(base + path, { redirect, headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text(), location: (r.headers.get("location") ?? "").replace(/^https?:\/\/[^/]+/, ""), url: r.url.replace(base, "") }; };
  const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
  const text = (html) => decode(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
  const marked = (html) => Object.fromEntries([...html.matchAll(/<span[^>]*data-n="([^"]+)"[^>]*>([^<]*)</g)].map((x) => [x[1].replace(/&amp;/g, "&"), x[2]]));
  for (const [path, to] of [["/board/v4", "/board"], ["/board/v4?row=henry-hub", "/board?row=henry-hub"]]) {
    const r = await get(path, true, "manual");
    check((r.status === 308 || r.status === 301) && r.location === to, `${path} answers a permanent redirect to ${to} (${r.status} ${r.location})`);
  }
  const { status, html, url } = await get("/board/v4");
  check(status === 200 && url === "/board" && html.includes('data-board="1"') && !html.includes('data-in-review="1"'), "/board/v4 ends on /board, open in the internal view");
  const got = marked(html), wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, file ${val}`); };
  let shown = 0, ranges = 0, noRow = 0;
  const formulas = [];
  for (const g of file.groups) {
    for (const r of b.rowsOf(file, g, {})) {
      if (r.group !== g.id) continue;          // a row listed in a second group is checked in its own
      if (!html.includes(`data-row="${r.id}"`)) { noRow += 1; wrong.push(`${r.id}: no row`); continue; }
      if (r.formula) formulas.push(r);
      if (r.status !== "ok") continue;
      shown += 1;
      want(`${r.id}|last`, b.fmt(r.last.v, r.unit));
      for (const [k] of b.MOVES) { const mv = r.moves[k]; if (mv) want(`${r.id}|${k}`, b.signed(mv.ch, r.unit)); else if (`${r.id}|${k}` in got) wrong.push(`${r.id}|${k}: on the page, not in the file`); }
      if (r.range && r.range.pos !== null) { ranges += 1; want(`${r.id}|lo`, b.fmt(r.range.lo, r.unit)); want(`${r.id}|hi`, b.fmt(r.range.hi, r.unit)); }
    }
  }
  check(shown > 30 && wrong.length === 0, `every marked number of the ${shown} rows shown is the file's: latest value, moves and the ends of the range (${Object.keys(got).length} marked)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const drawn = [...html.matchAll(/data-range="/g)].length;
  check(noRow === 0 && drawn >= ranges && ranges > 0, `a row for each row of the file's default view, and ${drawn} range marks drawn for the ${ranges} rows that hold a range`);
  const plain = decode(html), t = text(html);
  const unprinted = formulas.filter((r) => !plain.includes(`Formula: ${r.formula}`));
  check(formulas.length >= 3 && unprinted.length === 0, `the formula of each of the ${formulas.length} computed rows is printed on hover of its name${unprinted.length ? ` (not printed: ${unprinted.slice(0, 3).map((r) => r.id).join(", ")})` : ""}`);
  const spark = file.rows.filter((r) => r.group === "spark" && /spark/.test(r.id) && r.status === "ok" && html.includes(`data-row="${r.id}"`));   // MISO's and PJM's are blank rows, with no formula
  check(spark.length > 0 && t.includes("spark spread, indicative") && spark.every((r) => /Indicative: Henry Hub is in Louisiana, not the gas a plant in this grid burns/.test(r.formula ?? "") && plain.includes(`Formula: ${r.formula}`)),
    `the spark spread is labeled indicative, and its formula says why (${spark.length} rows)`);
  const blankRow = (id) => { const x = html.match(new RegExp(`<tr[^>]*data-row="${id}"[\\s\\S]*?</tr>`)); return x ? x[0] : ""; };
  const greyed = file.rows.filter((r) => r.status === "licensed" && !/^(miso|pjm)-/.test(r.id));
  const onPage = greyed.filter((r) => html.includes(`data-row="${r.id}"`));
  check(greyed.length >= 7 && greyed.every((r) => r.note && /supply|Source|permission/.test(r.note)) && onPage.length > 0 && onPage.every((r) => blankRow(r.id).includes("licensed source needed") && !/data-n=/.test(blankRow(r.id))),
    `${greyed.length} prices no free source gives, each naming the source that would supply it; the ${onPage.length} on the default view are blank with "licensed source needed"`);
  const miso = blankRow("miso-indiana-hub-da"), pjm = blankRow("pjm-western-hub-da");
  check(miso.includes("paused while terms are reviewed") && !/data-n=/.test(miso) && pjm.includes("licensed source needed") && !/data-n=/.test(pjm) && t.includes("MISO Indiana hub") && t.includes("PJM Western hub"), "PJM licensed and MISO paused, in words, their rows blank");
  check(!Object.keys(got).some((k) => /^(top\|)?(miso|pjm)-/.test(k)) && !file.rows.some((r) => /^(miso|pjm)-/.test(r.id) && (r.last || r.spark)), "no figure of MISO's or PJM's prices, on the page or in the file");
  check(!/\bundefined\b|NaN/.test(t), 'no "undefined" and no NaN in the text');
  const v = await get("/board/v4", false);
  check(v.status === 200 && v.url === "/board" && v.html.includes('data-in-review="1"') && !v.html.includes("data-n="), "as a visitor: the old address ends on the in-review page, and no number of the board");
  console.log(`${n - bad} of ${n} checks pass`);
  process.exitCode = bad ? 1 : 0;
}
