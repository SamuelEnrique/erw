// Energy Research Warehouse (ERW) site, session 102: does each page in review render, with data, on a deployed site?
//
//   node scripts/check-review-pages.mjs <base-url> <path> [<path> ...]
//   node scripts/check-review-pages.mjs https://erw-flame.vercel.app /queues /mix/v2 "/contracts?view=largest"
//
// Each page is asked twice, as HTML:
//   visitor        without the cookie a page in review answers the short in-review page, and holds none of its figures
//   internal view  with the cookie of /internal/unlock (INTERNAL_COSTS_TOKEN, from the environment or the repository's
//                  .env) the page answers 200, is not the in-review page, says nowhere that a table could not be read
//                  or is not loaded, and holds figures: the count of numbers in its visible text is printed
// A page drawn by the browser (a map, a game) holds few figures in its HTML: for those the count is what the server
// sent, and the page's own browser check (check-network-v3.mjs, play-battery.mjs) is the proof. Exit 1 on a failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const [baseArg, ...given] = process.argv.slice(2);
// Git Bash on Windows rewrites an argument that begins with "/" into a Windows path (run with MSYS_NO_PATHCONV=1, or
// give the paths without the leading slash): both spellings are taken
const paths = given.map((p) => p.replaceAll("\\", "/").replace(/^[A-Za-z]:\/.*?\/Git(?=\/)/, "")).map((p) => (p.startsWith("/") ? p : `/${p}`));
if (!baseArg || paths.length === 0) { console.log("usage: check-review-pages.mjs <base-url> <path> [<path> ...]"); process.exit(2); }
const base = baseArg.replace(/\/$/, "");
const here = path.dirname(fileURLToPath(import.meta.url));
const env = (k) => {
  if (process.env[k]) return process.env[k];
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    const m = fs.readFileSync(f, "utf8").match(new RegExp(`^${k}=(.*)$`, "m"));
    if (m) return m[1].trim().replace(/^["']|["']$/g, "");
  }
  return undefined;
};
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }

const get = async (p, withCookie) => {
  const r = await fetch(base + p, { headers: withCookie ? { Cookie: cookie } : {}, redirect: "manual" });
  return { status: r.status, html: await r.text(), location: r.headers.get("location") };
};
// the visible text: scripts, styles and tags out
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/g, " ").replace(/<style[\s\S]*?<\/style>/g, " ").replace(/<[^>]+>/g, " ").replace(/&[a-z#0-9]+;/g, " ").replace(/\s+/g, " ");
const BAD = [/could not be read/i, /not loaded here yet/i, /no number is shown/i, /Application error/i, /Internal Server Error/i];
const inReview = (html) => /data-in-review-page|This (page|tool) is in review/i.test(html);

let bad = 0;
for (const p of paths) {
  const v = await get(p, false);
  const i = await get(p, true);
  const t = text(i.html);
  const figures = (t.match(/\b\d[\d,]*(\.\d+)?\b/g) ?? []).length;
  const said = BAD.filter((r) => r.test(t)).map(String);
  const title = (i.html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/) ?? [, ""])[1].replace(/<[^>]+>/g, "").trim().slice(0, 70);
  const visitorClosed = v.status !== 200 || inReview(v.html) || text(v.html).length < t.length / 2;
  const ok = i.status === 200 && !inReview(i.html) && said.length === 0 && figures > 0 && visitorClosed;
  if (!ok) bad += 1;
  console.log(`${ok ? "ok  " : "FAIL"} ${p}: internal ${i.status}, "${title}", ${figures} figures in ${t.length.toLocaleString("en-US")} characters of text`
    + `${said.length ? `, says ${said.join(" ")}` : ""}; visitor ${v.status}${v.location ? ` to ${v.location}` : ""}${visitorClosed ? ", closed" : ", OPEN TO A VISITOR"}`);
}
console.log(`${paths.length - bad} of ${paths.length} pages render with data in the internal view at ${base}`);
process.exit(bad ? 1 : 0);
