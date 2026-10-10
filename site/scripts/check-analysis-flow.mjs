// Energy Research Warehouse (ERW) site, session 182, part 4: the request flow of /analysis in a real browser.
//
//   npm run build && npx next start -p 3183
//   node scripts/check-analysis-flow.mjs [base-url]                    (default http://localhost:3183)
//   node scripts/check-analysis-flow.mjs [base-url] --stub 54381       also the queue, against the local stand-in
//       (the server then started with SUPABASE_URL=http://localhost:54381 SUPABASE_ANON_KEY=local, as
//        scripts/check-internal-findings.mjs says; without --stub no request is queued, so production is never written)
//
//   step one   the list holds every analysis of the catalogue and all ten templates (7 findings, the impact study, 10
//              templates); picking an analysis shows its inputs, a version where it has two, the impact study's own form
//   step two   the forms that fit are drawn as examples (one canvas a tile), the default is preselected and labeled
//              "Default for this analysis", Previous and Next flip, the choice lands in the address and survives a reload
//   a card     a computed card shown in the flow and on its own page is re-drawn in every other form with the same
//              numbers (read from the drawn chart, against the card's JSON); hover shows a tooltip in every form
//   templates  each of the nine public templates is reachable and drawn, in each of its forms with the weekly file's
//              data; its inputs are the gallery's; a choice the weekly run could not compute says so; the internal
//              tenth is listed with its inputs and is not drawn
//   the page   the two superseded cards left the list and are linked; the old sections are gone; no word of advice
//   phone      at 390 px nothing scrolls sideways, the tiles stand two to a row, every press target is 44 px high
//   queue      (--stub) a request is queued from the flow, kept in the address and in the list; a done request opened
//              by its address is drawn in the chosen form with the committed card's numbers
// Exit 1 on a failure; 2 when no browser is on the machine.
import fs from "node:fs";
import path from "node:path";
import { register } from "node:module";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

register("./alias-loader.mjs", import.meta.url);
const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const F = await import("../lib/chartforms.ts");
const A = await import("../lib/analysisflow.ts");

const args = process.argv.slice(2);
const base = (args.find((a) => a.startsWith("http")) ?? "http://localhost:3183").replace(/\/$/, "");
const stubPort = args.includes("--stub") ? Number(args[args.indexOf("--stub") + 1]) : 0;
const read = (...p) => JSON.parse(fs.readFileSync(path.join(...p), "utf-8"));
const dir = path.join(site, "data", "findings");
const catalogue = read(dir, "catalogue.json");
const card = (id) => read(dir, `${id}.json`);
const docs = path.join(site, "..", "docs", "analysis");
const templates = read(docs, "templates.json").templates;
const gallery = read(docs, "gallery", "index.json").templates;
const items = A.flowList(catalogue, templates);
const allCards = fs.readdirSync(dir).filter((f) => f.endsWith(".json") && f !== "catalogue.json").map((f) => read(dir, f));

let bad = 0, n = 0;
const lines = [];
const check = (ok, what, shown = "") => { n += 1; if (!ok) bad += 1; lines.push(`${ok ? "ok  " : "FAIL"} ${what}${shown ? ` ${shown}` : ""}`); };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const q = (s) => JSON.stringify(s);

let stub = null;
if (stubPort) {
  const S = await import("./findings-stub.mjs");
  stub = { ...(await S.startStub(stubPort)), DONE_ID: S.DONE_ID };
}

let code;
try {
  code = await withBrowser(async ({ go, wait, unlock, send, sleep, errors }) => {
    const js = async (expression) => {
      const r = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
      if (r.exceptionDetails) throw new Error(`in the page: ${r.exceptionDetails.exception?.description ?? r.exceptionDetails.text}`);
      return r.result?.value;
    };
    const size = (w, h) => send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: w < 500 });
    const click = (sel) => js(`(() => { const e = document.querySelector(${q(sel)}); if (!e) return false; e.click(); return true; })()`);
    const choose = (sel, v) => js(`(() => { const e = document.querySelector(${q(sel)}); if (!e) return false; e.value = ${q(v)}; e.dispatchEvent(new Event("change", { bubbles: true })); return true; })()`);
    const picker = () => js(`(() => { const p = document.querySelector("[data-flow] [data-form-picker]"); if (!p) return null; return { chosen: p.dataset.formChosen, def: p.dataset.formDefault, offered: p.dataset.formOffered.split(","),
      tiles: [...p.querySelectorAll("[data-form-tile]")].map((t) => ({ id: t.dataset.formTile, on: t.dataset.formSelected === "1", canvas: !!t.querySelector("[data-form-example] canvas"), mark: !!t.querySelector("[data-form-default-mark]"),
        pressed: t.querySelector("button").getAttribute("aria-pressed") })), count: p.querySelector("[data-form-count]").textContent }; })()`);
    const drawnAll = (id) => wait(`(() => { const p = document.querySelector("[data-flow][data-flow-analysis='${id}'] [data-form-picker]"); return !!p && [...p.querySelectorAll("[data-form-tile]")].every((t) => t.querySelector("[data-form-example] canvas")); })()`, 20000, `the examples of ${id}`);
    // the numbers a drawn chart holds, series by series (the fitted line of a scatter and empty series left out)
    const dataOf = (sel) => js(`(() => { const el = document.querySelector(${q(sel)}); const inst = el && window.echarts.getInstanceByDom(el); if (!inst) return null;
      return inst.getOption().series.filter((s) => s.data && s.data.length).map((s) => s.data.map((d) => (d && typeof d === "object" && !Array.isArray(d) ? d.value : d))); })()`);
    const hover = (sel, at = 1) => js(`(async () => { const el = document.querySelector(${q(sel)}); const inst = el && window.echarts.getInstanceByDom(el); if (!inst) return "";
      inst.dispatchAction({ type: "showTip", seriesIndex: 0, dataIndex: ${at} }); await new Promise((r) => setTimeout(r, 250));
      const tip = [...el.querySelectorAll("div")].find((d) => /z-index/.test(d.getAttribute("style") || "") && d.innerText.trim().length > 0); return tip ? tip.innerText.replace(/\\s+/g, " ").trim() : ""; })()`);
    const address = () => js("location.search");

    await unlock(base);
    await size(1280, 900);
    await go(`${base}/analysis`);
    await wait(`!!document.querySelector("[data-flow] [data-form-picker]")`, 20000, "the flow");

    // ---- step one ----
    const list = await js(`[...document.querySelectorAll("[data-flow-pick]")].map((e) => ({ id: e.dataset.flowPick, group: e.closest("[data-flow-group]").dataset.flowGroup, name: e.textContent.trim(), h: Math.round(e.getBoundingClientRect().height) }))`);
    check(same(list.map((i) => i.id), items.map((i) => i.id)), `step one lists the ${items.length} entries of the flow, in order`, `(${list.length})`);
    const count = (g) => list.filter((i) => i.group === g).length;
    check(count("findings") === 7 && count("impact") === 1 && count("templates") === 10, "7 findings, the impact study, 10 templates", `(${count("findings")}, ${count("impact")}, ${count("templates")})`);
    check(items.every((it) => list.find((l) => l.id === it.id)?.name.startsWith(it.name)), "each entry is named in plain words");
    const versionIds = items.flatMap((i) => i.versions.map((v) => v.id));
    check(catalogue.every((c) => versionIds.includes(c.id)), `every analysis of the catalogue (${catalogue.length}) is an entry or a version of one`);
    check((await address()) === "", "nothing is written into the address before a choice", `(${await address()})`);

    // ---- each finding and each version: its inputs, its forms, its default ----
    for (const it of items.filter((i) => i.group !== "templates")) {
      await click(`[data-flow-pick=${q(it.id)}]`);
      for (const v of it.versions) {
        if (it.versions.length > 1) {
          check(await choose("[data-flow-version-input]", v.id), `${it.id}: the version ${v.id} can be chosen`);
          await wait(`document.querySelector("[data-flow]").dataset.flowVersion === ${q(v.id)}`, 10000, `version ${v.id}`);
        }
        await drawnAll(it.id);
        const entry = catalogue.find((c) => c.id === v.id);
        const want = F.formsOfSpec(card(v.id).chart);
        const p = await picker();
        check(same(p.offered, want) && p.def === want[0] && p.chosen === want[0], `${v.id}: offered ${want.join(", ")}; the default ${want[0]} is preselected`, `(${p.offered.join(", ")}; chosen ${p.chosen})`);
        check(p.tiles.length === want.length && p.tiles.every((t) => t.canvas), `${v.id}: each of its ${want.length} forms is drawn as an example`);
        check(p.tiles.filter((t) => t.mark).map((t) => t.id).join() === want[0] && p.tiles.filter((t) => t.on).map((t) => t.id).join() === want[0], `${v.id}: one tile is labeled the default, and it is the pressed one`);
        if (it.id === A.IMPACT) {
          const im = await js(`(() => { const f = document.querySelector("[data-flow-impact='shown'] [data-impact-form]"); if (!f) return null; const pk = f.querySelector("[data-form-picker]"), sub = f.querySelector("[data-impact-submit]");
            return { visible: f.offsetParent !== null, inputs: [...f.querySelectorAll("[data-impact-input]")].map((e) => e.dataset.impactInput), before: !!pk && !!sub && !!(pk.compareDocumentPosition(sub) & Node.DOCUMENT_POSITION_FOLLOWING) }; })()`);
          check(im && im.visible && ["series", "control", "event", "window"].every((k) => im.inputs.includes(k)) && im.before, "the impact study shows its own inputs, then the picker, then Ask");
        } else {
          const ins = await js(`[...document.querySelectorAll("[data-flow-inputs] [data-request-input]")].map((e) => e.dataset.requestInput + "=" + e.value)`);
          check(same(ins, Object.entries(entry.inputs).map(([k, x]) => `${k}=${x.default}`)), `${v.id}: its declared inputs at their defaults`, `(${ins.join(", ")})`);
          check(await js(`!!document.querySelector("[data-flow-ask] [data-request-submit]") && !!document.querySelector("[data-flow-wait]") && !!document.querySelector("[data-flow-show='${v.id}']")`), `${v.id}: Ask, how a request waits, and the computed card of the defaults`);
        }
      }
    }
    check(await js(`document.querySelector("[data-flow-impact]").dataset.flowImpact === "shown"`) && (await click(`[data-flow-pick="gas_sets_price"]`))
      && await js(`(() => { const d = document.querySelector("[data-flow-impact]"); return d.dataset.flowImpact === "hidden" && d.offsetParent === null; })()`), "the impact study's inputs are hidden once another analysis is picked");

    // ---- step two: the toggle, the address, a reload ----
    await drawnAll("gas_sets_price");
    await click("[data-form-next]");
    let p = await picker();
    check(p.chosen === "lines" && p.count.startsWith("2 of 3"), "Next flips to the second form", `(${p.count})`);
    check(/analysis=gas_sets_price/.test(await address()) && /[?&]form=lines/.test(await address()), "the choice lands in the address", `(${await address()})`);
    await click("[data-form-prev]");
    p = await picker();
    check(p.chosen === "bars" && !/[?&]form=/.test(await address()), "Previous flips back to the default, which the address does not carry", `(${await address()})`);
    await click("[data-form-prev]");
    p = await picker();
    check(p.chosen === "multiples", "Previous from the first form goes round to the last", `(${p.chosen})`);
    check(await js(`!!document.querySelector("[data-form-reset]")`) && (await click("[data-form-reset]")) && (await picker()).chosen === "bars", "Back to the default returns to it");
    await click(`[data-form-tile-pick="lines"]`);
    await choose(`[data-flow-inputs] [data-request-input="heat_rate"]`, String(catalogue.find((c) => c.id === "gas_sets_price").inputs.heat_rate.choices.find((v) => String(v) !== String(catalogue.find((c) => c.id === "gas_sets_price").inputs.heat_rate.default))));
    const kept = await address();
    check(/form=lines/.test(kept) && /i\.heat_rate=/.test(kept), "a pressed tile and a changed input are in the address", `(${kept})`);
    await go(`${base}/analysis${kept}`);
    await drawnAll("gas_sets_price");
    p = await picker();
    const hr = await js(`document.querySelector('[data-flow-inputs] [data-request-input="heat_rate"]').value`);
    check(p.chosen === "lines" && p.def === "bars" && /heat_rate=/.test(kept) && kept.includes(`i.heat_rate=${hr}`), "after a reload the analysis, the input and the form are as chosen", `(${p.chosen}, heat rate ${hr})`);
    check(await js(`!document.querySelector("[data-flow-show]")`), "with an input off its default no computed card is offered: it needs a request");
    await click("[data-flow-reset]");
    check((await picker()).chosen === "bars" && !/i\.heat_rate|form=/.test(await address()), "Reset returns the inputs and the form to their defaults", `(${await address()})`);

    // ---- a computed card, re-drawn in every form, the same numbers ----
    for (const id of ["gas_sets_price", "queue_divorce", "batteries_curtailment_hourly"]) {
      const c = card(id);
      const it = items.find((i) => i.versions.some((v) => v.id === id));
      await click(`[data-flow-pick=${q(it.id)}]`);
      if (it.versions.length > 1) await choose("[data-flow-version-input]", id);
      await drawnAll(it.id);
      await click(`[data-flow-show=${q(id)}]`);
      const forms = F.formsOfSpec(c.chart);
      const want = c.chart.series.map((s) => s.values);
      const boxes = await js(`[...document.querySelectorAll("[data-finding-cards] [data-card='${id}'] [data-callout-before], [data-finding-cards] [data-card='${id}'] [data-callout-after]")].map((e) => e.textContent)`);
      for (const f of forms) {
        await click(`[data-form-tile-pick=${q(f)}]`);
        const sel = `[data-flow-card=${q(id)}] [data-finding-chart]`;
        await wait(`(() => { const e = document.querySelector(${q(sel)}); return !!e && !!e.querySelector("canvas") && document.querySelector("[data-flow-card] [data-form]").dataset.form === ${q(f)}; })()`, 20000, `${id} as ${f}`);
        await sleep(150);
        const got = await dataOf(sel);
        check(same(got, want), `${id}: drawn as ${f}, the chart holds the card's numbers (${want.length} series, ${want.reduce((k, s) => k + s.length, 0)} values)`);
        const now = await js(`[...document.querySelectorAll("[data-flow-card] [data-callout-before], [data-flow-card] [data-callout-after]")].map((e) => e.textContent)`);
        check(same(now, boxes) && now.length === c.callouts.length * 2, `${id}: as ${f}, its callouts are the list's (${now.length} numbers)`);
        const tip = await hover(sel);
        check(tip.length > 0 && /\d/.test(tip), `${id}: as ${f}, hover shows the values`, `(${tip.slice(0, 70)})`);
        const ex = await hover(`[data-form-tile=${q(f)}] [data-form-example]`);
        check(ex.length > 0, `${id}: the example of ${f} answers the mouse`);
      }
      check(await js(`document.querySelectorAll("[data-flow-card] [data-form-toggles]").length === 0`), `${id}: inside the flow the picker is the only control of the form`);
    }
    // on a card's own page: the toggles, the address, the same numbers
    {
      const c = card("gas_sets_price");
      const want = c.chart.series.map((s) => s.values);
      await go(`${base}/analysis/card/gas_sets_price?form=lines`);
      await wait(`!!document.querySelector('[data-form="lines"] [data-form-drawn="lines"] canvas')`, 20000, "the card page as lines");
      check(same(await dataOf(`[data-form-drawn="lines"]`), want), "/analysis/card/gas_sets_price?form=lines draws the card as lines, the same numbers");
      const tg = await js(`document.querySelector("[data-form-toggles]").dataset.formToggles`);
      check(tg === "bars,lines,multiples", "the card page carries the toggles of its forms", `(${tg})`);
      await click(`[data-form-pick="multiples"]`);
      await wait(`!!document.querySelector('[data-form-drawn="multiples"] canvas')`, 20000, "the card page as small multiples");
      check(same(await dataOf(`[data-form-drawn="multiples"]`), want) && /form=multiples/.test(await address()), "a toggle redraws it as small multiples, the same numbers, and the address follows", `(${await address()})`);
      check((await hover(`[data-form-drawn="multiples"]`)).length > 0, "hover works on the small multiples");
      await click(`[data-form-pick="bars"]`);
      await wait(`!!document.querySelector('[data-finding-chart="grouped_bar"] canvas')`, 20000, "the card page in its default form");
      check(!/form=/.test(await address()) && same(await dataOf(`[data-finding-chart="grouped_bar"]`), want), "the default form is the card's own drawing, and leaves the address");
      // a card of many grids as lines: one series a grid, the first measure
      const g = card("peak_hour_grids");
      await go(`${base}/analysis/card/peak_hour_grids?form=lines`);
      await wait(`!!document.querySelector('[data-form-drawn="lines"] canvas')`, 20000, "the five-grid card as lines");
      check(same(await dataOf(`[data-form-drawn="lines"]`), g.chart.panels.map((x) => x.values[g.chart.measures[0].key])), "the five-grid card as lines holds each grid's values of the first measure");
      await click(`[data-form-measure=${q(g.chart.measures[1].key)}]`);
      await sleep(400);
      check(same(await dataOf(`[data-form-drawn="lines"]`), g.chart.panels.map((x) => x.values[g.chart.measures[1].key])), "its measure toggle shows the second measure's values");
      await go(`${base}/analysis/card/batteries_curtailment`);
      await wait(`!!document.querySelector('[data-finding-chart="scatter"] canvas')`, 20000, "the scatter card");
      check(await js(`!document.querySelector("[data-form-toggles]")`), "a card of points offers no other form: no toggle is drawn");
      await go(`${base}/analysis/card/gas_sets_price?render=1&form=lines`);
      await wait(`!!document.querySelector('[data-finding-chart="grouped_bar"] canvas')`, 20000, "the render frame");
      check(await js(`!document.querySelector("[data-form-toggles]") && !document.querySelector("[data-form-drawn]")`), "the renderer's frame draws the default form and no toggle");
    }

    // ---- the ten templates ----
    await go(`${base}/analysis`);
    await wait(`!!document.querySelector("[data-flow] [data-form-picker]")`, 20000, "the flow");
    for (const g of gallery) {
      const id = `${A.TEMPLATE_PREFIX}${g.template}`;
      await click(`[data-flow-pick=${q(id)}]`);
      await wait(`!!document.querySelector("[data-template-chart='${g.template}'] canvas")`, 20000, `${g.template} drawn`);
      await drawnAll(id);
      const params = A.defaultParams(g);
      const file = A.comboOf(g, params).file;
      const chart = read(docs, "gallery", file);
      const forms = F.formsOfOption(chart.option);
      const seen = await js(`({ inputs: [...document.querySelectorAll("[data-flow-inputs] [data-template-input]")].map((e) => e.dataset.templateInput + "=" + e.value), title: document.querySelector("[data-template-chart] h4").textContent,
        facts: document.querySelectorAll("[data-template-facts] li").length, method: !!document.querySelector("[data-template-method]"), weekly: document.querySelector("[data-template-weekly]").textContent,
        ask: !!document.querySelector("[data-flow] [data-request-submit]"), dl: document.querySelector("[data-template-download]").getAttribute("href") })`);
      check(same(seen.inputs, Object.entries(params).map(([k, v]) => `${k}=${v}`)), `${g.template}: reachable, with the gallery's inputs at their defaults`, `(${seen.inputs.join(", ")})`);
      check(seen.title === chart.title && seen.facts === chart.facts.length && seen.method && seen.dl === `/analysis-files/gallery/${file}`, `${g.template}: its title, its ${chart.facts.length} facts, its method and its data file`);
      check(!seen.ask && /shown at once and no request is queued/.test(seen.weekly), `${g.template}: no Ask button, and the page says nothing is queued`);
      const p0 = await picker();
      check(same(p0.offered, forms) && p0.chosen === forms[0] && p0.tiles.every((t) => t.canvas), `${g.template}: offered ${forms.join(", ")}; default ${forms[0]} preselected; every form drawn as an example`, `(${p0.offered.join(", ")})`);
      const want = chart.option.series.map((s) => s.data);
      for (const f of forms) {
        await click(`[data-form-tile-pick=${q(f)}]`);
        await wait(`document.querySelector("[data-template-chart]").dataset.templateForm === ${q(f)}`, 10000, `${g.template} as ${f}`);
        await sleep(200);
        check(same(await dataOf(`[data-template-chart] [data-form-drawn=${q(f)}]`), want), `${g.template}: drawn as ${f} with the weekly file's data`);
        const tip = await hover(`[data-template-chart] [data-form-drawn=${q(f)}]`, 0);
        check(tip.length > 0, `${g.template}: as ${f}, hover shows the values`, `(${tip.slice(0, 60)})`);
      }
    }
    // another choice of inputs, and a choice the weekly run could not compute
    await click(`[data-flow-pick="template:da_rt_spread_by_hour"]`);
    await wait(`!!document.querySelector('[data-template-chart="da_rt_spread_by_hour"] canvas')`, 20000, "da_rt_spread_by_hour");
    await choose(`[data-template-input="iso"]`, "caiso");
    await wait(`/CAISO/.test(document.querySelector("[data-template-chart] h4")?.textContent ?? "")`, 20000, "the CAISO chart");
    const hubs = await js(`({ hub: document.querySelector('[data-template-input="hub"]').value, held: [...document.querySelectorAll('[data-template-input="hub"] option')].filter((o) => !/not held/.test(o.textContent)).length, all: document.querySelectorAll('[data-template-input="hub"] option').length })`);
    const gda = gallery.find((x) => x.template === "da_rt_spread_by_hour");
    const caiso = Object.values(gda.combos).filter((c) => c.params.iso === "caiso");
    check(hubs.all === new Set(caiso.map((c) => c.params.hub)).size && hubs.held === new Set(caiso.filter((c) => c.file).map((c) => c.params.hub)).size && /i\.iso=caiso/.test(await address()),
      "a grid changes the hubs offered: every hub the gallery listed, the held ones first; the address keeps the inputs", `(${hubs.held} held of ${hubs.all}; ${await address()})`);
    const none = caiso.find((c) => !c.file);
    await choose(`[data-template-input="hub"]`, String(none.params.hub));
    await wait(`!!document.querySelector("[data-template-none]")`, 10000, "a choice that is not held");
    check(await js(`document.querySelector("[data-template-none]").textContent.includes(${q(none.reason)}) && !document.querySelector("[data-template-chart]") && !!document.querySelector("[data-form-none]")`),
      "a choice the weekly run could not compute says why, and draws nothing", `(${none.params.hub}: ${none.reason})`);
    await click(`[data-flow-pick="template:chokepoint_transits"]`);
    const inner = await js(`({ note: document.querySelector("[data-form-internal]")?.textContent ?? "", inputs: document.querySelectorAll("[data-template-internal-inputs] li").length, words: document.querySelector("[data-template-internal-inputs]")?.textContent ?? "",
      canvas: document.querySelectorAll("[data-flow] canvas").length, ask: !!document.querySelector("[data-flow] [data-request-submit]"), method: document.querySelector("[data-template-method]")?.textContent ?? "" })`);
    check(/licensed internal/.test(inner.note) && inner.inputs === 3 && /Strait of Hormuz/.test(inner.words) && inner.canvas === 0 && !inner.ask && /PortWatch/.test(inner.method),
      "the tenth template (chokepoint transits) is listed with its three inputs and its method, and is not drawn: internal", `(${inner.inputs} inputs, ${inner.canvas} canvases)`);

    // ---- the page around the flow ----
    const pg = await js(`({ heads: [...document.querySelectorAll("main h2, h2")].map((h) => h.textContent), n: Number(document.querySelector("[data-finding-cards]").dataset.findingCards), drawn: [...document.querySelectorAll("[data-finding-cards] [data-card]")].map((e) => e.dataset.card),
      links: [...document.querySelectorAll("[data-superseded]")].map((e) => e.dataset.superseded + "|" + (e.querySelector("a")?.getAttribute("href") ?? "")), text: document.body.innerText, list: !!document.querySelector('[data-request-form][data-request-list="1"]'),
      oldRow: !!document.querySelector("[data-request-finding]"), roundup: document.querySelectorAll("[data-finding-cards] [data-roundup-button]").length, toggles: document.querySelectorAll("[data-finding-cards] [data-form-toggles]").length })`);
    const sup = ["batteries_lunch", "peak_hour_moved"];
    const current = allCards.filter((c) => !sup.includes(c.id));
    check(pg.n === current.length && same([...pg.drawn].sort(), current.map((c) => c.card_id).sort()), `the list of findings draws the ${current.length} current cards; the two superseded ones left it`, `(${pg.drawn.length})`);
    check(same(pg.links.sort(), sup.map((s) => `${s}|/analysis/card/${s}`).sort()), "each superseded card is linked under its five-grid card", `(${pg.links.join(", ")})`);
    for (const h of ["Findings", "Found by the scanner", "Ask for an analysis", "Requests", "Archive: the chart of each week"]) check(pg.heads.includes(h), `the section "${h}" is on the page`);
    check(pg.heads.some((h) => h.startsWith("This week's results")), "the week's results table is on the page");
    check(!pg.heads.includes("Template gallery") && !pg.heads.includes("Ask for a finding") && !pg.heads.includes("Impact of an event on a series") && !pg.oldRow, "the three old sections are gone: one flow holds them");
    check(pg.list && pg.roundup === current.length, `the list of requests stands under the flow; Use in Roundup is on each of the ${current.length} cards`, `(${pg.roundup})`);
    check(pg.toggles === current.filter((c) => F.formsOfSpec(c.chart).length > 1).length, "each card of the list with more than one form carries its toggles", `(${pg.toggles})`);
    check(/Default for this analysis/.test(await js(`(() => { document.querySelector('[data-flow-pick="gas_sets_price"]').click(); return new Promise((r) => setTimeout(() => r(document.body.innerText), 300)); })()`)), "the preselected form is labeled Default for this analysis");
    check(!/recommend|you should|we suggest|best form|better form/i.test(pg.text), "no word of advice on the page");
    check(!/claude-[a-z]+-\d/.test(pg.text) && !pg.text.includes(String.fromCharCode(0x2014)), "no model name and no em dash on the page");
    for (const s of sup) {
      await go(`${base}/analysis/card/${s}`);
      check(await js(`!!document.querySelector("[data-card='${s}']")`), `the superseded card ${s} is drawn at its own address`);
    }

    // ---- a phone ----
    await size(390, 844);
    for (const [addr, sel] of [["/analysis", "[data-flow] [data-form-picker]"], ["/analysis?analysis=gas_sets_price&form=lines", "[data-flow] [data-form-picker]"], ["/analysis?analysis=template:deals_by_month", "[data-template-chart] canvas"],
      ["/analysis?analysis=impact_study", "[data-flow-impact='shown'] [data-form-picker]"], ["/analysis/card/peak_hour_grids?form=bars", "[data-form-drawn='bars'] canvas"]]) {
      await go(`${base}${addr}`);
      await wait(`!!document.querySelector(${q(sel)})`, 20000, `${addr} at 390 px`);
      await sleep(600);
      const w = await js(`(() => { const tiles = [...document.querySelectorAll("[data-flow] [data-form-tile]")].map((t) => { const r = t.getBoundingClientRect(), b = t.querySelector("button").getBoundingClientRect(); return { top: Math.round(r.top), left: Math.round(r.left), right: Math.round(r.right), h: Math.round(b.height) }; });
        const keys = [...document.querySelectorAll("[data-flow] [data-form-prev], [data-flow] [data-form-next], [data-flow] [data-flow-pick], [data-flow] [data-request-submit], [data-flow] [data-flow-reset], [data-flow] [data-impact-submit], [data-flow] [data-impact-reset]")].filter((e) => e.offsetParent !== null).map((e) => Math.round(e.getBoundingClientRect().height));
        const im = document.querySelector("[data-flow-impact='shown'] [data-impact-form]");
        return { scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth, tiles, low: Math.min(...keys, 999), keys: keys.length, form: im ? Math.round(im.getBoundingClientRect().right) : null }; })()`);
      check(w.client === 390 && w.scroll <= w.client + 1, `${addr} at 390 px does not scroll sideways`, `(scroll width ${w.scroll})`);
      if (w.tiles.length) {
        const two = w.tiles.length < 2 || (w.tiles[0].top === w.tiles[1].top && w.tiles[1].left > w.tiles[0].left);
        check(two && w.tiles.every((t) => t.right <= 390 && t.h >= 44) && w.low >= 44, `${addr}: the tiles stand two to a row inside the screen, and every press target is at least 44 px high`, `(${w.tiles.length} tiles, lowest target ${w.low} px of ${w.keys})`);
      }
      if (w.form !== null) check(w.form <= 390, `${addr}: the impact study's form ends inside the screen`, `(${w.form})`);
    }
    await size(1280, 900);

    // ---- the queue, against the stand-in only ----
    if (stub) {
      await go(`${base}/analysis?analysis=queue_divorce&form=bars`);
      await drawnAll("queue_divorce");
      const qd = catalogue.find((c) => c.id === "queue_divorce");
      const fy = String(qd.inputs.first_year.choices.find((v) => String(v) !== String(qd.inputs.first_year.default)));
      await choose(`[data-flow-inputs] [data-request-input="first_year"]`, fy);
      const before = stub.requests.length;
      await click("[data-flow-ask] [data-request-submit]");
      await wait(`/request=/.test(location.search)`, 15000, "the request in the address");
      const asked = stub.requests[stub.requests.length - 1];
      check(stub.requests.length === before + 1 && asked.finding === "queue_divorce" && asked.params.first_year === fy && !("form" in asked.params) && Object.keys(asked.params).sort().join() === Object.keys(qd.inputs).sort().join(),
        "Ask queues the finding with its inputs and nothing else: the form is not in the queue", `(${JSON.stringify(asked.params)})`);
      const adr = await address();
      check(adr.includes(`request=${asked.id}`) && /form=bars/.test(adr) && adr.includes(`i.first_year=${fy}`), "the address keeps the request, its inputs and its form", `(${adr})`);
      await wait(`!!document.querySelector('[data-request-card="queued"]')`, 20000, "the queued request");
      const waits = await js(`({ card: document.querySelector('[data-request-card="queued"]').textContent, note: document.querySelector("[data-request-note]")?.textContent ?? "" })`);
      check(/queued: it waits for the data machine/.test(waits.card) && /queued at .* UTC/.test(waits.note) && /drawn as paired bars/.test(waits.note), "a queued request is shown as waiting for the data machine, never as running", `(${waits.card.slice(0, 80)})`);
      await wait(`!!document.querySelector("[data-request-id='${asked.id}']")`, 25000, "the request in the list");
      check(await js(`document.querySelector("[data-request-id='${asked.id}']").dataset.requestStatus === "queued"`), "the list of requests holds it, queued, at once");
      // a done request opened by its address, in a chosen form
      const done = card("impact_study");
      await go(`${base}/analysis?analysis=impact_study&form=bars&request=${stub.DONE_ID}`);
      await wait(`!!document.querySelector('[data-request-card="done"] [data-form-drawn="bars"] canvas')`, 25000, "the done request as paired bars");
      check(same(await dataOf(`[data-request-card="done"] [data-form-drawn="bars"]`), done.chart.series.map((s) => s.values)), "a done request opened by its address is drawn in the address's form, with the committed card's numbers");
      const f2 = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      const txt = await js(`document.querySelector('[data-request-card="done"]').innerText.replace(/\\s+/g, " ")`);
      check([done.numbers.series_pre, done.numbers.series_post, done.numbers.control_pre, done.numbers.control_post].every((v) => txt.includes(f2(v))), "its computed numbers are on the card whatever the form");
      await click(`[data-flow-impact="shown"] [data-form-tile-pick="multiples"]`);
      await wait(`!!document.querySelector('[data-request-card="done"] [data-form-drawn="multiples"] canvas')`, 20000, "the done request as small multiples");
      check(same(await dataOf(`[data-request-card="done"] [data-form-drawn="multiples"]`), done.chart.series.map((s) => s.values)) && /form=multiples/.test(await address()), "re-shown as small multiples without a new request: the same numbers", `(${stub.requests.length - before - 1} more requests)`);
      check(stub.requests.length === before + 1, "changing the form queued nothing");
    } else {
      lines.push("note the queue was not exercised (no --stub): nothing is written to the production queue by this check");
    }
    check(errors.length === 0, "no exception in the pages", errors.slice(0, 2).join(" | "));
    return bad ? 1 : 0;
  });
} catch (e) {
  lines.push(`FAILED: ${e.message}`);
  code = 1;
} finally {
  if (stub) await stub.close();
}
if (code === null) { lines.push("no browser on this machine: nothing is proven here"); code = 2; }
lines.push(`${n - bad} of ${n} checks passed`);
await new Promise((done) => process.stdout.write(lines.join("\n") + "\n", done));
process.exit(code);
