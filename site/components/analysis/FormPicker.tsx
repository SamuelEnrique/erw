"use client";
// Session 182, part 4: step two of the request flow, "how to show it". A visual picker of chart forms: each form
// that fits the chosen analysis is a tile with a small drawing of that form, made from real data (the analysis's own
// committed card, or the week's chart of the chosen template), never from invented numbers. The user flips through
// the forms with Previous and Next, or presses a tile. The form the analysis's own code declares is preselected and
// labeled "Default for this analysis"; "Back to the default" returns to it. The tiles are toggles (aria-pressed).
// On a phone the tiles stand two to a row, each with a press target 44 px high, and nothing scrolls sideways.
import { FORMS, formName, type FormId } from "@/lib/chartforms";
import { OptionChart } from "./FormChart";

export const EXAMPLE_HEIGHT = 112;

export function FormPicker({ forms, def, value, onPick, examples, caption }: {
  forms: FormId[]; def: FormId; value: FormId; onPick: (f: FormId) => void; examples: Partial<Record<FormId, unknown>>; caption: string;
}) {
  const at = Math.max(0, forms.indexOf(value));
  const flip = (step: number) => onPick(forms[(at + step + forms.length) % forms.length]);
  const key = "min-h-[44px] min-w-[44px] border border-rule bg-panel px-3 text-sm text-ink hover:border-ink disabled:opacity-50";
  return (
    <div data-form-picker="1" data-form-chosen={value} data-form-default={def} data-form-offered={forms.join(",")}>
      <div className="mb-2 flex flex-wrap items-center gap-2" role="group" aria-label="Flip through the chart forms">
        <button type="button" className={key} onClick={() => flip(-1)} disabled={forms.length < 2} data-form-prev="1">Previous</button>
        <button type="button" className={key} onClick={() => flip(1)} disabled={forms.length < 2} data-form-next="1">Next</button>
        <span className="text-xs text-muted" data-form-count="1">{at + 1} of {forms.length}: {formName(value)}</span>
        {value !== def ? <button type="button" className={key} onClick={() => onPick(def)} data-form-reset="1">Back to the default</button> : null}
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
        {forms.map((f) => (
          <div key={f} className={`min-w-0 border bg-panel ${f === value ? "border-ink" : "border-rule"}`} data-form-tile={f} data-form-selected={f === value ? "1" : "0"}>
            <button type="button" aria-pressed={f === value} onClick={() => onPick(f)} data-form-tile-pick={f}
              className={`flex min-h-[44px] w-full flex-col items-start justify-center px-2 py-1 text-left text-xs ${f === value ? "bg-ink text-paper" : "text-ink"}`}>
              <span className="font-semibold">{formName(f)}</span>
              {f === def ? <span className="text-[10px]" data-form-default-mark="1">Default for this analysis</span> : null}
            </button>
            {examples[f] ? <OptionChart option={examples[f]} label={`Example: ${formName(f)}`} height={EXAMPLE_HEIGHT} form={f} small />
              : <p className="px-2 py-3 text-[11px] text-muted">No example can be drawn.</p>}
            <p className="px-2 pb-1 text-[10px] leading-snug text-muted">{FORMS.find((x) => x.id === f)?.shows}</p>
          </div>
        ))}
      </div>
      <p className="mt-1 max-w-3xl text-[11px] text-muted" data-form-caption="1">
        {caption}{forms.length === 1 ? " One form fits this analysis: no other keeps what it shows." : ""}
      </p>
    </div>
  );
}
