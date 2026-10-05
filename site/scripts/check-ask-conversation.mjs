// Energy Research Warehouse (ERW) site, session 121: Ask ERCOT's conversation, in a real browser.
//
//   npm run build && npx next start -p 3049
//   node scripts/check-ask-conversation.mjs [base-url]      (default http://localhost:3049)
//
// IT ASKS THREE QUESTIONS: THREE MODEL CALLS THAT COST MONEY (a few cents in all). It is run by a person or a session
// that has the spend to make, never by a workflow. In the internal view it opens /ask/ercot and:
//   1. asks a question with a series: the page shows what is being read before the answer; the answer comes with a
//      chart, and the line under the chart says how many of the fetched rows it shows;
//   2. asks "And a year earlier?": the answer stays below the first (two turns on the page), is an answer and not a
//      refusal, and names the year before, which only the conversation could tell it;
//   3. asks something outside the tables: a refusal, with a box of the nearest tables held, each a table of the guide.
// Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3049").replace(/\/$/, "");
const spec = JSON.parse(fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "lib", "chat", "spec_ercot.json"), "utf8"));
let bad = 0;
const check = (ok, what) => { if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
// type into React's input and submit the form
const askJs = (q) => `(() => { const i = document.querySelector('#q'); const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; set.call(i, ${JSON.stringify(q)});
  i.dispatchEvent(new Event('input', { bubbles: true })); setTimeout(() => i.form.requestSubmit(), 50); return true; })()`;
const turn = (n) => `(() => { const s = document.querySelector('[data-turn="${n}"]'); if (!s) return null; return { status: s.getAttribute('data-status'), answer: s.querySelector('[data-answer]')?.innerText ?? '',
  chart: s.querySelector('[data-chart-check]')?.getAttribute('data-chart-check') ?? null, chartText: s.querySelector('[data-chart-check]')?.innerText ?? '',
  nearest: [...s.querySelectorAll('[data-nearest] li')].map((li) => li.innerText), premise: s.querySelector('[data-premise]')?.innerText ?? null }; })()`;

const code = await withBrowser(async ({ go, evaluate, wait, unlock, sleep }) => {
  await unlock(base);
  await go(`${base}/ask/ercot`);
  await wait(`!!document.querySelector('#q')`, 15000, "the question box");

  await evaluate(askJs("How many MW of batteries were operating in ERCOT in December of each year from 2020 to 2024?"));
  let sawProgress = false;
  for (let i = 0; i < 400; i += 1) {
    const p = await evaluate(`document.querySelector('[data-progress]')?.getAttribute('data-progress') ?? null`);
    if (p !== null && Number(p) > 0) sawProgress = true;
    if (await evaluate(`!!document.querySelector('[data-turn="1"]')`)) break;
    await sleep(150);
  }
  const t1 = await evaluate(turn(1));
  check(!!t1 && t1.status === "answered" && t1.answer.length > 20, `turn 1 is an answer (${t1?.status})`);
  check(sawProgress, "while it was answered the page named a table being read");
  const [drawn, rows] = (t1?.chart ?? "0/0").split("/").map(Number);
  check(!!t1?.chart && rows >= 3 && drawn <= rows && t1.chartText.includes(String(rows)), `turn 1 has a chart and says how many of the ${rows} fetched rows it shows (${t1?.chart})`);

  await evaluate(askJs("And a year earlier than the first of those?"));
  await wait(`!!document.querySelector('[data-turn="2"]')`, 90000, "the second answer");
  const t2 = await evaluate(turn(2));
  check(!!t2 && t2.status === "answered", `turn 2 is an answer, not a refusal (${t2?.status})`);
  check(!!t2 && t2.answer.includes("2019"), "turn 2 names 2019, which only the conversation could tell it");
  check(await evaluate(`document.querySelectorAll('[data-turn]').length === 2 && !!document.querySelector('[data-turn="1"] [data-answer]')`), "the first answer is still on the page above the second");

  await evaluate(askJs("What does a household in Houston pay per kWh on its electricity bill?"));
  await wait(`!!document.querySelector('[data-turn="3"]')`, 90000, "the third answer");
  const t3 = await evaluate(turn(3));
  check(!!t3 && t3.status === "not_in_warehouse", `turn 3 is a refusal (${t3?.status})`);
  check(!!t3 && t3.nearest.length >= 1 && t3.nearest.every((x) => spec.tables.some((t) => x.startsWith(t + ":"))), `the refusal shows the nearest tables held, each a table of the guide (${t3?.nearest.map((x) => x.split(":")[0]).join(", ")})`);
  check(!!t3 && t3.nearest.every((x) => spec.tables.some((t) => x === `${t}: ${spec.holds[t]}`)), "and beside each, the guide's own sentence of what it holds");
  return bad ? 1 : 0;
});
if (code === null) { console.log("not proven here: no browser on this machine"); process.exit(0); }
console.log(bad ? `${bad} failed` : "the conversation holds");
process.exit(code);
