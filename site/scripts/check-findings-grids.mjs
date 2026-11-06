// Energy Research Warehouse (ERW) site, session 182: the three finding cards in a real browser.
//
//   npm run build && npx next start -p 3182
//   node scripts/check-findings-grids.mjs [base-url] [--shots dir]      (default http://localhost:3182)
//
// For "Batteries ate their own lunch? Five grids" and "The peak hour moved: five grids", at desktop width and at a
// phone's 390 px:
//   multiples  the small multiples are drawn (one drawing, one SVG panel a grid), the axes are stated on the chart, MISO and PJM are greyed
//              placeholders, and the page does not scroll sideways
//   one grid   a click on a grid shows it large: its chart, its three callouts as the card's JSON holds them, its
//              regression table where the card has one, its words and its caveat; the address keeps the choice
//              (?<param>=<grid>), and opening that address shows the same grid
//   ERCOT      the one-grid view of ERCOT prints the old ERCOT card's callout numbers
// For the hourly curtailment card: drawn, with its effect table, at both widths, no sideways scroll.
// The render frames (1080 x 1350 and 1600 x 900, ?render=1): the whole card on the picture, no control on it, and
// (session 588) the lowest chart text above the callouts' top.
// With --shots, a PNG of each view is written (the phone views are what the report describes). Exit 1 on a failure;
// 2 when no browser is on the machine.
// Session 474: sessions 317 and 318 drew the cards' charts in the shared SVG set (components/SvgOption.tsx), so every
// wait for a canvas waited 30 s for something no page draws any more and the check failed on production; it now waits
// for the drawing's SVG, and the small multiples are counted as panels (data-panel), one a grid of the card's JSON.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const base = (args.find((a) => a.startsWith("http")) ?? "http://localhost:3182").replace(/\/$/, "");
const shots = args.includes("--shots") ? args[args.indexOf("--shots") + 1] : null;
const card = (id) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "findings", `${id}.json`), "utf-8"));
let bad = 0, n = 0;
const lines = [];
const check = (ok, what) => { n += 1; if (!ok) bad += 1; lines.push(`${ok ? "ok  " : "FAIL"} ${what}`); };

const code = await withBrowser(async ({ go, wait, unlock, send, sleep, errors }) => {
  const js = async (expression) => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true })).result?.value;
  const size = (w, h) => send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: w < 500 });
  const shot = async (name) => {
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    const m = await js("({ w: document.documentElement.clientWidth, h: Math.min(document.documentElement.scrollHeight, 5000) })");
    const s = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: m.w, height: m.h, scale: 1 } });
    fs.writeFileSync(path.join(shots, `${name}.png`), Buffer.from(s.data, "base64"));
  };
  const sideways = () => js("document.documentElement.scrollWidth - document.documentElement.clientWidth");
  await unlock(base);
  for (const [w, h, tag] of [[1280, 900, "desktop"], [390, 844, "phone"]]) {
    await size(w, h);
    for (const id of ["batteries_lunch_grids", "peak_hour_grids"]) {
      const c = card(id);
      const param = c.chart.param;
      const t = `${id} ${tag}:`;
      await go(`${base}/research/card/${id}`);
      await wait('!!document.querySelector("[data-finding-chart=\\"multiples\\"] [data-panel] svg")', 30000, "the small multiples");
      await sleep(600);
      check((await js('document.querySelectorAll("[data-finding-chart=\\"multiples\\"]").length')) === 1
        && (await js('[...document.querySelectorAll("[data-finding-chart=\\"multiples\\"] [data-panel]")].filter((e) => e.querySelector("svg")).length')) === c.chart.panels.length,
        `${t} the small multiples are drawn (${c.chart.panels.length} panels, each an SVG)`);
      check((await js('document.querySelector("[data-multi-view]").getAttribute("data-multi-view")')) === "all", `${t} every grid is the first view`);
      const note = await js('document.querySelector("[data-multi-note]").textContent');
      check(note.includes("One timeline for every grid") && note.includes("Left axis") && note.includes("Right axis"), `${t} the axes are stated on the chart`);
      check((await js('[...document.querySelectorAll("[data-placeholder]")].map((e) => e.textContent).join("|")')) === "MISO: paused while terms are reviewed|PJM: licensed source needed", `${t} MISO and PJM are placeholders`);
      check((await js('document.querySelectorAll("[data-multi-pick]").length')) === 6, `${t} the control offers every grid and each of the five`);
      const box = await js('(() => { const r = document.querySelector("[data-finding-chart=\\"multiples\\"]").getBoundingClientRect(); return { w: r.width, h: r.height }; })()');
      check(box.h / 5 >= 84, `${t} the five panels stack as rows of ${Math.round(box.h / 5)} px in a chart ${Math.round(box.w)} px wide`);
      check((await sideways()) <= 0, `${t} no sideways scroll`);
      await shot(`${id}_${tag}_all`);
      for (const p of c.chart.panels) {
        await js(`document.querySelector('[data-multi-pick="${p.grid}"]').click()`);
        await wait(`!!document.querySelector('[data-multi-grid="${p.grid}"] svg')`, 20000, `${p.grid} large`);
        const got = await js(`(() => { const r = document.querySelector('[data-multi-grid="${p.grid}"]'); return {
          before: [...r.querySelectorAll("[data-grid-before]")].map((e) => e.textContent), after: [...r.querySelectorAll("[data-grid-after]")].map((e) => e.textContent),
          rows: r.querySelectorAll("[data-grid-table] tbody tr").length, words: r.querySelector("[data-grid-words]").textContent, caveat: r.querySelector("[data-grid-caveat]").textContent,
          search: location.search }; })()`);
        check(JSON.stringify(got.before) === JSON.stringify(p.callouts.map((x) => x.before.text)) && JSON.stringify(got.after) === JSON.stringify(p.callouts.map((x) => x.after.text)),
          `${t} ${p.grid} large: callouts ${got.before.join(", ")} then ${got.after.join(", ")}`);
        check(got.rows === p.table.length, `${t} ${p.grid} large: ${p.table.length} regression rows`);
        check(got.words === p.in_words && got.caveat === p.caveat, `${t} ${p.grid} large: its words and its caveat`);
        check(new URLSearchParams(got.search).get(param) === p.grid, `${t} ${p.grid} large: the address keeps it (${got.search})`);
        check((await sideways()) <= 0, `${t} ${p.grid} large: no sideways scroll`);
        if (p.grid === "ercot" || p.grid === "nyiso") await shot(`${id}_${tag}_${p.grid}`);
      }
      await go(`${base}/research/card/${id}?${param}=ercot`);
      await wait('!!document.querySelector("[data-multi-grid=\\"ercot\\"] svg")', 20000, "ERCOT from the address");
      check(true, `${t} ?${param}=ercot opens ERCOT large`);
      if (id === "batteries_lunch_grids") {
        const old = card("batteries_lunch");
        const b = await js('[...document.querySelectorAll("[data-multi-grid=\\"ercot\\"] [data-grid-before], [data-multi-grid=\\"ercot\\"] [data-grid-after]")].map((e) => e.textContent).sort().join("|")');
        check(b === old.callouts.flatMap((x) => [x.before.text, x.after.text]).sort().join("|"), `${t} ERCOT large prints the old ERCOT card's callouts (${b})`);
      }
      await js('document.querySelector(\'[data-multi-pick="all"]\').click()');
      await sleep(300);
      check((await js("location.search")) === "", `${t} back to every grid clears the address`);
      if (c.chart.measures.length > 1) {
        const k = c.chart.measures[1].key;
        await js(`document.querySelector('[data-multi-measure="${k}"]').click()`);
        await sleep(400);
        check(new URLSearchParams(await js("location.search")).get(`${param}_measure`) === k, `${t} the measure ${k} is kept in the address`);
      }
    }
    const id = "batteries_curtailment_hourly";
    await go(`${base}/research/card/${id}`);
    await wait(`!!document.querySelector('[data-card="${id}"] [data-finding-chart] svg')`, 30000, "the hourly card's chart");
    await sleep(500);
    check((await js('document.querySelectorAll("[data-effect-table] tbody tr").length')) === card(id).effect_table.rows.length, `${id} ${tag}: the effect table`);
    check((await sideways()) <= 0, `${id} ${tag}: no sideways scroll`);
    await shot(`${id}_${tag}`);
  }
  // the photograph's frame holds the whole card: nothing is cut at the foot or the side of either picture
  for (const id of ["batteries_lunch_grids", "peak_hour_grids", "batteries_curtailment_hourly", "batteries_curtailment"]) {
    for (const [w, h] of [[1080, 1350], [1600, 900]]) {
      await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: false });
      await go(`${base}/research/card/${id}?render=1`);
      await wait('!!document.querySelector("[data-render=\\"1\\"] [data-finding-chart] svg")', 30000, "the render frame's chart");
      await sleep(500);
      const m = await js("({ h: document.documentElement.scrollHeight, w: document.documentElement.scrollWidth, foot: Math.round(document.querySelector('.finding-render-foot').getBoundingClientRect().bottom), controls: [...document.querySelectorAll('.multi-controls')].filter((e) => e.offsetParent !== null).length })");
      check(m.foot <= h && m.h <= h && m.w <= w, `${id} ${w} x ${h}: the whole card is on the picture (its last line ends at ${m.foot} of ${h} px)`);
      check(m.controls === 0, `${id} ${w} x ${h}: no control on the picture`);
      // session 588: the chart is not drawn over the card's words; the lowest text of the drawing (an axis label, a
      // series' name) ends above the callouts' top (the paragraph's, on a card without callouts). In the tall frame the
      // five panels ran in one column to 870 px, over the callouts' boxes near 830 (docs/brand/review-497/after/)
      const low = await js("(() => { const t = [...document.querySelectorAll('[data-render=\"1\"] [data-finding-chart] svg text')].map((e) => e.getBoundingClientRect()).filter((r) => r.height > 0); const below = document.querySelector('[data-render=\"1\"] .finding-callouts') ?? document.querySelector('[data-render=\"1\"] .finding-why'); return { text: Math.round(Math.max(0, ...t.map((r) => r.bottom))), top: below ? Math.round(below.getBoundingClientRect().top) : null, n: t.length }; })()");
      check(low.n > 0 && low.top !== null && low.text <= low.top, `${id} ${w} x ${h}: the lowest chart text ends at ${low.text} px, above the callouts' top at ${low.top} px`);
      // and in the tall frame's small multiples, no two of a panel's timeline labels run into each other (its two
      // columns made each panel half as wide). The wide frame's five side by side panels (session 497) are not held to
      // it: their plots are some 20 px wide and the peak hour card's eight years print over each other there, a layout
      // choice listed for Samuel in session 588's report
      const gap = await js("(() => { let worst = null; for (const p of document.querySelectorAll('[data-render=\"1\"] [data-finding-chart=\"multiples\"] [data-panel] svg')) { const t = [...p.querySelectorAll('text[text-anchor=\"middle\"]')].map((e) => e.getBoundingClientRect()).filter((r) => r.width > 0).sort((a, b) => a.left - b.left); for (let i = 1; i < t.length; i++) worst = Math.min(worst ?? 1e9, t[i].left - t[i - 1].right); } return worst; })()");
      if (gap !== null && h > w) check(gap >= 0, `${id} ${w} x ${h}: the panels' timeline labels stand apart (the closest two ${Math.round(gap * 10) / 10} px)`);
    }
  }
  const errs = errors.filter((e) => !/favicon/.test(String(e)));
  check(errs.length === 0, `no page error (${errs.slice(0, 3).join("; ") || "none"})`);
  return bad ? 1 : 0;
}, { width: 1280, height: 900 });

const text = lines.join("\n") + `\n${n - bad} of ${n} checks passed\n`;
await new Promise((done) => process.stdout.write(text, done));
if (code === null) { console.log("no Chrome or Edge on this machine: not checked here"); process.exitCode = 2; } else process.exitCode = bad || code ? 1 : 0;
