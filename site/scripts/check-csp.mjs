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
// It also proves the chart library still loads on a page that draws a chart, and with --phone it opens the new pages
// (/privacy, /internal/open, /internal/usage, /terms) at 390 px and fails if any is wider than the screen.
// What it does not prove: what a page does only after a click (a download, the 3D map's controls, a share card).
// That is why the full policy is report-only. No browser on the machine: it says so and exits 0 (1 on the runner).
import { withBrowser } from "./browser.mjs";

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
  await unlock(base);
  let enforced = 0, reported = 0, wide = 0, failed = 0;
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
