// Energy Research Warehouse (ERW) site: the browser test of /cost-of-power/battery and of the release gate (session 67).
//
//   npm run build && npm start
//   node scripts/test-battery-stack.mjs [base-url] [screenshot-dir]
//
// Drives a headless Chrome or Edge over the DevTools protocol (as scripts/screenshots.mjs does), in a fresh profile, so
// the browser is a visitor with no internal cookie. Asserts:
//   1. the duration toggle (2, 4, 8 hours) changes the summary sentence, each headline number, the chart and the
//      income table, and the address;
//   2. typing the contract terms makes no network request, leaves the address unchanged, writes nothing to storage or
//      cookies, and shows the contract result;
//   3. the contract terms survive a change of duration, and no request made by that change carries them;
//   4. the gate, as a visitor: the six live pages open as themselves, a page in review shows the in-review page, and
//      the menu lists every item with the ones in review greyed, labeled, not links and not reachable by keyboard.
// Prints one line per assertion; exits 1 if any fails.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const shots = process.argv[3];
const PORT = 9347;
const { PAGES } = await import("../lib/pages.ts");
const { statusOf } = await import("../lib/release.ts");

function chromePath() {
  const c = [process.env.CHROME_PATH, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"].filter(Boolean);
  const p = c.find((x) => fs.existsSync(x));
  if (!p) throw new Error("no Chrome or Edge found; set CHROME_PATH");
  return p;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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
    close: () => ws.close(),
  };
}

let failed = 0;
function check(ok, what, detail = "") {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`);
}

const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-battery-test-"));
const chrome = spawn(chromePath(), ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--hide-scrollbars", "--disable-gpu", "about:blank"]);
try {
  let version;
  for (let i = 0; i < 50 && !version; i++) { await sleep(200); version = await fetch(`http://127.0.0.1:${PORT}/json/version`).then((r) => r.json()).catch(() => undefined); }
  if (!version) throw new Error("headless browser did not start");
  const target = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" }).then((r) => r.json());
  const page = await cdp(target.webSocketDebuggerUrl);
  await page.send("Page.enable");
  await page.send("Network.enable");
  const requests = [];
  page.on((m) => { if (m.method === "Network.requestWillBeSent") requests.push({ url: m.params.request.url, body: m.params.request.postData ?? "", headers: JSON.stringify(m.params.request.headers ?? {}) }); });
  const ev = async (expression) => {
    const r = await page.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(`${r.exceptionDetails.text}: ${expression.slice(0, 80)}`);
    return r.result.value;
  };
  const go = async (route, width = 1280) => {
    await page.send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
    const loaded = new Promise((res) => page.on((m) => m.method === "Page.loadEventFired" && res()));
    const nav = await page.send("Page.navigate", { url: base + route });
    if (nav.errorText) throw new Error(`${route}: ${nav.errorText}`);
    await Promise.race([loaded, sleep(30000)]);
    await sleep(1500);
  };
  const shot = async (name, width) => {
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    const { cssContentSize } = await page.send("Page.getLayoutMetrics");
    const height = Math.min(Math.ceil(cssContentSize.height), 6000);
    await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await sleep(500);
    const s = await page.send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height, scale: 1 } });
    fs.writeFileSync(path.join(shots, `${name}.png`), Buffer.from(s.data, "base64"));
  };
  const STATE = `(() => ({
    url: location.pathname + location.search,
    summary: document.querySelector("[data-summary]")?.textContent ?? "",
    headline: [...document.querySelectorAll("[data-summary] ~ div .font-serif.text-3xl")].map((e) => e.textContent),
    chart: document.querySelector("figure svg")?.outerHTML ?? "",
    table: document.querySelector("table")?.textContent ?? "",
    contract: document.querySelector("[data-contract-result]")?.getAttribute("data-contract-result") ?? "",
    contractText: document.querySelector("[data-contract-result]")?.textContent ?? "",
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
  }))()`;
  const clickDuration = async (d, before) => {
    await ev(`document.querySelector('a[data-duration="${d}"]').click()`);
    for (let i = 0; i < 60; i++) { await sleep(250); const s = await ev(STATE); if (s.summary && s.summary !== before.summary) return s; }
    return ev(STATE);
  };

  // 1. the duration toggle, on both grids and both strategies
  for (const q of ["grid=ercot&dur=4&strat=foresight", "grid=caiso&dur=4&strat=dayahead"]) {
    await go(`/cost-of-power/battery?${q}`);
    const s4 = await ev(STATE);
    check(s4.summary.includes("4-hour battery") && s4.headline.length === 3 && s4.chart.length > 500, `${q}: the page shows a summary, three headline numbers and a chart`, s4.summary.replace(/\s+/g, " ").trim());
    if (q.startsWith("grid=ercot")) await shot("battery-ercot-4h-desktop", 1280);
    let prev = s4;
    for (const d of [2, 8]) {
      const s = await clickDuration(d, prev);
      const what = `${q.split("&")[0]}, ${q.split("&")[2]}: ${prev.url.match(/dur=(\d)/)[1]} to ${d} hours changes`;
      check(s.url.includes(`dur=${d}`), `${what} the address`, s.url);
      check(s.summary !== prev.summary && s.summary.includes(`${d}-hour battery`), `${what} the summary sentence`, s.summary.replace(/\s+/g, " ").trim());
      check(s.headline.length === 3 && s.headline.every((h, i) => h !== prev.headline[i]), `${what} each headline number`, s.headline.join(" | "));
      check(s.chart !== prev.chart, `${what} the chart`);
      check(s.table !== prev.table, `${what} the income table`);
      prev = s;
    }
  }

  // 2. the contract: no request, no address change, nothing stored
  await go("/cost-of-power/battery?grid=ercot&dur=4&strat=foresight");
  const before = await ev(STATE);
  const stored = `JSON.stringify([localStorage.length, sessionStorage.length, document.cookie])`;
  const storedBefore = await ev(stored);
  await sleep(1500);
  requests.length = 0;
  const type = (k, v) => ev(`(() => { const i = document.querySelector('input[data-contract="${k}"]'); const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set; set.call(i, ${JSON.stringify(v)}); i.dispatchEvent(new Event("input", { bubbles: true })); i.dispatchEvent(new Event("change", { bubbles: true })); i.blur(); return i.value; })()`);
  await type("share", "61.7");
  await type("price", "7.3131");
  await type("end", "2031-06");
  await sleep(2500);
  const after = await ev(STATE);
  check(requests.length === 0, "entering the contract terms makes no network request", requests.map((r) => r.url).join(", "));
  check(after.url === before.url, "entering the contract terms leaves the address unchanged", after.url);
  check((await ev(stored)) === storedBefore, "entering the contract terms writes nothing to storage or cookies");
  check(after.contract === "shown" && /Debt coverage with the contract/.test(after.contractText) && /June 2031/.test(after.contractText), "the contract result is shown, computed in the browser", after.contractText.replace(/\s+/g, " ").slice(0, 160));
  check(await ev(`!document.querySelector("[data-contract-inputs] input[name]") && !document.querySelector("[data-contract-inputs]").closest("form")`), "the contract inputs have no field name and sit in no form");
  await shot("battery-ercot-4h-contract-desktop", 1280);

  // 3. the terms survive a change of duration, and no request of that change carries them
  await page.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  requests.length = 0;
  const moved = await clickDuration(8, after);
  const leak = requests.filter((r) => /7\.3131|61\.7|2031-06/.test(r.url + r.body + r.headers));
  check(moved.url.includes("dur=8") && moved.contract === "shown" && moved.contractText !== after.contractText, "the contract terms survive a change of duration and are recomputed");
  check(requests.length > 0 && leak.length === 0, `the ${requests.length} request(s) of that change carry no contract term`, leak.map((r) => r.url).join(", "));

  // the phone: the panel stacks on top, nothing wider than the screen
  await go("/cost-of-power/battery?grid=caiso&dur=2&strat=dayahead", 390);
  const phone = await ev(`(() => { const a = document.querySelector("aside").getBoundingClientRect(), s = document.querySelector("[data-summary]").getBoundingClientRect(); return { stacked: a.bottom <= s.top + 1, sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }; })()`);
  check(phone.stacked, "on a phone the input panel stacks on top of the answer");
  check(phone.sw <= phone.cw + 1, "on a phone the page is no wider than the screen", `${phone.sw} px in ${phone.cw} px`);
  await shot("battery-caiso-2h-mobile", 390);

  // 4. the gate, as a visitor
  for (const p of ["/", "/cost-of-power/battery", "/cost-of-power/seller", "/network", "/storage", "/about", "/terms"]) {
    await go(p);
    const r = await ev(`({ review: !!document.querySelector("[data-in-review]"), h1: document.querySelector("h1")?.textContent ?? "" })`);
    check(!r.review && r.h1.length > 0, `visitor: ${p} opens`, r.h1);
    if (p === "/storage") await shot("storage-desktop", 1280);
    if (p === "/") await shot("home-desktop", 1280);
  }
  await go("/board");
  const rev = await ev(`({ review: !!document.querySelector("[data-in-review]"), text: document.querySelector("main").textContent, robots: document.querySelector('meta[name="robots"]')?.content ?? "", path: location.pathname })`);
  check(rev.review && rev.text.includes("Price board") && rev.text.includes("This tool is in review and will open when it is approved") && /noindex/.test(rev.robots) && rev.path === "/board",
    "visitor: /board shows the in-review page, with the tool's name, at its own address, noindex", rev.text.replace(/\s+/g, " ").slice(0, 110));
  await shot("in-review-desktop", 1280);
  await go("/");
  const want = PAGES.filter((p) => statusOf(p.href) === "review");
  const menu = await ev(`(() => {
    const nav = document.querySelector('nav[aria-label="Site"]');
    nav.querySelectorAll("details").forEach((d) => d.setAttribute("open", ""));
    const greyed = [...nav.querySelectorAll(".gate-review")];
    return {
      text: nav.textContent,
      greyed: greyed.length,
      labeled: greyed.every((g) => g.querySelector(".gate-label")?.textContent === "in review"),
      focusable: greyed.filter((g) => g.matches("a, button, [tabindex]") || g.querySelector("a, button, [tabindex]")).length,
      links: [...nav.querySelectorAll("a[href]")].map((a) => a.getAttribute("href")),
      color: greyed.length ? getComputedStyle(greyed[0]).color : "",
      internal: /internal view/.test(nav.textContent),
    };
  })()`);
  check(PAGES.every((p) => menu.text.includes(p.label)), "visitor: the menu shows every item");
  check(menu.greyed >= want.length && menu.labeled, `visitor: the ${want.length} items in review are greyed and labeled "in review"`, `${menu.greyed} greyed, color ${menu.color}`);
  check(menu.focusable === 0 && !menu.links.some((h) => statusOf(h) === "review"), "visitor: no item in review is a link or reachable by keyboard", menu.links.join(" "));
  check(!menu.internal, "visitor: no internal view mark");
  await ev(`document.querySelector('nav[aria-label="Site"]').querySelectorAll("details").forEach((d, i) => i === 0 ? d.setAttribute("open", "") : d.removeAttribute("open"))`);
  await shot("menu-visitor-desktop", 1280);

  // 5. the internal view: unlock opens everything and marks the menu; lock closes it again. The token is read from the
  // environment or site/.env.local and is never printed.
  const token = (() => {
    if (process.env.INTERNAL_COSTS_TOKEN) return process.env.INTERNAL_COSTS_TOKEN;
    const f = path.join(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..", ".env.local");
    if (!fs.existsSync(f)) return "";
    const m = fs.readFileSync(f, "utf-8").match(/^INTERNAL_COSTS_TOKEN=(.*)$/m);
    return m ? m[1].trim().replace(/^"|"$/g, "") : "";
  })();
  if (!token) {
    console.log("skip the internal view: INTERNAL_COSTS_TOKEN is not set here");
  } else {
    await go(`/internal/unlock?token=${encodeURIComponent(token)}`);
    const inside = await ev(`(() => { const nav = document.querySelector('nav[aria-label="Site"]'); return { path: location.pathname + location.search, greyed: document.querySelectorAll(".gate-review").length, mark: /internal view/.test(nav.textContent), board: !!nav.querySelector('a[href="/board"]'), readable: document.cookie.includes("erw_internal") }; })()`);
    check(inside.path === "/" && inside.greyed === 0 && inside.mark && inside.board, "internal: unlock goes to the home page, nothing is greyed, the menu links every page and carries the internal view mark", JSON.stringify({ ...inside, path: inside.path }));
    check(!inside.readable, "internal: the cookie the gate checks is httpOnly (the page's script cannot read it)");
    await go("/board");
    check(!(await ev(`!!document.querySelector("[data-in-review]")`)), "internal: /board opens");
    await go("/internal/lock");
    const out = await ev(`({ greyed: document.querySelectorAll('nav[aria-label="Site"] .gate-review').length, mark: /internal view/.test(document.querySelector('nav[aria-label="Site"]').textContent) })`);
    check(out.greyed > 0 && !out.mark, "internal: lock closes it again", JSON.stringify(out));
    await go("/internal/unlock?token=not-the-token");
    check(await ev(`document.querySelectorAll('nav[aria-label="Site"] .gate-review').length > 0 || !document.querySelector("nav")`), "internal: a wrong token opens nothing");
  }
  page.close();
} finally {
  chrome.kill();
  await sleep(500);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* the profile is in the temp folder */ }
}
console.log(failed ? `battery and gate browser test: ${failed} assertion(s) FAILED` : "battery and gate browser test: all assertions pass");
process.exit(failed ? 1 : 0);
