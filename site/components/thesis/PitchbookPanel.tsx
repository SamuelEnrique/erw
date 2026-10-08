"use client";
// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis), the PitchBook panel of a finished run.
// Until the answer arrives: the companies asked for, the request to paste into a Claude chat that holds a PitchBook
// connector (read-only, with a Copy button for that text alone), and a box for the answer, which goes to
// POST /api/thesis/pitchbook under the run's one-time key (the pasted JSON may carry its own "key"). The route checks
// and labels the answer; what it refuses is said here in its own words. Once received: the day the figures were pulled.
//
// Session 150: the stage takes three providers, and the person chooses one before copying the request: PitchBook
// (first, and chosen when the panel opens, as before), Harmonic or Crunchbase (lib/thesis/providers.ts). The request
// text changes with the choice: PitchBook's is the text the run saved, as it is; the other two are made here from the
// companies and the search the run saved. The answer box takes only the format of the provider chosen: an answer in
// another provider's format is not sent anywhere, and the panel says which format it was given. PitchBook's answer
// goes where it always went, unchanged; the other two go to POST /api/thesis/provider. A provider whose answer the
// run holds reads "received" and cannot be chosen again. Nothing the panel showed before is dropped.
//
// Session 158: a provider whose answers are not kept (NOT_KEPT in lib/thesis/providers.ts: Crunchbase, until its terms
// are ruled on) stays in the choice, but cannot be chosen: its button is off and a short mark beside it reads "not yet
// available", the plain reason on hover. Its request text is never put in the box, so it cannot be copied. A run that
// already holds such a provider's answer shows it as received, as before.
import { useRouter } from "next/navigation";
import { useState } from "react";
import { extractJson, type PitchbookPayload } from "@/lib/thesis/pitchbook";
import { NOT_KEPT_MARK, PROVIDERS, PROVIDER_IDS, formatFault, notKept, providerOfFormat, type ProviderId } from "@/lib/thesis/providers";
import type { PitchbookRequest } from "@/lib/thesis/types";
import { PB_PENDING, arr, str, whenWords } from "@/lib/thesis/view";

/** What the panel says of an answer of Harmonic or Crunchbase the run holds (worked out on the server). */
export type ProviderReceived = { provider: ProviderId; pulled_on: string; pasted_at: string | null; found: number; asked: number; more: number; lists: number; not_mapped: number };

export function PitchbookPanel({ runId, niche = "", request, pitchbookKey, pitchbook, receivedAt, others = [] }: {
  runId: string; niche?: string; request: PitchbookRequest | null; pitchbookKey: string | null; pitchbook: PitchbookPayload | null; receivedAt: string | null; others?: ProviderReceived[];
}) {
  const router = useRouter();
  const [picked, setPicked] = useState<ProviderId>("pitchbook");
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [said, setSaid] = useState("");
  const [copied, setCopied] = useState(false);

  const have = (id: ProviderId) => (id === "pitchbook" ? !!pitchbook : others.some((o) => o.provider === id));
  const open = PROVIDER_IDS.filter((id) => !have(id) && !notKept(id));       // session 158: one whose answers are not kept is never open
  // the provider chosen: the one picked while it is still open, otherwise the first that is (PitchBook first)
  const chosen: ProviderId | null = open.includes(picked) ? picked : open[0] ?? null;
  const provider = chosen ? PROVIDERS[chosen] : null;
  const asked = arr(request?.companies);
  const paste = provider && request ? provider.requestText({ run_id: runId, niche, request }) : "";
  const any = !!pitchbook || others.length > 0;

  const received = (
    <>
      {pitchbook ? (
        <>
          <h2 className="font-serif text-lg text-accent">PitchBook received</h2>
          <p className="text-xs text-muted">
            Pulled on <span data-thesis-pulled="1">{whenWords(str(pitchbook.pulled_on))}</span>
            {receivedAt ? <span>, submitted {whenWords(receivedAt)}</span> : null}
            : {arr(pitchbook.companies).filter((c) => c?.found).length} of {arr(pitchbook.companies).length} companies found
            {arr(pitchbook.additional_companies).length ? `, ${arr(pitchbook.additional_companies).filter((c) => c?.found).length} more found by PitchBook` : ""}.
          </p>
        </>
      ) : null}
      {others.map((o, i) => { const label = PROVIDERS[o.provider].label;
        return (
          <div key={o.provider} className={pitchbook || i ? "mt-2" : ""} data-thesis-provider-received={o.provider}>
            <h2 className="font-serif text-lg text-accent">{label} received</h2>
            <p className="text-xs text-muted">
              Pulled on <span>{whenWords(o.pulled_on)}</span>
              {o.pasted_at ? <span>, submitted {whenWords(o.pasted_at)}</span> : null}
              : {o.found} of {o.asked} companies found
              {o.more ? `, ${o.more} more found by ${label}` : ""}{o.lists ? `, ${o.lists} saved ${o.lists === 1 ? "search" : "searches"}` : ""}
              {o.not_mapped ? <span className="cursor-help border-b border-dotted border-muted" title={`${label} returned ${o.not_mapped} ${o.not_mapped === 1 ? "field" : "fields"} this page does not use. Each is kept as given and listed beside its company.`} data-thesis-not-mapped={o.not_mapped}>, {o.not_mapped} not mapped</span> : null}.
            </p>
          </div>
        ); })}
    </>
  );
  if (!request || !provider || !chosen) {
    if (!any) return null;
    return <section className="mb-5 border border-rule bg-panel px-3 py-2 text-sm" aria-label="PitchBook" data-thesis-pitchbook={pitchbook ? "received" : "pending"}>{received}</section>;
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(paste);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setSaid("The text could not be copied: select it in the box and copy it by hand.");
    }
  }
  async function send(url: string, body: unknown): Promise<{ ok: boolean; reason: string }> {
    const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), cache: "no-store" });
    const r = (await res.json().catch(() => null)) as { ok?: boolean; reason?: string } | null;
    return { ok: res.ok && !!r?.ok, reason: r?.reason || "The answer could not be stored." };
  }
  async function submit() {
    if (busy || !chosen) return;
    const got = extractJson(answer);
    if (!got.ok) {
      setSaid(got.reason);
      return;
    }
    const value = got.value as Record<string, unknown>;
    // an answer in another provider's format is not sent anywhere: the panel says which format it was given
    const fault = formatFault(chosen, value.format);
    if (fault && (chosen !== "pitchbook" || providerOfFormat(value.format))) {
      setSaid(fault);
      return;
    }
    let key: string | null = null, payload: Record<string, unknown> = {};
    if (chosen === "pitchbook") {
      const { key: inside, ...rest } = value;
      payload = rest;
      key = typeof inside === "string" && inside.trim() ? inside.trim() : pitchbookKey;
      if (!key) {
        setSaid("This run holds no key to submit under.");
        return;
      }
    }
    setBusy(true);
    setSaid("");
    try {
      // PitchBook's answer goes where it has gone since session 135, as it did. The others go to the providers' route.
      const r = chosen === "pitchbook" ? await send("/api/thesis/pitchbook", { run_id: runId, key, payload }) : await send("/api/thesis/provider", { run_id: runId, provider: chosen, pasted: answer });
      if (r.ok) {
        // for PitchBook the hash of the pasted text is then recorded beside the answer; a record that could not be
        // written changes nothing but the hover of the label, which then says the hash is not held
        if (chosen === "pitchbook") await send("/api/thesis/provider", { run_id: runId, provider: chosen, pasted: answer }).catch(() => null);
        setAnswer("");
        router.refresh();
        return;
      }
      setSaid(r.reason);
    } catch {
      setSaid("The answer could not be stored.");
    } finally {
      setBusy(false);
    }
  }

  const box = "w-full border border-rule bg-white px-2 py-1.5 font-mono text-xs text-ink focus:border-accent focus:outline-none";
  const button = "border border-accent px-3 py-1 text-xs font-semibold disabled:opacity-60";
  return (
    <section className="mb-5 border border-rule bg-panel px-3 py-3 text-sm" aria-label="PitchBook" data-thesis-pitchbook={pitchbook ? "received" : "pending"} data-thesis-provider={chosen}>
      {any ? <div className="mb-3 border-b border-rule pb-2">{received}</div> : null}
      <h2 className="font-serif text-lg text-accent">{pitchbook ? "Another data provider" : PB_PENDING}</h2>
      <p className="mb-1 mt-1 text-xs text-muted">Asked for {asked.length} {asked.length === 1 ? "company" : "companies"}</p>
      <ul className="mb-3 flex flex-wrap gap-1 text-xs" data-thesis-asked="1">
        {asked.map((c, i) => (
          <li key={`${str(c?.name)}|${i}`} className="border border-rule bg-white px-1.5 py-px" title={[str(c?.website), arr(c?.lookups).join(", ")].filter(Boolean).join(": ")}>{str(c?.name)}</li>
        ))}
      </ul>
      <fieldset className="mb-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs" data-thesis-providers="1">
        <legend className="mb-1 text-xs text-muted">Data provider</legend>
        {PROVIDER_IDS.map((id) => { const p = PROVIDERS[id], done = have(id), off = done ? null : notKept(id);
          return (
            <label key={id} className={`inline-flex items-center gap-1 ${done || off ? "text-muted" : "cursor-pointer"}`} title={p.terms}>
              <input type="radio" name="thesis-provider" value={id} checked={id === chosen} disabled={done || busy || !!off} onChange={() => { setPicked(id); setSaid(""); setCopied(false); }} data-thesis-provider-choice={id} />
              <span className={id === chosen ? "font-semibold" : ""}>{p.label}</span>
              {done ? <span className="italic">received</span> : null}
              {off ? <span className="cursor-help whitespace-nowrap border-b border-dotted border-muted text-[11px] italic" title={off} data-thesis-provider-unavailable={id}>{NOT_KEPT_MARK}</span> : null}
            </label>
          ); })}
      </fieldset>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="min-w-0">
          <div className="mb-1 flex items-baseline justify-between gap-2">
            <label htmlFor="thesis-paste" className="text-xs text-muted">Paste this into a Claude chat that has a {provider.label} connector</label>
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
