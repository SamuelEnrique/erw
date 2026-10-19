// Energy Research Warehouse (ERW) site, session 92: a real browser for a check, with nothing to install.
//
//   import { withBrowser } from "./browser.mjs";
//   const code = await withBrowser(async ({ go, evaluate, wait, unlock }) => { ...; return 0; });
//
// Starts the machine's own Chrome or Edge headless with a fresh profile, speaks to it over the DevTools protocol
// (Node's own WebSocket; no package), runs the check and closes the browser. scripts/check-no-request.mjs (session 88)
// has the same code inline and is left as it is; new browser checks use this file.
//
//   go(url)                load a page and wait for its load event
//   evaluate(js)           run an expression in the page and return its value (a promise is awaited)
//   wait(js, ms, what)     poll an expression until it is truthy; throws with `what` after ms (default 15 s)
//   unlock(base)           open the internal view (INTERNAL_COSTS_TOKEN from the environment, site/.env.local or ../.env)
//                          Session 301 (the security review's H1): by the form at /internal/open, the token in the posted
//                          body, never in an address. unlockPost(base, token) is the same door for a script that
//                          fetches (the Cookie header is read from its answer), unlockForm(h, base, token) for a
//                          script that drives its own browser.
//   requests               every request the page made: { at, kind, url }
//
// No browser on the machine: withBrowser returns null (the caller says "not proven here"); on the workflow's runner
// (GITHUB_ACTIONS) it throws, so a green step there means the check was made.
import { execFileSync, spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export function env(name) {
  if (process.env[name]) return process.env[name];
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
      const m = line.match(/^([A-Z_]+)=(.*)$/);
      if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
    }
  }
  return undefined;
}

/** Session 301 (docs/reviews/2026-10-10-security.md, H1): the internal view opened as a script, by a POST of the token
 * to /internal/unlock in the request's body (the form's own door, session 177), never by the old link that put the
 * token in an address. Returns the answer (a 303 carrying the two cookies: read them with getSetCookie()); with no
 * token, a 404 made here, no request sent (the old link answered 404 too, and a wrong try would count). */
export async function unlockPost(base, token) {
  if (!token) return new Response("Not found", { status: 404 });
  const origin = new URL(base).origin;
  return fetch(`${origin}/internal/unlock`, {
    method: "POST", redirect: "manual",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Origin: origin, "User-Agent": "erw-check (node)" },
    body: new URLSearchParams({ token }).toString(),
  });
}

/** The same door from inside a browser a script drives: the form at /internal/open is filled and submitted, and the
 * script waits until the home page is shown with the view's cookie (as check-csp.mjs proves it). `h` is the script's
 * own { go, evaluate, sleep }; `base` may be "" when its go() takes a path. Throws when the view does not open. */
export async function unlockForm(h, base, token) {
  const pause = h.sleep ?? sleep;
  await h.go(`${base}/internal/open`);
  await h.evaluate(`(() => { const i = document.querySelector('form[action="/internal/unlock"] input[name="token"]'); i.value = ${JSON.stringify(token)}; i.form.requestSubmit(); })()`);
  for (let i = 0; i < 60; i += 1) {
    await pause(250);
    const landed = await h.evaluate("location.pathname === '/' && document.cookie.split(';').some((c) => c.trim() === 'erw_view=internal')").catch(() => false);
    if (landed) return;
  }
  throw new Error("the form at /internal/open did not open the internal view");
}

export function browserPath() {
  const named = process.env.BROWSER_PATH || process.env.CHROME_PATH;
  if (named && fs.existsSync(named)) return named;
  const pf = [process.env["PROGRAMFILES(X86)"], process.env.PROGRAMFILES, process.env.LOCALAPPDATA].filter(Boolean);
  const fixed = [
    ...pf.flatMap((p) => [path.join(p, "Google", "Chrome", "Application", "chrome.exe"), path.join(p, "Microsoft", "Edge", "Application", "msedge.exe")]),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  ];
  for (const f of fixed) if (fs.existsSync(f)) return f;
  if (process.platform !== "win32") {
    for (const n of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"]) {
      try { return execFileSync("which", [n], { encoding: "utf-8" }).trim(); } catch { /* not this one */ }
    }
  }
  return null;
}

export async function withBrowser(check, { width = 1280, height = 900 } = {}) {
  const exe = browserPath();
  if (!exe) {
    if (process.env.GITHUB_ACTIONS === "true") throw new Error("no Chrome or Edge was found on the runner (set BROWSER_PATH)");
    return null;
  }
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-browser-"));
  const args = ["--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, `--window-size=${width},${height}`, "--no-first-run", "--no-default-browser-check",
    "--disable-background-networking", "--disable-component-update", "--disable-sync", "--disable-extensions", "--enable-unsafe-swiftshader", "about:blank"];
  if (process.platform === "linux") args.unshift("--no-sandbox");
  const child = spawn(exe, args, { stdio: ["ignore", "ignore", "pipe"] });
  try {
    const port = await new Promise((resolve, reject) => {
      let buf = "";
      const t = setTimeout(() => reject(new Error(`the browser did not open its DevTools port: ${buf.slice(-300)}`)), 30000);
      child.stderr.on("data", (d) => {
        buf += d.toString();
        const m = buf.match(/DevTools listening on ws:\/\/[^:]+:(\d+)\//);
        if (m) { clearTimeout(t); resolve(Number(m[1])); }
      });
      child.on("exit", (c) => { clearTimeout(t); reject(new Error(`the browser exited (${c}): ${buf.slice(-300)}`)); });
    });
    const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" })).json();
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = () => reject(new Error("the DevTools socket did not open")); });
    let id = 0, loads = 0;
    const waiting = new Map();
    const requests = [], errors = [];
    ws.onmessage = (m) => {
      const d = JSON.parse(m.data);
      if (d.id && waiting.has(d.id)) { const { resolve, reject } = waiting.get(d.id); waiting.delete(d.id); d.error ? reject(new Error(d.error.message)) : resolve(d.result); return; }
      if (d.method === "Page.loadEventFired") loads += 1;
      if (d.method === "Network.requestWillBeSent") requests.push({ at: Date.now(), kind: d.params.type ?? "request", url: d.params.request.url });
      if (d.method === "Runtime.exceptionThrown") errors.push(d.params.exceptionDetails?.exception?.description ?? d.params.exceptionDetails?.text ?? "an exception");
    };
    const send = (method, params = {}) => new Promise((resolve, reject) => { id += 1; waiting.set(id, { resolve, reject }); ws.send(JSON.stringify({ id, method, params })); });
    const evaluate = async (expression) => {
      const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error(`in the page: ${r.exceptionDetails.exception?.description ?? r.exceptionDetails.text}`);
      return r.result.value;
    };
    const go = async (url) => {
      const before = loads;
      await send("Page.navigate", { url });
      for (let i = 0; i < 600 && loads === before; i += 1) await sleep(100);
      if (loads === before) throw new Error(`${url} did not finish loading in 60 s`);
    };
    const wait = async (expression, ms = 15000, what = expression) => {
      const t0 = Date.now();
      for (;;) {
        const v = await evaluate(expression);
        if (v) return v;
        if (Date.now() - t0 > ms) throw new Error(`waited ${ms / 1000} s for: ${what}`);
        await sleep(150);
      }
    };
    const unlock = async (base) => {
      const token = env("INTERNAL_COSTS_TOKEN");
      if (!token) throw new Error("INTERNAL_COSTS_TOKEN is not set: the pages in review cannot be opened");
      await unlockForm({ go, evaluate, sleep }, base, token);   // session 301: the form, never the token in an address
    };
    await send("Page.enable");
    await send("Network.enable");
    await send("Runtime.enable");
    return await check({ go, evaluate, wait, unlock, send, requests, errors, sleep });
  } finally {
    try { child.kill(); } catch { /* already gone */ }
    await sleep(500);
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch { /* the browser still holds a file: the temp directory is left */ }
  }
}
