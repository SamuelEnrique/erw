// Energy Research Warehouse (ERW) site, session 113: /deals/v2 in a real browser, at a laptop's width or a phone's.
//
//   node scripts/check-deals-v2.mjs [base-url] [--phone] [--shot <file.png>]
//
// Opens the internal view (the page is in review) and checks what a reader meets: the choices in a fog beige panel to
// the left of the answer on a laptop and above it on a phone, no sideways scroll of the page, the headline count equal
// to the rows of the table, a source link on every row, "not stated" where a story gives no size, the one-click
// choices and the form each changing the address and the answer, and no error in the page. Exit 0 all passed, 1 some
// failed, 2 no browser on this machine (not proven here).
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";

const args = process.argv.slice(2);
const phone = args.includes("--phone");
const shot = args.includes("--shot") ? args[args.indexOf("--shot") + 1] : null;
const base = (args.find((a) => /^https?:/.test(a)) ?? "http://localhost:3000").replace(/\/$/, "");
const [width, height] = phone ? [390, 844] : [1280, 900];

let passed = 0, failed = 0;
const ok = (cond, what, detail = "") => { cond ? (passed += 1) : (failed += 1); console.log(`${cond ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`); };
const num = (s) => Number(String(s ?? "").replace(/,/g, ""));

const STATE = `(() => {
  const q = (s) => document.querySelector(s);
  const panel = q('section[aria-label="Your selection"]'), sentence = q('[data-deals-summary]');
  const rows = [...document.querySelectorAll('tr[data-deal]')];
  const box = (e) => { const r = e.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, bottom: r.bottom }; };
  return {
    title: q('h1')?.textContent ?? '', sentence: sentence?.textContent ?? '', count: q('[data-deals="count"]')?.textContent ?? '',
    mw: q('[data-deals="mw"]')?.textContent ?? '', withMw: q('[data-deals="with_mw"]')?.textContent ?? '',
    rows: rows.length, noLink: rows.filter((r) => ![...r.querySelectorAll('a')].some((a) => /^https?:/.test(a.getAttribute('href') ?? ''))).length,
    noSize: rows.filter((r) => r.querySelector('[data-deal-mw=""]')).length,
    noSizeSaid: rows.filter((r) => r.querySelector('[data-deal-mw=""]') && /not stated| MWh/.test(r.querySelector('[data-deal-mw=""]').textContent)).length,
    panel: panel ? box(panel) : null, answer: sentence ? box(sentence) : null, panelColor: panel ? getComputedStyle(panel).backgroundColor : '',
    paper: getComputedStyle(document.documentElement).getPropertyValue('--color-paper').trim(),
    pageWidth: document.scrollingElement.scrollWidth, window: window.innerWidth, bars: document.querySelectorAll('[data-deals-month]').length,
    barSum: [...document.querySelectorAll('[data-deals-month]')].reduce((a, g) => a + Number(g.getAttribute('data-deals-n')), 0),
    stated: q('[data-deals-stated]')?.textContent ?? '', href: location.pathname + location.search,
  };
})()`;

const code = await withBrowser(async ({ go, evaluate, wait, unlock, send, errors }) => {
  await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: phone });
  await unlock(base);
  await go(`${base}/deals/v2`);
  await wait(`!!document.querySelector('[data-deals-summary]')`, 20000, "the summary sentence");
  let s = await evaluate(STATE);
  ok(s.title === "The deals tracker", "the page is the tracker, not the in-review page", s.title);
  ok(num(s.count) > 0 && s.rows === num(s.count), "the headline count is the table's rows", `${s.count} and ${s.rows}`);
  ok(s.noLink === 0, "every row has a link to a source", `${s.noLink} without`);
  ok(s.noSize > 0 && s.noSizeSaid === s.noSize, "a row without a size says so", `${s.noSizeSaid} of ${s.noSize}`);
  ok(s.rows - s.noSize === num(s.withMw), "the deals that state a size are the ones counted", `${s.rows - s.noSize} and ${s.withMw}`);
  ok(s.barSum === s.rows && s.bars > 12, "the chart's months add up to the deals", `${s.barSum} in ${s.bars} months`);
  ok(/not a complete record/.test(await evaluate(`document.querySelector('h1').parentElement.textContent`)), "it says it is not a complete record");
  ok(/state a size in MW/.test(s.stated) && /state a price/.test(s.stated), "it says how many state a size and a price", s.stated.slice(0, 120));
  ok(s.pageWidth <= s.window + 1, "the page does not scroll sideways", `${s.pageWidth} in ${s.window}`);
  if (phone) ok(s.panel && s.answer && s.panel.bottom <= s.answer.top + 1, "on a phone the choices are above the answer", JSON.stringify([s.panel?.bottom, s.answer?.top]));
  else ok(s.panel && s.answer && s.panel.right <= s.answer.left && Math.abs(s.panel.top - s.answer.top) < 80, "on a laptop the choices are to the left of the answer", JSON.stringify([s.panel?.right, s.answer?.left]));
  // fog beige: the panel's colour is the paper token of app/tokens.css, and not white
  const paper = await evaluate(`(() => { const d = document.createElement('div'); d.className = 'bg-paper'; document.body.appendChild(d); const c = getComputedStyle(d).backgroundColor; d.remove(); return c; })()`);
  ok(s.panelColor === paper && !/255, 255, 255|0, 0, 0, 0/.test(s.panelColor), "the panel is fog beige", s.panelColor);
  if (shot) fs.writeFileSync(shot, Buffer.from((await send("Page.captureScreenshot", { format: "png" })).data, "base64"));
  const all = s;

  // the one-click choices
  for (const [view, label] of [["storage", "Storage only"], ["ai", "AI power"]]) {
    await wait(`!!document.querySelector('a[data-view="${view}"]')`, 20000, `the ${label} choice`);
    await evaluate(`document.querySelector('a[data-view="${view}"]')?.click()`);
    await wait(`location.search.includes('view=${view}') && document.querySelector('a[data-view="${view}"]').getAttribute('aria-current') === 'true'`, 20000, `${label} in the address`);
    s = await evaluate(STATE);
    ok(s.rows === num(s.count) && s.rows < all.rows && s.sentence !== all.sentence, `${label}: one click changes the answer`, `${s.count} deals: ${s.sentence.slice(0, 90)}`);
    ok(s.barSum === s.rows, `${label}: the chart follows`, `${s.barSum}`);
  }
  // the form: a deal type and a year on top of the AI view
  await evaluate(`(() => { const f = document.querySelector('form[action="/deals/v2"]'); f.querySelector('select[name="type"]').value = 'ppa'; f.querySelector('select[name="year"]').value = '2026'; f.requestSubmit(); })()`);
  await wait(`location.search.includes('type=ppa') && location.search.includes('year=2026') && !!document.querySelector('[data-deals-summary]')`, 20000, "the form's address");
  s = await evaluate(STATE);
  ok(/view=ai/.test(s.href) && s.rows === num(s.count) && /AI power, power purchase, 2026/.test(s.sentence), "the form keeps the view and adds its choices", `${s.href}: ${s.count} deals`);
  // a counterparty
  await go(`${base}/deals/v2?party=Constellation`);
  s = await evaluate(STATE);
  ok(s.rows === num(s.count) && s.rows > 0 && s.rows === await evaluate(`[...document.querySelectorAll('tr[data-deal]')].filter((r) => /constellation/i.test(r.children[2].textContent)).length`), "a counterparty shows only its deals", `${s.rows}`);
  // tolling: empty, and said why
  await go(`${base}/deals/v2?type=tolling`);
  s = await evaluate(STATE);
  ok(s.rows === 0 && /No deal held matches/.test(s.sentence) && /no tolling type/.test(await evaluate(`document.body.textContent`)), "tolling is empty and the page says why");
  ok(errors.length === 0, "no error in the page", errors.slice(0, 2).join(" | "));
  return failed ? 1 : 0;
}, { width, height });

if (code === null) { console.log("no Chrome or Edge on this machine: not proven here"); process.exit(2); }
console.log(`${passed} of ${passed + failed} checks passed at ${width} wide, ${base}`);
process.exit(code);
