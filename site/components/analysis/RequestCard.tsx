"use client";
// Session 181: the card of one request, read where it was asked. A card computed on the data machine is written into
// its queue row; the deployed site holds no file of it until somebody commits one. This reads the row
// (GET /api/analysis?id=<request>, internal view only) and draws the card with the same component as every other card.
// With `wait` it asks again every 15 seconds until the request is done or has failed, and says which.
//
// The downloads of such a card are made here from what the card carries: the data as CSV from the card's own rows
// (the rows the analysis wrote, under the card's four comment lines), the Stata do-file from the card's text, and the
// Python from the site's copy of the analysis module. A card that carries no rows offers none.
import { useEffect, useState } from "react";
import { FindingCard } from "./FindingCard";
import type { Card } from "@/lib/findings";

type Row = { id: string; finding: string; status: string; note: string; asked_at: string; done_at: string | null; card_id: string | null; card: Card | null };
const WORDS: Record<string, string> = { queued: "queued: it waits for the data machine", running: "running on the data machine", failed: "failed" };

const cell = (v: string | number | null) => (v === null || v === undefined ? "" : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));

/** The card's rows as the CSV the engine writes: the comment lines, the header, one line a row. */
export function csvOf(card: Card): string {
  const rows = card.rows ?? [];
  if (!rows.length) return "";
  const cols = Object.keys(rows[0]);
  return [...(card.csv_header ?? []).map((h) => `# ${h}`), cols.join(","), ...rows.map((r) => cols.map((c) => cell(r[c])).join(","))].join("\n") + "\n";
}

function save(name: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url; a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function RequestCard({ requestId, wait = false }: { requestId: string; wait?: boolean }) {
  const [row, setRow] = useState<Row | null>(null);
  const [note, setNote] = useState("Reading the request.");
  useEffect(() => {
    let stop = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const read = async () => {
      try {
        const r = await fetch(`/api/analysis?id=${encodeURIComponent(requestId)}`, { cache: "no-store" });
        const j = (await r.json()) as { request: Row | null; reason?: string };
        if (stop) return;
        if (!j.request) { setNote(j.reason ?? "The request could not be read."); return; }
        setRow(j.request);
        setNote("");
        if (wait && (j.request.status === "queued" || j.request.status === "running")) timer = setTimeout(read, 15000);
      } catch (e) {
        if (!stop) setNote((e as Error).message);
      }
    };
    timer = setTimeout(read, 0);
    return () => { stop = true; if (timer) clearTimeout(timer); };
  }, [requestId, wait]);
  if (!row) return <p className="mt-3 text-xs text-muted" data-request-card="reading">{note}</p>;
  const card = row.card;
  if (!card) {
    return <p className="mt-3 text-xs text-muted" data-request-card={row.status}>Request {row.id}: {WORDS[row.status] ?? row.status}{row.note ? `: ${row.note}` : ""}.</p>;
  }
  const csv = csvOf(card);
  return (
    <div className="mt-4 border border-rule p-3" data-request-card="done" data-request-card-id={row.id}>
      <FindingCard card={card} roundup={false} files={false} />
      {csv ? (
        <p className="mt-2 flex flex-wrap items-center gap-3 text-xs" data-request-downloads="1">
          <span className="text-muted">Downloads:</span>
          <button type="button" className="underline" onClick={() => save(card.csv_name ?? `${card.card_id}.csv`, csv)} data-download="csv">data (CSV)</button>
          <a href={`/findings/${card.id}.py`} download data-download="python">Python</a>
          {card.do_file ? <button type="button" className="underline" onClick={() => save(`${card.card_id}.do`, card.do_file ?? "")} data-download="stata">Stata do-file</button> : null}
        </p>
      ) : null}
    </div>
  );
}
