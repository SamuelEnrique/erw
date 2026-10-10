"use client";
// Session 181: the three rulings on a scanner draft at /internal/findings: Approve (the card appears on /analysis,
// marked as the scanner's), Dismiss (it never appears), Ask for a full card (an analysis is queued for the data
// machine where the flag's series is one the impact study knows; otherwise the draft waits, marked, for a session to
// write the card). Each change is a POST to /internal/findings/state, which checks the internal cookie; the database
// keeps every change with its time.
import { useState } from "react";

type State = "draft" | "approved" | "dismissed" | "full_card_asked";
type Change = { state: State; from: State; at: string };
const WORDS: Record<State, string> = { draft: "Draft, not reviewed", approved: "Approved", dismissed: "Dismissed", full_card_asked: "Full card asked" };
const BUTTONS: { state: State; label: string }[] = [
  { state: "approved", label: "Approve" }, { state: "dismissed", label: "Dismiss" }, { state: "full_card_asked", label: "Ask for a full card" },
];
const when = (iso: string) => iso.replace("T", " ").slice(0, 16) + " UTC";

export function DraftReview({ id, state: first, history: firstHistory, requestId, fullCard }: { id: string; state: State; history: Change[]; requestId: string | null; fullCard: string }) {
  const [state, setState] = useState<State>(first);
  const [history, setHistory] = useState<Change[]>(firstHistory);
  const [note, setNote] = useState(requestId ? `request ${requestId}` : "");
  const [busy, setBusy] = useState(false);
  const rule = async (to: State) => {
    setBusy(true);
    try {
      const r = await fetch("/internal/findings/state", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id, state: to }) });
      const j = (await r.json()) as { ok: boolean; reason?: string; state?: State; from?: State; at?: string; note?: string };
      if (j.ok && j.state && j.at) {
        setHistory([...history, { state: j.state, from: j.from ?? state, at: j.at }]);
        setState(j.state);
        setNote(j.note ?? "");
      } else setNote(j.reason ?? "not changed");
    } catch (e) {
      setNote((e as Error).message);
    }
    setBusy(false);
  };
  return (
    <div className="mt-3 border-t border-rule pt-3 text-sm" data-draft-review={id} data-draft-state={state}>
      <div className="flex flex-wrap items-center gap-2">
        <strong data-draft-state-words="1">{WORDS[state]}</strong>
        {BUTTONS.map((b) => (
          <button key={b.state} type="button" disabled={busy || state === b.state} onClick={() => rule(b.state)} data-draft-button={b.state}
            className="border border-rule bg-panel px-3 py-1 text-sm text-ink hover:border-ink disabled:opacity-50">
            {b.label}
          </button>
        ))}
      </div>
      <p className="mt-1 text-xs text-muted">Ask for a full card: {fullCard}</p>
      {note ? <p className="mt-1 text-xs text-muted" data-draft-note="1">{note}</p> : null}
      {history.length ? (
        <p className="mt-1 text-xs text-muted" data-draft-history={history.length}>
          {history.map((h) => `${WORDS[h.state].toLowerCase()} ${when(h.at)}`).join("; ")}
        </p>
      ) : null}
    </div>
  );
}
