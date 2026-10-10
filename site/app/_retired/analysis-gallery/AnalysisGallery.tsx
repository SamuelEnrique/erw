"use client";
// Session 23: the template gallery on /analysis. Each template's parameters are chosen here; the chart for that
// choice was computed by warehouse/analysis/run.py from the public tables, on the warehouse's side, and is served
// from its cache (public/analysis-files/gallery/, recomputed every week).
// Session 182, part 4: retired. The gallery is folded into the request flow on /analysis
// (components/analysis/RequestFlow.tsx): the same nine public templates, the same inputs, the same weekly files, now
// with a choice of chart form. Nothing imports this file; it is kept as the record of what the gallery was.
import { useEffect, useMemo, useState } from "react";
import { EChartOption } from "@/components/EChartOption";
import { paramWords } from "@/lib/findingwords";  // session 170: human labels ("ERCOT North Hub", not HB_NORTH)

type Combo = { params: Record<string, unknown>; file: string | null; reason?: string };
type Entry = { template: string; title: string; default: string; combos: Record<string, Combo> };
type Tpl = { template: string; title: string; method: string; tables: string[] };
type Chart = { title: string; subtitle: string; source_line: string; option: unknown; computed_at: string; facts: string[] };

export function AnalysisGallery({ gallery, templates }: { gallery: Entry[]; templates: Tpl[] }) {
  const [name, setName] = useState(gallery[0]?.template ?? "");
  const entry = gallery.find((g) => g.template === name);
  const tpl = templates.find((t) => t.template === name);
  const [params, setParams] = useState<Record<string, string>>({});
  useEffect(() => {
    if (!entry) return;
    const d = entry.combos[entry.default]?.params ?? Object.values(entry.combos)[0]?.params ?? {};
    setParams(Object.fromEntries(Object.entries(d).map(([k, v]) => [k, String(v)])));
  }, [entry]);
  const names = useMemo(() => (entry ? Object.keys(Object.values(entry.combos)[0]?.params ?? {}) : []), [entry]);
  // the choices of each parameter, given the ones before it (a hub depends on the ISO)
  const choices = (p: string) => {
    if (!entry) return [];
    const before = names.slice(0, names.indexOf(p));
    const vals = Object.values(entry.combos)
      .filter((c) => before.every((b) => String(c.params[b]) === params[b]))
      .map((c) => String(c.params[p]));
    return Array.from(new Set(vals));
  };
  const combo = entry ? Object.values(entry.combos).find((c) => names.every((n) => String(c.params[n]) === params[n])) : undefined;
  const [chart, setChart] = useState<Chart | null>(null);
  const [err, setErr] = useState("");
  useEffect(() => {
    setChart(null);
    setErr("");
    if (!combo) return;
    if (!combo.file) {
      setErr(`Not available for these parameters: ${combo.reason ?? "no data"}.`);
      return;
    }
    fetch(`/analysis-files/gallery/${combo.file}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setChart)
      .catch((e) => setErr(`The chart could not load: ${(e as Error).message}.`));
  }, [combo]);
  const set = (p: string, v: string) => {
    const next = { ...params, [p]: v };
    // keep later parameters valid
    for (const q of names.slice(names.indexOf(p) + 1)) {
      const ok = Object.values(entry!.combos).filter((c) => names.slice(0, names.indexOf(q)).every((b) => String(c.params[b]) === next[b]));
      if (!ok.some((c) => String(c.params[q]) === next[q])) next[q] = ok[0] ? String(ok[0].params[q]) : "";
    }
    setParams(next);
  };
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-end gap-3 text-sm">
        <label className="flex flex-col text-xs text-muted">
          Template
          <select value={name} onChange={(e) => setName(e.target.value)} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink">
            {gallery.map((g) => (
              <option key={g.template} value={g.template}>
                {g.title}
              </option>
            ))}
          </select>
        </label>
        {names.map((p) => (
          <label key={p} className="flex flex-col text-xs text-muted">
            {paramWords(p)}
            <select value={params[p] ?? ""} onChange={(e) => set(p, e.target.value)} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink">
              {choices(p).map((v) => (
                <option key={v} value={v}>
                  {paramWords(v)}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      {tpl ? <p className="mb-3 max-w-3xl text-xs text-muted">{tpl.method}</p> : null}
      {err ? <p className="text-sm text-muted">{err}</p> : null}
      {chart ? (
        <figure>
          <h3 className="text-lg">{chart.title}</h3>
          <p className="text-xs text-muted">{chart.subtitle}</p>
          <EChartOption option={chart.option} label={chart.title} />
          <ul className="mt-2 list-disc pl-5 text-xs">
            {chart.facts.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
          <figcaption className="mt-2 text-xs text-muted">
            {chart.source_line} Computed {chart.computed_at.replace("T", " ").replace("Z", " UTC")}.
          </figcaption>
        </figure>
      ) : null}
    </div>
  );
}
