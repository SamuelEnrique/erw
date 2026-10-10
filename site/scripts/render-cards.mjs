// Energy Research Warehouse (ERW) site, session 170: the finding cards' renders, 1080 x 1350 (LinkedIn) and
// 1600 x 900 (X), from a built site in a real browser (scripts/browser.mjs, the machine's own Chrome or Edge headless).
//
//   npm run build && npx next start -p 3170
//   node scripts/render-cards.mjs [base-url] [--only card_id,card_id] [--out dir]     (default http://localhost:3170,
//                                                                                     out public/findings)
//
// Each card is photographed at /analysis/card/<id>?render=1, the frame app/analysis/card/render.css draws in the two
// bundled fonts. The renderer fails on any font fallback: before the shot it asks the page whether "Source Serif 4"
// and "Inter" are loaded faces (document.fonts, status "loaded", from the files under public/fonts/), and whether the
// title and the subtitle were laid out in them; a face that did not load, a missing file or a fallback is exit 1 for
// that card and no PNG is written. scripts/test-render-fonts.mjs proves it by removing a font. The internal view is
// opened first (the page is in review). Exit 1 on any failure; 2 when no browser is on the machine.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const base = (args.find((a) => a.startsWith("http")) ?? "http://localhost:3170").replace(/\/$/, "");
const only = args.includes("--only") ? args[args.indexOf("--only") + 1].split(",") : null;
const outDir = args.includes("--out") ? args[args.indexOf("--out") + 1] : path.join(here, "..", "public", "findings");
export const SIZES = [[1080, 1350], [1600, 900]];
export const FONTS = ["Source Serif 4", "Inter"];
export const FONT_FILES = ["SourceSerif4-Variable.ttf", "SourceSerif4-Italic-Variable.ttf", "Inter-Variable.ttf"];

/** The JavaScript run in the page: are both faces loaded from the bundle, and are the title and subtitle set in them? */
export const FONT_CHECK = `(async () => {
  await document.fonts.ready;
  const faces = [...document.fonts].filter((f) => f.status === "loaded").map((f) => f.family.replace(/^"|"$/g, ""));
  const want = ${JSON.stringify(FONTS)};
  const missing = want.filter((w) => !faces.includes(w));
  const t = document.querySelector(".finding-render .finding-title");
  const s = document.querySelector(".finding-render .finding-subtitle");
  const fam = (el) => (el ? getComputedStyle(el).fontFamily : "");
  const ok = (el, w) => el && fam(el).includes(w) && document.fonts.check(getComputedStyle(el).font || "16px " + JSON.stringify(w), el.textContent || "a");
  const fallback = [];
  if (!ok(t, "Source Serif 4")) fallback.push("title");
  if (!ok(s, "Source Serif 4")) fallback.push("subtitle");
  return { missing, fallback, faces, title: t ? t.textContent : null };
})()`;

export function cardIds() {
  const dir = path.join(here, "..", "data", "findings");
  return fs.readdirSync(dir).filter((f) => f.endsWith(".json") && f !== "catalogue.json").map((f) => f.slice(0, -5));
}

export function fontsPresent() {
  const dir = path.join(here, "..", "public", "fonts");
  return FONT_FILES.filter((f) => !fs.existsSync(path.join(dir, f)));
}

export async function render(base, ids, outDir, log = console.log) {
  const absent = fontsPresent();
  if (absent.length) {
    log(`FAIL the bundled fonts are not all in public/fonts/: missing ${absent.join(", ")} (no render is made in a fallback font)`);
    return 1;
  }
  fs.mkdirSync(outDir, { recursive: true });
  let bad = 0;
  const code = await withBrowser(async ({ go, wait, unlock, send, sleep }) => {
    await unlock(base);
    for (const id of ids) {
      for (const [w, h] of SIZES) {
        await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: false });
        await go(`${base}/analysis/card/${id}?render=1`);
        await wait('!!document.querySelector("[data-render=\\"1\\"] canvas")', 30000, "the card's chart");
        await sleep(800);
        const r = await send("Runtime.evaluate", { expression: FONT_CHECK, awaitPromise: true, returnByValue: true });
        const v = r.result?.value ?? {};
        if ((v.missing ?? ["unknown"]).length || (v.fallback ?? ["unknown"]).length) {
          bad += 1;
          log(`FAIL ${id} ${w}x${h}: font fallback (missing faces: ${(v.missing ?? []).join(", ") || "none"}; fallback on: ${(v.fallback ?? []).join(", ") || "none"})`);
          continue;
        }
        const shot = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: w, height: h, scale: 1 } });
        const out = path.join(outDir, `${id}_${w}x${h}.png`);
        fs.writeFileSync(out, Buffer.from(shot.data, "base64"));
        log(`ok   ${out}`);
      }
    }
    return bad ? 1 : 0;
  }, { width: 1600, height: 1350 });
  if (code === null) { log("no Chrome or Edge on this machine: not rendered here"); return 2; }
  return code;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const ids = only ?? cardIds();
  process.exitCode = await render(base, ids, outDir);
}
