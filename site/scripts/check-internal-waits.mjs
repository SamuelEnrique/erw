// Energy Research Warehouse (ERW) site, session 188: /internal/waits on the built site (docs/machines.md, "Continuous
// work"). The page reads content/waits.json, written by scripts/build-waits.mjs before the build; this compares what
// the server sends with that file. It reads no database and changes nothing.
//
//   npm run build
//   npx next start -p 3188
//   node scripts/check-internal-waits.mjs [base-url] [shots-dir]      (default http://localhost:3188)
//
//   visitor   without the internal cookie the page answers 404 and none of the reports' words; a token in the
//             address opens nothing
//   internal  with the cookie: 200, no-store, noindex; the three counts are the file's; every report of the file is
//             there with its number, title, date and its link to GitHub, newest first; every waiting item's line is
//             linked; the place of the marker file is said; the token is nowhere in the page
//   phone     at 390 px the page does not scroll sideways (a real browser; skipped with a note where there is none)
// Exit 1 on a failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env, withBrowser, unlockPost } from "./browser.mjs";

const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const base = (process.argv[2] ?? "http://localhost:3188").replace(/\/$/, "");
const shots = process.argv[3] ?? "";
let bad = 0, n = 0;
const check = (ok, what, shown = "") => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what} ${shown}`); } else console.log(`ok   ${what} ${shown}`); };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")
  .replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/\s+/g, " ");

let code = 1;
try {
  const w = JSON.parse(fs.readFileSync(path.join(site, "content", "waits.json"), "utf-8"));
  const token = env("INTERNAL_COSTS_TOKEN") ?? "";
  check(w.unread === null && w.marker.error === null, "the build read the reports and the marker", `(${w.counts.listed} of ${w.counts.after} reports after session ${w.marker.last}, ${w.counts.items} items)`);

  // visitor
  const no = await fetch(`${base}/internal/waits`);
  const noHtml = await no.text();
  check(no.status === 404, "without the cookie /internal/waits is 404", `(${no.status})`);
  check(!noHtml.includes("data-wait-report") && !noHtml.includes("Waits for Samuel") && !noHtml.includes("LAST_ANSWERED"), "a visitor is sent none of the page's words");
  check(w.reports.every((r) => !noHtml.includes(r.title)), "a visitor is sent no report's title");
  const tok = await fetch(`${base}/internal/waits?token=${encodeURIComponent(token)}`);
  check(tok.status === 404, "a token in the address opens nothing", `(${tok.status})`);

  // internal
  const unlock = await unlockPost(base, token);
  const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  if (!cookie) throw new Error(`${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`);
  const r = await fetch(`${base}/internal/waits`, { headers: { Cookie: cookie } });
  const html = await r.text();
  const t = text(html);
  check(r.status === 200 && html.includes('data-waits="1"'), "with the cookie the page opens", `(${r.status})`);
  check(/no-store/.test(r.headers.get("cache-control") ?? ""), "the page is no-store", `(${r.headers.get("cache-control")})`);
  check(/noindex/.test(r.headers.get("x-robots-tag") ?? "") || /<meta name="robots" content="noindex/.test(html), "the page is noindex");
  check(token.length >= 24 && !html.includes(token), "the token is nowhere in the page");
  const num = (k) => Number((html.match(new RegExp(`data-n="${k}"[^>]*>([0-9,]+)<`)) ?? [])[1]?.replace(/,/g, "") ?? NaN);
  check(num("after") === w.counts.after && num("listed") === w.counts.listed && num("items") === w.counts.items, "the three counts are the file's",
    `(${num("after")}, ${num("listed")}, ${num("items")})`);
  const ids = [...html.matchAll(/data-wait-report="([^"]+)"/g)].map((m) => m[1]);
  check(JSON.stringify(ids) === JSON.stringify(w.reports.map((x) => x.id)), "every report of the file is listed, newest first", `(${ids.join(", ")})`);
  check(w.reports.every((x) => t.includes(`Session ${x.id}: ${x.title}`.replace(/\s+/g, " "))), "each report's number and title are shown");
  check(w.reports.every((x) => x.date_words === null || t.includes(x.date_words)), "each report's date is shown as the report writes it");
  check(w.reports.every((x) => html.includes(`href="${x.url}"`)), "each report links to its file on GitHub");
  const lines = w.reports.reduce((a, x) => a + x.waits.filter((it) => html.includes(`href="${x.url}?plain=1#L${it.line}"`)).length, 0);
  check(lines === w.counts.items, "every waiting item links to its line of the report", `(${lines} of ${w.counts.items})`);
  const first = w.reports[0]?.waits[0];
  if (first) {
    const words = first.md.replace(/^\s*([-*+]|\d+[.)])\s+/, "").replace(/[*_`]/g, "").replace(/\s+/g, " ").slice(0, 60);
    check(t.replace(/[*_`]/g, "").includes(words), "the newest report's first item is in the report's own words", `("${words}")`);
  }
  check(t.includes(`the reports after session ${w.marker.last}`) && t.includes("last_answered:") && html.includes(`${w.repo}/blob/main/${w.marker.path}`),
    "the page says which report was the last answered, and where a person changes it");
  const folded = (html.match(/<details[^>]*data-decided="[0-9]+"/g) ?? []).length;
  check(folded === w.reports.filter((x) => x.decided.length > 0).length, "what was decided without the owner is folded under its report", `(${folded})`);
  check(w.decided_only.every((d) => html.includes(`href="${d.url}"`)), "a report with only decisions is named in one line, not listed");
  // session 414: the ledger of the run (each ruling once)
  const L = w.ledger;
  check(!!L && L.error === null && html.includes('data-ledger="1"'), "the ledger is drawn", `(${L ? `${L.from} to ${L.to}` : "absent"})`);
  if (L && L.error === null) {
    const ln = (k) => Number((html.match(new RegExp(`data-ln="${k}"[^>]*>([0-9,]+)<`)) ?? [])[1]?.replace(/,/g, "") ?? NaN);
    check(ln("items") === L.counts.items && ln("lines") === L.counts.lines && ln("reports") === L.counts.reports, "the ledger's counts are the file's",
      `(${ln("items")} items, ${ln("lines")} lines, ${ln("reports")} reports)`);
    const drawn = [...html.matchAll(/data-ledger-item="([^"]+)"/g)].map((m) => m[1]);
    check(drawn.length === L.groups.length && new Set(drawn).size === drawn.length, "each item of the ledger is drawn once", `(${drawn.length} of ${L.groups.length})`);
    const linked = L.groups.every((g) => [...g.asked, ...g.restated].every((x) => html.includes(`href="${x.url}"`)));
    check(linked, "every item of the ledger links to each line that asks it");
    const firsts = L.groups.filter((g) => g.first).sort((a, b) => a.first.place - b.first.place).map((g) => g.id);
    check(JSON.stringify(drawn.slice(0, firsts.length)) === JSON.stringify(firsts), "the first three are drawn first, in their order", `(${firsts.join(", ")})`);
    check(L.blocks.every((b) => html.includes(`data-ledger-block="${b.key}"`)), "every block is drawn, an empty one too");
    check(!noHtml.includes("data-ledger") && !noHtml.includes("each ruling once") && L.groups.every((g) => !noHtml.includes(`data-ledger-item="${g.id}"`)), "a visitor is sent none of the ledger");
  }
  const home = await fetch(`${base}/`, { headers: { Cookie: cookie } });
  check(!(await home.text()).includes("/internal/waits"), "the home page and the menu do not link to it, even in the internal view");

  // phone
  const seen = await withBrowser(async ({ go, wait, evaluate, unlock: open, send, errors }) => {
    await open(base);
    await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await go(`${base}/internal/waits`);
    await wait(`!!document.querySelector('[data-waits="1"]')`, 20000, "/internal/waits at 390 px");
    const m = await evaluate(`({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth,
      wide: [...document.querySelectorAll('[data-waits="1"] *')].filter((e) => e.getBoundingClientRect().right > 391 && !e.closest('pre')).length,
      reports: document.querySelectorAll('[data-wait-report]').length, h1: document.querySelector('h1').innerText })`);
    check(m.client === 390 && m.scroll <= m.client + 1, "/internal/waits at 390 px does not scroll sideways", `(scroll width ${m.scroll}, width ${m.client})`);
    check(m.wide === 0, "no element of the page runs past the phone's edge (a command in a code block scrolls inside its own box)", `(${m.wide})`);
    check(m.reports === w.reports.length && m.h1 === "Waits for Samuel (internal)", "the browser drew every report", `(${m.reports})`);
    if (shots) {
      fs.mkdirSync(shots, { recursive: true });
      const shot = await send("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(path.join(shots, "waits-phone.png"), Buffer.from(shot.data, "base64"));
      await evaluate(`document.querySelector('details') && (document.querySelector('details').open = true)`);
      const again = await evaluate(`document.documentElement.scrollWidth`);
      check(again <= 391, "with a report's decisions unfolded it still does not scroll sideways", `(${again})`);
      await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
      await go(`${base}/internal/waits`);
      await wait(`!!document.querySelector('[data-waits="1"]')`, 20000, "/internal/waits at 1280 px");
      const wide = await send("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(path.join(shots, "waits-desktop.png"), Buffer.from(wide.data, "base64"));
    }
    check(errors.length === 0, "no exception in the page", errors.slice(0, 2).join(" | "));
    return 0;
  });
  if (seen === null) console.log("note no browser on this machine: 390 px is not proven here");
  code = bad ? 1 : 0;
} catch (e) {
  console.log(`FAILED: ${e.message}`);
  code = 1;
}
console.log(`${n - bad} of ${n} checks passed`);
process.exitCode = code;
