// Energy Research Warehouse (ERW) site, session 183: the face of /cost-of-power/seller in the internal view, in a
// headless browser, at desktop width (1280) and phone width (390).
//
//   npm run build && npm start
//   node scripts/check-seller-face.mjs [base-url] [screenshot-dir]
//
// The page is in review, so this unlocks the internal view first (/internal/unlock with INTERNAL_COSTS_TOKEN from the
// environment, site/.env.local or the root .env; the token is never printed) and asserts:
//   1. the default page opens with its summary, its three headline numbers and its charts, priced at the main hub;
//   2. session 183's fix: at another hub (ERCOT's West hub, real time; ERCOT's AEN load zone, day-ahead; a New York
//      zone; a battery and a peaker at the West hub) revenue of the last twelve months and debt coverage differ from
//      the main hub's, the page names the hub and the market beside the figure, the check keys carry the hub, and the
//      battery beside the plant says it stays at the main hub;
//   3. the link to the step-by-step note beside the Method link, and the three downloads, each answering 200;
//   4. at 390 px the page does not scroll sideways, at the main hub and at another hub (session 162 left this unlooked).
// Prints one line per assertion; exits 1 if any fails.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const shots = process.argv[3];
const PORT = 9383;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function token() {
  if (process.env.INTERNAL_COSTS_TOKEN) return process.env.INTERNAL_COSTS_TOKEN;
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    const m = fs.readFileSync(f, "utf-8").match(/^INTERNAL_COSTS_TOKEN=(.*)$/m);
    if (m) return m[1].trim().replace(/^["']|["']$/g, "");
  }
  return "";
}
function chromePath() {
  const c = [process.env.CHROME_PATH, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"].filter(Boolean);
  const p = c.find((x) => fs.existsSync(x));
  if (!p) throw new Error("no Chrome or Edge found; set CHROME_PATH");
  return p;
}
async function cdp(wsUrl) {
  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0;
  const pending = new Map(), listeners = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const { res, rej } = pending.get(m.id); pending.delete(m.id); m.error ? rej(new Error(m.error.message)) : res(m.result); }
    else if (m.method) listeners.forEach((f) => f(m));
  };
  return {
    send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); }),
    on: (f) => listeners.push(f),
  };
}
let failed = 0;
function check(ok, what, detail = "") {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`);
}

const tok = token();
if (!tok) { console.log("check-seller-face FAILED: INTERNAL_COSTS_TOKEN is not set here, so the page in review cannot be opened"); process.exit(1); }
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-seller-face-"));
const chrome = spawn(chromePath(), ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--hide-scrollbars", "--disable-gpu", "about:blank"]);
try {
  let version;
  for (let i = 0; i < 50 && !version; i++) { await sleep(200); version = await fetch(`http://127.0.0.1:${PORT}/json/version`).then((r) => r.json()).catch(() => undefined); }
  if (!version) throw new Error("headless browser did not start");
  const target = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" }).then((r) => r.json());
  const page = await cdp(target.webSocketDebuggerUrl);
  await page.send("Page.enable");
  const ev = async (expression) => {
    const r = await page.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(`${r.exceptionDetails.text}: ${expression.slice(0, 80)}`);
    return r.result.value;
  };
  const go = async (route, width = 1280) => {
    await page.send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
    const loaded = new Promise((res) => page.on((m) => m.method === "Page.loadEventFired" && res()));
    const nav = await page.send("Page.navigate", { url: base + route });
    if (nav.errorText) throw new Error(`${route.split("?")[0]}: ${nav.errorText}`);
    await Promise.race([loaded, sleep(30000)]);
    await sleep(1500);
  };
  const shot = async (name, width) => {
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    const { cssContentSize } = await page.send("Page.getLayoutMetrics");
    const height = Math.min(Math.ceil(cssContentSize.height), 12000);
    await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await sleep(500);
    const s = await page.send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height, scale: 1 } });
    fs.writeFileSync(path.join(shots, `${name}.png`), Buffer.from(s.data, "base64"));
  };
  const STATE = `(() => {
    const t = (sel) => document.querySelector(sel)?.textContent ?? null;
    const wrap = document.querySelector("[data-priced-hub]");
    const cover = document.querySelector('[data-stat="cover"] [data-check]');
    return {
      inReview: !!document.querySelector("[data-in-review]"),
      summary: t("[data-summary]") ?? "", l12: t('[data-stat="l12_kw"]'), pricedAt: t('[data-stat="priced_at"]'),
      cover: cover ? Number(cover.getAttribute("data-raw")) : null, coverKey: cover?.getAttribute("data-check") ?? null,
      hub: wrap?.getAttribute("data-priced-hub") ?? null, market: wrap?.getAttribute("data-priced-market") ?? null,
      noModel: !!document.querySelector('[data-hub-model="none"]'), hybridAt: t("[data-hybrid-at]"),
      months: t("#months h2") ?? "", stress: document.querySelectorAll('[data-check*="stress_total"]').length,
      charts: document.querySelectorAll("[data-chart] canvas").length, tables: document.querySelectorAll("table").length,
      bad: /undefined|NaN/.test(document.querySelector("main")?.innerText ?? document.body.innerText),
      links: [...document.querySelectorAll("a")].map((a) => ({ href: a.getAttribute("href"), text: a.textContent, download: a.hasAttribute("download") })),
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    };
  })()`;
  const num = (s) => (s === null ? null : Number(String(s).replace(/,/g, "")));

  await go(`/internal/unlock?token=${encodeURIComponent(tok)}`);
  await go("/cost-of-power/seller");
  const d = await ev(STATE);
  check(!d.inReview && d.summary.includes("merchant solar plant in ERCOT priced at the hub average") && d.charts >= 4 && d.tables >= 4 && !d.bad, "the default page opens in the internal view with its summary, charts and tables", `${d.charts} charts, ${d.tables} tables`);
  check(d.hub === "HB_HUBAVG" && d.market === "rt" && d.pricedAt === "the hub average" && d.hybridAt === null && !d.noModel, "the default page is priced at the hub average, the page's snapshot", `USD ${d.l12} per kW, coverage ${d.cover}`);
  check(d.coverKey !== null && !d.coverKey.includes("&hub="), "the default page's check keys are the snapshot's own", d.coverKey ?? "");
  const note = d.links.find((a) => a.text === "Every number, step by step");
  check(note && note.href === "/data/methods/generator_earns_algorithm", "the lead links the step-by-step note beside the Method note");
  const files = d.links.filter((a) => a.download).map((a) => a.href);
  check(files.length === 3 && files.every((h) => h.startsWith("/seller/erw_2026_generator_")), "the source line offers three downloads", files.join(", "));
  for (const h of [...files, "/data/methods/generator_earns_algorithm"]) {
    const res = await fetch(base + h, { headers: { Cookie: await ev("document.cookie") } }).catch(() => null);
    check(res && res.status === 200, `${h} answers 200`, res ? `${res.status}, ${(await res.arrayBuffer()).byteLength.toLocaleString("en-US")} bytes` : "no answer");
  }
  await shot("seller-ercot-solar-desktop", 1280);

  // another hub: revenue and debt coverage move with it, and the page says where it is priced
  const at = async (q) => { await go(`/cost-of-power/seller?${q}`); return ev(STATE); };
  const w = await at("iso=ercot&asset=solar&hub=HB_WEST");
  check(!w.inReview && !w.bad && w.hub === "HB_WEST" && w.market === "rt" && w.pricedAt === "the West hub (real-time prices)" && !w.noModel, "ERCOT solar at the West hub: priced at the West hub, real time", w.pricedAt ?? "");
  check(num(w.l12) !== null && num(w.l12) !== num(d.l12) && w.cover !== null && w.cover !== d.cover, "ERCOT solar at the West hub: revenue of the last twelve months and debt coverage differ from the hub average's", `USD ${w.l12} per kW against ${d.l12}; coverage ${w.cover?.toFixed(2)} against ${d.cover?.toFixed(2)}`);
  check(w.summary.includes("priced at the West hub (real-time prices)") && w.months.includes("HB_WEST") && w.months.includes("real-time prices"), "ERCOT solar at the West hub: the sentence and the months' title name the hub and the market");
  check(w.coverKey !== null && w.coverKey.includes("&hub=HB_WEST&market=rt|"), "ERCOT solar at the West hub: the check keys carry the hub and the market", w.coverKey ?? "");
  check(w.hybridAt !== null && w.hybridAt.includes("the hub average") && w.stress === 3, "ERCOT solar at the West hub: the battery beside it says it stays at the hub average; the three stress events are the hub's");
  await shot("seller-ercot-solar-west-desktop", 1280);
  const z = await at("iso=ercot&asset=wind&hub=LZ_AEN");
  check(!z.bad && z.hub === "LZ_AEN" && z.market === "da" && z.pricedAt === "the AEN load zone (day-ahead prices)" && num(z.l12) > 0, "ERCOT wind at the AEN load zone: priced at day-ahead prices, and said so", `USD ${z.l12} per kW`);
  const dw = await at("iso=ercot&asset=wind");
  check(num(z.l12) !== num(dw.l12) && z.cover !== dw.cover, "ERCOT wind at the AEN load zone: revenue and debt coverage differ from the hub average's", `USD ${z.l12} against ${dw.l12}; coverage ${z.cover?.toFixed(2)} against ${dw.cover?.toFixed(2)}`);
  for (const asset of ["battery", "peaker"]) {
    const a = await at(`iso=ercot&asset=${asset}&hub=HB_WEST`), m = await at(`iso=ercot&asset=${asset}`);
    check(!a.bad && a.hub === "HB_WEST" && num(a.l12) !== null && num(a.l12) !== num(m.l12) && a.cover !== m.cover, `ERCOT ${asset} at the West hub: revenue and debt coverage differ from the hub average's`, `USD ${a.l12} per kW against ${m.l12}; coverage ${a.cover?.toFixed(2)} against ${m.cover?.toFixed(2)}`);
  }
  const pk = await at("iso=ercot&asset=peaker&hub=HB_WEST&hr=9&vom=3"), pk0 = await at("iso=ercot&asset=peaker&hub=HB_WEST");
  check(!pk.bad && num(pk.l12) > num(pk0.l12), "ERCOT peaker at the West hub with a lower heat rate earns more: computed from the hub's own hours", `USD ${pk.l12} per kW against ${pk0.l12}`);
  const ny = await at("iso=nyiso&asset=wind&hub=WEST"), ny0 = await at("iso=nyiso&asset=wind");
  check(!ny.bad && ny.hub === "WEST" && num(ny.l12) !== null && num(ny.l12) !== num(ny0.l12) && ny.hybridAt === null, "NYISO wind at the West zone: revenue differs from New York City's", `USD ${ny.l12} per kW against ${ny0.l12}`);
  const ne = await at("iso=isone&asset=solar&hub=.Z.MAINE");
  check(!ne.bad && ne.hub === ".Z.MAINE" && ne.l12 === null, "ISO-NE solar at the Maine zone: the model is the zone's, and it holds no twelve months (nothing is filled)", ne.summary.slice(0, 90));

  for (const [q, name] of [["iso=ercot&asset=solar", "seller-ercot-solar-phone"], ["iso=ercot&asset=solar&hub=HB_WEST", "seller-ercot-solar-west-phone"], ["iso=caiso&asset=wind&hub=TH_NP15_GEN-APND", "seller-caiso-wind-np15-phone"]]) {
    await go(`/cost-of-power/seller?${q}`, 390);
    const s = await ev(STATE);
    check(s.clientW === 390 && s.scrollW <= s.clientW + 1 && !s.bad, `${q} at 390 px: the page does not scroll sideways`, `scroll width ${s.scrollW}, width ${s.clientW}`);
    await shot(name, 390);
  }
} catch (e) {
  failed++;
  console.log(`FAIL the browser run stopped: ${e.message}`);
} finally {
  chrome.kill();
  await sleep(300);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* the profile folder is temporary */ }
}
console.log(failed ? `check-seller-face FAILED: ${failed}` : "check-seller-face: all passed");
process.exit(failed ? 1 : 0);
