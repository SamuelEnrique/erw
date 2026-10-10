// Energy Research Warehouse (ERW) site, session 177: the Content-Security-Policy, in a real browser.
//
//   npm run build && npm start                         (the site on http://localhost:3000)
//   node scripts/check-csp.mjs [base-url] [--phone]
//
// next.config.ts sends two policies. The ENFORCED one holds only directives that cannot break a page. The full one is
// sent as Content-Security-Policy-Report-Only: it blocks nothing, and the browser reports what it would have blocked.
// This opens every page of the release list (lib/release.ts) in the internal view, in the machine's own Chrome or
// Edge, waits for the page to draw, and collects every `securitypolicyviolation` event the browser raises:
//   an ENFORCED violation   something on a page was blocked: the check fails (exit 1)
//   a report-only violation the full policy would block something the page uses: listed, with the page, the
//                           directive and the origin; the check fails with --strict, and otherwise says so and passes
// It also proves, in the browser, what a script cannot: the internal view opens by the form at /internal/open (a
// browser decides a posted form's Origin header by the page's referrer policy); the sign-up form posted by the browser
// is taken as this site's own (nothing is stored, no email is sent); the chart library, pinned by its hash, still
// loads and draws. With --recorded, a page view must add to the counts on /internal/usage. With --phone it opens the
// new pages (/privacy, /internal/open, /internal/usage, /terms) at 390 px and fails if any is wider than the screen.
// What it does not prove: what a page does only after a click (a download, the 3D map's controls, a share card).
// That is why the full policy is report-only. No browser on the machine: it says so and exits 0 (1 on the runner).
import { env, withBrowser } from "./browser.mjs";

const args = process.argv.slice(2);
const strict = args.includes("--strict"), phone = args.includes("--phone");
const base = (args.find((a) => !a.startsWith("--")) ?? "http://localhost:3000").replace(/\/$/, "");
const { RELEASE } = await import("../lib/release.ts");
const NEW = ["/privacy", "/terms", "/internal/open", "/internal/usage"];
const PAGES = phone ? NEW : [...new Set([...Object.keys(RELEASE), "/internal/open", "/internal/usage", "/internal/costs", "/internal/ask", "/in-review"])];
const HOOK = "window.__csp = []; document.addEventListener('securitypolicyviolation', (e) => window.__csp.push({ directive: e.effectiveDirective || e.violatedDirective, blocked: e.blockedURI, disposition: e.disposition, source: (e.sourceFile || '') + ':' + (e.lineNumber || 0) }));";

const code = await withBrowser(async ({ go, evaluate, unlock, send, sleep }) => {
  await send("Page.addScriptToEvaluateOnNewDocument", { source: HOOK });
  if (phone) await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  // The internal view is opened as a person opens it since session 177: by the form at /internal/open, in this real
  // browser (a browser, unlike a script, decides the Origin header of a posted form by the page's referrer policy:
  // under no-referrer it writes "null", and the route would answer 404). The token is typed into the field and the
  // form is submitted; it must land on the home page holding the view's cookie. The token is never printed.
  let enforced = 0, reported = 0, wide = 0, failed = 0;
  const token = env("INTERNAL_COSTS_TOKEN");
  if (!token) throw new Error("INTERNAL_COSTS_TOKEN is not set: the pages in review cannot be opened");
  await go(base + "/internal/open");
  await evaluate(`(() => { const i = document.querySelector('form[action="/internal/unlock"] input[name="token"]'); i.value = ${JSON.stringify(token)}; i.form.requestSubmit(); })()`);
  let landed = { path: "", view: false };
  for (let i = 0; i < 40; i += 1) {
    await sleep(250);
    landed = await evaluate("({ path: location.pathname, view: document.cookie.split(';').some((c) => c.trim() === 'erw_view=internal') })").catch(() => landed);
    if (landed.path === "/" && landed.view) break;
  }
  const opened = landed.path === "/" && landed.view;
  console.log(`${opened ? "ok  " : "FAIL"} the form at /internal/open opens the internal view in a real browser (landed on ${landed.path || "nothing"}, the view's cookie ${landed.view ? "set" : "not set"})`);
  if (!opened) { failed += 1; await unlock(base); }      // the rest of the check still runs, by the old link
  const kinds = new Map();
  for (const p of PAGES) {
    try {
      await go(base + p);
    } catch (e) {
      failed += 1;
      console.log(`FAIL ${p}: ${e.message}`);
      continue;
    }
    await sleep(phone ? 600 : 1800);       // the charts, the map and the page's own requests
    const seen = await evaluate("JSON.stringify(window.__csp || [])").then(JSON.parse).catch(() => []);
    const here = seen.filter((v) => v.disposition === "enforce").length;
    enforced += here;
    reported += seen.length - here;
    for (const v of seen) {
      let origin = v.blocked;
      try { origin = new URL(v.blocked).origin; } catch { /* inline, eval, data, blob */ }
      const k = `${v.disposition} ${v.directive} ${origin}`;
      kinds.set(k, [...(kinds.get(k) ?? []), p]);
    }
    let note = "";
    if (phone) {
      const w = await evaluate("[document.documentElement.scrollWidth, window.innerWidth]");
      if (w[0] > w[1] + 1) { wide += 1; note = `  WIDER THAN THE SCREEN: ${w[0]} of ${w[1]} px`; }
      else note = `  ${w[0]} of ${w[1]} px`;
    }
    console.log(`${here ? "FAIL" : "ok  "} ${p}: ${seen.length} violation(s)${here ? `, ${here} ENFORCED` : ""}${note}`);
  }
  let charts = true;
  if (!phone) {
    // the detector is proven first: a script the full policy does not allow (a data: address; no request leaves) must
    // be reported, and must still run, since the full policy is report-only
    await go(base + "/terms");
    const probe = await evaluate(`(async () => {
      const before = window.__csp.length;
      const s = document.createElement("script");
      s.src = "data:text/javascript,window.__probe=1";
      document.head.appendChild(s);
      await new Promise((r) => setTimeout(r, 700));
      return { seen: window.__csp.slice(before), ran: window.__probe === 1 };
    })()`);
    const caught = probe.seen.some((v) => v.disposition === "report" && /script-src/.test(v.directive));
    console.log(`${caught && probe.ran ? "ok  " : "FAIL"} the detector: a script from a data: address is reported by the full policy${probe.ran ? " and still runs (report-only)" : " and DID NOT RUN (the policy is enforced?)"}`);
    if (!caught || !probe.ran) failed += 1;
    await go(base + "/storage");
    await sleep(3000);
    charts = await evaluate("typeof window.echarts === 'object' && document.querySelectorAll('canvas').length > 0");
    console.log(`${charts ? "ok  " : "FAIL"} /storage: the chart library loaded and drew`);
    // The sign-up form, posted by this real browser with neither email chosen: the route must take it as this site's
    // own form and answer "choose one" (state none). Another site's form is answered "invalid". Nothing is stored and
    // no email is sent: the route stops before either.
    await go(base + "/subscribe");
    await evaluate(`(() => { const f = document.querySelector('form[action="/api/subscribe"]'); f.querySelector('input[name="email"]').value = "nobody@example.com";
      for (const n of ["daily", "weekly"]) f.querySelector('input[name="' + n + '"]').checked = false; f.submit(); })()`);
    let state = "";
    for (let i = 0; i < 40 && !state; i += 1) {
      await sleep(250);
      state = await evaluate("location.pathname === '/subscribe' ? (new URLSearchParams(location.search).get('state') || '') : ''").catch(() => "");
    }
    console.log(`${state === "none" ? "ok  " : "FAIL"} the sign-up form, posted by the browser, is taken as this site's own (state "${state || "nothing"}"; nothing stored, no email)`);
    if (state !== "none") failed += 1;
    // --recorded (after migration 028, on a server that holds ASK_VISITOR_SALT): a page view in this browser must add
    // to the counts on /internal/usage. It writes real counts: the pages this check opened.
    if (args.includes("--recorded")) {
      const events = async () => {
        await go(base + "/internal/usage");
        return evaluate("Number((document.querySelector('[data-n=events]')?.textContent || 'NaN').replace(/,/g, ''))");
      };
      const before = await events();
      await go(base + "/storage");
      await sleep(2500);
      const after = await events();
      const counted = Number.isFinite(before) && Number.isFinite(after) && after > before;
      console.log(`${counted ? "ok  " : "FAIL"} --recorded: opening /storage in this browser added to the counts on /internal/usage (${before} to ${after} events)`);
      if (!counted) failed += 1;
    }
  }
  for (const [k, pages] of [...kinds.entries()].sort()) console.log(`  ${k}: ${pages.length} page(s), first ${pages[0]}`);
  console.log(`${PAGES.length} pages${phone ? " at 390 px" : ""}: ${enforced} enforced violation(s), ${reported} report-only violation(s), ${failed} page(s) not loaded${phone ? `, ${wide} wider than the screen` : ""}`);
  if (reported && !strict) console.log("the full policy is report-only: it blocked nothing; the lines above are what it would block");
  return enforced || failed || wide || !charts || (strict && reported) ? 1 : 0;
}, phone ? { width: 390, height: 844 } : {});
if (code === null) {
  console.log("no Chrome or Edge on this machine: the policy was not proven here");
  process.exit(0);
}
process.exit(code);
