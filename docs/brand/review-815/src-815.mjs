// Energy Research Warehouse (ERW), session 815: which picture of the chart of the day a 390 px and a 1280 px viewport load.
//   node docs/brand/review-815/src-815.mjs <url>      (the internal view is opened first)
import { withBrowser } from "../../../site/scripts/browser.mjs";
const [url] = process.argv.slice(2);
const code = await withBrowser(async ({ go, unlock, send, sleep }) => {
  const js = async (expression) => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true })).result?.value;
  await unlock(new URL(url).origin);
  for (const [w, h, mobile] of [[1280, 800, false], [390, 844, true]]) {
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile });
    await go(url);
    await sleep(1500);
    const m = await js(`(() => { const i = document.querySelector("img[src*='digest-charts']"); return i ? { src: i.currentSrc, srcset: i.getAttribute("srcset"), w: Math.round(i.getBoundingClientRect().width), nw: i.naturalWidth, nh: i.naturalHeight } : null; })()`);
    console.log(`${w}x${h}: ${JSON.stringify(m)}`);
  }
  return 0;
}, { width: 1280, height: 800 });
process.exit(code ?? 2);
