// Energy Research Warehouse (ERW) site, session 127: the price board, version 4, on the built site.
//
//   npm run build && npx next start -p 3127
//   node --import ./scripts/alias-loader.mjs scripts/check-board-v4.mjs [base-url]      (default http://localhost:3127)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   numbers   every number the page marks (data-n) equals the site's copy of price_board_stats (data/board_v4.json):
//             each line's latest value, its four moves and the two ends of its range
//   lines     a row for each of the copy's lines, and a range mark for each line that holds a range
//   formulas  each spread's formula is printed under its table
//   not held  the seven prices no free source gives, greyed, each with a source; PJM licensed and MISO paused in words
//   visitor   without the cookie the page is the in-review page and carries no number
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
import * as g from "../lib/board4.ts";

const base = (process.argv[2] ?? "http://localhost:3127").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/board_v4.json", import.meta.url), "utf-8"));
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exitCode = 1; }
else {
  const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
  const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
  const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1].replace(/&amp;/g, "&"), x[2]]));
  const { status, html } = await get("/board/v4");
  check(status === 200 && !html.includes('data-in-review="1"'), "/board/v4 opens in the internal view");
  const got = marked(html), wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, copy ${val}`); };
  let ranges = 0;
  for (const l of file.lines) {
    if (!l.last) continue;
    want(`${l.key}|last`, g.value(l.last.v, l.unit));
    for (const [k] of g.MOVES) { const m = l.moves?.[k]; if (m) want(`${l.key}|${k}`, g.signed(m.change, l.unit)); else if (`${l.key}|${k}` in got) wrong.push(`${l.key}|${k}: on the page, not in the copy`); }
    if (l.range && l.range.position !== null) { ranges += 1; want(`${l.key}|low`, g.value(l.range.low, l.unit)); want(`${l.key}|high`, g.value(l.range.high, l.unit)); }
  }
  const h = g.held(file);
  want("sum|prices", String(h.prices)); want("sum|spreads", String(h.spreads));
  check(wrong.length === 0, `every marked number is the copy's (${Object.keys(got).length} on the page, ${file.lines.length} lines)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const drawn = [...html.matchAll(/data-range="([^"]+)"/g)].length;
  check(drawn === ranges, `${drawn} range marks drawn, ${ranges} lines hold a range`);
  const t = text(html);
  const spreads = g.GROUPS.filter((x) => x.spread);
  check(spreads.every((x) => html.includes(`data-formula="${x.id}"`) && t.includes(`Formula: ${g.groupLines(file, x.id)[0].formula}.`)), `the formula of each of the ${spreads.length} spreads is printed`);
  check(t.includes("indicative") && t.includes("it is not the gas a plant in any of these grids burns"), "the spark spread is labeled indicative, and why");
  check(g.NOT_HELD.every((x) => t.includes(x.name) && t.includes(x.source)) && (t.match(/licensed source needed/g) ?? []).length === g.NOT_HELD.length, `${g.NOT_HELD.length} prices not held, each greyed with its source`);
  check(html.includes('data-withheld="PJM"') && html.includes('data-withheld="MISO"') && /MISO power prices\s+Paused/.test(t) && /PJM power prices\s+Licensed/.test(t), "PJM licensed and MISO paused, in words");
  check(!/miso:|pjm:/i.test(Object.keys(got).join(" ")), "no figure of MISO's or PJM's prices");
  check(!/\bundefined\b|NaN/.test(t), 'no "undefined" and no NaN in the text');
  const v = await get("/board/v4", false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-n="), "as a visitor: the in-review page, and no number of the board");
  console.log(`${n - bad} of ${n} checks pass`);
  process.exitCode = bad ? 1 : 0;
}
