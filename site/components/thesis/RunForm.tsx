"use client";
// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis), the form that asks for a run. It sends
// the niche, and a stage and a geography when given, to POST /api/thesis/run; when the run is queued the address
// becomes /thesis?run=<its id> and the page shows its state.
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

export function RunForm() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [said, setSaid] = useState("");

  async function send(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy) return;
    const f = new FormData(e.currentTarget);
    const body = { niche: String(f.get("niche") ?? ""), stage: String(f.get("stage") ?? ""), geography: String(f.get("geography") ?? "") };
    setBusy(true);
    setSaid("");
    try {
      const res = await fetch("/api/thesis/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), cache: "no-store", credentials: "same-origin" });
      if (res.status === 404) {
        setSaid("The internal view is not open in this browser.");
        return;
      }
      const r = (await res.json().catch(() => null)) as { ok?: boolean; run_id?: string; reason?: string } | null;
      if (r && r.ok && r.run_id) {
        router.push(`/thesis?run=${encodeURIComponent(r.run_id)}`);
        router.refresh();
        return;
      }
      setSaid(r?.reason || "The run could not be queued.");
    } catch {
      setSaid("The run could not be queued.");
    } finally {
      setBusy(false);
    }
  }

  const input = "w-full border border-rule bg-white px-2 py-1.5 text-sm text-ink focus:border-accent focus:outline-none";
  return (
    <form onSubmit={send} className="grid gap-3 sm:grid-cols-[minmax(0,3fr)_minmax(0,1fr)_minmax(0,1fr)_auto] sm:items-end" data-thesis-form="1">
      <label className="block min-w-0 text-xs text-muted">Niche
        <input name="niche" type="text" required minLength={8} maxLength={400} autoComplete="off" placeholder="For example: long-duration storage for data centers" className={`mt-0.5 ${input}`} />
      </label>
      <label className="block min-w-0 text-xs text-muted">Stage <span className="text-[10px]">(optional)</span>
        <input name="stage" type="text" maxLength={80} autoComplete="off" placeholder="Seed to Series B" className={`mt-0.5 ${input}`} />
      </label>
      <label className="block min-w-0 text-xs text-muted">Geography <span className="text-[10px]">(optional)</span>
        <input name="geography" type="text" maxLength={80} autoComplete="off" placeholder="United States" className={`mt-0.5 ${input}`} />
      </label>
      <button type="submit" disabled={busy} className="border border-accent bg-accent px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-60" data-thesis-run="1">{busy ? "Sending" : "Run"}</button>
      {said ? <p role="alert" className="text-sm text-accent sm:col-span-4" data-thesis-said="1">{said}</p> : null}
    </form>
  );
}
