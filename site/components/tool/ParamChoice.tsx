"use client";
// Energy Research Warehouse (ERW) site, session 353: one choice of an address parameter on a page the server prices (the
// generator's node and its contract's shape): a select, its default and the default's source in grey under it, and a
// Reset. A change rewrites that parameter (taken out at the default, so the bare address stays bare) and asks the
// server again, the other parameters kept. PriceYearsNav (session 352) is the same for the price years.
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

export function ParamChoice({ name, value, dflt, label, options, note, path }: { name: string; value: string; dflt: string; label: string; options: [string, string][]; note: ReactNode; path: string }) {
  const router = useRouter();
  const go = (id: string) => {
    const q = new URLSearchParams(window.location.search);
    if (id === dflt) q.delete(name); else q.set(name, id);
    const s = q.toString();
    router.push(`${path}${s ? `?${s}` : ""}`, { scroll: false });
  };
  return (
    <div className="mt-3 text-sm" data-param-choice={name}>
      <label className="block">
        <span className="font-semibold">{label}</span>
        <select value={value} onChange={(e) => go(e.target.value)} className="mt-1 block w-full max-w-full border border-rule bg-white px-2 py-1 text-sm text-ink" data-param-select={name}>
          {options.map(([id, words]) => <option key={id} value={id}>{words}</option>)}
        </select>
      </label>
      <p className="mt-1 text-xs leading-snug text-muted" data-default={name}>{note}</p>
      {value !== dflt ? <button type="button" data-reset={name} aria-label={`Reset: ${label}`} onClick={() => go(dflt)} className="mt-1 border border-rule px-1.5 py-px text-xs">Reset</button> : null}
    </div>
  );
}
