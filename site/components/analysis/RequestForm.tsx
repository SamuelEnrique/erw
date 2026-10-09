"use client";
// Session 170: ask for a finding with chosen inputs. The request waits in a queue (a row of the request table, migration
// 026) and runs on the data machine, the laptop that holds the full histories; the card appears in 1 to 5 minutes when
// the machine is awake. When it is off the row stays queued and this form says so, with the time it was asked; the
// worker (warehouse/analysis/findings/worker.py) takes it when the machine wakes. No typed free text: inputs are chosen.
import { useEffect, useState } from "react";
import type { CatalogueEntry } from "@/lib/findings";

type Req = { id: string; finding: string; params: Record<string, string>; status: string; asked_at: string; done_at: string | null; note: string; card_id: string | null };

const when = (iso: string) => iso.replace("T", " ").slice(0, 16) + " UTC";
const STATUS: Record<string, string> = { queued: "queued, waits for the data machine", running: "running on the data machine", done: "done", failed: "failed" };

export function RequestForm({ catalogue }: { catalogue: CatalogueEntry[] }) {
  const [name, setName] = useState(catalogue[0]?.id ?? "");
  const entry = catalogue.find((c) => c.id === name);
  const [params, setParams] = useState<Record<string, string>>({});
  useEffect(() => {
    if (entry) setParams(Object.fromEntries(Object.entries(entry.inputs).map(([k, v]) => [k, String(v.default)])));
  }, [entry]);
  const [reqs, setReqs] = useState<Req[] | null>(null);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const load = async () => {
    try {
      const r = await fetch("/api/analysis", { cache: "no-store" });
      if (r.ok) setReqs(((await r.json()) as { requests: Req[] }).requests);
      else setReqs([]);
    } catch { setReqs([]); }
  };
  useEffect(() => { load(); const t = setInterval(load, 20000); return () => clearInterval(t); }, []);
  const submit = async () => {
    if (!entry) return;
    setBusy(true); setNote("");
    try {
      const r = await fetch("/api/analysis", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind: "run", finding: entry.id, params }) });
      const j = (await r.json()) as { ok: boolean; reason?: string; id?: string };
      setNote(j.ok ? `queued at ${when(new Date().toISOString())}: the card appears here in 1 to 5 minutes when the data machine is awake` : (j.reason ?? "not queued"));
      load();
    } catch (e) { setNote((e as Error).message); }
    setBusy(false);
  };
  if (!catalogue.length) return <p className="text-sm text-muted">No finding is in the catalogue yet.</p>;
  return (
    <div data-request-form="1">
      <div className="mb-3 flex flex-wrap items-end gap-3 text-sm">
        <label className="flex flex-col text-xs text-muted">
          Finding
          <select value={name} onChange={(e) => setName(e.target.value)} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink" data-request-finding="1">
            {catalogue.map((c) => <option key={c.id} value={c.id}>{c.title} ({c.kind})</option>)}
          </select>
        </label>
        {entry ? Object.entries(entry.inputs).map(([k, inp]) => (
          <label key={k} className="flex flex-col text-xs text-muted">
            {inp.label}
            <select value={params[k] ?? ""} onChange={(e) => setParams({ ...params, [k]: e.target.value })} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink" data-request-input={k}>
              {inp.choices.map((v) => <option key={String(v)} value={String(v)}>{inp.words?.[String(v)] ?? String(v)}</option>)}
            </select>
          </label>
        )) : null}
        <button type="button" onClick={submit} disabled={busy} className="border border-rule bg-panel px-3 py-1 text-sm text-ink hover:border-ink disabled:opacity-60" data-request-submit="1">
          Ask the warehouse
        </button>
      </div>
      {note ? <p className="mb-2 text-xs text-muted" data-request-note="1">{note}</p> : null}
      {reqs === null ? <p className="text-xs text-muted">Reading the queue.</p> : reqs.length === 0 ? (
        <p className="text-xs text-muted" data-request-rows="0">No request waits. A request runs on the data machine; when it is off, the row stays queued here with the time it was asked.</p>
      ) : (
        <table className="w-full max-w-3xl text-xs" data-request-rows={reqs.length}>
          <thead><tr className="border-b border-rule text-left text-muted"><th className="py-1 pr-3">Finding</th><th className="py-1 pr-3">Inputs</th><th className="py-1 pr-3">Asked</th><th className="py-1 pr-3">State</th><th className="py-1">Card</th></tr></thead>
          <tbody>
            {reqs.map((r) => (
              <tr key={r.id} className="border-b border-rule" data-request-id={r.id} data-request-status={r.status}>
                <td className="py-1 pr-3">{catalogue.find((c) => c.id === r.finding)?.title ?? r.finding}</td>
                <td className="py-1 pr-3">{Object.entries(r.params).map(([k, v]) => `${k}: ${catalogue.find((c) => c.id === r.finding)?.inputs[k]?.words?.[v] ?? v}`).join(", ")}</td>
                <td className="py-1 pr-3 font-mono">{when(r.asked_at)}</td>
                <td className="py-1 pr-3">{STATUS[r.status] ?? r.status}{r.note ? `: ${r.note}` : ""}</td>
                <td className="py-1">{r.card_id ? <a href={`/analysis/card/${r.card_id}`}>{r.card_id}</a> : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
