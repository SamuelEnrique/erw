import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { shown } from "@/lib/format";
import { problemSet, SETS, type Part } from "@/lib/problems";
import { attempt } from "@/lib/supabase";

// Session 44: a problem set (lib/problems.ts). Every answer is computed on the server from the warehouse tables and
// carries its check key; the numbers move as the data updates. "Show answer" is a plain <details>, so it works without
// scripts and a teacher can assign the page with the answers closed.
export const revalidate = 3600;
export function generateStaticParams() {
  return SETS.map((s) => ({ slug: s.slug }));
}
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  return { title: SETS.find((s) => s.slug === slug)?.title ?? "Problem set" };
}

function Parts({ parts }: { parts: Part[] }) {
  return (
    <>
      {parts.map((p, i) =>
        typeof p === "string" ? <span key={i}>{p}</span> : (
          <span key={i} className="font-mono"><Num check={p.k} raw={p.v}>{shown(p.v)}</Num>{p.u ? ` ${p.u}` : ""}</span>
        ))}
    </>
  );
}

export default async function Problems({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  if (!SETS.some((s) => s.slug === slug)) notFound();
  const got = await attempt(() => problemSet(slug));
  const meta = SETS.find((s) => s.slug === slug)!;
  return (
    <>
      <p className="mb-1 text-xs text-muted"><Link href="/learn/problems">Problem sets</Link> / {meta.title}</p>
      <h1 className="mb-1 text-3xl">{meta.title}</h1>
      <p className="mb-3 max-w-3xl text-sm">{meta.line} Every answer is computed from the warehouse&apos;s tables when the page is built, so the numbers move as the data updates.</p>
      <div className="mb-5 max-w-3xl border-l-2 border-accent pl-3 text-sm">
        <p><strong>For teachers.</strong> {meta.teacher}</p>
        <p className="mt-1 text-xs text-muted">Pages: {meta.pages.map((p, i) => <span key={p.href}>{i ? ", " : ""}<Link href={p.href}>{p.label}</Link></span>)}.</p>
      </div>
      {!got.ok || !got.data ? (
        <NoData what="the problem set" reason={got.ok ? "no data" : got.reason} />
      ) : (
        <ol className="space-y-6">
          {got.data.questions.map((q, n) => (
            <li key={q.id}>
              <Section title={`Question ${n + 1}`}>
                <p className="mb-1 max-w-3xl">{q.q}</p>
                <p className="mb-2 text-xs text-muted">Tables: {q.tables.map((t, i) => <span key={t}>{i ? ", " : ""}<Link href={`/data#${t}`} className="font-mono">{t}</Link></span>)}</p>
                <details className="max-w-3xl border border-rule bg-panel p-2 text-sm">
                  <summary className="cursor-pointer text-accent">Show answer</summary>
                  <p className="mt-2"><strong>Answer.</strong> <Parts parts={q.answer} /></p>
                  <p className="mt-2 font-semibold">Worked solution</p>
                  <ol className="list-decimal pl-6">
                    {q.steps.map((s, i) => <li key={i}><Parts parts={s} /></li>)}
                  </ol>
                  <p className="mt-2 text-muted">Why it matters: {q.why}</p>
                </details>
              </Section>
            </li>
          ))}
        </ol>
      )}
    </>
  );
}
