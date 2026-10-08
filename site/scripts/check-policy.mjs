// Energy Research Warehouse (ERW) site, session 157: the policy monitor (/policy, in review) on the built site, and its
// second view "What changed this week" (/policy?view=week).
//
//   npm run build && npx next start -p 3149
//   node --import ./scripts/alias-register.mjs scripts/check-policy.mjs [base-url]      (default http://localhost:3149)
//
// The page is read in the internal view (it is in review), first as HTML and then in a real browser (scripts/browser.mjs):
//   before     what /policy showed before session 157 is all still there, in its own view: the lead, "This week in
//              policy", "Every action" with its six filters and its table, the source line; and the two views' links
//   opens      the view opens with seven days and no filter; a visitor gets the in-review page and no row
//   rows       every row has a date, a status, a link to a source document with a hover, and a read marked as a
//              model's (its hover naming a model's read) or the placeholder "no read yet" with its hover
//   windows    seven days and thirty: the switch answers the mouse and the keyboard, changes the rows and the address;
//              every row of seven days is a row of thirty
//   filters    agency, topic, grid and large loads: each changes the rows and the address, and the rows are exactly the
//              rows of the window that carry that agency, topic, grid or mark (read from the rows' own marks, not from
//              the page's code); a choice that leaves nothing shows a short placeholder with a hover
//   MISO       the fixed words "paused while terms are reviewed", the site's hover, and no row
//   refusing   a regulator whose list refuses a plain request (data/policy/refresh.json) is named in the agency filter
//              with a short mark whose hover is the file's reason, word for word
//   chart      a count answers the mouse and the keyboard with the agency, the number and the window; a click on a count
//              filters the list and writes the address
//   address    an address with a window and four filters restores the view, on the server (no script) and in the browser
//   scope      none of the words "zoning", "city council", "county board" anywhere in the view, hovers included
//   face       the view's face holds no sentence of the Method note (docs/methods/policy_monitor.md), and links it
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import { METHOD, MUNICIPAL, NONE_WORDS, NO_READ, PAUSED_WORDS, PAUSE_WHY, sinceDay } from "../lib/policyweek.ts";

const base = (process.argv[2] ?? "http://localhost:3149").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const readJson = (rel) => { const u = new URL(rel, import.meta.url); return fs.existsSync(u) ? JSON.parse(fs.readFileSync(u, "utf8")) : null; };

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
/** The page as a reader sees it: no script, no style, no attribute (so no hover). */
const face = (html) => decode(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const rowsIn = (html) => [...html.matchAll(/<tr[^>]*data-week-row="([^"]+)"[^>]*>/g)].map((m) => decode(m[1]));

// ---- before: what /policy showed is all still there, in its own view ------------------------------------------------
{
  const p = await get("/policy");
  const t = face(p.html);
  check(p.status === 200 && !p.html.includes('data-in-review="1"') && p.html.includes('data-policy="all"') && !p.html.includes('data-week="1"'), "/policy opens in the internal view, as the page it was (the view of every action)");
  const kept = ["Energy rules, proposed rules and notices of DOE, FERC, EPA, NRC, BLM and Interior from the Federal Register", "each scored for significance and, when it scores 5 or more, read for its impact",
    "Significance uses the same rubric as the news digest", "so FERC appears through the Federal Register", "This week in policy", "Every action", "Agency", "Type", "Sector", "State", "Significance", "From", "5 or more", "7 or more",
    "Date", "Title", "Scores from warehouse/policy/score.py (the news rubric)", "policy_actions", "policy_reads"];
  const lost = kept.filter((w) => !t.includes(w));
  const tableRows = (p.html.match(/<tr class="cursor-pointer/g) ?? []).length;
  const of = /(\d+) of (\d+) actions/.exec(t);
  check(lost.length === 0 && tableRows > 0 && !!of && Number(of[2]) >= Number(of[1]) && Number(of[1]) > 0, `what /policy showed before is all still there: its lead, "This week in policy", "Every action" with its six filters, ${tableRows} rows of the table (${of?.[0]}), its source line${lost.length ? `; LOST: ${lost.join(" | ")}` : ""}`);
  check(/data-view="all"[^>]*>Every action, scored</.test(p.html) && /data-view="week"[^>]*>What changed this week</.test(p.html) && /href="\/policy\?view=week"/.test(p.html) && /aria-current="page"[^>]*data-view="all"/.test(p.html) && p.html.includes(METHOD.href),
    "the two views are linked from it, this one marked as open, and the Method note is named");
  check(!/\bundefined\b|NaN/.test(t), "/policy: no \"undefined\" and no NaN in the text");
}

// ---- the view, as HTML ----------------------------------------------------------------------------------------------
const week = await get("/policy?view=week");
const month = await get("/policy?view=week&days=30");
{
  const t = face(week.html);
  check(week.status === 200 && !week.html.includes('data-in-review="1"') && week.html.includes('data-policy="week"') && week.html.includes('data-week="1"') && /data-week-days="7"/.test(week.html) && t.includes("What changed this week") && !t.includes("This week in policy") && !t.includes("Significance"),
    "/policy?view=week opens the view \"What changed this week\" with seven days, and not the other view's blocks");
  check(/aria-current="page"[^>]*data-view="week"/.test(week.html) && /href="\/policy"[^>]*data-view="all"/.test(week.html), "the other view is one link away");
  check(!/\bundefined\b|NaN/.test(t) && !/\bundefined\b|NaN/.test(face(month.html)), "the view: no \"undefined\" and no NaN in the text, seven days and thirty");
  const v = await get("/policy?view=week&days=30", false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-week-row=") && !v.html.includes('data-week="1"'), "as a visitor: the in-review page, and no row of the view");
  // scope: the three words, anywhere in what the view sends (its face, its hovers and the rows it holds for thirty days)
  for (const [name, p] of [["seven days", week], ["thirty days", month]]) {
    const all = decode(p.html).toLowerCase().replace(/\s+/g, " ");
    const found = MUNICIPAL.filter((w) => all.includes(w));
    check(found.length === 0, `scope, ${name}: none of ${MUNICIPAL.map((w) => `"${w}"`).join(", ")} in the view, hovers included${found.length ? ` (FOUND: ${found.join(", ")})` : ""}`);
  }
  // the face holds no sentence of the Method note
  const note = new URL(`../../${METHOD.doc}`, import.meta.url);
  if (fs.existsSync(note)) {
    const md = fs.readFileSync(note, "utf8");
    const sentences = [...new Set(md.split(/\n/).filter((l) => !/^\s*(#|\||```|-{3,})/.test(l)).join(" ").replace(/[*_`>]/g, "").split(/(?<=[.!?])\s+/).map((s) => s.replace(/^\s*[-0-9.]+\s+/, "").replace(/\s+/g, " ").trim()).filter((s) => s.length >= 40))];
    const faces = [face(week.html), face(month.html)];
    const on = sentences.find((s) => faces.some((f) => f.includes(s)));
    check(sentences.length > 10 && !on, `the view's face holds no sentence of the Method note (${sentences.length} sentences of ${METHOD.doc}, seven days and thirty)${on ? `: "${on.slice(0, 120)}"` : ""}`);
    const m = await get(METHOD.href);
    check(m.status === 200 && !m.html.includes('data-in-review="1"') && week.html.includes(METHOD.href), `the Method note is named and its page opens (${METHOD.href}: ${m.status})`);
  } else check(false, `${METHOD.doc} is beside the site, so the view's face can be read against it and its link opens`);
  check(!/How it is computed|What is not here|Limitations|Method:/.test(t), "no method heading on the face");
}

// ---- the view, in a real browser --------------------------------------------------------------------------------------
const refresh = readJson("../data/policy/refresh.json");
const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, send, errors }) => {
  await open(base);
  const ready = () => wait(`!!document.querySelector('[data-week="1"]') && !!document.querySelector('[data-week-window-choice="30"]')`, 30000, "the view");
  /** What the view shows now: its state, its address and every row with its own marks. */
  const read = () => evaluate(`(() => {
    const w = document.querySelector('[data-week="1"]');
    const rows = [...w.querySelectorAll('tr[data-week-row]')].map((tr) => {
      const a = tr.querySelector('a[data-week-link]'), mark = tr.querySelector('[data-week-mark="model"]'), none = tr.querySelector('[data-week-read] [data-missing]'), st = tr.querySelector('[data-week-status]');
      return { id: tr.dataset.weekRow, kind: tr.dataset.weekKind, body: tr.dataset.weekBody, grids: tr.dataset.weekGrids, large: tr.dataset.weekLoads, date: tr.querySelector('[data-week-date]')?.dataset.weekDate ?? '', dateWords: tr.querySelector('[data-week-date]')?.textContent.trim() ?? '',
        status: st?.textContent.trim() ?? '', statusTip: st?.querySelector('[title]')?.title ?? '', href: a?.getAttribute('href') ?? '', linkWords: a?.textContent.trim() ?? '', linkTip: a?.title ?? '',
        topics: (tr.querySelector('[data-week-topics]')?.dataset.weekTopics ?? '').split(' ').filter(Boolean), topicTips: [...tr.querySelectorAll('[data-week-topic]')].every((s) => s.title.length > 10),
        read: tr.querySelector('[data-week-read]')?.dataset.weekRead ?? '', readText: tr.querySelector('[data-week-read]')?.textContent.trim() ?? '', markWords: mark?.textContent.trim() ?? '', markTip: mark?.title ?? '', noneWords: none?.textContent.trim() ?? '', noneTip: none?.title ?? '' };
    });
    const pressed = (sel) => [...w.querySelectorAll(sel)].filter((b) => b.getAttribute('aria-pressed') === 'true').map((b) => Object.values(b.dataset)[0]);
    return { days: Number(w.dataset.weekDays), today: w.dataset.weekToday, shown: Number(w.dataset.weekShown), state: w.dataset.weekState, search: location.search, path: location.pathname, rows,
      groups: [...w.querySelectorAll('[data-week-group]')].map((g) => [g.dataset.weekGroup, Number(g.dataset.weekGroupCount), g.querySelectorAll('tr[data-week-row]').length]),
      window: pressed('[data-week-window-choice]'), agency: pressed('[data-week-agency]'), topic: pressed('[data-week-topic-choice]'), grid: pressed('[data-week-grid]'), large: w.querySelector('button[data-week-large]')?.getAttribute('aria-pressed') === 'true',
      tables: w.querySelectorAll('table').length, paused: w.querySelector('[data-week-paused] [data-missing]') ? { words: w.querySelector('[data-week-paused] [data-missing]').textContent.trim(), why: w.querySelector('[data-week-paused] [data-missing]').title } : null,
      empty: w.querySelector('[data-week-empty] [data-missing]') ? { words: w.querySelector('[data-week-empty] [data-missing]').textContent.trim(), why: w.querySelector('[data-week-empty] [data-missing]').title } : null,
      untitled: [...w.querySelectorAll('[data-missing]')].filter((m) => !m.title).length, placeholders: w.querySelectorAll('[data-missing]').length };
  })()`);
  const click = async (sel, until, what) => { await evaluate(`document.querySelector(${JSON.stringify(sel)}).click()`); await wait(until, 15000, what); return read(); };
  const ids = (rows) => rows.map((r) => r.id);
  const query = (s) => Object.fromEntries(new URLSearchParams(s));

  await go(`${base}/policy?view=week`);
  await ready();
  const seven = await read();
  check(seven.days === 7 && seven.path === "/policy" && same(query(seven.search), { view: "week" }) && same(seven.window, ["7"]) && same(seven.agency, [""]) && same(seven.topic, [""]) && same(seven.grid, [""]) && !seven.large,
    `the view opens with seven days and no filter (${seven.shown} rows; today ${seven.today})`);
  const method = await wait(`(document.querySelector('[data-method="1"] a') || { getAttribute: () => '' }).getAttribute('href')`, 15000, "the Method note's link");
  check(method === METHOD.href, `the Method note is linked from the view (${method})`);

  // windows: the mouse, then the keyboard
  const thirty = await click('[data-week-window-choice="30"]', `document.querySelector('[data-week="1"]').dataset.weekDays === '30'`, "thirty days");
  const all = thirty.rows;   // the rows of thirty days with their own marks: what every filter below is read against
  const in7 = (r) => r.date >= sinceDay(thirty.today, 7), in30 = (r) => r.date >= sinceDay(thirty.today, 30);
  check(thirty.days === 30 && same(query(thirty.search), { view: "week", days: "30" }) && same(thirty.window, ["30"]) && all.every(in30) && all.length === thirty.shown && all.length >= seven.rows.length,
    `thirty days: the switch answers the mouse, the address says days=30, ${all.length} rows, each dated ${sinceDay(thirty.today, 30)} or later`);
  check(seven.rows.every(in7) && same(ids(seven.rows), ids(all.filter(in7))) && seven.rows.length === seven.shown, `seven days: ${seven.rows.length} rows, each dated ${sinceDay(seven.today, 7)} or later, and exactly the rows of thirty days that are`);
  check(new Set(ids(all)).size === all.length && same(ids(all.filter((r, i) => i === 0 || all[i - 1].body !== r.body || all[i - 1].date >= r.date)), ids(all)) && thirty.groups.every((g) => g[1] === g[2]) && thirty.groups.reduce((s, g) => s + g[1], 0) === all.length,
    `the list is in groups by agency (${thirty.groups.map((g) => `${g[0]} ${g[1]}`).join(", ")}), newest first in each, no row twice`);
  await evaluate(`document.querySelector('[data-week-window-choice="7"]').focus()`);
  await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13, text: "\r" });
  await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
  await wait(`document.querySelector('[data-week="1"]').dataset.weekDays === '7'`, 15000, "seven days by the keyboard");
  const back = await read();
  check(back.days === 7 && same(query(back.search), { view: "week" }) && same(ids(back.rows), ids(seven.rows)), "the switch answers the keyboard: Enter on \"Last 7 days\" brings the seven days and their address back");
  await click('[data-week-window-choice="30"]', `document.querySelector('[data-week="1"]').dataset.weekDays === '30'`, "thirty days");

  // rows: a date, a status, a link, a read marked as a model's or the placeholder
  {
    const wrong = [];
    for (const r of all) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(r.date) || !/^\d{1,2} [A-Z][a-z]{2} \d{4}$/.test(r.dateWords)) wrong.push(`${r.id}: no date`);
      if (!r.status || !r.statusTip) wrong.push(`${r.id}: no status, or a status with no hover`);
      if (!/^https?:\/\/\S/.test(r.href) || !r.linkWords || r.linkTip.length < 10) wrong.push(`${r.id}: no link to a source document, or a link with no hover`);
      if (r.read === "model" ? !(r.markWords.toLowerCase() === "model's read" && r.markTip.startsWith("A model's read") && r.readText.length > r.markWords.length + 5) : !(r.read === "none" && r.noneWords === NO_READ && r.noneTip.length > 10)) wrong.push(`${r.id}: its read is neither marked as a model's nor the placeholder`);
      if (!r.topicTips) wrong.push(`${r.id}: a topic with no hover`);
    }
    const withRead = (rows) => rows.filter((r) => r.read === "model").length;
    check(wrong.length === 0 && all.length > 0, `every row has a date, a status, a link with a hover and a read marked "model's read" or "${NO_READ}" (thirty days: ${all.length} rows, ${withRead(all)} with a read, ${all.length - withRead(all)} with the placeholder; seven days: ${seven.rows.length}, ${withRead(seven.rows)} with a read; ${all.filter((r) => r.kind === "docket").length} docket rows)${wrong.length ? `: ${wrong.slice(0, 4).join("; ")}` : ""}`);
    check(thirty.untitled === 0 && seven.untitled === 0, `every placeholder carries its reason on hover (${thirty.placeholders} placeholders at thirty days)`);
  }

  // filters: each changes the rows and the address; the rows are exactly those of the window that carry the mark
  const state = (k, v) => `(() => { const b = document.querySelector('[data-week-${k}="${v}"]'); return !!b && b.getAttribute('aria-pressed') === 'true'; })()`;
  {
    const bodies = await evaluate(`[...document.querySelectorAll('[data-week-filter="agency"] [data-week-agency]')].map((b) => ({ key: b.dataset.weekAgency, label: b.textContent.trim(), tip: b.title }))`);
    const held = [...new Set(all.map((r) => r.body))];
    check(bodies[0].key === "" && held.every((k) => bodies.some((b) => b.key === k)) && bodies.slice(1).every((b) => b.tip.length > 3), `the agency filter names ${bodies.length - 1} agencies and regulators (${bodies.slice(1).map((b) => b.label).join(", ")}), each with a hover`);
    let right = true, said = [];
    for (const k of held.slice(0, 3)) {
      const got = await click(`[data-week-agency="${k}"]`, state("agency", k), `the agency ${k}`);
      const want = all.filter((r) => r.body === k);
      if (!(same(ids(got.rows), ids(want)) && query(got.search).agency === k && got.shown === want.length && got.rows.length < all.length + (held.length === 1 ? 1 : 0))) right = false;
      said.push(`${k} ${got.rows.length}`);
    }
    check(right && held.length > 0, `the agency filter changes the rows and the address (${said.join(", ")} of ${all.length})`);
    const none = bodies.slice(1).find((b) => !held.includes(b.key));
    if (none) {
      const got = await click(`[data-week-agency="${none.key}"]`, state("agency", none.key), `the agency ${none.key}`);
      check(got.rows.length === 0 && got.state === "none" && got.empty?.words === NONE_WORDS && got.empty.why.includes(none.label) && query(got.search).agency === none.key, `a filter that leaves nothing shows "${NONE_WORDS}" with its reason on hover (${none.label}: "${got.empty?.why ?? ""}")`);
    } else console.log("not proven here: every agency of the filter holds a row in thirty days, so no agency leaves nothing");
    await click('[data-week-agency=""]', state("agency", ""), "every agency");
  }
  {
    const topics = await evaluate(`[...document.querySelectorAll('[data-week-filter="topic"] [data-week-topic-choice]')].map((b) => ({ key: b.dataset.weekTopicChoice, label: b.textContent.trim(), tip: b.title }))`);
    check(topics.length === 9 && topics.slice(1).every((t) => t.tip.length > 20), `the topic filter names eight topics, each with a hover (${topics.slice(1).map((t) => t.label).join(", ")})`);
    let right = topics.length > 1, said = [], emptied = null;
    for (const t of topics.slice(1)) {
      const got = await click(`[data-week-topic-choice="${t.key}"]`, state("topic-choice", t.key), `the topic ${t.key}`);
      const want = all.filter((r) => r.topics.includes(t.key));
      if (!(same(ids(got.rows), ids(want)) && query(got.search).topic === t.key && got.shown === want.length)) right = false;
      if (!want.length) { if (!(got.empty?.words === NONE_WORDS && got.empty.why.length > 20)) right = false; emptied = t.label; }
      said.push(`${t.label} ${got.rows.length}`);
    }
    check(right, `the topic filter changes the rows and the address, each topic the rows that carry it (${said.join(", ")})${emptied ? `; one with none shows "${NONE_WORDS}"` : ""}`);
    await click('[data-week-topic-choice=""]', state("topic-choice", ""), "every topic");
  }
  {
    const grids = await evaluate(`[...document.querySelectorAll('[data-week-filter="grid"] [data-week-grid]')].map((b) => ({ key: b.dataset.weekGrid, label: b.textContent.trim(), tip: b.title }))`);
    check(same(grids.map((g) => g.label), ["All", "ERCOT", "PJM", "MISO", "CAISO", "NYISO", "ISO-NE", "SPP"]) && grids.slice(1).every((g) => g.tip.length > 10), "the grid filter names ERCOT, PJM, MISO, CAISO, NYISO, ISO-NE and SPP, each with a hover");
    let right = grids.length === 8, said = [], narrowed = false;
    for (const g of grids.slice(1).filter((x) => x.key !== "miso")) {
      const got = await click(`[data-week-grid="${g.key}"]`, state("grid", g.key), `the grid ${g.key}`);
      const want = all.filter((r) => r.grids === "all" || r.grids.split(" ").includes(g.key));
      if (!(same(ids(got.rows), ids(want)) && query(got.search).grid === g.key && got.shown === want.length)) right = false;
      if (want.length < all.length) narrowed = true;
      said.push(`${g.label} ${got.rows.length}`);
    }
    check(right && narrowed, `the grid filter changes the rows and the address: a grid's rows are those that name it and those that name no operator (${said.join(", ")} of ${all.length})`);
    if (grids.some((g) => g.key === "miso")) {
      const got = await click('[data-week-grid="miso"]', state("grid", "miso"), "MISO");
      check(got.state === "paused" && got.rows.length === 0 && got.tables === 0 && got.paused?.words === PAUSED_WORDS && got.paused.why === PAUSE_WHY && query(got.search).grid === "miso" && grids.find((g) => g.key === "miso").tip === PAUSE_WHY,
        `MISO shows "${PAUSED_WORDS}" with the site's hover, no row and no chart`);
    } else check(false, "MISO is a choice of the grid filter");
    const onlyMiso = all.filter((r) => r.grids === "miso");
    console.log(`     (${onlyMiso.length} rows of thirty days are under MISO alone: listed with no grid chosen, under no grid's filter)`);
    await click('[data-week-grid=""]', state("grid", ""), "every grid");
  }
  {
    const got = await click('button[data-week-large]', `document.querySelector('button[data-week-large]').getAttribute('aria-pressed') === 'true'`, "large loads only");
    const want = all.filter((r) => r.large === "1");
    check(same(ids(got.rows), ids(want)) && query(got.search).large === "1" && got.large && (want.length > 0 || got.empty?.words === NONE_WORDS) && want.every((r) => r.kind === "docket" || r.topics.includes("large_load")),
      `large loads only changes the rows and the address: ${want.length} of ${all.length} rows (${want.filter((r) => r.kind === "action").length} actions tagged large loads, ${want.filter((r) => r.kind === "docket").length} docket rows)`);
    const cleared = await click('[data-week-clear]', `document.querySelector('button[data-week-large]').getAttribute('aria-pressed') === 'false'`, "the filters cleared");
    check(same(ids(cleared.rows), ids(all)) && same(query(cleared.search), { view: "week", days: "30" }), "clearing the filters brings every row of the window back, and the plain address");
  }

  // a refusing regulator: named in the filter, marked, its hover the file's reason word for word
  if (refresh) {
    const marks = await evaluate(`[...document.querySelectorAll('[data-week-mark-refresh]')].map((m) => ({ of: m.dataset.weekMarkOf, kind: m.dataset.weekMarkRefresh, words: m.textContent.trim(), why: m.title, chip: !!m.parentElement.querySelector('button[data-week-agency="' + m.dataset.weekMarkOf + '"]') }))`);
    const off = refresh.regulators.filter((r) => r.refreshed === false);
    const wrong = off.filter((r) => { const m = marks.find((x) => x.of === r.key); return !(m && m.chip && m.kind === "not refreshed" && m.words === "not refreshed" && m.why === r.reason); });
    check(off.length > 0 && wrong.length === 0, `a regulator whose list refuses a plain request is named in the agency filter with the mark "not refreshed", its hover the file's reason word for word (${off.map((r) => r.short).join(", ")})${wrong.length ? `: WRONG ${wrong.map((r) => r.key).join(", ")}` : ""}`);
    const part = marks.filter((m) => m.kind === "in part");
    check(part.every((m) => m.why.length > 20 && m.chip), `${part.length} more are marked "in part", each hover saying which of its hosts is never asked (${part.map((m) => m.of).join(", ")})`);
    const eleven = await evaluate(`${JSON.stringify(refresh.regulators.map((r) => r.key))}.filter((k) => !document.querySelector('button[data-week-agency="' + k + '"]'))`);
    check(refresh.regulators.length === 11 && eleven.length === 0, "the eleven regulators are all choices of the agency filter");
  } else check(false, "data/policy/refresh.json is on the machine, so the refusing regulators' marks can be read against it");

  // the chart answers the mouse and the keyboard, and a click on a count filters the list
  {
    await wait(`!!document.querySelector('[data-hover="1"] table[data-chart="week"] [data-week-total]')`, 15000, "the chart");
    const cells = await evaluate(`[...document.querySelectorAll('table[data-chart="week"] [data-week-cell]')].map((c) => ({ key: c.dataset.weekCell, n: Number(c.dataset.n), button: c.tagName === 'BUTTON' }))`);
    const totals = await evaluate(`[...document.querySelectorAll('table[data-chart="week"] [data-week-total]')].map((c) => [c.dataset.weekTotal, Number(c.dataset.n)])`);
    const byBody = (k) => all.filter((r) => r.body === k);
    const rightTotals = totals.every(([k, v]) => byBody(k).length === v) && totals.reduce((s, x) => s + x[1], 0) === all.length;
    const rightCells = cells.every((c) => { const [b, t] = c.key.split("|"); return c.n === byBody(b).filter((r) => (t ? r.topics.includes(t) : r.topics.length === 0)).length; });
    check(rightTotals && rightCells && totals.length > 0, `the chart counts the list: ${totals.length} agencies, ${cells.length} counts by topic, each the number of rows that carry it (${totals.map((x) => x.join(" ")).join(", ")})`);
    const hover = (sel) => evaluate(`(async () => {
      const mark = document.querySelector(${JSON.stringify(sel)});
      if (!mark) return null;
      const r = mark.getBoundingClientRect();
      for (let i = 0; i < 20; i += 1) {
        mark.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 }));
        await new Promise((ok) => setTimeout(ok, 150));
        const box = mark.closest('[data-hover="1"]').querySelector('[data-tooltip="1"]');
        if (box) return box.textContent;
      }
      return '';
    })()`);
    const tip = await hover('table[data-chart="week"] [data-week-total]');
    check(typeof tip === "string" && /^.+: \d+ actions? in all in the last 30 days$/.test(tip), `the chart answers the mouse ("${String(tip).slice(0, 110)}")`);
    const live = cells.find((c) => c.button && c.key.split("|")[1]);
    const focusTip = await evaluate(`(async () => { const b = document.querySelector(${JSON.stringify(live ? `[data-week-cell="${live.key}"]` : "[data-week-total]")}); b.focus(); await new Promise((ok) => setTimeout(ok, 400)); const box = b.closest('[data-hover="1"]').querySelector('[data-tooltip="1"]'); return box ? box.textContent : ''; })()`);
    check(/: \d+ actions? .*in the last 30 days$/.test(String(focusTip)), `the chart answers the keyboard: a count that takes the focus shows its words ("${String(focusTip).slice(0, 110)}")`);
    if (live) {
      const [b, t] = live.key.split("|");
      const got = await click(`[data-week-cell="${live.key}"]`, `${state("agency", b)} && ${state("topic-choice", t)}`, "a count clicked");
      const want = all.filter((r) => r.body === b && r.topics.includes(t));
      check(same(ids(got.rows), ids(want)) && got.rows.length === live.n && query(got.search).agency === b && query(got.search).topic === t, `a click on a count lists its actions and writes the address (${b}, ${t}: ${live.n})`);
    } else {
      const [b, v] = totals[0];
      const got = await click(`[data-week-total="${b}"]`, state("agency", b), "a total clicked");
      check(same(ids(got.rows), ids(byBody(b))) && got.rows.length === v && query(got.search).agency === b, `a click on a count lists its actions and writes the address (${b}: ${v}; no topic holds a row in thirty days, so an agency's total was clicked)`);
    }
    const out = await evaluate(`[...document.querySelectorAll('[data-chart]')].filter((s) => !s.closest('[data-hover="1"]')).length`);
    check(out === 0, "no chart stands outside a hover frame");
  }

  // the address restores the view: on the server (no script) and in the browser
  {
    // a row that carries a topic and names a grid, where thirty days hold one: its agency, topic, grid and mark are the address
    const pick = all.find((r) => r.topics.length && r.grids !== "all" && r.grids.split(" ").some((g) => g && g !== "miso")) ?? all.find((r) => r.topics.length) ?? all[0];
    const body = pick.body, topic = pick.topics[0] ?? "", large = pick.large === "1";
    const grid = pick.grids === "all" ? "pjm" : pick.grids.split(" ").find((g) => g && g !== "miso") ?? "pjm";
    const want = all.filter((r) => r.body === body && (!topic || r.topics.includes(topic)) && (r.grids === "all" || r.grids.split(" ").includes(grid)) && (!large || r.large === "1"));
    const path = `/policy?view=week&days=30&agency=${body}${topic ? `&topic=${topic}` : ""}&grid=${grid}${large ? "&large=1" : ""}`;
    const server = await get(path);
    check(same(rowsIn(server.html), ids(want)) && new RegExp(`data-week-days="30"`).test(server.html), `the address restores the view on the server, before any script runs (${path}: ${want.length} rows)`);
    await go(base + path);
    await ready();
    const got = await read();
    check(got.days === 30 && same(got.agency, [body]) && same(got.topic, [topic]) && same(got.grid, [grid]) && got.large === large && want.length > 0 && same(ids(got.rows), ids(want)) && got.search === path.slice("/policy".length), "the address restores the view in the browser: the window, the filters and the rows");
    await go(`${base}/policy?view=week&days=365&agency=nobody&topic=zoning&grid=mars&large=maybe`);
    await ready();
    const odd = await read();
    check(odd.days === 7 && same(odd.agency, [""]) && same(odd.topic, [""]) && same(odd.grid, [""]) && !odd.large && same(ids(odd.rows), ids(seven.rows)), "an address the view does not understand opens seven days with no filter");
    await go(`${base}/policy?view=week&grid=miso&days=30`);
    await ready();
    const miso = await read();
    check(miso.state === "paused" && miso.rows.length === 0 && miso.paused?.words === PAUSED_WORDS && rowsIn((await get("/policy?view=week&grid=miso&days=30")).html).length === 0, "an address that names MISO shows the fixed words and no row, on the server too");
  }

  // the other view still works in the browser
  await go(`${base}/policy`);
  await wait(`document.querySelectorAll('tr.cursor-pointer').length > 0 && document.querySelectorAll('select').length >= 5`, 30000, "the table of every action");
  const old = await evaluate(`(() => { const rows = document.querySelectorAll('tr.cursor-pointer').length; rows && document.querySelector('tr.cursor-pointer').click(); return { rows, selects: document.querySelectorAll('select').length, date: document.querySelectorAll('input[type="date"]').length }; })()`);
  await wait(`!!document.querySelector('td[colspan="6"]')`, 15000, "a row of the table opened");
  check(old.rows > 0 && old.selects === 5 && old.date === 1, `the view of every action still works in the browser: ${old.rows} rows drawn, five selects and a date, and a row opens to its detail`);
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors.slice(0, 2).join(" | ").slice(0, 200)}` : ""}`);
  return 0;
});
if (code === null) { console.log("FAILED: no Chrome or Edge on this machine, so the view was not read in a browser"); bad += 1; }
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
