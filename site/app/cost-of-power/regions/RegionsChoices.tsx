"use client";
// Chain 780 (session 11600): the choices of "Where the next gigawatts can go" on the All grids tab: which kind of
// place is listed, which two places stand side by side as A and B, and which columns the table keeps. Every choice
// lives in the address (srkind, sra, srb, srcols: app/cost-of-power/regions/lib.ts), so a link carries it and the
// back button undoes it; the tab's own names in the address are kept as they came. The server draws the table from
// the address; nothing is fetched here.
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AB_ANCHOR, ANCHOR, KINDS, KIND_PLURAL, colsChange, srHref, unitWords, type Column, type Kind, type Param, type SectionHead } from "./lib";

const field = "mt-1 block max-w-full border border-rule bg-white px-2 py-1 text-sm text-ink";
const btn = "border border-rule bg-white px-2 py-1 text-sm";

export function RegionsChoices({ q, columns, sections, chosen, defaults, kind, a, b, places, counts }: {
  q: Record<string, string | undefined>; columns: Column[]; sections: Pick<SectionHead, "id" | "title">[]; chosen: string[]; defaults: string[];
  kind: Kind | "all"; a: string | null; b: string | null; places: { id: string; name: string; kind: Kind }[]; counts: Record<Kind, number>;
}) {
  const router = useRouter();
  const [picked, setPicked] = useState<string[]>(chosen);
  const go = (change: Partial<Record<Param, string | null>>, hash: string = ANCHOR) => router.push(srHref(q, change, hash), { scroll: false });
  const toggle = (key: string) => setPicked((p) => (p.includes(key) ? p.filter((k) => k !== key) : [...p, key]));
  const same = picked.length === chosen.length && picked.every((k) => chosen.includes(k));
  const total = KINDS.reduce((n, k) => n + counts[k], 0);
  return (
    <form className="mb-3 text-sm" data-sr-choices="1" onSubmit={(e) => { e.preventDefault(); go(colsChange(picked, columns)); }}>
      <div className="flex flex-wrap items-end gap-x-4 gap-y-2">
        <label className="block"><span className="font-semibold">Places listed</span>
          <select name="srkind" value={kind} onChange={(e) => go({ srkind: e.target.value === "all" ? null : e.target.value })} className={field} data-sr-kind="1">
            <option value="all">every place ({total})</option>
            {KINDS.map((k) => <option key={k} value={k}>the {KIND_PLURAL[k]} ({counts[k]})</option>)}
          </select>
        </label>
        {(["a", "b"] as const).map((slot) => (
          <label key={slot} className="block"><span className="font-semibold">{slot === "a" ? "A, side by side" : "B, side by side"}</span>
            <select name={`sr${slot}`} value={(slot === "a" ? a : b) ?? ""} onChange={(e) => go(slot === "a" ? { sra: e.target.value || null } : { srb: e.target.value || null }, e.target.value ? AB_ANCHOR : ANCHOR)} className={`${field} w-56`} data-sr-pick={slot}>
              <option value="">none</option>
              {KINDS.map((k) => (
                <optgroup key={k} label={KIND_PLURAL[k]}>
                  {places.filter((p) => p.kind === k).map((p) => <option key={p.id} value={p.id} disabled={(slot === "a" ? b : a) === p.id}>{p.name}</option>)}
                </optgroup>
              ))}
            </select>
          </label>
        ))}
        {a || b ? <button type="button" className={btn} onClick={() => go({ sra: null, srb: null })} data-sr-reset="ab">Clear A and B</button> : null}
      </div>
      <details className="mt-3 border-t border-rule pt-2" data-sr-picker={`${chosen.length}|${columns.length}`}>
        <summary className="cursor-pointer py-0.5 font-semibold">Columns shown: {chosen.length} of {columns.length}</summary>
        <div className="mt-2 grid gap-x-6 gap-y-3 sm:grid-cols-2 xl:grid-cols-4">
          {sections.filter((s) => columns.some((c) => c.section === s.id)).map((s) => (
            <fieldset key={s.id} className="min-w-0" data-sr-picker-section={s.id}>
              <legend className="font-semibold">{s.title}</legend>
              {columns.filter((c) => c.section === s.id).map((c) => (
                <label key={c.key} className="flex items-start gap-2 py-0.5">
                  <input type="checkbox" className="mt-1" checked={picked.includes(c.key)} onChange={() => toggle(c.key)} data-sr-col-pick={c.key} />
                  <span>{c.label}{unitWords(c.unit) ? `, ${unitWords(c.unit)}` : ""}</span>
                </label>
              ))}
            </fieldset>
          ))}
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <button type="submit" className="border border-accent bg-accent px-3 py-1 text-white" disabled={same || picked.length === 0} data-sr-show="1">Show these {picked.length} columns</button>
          <button type="button" className={btn} onClick={() => { const all = columns.map((c) => c.key); setPicked(all); go(colsChange(all, columns)); }} data-sr-cols="all">Every column</button>
          <button type="button" className={btn} onClick={() => { setPicked(defaults); go({ srcols: null }); }} data-sr-cols="default">The columns the table opens on</button>
        </div>
      </details>
    </form>
  );
}
