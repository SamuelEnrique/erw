// Energy Research Warehouse (ERW) site, session 190: the face of /cost-of-power ("What a datacenter pays") in the
// internal view, in a headless browser, at desktop width (1280) and phone width (390).
//
//   npm run build && npx next start -p 3190
//   node scripts/check-datacenter-face.mjs [base-url] [screenshot-dir]
//
// The page is in review, so this unlocks the internal view first (INTERNAL_COSTS_TOKEN from the environment,
// site/.env.local or the root .env; the token is never printed) and asserts:
//   1. the default page opens with its summary and its three headline numbers, and each equals the arithmetic of
//      lib/datacenter.ts over the page's own files (the same figures the replication CSV rebuilds);
//   2. session 190's additions: the lead links the step-by-step note beside the Method note; the source line offers
//      three downloads; each of the four addresses answers 200; the CSV as served is the committed file, byte for byte;
//   3. the first tab reads "What a datacenter pays" on all three pages of the cost of power (until session 190 the
//      battery page kept "What power costs to buy");
//   4. at 390 px the page does not scroll sideways, for a flat load, a flexible load and New York, and the new links
//      are on the page;
//   5. as a visitor the page is the in-review page and shows none of the above.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env, withBrowser } from "./browser.mjs";
import { badMonth, gpuHour, gpus, inputsOf, last36, lastTwelve, monthsOf, span, two, usdShort, whole } from "../lib/datacenter.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3190").replace(/\/$/, "");
const shots = process.argv[3];
let bad = 0, n = 0;
const check = (ok, what, detail = "") => { n += 1; if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`); };
const NOTE = "/data/methods/datacenter_pays_algorithm";
const FILES = ["/datacenter/erw_2026_datacenter_hourly.csv", "/datacenter/erw_2026_datacenter_replication.do", "/datacenter/erw_2026_datacenter_replication.py"];

// the default page's figures from the library and the page's files
const dir = path.join(here, "..", "data", "datacenter");
const index = JSON.parse(fs.readFileSync(path.join(dir, "index.json"), "utf-8"));
const x = inputsOf({}, index);
const files = index.grids[x.grid].years.map((y) => JSON.parse(fs.readFileSync(path.join(dir, `${x.grid}_${y}.json`), "utf-8")));
const ms = monthsOf(files, x.region, x.buy, x), l12 = lastTwelve(ms), s12 = l12 ? span(l12) : null, w36 = last36(ms), worst = badMonth(w36?.months ?? []);
const want = s12 ? { per: two(s12.per), cost: usdShort(s12.cost * x.mw), mwh: whole(s12.energy * x.mw), gpu: gpuHour(s12.per, x.gpu, x.pue).toFixed(4), gpus: whole(gpus(x.mw, x.gpu, x.pue)),
  bad: worst ? two(worst.cost / worst.energy) : null } : null;

const STATE = `(() => {
  const t = (sel) => document.querySelector(sel)?.textContent ?? null;
  const main = document.querySelector("main") ?? document.body;
  return {
    inReview: !!document.querySelector("[data-in-review]"), title: t("h1"), summary: t("[data-summary]") ?? "",
    per: t('[data-stat="l12_per"]'), cost: t('[data-stat="l12_cost"]'), gpu: t('[data-stat="gpu_hour"]'),
    text: main.innerText, bad: /undefined|NaN/.test(main.innerText),
    tabs: [...document.querySelectorAll('nav[aria-label="Cost of power"] a')].map((a) => a.textContent),
    links: [...document.querySelectorAll("a")].map((a) => ({ href: a.getAttribute("href"), text: a.textContent, download: a.hasAttribute("download"),
      shown: a.getBoundingClientRect().width > 0, right: a.getBoundingClientRect().right })),
    lead: document.querySelector("h1")?.parentElement?.innerText ?? "",
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
  };
})()`;

const code = await withBrowser(async ({ go, evaluate, unlock, send, sleep }) => {
  const size = async (width) => send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
  const open = async (route, width = 1280) => { await size(width); await go(base + route); await sleep(1200); return evaluate(STATE); };
  const shot = async (name, width) => {
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    const { cssContentSize } = await send("Page.getLayoutMetrics");
    const height = Math.min(Math.ceil(cssContentSize.height), 12000);
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await sleep(400);
    const s = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height, scale: 1 } });
    fs.writeFileSync(path.join(shots, `${name}.png`), Buffer.from(s.data, "base64"));
  };

  // 5. a visitor first, before the internal view is unlocked
  const v = await open("/cost-of-power");
  check(v.inReview && v.per === null && !v.links.some((a) => a.download) && !v.links.some((a) => a.href === NOTE), "as a visitor the page is the in-review page: no figure, no download, no link to the note");

  await unlock(base);
  const d = await open("/cost-of-power");
  check(!d.inReview && d.title === "What a datacenter pays" && !d.bad && d.summary.includes("A flat 100 MW load at LZ_NORTH in ERCOT, buying real time"), "the default page opens in the internal view with its summary", d.summary.slice(0, 110));
  check(want !== null && d.per === want.per && d.cost === want.cost && d.gpu === want.gpu, "the summary's three figures are the library's over the page's files", `USD ${d.per} per MWh, USD ${d.cost}, USD ${d.gpu} per GPU-hour`);
  check(want !== null && d.text.includes(`USD ${want.cost} for ${want.mwh} MWh`) && d.text.includes(`powers ${want.gpus} GPUs`) && (want.bad === null || d.text.includes(`USD ${want.bad}`)), "the three headline numbers' notes carry the library's energy, GPU count and bad month",
    `${want?.mwh} MWh, ${want?.gpus} GPUs, bad month USD ${want?.bad}`);
  const note = d.links.find((a) => a.text === "Every number, step by step");
  check(!!note && note.href === NOTE && /Method note\.\s+Every number, step by step\./.test(d.lead), "the lead links the step-by-step note beside the Method note");
  // session 236: the source line's three files; the page's own CSV downloads (sessions 213 and 236) are other links
  const got = d.links.filter((a) => a.download && FILES.includes(a.href));
  check(got.length === 3 && got.map((a) => a.href).join() === FILES.join() && got.map((a) => a.text).join() === "CSV,Stata do-file,Python mirror", "the source line offers three downloads: CSV, Stata do-file, Python mirror", got.map((a) => a.href).join(", "));
  check(/The default case hour by hour: CSV, Stata do-file, Python mirror\./.test(d.text), 'the source line reads "The default case hour by hour: CSV, Stata do-file, Python mirror."');
  const cookie = await evaluate("document.cookie");
  for (const h of [...FILES, NOTE]) {
    const res = await fetch(base + h, { headers: { Cookie: cookie } }).catch(() => null);
    const body = res ? Buffer.from(await res.arrayBuffer()) : null;
    check(!!res && res.status === 200, `${h} answers 200`, res ? `${res.status}, ${body.length.toLocaleString("en-US")} bytes` : "no answer");
    if (h.startsWith("/datacenter/") && body) check(body.equals(fs.readFileSync(path.join(here, "..", "public", h.slice(1)))), `${h} as served is the committed file, byte for byte`);
  }
  await shot("datacenter-default-desktop", 1280);

  // 3. the three tabs read alike on the three pages
  for (const route of ["/cost-of-power", "/cost-of-power/seller", "/cost-of-power/battery"]) {
    const t = await open(route);
    check(t.tabs.join("|") === "What a datacenter pays|What a generator earns|What a battery earns", `${route}: the three tabs read alike`, t.tabs.join(" | "));
  }

  // 4. phone width
  for (const [q, name] of [["", "datacenter-default-phone"], ["?grid=ercot&region=LZ_NORTH&mw=100&run=hours&n=100&buy=rt", "datacenter-off100-phone"], ["?grid=nyiso", "datacenter-nyiso-phone"]]) {
    const s = await open(`/cost-of-power${q}`, 390);
    const mine = s.links.filter((a) => a.download || a.href === NOTE);
    check(s.clientW === 390 && s.scrollW <= s.clientW + 1 && !s.bad, `/cost-of-power${q} at 390 px: the page does not scroll sideways`, `scroll width ${s.scrollW}, width ${s.clientW}`);
    check(mine.length >= 4 && FILES.every((f) => mine.some((a) => a.href === f)) && mine.every((a) => a.shown && a.right <= 390 + 1), `/cost-of-power${q} at 390 px: the note's link and the three downloads are on the page, inside its width`, mine.map((a) => `${a.text} ${Math.round(a.right)}`).join(", "));
    await shot(name, 390);
  }
  return 0;
}, { width: 1280, height: 900 }).catch((e) => { bad += 1; console.log(`FAIL the browser run stopped: ${e.message}`); return 1; });

if (code === null) { console.log("check-datacenter-face: no Chrome or Edge on this machine; nothing was checked"); process.exit(env("GITHUB_ACTIONS") === "true" ? 1 : 0); }
console.log(bad ? `check-datacenter-face FAILED: ${bad} of ${n}` : `check-datacenter-face: all ${n} passed`);
process.exit(bad ? 1 : 0);
