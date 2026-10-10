"use client";
// Session 181: the scanner's approved drafts on /analysis, in their own group, each marked "Found by the scanner" with
// the date it flagged and the day it was approved. Read from /internal/findings/approved, which answers only the
// internal view: a draft appears here after a person approved it at /internal/findings, never before, and a
// dismissed draft never does. The cards are the scanner's own (chart, callouts, footnote computed by code; no paragraph).
import { useEffect, useState } from "react";
import { FindingCard } from "./FindingCard";
import type { Card } from "@/lib/findings";

type Found = { id: string; flag_date: string; approved_at: string; card: Card };

export function ScannerFound() {
  const [found, setFound] = useState<Found[] | null>(null);
  useEffect(() => {
    const t = setTimeout(() => {
      fetch("/internal/findings/approved", { cache: "no-store" })
        .then(async (r) => setFound(r.ok ? ((await r.json()) as { drafts: Found[] }).drafts : []))
        .catch(() => setFound([]));
    }, 0);
    return () => clearTimeout(t);
  }, []);
  if (found === null) return <p className="text-sm text-muted" data-scanner-cards="reading">Reading the approved drafts.</p>;
  if (found.length === 0) {
    return <p className="text-sm text-muted" data-scanner-cards="0">No draft of the scanner has been approved yet. Drafts wait at /internal/findings.</p>;
  }
  return (
    <div className="flex flex-col gap-10" data-scanner-cards={found.length}>
      {found.map((d) => <FindingCard key={d.id} card={d.card} roundup={false} found={`flagged ${d.flag_date}, approved ${d.approved_at}`} />)}
    </div>
  );
}
