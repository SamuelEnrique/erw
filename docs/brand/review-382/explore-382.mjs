// Energy Research Warehouse (ERW), session 382: a first look at the three pages of the trader path, in the internal
// view, before the walk is written. Prints each page's headings, buttons, form controls and checked keys.
//
//   node docs/brand/review-382/explore-382.mjs http://localhost:3382 > runs/.../explore.json
import { withBrowser } from "../../../site/scripts/browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3382").replace(/\/$/, "");
const pages = (process.argv[3] ?? "/cost-of-power/seller,/cost-of-power/battery,/board").split(",");
const LOOK = `(() => ({
  url: location.pathname + location.search,
  title: document.title,
  unreadable: document.body.innerText.includes("could not be read"),
  inReview: !!document.querySelector("[data-in-review]"),
  heads: [...document.querySelectorAll("h1,h2,h3")].map((e) => e.tagName + " " + e.textContent.replace(/\\s+/g, " ").trim()).slice(0, 60),
  buttons: [...document.querySelectorAll("button")].map((e) => e.textContent.replace(/\\s+/g, " ").trim()).filter(Boolean).slice(0, 60),
  inputs: [...document.querySelectorAll("input,select")].map((e) => (e.name || e.id || "") + ":" + e.type + "=" + e.value).slice(0, 80),
  checks: [...document.querySelectorAll("[data-check]")].map((e) => e.getAttribute("data-check") + " = " + e.textContent.trim()).slice(0, 80),
  ncheck: document.querySelectorAll("[data-check]").length,
  ns: [...document.querySelectorAll("[data-n]")].map((e) => e.getAttribute("data-n") + " = " + e.textContent.trim()).slice(0, 40),
  nn: document.querySelectorAll("[data-n]").length,
  links: [...new Set([...document.querySelectorAll("a[href]")].map((a) => a.getAttribute("href")))].slice(0, 120),
  text: document.body.innerText.slice(0, 2500),
}))()`;

const out = await withBrowser(async ({ go, evaluate, unlock, sleep }) => {
  await unlock(base);
  const res = [];
  for (const p of pages) {
    await go(base + p);
    await sleep(2500);
    res.push(await evaluate(LOOK));
  }
  return res;
});
console.log(JSON.stringify(out, null, 1));
