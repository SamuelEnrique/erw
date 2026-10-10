"use client";
// Session 182, part 4: one flow for requests on /analysis, in two steps. It takes the place of "Ask for a finding",
// of the impact study's own section and of the template gallery, and nothing of the three is lost.
//
//   Step one, what to analyze. One list (lib/analysisflow.ts): the findings of the catalogue, each shown once with an
//   earlier form of the same analysis as a choice of "Version"; the impact study (its inputs are ImpactForm, handed in
//   by the page); and the ten weekly chart templates as analyses, each with the inputs the weekly run computes.
//   Step two, how to show it. A picker of chart forms (FormPicker), each form drawn as an example from real data, the
//   form the analysis's own code declares preselected and labeled "Default for this analysis", changeable.
//
// What then happens depends on the analysis, and the page says which. A finding or the impact study is a request: it
// waits in the queue (POST /api/analysis, unchanged: the request carries the finding and its inputs, as before) and
// the data machine's worker computes it; the card that arrives is drawn in the chosen form. A template is not a
// request: the weekly run has already computed it for every choice of its inputs, so its chart is shown at once, in
// the chosen form, and nothing is shown as waiting. The internal template (chokepoint transits) is listed with its
// inputs and is not drawn: its table is licensed internal.
//
// The chosen form is how the page draws a card, not part of the computation, so it travels in the address and not in
// the queue: ?analysis=<id>&version=<id>&i.<input>=<value>&form=<form>&request=<id>. A link opens the same view, and a
// card already computed is re-shown in another form without a new request. The flow compares nothing and advises nothing.
import { useEffect, useMemo, useState, type ReactNode } from "react";
import type { Card, CatalogueEntry } from "@/lib/findings";
import { GROUPS, IMPACT, INTERNAL_FORM, comboOf, defaultParams, flowList, inputChoices, inputNames, nameWords, validParams, valueWords, type GalleryEntry, type Tpl } from "@/lib/analysisflow";
import { formName, formsOfOption, formsOfSpec, isForm, reformOption, thumbOfOption, thumbOfSpec, type FormId } from "@/lib/chartforms";
import { FindingCard } from "./FindingCard";
import { FlowHost } from "./FlowHost";
import { FormScope, OptionChart } from "./FormChart";
import { EXAMPLE_HEIGHT, FormPicker } from "./FormPicker";
import { RequestCard } from "./RequestCard";

type Chart = { title: string; subtitle: string; source_line: string; option: Record<string, unknown>; computed_at: string; facts: string[] };
const when = (iso: string) => iso.replace("T", " ").slice(0, 16) + " UTC";
const REQUEST_ID = /^[A-Za-z0-9-]{6,60}$/;
export const ASKED_EVENT = "erw-analysis-asked";   // the list of requests reads the queue again when it hears this

export function RequestFlow({ catalogue, templates, gallery, computedAt, cards, impactForm }: {
  catalogue: CatalogueEntry[]; templates: Tpl[]; gallery: GalleryEntry[]; computedAt?: string; cards: Record<string, Card>; impactForm?: ReactNode;
}) {
  const items = useMemo(() => flowList(catalogue, templates), [catalogue, templates]);
  const [sel, setSel] = useState(items[0]?.id ?? "");
  const [ver, setVer] = useState(items[0]?.versions[0]?.id ?? "");
  const [chosen, setChosen] = useState<Record<string, string>>({});      // a finding's inputs, over its defaults
  const [tparams, setTparams] = useState<Record<string, string>>({});    // a template's inputs
  const [formWanted, setFormWanted] = useState<FormId | null>(null);     // null: the default for the analysis
  const [request, setRequest] = useState("");                            // the request whose card is drawn here
  const [impactAsked, setImpactAsked] = useState("");                    // a request the impact form draws itself
  const [shown, setShown] = useState(false);                             // the committed card of these inputs, drawn here
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [loaded, setLoaded] = useState<{ file: string; chart: Chart | null; err: string } | null>(null);
  const [touched, setTouched] = useState(false);                         // the address is written only once something was chosen

  const item = items.find((i) => i.id === sel) ?? items[0];
  const isTpl = Boolean(item?.template);
  const entry = item && !isTpl ? catalogue.find((c) => c.id === (item.versions.some((v) => v.id === ver) ? ver : item.versions[0]?.id)) : undefined;
  const g = isTpl ? gallery.find((x) => x.template === item.template) : undefined;
  const tpl = isTpl ? templates.find((t) => t.template === item.template) : undefined;
  const card = entry ? cards[entry.id] : undefined;
  const defaults: Record<string, string> = entry ? Object.fromEntries(Object.entries(entry.inputs).map(([k, v]) => [k, String(v.default)])) : {};
  const params: Record<string, string> = { ...defaults };
  if (entry) for (const [k, v] of Object.entries(chosen)) if (entry.inputs[k]?.choices.map(String).includes(v)) params[k] = v;
  const atDefaults = Boolean(entry) && Object.keys(defaults).every((k) => params[k] === defaults[k]);
  const names = inputNames(g);
  const combo = g ? comboOf(g, tparams) : undefined;
  const file = combo?.file ?? "";
  const cur = loaded && loaded.file === file ? loaded : null;

  // the address is read once, after the mount: a link opens the same analysis, inputs, form and request
  useEffect(() => {
    const t = setTimeout(() => {
      const q = new URLSearchParams(window.location.search);
      const it = items.find((i) => i.id === q.get("analysis"));
      if (!it) return;
      const ins: Record<string, string> = {};
      q.forEach((v, k) => { if (k.startsWith("i.")) ins[k.slice(2)] = v; });
      setSel(it.id);
      setVer(it.versions.find((v) => v.id === q.get("version"))?.id ?? it.versions[0]?.id ?? "");
      const gal = it.template ? gallery.find((x) => x.template === it.template) : undefined;
      if (gal) setTparams(validParams(gal, { ...defaultParams(gal), ...ins })); else setChosen(ins);
      const f = q.get("form");
      setFormWanted(isForm(f) ? f : null);
      const r = q.get("request") ?? "";
      setRequest(REQUEST_ID.test(r) ? r : "");
      setShown(q.get("card") === "1");
      setTouched(true);
    }, 0);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // a template's chart for the chosen inputs: the weekly run's file, read when the choice changes
  useEffect(() => {
    if (!file) return;
    let stop = false;
    fetch(`/analysis-files/gallery/${file}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((c: Chart) => { if (!stop) setLoaded({ file, chart: c, err: "" }); })
      .catch((e) => { if (!stop) setLoaded({ file, chart: null, err: `The chart could not load: ${(e as Error).message}.` }); });
    return () => { stop = true; };
  }, [file]);

  const source = isTpl ? cur?.chart?.option : card?.chart;
  const forms = useMemo<FormId[]>(() => (!source ? [] : isTpl ? formsOfOption(source as Record<string, unknown>) : formsOfSpec(source as Card["chart"])), [source, isTpl]);
  const def = forms[0];
  const form = formWanted && forms.includes(formWanted) ? formWanted : def;
  const examples = useMemo(() => Object.fromEntries(forms.map((f) => [f, isTpl ? thumbOfOption(source as Record<string, unknown>, f, EXAMPLE_HEIGHT) : thumbOfSpec(source as Card["chart"], f, EXAMPLE_HEIGHT)])),
    [forms, source, isTpl]);

  // the choice is kept in the address, so that the view can be shared and survives a reload
  useEffect(() => {
    if (!touched || !item) return;
    const u = new URL(window.location.href);
    for (const k of [...u.searchParams.keys()]) if (k.startsWith("i.")) u.searchParams.delete(k);
    const put = (k: string, v: string | null) => { if (v) u.searchParams.set(k, v); else u.searchParams.delete(k); };
    put("analysis", item.id);
    put("version", entry && item.versions.length > 1 ? entry.id : null);
    if (isTpl) for (const [k, v] of Object.entries(tparams)) put(`i.${k}`, v);
    else for (const k of Object.keys(defaults)) put(`i.${k}`, params[k] !== defaults[k] ? params[k] : null);
    put("form", form && form !== def ? form : null);
    put("request", request || null);
    put("card", shown && atDefaults ? "1" : null);
    window.history.replaceState(null, "", u.toString());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [touched, sel, ver, chosen, tparams, form, def, request, shown]);

  const pickItem = (id: string) => {
    const it = items.find((i) => i.id === id);
    if (!it) return;
    const gal = it.template ? gallery.find((x) => x.template === it.template) : undefined;
    setSel(id); setVer(it.versions[0]?.id ?? ""); setChosen({}); setTparams(gal ? defaultParams(gal) : {});
    setFormWanted(null); setRequest(""); setImpactAsked(""); setShown(false); setNote(""); setTouched(true);
  };
  const reset = () => { setChosen({}); setTparams(g ? defaultParams(g) : {}); setFormWanted(null); setNote(""); setTouched(true); };
  const setInput = (k: string, v: string) => { setChosen({ ...params, [k]: v }); setShown(false); setTouched(true); };
  const setTemplateInput = (k: string, v: string) => { if (g) setTparams(validParams(g, { ...tparams, [k]: v }, k)); setTouched(true); };
  const pickForm = (f: FormId) => { setFormWanted(f === def ? null : f); setTouched(true); };
  const submit = async () => {
    if (!entry) return;
    setBusy(true); setNote("");
    try {
      const r = await fetch("/api/analysis", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ kind: "run", finding: entry.id, params }) });
      const j = (await r.json()) as { ok: boolean; reason?: string; id?: string };
      setNote(j.ok ? `queued at ${when(new Date().toISOString())} (request ${j.id}): the card appears below, drawn as ${formName(form ?? "lines").toLowerCase()}, in 1 to 5 minutes when the data machine is awake` : (j.reason ?? "not queued"));
      if (j.ok && j.id) { setRequest(j.id); setTouched(true); window.dispatchEvent(new Event(ASKED_EVENT)); }
    } catch (e) { setNote((e as Error).message); }
    setBusy(false);
  };

  if (!item) return <p className="text-sm text-muted">No analysis is in the catalogue yet.</p>;
  const field = "mt-1 w-full max-w-full border border-rule bg-panel px-2 py-2 text-sm text-ink";
  const key = "min-h-[44px] border border-rule bg-panel px-3 py-1 text-sm text-ink hover:border-ink disabled:opacity-60";
  const caption = isTpl
    ? `Each example is this template's own chart for the chosen inputs, as the weekly run computed it${cur?.chart ? ` (${cur.chart.computed_at.slice(0, 10)})` : ""}, drawn small. Hover reads the values.`
    : card ? `Each example is this analysis's committed card with its default inputs (computed ${card.computed_at.slice(0, 10)}), drawn small: real values, hover reads them. A request with other inputs has its own numbers, which arrive with its card.` : "";
  const stepTwo = (
    <div className="mt-6" data-flow-step="2">
      <h3 className="mb-2 text-base font-semibold">Step 2: how to show it</h3>
      {item.internal ? (
        <p className="max-w-3xl text-sm text-muted" data-form-internal="1">
          This template&apos;s own form is {formName(INTERNAL_FORM[item.template ?? ""] ?? "lines").toLowerCase()} (a timeline). No example is drawn: its table is licensed internal, so its numbers never reach the site.
        </p>
      ) : forms.length && form && def ? (
        <FormPicker forms={forms} def={def} value={form} onPick={pickForm} examples={examples} caption={caption} />
      ) : (
        <p className="text-sm text-muted" data-form-none="1">{isTpl && file && !cur ? "Reading the chart." : isTpl ? "No chart is held for these inputs, so no form can be drawn." : "No card of this analysis is committed, so no example can be drawn."}</p>
      )}
    </div>
  );
  const host = {
    between: item.id === IMPACT ? stepTwo : null,
    onAsked: (id: string) => { setImpactAsked(id); setRequest(id); setTouched(true); window.dispatchEvent(new Event(ASKED_EVENT)); },
  };
  const tH = cur?.chart && form === "multiples" ? Math.max(360, ((cur.chart.option.series as unknown[]) ?? []).length * 96 + 74) : 360;
  const template = isTpl && !item.internal && cur?.chart && form ? reformOption(cur.chart.option, form, tH) : null;

  return (
    <FormScope.Provider value={form ?? null}>
      <div data-flow="1" data-flow-analysis={item.id} data-flow-version={entry?.id ?? ""} data-flow-form={form ?? ""} data-flow-items={items.length}>
        <h3 className="mb-2 text-base font-semibold">Step 1: what to analyze</h3>
        {GROUPS.map((grp) => {
          const list = items.filter((i) => i.group === grp.id);
          return list.length ? (
            <div key={grp.id} className="mb-3" data-flow-group={grp.id} data-flow-group-n={list.length}>
              <div className="text-xs font-semibold uppercase tracking-wide text-muted">{grp.title} <span className="font-normal normal-case tracking-normal">{grp.note}</span></div>
              <div className="mt-1 grid gap-1 sm:grid-cols-2 lg:grid-cols-3" role="group" aria-label={grp.title}>
                {list.map((i) => (
                  <button key={i.id} type="button" aria-pressed={i.id === item.id} onClick={() => pickItem(i.id)} data-flow-pick={i.id}
                    className={`min-h-[44px] border px-2 py-1 text-left text-sm ${i.id === item.id ? "border-ink bg-ink text-paper" : "border-rule bg-panel text-ink hover:border-ink"}`}>
                    {i.name}{i.internal ? " (internal: not drawn on the site)" : ""}
                  </button>
                ))}
              </div>
            </div>
          ) : null;
        })}

        <div className="mt-4" data-flow-inputs={item.id}>
          <div className="text-xs font-semibold uppercase tracking-wide text-muted">Inputs: {item.name}</div>
          {entry && item.id !== IMPACT ? (
            <>
              <div className="mt-1 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {item.versions.length > 1 ? (
                  <label className="flex min-w-0 flex-col text-xs text-muted">
                    Version
                    <select value={entry.id} onChange={(e) => { setVer(e.target.value); setChosen({}); setFormWanted(null); setShown(false); setTouched(true); }} className={field} data-flow-version-input="1">
                      {item.versions.map((v) => <option key={v.id} value={v.id}>{v.label}</option>)}
                    </select>
                  </label>
                ) : null}
                {Object.entries(entry.inputs).map(([k, inp]) => (
                  <label key={k} className="flex min-w-0 flex-col text-xs text-muted">
                    {inp.label}
                    <select value={params[k] ?? ""} onChange={(e) => setInput(k, e.target.value)} className={field} data-request-input={k}>
                      {inp.choices.map((v) => <option key={String(v)} value={String(v)}>{inp.words?.[String(v)] ?? String(v)}</option>)}
                    </select>
                  </label>
                ))}
              </div>
              <p className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted">
                <button type="button" onClick={reset} className={key} data-flow-reset="1">Reset</button>
                <span>Defaults: {Object.entries(entry.inputs).map(([k, inp]) => `${inp.label}: ${inp.words?.[defaults[k]] ?? defaults[k]}`).join("; ")}.</span>
              </p>
            </>
          ) : null}
          {isTpl && tpl ? (
            <>
              {g && !item.internal ? (
                <div className="mt-1 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {names.map((p) => (
                    <label key={p} className="flex min-w-0 flex-col text-xs text-muted">
                      {nameWords(p)}
                      <select value={tparams[p] ?? ""} onChange={(e) => setTemplateInput(p, e.target.value)} className={field} data-template-input={p}>
                        {inputChoices(g, names, tparams, p).map((c) => <option key={c.value} value={c.value}>{valueWords(p, c.value)}{c.held ? "" : " (not held)"}</option>)}
                      </select>
                    </label>
                  ))}
                </div>
              ) : (
                <ul className="mt-1 list-disc pl-5 text-sm" data-template-internal-inputs={tpl.template}>
                  {Object.entries(tpl.params).map(([k, v]) => (
                    <li key={k}>{nameWords(k)}: {(Array.isArray(v.choices) ? v.choices : []).map((c) => valueWords(k, String(c))).join(", ")} (default {valueWords(k, String(v.default))})</li>
                  ))}
                </ul>
              )}
              <p className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted">
                {g && !item.internal ? <button type="button" onClick={reset} className={key} data-flow-reset="1">Reset</button> : null}
                <span data-template-weekly="1">
                  {item.internal
                    ? "Internal: the table's license keeps this template on the warehouse's machines. It runs there every week with the others, is never chosen as the chart of the week and is never drawn on the site."
                    : `Computed by the weekly run for every choice of these inputs${computedAt ? ` (last ${computedAt.slice(0, 10)})` : ""}, from public tables only: the chart is shown at once and no request is queued.`}
                </span>
              </p>
              <p className="mt-2 max-w-3xl text-xs text-muted" data-template-method={tpl.template}>{tpl.method}</p>
            </>
          ) : null}
          <div hidden={item.id !== IMPACT} data-flow-impact={item.id === IMPACT ? "shown" : "hidden"}><FlowHost.Provider value={host}>{impactForm}</FlowHost.Provider></div>
        </div>

        {item.id !== IMPACT ? stepTwo : null}

        {entry && item.id !== IMPACT ? (
          <div className="mt-4" data-flow-ask="1">
            <div className="flex flex-wrap items-center gap-3">
              <button type="button" onClick={submit} disabled={busy} className={key} data-request-submit="1">Ask the warehouse</button>
              {atDefaults && card ? (
                <>
                  <button type="button" onClick={() => { setShown(!shown); setTouched(true); }} className={key} data-flow-show={card.card_id}>
                    {shown ? "Hide the computed card" : `Show the card computed ${card.computed_at.slice(0, 10)}`}
                  </button>
                  <a className="text-xs" href={`/analysis/card/${card.card_id}${form && form !== def ? `?form=${form}` : ""}`} data-flow-card-link={card.card_id}>The card&apos;s own address, in this form</a>
                </>
              ) : null}
            </div>
            <p className="mt-2 max-w-3xl text-xs text-muted" data-flow-wait="1">
              A request waits in the queue and is computed on the data machine: the card arrives here in 1 to 5 minutes when the machine is awake, drawn in the form chosen above. When the machine is
              off, the request stays queued with the time it was asked, in the list of requests below, and runs when the machine wakes.
              {atDefaults && card ? " These inputs are the defaults, and their card is already computed: it can be shown here in any form without a new request." : ""}
            </p>
            {note ? <p className="mt-2 text-xs text-muted" data-request-note="1">{note}</p> : null}
            {shown && atDefaults && card ? <div className="mt-4 border border-rule p-3" data-flow-card={card.card_id}><FindingCard card={card} /></div> : null}
          </div>
        ) : null}
        {request && request !== impactAsked ? <RequestCard key={request} requestId={request} wait /> : null}

        {isTpl && !item.internal ? (
          <div className="mt-4" data-flow-template={item.template}>
            {combo && !combo.file ? <p className="text-sm text-muted" data-template-none="1">Not held for these inputs: {combo.reason ?? "no data"}. The weekly run tried them and wrote no chart.</p> : null}
            {cur?.err ? <p className="text-sm text-muted">{cur.err}</p> : null}
            {cur?.chart && template && form ? (
              <figure data-template-chart={item.template} data-template-form={form}>
                <h4 className="text-lg">{cur.chart.title}</h4>
                <p className="text-xs text-muted">{cur.chart.subtitle}</p>
                <OptionChart option={template} label={`${cur.chart.title}, as ${formName(form).toLowerCase()}`} height={tH} form={form} />
                <ul className="mt-2 list-disc pl-5 text-xs" data-template-facts="1">
                  {cur.chart.facts.map((f) => <li key={f}>{f}</li>)}
                </ul>
                <figcaption className="mt-2 break-words text-xs text-muted">
                  {cur.chart.source_line} Computed {cur.chart.computed_at.replace("T", " ").replace("Z", " UTC")} by the weekly run.{" "}
                  <a href={`/analysis-files/gallery/${file}`} download data-template-download="json">The chart&apos;s data (JSON)</a>
                </figcaption>
              </figure>
            ) : null}
          </div>
        ) : null}
      </div>
    </FormScope.Provider>
  );
}
