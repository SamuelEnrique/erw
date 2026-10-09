"use client";
// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis), the form that asks for a run. It sends
// the niche, and a stage and a geography when given, to POST /api/thesis/run; when the run is queued the address
// becomes /thesis?run=<its id> and the page shows its state.
//
// Session 169, the gate on the niche (lib/thesis/niche.ts, the same module the route reads). A sector or a market
// topic is refused before a run is queued: the refusal's sentence, three to five narrower niches as chips (a click
// puts the chip in the box; Run is still the reader's to press), and a "Run anyway" box. A refusal the curated table
// answers is shown at once, with no request; any other input goes to the route, which decides and answers the same
// way. The box is unticked whenever the niche's words change, so it only ever speaks for the input it was ticked on.
import { useRouter } from "next/navigation";
import { useRef, useState, type FormEvent } from "react";
import { NICHE_EXAMPLES, NICHE_HELP, NICHE_LABEL, NICHE_PLACEHOLDER, RUN_ANYWAY, gate, refusalWords } from "@/lib/thesis/niche";

type Refusal = { message: string; suggestions: string[] };

export function RunForm() {
  const router = useRouter();
  const box = useRef<HTMLInputElement>(null);
  const [niche, setNiche] = useState("");
  const [busy, setBusy] = useState(false);
  const [said, setSaid] = useState("");
  const [refusal, setRefusal] = useState<Refusal | null>(null);
  const [anyway, setAnyway] = useState(false);

  function type(v: string) {
    setNiche(v);
    setAnyway(false);
    setSaid("");
  }
  function pick(v: string) {
    type(v);
    setRefusal(null);
    box.current?.focus();
  }

  async function send(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy) return;
    const f = new FormData(e.currentTarget);
    const asked = String(f.get("niche") ?? niche).replace(/\s+/g, " ").trim();      // the box as it stands, whatever set it
    setSaid("");
    if (!anyway && asked.length >= 8) {
      // the rules, here as in the route: a refusal the table answers needs no request
      const g = gate(asked);
      if (g.verdict === "refuse" && g.suggestions.length) {
        setRefusal({ message: refusalWords(asked), suggestions: g.suggestions });
        return;
      }
    }
    const body = { niche: asked, stage: String(f.get("stage") ?? ""), geography: String(f.get("geography") ?? ""), ...(anyway ? { run_anyway: true } : {}) };
    setBusy(true);
    try {
      const res = await fetch("/api/thesis/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), cache: "no-store", credentials: "same-origin" });
      if (res.status === 404) {
        setSaid("The internal view is not open in this browser.");
        return;
      }
      const r = (await res.json().catch(() => null)) as { ok?: boolean; run_id?: string; reason?: string; refused?: boolean; suggestions?: unknown } | null;
      if (r && r.ok && r.run_id) {
        setRefusal(null);
        router.push(`/thesis?run=${encodeURIComponent(r.run_id)}`);
        router.refresh();
        return;
      }
      if (r && r.refused) {
        setRefusal({ message: r.reason || refusalWords(asked), suggestions: (Array.isArray(r.suggestions) ? r.suggestions : []).filter((s): s is string => typeof s === "string").slice(0, 5) });
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
  const chip = "border border-rule bg-white px-2 py-0.5 text-left text-xs text-ink hover:border-accent";
  return (
    <form onSubmit={send} className="grid gap-3 sm:grid-cols-[minmax(0,3fr)_minmax(0,1fr)_minmax(0,1fr)_auto] sm:items-end" data-thesis-form="1">
      <label className="block min-w-0 text-xs text-muted">{NICHE_LABEL}
        <input ref={box} name="niche" type="text" required minLength={8} maxLength={400} autoComplete="off" placeholder={NICHE_PLACEHOLDER} value={niche}
          onChange={(e) => type(e.target.value)} aria-describedby="thesis-niche-help" className={`mt-0.5 ${input}`} />
      </label>
      <label className="block min-w-0 text-xs text-muted">Stage <span className="text-[10px]">(optional)</span>
        <input name="stage" type="text" maxLength={80} autoComplete="off" placeholder="Seed to Series B" className={`mt-0.5 ${input}`} />
      </label>
      <label className="block min-w-0 text-xs text-muted">Geography <span className="text-[10px]">(optional)</span>
        <input name="geography" type="text" maxLength={80} autoComplete="off" placeholder="United States" className={`mt-0.5 ${input}`} />
      </label>
      <button type="submit" disabled={busy} className="border border-accent bg-accent px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-60" data-thesis-run="1">{busy ? "Sending" : "Run"}</button>
      <div className="sm:col-span-4">
        <p id="thesis-niche-help" className="text-xs text-muted" data-thesis-help="1">{NICHE_HELP}</p>
        <p className="mt-1.5 flex flex-wrap items-center gap-1.5" data-thesis-examples="1">
          {NICHE_EXAMPLES.map((x) => <button key={x} type="button" onClick={() => pick(x)} className={chip} data-thesis-example={x}>{x}</button>)}
        </p>
      </div>
      {refusal ? (
        <div role="alert" className="border border-accent bg-panel px-3 py-2 text-sm sm:col-span-4" data-thesis-refused="1">
          <p>{refusal.message}</p>
          <p className="mt-1.5 flex flex-wrap items-center gap-1.5" data-thesis-suggestions={refusal.suggestions.length}>
            {refusal.suggestions.map((x) => <button key={x} type="button" onClick={() => pick(x)} className={chip} data-thesis-suggestion={x}>{x}</button>)}
          </p>
          <label className="mt-2 flex w-fit items-center gap-1.5 text-xs text-muted">
            <input type="checkbox" checked={anyway} onChange={(e) => setAnyway(e.target.checked)} data-thesis-anyway="1" />{RUN_ANYWAY}
          </label>
        </div>
      ) : null}
      {said ? <p role="alert" className="text-sm text-accent sm:col-span-4" data-thesis-said="1">{said}</p> : null}
    </form>
  );
}
