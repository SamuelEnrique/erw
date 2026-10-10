"use client";
// Session 182, part 4: a finding card's chart in a chosen form. The forms that can honestly show the card's data and
// the default (the form the card's own code declares) come from lib/chartforms.ts. In the default form the chart is
// drawn exactly as before (CardChart: the card's own drawing, small multiples included); in another form the same
// values are redrawn, and hover shows them. Nothing is computed again: a card already computed is re-shown.
//
// Where the choice lives. Inside the request flow the flow's picker decides (FormScope) and this draws no control of
// its own. Anywhere else the card carries a small row of toggles, and the choice is kept in the address under
// `addressKey` (?form=bars on a card's own page, ?form.<card>=bars in a list), so a link opens the same view. With no
// address key (the renderer's frame) the default is drawn and no control is shown.
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useEChart } from "@/components/echarts";
import { asMulti, formName, formsOfSpec, isForm, plainSeries, specOption, type FormId } from "@/lib/chartforms";
import type { ChartSpec } from "@/lib/findingchart";
import { CardChart } from "./CardChart";

/** The form the request flow chose for the cards drawn inside it; null outside the flow. */
export const FormScope = createContext<FormId | null>(null);

export function OptionChart({ option, label, height, form, small = false }: { option: unknown; label: string; height: number; form: string; small?: boolean }) {
  const box = useEChart((chart) => chart.setOption(option, true), [option]);
  return <div ref={box} role="img" aria-label={label} style={{ height }} className="w-full" {...(small ? { "data-form-example": form } : { "data-finding-chart": form, "data-form-drawn": form })} />;
}

function Reformed({ spec, form, label, height }: { spec: ChartSpec; form: FormId; label: string; height: number }) {
  const multi = asMulti(spec);
  const [measure, setMeasure] = useState(multi?.measures[0].key);
  const panels = form === "multiples" ? spec.series.length : 0;
  const H = panels ? Math.max(height, panels * 96 + 50) : height;
  const option = useMemo(() => specOption(spec, form, H, measure), [spec, form, H, measure]);
  if (!option) return null;
  const axis = form === "multiples" ? "" : plainSeries(spec, measure).yLabel;
  return (
    <>
      {multi && multi.measures.length > 1 ? (
        <div className="mb-1 mt-1 flex flex-wrap items-center gap-1" role="group" aria-label="Measure shown">
          {multi.measures.map((m) => (
            <button key={m.key} type="button" aria-pressed={measure === m.key} onClick={() => setMeasure(m.key)} data-form-measure={m.key}
              className={`border px-2 py-1 text-xs ${measure === m.key ? "border-ink bg-ink text-paper" : "border-rule bg-panel text-ink"}`}>{m.label}</button>
          ))}
        </div>
      ) : null}
      {axis ? <p className="mt-1 text-[11px] text-muted" data-form-axis="1">Vertical axis: {axis}</p> : null}
      <OptionChart option={option} label={`${label}, as ${formName(form).toLowerCase()}`} height={H} form={form} />
    </>
  );
}

export function FormChart({ spec, label, height = 340, addressKey = null }: { spec: ChartSpec; label: string; height?: number; addressKey?: string | null }) {
  const scope = useContext(FormScope);
  const forms = useMemo(() => formsOfSpec(spec), [spec]);
  const def = forms[0];
  const [own, setOwn] = useState<FormId | null>(null);
  useEffect(() => {
    if (!addressKey) return;
    const t = setTimeout(() => {     // the address is read after the mount, so that the first paint is the page as it was built
      const v = new URLSearchParams(window.location.search).get(addressKey);
      if (isForm(v) && forms.includes(v)) setOwn(v);
    }, 0);
    return () => clearTimeout(t);
  }, [addressKey, forms]);
  const wanted = scope ?? own;
  const form = wanted && forms.includes(wanted) ? wanted : def;
  const pick = (f: FormId) => {
    setOwn(f);
    if (!addressKey) return;
    const u = new URL(window.location.href);
    if (f === def) u.searchParams.delete(addressKey); else u.searchParams.set(addressKey, f);
    window.history.replaceState(null, "", u.toString());
  };
  const toggles = !scope && Boolean(addressKey) && forms.length > 1;
  return (
    <div data-form={form ?? "none"} data-form-default={def ?? "none"}>
      {toggles ? (
        <div className="mt-2 flex flex-wrap items-center gap-1" role="group" aria-label="Chart form" data-form-toggles={forms.join(",")}>
          <span className="mr-1 text-[11px] text-muted">Shown as</span>
          {forms.map((f) => (
            <button key={f} type="button" aria-pressed={form === f} onClick={() => pick(f)} data-form-pick={f} title={f === def ? "Default for this analysis" : undefined}
              className={`border px-2 py-1 text-xs ${form === f ? "border-ink bg-ink text-paper" : "border-rule bg-panel text-ink"}`}>
              {formName(f)}{f === def ? " (default)" : ""}
            </button>
          ))}
        </div>
      ) : null}
      {scope && def && !forms.includes(scope) ? (
        <p className="mt-1 text-[11px] text-muted" data-form-unfit={scope}>This card&apos;s data does not fit {formName(scope).toLowerCase()}: it is drawn in its own form, {formName(def).toLowerCase()}.</p>
      ) : null}
      {!def || form === def ? <CardChart spec={spec} label={label} height={height} /> : <Reformed key={form} spec={spec} form={form} label={label} height={height} />}
    </div>
  );
}
