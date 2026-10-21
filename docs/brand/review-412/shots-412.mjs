// Session 412: window screenshots at 1280 and 390 of a list of pages, in the internal view.
//   node shots.mjs <base> <outdir> <suffix> name=path [name=path...]
// A name ending in "-focus" tabs `n` times (name-focus3=path: three Tabs) before the shot, to show the focus ring.
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const [base, outdir, suffix, ...pairs] = process.argv.slice(2);
fs.mkdirSync(outdir, { recursive: true });
const code = await withBrowser(async ({ go, unlock, send, sleep, evaluate }) => {
  await unlock(base);
  for (const pair of pairs) {
    const i = pair.indexOf("=");
    const name = pair.slice(0, i); const rest = pair.slice(i + 1); const focusSel = rest.includes("@@") ? rest.split("@@")[1] : null; const [p, sel] = focusSel ? [rest.split("@@")[0], null] : rest.split("@");
    const tabs = Number((name.match(/-focus(\d+)$/) ?? [])[1] ?? 0);
    for (const [w, h, mobile] of [[1280, 900, false], [390, 844, true]]) {
      await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile });
      await go(base + p);
      await sleep(2500);
      for (let t = 0; t < tabs; t += 1) {
        await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await sleep(60);
      }
      if (tabs) await evaluate("(document.activeElement && document.activeElement.scrollIntoView({block:'center'}), true)");
      if (focusSel) {
        await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(focusSel)}); if (e) { e.focus(); e.scrollIntoView({block:"center"}); } return !!e; })()`);
      }
      if (sel) await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (e) e.scrollIntoView({block:"center"}); return !!e; })()`);
      await sleep(400);
      const shot = await send("Page.captureScreenshot", { format: "png" });
      const f = path.join(outdir, `${name}_${suffix}_${w}.png`);
      fs.writeFileSync(f, Buffer.from(shot.data, "base64"));
      console.log(f);
    }
  }
  return 0;
});
process.exitCode = code === 0 ? 0 : 1;
