// Energy Research Warehouse (ERW) site, session 2200 (chain 086): the test of scripts/check-explorers.mjs.
//
//   node scripts/test-check-explorers.mjs                      the judging, on fixtures (no browser, no request)
//   CHECK_EXPLORERS_BROWSER_TEST=1 node scripts/...            and a fixture page read end to end in the machine's browser
//
// The fixture page, served in this process on a free port of 127.0.0.1, holds two figures (one with its source in its
// title, one with a Tip beside it, one with neither), two charts (one that draws a card with a figure on pointer move,
// one that draws nothing; session 2201: a bar chart whose wrapper draws the card) and a table wider than a phone. No request leaves the machine. Exit 0 when every case is
// judged as it should be.
import http from "node:http";
import { judge, readPage, PHONE } from "./check-explorers.mjs";
import { withBrowser } from "./browser.mjs";

let bad = 0, n = 0;
const ok = (cond, what) => { n += 1; if (!cond) bad += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); };

// 1. the judging on readings
const reading = {
  tips: [
    { key: "series|t|e|v|2025-01-01T00:00:00Z", title: "t: e, v, 2025. Source: a report.", tip: false },
    { key: "series|t|e|w|2025-01-01T00:00:00Z", title: "", tip: true },
    { key: "series|t|e|x|2025-01-01T00:00:00Z", title: "", tip: false },
  ],
  charts: [{ i: 0, kind: "svg:box", id: "a" }, { i: 1, kind: "time:lines", id: "b" }, { i: 2, kind: "bars", id: "c" }],
};
const f = judge("/explore/x", reading, [{ card: true, figure: true }, { card: false, figure: false }, { card: true, figure: false }], { scrollWidth: 402, clientWidth: 390 });
ok(f.filter((x) => x.kind === "tip").length === 1 && f.find((x) => x.kind === "tip").what.endsWith("|x|2025-01-01T00:00:00Z"), "the figure with no title and no tip is the one tip finding");
ok(f.filter((x) => x.kind === "hover").length === 2, "the chart with no card and the chart whose card names no figure are the two hover findings");
ok(f.find((x) => x.kind === "hover" && x.what === "time:lines b")?.why.startsWith("no hover card"), "the chart with no card is named with its kind and id");
ok(f.filter((x) => x.kind === "width").length === 1 && f.find((x) => x.kind === "width").what === "402 px", "a page wider than 390 as a phone is the one width finding");
ok(judge("/explore/y", { tips: [], charts: [] }, [], { scrollWidth: 390, clientWidth: 390 }).length === 0, "a page with nothing to find has no finding");
ok(PHONE.width === 390 && PHONE.height === 844, "the phone is 390 by 844");

// 2. the fixture page in the browser
if (process.env.CHECK_EXPLORERS_BROWSER_TEST === "1") {
  const page = `<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{margin:0;padding:8px}.card{position:absolute;border:1px solid #ccc}</style></head><body>
<p><span data-check="series|t|e|v|2025-01-01T00:00:00Z" data-raw="1" title="t: e, v, 2025. Source: a report.">1.00</span>
<span data-tip="k"><span data-check="series|t|e|w|2025-01-01T00:00:00Z" data-raw="2">2.00</span><button type="button">i</button></span>
<span data-check="series|t|e|x|2025-01-01T00:00:00Z" data-raw="3">3.00</span></p>
<div data-chart="a" data-svg-chart="box" style="position:relative;width:600px"><svg width="600" height="200" role="img" aria-label="a"><rect width="600" height="200" fill="#eee"/></svg></div>
<div data-time-chart="lines" style="position:relative;width:600px"><svg width="600" height="200" role="img" aria-label="b"><rect width="600" height="200" fill="#ddd"/></svg></div>
<div data-bars-hover="c" style="position:relative;width:600px"><svg data-bars="c" width="600" height="200" role="img" aria-label="c"><rect width="600" height="200" fill="#ccc"/></svg></div>
<table style="width:600px"><tr><td>wide</td></tr></table>
<script>
const a = document.querySelector('[data-chart="a"]');
a.addEventListener("mousemove", () => { if (!a.querySelector("[data-chart-card]")) { const c = document.createElement("div"); c.setAttribute("data-chart-card", "1"); c.className = "card"; c.textContent = "2025: 12.5 USD/MWh"; a.appendChild(c); } });
const w = document.querySelector('[data-bars-hover="c"]');
w.addEventListener("mousemove", () => { if (!w.querySelector("[data-chart-card]")) { const c = document.createElement("div"); c.setAttribute("data-chart-card", "1"); c.className = "card"; c.textContent = "2024: +3.2 percent"; w.appendChild(c); } });
</script></body></html>`;
  const server = http.createServer((req, res) => { res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }); res.end(page); });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    const got = await withBrowser(async (h) => readPage(h, base, "/"));
    if (got === null) {
      console.log("skip the browser part: no Chrome or Edge on this machine");
    } else {
      const fx = judge("/", got.reading, got.hovers, got.phone);
      console.log(`     read: ${JSON.stringify({ charts: got.reading.charts, hovers: got.hovers, phone: got.phone })}`);
      ok(got.reading.tips.length === 3, `three figures read (${got.reading.tips.length})`);
      ok(got.reading.charts.length === 3, `three charts read (${got.reading.charts.length})`);
      ok(got.hovers[0]?.card === true && got.hovers[0]?.figure === true, "the chart that draws a card on pointer move is seen to");
      ok(got.hovers[1]?.card === false, "the chart that draws nothing is seen not to");
      ok(got.hovers[2]?.card === true && got.hovers[2]?.figure === true && got.reading.charts[2].kind === "bars", "the bar chart's card, drawn by its wrapper, is seen (session 2201)");
      ok(fx.some((x) => x.kind === "tip" && x.what.includes("|x|")), "the figure with neither title nor tip is found in the browser");
      ok(fx.some((x) => x.kind === "hover" && x.what.startsWith("time:lines")), "the chart with no card is found in the browser");
      ok(got.phone.scrollWidth > 390 && fx.some((x) => x.kind === "width"), `the 600 px table makes the page wider than a phone (${got.phone.scrollWidth} px)`);
    }
  } finally {
    server.close();
  }
}

console.log(`${n - bad} of ${n} passed`);
process.exit(bad ? 1 : 0);
