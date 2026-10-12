// Energy Research Warehouse (ERW) site, session 195: the face of the three decision pages now that they share one
// decisions block (components/decisions/ScenarioBlock.tsx) and scenario A sets each page's headline.
//
//   npm run build && npm start
//   node scripts/check-decisions-face.mjs [base-url] [output-dir]
//
// For /cost-of-power/battery, /cost-of-power/seller and /cost-of-power, in the internal view, at 1280 and at 390 px, in
// four states: the defaults; scenario A changed; scenario B changed as well; and the link a session report gave
// (179, 186, 194), opened cold. At 1280 the changes are typed as a reader types them; at 390 the address the typing
// left is opened, so the address round trip is part of the check. In every state it reads the page's own text and
// holds that:
//   1. the block is drawn, with no "undefined" and no "NaN" anywhere on the page;
//   2. the three headline numbers are scenario A's rows of the table, to the digit shown;
//   3. the sentence under the table states scenario A, whichever scenario is in view;
//   4. no sentence of the headline, of the panel's note or of the block tells the reader what to do;
//   5. at 390 px the page does not scroll sideways;
//   6. a change of B leaves the headline as it was.
// It prints every number it read (the session report quotes them from here), writes them to <output-dir>/face.json and
// a screenshot of each state to <output-dir>/<page>-<state>-<width>.png. Exits 1 if any assertion fails; 0 with a note
// when the machine has no browser.
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const outDir = process.argv[3];
let failed = 0, n = 0;
const check = (ok, what, detail = "") => { n += 1; if (!ok) failed += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`); };
// words that tell a reader what to do; a sentence of these pages states a number and its condition
const ADVICE = /\b(should|better|worth|attractive|recommend\w*|advis\w*|ought|prefer\w*|ideal\w*)\b/i;

const PAGES = [
  { id: "battery", path: "/cost-of-power/battery", rows: ["revenue", "p10", "coverage"], sentence: "[data-npv-sentence]",
    a: [["capex", "1300"]], b: [["hurdle", "10"], ["term", "10"]], link: "?ac=1300&bt=10&be=92&by=2&bh=10&v=b", from: "session 179" },
  { id: "seller", path: "/cost-of-power/seller", rows: ["revenue", "capture", "coverage"], sentence: "[data-npv-sentence]",
    a: [["capex", "1500"]], b: [["hurdle", "10"], ["term", "10"], ["deg", "0.5"]], link: "?ac=1500&bt=10&bd=0.5&bh=10&v=b", from: "session 186" },
  { id: "datacenter", path: "/cost-of-power", rows: ["price", "bad", "gpu"], sentence: "[data-pv-sentence]",
    a: [["pue", "1.2"]], b: [["upfront", "50"], ["hurdle", "10"]], link: "?ap=1.2&bw=1&bu=50&bh=10&v=b", from: "session 194" },
];

const out = [];
const code = await withBrowser(async ({ go, evaluate, send, unlock, sleep }) => {
  await unlock(base);
  const size = async (width) => send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
  const shot = async (name, width) => {
    if (!outDir) return;
    fs.mkdirSync(outDir, { recursive: true });
    const { cssContentSize } = await send("Page.getLayoutMetrics");
    const height = Math.min(Math.ceil(cssContentSize.height), 12000);
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await sleep(400);
    const s = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height, scale: 1 } });
    fs.writeFileSync(path.join(outDir, `${name}.png`), Buffer.from(s.data, "base64"));
    await size(width);
  };
  const type = async (k, text) => {
    await evaluate(`(() => { const e = document.querySelector('input[data-assumption="${k}"]'); e.scrollIntoView({ block: "center" }); e.focus(); e.select(); })()`);
    await send("Input.insertText", { text });
    await sleep(350);
    await evaluate(`document.activeElement && document.activeElement.blur()`);
    await sleep(150);
  };
  const read = (p) => evaluate(`(() => {
    const root = document.querySelector("[data-scenarios]");
    if (!root) return null;
    const sum = document.querySelector("[data-summary]");
    // the headline row follows the summary sentence; on the generator's page the summary is the block before it
    let row = sum?.nextElementSibling;
    while (row && !/sm:grid-cols-3/.test(row.className)) row = row.nextElementSibling;
    const cell = (k) => { const c = root.querySelector('[data-cell="' + k + '"]'); if (!c) return null; const first = c.firstChild; return { v: (first?.textContent ?? "").trim(), text: c.textContent, raw: c.getAttribute("data-raw") }; };
    const main = document.querySelector("main") ?? document.body;
    return {
      view: root.querySelector("[data-assumptions]").getAttribute("data-assumptions"),
      summary: (sum?.textContent ?? "").replace(/\\s+/g, " ").trim(), headline: (row?.innerText ?? "").replace(/\\s+/g, " ").trim(),
      a: Object.fromEntries(${JSON.stringify(p.rows)}.map((k) => [k, cell("a|" + k)])), b: Object.fromEntries(${JSON.stringify(p.rows)}.map((k) => [k, cell("b|" + k)])),
      rows: [...root.querySelectorAll("[data-scenario-table] tbody tr")].map((r) => r.getAttribute("data-row")),
      table: [...root.querySelectorAll("[data-cell]")].map((c) => [c.getAttribute("data-cell"), c.textContent]),
      differs: root.querySelector("[data-differs-words]")?.textContent ?? "", against: root.querySelector("[data-against-words]")?.textContent ?? "",
      sentence: root.querySelector(${JSON.stringify(p.sentence)})?.textContent ?? "", chart: root.querySelector("[data-sensitivity] figcaption span")?.textContent ?? "",
      bars: root.querySelectorAll("[data-bar]").length,
      block: root.innerText, panel: document.querySelector("[data-costs-in-a]")?.textContent ?? "",
      fields: [...document.querySelectorAll("aside form input[name]")].map((e) => e.name),
      bad: /undefined|NaN/.test(main.innerText), search: location.search,
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    };
  })()`);
  const numeral = (v) => v.replace(/^USD /, "").replace(/ times$/, "").replace(/ with$/, "");

  for (const p of PAGES) {
    let typed = { a: "", b: "" }, headA = "";
    for (const width of [1280, 390]) {
      const states = [
        ["defaults", async () => { await go(base + p.path); }],
        ["a-changed", async () => {
          if (width === 1280) { for (const [k, v] of p.a) await type(k, v); typed.a = await evaluate("location.search"); }
          else await go(base + p.path + typed.a);
        }],
        ["b-changed", async () => {
          if (width === 1280) { await evaluate(`document.querySelector('[data-view="b"]').click()`); await sleep(350); for (const [k, v] of p.b) await type(k, v); typed.b = await evaluate("location.search"); }
          else await go(base + p.path + typed.b);
        }],
        ["shared-link", async () => { await go(base + p.path + p.link); }],
      ];
      await size(width);
      for (const [name, act] of states) {
        await act();
        await sleep(name === "defaults" || name === "shared-link" || width === 390 ? 1800 : 400);
        const s = await read(p);
        const tag = `${p.id}, ${name}, ${width} px`;
        check(!!s && s.rows.length >= 8 && s.bars >= 8 && !s.bad, `${tag}: the block is drawn, with no "undefined" and no "NaN" on the page`, s ? `${s.rows.length} rows, ${s.bars} bars` : "no block");
        if (!s) continue;
        const want = p.rows.map((k) => s.a[k]?.v ?? "").map(numeral);
        check(want.every((v) => v && s.headline.includes(v)), `${tag}: the three headline numbers are scenario A's rows`, `${want.join(" | ")} in "${s.headline.slice(0, 110)}"`);
        check(/^Scenario A, /.test(s.sentence), `${tag}: the sentence under the table states scenario A (${s.view.toUpperCase()} in view)`, s.sentence);
        const said = [s.headline, s.summary, s.panel, s.block].join(" \n ");
        const hit = said.match(ADVICE);
        check(!hit, `${tag}: no sentence tells the reader what to do`, hit ? `"${hit[0]}" in: ${said.slice(Math.max(0, hit.index - 60), hit.index + 60)}` : "");
        check(!s.fields.some((f) => ["fom", "ds", "gpu", "pue"].includes(f)), `${tag}: the panel on the left holds none of the duplicate fields`, [...new Set(s.fields)].join(", "));
        if (width === 390) check(s.clientW === 390 && s.scrollW <= s.clientW + 1, `${tag}: the page does not scroll sideways`, `scroll width ${s.scrollW}`);
        if (name === "a-changed") headA = s.headline;
        if (name === "b-changed") check(s.headline === headA, `${tag}: the change of B left the headline as it was`);
        if (name === "shared-link") check(s.search === p.link, `${tag}: the link of ${p.from} keeps its address`, s.search);
        out.push({ page: p.id, state: name, width, address: p.path + s.search, summary: s.summary, headline: s.headline, a: s.a, b: s.b, table: s.table, differs: s.differs, against: s.against, sentence: s.sentence, chart: s.chart });
        console.log(`     ${p.path}${s.search}\n     headline: ${s.headline}\n     A: ${p.rows.map((k) => `${k} ${s.a[k]?.v}`).join("; ")} | B: ${p.rows.map((k) => `${k} ${s.b[k]?.v}`).join("; ")}\n     ${s.sentence}\n     ${s.differs}${s.against ? `\n     ${s.against}` : ""}`);
        await shot(`${p.id}-${name}-${width}`, width);
      }
    }
  }
  return failed ? 1 : 0;
});
if (code === null) { console.log("no Chrome or Edge on this machine: not proven here"); process.exit(0); }
if (outDir) fs.writeFileSync(path.join(outDir, "face.json"), JSON.stringify(out, null, 1));
console.log(failed ? `\ncheck-decisions-face FAILED: ${failed} of ${n}` : `\ncheck-decisions-face: all ${n} passed`);
process.exit(code);
