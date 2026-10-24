// Energy Research Warehouse (ERW) site, session 1413 (chain 107): a figure the energy mix views compute from a committed
// file's arrays (components/mix/views.tsx: the duck curve by year, the average day's peak hours, the history by state,
// the availability means), keyed fmt|<form>|filecalc|<function>|<data file>|<args> (lib/mixViewCalc.ts names each
// function). scripts/check-values.mjs reads the file in the repository and applies the page's own function to it
// (scripts/check-filecalc.mjs), then holds the text to that value written in the form (scripts/check-format.mjs). The
// text is the view's own, written by the same function as before; the tip names what the figure is, its rule and its file.
import { Num } from "@/components/Num";
import { FILECALC, filecalcKey, sourceOf, type FilecalcFn } from "@/lib/mixViewCalc";

/** The tip of a computed figure: its source, what it is and for which case, its rule, and the committed file. */
export function calcTip(fn: FilecalcFn, file: string, args: string[]): string {
  return `${sourceOf(file)}: ${FILECALC[fn].what} (${args.join(", ")}), computed by ${FILECALC[fn].rule} from the committed file site/data/${file}`;
}

/** A computed figure: the value as the view writes it (text), keyed by the function that recomputes it. */
export function CalcKey({ v, form, text, fn, file, args }: { v: number; form: string; text: string; fn: FilecalcFn; file: string; args: string[] }) {
  return <span title={calcTip(fn, file, args)} className="cursor-help border-b border-dotted border-muted"><Num check={`fmt|${form}|${filecalcKey(fn, file, args)}`} raw={v}>{text}</Num></span>;
}
