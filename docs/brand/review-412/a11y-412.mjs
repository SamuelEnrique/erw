// Session 412: the accessibility tree and the keyboard order of each page, in the internal view.
//   node a11y.mjs <base> <out.json> <path> [path...]
import fs from "node:fs";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const [base, out, ...paths] = process.argv.slice(2);
const INTERACTIVE = new Set(["button", "link", "combobox", "textbox", "checkbox", "radio", "slider", "tab", "menuitem", "switch", "spinbutton", "searchbox", "listbox", "option"]);
const result = {};
const code = await withBrowser(async ({ go, evaluate, unlock, send, sleep }) => {
  await unlock(base);
  await send("Accessibility.enable");
  for (const p of paths) {
    const r = { unnamed: [], tabs: [], noFocusRing: [], error: null };
    try {
      await go(base + p);
      await sleep(2500);
      const { nodes } = await send("Accessibility.getFullAXTree");
      for (const n of nodes) {
        const role = n.role?.value;
        if (!INTERACTIVE.has(role) || n.ignored) continue;
        const name = (n.name?.value ?? "").trim();
        if (!name) {
          let html = "";
          if (n.backendDOMNodeId) {
            try {
              const { object } = await send("DOM.resolveNode", { backendNodeId: n.backendDOMNodeId });
              const v = await send("Runtime.callFunctionOn", { objectId: object.objectId, functionDeclaration: "function(){return this.outerHTML ? this.outerHTML.slice(0,220) : String(this.nodeName)}", returnByValue: true });
              html = v.result.value;
            } catch { /* gone */ }
          }
          r.unnamed.push({ role, html });
        }
      }
      // keyboard order: up to 80 Tab presses from the top
      await evaluate("(document.activeElement && document.activeElement.blur(), window.scrollTo(0,0), true)");
      for (let i = 0; i < 80; i += 1) {
        await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await sleep(40);
        const f = await evaluate(`(() => { const e = document.activeElement; if (!e || e === document.body) return null;
          const s = getComputedStyle(e); const b = e.getBoundingClientRect();
          const ring = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== 'none';
          return { tag: e.tagName.toLowerCase(), text: (e.getAttribute('aria-label') || e.innerText || e.value || '').trim().slice(0,50), ring, outline: s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor, w: Math.round(b.width), h: Math.round(b.height), y: Math.round(b.top + scrollY), x: Math.round(b.left), inMain: !!e.closest('main'), brand: !!e.closest('.brand-a') }; })()`);
        if (!f) break;
        r.tabs.push(f);
        if (!f.ring) r.noFocusRing.push(f);
      }
    } catch (e) { r.error = String(e.message ?? e); }
    result[p] = r;
    console.log(`${p}: unnamed ${r.unnamed.length}, tab stops ${r.tabs.length}, no ring ${r.noFocusRing.length}${r.error ? ", error " + r.error : ""}`);
  }
  fs.writeFileSync(out, JSON.stringify(result, null, 1));
  return 0;
});
process.exitCode = code === 0 ? 0 : 1;
