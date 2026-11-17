// Energy Research Warehouse (ERW) site, chain 305 (session 7602, the portable laptop): the rows of
// docs/state/browser_reads_wanted.md read in a real browser on a local build, as session 7600 and 7601 read rows 1 to 31.
//
//   node scripts/read-rows-c305.mjs <rows.json> <out.json> [shots-dir] [--only 32,33]
//
// rows.json is a list of { row, path, widths: [1280, 390], visitor?: true, steps: [...], expect: [...], shot: "name" }.
// Each row is opened at each width in the internal view (or as a visitor), its steps run, and what was seen is written:
// every expected string found in the visible text, only in the page's hidden words (a closed hover's box), or not at all;
// whether the page scrolls sideways; every "i" box opened by a real mouse hover and by a focus, with its place against
// the window; the words a step collected (a chart's hover cards, a link's address). Nothing here decides a row: the
// session reads the output and writes the row's state. Steps:
//   { click: "words" }            a real mouse click on the smallest visible link, button, summary, label or option holding the words
//   { clickSel: "css" }           the same on the first visible element the selector finds
//   { type: ["label words", "value"] }   the input or textarea whose label holds the words, cleared and typed
//   { select: ["label words", "option words"] }  the select whose label holds the words, set to the option holding the words
//   { openFolds: true }           every <details> opened (their state as the page opened is kept first)
//   { tips: "css" }               every mark the selector finds (default the site's shared mark) hovered, then focused
//   { sweep: ["css", n] }         the mouse moved across the element at n places and three heights: new words kept
//   { hover: "words" }            the mouse rested on the smallest element holding the words: new words kept
//   { eval: "js" }                an expression's value kept
//   { wait: ms }, { scroll: "words" }, { url: true } (the address kept), { shot: "suffix" }
import fs from "node:fs";
import path from "node:path";
import { withBrowser, sleep } from "./browser.mjs";

const [rowsFile, outFile, shotsDir = ""] = process.argv.slice(2);
const onlyArg = process.argv.indexOf("--only");
const only = onlyArg > 0 ? new Set(process.argv[onlyArg + 1].split(",").map(Number)) : null;
const BASE = process.env.READ_BASE || "http://localhost:3305";
const rows = JSON.parse(fs.readFileSync(rowsFile, "utf-8")).filter((r) => !only || only.has(r.row));
if (shotsDir) fs.mkdirSync(shotsDir, { recursive: true });

const FIND = `(words, sel) => {
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const pool = [...document.querySelectorAll(sel)].filter(vis);
  const norm = (t) => (t || '').replace(/\\s+/g, ' ').trim();
  const hits = pool.filter((e) => norm(e.innerText || e.textContent).includes(words) || (e.getAttribute('aria-label') || '').includes(words) || (e.value || '') === words);
  hits.sort((a, b) => norm(a.innerText).length - norm(b.innerText).length);
  return hits[0] || null;
}`;

const out = [];
const code = await withBrowser(async ({ go, evaluate, send, unlock }) => {
  let unlocked = false;
  for (const r of rows) {
    for (const width of r.widths ?? [1280, 390]) {
      const height = width < 500 ? 844 : 900;
      const res = { row: r.row, path: r.path, width, found: [], hiddenOnly: [], missing: [], notes: [], collected: [], tips: [] };
      try {
        await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 500 });
        if (r.visitor) {
          await send("Network.clearBrowserCookies"); unlocked = false;
        } else if (!unlocked) { await unlock(BASE); unlocked = true; }
        if (r.path.includes("#")) await go("about:blank");   // a change of hash alone fires no load event
        await go(BASE + r.path);
        await sleep(r.settle ?? 1500);
        res.foldsAtOpen = await evaluate(`[...document.querySelectorAll('details')].map((d) => ({ open: d.open, summary: (d.querySelector('summary')?.innerText || '').replace(/\\s+/g,' ').trim().slice(0, 90) }))`);
        const mouse = async (x, y, type = "mouseMoved") => send("Input.dispatchMouseEvent", { type, x, y, button: type === "mouseMoved" ? "none" : "left", clickCount: type === "mouseMoved" ? 0 : 1 });
        const centre = async (expr) => evaluate(`(() => { const e = ${expr}; if (!e) return null; e.scrollIntoView({ block: 'center', inline: 'nearest' }); const b = e.getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2, tag: e.tagName, text: (e.innerText || e.value || '').replace(/\\s+/g,' ').trim().slice(0, 80) }; })()`);
        const textNow = async () => evaluate(`document.body.innerText`);
        const newLines = (before, after) => { const b = new Set(before.split("\n").map((s) => s.trim())); return after.split("\n").map((s) => s.trim()).filter((s) => s && !b.has(s)); };
        for (const s of r.steps ?? []) {
          if (s.click || s.clickSel) {
            const expr = s.clickSel ? `[...document.querySelectorAll(${JSON.stringify(s.clickSel)})].find((e) => e.getBoundingClientRect().width > 0)` : `(${FIND})(${JSON.stringify(s.click)}, 'a,button,summary,label,option,[role=button],[role=tab],input[type=radio],input[type=checkbox]')`;
            const c = await centre(expr);
            if (!c) { res.notes.push(`click: nothing visible holds "${s.click ?? s.clickSel}"`); continue; }
            await sleep(150); await mouse(c.x, c.y); await mouse(c.x, c.y, "mousePressed"); await mouse(c.x, c.y, "mouseReleased");
            await sleep(s.after ?? 1200);
            res.notes.push(`clicked ${c.tag} "${c.text}"`);
          } else if (s.type) {
            const [label, value] = s.type;
            const ok = await evaluate(`(() => { const lab = [...document.querySelectorAll('label')].find((l) => l.innerText.replace(/\\s+/g,' ').includes(${JSON.stringify(label)}));
              let el = lab ? (lab.control || lab.querySelector('input,textarea') || document.getElementById(lab.htmlFor)) : null;
              if (!el) el = [...document.querySelectorAll('input,textarea')].find((i) => (i.getAttribute('aria-label') || i.placeholder || i.name || '').includes(${JSON.stringify(label)}));
              if (!el) return false; el.scrollIntoView({ block: 'center' }); el.focus(); el.select && el.select(); return true; })()`);
            if (!ok) { res.notes.push(`type: no field labelled "${label}"`); continue; }
            await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Delete", code: "Delete", windowsVirtualKeyCode: 46 });
            await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Delete", code: "Delete", windowsVirtualKeyCode: 46 });
            if (value !== "") await send("Input.insertText", { text: String(value) });
            await sleep(s.after ?? 600);
            res.notes.push(`typed "${value}" in "${label}"`);
          } else if (s.select) {
            const [label, opt] = s.select;
            const v = await evaluate(`(() => { const lab = [...document.querySelectorAll('label')].find((l) => l.innerText.replace(/\\s+/g,' ').includes(${JSON.stringify(label)}));
              let el = lab ? (lab.querySelector('select') || lab.control || document.getElementById(lab.htmlFor)) : null;
              if (!el || el.tagName !== 'SELECT') el = [...document.querySelectorAll('select')].find((x) => (x.getAttribute('aria-label') || x.name || '').includes(${JSON.stringify(label)}));
              if (!el) return 'no select';
              const o = [...el.options].find((o) => o.text.includes(${JSON.stringify(opt)}) || o.value === ${JSON.stringify(opt)});
              if (!o) return 'no option: ' + [...el.options].map((o) => o.text).slice(0, 60).join(' | ');
              const set = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set; set.call(el, o.value);
              el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); return 'set ' + o.text; })()`);
            await sleep(s.after ?? 1200);
            res.notes.push(`select "${label}": ${v}`);
          } else if (s.openFolds) {
            await evaluate(`[...document.querySelectorAll('details')].forEach((d) => { d.open = true; })`); await sleep(400);
          } else if (s.tips !== undefined) {
            const sel = s.tips || "span.tip[data-tip] > button";
            const n = await evaluate(`[...document.querySelectorAll(${JSON.stringify(sel)})].filter((e) => e.getBoundingClientRect().width > 0).length`);
            const limit = Math.min(n, s.max ?? 40);
            for (let i = 0; i < limit; i += 1) {
              const pick = `[...document.querySelectorAll(${JSON.stringify(sel)})].filter((e) => e.getBoundingClientRect().width > 0)[${i}]`;
              for (const how of ["hover", "focus"]) {
                await mouse(1, 1); await evaluate(`document.activeElement && document.activeElement.blur && document.activeElement.blur()`);
                const c = await centre(pick);
                if (!c) continue;
                if (how === "hover") await mouse(c.x, c.y); else await evaluate(`${pick}.focus()`);
                await sleep(250);
                const m = await evaluate(`(() => { const t = ${pick}; const host = t.closest('span.tip') || t.parentElement; const box = host.querySelector('[role=tooltip]') || document.getElementById(t.getAttribute('aria-describedby'));
                  if (!box) return { box: false };
                  const b = box.getBoundingClientRect(); const s = getComputedStyle(box);
                  return { box: true, shown: s.display !== 'none' && s.visibility !== 'hidden' && b.width > 0, left: Math.round(b.left), right: Math.round(b.right), top: Math.round(b.top), bottom: Math.round(b.bottom),
                    vw: document.documentElement.clientWidth, vh: innerHeight, sw: document.documentElement.scrollWidth, cut: box.scrollHeight > box.clientHeight + 2,
                    label: t.getAttribute('aria-label') || '', words: box.innerText.replace(/\\s+/g,' ').trim().slice(0, 600) }; })()`);
                res.tips.push({ i, how, ...m });
              }
            }
            await mouse(1, 1);
          } else if (s.sweep) {
            const [sel, n = 40] = s.sweep;
            const box = await evaluate(`(() => { const e = [...document.querySelectorAll(${JSON.stringify(sel)})].filter((x) => x.getBoundingClientRect().width > 0)[${s.index ?? 0}]; if (!e) return null; e.scrollIntoView({ block: 'center' }); const b = e.getBoundingClientRect(); return { l: b.left, t: b.top, w: b.width, h: b.height }; })()`);
            if (!box) { res.notes.push(`sweep: nothing for ${sel}`); continue; }
            await mouse(1, 1); await sleep(200);
            const base = await textNow();
            const seen = new Set();
            for (const fy of s.heights ?? [0.3, 0.5, 0.8]) for (let k = 0; k < n; k += 1) {
              await mouse(box.l + box.w * (k + 0.5) / n, box.t + box.h * fy); await sleep(60);
              for (const l of newLines(base, await textNow())) seen.add(l);
            }
            res.collected.push({ sweep: sel, lines: [...seen].slice(0, 400) });
            await mouse(1, 1);
          } else if (s.hover) {
            const c = await centre(`(${FIND})(${JSON.stringify(s.hover)}, ${JSON.stringify(s.within || "abbr,span,td,th,a,button,dfn,u,strong,b,p,div,li,text,tspan")})`);
            if (!c) { res.notes.push(`hover: nothing visible holds "${s.hover}"`); continue; }
            await mouse(1, 1); await sleep(150);
            const base = await textNow();
            await mouse(c.x, c.y); await sleep(500);
            const title = await evaluate(`(() => { const e = document.elementFromPoint(${c.x}, ${c.y}); let t = e; while (t && !t.getAttribute?.('title')) t = t.parentElement; return t ? t.getAttribute('title') : null; })()`);
            res.collected.push({ hover: s.hover, at: c.text, lines: newLines(base, await textNow()).slice(0, 40), title });
          } else if (s.cardAt) {
            // { cardAt: ["css", index, fx, fy] }: the mouse rested at a point of an element; the chart cards' words kept whole
            const [sel, idx = 0, fx = 0.5, fy = 0.5] = s.cardAt;
            const c = await evaluate(`(() => { const e = [...document.querySelectorAll(${JSON.stringify(sel)})].filter((x) => x.getBoundingClientRect().width > 0)[${idx}]; if (!e) return null; e.scrollIntoView({ block: 'center' }); const b = e.getBoundingClientRect(); return { x: b.left + b.width * ${fx}, y: b.top + b.height * ${fy} }; })()`);
            if (!c) { res.notes.push(`cardAt: nothing for ${sel}`); continue; }
            await mouse(1, 1); await sleep(200); await mouse(c.x, c.y); await sleep(500);
            res.collected.push({ cardAt: `${sel} #${idx} at ${fx},${fy}`, cards: await evaluate(`[...document.querySelectorAll('[data-chart-card]')].filter((e) => e.getBoundingClientRect().width > 0).map((e) => e.innerText.replace(/\\s+/g, ' ').slice(0, 600))`) });
          } else if (s.wheel) {
            // { wheel: [fx, fy, deltaY, times] }: the mouse wheel turned at a point of the first large canvas, as a reader zooms a map
            const [fx, fy, dy, times = 1] = s.wheel;
            const c = await evaluate(`(() => { const e = [...document.querySelectorAll('canvas')].find((x) => x.getBoundingClientRect().width > 300); if (!e) return null; e.scrollIntoView({ block: 'center' }); const b = e.getBoundingClientRect(); return { x: b.left + b.width * ${fx}, y: b.top + b.height * ${fy} }; })()`);
            if (!c) { res.notes.push("wheel: no canvas"); continue; }
            await sleep(300);
            for (let k = 0; k < times; k += 1) { await send("Input.dispatchMouseEvent", { type: "mouseWheel", x: c.x, y: c.y, deltaX: 0, deltaY: dy }); await sleep(250); }
            await sleep(800);
            res.notes.push(`wheel ${times} times at ${Math.round(c.x)}, ${Math.round(c.y)}`);
          } else if (s.eval) {
            res.collected.push({ eval: s.eval.slice(0, 80), value: await evaluate(s.eval) });
          } else if (s.wait) {
            await sleep(s.wait);
          } else if (s.scroll) {
            await centre(`(${FIND})(${JSON.stringify(s.scroll)}, 'h1,h2,h3,h4,summary,p,table,div,section')`); await sleep(400);
          } else if (s.url) {
            res.collected.push({ url: await evaluate("location.pathname + location.search + location.hash") });
          } else if (s.shot && shotsDir) {
            const f = path.join(shotsDir, `row-${String(r.row).padStart(2, "0")}-${s.shot}-${width}.png`);
            const shot = await send("Page.captureScreenshot", { format: "png" });
            fs.writeFileSync(f, Buffer.from(shot.data, "base64")); res.notes.push(`picture ${path.basename(f)}`);
          }
        }
        const text = await textNow();
        const all = await evaluate(`document.body.textContent + ' ' + [...document.querySelectorAll('[title],[aria-label]')].map((e) => (e.getAttribute('title') || '') + ' ' + (e.getAttribute('aria-label') || '')).join(' ')`);
        const norm = (t) => t.replace(/\s+/g, " ").replace(/−/g, "-");
        const vis = norm(text), hid = norm(all);
        for (const e of r.expect ?? []) {
          const w = norm(e);
          if (vis.includes(w)) res.found.push(e); else if (hid.includes(w)) res.hiddenOnly.push(e); else res.missing.push(e);
        }
        res.sideways = await evaluate(`({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, body: document.body.scrollWidth })`);
        res.inReview = /in review/i.test(vis.slice(0, 600)) && !/Decisions on this page/.test(vis);
        res.finalUrl = await evaluate("location.pathname + location.search + location.hash");
        if (r.shot && shotsDir) {
          const f = path.join(shotsDir, `row-${String(r.row).padStart(2, "0")}-${r.shot}-${width}.png`);
          const shot = await send("Page.captureScreenshot", { format: "png" });
          fs.writeFileSync(f, Buffer.from(shot.data, "base64"));
          res.notes.push(`picture ${path.basename(f)}`);
        }
        if (r.keepText) res.text = vis.slice(0, r.keepText);
      } catch (err) {
        res.error = String(err.message || err);
      }
      out.push(res);
      const tipsBad = res.tips.filter((t) => t.shown && (t.left < 0 || t.right > t.vw || t.sw > t.vw || t.cut)).length;
      const tipsShown = res.tips.filter((t) => t.shown).length;
      console.log(`row ${r.row} @${width}: found ${res.found.length}, hidden ${res.hiddenOnly.length}, missing ${res.missing.length}; sideways ${res.sideways ? res.sideways.sw > res.sideways.cw : "?"}; tips shown ${tipsShown}/${res.tips.length}, outside ${tipsBad}${res.error ? "; ERROR " + res.error : ""}`);
      fs.writeFileSync(outFile, JSON.stringify(out, null, 1));
    }
  }
  return 0;
});
if (code === null) { console.error("no browser on this machine: not read"); process.exit(2); }
process.exit(code);
