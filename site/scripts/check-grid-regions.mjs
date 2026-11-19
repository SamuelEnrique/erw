// Energy Research Warehouse (ERW) site, session 8602 (chain 504, 19 November 2026): the thirteen regions in the Grid
// tool, in a real browser.
//
//   npm run build && npx next start -p 3504
//   node scripts/check-grid-regions.mjs [base-url] [screenshot-folder]        (default http://localhost:3504)
//
// The page is in review, so every check is made in the internal view. No model call; the only requests are to the site
// under test. What the pages should hold is read here from the same files the server reads (data/regions/, the data
// machine's: docs/state/page_files_regions.md), so the check stands whatever those files hold on the day:
//   absent    with no index on the site: the tool says the regions are not built yet and is otherwise as it was
//   picker    the index's regions under the grids, none chosen; a region chosen is in the address and in the title
//   mix       the latest hour's figures are the file's; the hours, the average day and the years are drawn; a month
//             chosen is in the address; the shares are the file's; every part not held is blank with a reason on hover
//   trade     one row a neighbour with the file's megawatt-hours; a month one side did not report is blank, not zero
//   network   the region's balancing authorities as links; one opens its panel, whose region line opens the region
//   clean     the three parts, each blank with its reason
//   no file   a region whose file is not on the site says so and draws no figure
//   alike     a region beside the grid it nearly is: the hover carries the file's own sentence
//   the map   a region's hover on the map names its EIA region
//   phone     at 390 px nothing scrolls sideways; a wide table scrolls inside its own frame
// Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "./browser.mjs";
import { ALIKE, latestHour, newestTradeMonth, readAlike, readIndex, readMix, readTrade, regionHref, tradeMonth, whySentence } from "../lib/gridregions.ts";

const base = (process.argv[2] ?? "http://localhost:3504").replace(/\/$/, "");
const shots = process.argv[3] ?? null;
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const dir = new URL("../data/regions/", import.meta.url);
const json = (rel) => { try { return JSON.parse(fs.readFileSync(new URL(rel, dir), "utf-8")); } catch { return null; } };
const whole = (v) => Math.round(v).toLocaleString("en-US");
const index = readIndex(json("index.json"));
const READY = `!!document.querySelector('[data-grid-tool]')`;
const WIDE = `document.documentElement.scrollWidth <= window.innerWidth`;

const code = await withBrowser(async ({ go, evaluate, wait, unlock, sleep, send, errors }) => {
  const shot = async (name) => {
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    const h = await evaluate(`Math.min(document.documentElement.scrollHeight, 5200)`), w = await evaluate(`window.innerWidth`);
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: w < 500 });
    await sleep(400);
    fs.writeFileSync(path.join(shots, name), Buffer.from((await send("Page.captureScreenshot", { format: "png" })).data, "base64"));
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: w < 500 ? 844 : 900, deviceScaleFactor: 1, mobile: w < 500 });
    console.log(`     ${path.join(shots, name)}`);
  };
  const open = async (url) => { await go(`${base}${url}`); await wait(READY, 30000, "the tool"); await sleep(900); };
  await unlock(base);
  await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });

  await open("/grid");
  const top = await evaluate(`({ tool: document.querySelector('[data-grid-tool]').getAttribute('data-grid-tool'), grids: [...document.querySelectorAll('[data-segments="Grid"] a')].map((a) => a.innerText.trim()), gridOn: document.querySelector('[data-segments="Grid"] [aria-current="page"]')?.innerText.trim() ?? null,
    picker: document.querySelector('[data-region-picker]')?.getAttribute('data-region-picker') ?? null, regions: [...document.querySelectorAll('[data-segments="EIA region"] a')].map((a) => [a.innerText.trim(), a.getAttribute('href'), a.getAttribute('title') || '']),
    regionOn: document.querySelector('[data-segments="EIA region"] [aria-current="page"]')?.innerText.trim() ?? null, absent: document.querySelector('[data-region-picker="absent"]')?.innerText ?? null, absentTip: document.querySelector('[data-region-picker="absent"] [data-missing]')?.getAttribute('title') ?? null })`);
  check(top.tool === "us48" && top.grids.join(",") === "ERCOT,CAISO,PJM,MISO,NYISO,ISO-NE,SPP,US48" && top.gridOn === "US48", `the tool opens on the Lower 48 with its eight grids, as before (${top.grids.join(", ")}; ${top.gridOn} chosen)`);
  if (!index) {
    check(top.picker === "absent" && /not built yet/.test(top.absent ?? "") && /index\.json/.test(top.absentTip ?? "") && top.regions.length === 0, `the site holds no index of the regions: the row says "not built yet", its hover names the file, and no region can be chosen`);
    await shot("grid_regions_not_built_yet_1280.png");
    await open("/grid?region=se");
    check((await evaluate(`document.querySelector('[data-grid-tool]').getAttribute('data-grid-tool')`)) === "us48", "an address that names a region opens the tool as it was, the Lower 48");
    await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    await open("/grid");
    check(await evaluate(WIDE), `at 390 px the tool with the row is ${await evaluate(`document.documentElement.scrollWidth`)} px wide`);
    await shot("grid_regions_not_built_yet_390.png");
    console.log("     the rest is not proven here: data/regions/index.json is not on this build");
    return bad ? 1 : 0;
  }
  check(top.picker === String(index.regions.length) && top.regions.map((r) => r[0]).join("|") === index.regions.map((r) => r.name).join("|") && top.regionOn === null && top.regions.every((r, i) => r[1] === regionHref(index.regions[i].code, "mix")),
    `under the grids, the index's ${index.regions.length} regions in its order, none chosen, each a link to its own address (${top.regions.map((r) => r[0]).join(", ")})`);
  check(top.regions.every((r, i) => r[2].includes(index.regions[i].code) && index.regions[i].bas.every((b) => r[2].includes(b))), "each region's hover gives its code and every balancing authority EIA places in it");
  await shot("grid_us48_with_regions_1280.png");

  // a region with a mix file on the site, one of the six never drawn before when there is one
  const held = index.regions.filter((r) => readMix(json(`mix/${r.code.toLowerCase()}.json`)));
  const pick = held.find((r) => ["SE", "FLA", "CAR", "TEN", "NW", "SW"].includes(r.code)) ?? held[0];
  if (!pick) console.log("     the Mix tab of a region is not proven here: no mix file is on this build");
  else {
    const slug = pick.code.toLowerCase(), mixFile = readMix(json(`mix/${slug}.json`)), now = latestHour(mixFile);
    await evaluate(`[...document.querySelectorAll('[data-segments="EIA region"] a')].find((a) => a.innerText.trim() === ${JSON.stringify(pick.name)}).click()`);
    await wait(`document.querySelector('[data-grid-tool]')?.getAttribute('data-grid-region') === '${pick.code}'`, 30000, "the region");
    await sleep(900);
    const s = await evaluate(`({ search: window.location.search, h1: document.querySelector('h1').innerText, on: document.querySelector('[data-segments="EIA region"] [aria-current="page"]')?.innerText.trim(), gridOn: document.querySelector('[data-segments="Grid"] [aria-current="page"]')?.innerText ?? null,
      tabs: [...document.querySelectorAll('[data-tabs] a')].map((a) => [a.innerText.trim(), a.getAttribute('href')]), tab: document.querySelector('[data-tabs] [aria-current="page"]')?.innerText.trim(), title: document.title })`);
    check(s.search === `?region=${slug}` && s.h1.startsWith(pick.name) && s.on === pick.name && s.gridOn === null && s.tab === "Mix" && s.tabs.length === 4 && s.tabs.every((t) => t[1].includes(`region=${slug}`)) && s.title.includes(pick.name),
      `a region chosen is in the address (${s.search}), in the title ("${s.h1}") and in the picker, with the tool's four tabs`);
    const fig = await evaluate(`({ now: document.querySelector('[data-region-now]')?.getAttribute('data-region-now') ?? null, figures: Object.fromEntries([...document.querySelectorAll('[data-region-figure]')].map((e) => [e.getAttribute('data-region-figure'), e.innerText.replace(/\\s+/g, ' ').trim()])),
      rows: [...document.querySelectorAll('[data-region-table="now"] tbody tr')].map((r) => [...r.children].map((c) => c.innerText.trim())), svgs: document.querySelectorAll('[data-region-view="mix"] svg').length, hours: Number(document.querySelector('[data-region-hours]')?.getAttribute('data-region-hours') ?? 0),
      period: document.querySelector('[data-region-view]').getAttribute('data-region-period'), shares: [...document.querySelectorAll('[data-region-table="shares"] tbody tr')].map((r) => [...r.children].map((c) => c.innerText.trim())),
      rest: [...document.querySelectorAll('[data-region-table="rest"] tbody tr')].map((r) => ({ part: r.children[0].innerText.trim(), words: r.querySelector('[data-missing]')?.innerText ?? null, why: r.querySelector('[data-missing]')?.getAttribute('title') ?? '' })) })`);
    if (now) {
      const want = (v, sign) => (v === null ? "not held" : `${sign && v > 0 ? "+" : sign && v < 0 ? "-" : ""}${whole(Math.abs(sign ? v : v))} MW`);
      check(fig.now === now.ts && fig.figures["Demand"] === want(now.demand) && fig.figures["Net generation"] === want(now.net_generation) && fig.figures["Net imports"] === want(now.net_imports, true),
        `the latest hour held is the file's (${now.ts}): demand ${fig.figures["Demand"]}, net generation ${fig.figures["Net generation"]}, net imports ${fig.figures["Net imports"]}`);
      check(fig.rows.length === 8 && now.sources.every((x, i) => fig.rows[i][1] === (x.mw === null ? "not held" : whole(x.mw))), `the eight sources of that hour carry the file's megawatts (${fig.rows.map((r) => `${r[0]} ${r[1]}`).join(", ")})`);
      check(fig.hours === Math.min(mixFile.hourly.hours.n, 35 * 24), `the last days are drawn hour by hour (${fig.hours} hours)`);
    } else check(/not held/.test(await evaluate(`document.querySelector('#now').innerText`)), "the file carries no hourly part, and the block says so");
    const p = mixFile.months[fig.period];
    const top3 = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"].map((k) => [k, Number(p?.[`${k}_share_pct`] ?? 0)]).sort((a, b) => b[1] - a[1])[0];
    check(fig.period === mixFile.upto && fig.svgs >= 3 && !!p && fig.shares[0][1] === `${top3[1].toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`,
      `the tab opens on the file's newest month (${fig.period}), with the hours, the average day and the years drawn; the largest share is the file's (${fig.shares[0][0]} ${fig.shares[0][1]})`);
    check(fig.rest.length === 7 && fig.rest.every((r) => r.words === "not held for this region" && r.why.length > 40), `the seven parts of a grid's tab that the region's file does not hold are drawn, blank, each with its reason on hover (${fig.rest.map((r) => r.part).slice(0, 3).join("; ")}; ...)`);
    // the charts answer the mouse
    const c = await evaluate(`(() => { const s = document.querySelector('#day svg'); s.scrollIntoView({ block: 'center' }); const b = s.getBoundingClientRect(); return { x: b.left + b.width * 0.4, y: b.top + b.height * 0.5 }; })()`);
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: c.x, y: c.y });
    await sleep(400);
    const card = await evaluate(`(() => { const d = document.querySelector('#day'); const t = [...d.querySelectorAll('div')].filter((e) => /Natural gas|Demand/.test(e.innerText) && /MW/.test(e.innerText) && /\\d\\d:00/.test(e.innerText)).sort((a, b) => a.innerText.length - b.innerText.length)[0]; return t ? t.innerText.replace(/\\s+/g, ' ').slice(0, 160) : null; })()`);
    check(!!card, `the average day's chart answers the mouse with the hour and each source's megawatts (${card ?? "no card"})`);
    // a month chosen is in the address
    const other = Object.keys(mixFile.months).sort().reverse()[1];
    if (other) {
      await evaluate(`document.querySelector('[data-chip="Month:${other}"]').click()`);
      await wait(`document.querySelector('[data-region-view]')?.getAttribute('data-region-period') === '${other}'`, 20000, "the other month");
      check((await evaluate(`window.location.search`)) === `?region=${slug}&period=${other}`, `a month chosen is in the address (?region=${slug}&period=${other}) and the tab draws it`);
    }
    await open(`/grid?region=${slug}`);
    await shot(`region_${slug}_mix_1280.png`);

    // trade
    const trade = readTrade(json(`trade/${slug}.json`));
    await open(`/grid?region=${slug}&view=gravity`);
    if (!trade) check(/not built yet/.test(await evaluate(`document.querySelector('[data-region-view]').innerText`)), "the region's trade file is not on the site, and the tab says so");
    else {
      const month = newestTradeMonth(trade), m = tradeMonth(trade, month);
      const t = await evaluate(`({ month: document.querySelector('[data-region-view]').getAttribute('data-region-month'), rows: [...document.querySelectorAll('[data-region-table="trade"] tbody tr')].map((r) => [...r.children].map((c) => c.innerText.replace(/\\s+/g, ' ').trim())), heads: [...document.querySelectorAll('[data-region-table="trade"] thead [title]')].length })`);
      const mwh = (v) => (v === null ? "not held" : `${v > 0 ? "+" : v < 0 ? "-" : ""}${whole(Math.abs(v))}`);
      check(t.month === month && t.rows.length === m.rows.length + 1 && m.rows.every((r, i) => t.rows[i][0].endsWith(r.code) && t.rows[i][1] === mwh(r.own) && t.rows[i][2] === mwh(r.theirs) && t.rows[i][3] === mwh(r.gap)) && t.rows[m.rows.length][1] === mwh(m.total) && t.heads === 4,
        `the trade of ${month}: one row a neighbour with the file's own report, the neighbour's and the gap (${t.rows.slice(0, 3).map((r) => `${r[0]} ${r[1]}`).join("; ")}), a figure not held blank, never zero; every column head says its rule on hover`);
      await shot(`region_${slug}_trade_1280.png`);
    }

    // network: the region's authorities, one opened, and back to the region from its panel
    await open(`/grid?region=${slug}&view=network`);
    const bas = await evaluate(`[...document.querySelectorAll('[data-region-ba]')].map((a) => [a.getAttribute('data-region-ba'), a.getAttribute('href')])`);
    check(bas.map((b) => b[0]).join(",") === pick.bas.join(",") && (await evaluate(`!!document.querySelector('[data-grid-network]') && !document.querySelector('[data-panel]')`)), `the Network tab lists the region's ${pick.bas.length} balancing authorities over the network, no panel open (${pick.bas.join(", ")})`);
    const snap = JSON.parse(fs.readFileSync(new URL("../data/grid_network.json", import.meta.url), "utf-8"));
    const one = pick.bas.find((b) => snap.nodes.some((x) => x.id === b));
    if (one) {
      await evaluate(`document.querySelector('[data-region-ba="${one}"]').click()`);
      const pr = await wait(`(() => { const p = document.querySelector('[data-panel="${one}"]'); const r = p?.querySelector('[data-panel-region]'); return p ? { region: r?.getAttribute('data-panel-region') ?? null, href: r?.querySelector('a')?.getAttribute('href') ?? null, search: window.location.search } : null; })()`, 30000, "the authority's panel");
      check(pr.region === pick.code && pr.href === `/grid?region=${slug}` && pr.search.includes(`region=${slug}`) && pr.search.includes(`node=${one}`), `a click on ${one} opens its panel in the network, with the region still in the address; the panel's line "EIA region" opens the region (${pr.href})`);
      await shot(`region_${slug}_network_1280.png`);
    }
    // clean
    await open(`/grid?region=${slug}&view=clean`);
    const cl = await evaluate(`[...document.querySelectorAll('[data-region-table="clean"] [data-missing]')].map((e) => e.getAttribute('title') || '')`);
    check(cl.length === 3 && cl.every((w) => w.length > 30), "the Clean tab draws its three parts blank for a region, each with its reason on hover");

    // phone
    await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    await open(`/grid?region=${slug}`);
    const ph = await evaluate(`({ wide: ${WIDE}, scroll: document.documentElement.scrollWidth, frames: [...document.querySelectorAll('[data-region-table]')].map((f) => [f.getAttribute('data-region-table'), f.scrollWidth, f.clientWidth]), picker: [...document.querySelectorAll('[data-segments="EIA region"] a')].every((a) => { const b = a.getBoundingClientRect(); return b.left >= 0 && b.right <= 391; }) })`);
    check(ph.wide && ph.picker, `at 390 px the region's Mix tab is ${ph.scroll} px wide, the picker's thirteen inside the screen; a wide table scrolls in its own frame (${ph.frames.filter((f) => f[1] > f[2]).map((f) => `${f[0]} ${f[1]} in ${f[2]}`).join(", ") || "none is wider than its frame"})`);
    await shot(`region_${slug}_mix_390.png`);
    await open(`/grid?region=${slug}&view=gravity`);
    check(await evaluate(WIDE), `at 390 px the region's trade is ${await evaluate(`document.documentElement.scrollWidth`)} px wide`);
    await shot(`region_${slug}_trade_390.png`);
    await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  }

  // a region whose mix file is not on the site
  const none = index.regions.find((r) => !readMix(json(`mix/${r.code.toLowerCase()}.json`)));
  if (none) {
    await open(`/grid?region=${none.code.toLowerCase()}`);
    const a = await evaluate(`({ state: document.querySelector('[data-region-view]')?.getAttribute('data-region-mix'), words: document.querySelector('[data-region-view] [data-missing]')?.innerText ?? null, why: document.querySelector('[data-region-view] [data-missing]')?.getAttribute('title') ?? '', digits: (document.querySelector('[data-region-view]').innerText.match(/\\d/g) || []).length })`);
    check(a.state === "absent" && a.words === "not built yet" && a.why.includes(`mix/${none.code.toLowerCase()}.json`) && a.digits === 0, `${none.name}'s mix file is not on the site: the tab says "not built yet", its hover names the file, and no figure is drawn`);
  }
  // a region beside the grid it nearly is
  for (const [codeA, g] of Object.entries(ALIKE)) {
    const alike = readAlike(json(`demand/${codeA.toLowerCase()}.json`));
    if (!alike) continue;
    await open("/grid");
    const title = await evaluate(`document.querySelector('[data-segments="EIA region"] [data-segment="${codeA.toLowerCase()}"]')?.getAttribute('title') ?? ''`);
    check(title.includes(`Beside ${g.grid}: ${whySentence(alike)}`), `${codeA}'s hover says, in the data machine's own sentence, why it and ${g.grid} differ ("${whySentence(alike).slice(0, 90)}")`);
    break;
  }
  // the map's hover names the region
  await open("/grid?view=network&shape=map");
  await wait(`document.querySelector('[data-map-state]')?.getAttribute('data-map-state') === 'held'`, 30000, "the map");
  await evaluate(`window.scrollTo(0, Math.max(0, document.querySelector('[data-shape-toggle]').getBoundingClientRect().top + window.scrollY - 8))`);
  await sleep(400);
  const ba = index.bas.find((b) => b.code === "ERCO") ?? index.bas[0];
  const pt = await evaluate(`(() => { const e = document.querySelector('[data-region="${ba.code}"]'); if (!e) return null; const b = e.getBoundingClientRect(); for (let i = 1; i < 24; i += 1) for (let j = 1; j < 24; j += 1) { const x = b.left + (b.width * i) / 24, y = b.top + (b.height * j) / 24; if (document.elementFromPoint(x, y) === e) return { x, y }; } return null; })()`);
  if (pt) {
    // a point of the region away from its ties, so the region answers
    let said = null;
    for (const d of [[0, 0], [14, 9], [-14, 9], [9, -14], [22, 16]]) {
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: pt.x + d[0], y: pt.y + d[1] });
      await sleep(200);
      said = await evaluate(`document.querySelector('[data-map-hover="${ba.code}"]')?.innerText ?? null`);
      if (said) break;
    }
    const name = index.regions.find((r) => r.code === ba.region)?.name;
    check(!!said && said.includes(`EIA region: ${name}`), `on the map, the hover of ${ba.code} names its EIA region (${name})`);
  }
  check(errors.length === 0, `no error in the pages${errors.length ? `: ${errors.slice(0, 2).join("; ")}` : ""}`);
  return bad ? 1 : 0;
});
if (code === null) { console.log("not proven here: no browser on this machine"); process.exit(0); }
console.log(`${n} checks, ${bad} failed`);
process.exit(code === 0 && !bad ? 0 : 1);
