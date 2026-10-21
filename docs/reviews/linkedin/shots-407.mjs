// Session 407: the ten LinkedIn images, 1200 by 627 px, cut from pages of a local build. Each image is a browser
// viewport of 1200 by 627 CSS px at scale 1, scrolled to the chart that holds or sits beside the post's figure: the
// script finds the element the page wrote for the figure (data-check equal to the post's key), walks up from it to the
// nearest element that holds one of the shared chart components (TimeChart's [data-time-chart], svgchart's
// [data-svg-chart], SeriesChart's [data-series-chart]) and takes the first chart in it, with its ChartFrame figure and
// title where it has one. Nothing is drawn here: the pixels are the page's. The pages are in review: the internal
// view is opened by the form (unlock, the token posted, never in an address).
//
//   cd site && npm run build && npx next start -p 3407
//   node ../docs/reviews/linkedin/shots-407.mjs http://localhost:3407
//
// Prints one line an image (the page, the chart's kind and id, its title, the figure's text as the page shows it)
// and exits 1 when any image is not made, or the page's text for the figure is not the one posts.json holds.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = process.argv[2] ?? "http://localhost:3407";
const spec = JSON.parse(fs.readFileSync(path.join(here, "posts.json"), "utf-8"));
const only = (process.env.SHOTS_ONLY ?? "").split(",").map(Number).filter(Boolean);
const W = 1200, H = 627;
const CHART = `[data-time-chart="lines"],[data-time-chart="stacked"],[data-svg-chart],[data-series-chart]`;

/** The width and height a PNG says in its header. */
const pngSize = (buf) => ({ w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) });

const code = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep }) => {
  await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await unlock(base);
  let failed = 0;
  for (const p of spec.posts) {
    if (only.length && !only.includes(p.n)) continue;
    const k = JSON.stringify(p.key);
    const keyEl = `[...document.querySelectorAll("[data-check]")].find((e) => e.getAttribute("data-check") === ${k})`;
    try {
      await go(base + p.page);
      await wait(`!!(${keyEl})`, 30000, `the figure ${p.key} on ${p.page}`);
      if (await evaluate(`/could not be read/i.test(document.body.innerText)`)) console.log(`note ${p.page}: the page says the live set could not be read`);
      // the chart: the nearest ancestor of the figure that holds a shared chart, and its first chart
      const found = await evaluate(`(() => {
        const key = ${keyEl};
        let a = key.parentElement, chart = null;
        while (a && !chart) { chart = a.querySelector(${JSON.stringify(CHART)}); a = a.parentElement; }
        if (!chart) return null;
        window.__shot = chart.closest("figure") ?? chart;
        const section = window.__shot.closest("section");
        window.__head = section ? section.querySelector("h2") : null;
        const title = (window.__shot.querySelector("figcaption")?.textContent ?? window.__head?.textContent ?? "").trim();
        return { kind: chart.getAttribute("data-time-chart") ? "time-chart " + chart.getAttribute("data-time-chart") : chart.getAttribute("data-svg-chart") ? "svg-chart " + chart.getAttribute("data-svg-chart") : "series-chart",
          id: chart.getAttribute("data-chart") ?? chart.getAttribute("data-series-chart") ?? "", title, text: key.textContent.trim() };
      })()`);
      if (!found) throw new Error("no shared chart holds or sits beside the figure");
      // fixed and sticky bars would cover the chart: they are laid in the flow for the picture
      await evaluate(`(() => { for (const e of document.querySelectorAll("body *")) { const s = getComputedStyle(e).position; if (s === "fixed" || s === "sticky") e.style.position = "static"; } })()`);
      await sleep(800);
      // the frame: the section's title with the chart when both fit in 627 px, else the chart's frame alone, centred
      const top = await evaluate(`(() => {
        const f = window.__shot.getBoundingClientRect(), h = window.__head ? window.__head.getBoundingClientRect() : null;
        const y = (r) => r.top + scrollY;
        if (h && y(h) <= y(f) && f.bottom + scrollY - y(h) + 32 <= ${H}) return y(h) - 16;
        if (f.height + 32 <= ${H}) return y(f) - (${H} - f.height) / 2;
        return y(f) - 16;
      })()`);
      await evaluate(`window.scrollTo(0, ${Math.max(0, Math.round(top))})`);
      await sleep(1200);
      const shot = await send("Page.captureScreenshot", { format: "png" });
      const buf = Buffer.from(shot.data, "base64");
      const { w, h } = pngSize(buf);
      if (w !== W || h !== H) throw new Error(`the image is ${w} by ${h}, not ${W} by ${H}`);
      fs.writeFileSync(path.join(here, p.file), buf);
      const same = found.text === p.shown;
      if (!same) failed += 1;
      console.log(`${same ? "ok  " : "TEXT"} ${p.file}: ${p.page}, ${found.kind}${found.id ? ` "${found.id}"` : ""}, "${found.title.slice(0, 90)}"; the figure shows "${found.text}"${same ? "" : `, posts.json holds "${p.shown}"`}`);
    } catch (e) {
      failed += 1;
      console.log(`FAIL ${p.file}: ${p.page}: ${e.message ?? e}`);
    }
  }
  return failed ? 1 : 0;
}, { width: W, height: H });
if (code === null) { console.log("no browser on this machine: not proven here"); process.exit(1); }
process.exit(code);
