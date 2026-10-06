"use client";
// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis). While a run is queued or running the
// page says so in plain words and asks GET /api/thesis/run?id= for its state every 15 seconds; when the state changes
// the page is read again, so a finished run shows its report without anyone reloading.
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export const EVERY_MS = 15_000;
const WORDS: Record<string, string> = {
  queued: "Queued. The run is waiting to start.",
  running: "Running. The report is being written.",
};

export function RunWatch({ runId, status }: { runId: string; status: "queued" | "running" }) {
  const router = useRouter();
  const [read, setRead] = useState<{ at: string; ok: boolean } | null>(null);

  useEffect(() => {
    let alive = true;
    const ask = async () => {
      try {
        const res = await fetch(`/api/thesis/run?id=${encodeURIComponent(runId)}`, { cache: "no-store", credentials: "same-origin" });
        const r = res.ok ? ((await res.json()) as { status?: string }) : null;
        if (!alive) return;
        setRead({ at: new Date().toISOString().slice(11, 19), ok: !!r });
        if (r && r.status && r.status !== status) router.refresh();
      } catch {
        if (alive) setRead({ at: new Date().toISOString().slice(11, 19), ok: false });
      }
    };
    const timer = setInterval(ask, EVERY_MS);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [runId, status, router]);

  return (
    <div className="border border-rule bg-panel px-3 py-2 text-sm" role="status" aria-live="polite" data-thesis-watch={status}>
      <p className="font-semibold">{WORDS[status]}</p>
      <p className="mt-0.5 text-xs text-muted">
        Read again every 15 seconds.
        {read ? <span data-thesis-read="1"> Last read {read.at} UTC{read.ok ? "" : ": the state could not be read"}.</span> : null}
      </p>
    </div>
  );
}
