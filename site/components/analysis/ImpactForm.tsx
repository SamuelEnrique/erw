"use client";
// Session 181: the inputs of the impact study ("impact of X on Y"), self-contained so that any request flow can host
// it: a series, an event the warehouse holds or a date, a window of days before and after, and a control series.
// Each input has its default (the catalogue's, computed card on the page) and one Reset. The request is queued like
// any other (POST /api/analysis, kind run, finding impact_study) and computed by the data machine's worker; the card
// appears at /analysis/card/<id> when it is done. The form compares nothing itself and recommends nothing.
import { useContext, useState } from "react";
import type { CatalogueEntry } from "@/lib/findings";
import { RequestCard } from "./RequestCard";
import { FlowHost } from "./FlowHost";

const pad = (n: number) => String(n).padStart(2, "0");
const when = (iso: string) => iso.replace("T", " ").slice(0, 16) + " UTC";

// Session 182, part 4: the request flow hosts this form (FlowHost). The flow places step two, the picker of chart
// forms, between the inputs and the Ask button, and is told which request was queued, so that the address keeps it.
// Outside the flow the form is what it was.
export function ImpactForm({ entry }: { entry: CatalogueEntry }) {
  const host = useContext(FlowHost);
  const defaults = Object.fromEntries(Object.entries(entry.inputs).map(([k, v]) => [k, String(v.default)]));
  const [p, setP] = useState<Record<string, string>>(defaults);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [asked, setAsked] = useState("");       // the request this form queued: its card is drawn below when it is done
  const set = (k: string, v: string) => setP({ ...p, [k]: v });
  const years = entry.inputs.year?.choices.map(Number) ?? [];
  const date = `${p.year}-${pad(Number(p.month))}-${pad(Number(p.day))}`;
  const setDate = (v: string) => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v);
    if (m) setP({ ...p, year: String(Number(m[1])), month: String(Number(m[2])), day: String(Number(m[3])) });
  };
  const same = p.series === p.control;
  const select = (k: string, label: string) => (
    <label className="flex min-w-0 flex-col text-xs text-muted">
      {label}
      <select value={p[k]} onChange={(e) => set(k, e.target.value)} className="mt-1 w-full border border-rule bg-panel px-2 py-1 text-sm text-ink" data-impact-input={k}>
        {entry.inputs[k].choices.map((v) => <option key={String(v)} value={String(v)}>{entry.inputs[k].words?.[String(v)] ?? String(v)}</option>)}
      </select>
    </label>
  );
  const submit = async () => {
    setBusy(true); setNote("");
    try {
      const r = await fetch("/api/analysis", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ kind: "run", finding: entry.id, params: p }) });
      const j = (await r.json()) as { ok: boolean; reason?: string; id?: string };
      setNote(j.ok ? `queued at ${when(new Date().toISOString())} (request ${j.id}): the card appears below in 1 to 5 minutes when the data machine is awake` : (j.reason ?? "not queued"));
      setAsked(j.ok && j.id ? j.id : "");
      if (j.ok && j.id) host?.onAsked(j.id);
    } catch (e) { setNote((e as Error).message); }
    setBusy(false);
  };
  return (
    <div data-impact-form="1">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {select("series", "Series (Y)")}
        {select("control", "Control series")}
        {select("event", "Event (X), or a date")}
        {p.event === "date" ? (
          <label className="flex min-w-0 flex-col text-xs text-muted">
            The date
            <input type="date" value={date} min={`${years[0]}-01-01`} max={`${years[years.length - 1]}-12-31`} onChange={(e) => setDate(e.target.value)}
              className="mt-1 w-full border border-rule bg-panel px-2 py-1 text-sm text-ink" data-impact-input="date" />
          </label>
        ) : null}
        {select("window", "Window: days before and after")}
      </div>
      {same ? <p className="mt-2 text-xs text-accent" data-impact-same="1">The control is the series itself: the card would be refused. Pick another control.</p> : null}
      {host?.between ?? null}
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <button type="button" onClick={submit} disabled={busy} className="min-h-[44px] border border-rule bg-panel px-3 py-1 text-sm text-ink hover:border-ink disabled:opacity-60" data-impact-submit="1">
          Ask the warehouse
        </button>
        <button type="button" onClick={() => { setP(defaults); setNote(""); setAsked(""); }} className="min-h-[44px] border border-rule bg-panel px-3 py-1 text-sm text-ink hover:border-ink" data-impact-reset="1">
          Reset
        </button>
        <span className="text-xs text-muted">
          Defaults: {entry.inputs.series.words[defaults.series]}, {entry.inputs.event.words[defaults.event]}, {defaults.window} days, control {entry.inputs.control.words[defaults.control]}.
        </span>
      </div>
      {note ? <p className="mt-2 text-xs text-muted" data-impact-note="1">{note}</p> : null}
      {asked ? <RequestCard key={asked} requestId={asked} wait /> : null}
    </div>
  );
}
