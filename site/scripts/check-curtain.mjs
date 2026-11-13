// Energy Research Warehouse (ERW) site, session 5101: does a visitor get a page in review at one of the App Router's
// transport addresses? (site/proxy.ts; docs/reviews/security-faults-2026-11-13.md, row 1.)
//
//   node scripts/check-curtain.mjs https://erw-flame.vercel.app      after a deploy: the proof of row 1
//   node scripts/check-curtain.mjs http://localhost:3000             a local build: every address answers 404 there
//
// It reads as a visitor (no cookie, no token), GET only: for each page of the list, the page itself and its transport
// addresses (<page>.rsc, <page>.segments/_tree.segment.rsc, <page>.segments/_full.segment.rsc and the page's own
// segment). A page in review must answer the in-review page at its own address, and each transport address must
// answer 404 or the in-review page's data: an answer that is the page's own data fails the check, with the address.
// The host serves these addresses (Vercel); `next start` does not, so a local run proves only that nothing broke.
// Exit 0: no page in review is readable. Exit 1: at least one is. Exit 2: bad input, or the site did not answer.
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

/** The transport addresses of a page. "/" is "/index" in these addresses. */
export function transportOf(page) {
  const base = page === "/" ? "/index" : page.replace(/\/+$/, "");
  return [`${base}.rsc`, `${base}.segments/_tree.segment.rsc`, `${base}.segments/_full.segment.rsc`, `${base}.segments${base}/__PAGE__.segment.rsc`];
}

/** One answer read: "closed" (404 or another refusal), "curtain" (the in-review page, as page or as data), or "page"
 * (anything else that answered 200: the page's own content). `matched` is the host's X-Matched-Path, when it sends one. */
export function reading({ status, matched, body }) {
  if (status !== 200) return "closed";
  const m = (matched ?? "").toLowerCase();
  if (m === "/in-review" || m.startsWith("/in-review.")) return "curtain";
  // a host that names no matched path: the in-review page's data names its own segment and its query
  if (!m && /"in-review"|\?path=%2F|data-in-review/.test(body ?? "")) return "curtain";
  return "page";
}

/** The verdict for a page in review, from its own reading and its transport addresses' readings. */
export function verdict(own, transports) {
  const open = transports.filter((t) => t.reading === "page");
  if (own === "page") return { ok: true, live: true, open: [] };       // the page is live: its data may be read
  return { ok: open.length === 0, live: false, open: open.map((t) => t.address) };
}

export const PAGES = ["/", "/about", "/terms", "/cost-of-power/battery", "/cost-of-power", "/learn", "/digest", "/data"];

async function get(origin, address) {
  const res = await fetch(new URL(address, origin), { redirect: "manual", headers: { "user-agent": "node" } });
  const body = res.status === 200 ? (await res.text()).slice(0, 200_000) : "";
  return { status: res.status, matched: res.headers.get("x-matched-path"), body };
}

async function main(argv) {
  const origin = argv[0];
  if (!origin || !/^https?:\/\//.test(origin)) {
    console.error("usage: node scripts/check-curtain.mjs <origin>   (for example https://erw-flame.vercel.app)");
    return 2;
  }
  const pages = argv.length > 1 ? argv.slice(1) : PAGES;
  let bad = 0, read = 0;
  for (const page of pages) {
    let own, transports;
    try {
      own = reading(await get(origin, page));
      transports = [];
      for (const address of transportOf(page)) {
        const a = await get(origin, address);
        transports.push({ address, status: a.status, reading: reading(a) });
        read += 1;
      }
    } catch (e) {
      console.error(`could not read ${page}: ${e.message}`);
      return 2;
    }
    const v = verdict(own, transports);
    const line = transports.map((t) => `${t.status} ${t.reading}`).join(", ");
    if (v.live) console.log(`live     ${page}: the page is open to visitors, so its data is (${line})`);
    else if (v.ok) console.log(`ok       ${page}: ${own} at its own address; its transport addresses: ${line}`);
    else {
      bad += 1;
      console.log(`READABLE ${page}: in review, and a visitor is answered the page at ${v.open.join(" and ")}`);
    }
  }
  console.log(bad ? `\n${bad} of ${pages.length} pages in review can be read by a visitor` : `\nno page in review is readable at a transport address (${pages.length} pages, ${read} addresses)`);
  return bad ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  process.exit(await main(process.argv.slice(2)));
}
export const here = fileURLToPath(import.meta.url);
