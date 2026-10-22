// Energy Research Warehouse (ERW), session 725 (chain 062): the utility planner's path through the All grids tab of
// /cost-of-power, walked click by click in a real browser, in the internal view (every page is in review), at 1280 and
// at 390 px wide: the utility column and its county, demand growth and capacity above the peak, the planned generation,
// the time to connect with the large-load rules and waits, the interruptible profile, the tracker's facilities and the
// gaps page. One shot a step and a width into this folder, and one JSON a width of what each step showed (the address,
// the checked figures in view, every tip in view with its words, the sort line, the headline, the first rows).
// docs/reviews/siting-utility-path.md is written from these files. Session 723's walk-723.mjs in its shape.
//
//   node docs/brand/review-725/walk-725.mjs https://erw-flame.vercel.app <json-dir>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3725").replace(/\/$/, "");
const jsonDir = process.argv[3] ?? here;
const WIDTHS = [[1280, 900, false], [390, 844, true]];
const TAB = "/cost-of-power?view=allgrids";
const js = (s) => JSON.stringify(s);
const HELPERS = `(() => {
  window.__h = {
    click(el) { if (!el) throw new Error("nothing to click"); el.scrollIntoView({ block: "center" }); el.click(); return true; },
    set(sel, value) { const e = document.querySelector(sel); if (!e) throw new Error("no field " + sel); e.value = value; e.dispatchEvent(new Event("input", { bubbles: true })); e.dispatchEvent(new Event("change", { bubbles: true })); return true; },
    tick(sel, on) { const e = document.querySelector(sel); if (!e) throw new Error("no box " + sel); if (e.checked !== on) e.click(); return e.checked; },
    submit() { const f = document.querySelector("form[data-allgrids-form]"); if (!f) throw new Error("no form"); f.requestSubmit(); return true; },
  };
  return true;
})()`;
const state = {};
const STEPS = [
  { id: "01-open", page: `${TAB}&mw=1000`, focus: "h1", does: "opens the tab with a 1,000 MW load (Size 1000, Show)" },
  { id: "02-utility-dearest", act: `(() => { __h.set('select[data-allgrids-sort]', 'utility'); __h.set('select[data-allgrids-dir]', 'desc'); return __h.submit(); })()`,
    until: "location.search.includes('sort=utility')", focus: "p[data-allgrids-sort]", does: "Sort by the utility's industrial revenue per MWh, largest first, Show" },
  { id: "03-utility-ercot", act: `(() => { __h.tick('input[name="grid"][value="ercot"]', true); return __h.submit(); })()`,
    until: "location.search.includes('grid=ercot')", focus: "p[data-allgrids-sort]", does: "Grids shown: ERCOT, Show: the Texas rows' utilities and their counties" },
  { id: "04-headroom", act: `(() => { __h.tick('input[name="grid"][value="ercot"]', false); __h.set('select[data-allgrids-sort]', 'headroom'); __h.set('select[data-allgrids-dir]', 'desc'); return __h.submit(); })()`,
    until: "location.search.includes('sort=headroom') && !location.search.includes('grid=ercot')", focus: "p[data-allgrids-sort]", does: "every grid again; Sort by demand growth, largest first, Show" },
  { id: "05-headroom-zones", act: `(() => { __h.set('select[data-allgrids-kind]', 'zone'); return __h.submit(); })()`,
    until: "location.search.includes('kind=zone')", focus: "p[data-allgrids-sort]", does: "Kind: load zones only, Show: a zone's own growth" },
  { id: "06-connect", act: `(() => { __h.set('select[data-allgrids-kind]', 'all'); __h.set('select[data-allgrids-sort]', 'connect'); __h.set('select[data-allgrids-dir]', 'asc'); return __h.submit(); })()`,
    until: "location.search.includes('sort=connect')", focus: "p[data-allgrids-sort]", does: "Kind: load zones and hubs; Sort by months to connect, smallest first, Show: the rules and waits under each" },
  { id: "07-rule-tip", act: `(() => { const b = [...document.querySelectorAll('[data-connect-load] [data-tip-trigger]')].find((e) => /^rule /.test(e.textContent.trim())); if (!b) throw new Error('no rule'); b.scrollIntoView({ block: 'center' }); b.focus(); window.__ruleTip = document.getElementById(b.getAttribute('aria-describedby')); return b.textContent.trim(); })()`,
    settle: 1200, focus: "p[data-allgrids-sort]", does: "puts the keyboard on the first row's rule (Tab to it): its tip opens" },
  { id: "08-industry", act: `__h.set('select[data-allgrids-profile]', 'industry')`,
    until: "location.search.includes('profile=industry')", settle: 3500, focus: "p[data-allgrids-sort]", does: "Profile: Heavy industry (interruptible): the capacity column" },
  { id: "09-ab-zones", page: `${TAB}&mw=1000&sort=utility&grid=ercot&a=ercot%3ALZ_HOUSTON&b=ercot%3ALZ_NORTH`, focus: "[data-allgrids-abpanel]", block: "start",
    does: "A ERCOT LZ_HOUSTON, B ERCOT LZ_NORTH, Show: two zones' utilities, growth and connection side by side" },
  { id: "10-tracker", page: "/datacenters", focus: "h1", does: "opens the datacenter tracker: each facility's link to its row on the tab" },
  { id: "11-gaps", page: "/internal/siting-gaps", focus: "h1", does: "opens the gaps page: the utility, headroom and time-to-connect rows" },
  { id: "12-send", page: `${TAB}&mw=1000&sort=utility&grid=ercot&a=ercot%3ALZ_HOUSTON&b=ercot%3ALZ_NORTH`, focus: "h1", does: "opens step 9's address in a new tab" },
];
const LOOK = (focus) => `(() => {
  const f = ${js(focus)};
  const el = document.querySelector(f);
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight; };
  const text = (e) => (e ? e.textContent.replace(/\\s+/g, " ").trim() : null);
  const tipOf = (b) => { const id = b.getAttribute("aria-describedby"); const t = id ? document.getElementById(id) : null; return t ? text(t) : null; };
  return {
    url: location.pathname + location.search, found: !!el,
    unreadable: document.body.innerText.includes("could not be read"),
    errorText: (document.body.innerText.match(/[^\\n]*(Application error|could not be read)[^\\n]*/) || [""])[0],
    checksInView: [...document.querySelectorAll("[data-check]")].filter(vis).map((e) => ({ k: e.getAttribute("data-check"), raw: e.getAttribute("data-raw"), text: e.textContent.trim() })).slice(0, 160),
    tipsInView: [...document.querySelectorAll("[data-tip-trigger],[aria-describedby]")].filter(vis).map((b) => ({ on: text(b).slice(0, 60), tip: tipOf(b) })).filter((t) => t.tip).slice(0, 80),
    nChecks: document.querySelectorAll("[data-check]").length,
    sortLine: text(document.querySelector("p[data-allgrids-sort]")),
    countLine: text(document.querySelector("[data-allgrids-count]")),
    headline: text(document.querySelector("[data-allgrids-headline]")),
    abPanel: text(document.querySelector("[data-allgrids-abpanel]")),
    ruleTip: window.__ruleTip ? { shown: getComputedStyle(window.__ruleTip).display !== "none", text: text(window.__ruleTip), links: window.__ruleTip.querySelectorAll("a").length } : null,
    rows: [...document.querySelectorAll("[data-allgrids-row]")].slice(0, 8).map((r) => ({ id: r.getAttribute("data-allgrids-row"), text: text(r).slice(0, 360) })),
    heads: [...document.querySelectorAll("th[data-col]")].map((h) => h.getAttribute("data-col")),
    tracker: location.pathname === "/datacenters" ? { rows: document.querySelectorAll("tbody tr").length, links: document.querySelectorAll("[data-facility-siting]").length, text: text(document.querySelector("main") || document.body).slice(0, 900) } : null,
    gaps: location.pathname === "/internal/siting-gaps" ? { n: document.querySelector("[data-siting-gaps]")?.getAttribute("data-siting-gaps"), rows: [...document.querySelectorAll("tbody tr")].map((r) => text(r).slice(0, 160)).filter((t) => /Utility|Headroom|Time to connect/.test(t)) } : null,
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth, totalH: document.documentElement.scrollHeight,
    firstCheckY: (() => { const c = document.querySelector("[data-check]"); return c ? Math.round(c.getBoundingClientRect().top + scrollY) : null; })(),
    boxOpen: (() => { const d = document.querySelector("details[data-allgrids-box]"); return d ? d.open : null; })(),
  };
})()`;
let failed = 0;
for (const [width, height, mobile] of WIDTHS) {
  const res = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep, errors }) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await unlock(base);
    const out = [];
    for (const s of STEPS) {
      const rec = { step: s.id, width, does: s.does };
      try {
        if (s.page) await go(base + s.page);
        await evaluate(HELPERS);
        if (s.act) rec.act = await evaluate(s.act);
        if (s.until) await wait(s.until, 60000, `${s.id}: ${s.until}`);
        await sleep(s.settle ?? 2500);
        await evaluate(HELPERS);
        if (s.id !== "07-rule-tip") await evaluate(`(() => { const f = ${js(s.focus)}; const el = document.querySelector(f); if (el) { if (f === "h1") window.scrollTo(0, 0); else el.scrollIntoView({ block: ${js(s.block ?? "start")} }); } return !!el; })()`);
        await sleep(800);
        Object.assign(rec, await evaluate(LOOK(s.focus)));
        const shot = await send("Page.captureScreenshot", { format: "png" });
        fs.writeFileSync(path.join(here, `${s.id}_${width}.png`), Buffer.from(shot.data, "base64"));
        rec.shot = `${s.id}_${width}.png`;
        console.log(`${rec.found ? "ok  " : "MISS"} ${s.id} ${width}: ${rec.url}${rec.unreadable ? " (the live set could not be read)" : ""}`);
      } catch (e) { failed += 1; rec.error = String(e.message ?? e); console.log(`FAIL ${s.id} ${width}: ${rec.error}`); }
      out.push(rec);
    }
    return { steps: out, pageErrors: errors };
  }, { width, height });
  if (!res) { console.log("no browser on this machine"); process.exit(1); }
  fs.writeFileSync(path.join(jsonDir, `walk-${width}.json`), JSON.stringify(res, null, 1));
}
process.exit(failed ? 1 : 0);
