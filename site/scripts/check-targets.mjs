// Energy Research Warehouse (ERW) site, session 423: the footer's links and the touch targets of the nav aside and
// /about, measured in the internal view (pages in review are read as the reviewer reads them).
//
//   node scripts/check-targets.mjs <base> [--json out.json]
//
// Two rules, each read in a browser at 1280 and 390 px:
//   1. WCAG 1.4.1 (use of color), as docs/brand.md section 2 states it: "A link in running text is underlined". Every
//      link of the footer's sentence must draw an underline (text-decoration-line), not only its color.
//   2. WCAG 2.2, 2.5.8 (target size, minimum): a target is at least 24 by 24 CSS px, or an undersized target's 24 px
//      circle, centered on its box, meets no other target and no other undersized target's circle; a target inside a
//      sentence or a block of text (the inline exception) is listed and not failed. The brand's own 24 px rule
//      (docs/brand.md section 3, stricter: no spacing) is reported beside it and never fails the check.
// Exit 0 when both rules hold everywhere, 1 when one fails, 2 on bad input.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";

const args = process.argv.slice(2);
const base = args.find((a) => /^https?:\/\//.test(a));
const jsonAt = args.indexOf("--json");
const jsonOut = jsonAt >= 0 ? args[jsonAt + 1] : null;
if (!base) { console.error("usage: node scripts/check-targets.mjs <base> [--json out.json]"); process.exit(2); }

const PAGES = ["/", "/about"];
const WIDTHS = [1280, 390];

// In the page: the targets of one region, each with its box, whether it is inline in text, and whether it underlines.
const MEASURE = `(() => {
  const SEL = 'a[href], button, input:not([type="hidden"]), select, textarea, summary, [role="button"], [tabindex]:not([tabindex="-1"])';
  const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none"; };
  const blockOf = (el) => { let p = el.parentElement; while (p && getComputedStyle(p).display.startsWith("inline")) p = p.parentElement; return p; };
  const inlineInText = (el) => {
    if (!getComputedStyle(el).display.startsWith("inline")) return false;
    const block = blockOf(el); if (!block) return false;
    const clone = block.cloneNode(true);
    clone.querySelectorAll(SEL).forEach((t) => t.remove());
    return /[A-Za-z0-9]{2,}/.test(clone.textContent || "");
  };
  const read = (root, region) => root ? [...root.querySelectorAll(SEL)].filter(visible).map((el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return { region, text: (el.textContent || el.getAttribute("aria-label") || el.tagName).trim().replace(/\\s+/g, " ").slice(0, 60),
      tag: el.tagName.toLowerCase(), x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height,
      inline: inlineInText(el), underline: s.textDecorationLine.includes("underline") };
  }) : [];
  const all = [...document.querySelectorAll(SEL)].filter(visible).map((el) => { const r = el.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height }; });
  return {
    footer: read(document.querySelector("body > footer"), "footer"),
    aside: read(document.querySelector("[data-nav-aside]"), "nav aside"),
    about: location.pathname === "/about" ? read(document.querySelector("main"), "/about") : [],
    all,
  };
})()`;

// WCAG 2.5.8's spacing test for one undersized target against every other target on the page.
function spacingHolds(t, others) {
  const cx = t.x + t.w / 2, cy = t.y + t.h / 2, R = 12;
  for (const o of others) {
    if (Math.abs(o.x - t.x) < 0.5 && Math.abs(o.y - t.y) < 0.5 && Math.abs(o.w - t.w) < 0.5 && Math.abs(o.h - t.h) < 0.5) continue;
    const nx = Math.max(o.x, Math.min(cx, o.x + o.w)), ny = Math.max(o.y, Math.min(cy, o.y + o.h));
    if (Math.hypot(nx - cx, ny - cy) < R) return false;                 // the circle meets the other target
    if (o.w < 24 || o.h < 24) {
      const ox = o.x + o.w / 2, oy = o.y + o.h / 2;
      if (Math.hypot(ox - cx, oy - cy) < 2 * R) return false;          // the two circles meet
    }
  }
  return true;
}

const rows = [];
let failures = 0;
const code = await withBrowser(async ({ go, evaluate, unlock, send, sleep }) => {
  await unlock(base);
  for (const width of WIDTHS) {
    await send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
    for (const page of PAGES) {
      await go(new URL(page, base).href);
      await sleep(800);
      const m = await evaluate(MEASURE);
      for (const t of [...m.footer, ...m.aside, ...m.about]) {
        const bySize = t.w >= 24 && t.h >= 24;
        const bySpacing = bySize || spacingHolds(t, m.all);
        const wcag = bySize ? "size" : bySpacing ? "spacing" : t.inline ? "inline (exempt)" : "FAIL";
        const brand = bySize ? "24 px" : "under 24 px";
        const colorOnly = t.region === "footer" && t.tag === "a" && !t.underline;
        if (wcag === "FAIL") failures += 1;
        if (colorOnly) failures += 1;
        rows.push({ width, page, ...t, w: Math.round(t.w * 10) / 10, h: Math.round(t.h * 10) / 10, wcag, brand, colorOnly });
        console.log(`${colorOnly || wcag === "FAIL" ? "FAIL" : "ok  "} ${width} ${page} ${t.region}: "${t.text}" ${t.w.toFixed(1)} x ${t.h.toFixed(1)} px, WCAG 2.5.8 ${wcag}, brand ${brand}${t.region === "footer" ? `, underline ${t.underline ? "yes" : "no"}` : ""}`);
      }
    }
  }
  return 0;
});
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(rows, null, 1));
console.log(`${rows.length} targets read, ${failures} failing`);
process.exitCode = code !== 0 ? 1 : failures ? 1 : 0;
