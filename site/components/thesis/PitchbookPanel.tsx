"use client";
// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis), the PitchBook panel of a finished run.
// Until the answer arrives: the companies asked for, the request to paste into a Claude chat that holds a PitchBook
// connector (read-only, with a Copy button for that text alone), and a box for the answer, which goes to
// POST /api/thesis/pitchbook under the run's one-time key (the pasted JSON may carry its own "key"). The route checks
// and labels the answer; what it refuses is said here in its own words. Once received: the day the figures were pulled.
import { useRouter } from "next/navigation";
import { useState } from "react";
import { extractJson, type PitchbookPayload } from "@/lib/thesis/pitchbook";
import type { PitchbookRequest } from "@/lib/thesis/types";
import { PB_PENDING, arr, str, whenWords } from "@/lib/thesis/view";

export function PitchbookPanel({ runId, request, pitchbookKey, pitchbook, receivedAt }: {
  runId: string; request: PitchbookRequest | null; pitchbookKey: string | null; pitchbook: PitchbookPayload | null; receivedAt: string | null;
}) {
  const router = useRouter();
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [said, setSaid] = useState("");
  const [copied, setCopied] = useState(false);

  if (pitchbook) {
    return (
      <section className="mb-5 border border-rule bg-panel px-3 py-2 text-sm" aria-label="PitchBook" data-thesis-pitchbook="received">
        <h2 className="font-serif text-lg text-accent">PitchBook received</h2>
        <p className="text-xs text-muted">
          Pulled on <span data-thesis-pulled="1">{whenWords(str(pitchbook.pulled_on))}</span>
          {receivedAt ? <span>, submitted {whenWords(receivedAt)}</span> : null}
          : {arr(pitchbook.companies).filter((c) => c?.found).length} of {arr(pitchbook.companies).length} companies found
          {arr(pitchbook.additional_companies).length ? `, ${arr(pitchbook.additional_companies).filter((c) => c?.found).length} more found by PitchBook` : ""}.
        </p>
      </section>
    );
  }
  if (!request) return null;
  const asked = arr(request.companies);
  const paste = str(request.paste_text);

  async function copy() {
    try {
      await navigator.clipboard.writeText(paste);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setSaid("The text could not be copied: select it in the box and copy it by hand.");
    }
  }
  async function submit() {
    if (busy) return;
    const got = extractJson(answer);
    if (!got.ok) {
      setSaid(got.reason);
      return;
    }
    const { key: inside, ...payload } = got.value as Record<string, unknown>;
    const key = typeof inside === "string" && inside.trim() ? inside.trim() : pitchbookKey;
    if (!key) {
      setSaid("This run holds no key to submit under.");
      return;
    }
    setBusy(true);
    setSaid("");
    try {
      const res = await fetch("/api/thesis/pitchbook", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ run_id: runId, key, payload }), cache: "no-store" });
      const r = (await res.json().catch(() => null)) as { ok?: boolean; reason?: string } | null;
      if (res.ok && r?.ok) {
        setAnswer("");
        router.refresh();
        return;
      }
      setSaid(r?.reason || "The answer could not be stored.");
    } catch {
      setSaid("The answer could not be stored.");
    } finally {
      setBusy(false);
    }
  }

  const box = "w-full border border-rule bg-white px-2 py-1.5 font-mono text-xs text-ink focus:border-accent focus:outline-none";
  const button = "border border-accent px-3 py-1 text-xs font-semibold disabled:opacity-60";
  return (
    <section className="mb-5 border border-rule bg-panel px-3 py-3 text-sm" aria-label="PitchBook" data-thesis-pitchbook="pending">
      <h2 className="font-serif text-lg text-accent">{PB_PENDING}</h2>
      <p className="mb-1 mt-1 text-xs text-muted">Asked for {asked.length} {asked.length === 1 ? "company" : "companies"}</p>
      <ul className="mb-3 flex flex-wrap gap-1 text-xs" data-thesis-asked="1">
        {asked.map((c, i) => (
          <li key={`${str(c?.name)}|${i}`} className="border border-rule bg-white px-1.5 py-px" title={[str(c?.website), arr(c?.lookups).join(", ")].filter(Boolean).join(": ")}>{str(c?.name)}</li>
        ))}
      </ul>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="min-w-0">
          <div className="mb-1 flex items-baseline justify-between gap-2">
            <label htmlFor="thesis-paste" className="text-xs text-muted">Paste this into a Claude chat that has a PitchBook connector</label>
            <button type="button" onClick={copy} disabled={!paste} className={`${button} bg-white text-accent`} data-thesis-copy="1">{copied ? "Copied" : "Copy"}</button>
          </div>
          <textarea id="thesis-paste" readOnly value={paste} rows={9} className={box} onFocus={(e) => e.currentTarget.select()} data-thesis-paste="1" />
        </div>
        <div className="min-w-0">
          <div className="mb-1 flex items-baseline justify-between gap-2">
            <label htmlFor="thesis-answer" className="text-xs text-muted">Paste Claude&apos;s answer here</label>
            <button type="button" onClick={submit} disabled={busy || !answer.trim()} className={`${button} bg-accent text-white`} data-thesis-submit="1">{busy ? "Sending" : "Submit"}</button>
          </div>
          <textarea id="thesis-answer" value={answer} onChange={(e) => setAnswer(e.target.value)} rows={9} spellCheck={false} placeholder="Paste Claude's answer here" className={box} data-thesis-answer="1" />
        </div>
      </div>
      {said ? <p role="alert" className="mt-2 text-sm text-accent" data-thesis-said="1">{said}</p> : null}
    </section>
  );
}
