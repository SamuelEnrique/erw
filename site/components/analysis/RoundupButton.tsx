"use client";
// Session 170: "Use in Roundup". The Sunday Roundup takes the chosen finding for its week, else falls back to the
// rule's chart of the week, labeled. The choice is a row of the request table (kind roundup), read by
// warehouse/news/roundup.py on the runner. Only the internal view can set it (the route checks the cookie).
import { useState } from "react";

export function RoundupButton({ cardId }: { cardId: string }) {
  const [state, setState] = useState<"idle" | "sending" | "done" | "failed">("idle");
  const [note, setNote] = useState("");
  const click = async () => {
    setState("sending");
    try {
      const r = await fetch("/api/analysis", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind: "roundup", card_id: cardId }) });
      const j = (await r.json()) as { ok: boolean; reason?: string; week?: string };
      if (j.ok) { setState("done"); setNote(`chosen for the Roundup of ${j.week}`); } else { setState("failed"); setNote(j.reason ?? "not chosen"); }
    } catch (e) {
      setState("failed"); setNote((e as Error).message);
    }
  };
  return (
    <span className="inline-flex items-center gap-2">
      <button type="button" onClick={click} disabled={state === "sending" || state === "done"} data-roundup-button={cardId}
        className="border border-rule bg-panel px-2 py-0.5 text-xs text-ink hover:border-ink disabled:opacity-60">
        {state === "done" ? "Chosen for the Roundup" : state === "sending" ? "Choosing" : "Use in Roundup"}
      </button>
      {note ? <span className="text-[11px] text-muted" data-roundup-note="1">{note}</span> : null}
    </span>
  );
}
