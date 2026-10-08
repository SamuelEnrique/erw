// Energy Research Warehouse (ERW) site, session 150: Thesis Builder (/thesis), the figures of the data providers in a
// report, once a run holds an answer of a provider beside PitchBook (lib/thesis/providers.ts). Drawn by the report
// (components/thesis/Report.tsx), which keeps its own PitchBook block for a run that holds PitchBook's answer alone.
//
//   label          every figure stands with the name of the provider that supplied it. The label's hover says where the
//                  figure came from, whose copy the data is with the provider's own sentence on redistribution, the
//                  format, when the answer was pasted and the hash of the pasted text
//   differ         where two providers give the same fact differently, each value is shown as its provider gave it and
//                  the lines carry a short mark; none is averaged, preferred or dropped
//   not mapped     a field a provider returned that this page does not use is kept as given; the block says how many,
//                  and names them on hover
// Nothing here says how a report is made. No component here runs in the browser.
import type { ReactNode } from "react";
import { PROVIDERS, companyIn, disagreements, factsFor, factsOfCompany, hoverOf, notMappedOf, type Fact, type FactId, type Held, type ProviderPayload, type PvCompany, type PvResult, type Stamp } from "@/lib/thesis/providers";
import { PB_PENDING, PB_PENDING_WHY, arr, num, str } from "@/lib/thesis/view";

const MISSING = "cursor-help whitespace-nowrap border-b border-dotted border-muted text-[11px] italic text-muted";
const TAG = "whitespace-nowrap rounded-sm border border-accent px-1 align-baseline text-[10px] font-semibold not-italic text-accent";
const DIFFER = "The providers give this differently. Each value is shown as its provider gave it.";

function Gap({ words, why, kind }: { words: string; why: string; kind: string }) {
  return <span className={MISSING} title={why} data-missing={kind}>{words}</span>;
}
/** The visible label every provider's figure carries. PitchBook's keeps the mark it has had since session 135. */
export function ProviderTag({ s }: { s: Stamp }) {
  const label = PROVIDERS[s.provider].label;
  return <>{" "}<span className={TAG} title={hoverOf(s)} data-provider-tag={s.provider} {...(s.provider === "pitchbook" ? { "data-pb-tag": "1" } : {})}>{label}</span></>;
}
function Differs() {
  return <><span className="cursor-help whitespace-nowrap border border-accent bg-white px-1 text-[10px] uppercase tracking-wide text-accent" title={DIFFER} data-disagree-mark="1">differs</span>{" "}</>;
}
/** One figure of one provider: its name, its value, its provider. */
function Figure({ f, marked }: { f: Fact; marked: boolean }): ReactNode {
  return (
    <>
      {marked ? <Differs /> : null}
      <span className="text-muted">{f.label}:</span> <span title={f.note ?? undefined} className={f.note ? "cursor-help" : undefined}>{f.value}</span>
      <ProviderTag s={f} />
    </>
  );
}
const attrs = (f: Fact, marked: boolean) => ({
  "data-provider-figure": f.fact, "data-provider": f.provider, "data-disagree": marked ? "1" : undefined,
  ...(f.provider === "pitchbook" ? { "data-pb-figure": f.field } : {}),
});

/** The figures that answer one cell of the report (a cell that read "PitchBook pending"): one line a provider. */
export function ProviderCell({ held, company, fact }: { held: Held[]; company: string; fact: FactId }): ReactNode | null {
  const all = factsFor(held, company);
  const mine = all.filter((f) => f.fact === fact);
  if (!mine.length) return null;
  const marked = disagreements(all).has(fact);
  return <>{mine.map((f) => <span key={f.provider} className="block" {...attrs(f, marked)}><Figure f={f} marked={marked} /></span>)}</>;
}

function NotMapped({ h, c }: { h: Held; c: PvCompany | PvResult }) {
  const fields = notMappedOf(c as PvCompany);
  if (!fields.length) return null;
  const label = PROVIDERS[h.provider].label;
  const shown = fields.slice(0, 12).join(", ");
  return (
    <li data-not-mapped={fields.length} data-provider={h.provider}>
      <span className={MISSING} title={`Returned by ${label}, kept as given and not used here: ${shown}${fields.length > 12 ? `, and ${fields.length - 12} more` : ""}.`}>{fields.length} {fields.length === 1 ? "field" : "fields"} not mapped</span>
      <ProviderTag s={h} />
    </li>
  );
}

/** The providers' block of one company: every figure of every provider, each with its label. */
export function ProviderBlock({ name, held, asked }: { name: string; held: Held[]; asked: boolean }) {
  const facts = factsFor(held, name);
  const marked = disagreements(facts);
  const gaps: ReactNode[] = [];
  if (!held.some((h) => h.provider === "pitchbook")) {
    gaps.push(asked
      ? <Gap key="pitchbook" words={PB_PENDING} why={PB_PENDING_WHY} kind="pitchbook_pending" />
      : <Gap key="pitchbook" words="not asked" why="This company is not among those asked of PitchBook." kind="pitchbook_not_asked" />);
  }
  for (const h of held) {
    const label = PROVIDERS[h.provider].label, c = companyIn(h, name);
    if (!c) gaps.push(<Gap key={h.provider} words={`not in ${label}'s answer`} why={`${label}'s answer does not name this company.`} kind={`${h.provider}_absent`} />);
    else if (!c.found) gaps.push(<Gap key={h.provider} words={`not found in ${label}`} why={`${label} returned no company under this name.`} kind={`${h.provider}_not_found`} />);
    else if (!facts.some((f) => f.provider === h.provider)) gaps.push(<Gap key={h.provider} words={`no ${label} figure`} why={`${label} returned this company with no figure.`} kind={`${h.provider}_absent`} />);
  }
  return (
    <div className="min-w-[16rem] text-xs" data-provider-block={name}>
      {facts.length ? (
        <ul className="space-y-0.5" data-pb-block={name}>
          {facts.map((f) => <li key={`${f.fact}|${f.provider}`} {...attrs(f, marked.has(f.fact))}><Figure f={f} marked={marked.has(f.fact)} /></li>)}
          {held.filter((h) => h.provider !== "pitchbook").map((h) => { const c = companyIn(h, name); return c && c.found ? <NotMapped key={h.provider} h={h} c={c as PvCompany} /> : null; })}
        </ul>
      ) : null}
      {gaps.length ? <p className={`space-x-2 ${facts.length ? "mt-1" : ""}`}>{gaps}</p> : null}
    </div>
  );
}

const scalar = (v: unknown): string => (typeof v === "string" ? v : typeof v === "number" && Number.isFinite(v) ? num(v) : typeof v === "boolean" ? (v ? "yes" : "no") : "");
/** A result of a saved search of investors or of people: its mapped fields under the provider's own field names. */
function ResultFields({ h, r }: { h: Held; r: PvResult }) {
  const rows = Object.entries(r.record ?? {}).map(([k, v]) => [k, scalar(v)] as const).filter(([, v]) => v).slice(0, 8);
  return (
    <ul className="mt-1 space-y-0.5 text-xs">
      {rows.map(([k, v]) => <li key={k} data-provider-figure={k} data-provider={h.provider}><span className="font-mono text-[11px] text-muted">{k}:</span> {v}<ProviderTag s={h} /></li>)}
      <NotMapped h={h} c={r} />
    </ul>
  );
}
function Card({ h, name, why, children }: { h: Held; name: string; why?: string; children: ReactNode }) {
  return (
    <li className="border border-rule bg-panel px-2 py-1.5" data-company={name}>
      <span className="font-semibold">{name}</span><ProviderTag s={h} />
      {why ? <span className="mt-0.5 block text-xs">{why}<ProviderTag s={h} /></span> : null}
      {children}
    </li>
  );
}
function CompanyFacts({ h, c }: { h: Held; c: PvCompany }) {
  return (
    <ul className="mt-1 space-y-0.5 text-xs">
      {factsOfCompany(h, c).map((f) => <li key={f.fact} {...attrs(f, false)}><Figure f={f} marked={false} /></li>)}
      <NotMapped h={h} c={c} />
    </ul>
  );
}

/** What a provider beside PitchBook found beyond the companies asked for: its additional companies, and the results
 * of the saved searches the person named. Each line carries the provider's label. */
export function ProviderFound({ h, heading }: { h: Held; heading: (children: ReactNode) => ReactNode }) {
  if (h.provider === "pitchbook") return null;
  const p = h.payload as ProviderPayload, label = PROVIDERS[h.provider].label;
  const more = arr(p.additional_companies).filter((c) => c?.found);
  const lists = arr(p.lists).filter((l) => arr(l?.results).length);
  if (!more.length && !lists.length) return null;
  const OF: Record<string, string> = { companies: "companies", investors: "investors", people: "people" };
  return (
    <section className="mt-6" data-provider-additional={h.provider}>
      {more.length ? (
        <>
          {heading(<>Found by {label}<ProviderTag s={h} /></>)}
          <ul className="grid gap-3 text-sm lg:grid-cols-2">
            {more.map((c, i) => <Card key={`${str(c?.name)}|${i}`} h={h} name={str(c?.name)} why={str(c?.why)}><CompanyFacts h={h} c={c} /></Card>)}
          </ul>
        </>
      ) : null}
      {lists.map((l, k) => (
        <div key={`${str(l?.name)}|${k}`} data-provider-list={OF[str(l?.of)] ?? ""}>
          {heading(<>{label} saved search of {OF[str(l?.of)] ?? "results"}: {str(l?.name)}<ProviderTag s={h} /></>)}
          <ul className="grid gap-3 text-sm lg:grid-cols-2">
            {arr(l.results).map((r, i) => (
              <Card key={`${str(r?.name)}|${i}`} h={h} name={str(r?.name)}>
                {l.of === "companies" ? <CompanyFacts h={h} c={{ ...r, found: true }} /> : <ResultFields h={h} r={r} />}
              </Card>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}
