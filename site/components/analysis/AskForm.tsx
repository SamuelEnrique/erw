"use client";
// Session 315 (the owner's ruling of 13 October 2026, the Research tool's layout, built by the chain of 19 October):
// the request form first on /research: what a reader asks the warehouse to analyse, in their own words: the question,
// the tables it should read (chosen from the public tables of the live set, as many as the reader wants) and an email
// for the answer. It writes one row of analysis_requests through the server route of session 301 (POST /api/analysis:
// kind "run", finding "reader_question", the three fields as its params), the same queue the finding requests use; the
// data machine's worker leaves such a row alone (warehouse/analysis/findings/worker.py), and a person answers it by
// email. Nothing is computed here, and nothing is stored before the reader presses the button. The email is stored
// with the request and used for the answer alone; the page says so beside the field.
import { useState } from "react";
import { ASKED_EVENT } from "./RequestFlow";

export const QUESTION_MAX = 500, EMAIL_MAX = 120, TABLES_MAX = 10;
const when = (iso: string) => iso.replace("T", " ").slice(0, 16) + " UTC";
/** A plain check of an address's shape: one @, something on each side, a dot after it. */
export const emailOk = (s: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s.trim()) && s.trim().length <= EMAIL_MAX;

export function AskForm({ tables }: { tables: string[] }) {
  const [question, setQuestion] = useState("");
  const [chosen, setChosen] = useState<string[]>([]);
  const [email, setEmail] = useState("");
  const [filter, setFilter] = useState("");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [asked, setAsked] = useState("");
  const shown = tables.filter((t) => !filter.trim() || t.includes(filter.trim().toLowerCase()));
  const toggle = (t: string) => setChosen(chosen.includes(t) ? chosen.filter((x) => x !== t) : chosen.length < TABLES_MAX ? [...chosen, t].sort() : chosen);
  const ready = question.trim().length >= 10 && question.length <= QUESTION_MAX && emailOk(email);
  const submit = async () => {
    if (!ready) return;
    setBusy(true); setNote("");
    try {
      const r = await fetch("/api/analysis", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind: "run", finding: "reader_question", params: { question: question.trim(), tables: chosen.join(","), email: email.trim() } }) });
      const j = (await r.json()) as { ok: boolean; reason?: string; id?: string };
      if (j.ok && j.id) {
        setAsked(j.id); setNote(`Asked at ${when(new Date().toISOString())} (request ${j.id}). The answer comes by email; the request is listed below with the others.`);
        window.dispatchEvent(new Event(ASKED_EVENT));
      } else setNote(j.reason ?? "not asked");
    } catch (e) { setNote((e as Error).message); }
    setBusy(false);
  };
  const field = "mt-1 w-full max-w-full border border-rule bg-panel px-2 py-2 text-sm text-ink";
  return (
    <form className="max-w-3xl" data-ask-form="1" onSubmit={(e) => { e.preventDefault(); void submit(); }}>
      <label className="block text-xs text-muted">
        Your question: what should the warehouse analyse?
        <textarea value={question} onChange={(e) => setQuestion(e.target.value.slice(0, QUESTION_MAX))} rows={3} className={field} maxLength={QUESTION_MAX}
          placeholder="For example: how often did ERCOT's real-time price fall below zero in each month of 2025, and in which hours?" data-ask-question="1" />
        <span className="mt-0.5 block text-right" data-ask-count="1">{question.length} of {QUESTION_MAX}</span>
      </label>
      <fieldset className="mt-3" data-ask-tables={chosen.join(",")}>
        <legend className="text-xs text-muted">The tables to read (optional, up to {TABLES_MAX}): the public tables of the live set, by name. <a href="/data" className="underline">What each holds</a>.</legend>
        <input type="search" value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Find a table by name" aria-label="Find a table by name" className={`${field} max-w-xs`} data-ask-filter="1" />
        <div className="mt-2 flex max-h-40 flex-wrap gap-1.5 overflow-y-auto border border-rule bg-panel p-2 text-xs" data-ask-table-list={shown.length}>
          {shown.length === 0 ? <span className="text-muted">No table of that name.</span> : shown.map((t) => (
            <button key={t} type="button" aria-pressed={chosen.includes(t)} onClick={() => toggle(t)} data-ask-table={t}
              className={`border px-2 py-0.5 font-mono ${chosen.includes(t) ? "border-ink bg-ink text-white" : "border-rule bg-white text-ink hover:border-ink"}`}>{t}</button>
          ))}
        </div>
        {chosen.length ? <p className="mt-1 text-xs text-muted" data-ask-chosen={chosen.length}>Chosen: {chosen.join(", ")}.</p> : null}
      </fieldset>
      <label className="mt-3 block text-xs text-muted">
        Your email, for the answer
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value.slice(0, EMAIL_MAX))} className={`${field} max-w-sm`} autoComplete="email" data-ask-email="1" />
        <span className="mt-0.5 block">Stored with the request and used to send the answer; nothing else is done with it, and it is shown to no visitor.</span>
      </label>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <button type="submit" disabled={!ready || busy || Boolean(asked)} className="min-h-[44px] border border-rule bg-panel px-3 py-1 text-sm text-ink hover:border-ink disabled:opacity-60" data-ask-submit="1">
          Ask the warehouse
        </button>
        {!ready && !asked ? <span className="text-xs text-muted" data-ask-why="1">{question.trim().length < 10 ? "A question of at least ten characters" : !emailOk(email) ? "and an email address" : ""}</span> : null}
      </div>
      {note ? <p className="mt-2 text-xs text-muted" data-ask-note="1">{note}</p> : null}
    </form>
  );
}
