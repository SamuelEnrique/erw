// Session 583: the window at the place of each visible fix, at 1280 and 390, in the Chrome that chrome-583.mjs opened
// with the internal view (its DevTools port). One PNG a place and width, named <place>_<width>_<tag>.png.
//   node docs/brand/review-583/shots-583.mjs <base> <port> <out-dir> <tag>
import fs from "node:fs";
import path from "node:path";
const [base, port, outDir, tag] = process.argv.slice(2);
const dev = `http://127.0.0.1:${port}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// each place: its address and the link the fix draws (found by its words), brought to the middle of the window
const PLACES = [
  { name: "grid-ercot-neighbour", addr: "/grid/ercot", text: "Each neighbour" },
  { name: "grid-ercot-datacenters", addr: "/grid/ercot", text: "All datacenters" },
  { name: "event-method", addr: "/events/caiso-heat-2020", text: "Method" },
  { name: "exchange-grid-page", addr: "/grid?grid=ercot&view=exchange", text: "ERCOT's grid page" },
];
fs.mkdirSync(outDir, { recursive: true });
let failed = 0;
for (const p of PLACES) for (const w of [1280, 390]) {
  const t = await (await fetch(`${dev}/json/new?about:blank`, { method: "PUT" })).json();
  const sock = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((r) => { sock.onopen = r; });
  let id = 0, loads = 0; const wait = new Map();
  sock.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait.has(d.id)) { wait.get(d.id)(d.result); wait.delete(d.id); } if (d.method === "Page.loadEventFired") loads += 1; };
  const send = (method, params = {}) => new Promise((r) => { id += 1; wait.set(id, r); sock.send(JSON.stringify({ id, method, params })); });
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: w, height: w < 600 ? 844 : 900, deviceScaleFactor: 1, mobile: w < 600 });
  const b = loads; await send("Page.navigate", { url: base + p.addr });
  for (let i = 0; i < 600 && loads === b; i += 1) await sleep(100);
  await sleep(2500);
  const found = (await send("Runtime.evaluate", { returnByValue: true, expression: `(() => { const a = [...document.querySelectorAll("main a")].find((x) => x.textContent.trim() === ${JSON.stringify(p.text)}); if (!a) return false; a.scrollIntoView({ block: "center" }); return true; })()` }))?.result?.value;
  await sleep(500);
  const shot = await send("Page.captureScreenshot", { format: "png" });
  const file = path.join(outDir, `${p.name}_${w}_${tag}.png`);
  fs.writeFileSync(file, Buffer.from(shot.data, "base64"));
  console.log(`${file}: ${found ? "at the link" : "LINK NOT FOUND"}`);
  if (!found) failed += 1;
  sock.close(); await fetch(`${dev}/json/close/${t.id}`);
}
process.exit(failed ? 1 : 0);
